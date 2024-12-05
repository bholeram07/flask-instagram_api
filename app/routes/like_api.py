from flask import app, jsonify, Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like_schema import LikeSchema
from app.db import db

like_api = Blueprint("like_api", __name__)


@like_api.route("/posts/<uuid:post_id>/likes", methods=["POST"])
@jwt_required()
def like(post_id=None):
    like_schema = LikeSchema()
    if request.method == "POST":
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error": "User not found"}), 404
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post not exist"})
        like = Like(post=post_id, user=current_user_id)
        db.session.add(like)
        db.session.commit()
        like_data = like_schema.dump(like)
        return jsonify(like_data), 201
