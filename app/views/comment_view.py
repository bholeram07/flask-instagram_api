from flask import jsonify, request, Blueprint, current_app
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment_schema import CommentSchema
from app.schemas.comment_reply_schema import ReplyCommentSchema
from app.custom_pagination import CustomPagination
from app.extensions import db
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from sqlalchemy import desc
from app.pagination_response import paginate_and_serialize
from uuid import UUID
from datetime import datetime
from app.response.comment_response import comment_respose
from app.permissions.permissions import Permission
from app.utils.get_limit_offset import get_limit_offset
from app.utils.ist_time import current_time_ist

class CommentApi(MethodView):
    """
    API for handling comments on posts.
    """
    decorators = [jwt_required(), Permission.user_permission_required]
    comment_schema = CommentSchema()
    reply_comment_schema = ReplyCommentSchema()

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """
        Create a new comment or reply to a comment.
        """
        data = request.json
        post_id = data.get("post_id")
        parent_comment_id = data.get("comment_id")
        content = data.get("content")
        # if post id is provided create a comment
        if post_id:
            return self.create_comment(post_id, content, data)
        # if comment id is provided create a reply
        elif parent_comment_id:
            return self.create_reply(parent_comment_id, content, data)
        else:
            return jsonify({"error": "Post ID or Comment ID is required"}), 400

    def create_comment(self, post_id, content, data):
        """
        Create a new comment on a post.
        """
        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # check if post exist
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404
        if not post.is_enable_comment:
            return jsonify({"error": "Post owner disabled comments on this post"}), 404

        # validate comment data
        comment_data, error = validate_and_load(self.comment_schema, data)
        if error:
            return jsonify({"errors": error}), 400

        # create a comment
        comment = Comment(
            post_id=post_id, user_id=self.current_user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return jsonify(self.comment_schema.dump(comment)), 201

    def create_reply(self, parent_comment_id, content, data):
        """
        Create a reply to an existing comment.
        """
        if not is_valid_uuid(parent_comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400
        # validate reply comment data
        comment_data, errors = validate_and_load(
            self.reply_comment_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400

        # get the parent comment
        parent_comment = Comment.query.filter_by(
            id=parent_comment_id, is_deleted=False).first()
        if not parent_comment:
            return jsonify({"error": "Comment does not exist"}), 404
        if not content:
            return jsonify({"error": "Provide content for reply"}), 400

        # create the reply
        reply_comment = Comment(parent=parent_comment_id,
                                content=content, user_id=self.current_user_id)
        db.session.add(reply_comment)
        db.session.commit()

        # create the dynamic response
        response = {
            "id": reply_comment.id,
            "content": "This is the reply to the comment",
            "replied_by": reply_comment.user_id,
            "parent_comment": {
                "id": parent_comment.id,
                "content": parent_comment.content
            },
        }
        return jsonify(response), 200

    def get(self, comment_id):
        """
        Get a comment by its ID.
        """
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the comment
        comment = Comment.query.filter_by(
            id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"errors": "Comment does not exist"}), 404

        # get the reply count
        reply_count = Comment.query.filter_by(
            parent=comment_id, is_deleted=False).count()
        comment_data = self.comment_schema.dump(comment)
        comment_data["reply_count"] = reply_count

        # get the replies of the comment
        replies = Comment.query.filter_by(
            parent=comment_id, is_deleted=False).all()
        reply_data = self.get_replies_data(replies)
        comment_data["replies"] = reply_data

        return jsonify(comment_data), 200

    def get_replies_data(self, replies):
        """
        Helper function to get data of replies to a comment.
        """
        reply_data = []
        for reply in replies:
            reply_info = self.reply_comment_schema.dump(reply)
            author = User.query.get(reply.user_id)
            reply_info["author"] = {
                "id": author.id,
                "username": author.username
            }
            reply_data.append(reply_info)
        return reply_data

    def put(self, comment_id):
        """
        Update a comment by its ID.
        """
        # check if the comment id is valid
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the comment
        comment = Comment.query.filter_by(
            user_id=self.current_user_id, id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404

        # get the requested data
        data = request.json
        comment_update_data, errors = validate_and_load(
            self.comment_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400
        # update the content of the comment
        
        comment.content = comment_update_data.get("content")
        try:
            comment.updated_at = current_time_ist()
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"error": "Some error occurred during updating the comment"}), 500
            

        return jsonify(self.comment_schema.dump(comment)), 202

    def delete(self, comment_id):
        """
        Delete a comment by its ID.
        """
        # check the validation of uuid
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the comment
        comment = Comment.query.filter_by(
            id=comment_id, is_deleted=False).first()
        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404
        # fetch the post
        post_id = comment.post_id
        post = Post.query.get(post_id)

        # check if the user is the owner of the comment or post
        if comment.user_id != UUID(self.current_user_id) and post.user_id != UUID(self.current_user_id):
            return jsonify({"error": "You do not have permission to delete this comment"}), 403

        # database operations
        try:
            comment.is_deleted = True
            comment.deleted_at = current_time_ist()
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"error": "Some error occurred while deleting the comment"}), 500

        return jsonify({"message": "Comment deleted successfully"}), 204


class CommentListApi(MethodView):
    """
    API for handling list of comments on a post.
    """
    decorators = [jwt_required(), Permission.user_permission_required]
    comment_schema = CommentSchema()

    def get(self, post_id):
        """
        Get a list of comments for a post.
        """
        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the post
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        # get the limit and offset
        page_number, offset, page_size = get_limit_offset()
        comments = Comment.query.filter_by(post_id=post_id, is_deleted=False).order_by(
            desc(Comment.created_at)).offset(offset).limit(page_size).all()
        # serialize the comments
        serialized_comments = comment_respose(comments, self.comment_schema)
        return paginate_and_serialize(serialized_comments, page_number, page_size)
