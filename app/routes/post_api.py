from flask.views import MethodView
from flask import app, jsonify, Blueprint, request, current_app
from marshmallow import ValidationError
from datetime import timedelta
from app.schemas.post_schemas import PostSchema, UpdatePostSchema
from app.models.post import Post
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.allowed_file import allowed_file
from app.db import db
from app.custom_pagination import CustomPagination
from werkzeug.utils import secure_filename
import os

post_api = Blueprint("post_api", __name__)


class PostApi(MethodView):
    post_schema = PostSchema()
    decorators = [jwt_required()]

    def post(self, user_id=None):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error": "User not found"}), 404

        image = request.files.get("image")
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
        else:
            image_path = None

        data = request.form if request.form else request.json
        try:
            post_data = self.post_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        post = Post(
            title=data.get("title"),
            content=data.get("content"),
            image=image_path,
            user=current_user_id,
        )
        db.session.add(post)
        db.session.commit()
        post_data = self.post_schema.dump(post)
        return jsonify(post_data), 201

    def put(self):
        update_post_schema = UpdatePostSchema()
        current_user_id = get_jwt_identity()
        post_id = request.args.get("post_id")
        data = request.json
        if not current_user_id:
            return jsonify({"error": "Unauthorized"})
        if not post_id:
            return jsonify({"error": "Please Provide Post id"})
        post = Post.query.filter_by(user=current_user_id, id=post_id, is_deleted=False)
        if post == None:
            return jsonify({"error": "Post not exist"}), 204
        try:
            updated_data = update_post_schema.load(data)
            if "title" in data:
                post.title = data.get("title")
            if "content" in data:
                post.content = data.get("content")
                db.session.commit()
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        return jsonify(updated_data), 202

    def get(self,user_id = None):
        current_user_id = get_jwt_identity()
        post_id = request.args.get("post_id")
        if post_id:
            post = Post.query.filter_by(id=post_id, is_deleted=False).first()
            if not post:
                return jsonify({"error": "Not exist"}), 404
            post_data = self.post_schema.dump(post)
            return jsonify(post_data), 200

        elif user_id:
            posts = Post.query.filter_by(user=current_user_id).all()

        else:
            posts = Post.query.filter_by(user=current_user_id).all()

        if posts == None:
            return jsonify({"error": "Post not exist for the user"})
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(posts, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = self.post_schema.dump(
            paginated_data["items"], many=True
        )
        return jsonify(paginated_data), 200

    def delete(self):
        current_user_id = get_jwt_identity()
        post_id = request.args.get("post_id")
        if not post_id:
            return jsonify({"error": "Post id is required"})

        post = Post.query.filter_by(
            user=current_user_id, id=post_id, is_deleted=False
        ).first()
        if post == None:
            return jsonify({"error": "Post not exist"}), 404
        post.is_deleted = True
        db.session.commit()
        return jsonify(), 204


post_view = PostApi.as_view("post_api")
post_api.add_url_rule(
    "/api/posts/", view_func=post_view, methods=["GET", "POST", "PUT", "DELETE"]
)

post_api.add_url_rule("/api/users/<uuid:user_id>/posts/",view_func=post_view, methods=["GET"])
