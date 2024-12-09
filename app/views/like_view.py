from flask import app, jsonify, Blueprint, request, current_app
from flask_restful import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like_schema import LikeSchema
from app.uuid_validator import is_valid_uuid
from app.extensions import db



class LikeAPi(MethodView):
    like_schema = LikeSchema()
    decorators = [jwt_required()]

    def post(self,post_id =None):
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
            db.session.delete(like)
            db.session.commit()
            return jsonify({"detail": "Post unliked"}), 204
        else:
            like = Like(post=post_id, user=current_user_id)
        db.session.add(like)
        db.session.commit()
        post_data = {"id": post.id, "title": post.title, "content": post.content}
        like_data = self.like_schema.dump(like)
        user = User.query.get(current_user_id)
        user_data = {
            "id": user.id,
            "username": user.username,
            "profile_pic": user.profile_pic if user.profile_pic else None,
        }
        like_data["post"] = post_data
        like_data["user"] = user_data
        like_data["liked_at"] = like.created_at.isoformat()

        return jsonify(like_data), 201

       
