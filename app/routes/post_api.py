from flask import app, jsonify, Blueprint, request
from marshmallow import ValidationError
from datetime import timedelta
from app.schemas.post_schemas import PostSchema
from app.models.post import Post
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db

post_api = Blueprint("post_api", __name__)


@post_api.route("/posts", methods=["POST", "GET"])
@post_api.route("/posts/<uuid:post_id>", methods=["PUT", "DELETE", "GET"])
@post_api.route("/users/<uuid:user_id>/posts", methods=["GET"])
@jwt_required()
def posts(post_id=None, user_id=None):
    post_schema = PostSchema()

    if request.method == "POST":
        data = request.json
        current_user_id = get_jwt_identity()
        if not current_user_id:
            "User not found"
        print(data)
        print(current_user_id)
        try:
            post_data = post_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        post = Post(
            title=data.get("title"), content=data.get("content"), user=current_user_id
        )
        db.session.add(post)
        db.session.commit()
        result = post_schema.dump(post)
        return jsonify({"data": result}), 201

    if request.method == "PUT":
        data = request.json
        current_user_id = get_jwt_identity()
        if not current_user_id:
            print("User not Found")
        if not post_id:
            return jsonify({"error": "Please Provide Post id"})
        post = Post.query.filter_by(user=user_id, id=post)
        if post == None:
            return jsonify({"error": "Post not exist"}), 204

        try:
            updated_data = post_schema.load(data)
            updated_data["title"] = data.get("title")
            updated_data["content"] = data.get("content")
            db.session.commit()
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        return jsonify({"data": updated_data}), 202

    if request.method == "GET":
        current_user_id = get_jwt_identity()
        if post_id:
            posts = Post.query.get_or_404(post_id)
            post_data = post_schema.dump(post)
            return jsonify({"data": post_data}), 200
        elif user_id:
            posts = Post.query.filter_by(user=current_user_id).all()
        else:
            current_user_id = get_jwt_identity()
            posts = Post.query.filter_by(user=current_user_id).all()
        if posts == None:
            return jsonify({"error": "Post not exist for the user"})
        post_data = post_schema.dump(posts, many=True)
        return jsonify({"data": post_data}), 200

    if request.method == "DELETE":
        current_user_id = get_jwt_identity()
        if not post_id:
            return jsonify({"error": "Post id is requiered"})

        post = Post.query.filter_by(user=current_user_id, id=post_id).first()
        if post == None:
            return jsonify({"error": "Post not exist"}), 404
        db.session.delete(post)
        db.session.commit()
        return jsonify(), 204
