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

    def get(self, user_id=None):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user_id:
            if not is_valid_uuid(user_id):
                return jsonify({"error": "Invalid uuid format"}),400
            user = User.query.filter_by(id=user_id).first()
            if not user:
                return jsonify({"error": "User not found"}), 404
        else:
            user = User.query.get(current_user_id)
            if not user:
                return jsonify({"error": "Unauthorized"}), 403

        followers = user.followers.all()
        followers_data = [ {
                "id": follower.follower.id,
                "username": follower.follower.username,
                "image": follower.follower.profile_pic if follower.follower.profile_pic else None,
            }
            for follower in followers
        ]
        return jsonify(followers_data), 200
    
    
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "Provide user id"}), 400

        user_to_follow = User.query.filter_by(id=user_id).first()
        if not user_to_follow:
            return jsonify({"error": "User does not exist"}), 400


        follow_relationship = current_user.is_following(user_to_follow)
        if follow_relationship:
            db.session.delete(follow_relationship)
            db.session.commit()
            return jsonify({"detail": "Unfollowed"}), 200

        follow = Follow(
            follower_id=current_user.id,
            following_id=user_to_follow.id,
        )
        db.session.add(follow)
        db.session.commit()

        return jsonify({"detail": f"You are now following {user_to_follow.username}"}), 201

    



class FollowingApi(MethodView):
    decorators = [jwt_required()]

    def get(self, user_id=None):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user_id:
            user = User.query.filter_by(username=username).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

        if not user:
            return jsonify({"error": "User not found"}), 404

        following = user.following.all()
        following_list = [
        {
            "id": follow.following.id,
            "username": follow.following.username,
            "image": follow.following.profile_pic if follow.following.profile_pic else None,
        }
        for follow in following
        ]

        return jsonify(following_list), 200

        


