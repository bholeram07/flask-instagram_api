from app.utils.s3_utils import get_s3_client
import os
from app.utils.validation import validate_and_load
from app.uuid_validator import is_valid_uuid
from app.tasks import send_mail
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
from app.utils.update_profile_pic import update_profile_pic
from app.utils.ist_time import current_time_ist


class UserProfile(MethodView):
    """
    A RESTful API class providing profile functionality to the user.
    This includes retrieving and updating user profile information.
    """
    # Use the ProfileSchema for serializing and deserializing profile data
    profile_schema = ProfileSchema()
    decorators = [jwt_required()]

    # Get the ID of the currently logged-in user from the JWT token
    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self, user_id=None):
        """
        Retrieve the profile of the user.
        If a `user_id` is provided, retrieve the profile for that user.
        If no `user_id` is provided, retrieve the profile of the currently logged-in user.
        """
        if user_id:
            # Validate the UUID format of the provided user ID
            if not is_valid_uuid(user_id):
                return jsonify({"error": "Invalid UUID format"}), 400

            # Query for the user by ID, ensuring the user is active and not deleted
            user = User.query.filter_by(
                id=user_id, is_active=True, is_deleted=False).first()
            if not user:
                return jsonify({"error": "User not found"}), 404

         # Retrieve the currently logged-in user's profile
        else:
            user = User.query.get(self.current_user_id)

        # Count followers, following, and posts for the user
        followers_count = Follow.query.filter_by(following_id=user.id).count()
        following_count = Follow.query.filter_by(follower_id=user.id).count()

        # get the post count of the user
        post_count = Post.query.filter_by(
            user=user.id, is_deleted=False).count()

        # Serialize the user's profile data and add additional counts
        profile_data = self.profile_schema.dump(user)
        profile_data.update({
            "followers": followers_count,
            "following": following_count,
            "posts": post_count,
        })

        return jsonify(profile_data)

    def patch(self):
        """
        Update the profile of the currently logged-in user.
        Allows updating fields such as username, bio, is_private, and profile picture.
        """
        # Retrieve the currently logged-in user's record
        user = User.query.get(self.current_user_id)

        # Handle file uploads, specifically the profile picture
        file = request.files

        # if the file is provided
        if file and "profile_pic" in file:
            image = request.files.get("profile_pic")
            try:
                update_profile_pic(user, image)  # Update the profile picture
            except Exception as e:
                return jsonify({"error": str(e)})

        # Load request data (from form or JSON)
        data = None
        try:
            data = request.form or request.json or {}
        except Exception as e:
            if not file:
                return jsonify({"error": "Provide data to update"}), 400
        if not data and not file:
            return jsonify({"error": "Provide data to update"}), 400
        if file and not data:
            return jsonify(self.profile_schema.dump(user)), 202

        # Update the `is_private` field if provided and is a boolean
        if "is_private" in data:
            is_private = data.get("is_private")
            if isinstance(is_private, bool):
                user.is_private = is_private

        # Update `other_social` field if provided
        if "other_social" in data:
            other_social = data.get("other_social")
            user.other_social = None if not other_social.strip() else other_social

        # Handle username updates with validation
        if "username" in data:
            username = data.get("username")
            if username.strip() and username != user.username:
                # Check if the username is already taken
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    return jsonify({"error": "This username is already taken"}), 400

                # Initialize or validate username change limits
                if user.username_change_timestamp is None:
                    user.username_change_timestamp = datetime.now(timezone.utc)
                    user.username_change_count = 0

                now = datetime.now(timezone.utc)
                last_change_time = user.username_change_timestamp
                days_since_last_change = (now - last_change_time).days

                # Restrict username changes to 3 times in 15 days
                if days_since_last_change < 15 and user.username_change_count >= 3:
                    return jsonify({"error": "You can change your username only 3 times in 15 days"}), 400

                # Reset the count if 15 days have passed
                if days_since_last_change >= 15:
                    user.username_change_timestamp = now
                    user.username_change_count = 0

                user.username = username
                user.username_change_count += 1

        # Update `bio` field if provided
        if "bio" in data:
            bio = data.get("bio")
            user.bio = None if not bio.strip() else bio

        # Commit changes to the database
        try:
            user.updated_at = current_time_ist()
            db.session.commit()
            updated_data = self.profile_schema.dump(user)
            return jsonify(updated_data), 202
        except Exception as e:
            # Rollback on failure and log the error
            db.session.rollback()
            current_app.logger.error(f"Error updating profile: {str(e)}")
            return jsonify({"error": "An error occurred while updating the profile"}), 500
