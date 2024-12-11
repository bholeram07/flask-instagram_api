from flask import app, jsonify, Blueprint, request, current_app
from flask_restful import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.likes import Like
from app.models.post import Post
from app.models.user import User
from app.schemas.like_schema import LikeSchema
from app.uuid_validator import is_valid_uuid
from app.extensions import db
from app.custom_pagination import CustomPagination
from sqlalchemy import desc


class LikeAPi(MethodView):
    like_schema = LikeSchema()
    decorators = [jwt_required()]

    def post(self, post_id=None):
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

        like = Like.query.filter_by(
            post=post_id, user=current_user_id, is_deleted=False).first()
        if like:
            db.session.delete(like)
            db.session.commit()
            return jsonify({"detail": "Post unliked"}), 200
        else:
            like = Like(post=post_id, user=current_user_id)
        db.session.add(like)
        db.session.commit()
        post_data = {"id": post.id, "title": post.title,
                     "content": post.content}
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

    def get(self, post_id):
        current_user_id = get_jwt_identity()
        if not post_id:
            return jsonify({"error": "Please provide post id "}), 400

        if not is_valid_uuid(post_id):
            return {"error": "Invalid UUID format"}, 400

        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        likes = Like.query.filter_by(post=post_id).order_by(
            desc(Like.created_at)).all()
        likes_count = Like.query.filter_by(post=post_id).count()

        if likes_count == 0:
            return jsonify({"error": "No likes found on this post"}), 404

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(likes, page, per_page)
        paginated_data = paginator.paginate()

        paginated_data["items"] = self.like_schema.dump(
            paginated_data["items"], many=True)
        paginated_data["likes_count"] = likes_count

        return jsonify(paginated_data), 200
