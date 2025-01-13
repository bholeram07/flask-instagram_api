from flask import app, jsonify, Blueprint, request, current_app
from flask_restful import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.comment import Comment
from app.models.story import Story
from app.models.user import User
from app.schemas.like_schema import LikeSchema
from app.uuid_validator import is_valid_uuid
from app.extensions import db
from app.custom_pagination import CustomPagination
from app.pagination_response import paginate_and_serialize
from sqlalchemy import desc
from app.permissions.permissions import Permission
from app.utils.get_limit_offset import get_limit_offset
from typing import Tuple, Union, Dict, Optional, List
from app.utils.get_validate_user import get_post_or_404,get_comment_or_404

class PostLikeAPi(MethodView):
    like_schema = LikeSchema()
    decorators = [jwt_required(), Permission.user_permission_required]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self)->Tuple[Union[dict, str], int]:
        """
        create a like on the post and if not find like of the user on the post
        deslike the post 
        """
        # get the request data and initailize the post_id
        data:dict = request.get_json()
        post_id:str= data.get("post_id")

        # validates the post_id
        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400
        # fetch the post by post_id
        post: Post = get_post_or_404(post_id)

        # fetch the like of the user on the post
        like:Optional[Like]= Like.query.filter_by(
            post=post_id, user=self.current_user_id, is_deleted=False).first()

        # for dislike
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"message": "Post unliked"}), 200

        # for like
        else:
            like = Like(post=post_id, user=self.current_user_id)
            db.session.add(like)
            db.session.commit()

        # get a post data to the like response
        
        like_data:dict = self.like_schema.dump(like)


        return jsonify(like_data), 201

    def get(self, post_id:str)->dict:
        """
        This api is for get the likes on the post by post_id
        """

        if not post_id:
            return jsonify({"error": "Please provide post id "}), 400

        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # get a post
        post:Optional[Post] = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        # for get all the likes on the post
        page_number, offset, page_size = get_limit_offset()
        likes : Optional[Like] = (Like.query.filter_by(post=post_id,is_deleted = False).order_by(
            desc(Like.created_at)).offset(offset).limit(page_size).all())

        # count of the likes on the post
        likes_count:int = Like.query.filter_by(post=post_id).count()

        if likes_count == 0:
            return jsonify({"error": "No likes found on this post"}), 404

        # pagination
        return paginate_and_serialize(
            likes, page_number, page_size, self.like_schema, likes_count=likes_count
        )


class CommentLikeApi(MethodView):
    """
    An Api to handle the likes on the comment
    """
    decorators = [jwt_required(), Permission.user_permission_required]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self)-> Tuple[Union[dict, str], int]:
        """ 
        An function to create the like on the comment
        """
        # get the request data
        data:dict= request.get_json()
        # get the comment id
        comment_id:str = data.get("comment_id")
        if not comment_id:
            return jsonify({"error": "please provide comment id"}), 400
        # validate the comment id
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the comment by comment_id
        comment:Optional[Comment] = Comment.query.filter_by(
            id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"error": "Comment not exist"}), 404

        # check the like of the user on the comment
        like : Optional[Like] = Like.query.filter_by(
            comment=comment_id, user=self.current_user_id, is_deleted=False).first()

        # for dislike
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"message": "Comment unliked"}), 200

        # for like
        else:
            like = Like(
                comment=comment_id,
                user=self.current_user_id
            )
            db.session.add(like)
            db.session.commit()

        # serialize the response
        result = {
            "comment_id": comment_id,
            "content": comment.content,
            "comment_owner": comment.user_id,
            "liked_by": like.user,

        }
        return jsonify(result), 201

    def get(self, comment_id: Optional[str]=None):
        """ 
        An function to get the likes on the comment by comment id
        """
        # get the comment_id
        if not comment_id:
            return jsonify({"error": "Provide comment id"}), 404
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        comment: Optional[Comment] = Comment.query.filter_by(
            id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"errors": "Comment not exist"}), 400

        # get the page size and page_number given by the user
        page_number, offset, page_size = get_limit_offset()
        # fetch the likes on the comment
        likes : Optional[Like] = Like.query.filter_by(
            comment=comment_id,is_deleted = False).offset(
            offset).limit(page_size).all()
        like_data = []
        # generate a dynamic response
        for like in likes:
            like_data.append({
                "comment_id": comment_id,
                "author": comment.user_id,
                "liked_by": like.user
            })
        # apply the pagination
        item :dict = paginate_and_serialize(
            like_data, page_number, page_size), 200

        return item


class StorylikeApi(MethodView):
    """
    An Api to handle the likes on the story 
    """
    decorators = [jwt_required(), Permission.user_permission_required]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self)-> Tuple[Union[dict, str], int]:
        # get the request data
        data:dict = request.get_json()
        story_id:str = data.get("story_id")

        # validate the story_id
        if not is_valid_uuid(story_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the story by story_id
        story : Optional[Story]= Story.query.filter_by(
            id=story_id, is_deleted=False).first()
        # if story not exist
        if not story:
            return jsonify({"error": "story not exist"}), 404

        # if user like his own story
        if str(story.story_owner) == str(self.current_user_id):
            return jsonify({"error": "You can't like your own story"}), 400

        # check the like of the user on the story
        like: Optional[Like] = Like.query.filter_by(
            story=story_id, user=self.current_user_id, is_deleted = False).first()

        # for dislike
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"message": "Story unliked"}), 200

        # for like
        else:
            like = Like(
                story=story_id,
                user=self.current_user_id
            )
            db.session.add(like)
            db.session.commit()
        result = {
            "story_id": story_id,
            "content": story.content,
            "story_owner": story.story_owner,
            "liked_by": like.user,

        }
        return jsonify(result), 201

    def get(self, story_id:str)-> Tuple[Union[dict, str], int]:
        """
        An function to get the likes on the comment by comment id
        """
        if not is_valid_uuid(story_id):
            return jsonify({"error": "Invalid UUID format"}), 400
        # get the comment
        story: Optional[Story] = Story.query.filter_by(
            id=story_id).first()
        if not story:
            return jsonify({"error": "Story not exist"}), 404

        # get the page size and page_number given by the user
        page_number, offset, page_size = get_limit_offset()

        # fetch the likes on the comment
        likes: Optional[Like] = Like.query.filter_by(
            story=story_id,is_deleted = False).offset(
            offset).limit(page_size).all()

        like_data = []
        # generate a dynamic response
        for like in likes:
            like_data.append({
                "story_id": story_id,
                "owner": story.story_owner,
                "content": story.content
            })
        # apply the pagination
        item:dict = paginate_and_serialize(
            like_data, page_number, page_size), 200

        return item
