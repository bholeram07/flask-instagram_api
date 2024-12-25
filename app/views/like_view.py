from flask import app, jsonify, Blueprint, request, current_app
from flask_restful import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like_schema import LikeSchema
from app.uuid_validator import is_valid_uuid
from app.extensions import db
from app.custom_pagination import CustomPagination
from app.pagination_response import paginate_and_serialize
from sqlalchemy import desc


class LikeAPi(MethodView):
    like_schema = LikeSchema()
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self, post_id=None):
        """
        create a like on the post and if not find like of the user on the post
        deslike the post 
        """
        data = request.json
        post_id = data.get("post_id")

        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400

        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        like = Like.query.filter_by(
            post=post_id, user=self.current_user_id, is_deleted=False).first()
        
        #for dislike
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"message": "Post unliked"}), 200
        
        #for like
        else:
            like = Like(post=post_id, user=self.current_user_id)
        db.session.add(like)
        db.session.commit()
        
        #get a post data to the like response
        post_data = {
            "id": post.id,
            "title": post.title,
           
        }
        like_data = self.like_schema.dump(like)
        
        #get a user data to the comment 
        user = User.query.get(self.current_user_id)
        user_data = {
            "id": user.id,
            "username": user.username,
            "profile_pic": user.profile_pic if user.profile_pic else None,
        }
        #added a post and user data to the response
        like_data["post"] = post_data
        like_data["user"] = user_data
        like_data["liked_at"] = like.created_at.isoformat()

        return jsonify(like_data), 201

    def get(self, post_id):
        """
        This api is for get the likes on the post by post_id
        """
        if not post_id:
            return jsonify({"error": "Please provide post id "}), 400

        if not is_valid_uuid(post_id):
            return {"error": "Invalid UUID format"}, 400
        
        #get a post
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404
        
        #for get all the likes on the post
        likes = Like.query.filter_by(post=post_id).order_by(
            desc(Like.created_at)).all()
        
        #count of the likes on the post
        likes_count = Like.query.filter_by(post=post_id).count()

        if likes_count == 0:
            return jsonify({"error": "No likes found on this post"}), 404
        
        #pagination
        return paginate_and_serialize(
            likes,
            self.like_schema,
            extra_fields={"likes_count": likes_count}
        )

