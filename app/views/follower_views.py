from flask import jsonify, request, Blueprint, app, current_app
from flask_restful import MethodView
from app.custom_pagination import CustomPagination
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.follower import Follow
from app.models.user import User
from app.models.follow_request import FollowRequest
from app.uuid_validator import is_valid_uuid
from app.utils.get_validate_user import get_user
from app.permissions.permission import Permission


class FollowApi(MethodView):
    """
    A class handle the follow functionality.
    User can follow and unfollow the user and get the follower or following list
    """
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()
    

    def get(self, user_id=None):
        """
         get the follower list of the current user.
         if user id is provided than follower list of that user
        """
        user = get_user(self.current_user_id)
        if user_id:
            user = get_user(user_id)

        else:
            user = get_user(self.current_user_id)

        # fetch the follower
        followers = user.followers.all()
        if not followers:
            return jsonify({"message": "No any follower of this user"})

        # added the data of id,username and image in the list of follower
        followers_list = [{
            "id": follower.follower.id,
            "username": follower.follower.username,
            "image": follower.follower.profile_pic if follower.follower.profile_pic else None,
        }
            for follower in followers
        ]
        # pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(followers_list, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = followers_list

        return jsonify(paginated_data), 200

    def post(self):
        """
        A Api to follow the user
        """

        current_user = User.query.get(self.current_user_id)
        data = request.json
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Provide user id"}), 400
        

        # fetch the user which user want to follow
        user_to_follow = get_user(user_id)
        if not user_to_follow:
            return jsonify({"error": "User does not exist"}), 400
        if self.current_user_id == user_id:
            return jsonify({"error": "You cant follow yourself"}), 400
        if user_to_follow.is_private:
            follow_request = FollowRequest(
                follower_id=self.current_user_id, following_id=user_id)
            
            db.session.add(follow_request)
            return jsonify({"message": f"follow request sent to the {user_id}"}), 201

        # check the user is follower or not of the user already
        follow_relationship = Follow.query.filter_by(
            follower_id=self.current_user_id, following_id=user_to_follow.id).first()

        # if user already follower of user than unfollow the user
        if follow_relationship:
            db.session.delete(follow_relationship)
            db.session.commit()
            return jsonify({"message": "Unfollowed"}), 200

        # follow the user
        follow = Follow(
            follower_id=self.current_user_id,
            following_id=user_to_follow.id,
        )
        db.session.add(follow)
        db.session.commit()

        return jsonify({"message": f"You are now following {user_to_follow.username}"}), 201


class FollowingApi(MethodView):
    """
    A api to get the following list of the current or the provided user
    """
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self, user_id=None):
        """
         function to get the following list
        """

        if user_id:
           user = get_user(user_id)

        # fetch the current user
        else:
            user = get_user(self.current_user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404
        # fetch the following list of the user
        following = user.following.all()
        if not following:
            return jsonify({"message": "No any user in following list"})

        # added the id, username and image of the user in the response
        following_list = [
            {
                "id": follow.following.id,
                "username": follow.following.username,
                "image": follow.following.profile_pic if follow.following.profile_pic else None,
            }
            for follow in following
        ]
        # pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        paginator = CustomPagination(following_list, page, per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = following_list

        return jsonify(paginated_data), 200
