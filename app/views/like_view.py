from flask import app, jsonify, Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.user import User
from app.uuid_validator import is_valid_uuid
from app.schemas.like_schema import LikeSchema
from app.extensions import db

like_api = Blueprint("like_api", __name__)


@like_api.route("/api/posts/like/", methods=["POST"])
@like_api.route("/api/posts/<post_id>/like/", methods=["DELETE"])
@jwt_required()
def like(post_id=None):

    like_schema = LikeSchema()

    if request.method == "POST":
        current_user_id = get_jwt_identity()
        data = request.json
        post_id = data.get("post_id")

        if post_id is None:
            return jsonify({"error": "Please provide post id"}), 400

        if not is_valid_uuid(post_id):
            return {"error": "Invalid UUID format"}, 400

        if not current_user_id:
            return jsonify({"error": "User not found"}), 404

        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        like = Like.query.filter_by(post=post_id, user=current_user_id).first()
        if like:
            return jsonify({"error": "You already like this post"}), 409
        else:
            like = Like(post=post_id, user=current_user_id)
        db.session.add(like)
        db.session.commit()

        like_data = like_schema.dump(like)

        post_data = {"id": post.id, "title": post.title, "content": post.content}

        user = User.query.get(current_user_id)
        user_data = {
            "id": user.id,
            "username": user.username,
            "profile_image": user.profile_image if user.profile_image else None,
        }
        like_data["post"] = post_data
        like_data["user"] = user_data
        like_data["liked_at"] = like.created_at.isoformat()

        return jsonify(like_data), 201

    if request.method == "DELETE":
        current_user_id = get_jwt_identity()

        if not post_id:
            return jsonify({"error": "Please Provide post id"})

        if not is_valid_uuid(post_id):
            return {"error": "Invalid UUID format"}, 400

        like = Like.query.filter_by(post=post_id, user=current_user_id).first()
        if not like:
            return jsonify({"error": "Like not found"}), 404
        db.session.delete(like)
        db.session.commit()
        return jsonify({"detail": "Post unliked"}), 204
