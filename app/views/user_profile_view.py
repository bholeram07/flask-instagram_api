from app.utils.s3_utils import get_s3_client
import os
from app.utils.validation import validate_and_load
from app.uuid_validator import is_valid_uuid
from app.utils.tasks import send_mail
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.schemas.user_schema import ProfileSchema
from werkzeug.utils import secure_filename
from config import Config
import boto3
import secrets
from flask_restful import MethodView
from app.models.post import Post
from app.models.follower import Follow
from app.models.user import db, User
from flask import Blueprint, jsonify, request, current_app
from datetime import timedelta
from app.utils.update_profile_pic import update_profile_pic


class UserProfile(MethodView):
    """
    A Api provides profile functionality to the user
    """
    profile_schema = ProfileSchema()
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self, user_id=None):
        """
        Function to get the profile of the user
        """
        if user_id:
            # check the validation of the user_id
            is_valid_uuid(user_id)
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
        else:
            user = User.query.get(self.current_user_id)

        # get the follower ,following and post count of the user
        followers_count = Follow.query.filter_by(
            following_id=user.id).count()
        following_count = Follow.query.filter_by(
            follower_id=user.id).count()

        post_count = Post.query.filter_by(
            user=user.id, is_deleted=False).count()

        profile_data = self.profile_schema.dump(user)
        profile_data.update({
            "followers": followers_count,
            "following": following_count,
            "posts": post_count,
        })

        return jsonify(profile_data)

    def patch(self):
        """
        Function to update the profile of the user
        """
        user = User.query.get(self.current_user_id)
        file = request.files
        if file:
            image = request.files.get("profile_pic")
            try:
                update_profile_pic(user, image)
            except Exception as e:
                return jsonify({"error": e})

        data = request.form or request.json
        if "is_private" in data:
            is_private = data.get("is_private")
            # check the field is boolean or not
            if isinstance(is_private, bool):
                user.is_private = is_private

        if "other_social" in data:
            other_social = data.get("other_social")
            # handle the blank string
            user.other_social = None if not other_social.strip() else other_social

        if "username" in data:
            username = data.get("username")
            # Check if username is already taken or blank
            if username.strip() and username != user.username:
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    return jsonify({"error": "This username is already taken"}), 400

                if user.username_change_timestamp is None:
                    user.username_change_timestamp = datetime.now()
                    user.username.change_count = 0

                # make the json seralizable
                now = datetime.now(timezone.utc)
                last_change_time = user.username_change_timestamp
                days_since_last_change = (last_change_time - now).days
                if days_since_last_change > 0 and user.username_change_count >= 3:
                    return jsonify({"error": "You can change your username only 3 times in 15 days"}), 400

                if days_since_last_change >= 0:
                    user.username_change_timestamp = datetime.now()
                    user.username_change_count = 0
                user.username = username
                # user.username_change_timestamp = now
                user.username_change_count += 1
        if "bio" in data:
            bio = data.get("bio")
            user.bio = None if not bio.strip() else data["bio"]
        db.session.commit()
        updated_data = self.profile_schema.dump(user)
        return jsonify(updated_data), 202
