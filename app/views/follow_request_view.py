from sqlalchemy.exc import IntegrityError
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import MethodView
from app.uuid_validator import is_valid_uuid
from app.models.user import User
from app.models.follow_request import FollowRequest
from app.models.follower import Follow
from app.extensions import db
from app.utils.get_validate_user import get_user
from app.pagination_response import paginate_and_serialize
from app.utils.get_limit_offset import get_limit_offset


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
        if not user:
            return jsonify("user not exist"), 404

        # fetch the follow request
        followrequest = FollowRequest.query.filter_by(
            follower_id=self.current_user_id, following_id=user_id).first()
        if not followrequest:
            return jsonify({"error": "you not send  any follow request to this user"}), 400

        # database operation to delete the follow request
        db.session.delete(follow_request)
        db.session.commit()


class FollowrequestAccept(MethodView):
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """A function to accept or reject the follow request"""
        # Get the user_id from the request
        user_id = request.json.get("user_id")
        user = get_user(user_id)
        if not is_valid_uuid(user_id):
            return jsonify({"error": "Invalid UUID format"}), 400
        if not user:
            return jsonify({"error": "User not found"}), 404

        current_user = get_user(self.current_user_id)

        # Check that user account is private
        if not current_user.is_private:
            return jsonify({"error": "You can't implement this request; your account is public"}), 400

        if user_id == self.current_user_id:
            return jsonify({"error": "You can't accept your own follow request follow request to yourself"}), 400

        # Take the action from query params
        action = request.args.get("action", default="accept").lower()

        # Accept the request
        if action == "accept":
            followrequest = FollowRequest.query.filter_by(
                following_id=self.current_user_id, follower_id=user_id).first()
            if not followrequest:
                return jsonify({"error": "Follow request not found"}), 404

            db.session.delete(followrequest)
            db.session.commit()

            # Check if follow relationship already exists
            existing_follow = Follow.query.filter_by(
                follower_id=user_id,
                following_id=self.current_user_id
            ).first()
            if existing_follow:
                return jsonify({"message": "User is already your follower"}), 200
            # Follow the user
            follow = Follow(
                follower_id=user_id,
                following_id=self.current_user_id,
            )
            # Add the follow to the database atomic operation
            try:
                db.session.add(follow)
                db.session.commit()
                return jsonify({"message": "Follow request accepted; now the user is your follower"}), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": "Could not add follower due to database error"}), 500

        # Reject the request
        if action == "reject":
            followrequest = FollowRequest.query.filter_by(
                following_id=self.current_user_id, follower_id=user_id).first()
            if not followrequest:
                return jsonify({"error": "Follow request not found"}), 404
            db.session.delete(followrequest)
            db.session.commit()
            return jsonify({"message": "Follow request rejected"}), 200

        return jsonify({"error": "Invalid action"}), 400

    def get(self):
        """A function to get the follow request"""
        
        user = User.query.get(self.current_user_id)
        if not user.is_private:
            return jsonify({"error":"You can not implement this request as your account is public"}),400
        # page_number,offset,page_size
        page_number, offset, page_size = get_limit_offset()

        # fetch the follow request
        
        followrequest = FollowRequest.query.filter_by(
            following_id=self.current_user_id).offset(offset).limit(page_size).all()
        # serialize the follow request
        result = []
        result = [
            {
                "sender_id": req.follower.id,
                "username" : req.follower.username,
                "profile_pic" : req.follower.profile_pic

            } for req in followrequest
        ]
        return paginate_and_serialize(result, page_number, page_size)
