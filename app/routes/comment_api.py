from flask import jsonify, request, Blueprint, app, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment_schema import CommentSchema
from app.custom_pagination import CustomPagination
from app.db import db


comment_api = Blueprint("comment_api", __name__)


@comment_api.route("/api/comments/", methods=["GET", "POST", "PUT", "DELETE"])
@jwt_required()
def comments(post_id=None, comment_id=None):
    current_user_id = get_jwt_identity()
    comment_schema = CommentSchema()
    # data = request.json
    # post_id = data.get("post_id")

    if request.method == "POST":
        data = request.json
        post_id = data.get("post_id")
        if not post_id:
            return jsonify({"error": "please provide post id"}), 400
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post not exist"}), 404
        try:
            comment_data = comment_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        content = data.get("content")
        comment = Comment(post_id=post_id, user_id=current_user_id, content=content)
        db.session.add(comment)
        db.session.commit()
        comment_data = comment_schema.dump(comment)
        return jsonify(comment_data), 201

    if request.method == "GET":
        comment_id = request.args.get("comment_id")

        if comment_id:
            comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()
            if comment == None:
                return jsonify({"error": "Comment not exist"}), 404
            comment_data = comment_schema.dump(comment)
            return jsonify(comment_data), 200
        else:
            post_id = data.get("post_id")
            comments = Comment.query.filter_by(post_id=post_id, is_deleted=False).all()
            if comments == None:
                return jsonify({"error": "Comment not exist on this post"})
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(comments, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = comment_schema.dump(
            paginated_data["items"], many=True
        )
        return jsonify(paginated_data), 200

    if request.method == "PUT":
        data = request.json
        comment_id = request.args.get("comment_id")
        if not comment_id:
            return jsonify({"error": "Please Provide comment id"})

        comment = Comment.query.filter_by(
            id=comment_id, user_id=current_user_id, is_deleted=False
        ).first()
        if comment == None:
            return jsonify({"error": "Comment not exist"}), 404
        try:
            comment_update_data = comment_schema.load(data)

        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        comment.content = comment_update_data.get("content")
        db.session.commit()

        updated_comment_data = comment_schema.dump(comment)

        return jsonify(updated_comment_data), 202

    if request.method == "DELETE":
        comment_id = request.args.get("comment_id")
        if not comment_id:
            return jsonify({"error": "Please provide comment id"}), 400
        comment = Comment.query.filter_by(
            id=comment_id, user_id=current_user_id, is_deleted=False
        ).first()
        if comment == None:
            return jsonify({"error": "Comment not exist"}), 404
        comment.is_deleted = True
        db.session.commit()
        return jsonify(), 204
