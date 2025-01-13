from flask import jsonify, request, Blueprint, current_app, Response
from typing import Union, List, Dict, Optional
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
from app.response.comment_response import comment_response
from app.permissions.permissions import Permission
from app.utils.get_limit_offset import get_limit_offset
from app.utils.ist_time import current_time_ist
from app.helper.comments import create_reply, create_comment, get_replies_data
from app.utils.get_validate_user import get_post_or_404, get_comment_or_404


class CommentApi(MethodView):
    """
    API for handling comments on posts.
    """
    decorators = [jwt_required(), Permission.user_permission_required]
    comment_schema = CommentSchema()
    reply_comment_schema = ReplyCommentSchema()

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self) -> dict:
        """
        Create a new comment or reply to a comment.
        """
        data: Dict = request.get_json()
        post_id: str = data.get("post_id")
        parent_comment_id: str = data.get("comment_id")
        content: str = data.get("content")

        if post_id:
            return create_comment(post_id, content, data, self.current_user_id, self.comment_schema)

        elif parent_comment_id:
            return create_reply(parent_comment_id, content, data, self.current_user_id, self.reply_comment_schema)

        else:
            return jsonify({"error": "Post ID or Comment ID is required"}), 400

    def get(self, comment_id: str) -> dict:
        """
        Get a comment by its ID.
        """
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        comment = get_comment_or_404(comment_id)

        reply_count: int = Comment.query.filter_by(
            parent=comment_id, is_deleted=False).count()
        comment_data: dict = self.comment_schema.dump(comment)
        comment_data["reply_count"] = reply_count

        replies = Comment.query.filter_by(
            parent=comment_id, is_deleted=False).all()
        comment_data["replies"] = get_replies_data(
            replies, self.reply_comment_schema)
        comment_data["parent"] = comment.parent

        return jsonify(comment_data), 200

    def put(self, comment_id: str) -> Union[dict, int]:
        """
        Update a comment by its ID.
        """

        comment = get_comment_or_404(comment_id, self.current_user_id)

        data: dict = request.get_json()
        comment_update_data, errors = validate_and_load(
            self.comment_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400

        comment.content = comment_update_data.get("content")
        try:
            comment.updated_at = current_time_ist()
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"error": "Some error occurred during updating the comment"}), 500

        return jsonify(self.comment_schema.dump(comment)), 202

    def delete(self, comment_id: str) -> int:
        """
        Delete a comment by its ID.
        """
        comment: Comment = get_comment_or_404(comment_id)
        post: Post = get_post_or_404(comment.post_id)

        if comment.user_id != UUID(self.current_user_id) and post.user_id != UUID(self.current_user_id):
            return jsonify({"error": "You do not have permission to delete this comment"}), 403

        try:
            comment.is_deleted = True
            comment.deleted_at = current_time_ist()
            db.session.commit()
        except:
            db.session.rollback()
            return jsonify({"error": "Some error occurred while deleting the comment"}), 500

        return jsonify(), 204


class CommentListApi(MethodView):
    """
    API for handling list of comments on a post.
    """
    decorators = [jwt_required(), Permission.user_permission_required]
    comment_schema = CommentSchema()

    def get(self, post_id: str) -> dict:
        """
        Get a list of comments for a post.
        """
        post = get_post_or_404(post_id)

        # get the limit and offset
        page_number, offset, page_size = get_limit_offset()
        comments: Optional[Comment] = Comment.query.filter_by(post_id=post_id, is_deleted=False).order_by(
            desc(Comment.created_at)).offset(offset).limit(page_size).all()
        # serialize the comments
        serialized_comments = comment_response(comments, self.comment_schema)
        return paginate_and_serialize(serialized_comments, page_number, page_size)
