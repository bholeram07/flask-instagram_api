from flask import jsonify, request, Blueprint, app, current_app
from flask_restful import MethodView
from app.custom_pagination import CustomPagination
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.follower import Follow
from app.models.user import User
from app.uuid_validator import is_valid_uuid


class FollowApi(MethodView):
    decorators = [jwt_required()]

    def get(self, username=None):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
        else:
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({"error": "Unauthorized"}), 403

        followers = user.followers.all()
        follower_usernames = [follower.follower.username for follower in followers]
        return jsonify({"followers": follower_usernames}), 200

    def post(self):
        current_user_id = get_jwt_identity()
        data = request.json
        username = data.get("username")
        if not username:
            return jsonify({"error": "Provide username"}), 400

        user_to_follow = User.query.filter_by(username=username).first()
        if not user_to_follow:
            return jsonify({"error": "User does not exist"}), 400

        current_user = User.query.get(current_user_id)
        if current_user.id == user_to_follow.id:
            return jsonify({"error": "you cannot follow yourself"}), 400

        if current_user.is_following(user_to_follow):
            return jsonify({"detail": f"You are already following {username}"}), 400

        follow = Follow(
            follower_id=current_user.id,
            following_id=user_to_follow.id,
        )
        db.session.add(follow)
        db.session.commit()

        return jsonify({"detail": f"You are now following {username}"}), 201

    def delete(self, username):
        current_user_id = get_jwt_identity()
        if not username:
            return jsonify({"error": "username is required"})
        user_to_unfollow = User.query.filter_by(username=username).first()

        if not user_to_unfollow:
            return jsonify({"error": "User not exist"}), 400

        current_user = User.query.get(current_user_id)
        if current_user.id == user_to_unfollow.id:
            return jsonify({"error": "You cant unfollow yourself"}), 400

        follow = Follow.query.filter_by(
            follower_id=current_user.id, following_id=user_to_unfollow.id
        ).first()
        if not follow:
            return jsonify({"detail": f"You are not following {username}"}), 400

        db.session.delete(follow)
        db.session.commit()
        reverse_follow = Follow.query.filter_by(
            follower_id=user_to_unfollow.id, following_id=current_user.id
        ).first()
        if reverse_follow:
            return (
                jsonify(
                    {
                        "detail": f"You have unfollowed {username}, but they are still following you."
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "detail": f"You have unfollowed {username} and they are no longer following you."
                    }
                ),
                200,
            )


class FollowingApi(MethodView):
    decorators = [jwt_required()]

    def get(self, username=None):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if username:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

        if not user:
            return jsonify({"error": "User not found"}), 404

        following = user.following.all()
        following_usernames = [follow.following.username for follow in following]

        return jsonify({"following": following_usernames}), 200


