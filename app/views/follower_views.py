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
        followers_list = [ {
                "id": follower.follower.id,
                "username": follower.follower.username,
                "image": follower.follower.profile_pic if follower.follower.profile_pic else None,
            }
            for follower in followers
        ]
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(followers_list, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = followers_list 

        return jsonify(paginated_data), 200
    
    
    def post(self):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        data = request.json
        user_id = data.get("user_id")
        if not user_id:
            return jsonify({"error": "Provide user id"}), 400
        if not is_valid_uuid(user_id):
            return jsonify({"error" : "Invalid uuid format"}),400

        user_to_follow = User.query.filter_by(id=user_id).first()
        if not user_to_follow:
            return jsonify({"error": "User does not exist"}), 400


        follow_relationship = Follow.query.filter_by(
            follower_id=current_user_id, following_id=user_to_follow.id).first()

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
            user = User.query.filter_by(id=user_id).first()
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

        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(following_list, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = following_list

        return jsonify(paginated_data), 200
        


