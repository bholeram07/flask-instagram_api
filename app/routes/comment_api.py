from flask import jsonify, request, Blueprint, app, current_app
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment_schema import CommentSchema
from app.custom_pagination import CustomPagination
from app.db import db
from app.uuid_validator import is_valid_uuid

comment_api = Blueprint("comment_api", __name__)


class CommentApi(MethodView):
    decorators = [jwt_required()]
    comment_schema = CommentSchema()

    def post(self):
        current_user_id = get_jwt_identity()
        data = request.json
        post_id = data.get("post_id")

        if not post_id:
            return jsonify({"error": "please provide post id"}), 400

        if not is_valid_uuid(post_id):
            return jsonify({"error": "invalid uuid format"}), 400

        post = Post.query.filter_by(id=post_id, is_deleted=False).first()

        if not post:
            return jsonify({"error": "Post not exist"}), 404

        try:
            comment_data = self.comment_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        content = data.get("content")
        comment = Comment(post_id=post_id, user_id=current_user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        comment_data = self.comment_schema.dump(comment)
        return jsonify(comment_data), 201

    def get(self, post_id=None, comment_id=None):
        current_user_id = get_jwt_identity()
        comment_id = request.args.get("comment_id")

        if comment_id:

            if not is_valid_uuid(comment_id):
                return jsonify({"error": "Invalid uuid format"}), 400

            comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()

            if comment == None:
                return jsonify({"error": "Comment not exist"}), 404

            comment_data = self.comment_schema.dump(comment)
            return jsonify(comment_data), 200

        elif post_id:

            if not is_valid_uuid(post_id):
                return jsonify({"error": "Invalid uuid format"}), 400

            comments = Comment.query.filter_by(post_id=post_id, is_deleted=False).all()

            if not comments:
                return jsonify({"error": "No comments found for this post"}), 404

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(comments, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = self.comment_schema.dump(
            paginated_data["items"], many=True
        )
        return jsonify(paginated_data), 200

    def put(self):
        current_user_id = get_jwt_identity()
        data = request.json
        comment_id = request.args.get("comment_id")

        if not comment_id:
            return jsonify({"error": "Please Provide comment id"}), 400

        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        comment = Comment.query.filter_by(
            id=comment_id, user_id=current_user_id, is_deleted=False
        ).first()

        if comment == None:
            return jsonify({"error": "Comment not exist"}), 404

        try:
            comment_update_data = self.comment_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        comment.content = comment_update_data.get("content")
        db.session.commit()
        updated_comment_data = self.comment_schema.dump(comment)
        return jsonify(updated_comment_data), 202

    def delete(self):
        current_user_id = get_jwt_identity()
        comment_id = request.args.get("comment_id")

        if not comment_id:
            return jsonify({"error": "Please provide comment id"}), 400

        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        comment = Comment.query.filter_by(
            id=comment_id, user_id=current_user_id, is_deleted=False
        ).first()

        if comment == None:
            return jsonify({"error": "Comment not exist"}), 404

        comment.is_deleted = True
        db.session.commit()
        return jsonify(), 204


comment_view = CommentApi.as_view("comment_api")
comment_api.add_url_rule(
    "/api/comments/", view_func=comment_view, methods=["GET", "POST", "PUT", "DELETE"]
)
comment_api.add_url_rule(
    "/api/posts/<post_id>/comments/", view_func=comment_view, methods=["GET"]
)
