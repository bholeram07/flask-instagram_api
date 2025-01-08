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
from app.pagination_response import paginate_and_serialize
from app.utils.get_limit_offset import get_limit_offset
from app.permissions.permissions import Permission


class FollowApi(MethodView):
    """
    A class handle the follow functionality.
    User can follow and unfollow the user and get the follower or following list
    """
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    @Permission.user_permission_required
    def get(self, user_id=None):
        """
         get the follower list of the current user.
         if user id is provided than follower list of that user
        """
        # if user_id is provided than get the follower list of that user
        if user_id:
            # get the user
            user = get_user(user_id)
            # if user not exist
            if not user:
                return jsonify({"error": "User does not exist"}), 404

        # if user_id is not provided than get the follower list of the current user
        else:
            user = User.query.filter_by(id = self.current_user_id).first()

        # get the page,offset and page_size
        page, offset, page_size = get_limit_offset()

        # fetch the follower
        followers = user.followers.offset(offset).limit(page).all()

        # added the data of id,username and image in the list of follower
        followers_list = [{
            "id": follower.follower.id,
            "username": follower.follower.username,
            "image": follower.follower.profile_pic if follower.follower.profile_pic else None,
        }
            for follower in followers
        ]
        # pagination
        return paginate_and_serialize(followers_list, page, page_size)

    def post(self):
        """
        A function to follow the user.. if account is private than send the follow request,
        if request already exist than withdraw the request,
        and if account is public than follow and if already a follower than 
        unfolllow
        takes the user_id which user want to folllow
        """
        # get the current user
        current_user = User.query.filter_by(id = self.current_user_id).first()

        # get the data from the request
        data = request.json
        user_id = data.get("user_id")

        # if user_id is not provided
        if not user_id:
            return jsonify({"error": "Provide user id"}), 400

        # if user_id is not valid
        if not is_valid_uuid(user_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        # get the user to follow
        user_to_follow = get_user(user_id)

        # if user not exist
        if not user_to_follow:
            return jsonify({"error": "User does not exist"}), 400

        # user can't follow himself
        if self.current_user_id == user_id:
            return jsonify({"error": "You cant follow yourself"}), 400

        # if user account is private than send the follow request
        if user_to_follow.is_private:
            # fetch the follow request
            follow_request = FollowRequest.query.filter_by(
                follower_id=self.current_user_id, following_id=user_id).first()

            # if follow request already exist than withdraw the follow request
            if follow_request:
                db.session.delete(follow_request)
                db.session.commit()

            # send the follow request
            else:
                follow_relationship = Follow.query.filter_by(
                    follower_id=self.current_user_id, following_id=user_to_follow.id).first()

            # if user follow the user already than not send the request
                if follow_relationship:
                    return jsonify({"message": "You are already following the user,request not sent"}), 400

                # send the follow request
                else:
                    follow_request = FollowRequest(
                        follower_id=self.current_user_id, following_id=user_id)

                    # database operation
                    db.session.add(follow_request)
                    db.session.commit()
                    return jsonify({"message": f"follow request sent to the user"}), 200
            # return statement
            return jsonify({"message": f"follow request withdraw from the {user_id}"}), 200

        # for public account : check the user is follower or not of the user already
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
    decorators = [jwt_required(), Permission.user_permission_required]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self, user_id=None):
        """
         function to get the following list
        """

        if user_id:
            user = get_user(user_id)
            if not user:
                return jsonify({"error": "User not exist"}), 404

        # fetch the current user
        else:
            user = User.query.filter_by(id = self.current_user_id).first()

        if not user:
            return jsonify({"error": "User not found"}), 404
        # fetch the following list of the user
        # get the page_number,page_size and offset
        page_number, offset, page_size = get_limit_offset()
        following = user.following.offset(offset).limit(page_size).all()

        # added the id, username and image of the user in the response
        following_list = [
            {
                "id": follow.following.id,
                "username": follow.following.username,
                "image": follow.following.profile_pic if follow.following.profile_pic else None,
            }
            for follow in following
        ]
        return paginate_and_serialize(following_list, page_number, page_size)
