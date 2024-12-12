from flask import jsonify, request, Blueprint, current_app
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment_schema import CommentSchema
from app.custom_pagination import CustomPagination
from app.extensions import db
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from sqlalchemy import desc
from app.pagination_response import paginate_and_serialize
from uuid import UUID
from datetime import datetime


class CommentApi(MethodView):
    decorators = [jwt_required()]
    comment_schema = CommentSchema()

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """
        Creates a new comment. Requires user authentication.
        This api allows the user to create a comment by providing a  content and post id .
        """
        data = request.json
        post_id = data.get("post_id")

        if not post_id:
            return jsonify({"error": "Please provide post id"}), 400

        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        # fetch the post through post id
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        comment_data, error = validate_and_load(self.comment_schema, data)

        content = data.get("content")
        comment = Comment(
            post_id=post_id, user_id=self.current_user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        return jsonify(self.comment_schema.dump(comment)), 201

    def get(self, post_id=None, comment_id=None):
        """
        Retrieves comment on a specific post or by comment id, everyone can perform this operation
        """
        if comment_id:
            if not is_valid_uuid(comment_id):
                return jsonify({"error": "Invalid uuid format"}), 400
            comment = Comment.query.filter_by(id=comment_id, is_deleted=False).order_by(
                desc(Comment.created_at)).first()
            if not comment:
                return jsonify({"errors": "Comment not exist"}), 404
            return jsonify(self.comment_schema.dump(comment))

        if post_id:
            if not is_valid_uuid(post_id):
                return jsonify({"error": "Invalid uuid format"}), 400

            post = Post.query.filter_by(id=post_id, is_deleted=False).first()

            if not post:
                return jsonify({"error": "Post does not exist"}), 404

            comments = Comment.query.filter_by(
                post_id=post_id, is_deleted=False
            ).order_by(desc(Comment.created_at)).all()

            if not comments:
                return jsonify({"error": "No comments found for this post"}), 404

            # pagination

            return paginate_and_serialize(comments , self.comment_schema)
        return jsonify({"error": "Post id is required"}), 400

    def put(self, comment_id):
        ''' 
        Update a comment only a comment author and post owner can delete it
        '''
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        # check the user is owner of the comment or not
        comment = Comment.query.filter_by(user_id=self.current_user_id,
                                          id=comment_id, is_deleted=False
                                          ).first()

        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404

        data = request.json
        # serialize the data
        comment_update_data, errors = validate_and_load(
            self.comment_schema, data)
        if errors:
            return jsonify({"errors": errors})

        comment.content = comment_update_data.get("content")
        db.session.commit()

        return jsonify(self.comment_schema.dump(comment_update_data)), 202

    def delete(self, comment_id):
        """
        Delete a comment only a post owner or comment owner can delete it
        """
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        comment = Comment.query.filter_by(
            id=comment_id, is_deleted=False
        ).first()

        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404

        # get the post through the comment object
        post_id = comment.post_id
        post = Post.query.get(post_id)
        # check if the user is comment owner or the post owner
        if comment.user_id != UUID(self.current_user_id) and post.user != UUID(self.current_user_id):
            return jsonify({"error": "Comment not exist"}), 404

        # soft deletion
        comment.is_deleted = True
        comment.deleted_at = datetime.now()
        db.session.commit()

        return jsonify(), 204
