from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import MethodView
from app.uuid_validator import is_valid_uuid
from app.models.user import User
from app.models.follow_request import FollowRequest
from app.models.follower import Follow
from app.extensions import db
from app.utils.get_validate_user import get_user


class FollowRequestWithdraw(MethodView):
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def delete(self, user_id):
        """An api to withdraw the follow request"""
        # if user id is not goven
        if not user_id:
            return jsonify({"error": "user id is required"}), 400
        if not is_valid_uuid(user_id):
            return jsonify({"error": "Invalid UUid format"}), 400
        # fetch the user
        user = get_user(user_id)
        # fetch the follow request
        followrequest = FollowRequest.query.filter_by(
            follower_id=self.current_user_id, following_id=user_id).first()
        if not followrequest:
            return jsonify({"error": "you not send  any follow request to this user"}), 400
        db.session.delete(follow_request)
        db.session.commit()


class FollowrequestAccept(MethodView):
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """"A function to accept or reject the follow request"""
        # get the user_id from the request
        user_id = request.json.get("user_id")
        user = get_user(user_id)
        current_user = get_user(self.current_user_id)
    
        # check that user account is private or not
        if not current_user.is_private:
            return jsonify({"error": "You can't implement this request your account is public"}), 400
        # take the action from query params
        action = request.args.get("action", default="accept")
        # accept the request
        if action == "accept":
            followrequest = FollowRequest.query.filter_by(
                following_id=self.current_user_id, follower_id=user_id).first()
            if not followrequest:
                return jsonify({"errors":"Follow request not found"}),404
            db.session.delete(followrequest)
            db.session.commit()#atomicity
           
             # follow the user

            follow = Follow(
                follower_id=user_id,
                following_id=self.current_user_id,
            )
            db.session.add(follow)
            db.session.commit()
            return jsonify({"message": "Follow request accepted now user is your follower"}), 201
        # reject the request
        if action == "reject":
            followrequest = FollowRequest.query.filter_by(
                following_id=self.current_user_id, follower_id=user_id).first()
            db.session.delete(followrequest)
            db.session.commit()
            return jsonify({"message": "Follow request rejected"}), 400
        else:
            return jsonify({"error": "Invalid action"}), 404

    def get(self):
        followrequest = FollowRequest.query.filter_by(
            following_id=self.current_user_id).all()
        if not followrequest:
            return jsonify({"error": "Not any follow request"}), 404
        return jsonify({"message": "yes"}), 200
