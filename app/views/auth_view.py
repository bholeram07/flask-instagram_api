from flask_jwt_extended import get_jwt
from datetime import timedelta,datetime
from flask import Blueprint, jsonify, request, current_app, render_template,Response
from app.models.user import db, User
from app.models.follower import Follow
from app.models.post import Post
from app.constraints import get_reset_password_url
from flask_restful import MethodView
from flask import Flask, jsonify
from flask import url_for
import requests
import secrets
from config import Config
from app.generate_token import generate_verification_token
from app.utils.get_validate_user import get_user
from app.utils.blacklist_jwt_token import blacklist_jwt_token
from app.schemas.user_schema import (
    SignupSchema,
    LoginSchema,
    UpdatePasswordSchema,
    ResetPasswordSchema,
    ProfileSchema,
)
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    create_refresh_token,
    get_jwt,
)
from datetime import datetime, timedelta
from app.tasks import send_mail
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
import os
from typing import Tuple, Union,Optional




class Signup(MethodView):
    """API for user signup takes the username, email, and password."""

    signup_schema: SignupSchema = SignupSchema()

    def post(self) -> Tuple[Union[dict, str], int]:
        """Handles the POST request for user signup."""
        # Get the data
        data: dict = request.get_json()
        email: str = data.get('email', '')
        username: str = data.get('username', '')
        password: str = data.get('password', '')

        # Validate the data
        user_data, errors = validate_and_load(self.signup_schema, data)
        if errors:
            return {"errors": errors}, 400

        # Check if the username or email already exists
        if User.query.filter_by(email=email).first():
            return {"error": "Another account is using this email"}, 409
        if User.query.filter_by(username=username).first():
            return {"error": "This username is not available. Please try another"}, 409

        try:
            # Begin transaction
            user = User(email=email, username=username)
            # Set the password
            user.set_password(password)
            db.session.add(user)
            # Commit the changes
            db.session.commit()

            # Generate a verification token
            token: str = generate_verification_token(
                email, current_app.config['SECRET_KEY']
            )
            # Generate the verification URL
            verify_url: str = url_for(
                'auth.verify_email', token=token, _external=True)
            current_app.logger.info(verify_url)

            # Render the email template with the verification URL and username
            html_message: str = render_template(
                'verify_email.html',
                username=username,
                verification_url=verify_url
            )

            # Send the verification email asynchronously
            send_mail.delay(email, html_message, "Please Verify Your Email")

            return {"message": "Verification email sent. Please check your email to complete signup."}, 200

        except SQLAlchemyError as e:
            # Rollback the transaction if any exception occurs
            db.session.rollback()
            current_app.logger.error(f"Database error during signup: {str(e)}")
            return jsonify({"errors": "some error occured during signup"}),400
      


class Login(MethodView):
    """API for login takes the username or email and password."""

    # Schema for login
    login_schema: LoginSchema = LoginSchema()

    def post(self) -> Tuple[Union[dict, str], int]:
        """Handles the POST request for user login."""
        # Get the requested data
        data: dict = request.get_json()
        username_or_email: str = data.get("username_or_email", '')

        # Validate and load the data
        user_data, errors = validate_and_load(self.login_schema, data)
        if errors:
            return {"errors": errors}, 400

        # Retrieve the user by username or email
        user: Union[User, None] = None
        if username_or_email:
            user = User.query.filter(
                (User.username == username_or_email) | (
                    User.email == username_or_email),
                User.is_verified == True,
                User.is_deleted == False
            ).first()

        # Check user existence
        if not user:
            return {"error": "Invalid credentials"}, 400

        # Check the password
        if not user.check_password(data["password"]):
            return {"error": "Invalid credentials"}, 401

        # Reactivate user account if it was suspended
        if not user.is_active:
            user.is_active = True
            db.session.commit()
        # Generate the tokens on valid credentials
        
        # Access token
        access_token: str = create_access_token(
            identity=user.id, expires_delta=timedelta(hours=1)
        )
        # Refresh token
        refresh_token: str = create_refresh_token(
            identity=user.id, expires_delta=timedelta(days=1)
        )

        # Token expiration times
        access_token_expiration: datetime = datetime.utcnow() + timedelta(hours=1)
        refresh_token_expiration: datetime = datetime.utcnow() + timedelta(days=1)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_token_expiration_time": access_token_expiration.isoformat(),
            "refresh_token_expiration_time": refresh_token_expiration.isoformat(),
        }, 200


class UpdatePassword(MethodView):
    """API for password updation takes a current password and new password"""
    decorators = [jwt_required()]
    update_password_schema = UpdatePasswordSchema()

    def put(self) -> Tuple[Union[dict,str],int] : 
        # Get the user_id from the JWT token
        user_id = get_jwt_identity()
        data : dict = request.get_json()
        # Fetch user and validate current password
        user: Union[User,None] = get_user(user_id)
        
        # get the password from the request data
        current_password:str = data.get("current_password")
        new_password:str = data.get("new_password")
        if not current_password:
            return jsonify({"errors": {"current_password": "Missing data for required field"}}), 400

        # check the password
        if not user.check_password(current_password):
            return jsonify({"error": "Invalid credentials"}), 401

        # check with previous password
        if current_password == new_password:
            return jsonify({"error": "Old and new passwords must not be the same"}), 400

        # validate the data
        user_data, errors = validate_and_load(
            self.update_password_schema, data)
        # if errors
        if errors:
            return jsonify({"errors": errors}), 400

        # Atomic operation
        try:
            # Update the user's password
            user.set_password(new_password)
            db.session.add(user)  # Add the updated user to the session
            # Blacklist the current JWT
            blacklist_jwt_token()
            # Commit the transaction
            db.session.commit()
            return jsonify({"message": "Password updated successfully"}), 202

        except Exception as e:
            # Rollback the transaction in case of an error
            db.session.rollback()
            current_app.logger.error(f"Error during password update: {str(e)}")
            return jsonify({"error": "An error occurred while updating the password"}), 500


class Logout(MethodView):
    """Api for the logout the user by invalidate the jwt token"""
    decorators = [jwt_required()]

    def delete(self) -> int:
        # Blacklist the current JWT
        blacklist_jwt_token()
        return jsonify(), 204


class ResetPasswordSendMail(MethodView):
    """An Api for the send the link with the token to user's mail for reset password """

    def post(self)-> Tuple[Union[dict,str],int]:
        data: dict = request.get_json()
        email: str = data.get("email")
        if not email:
            return jsonify({"errors": {"email": "Missing data for required field."}}), 400
        # get the user object by email
        user : Union[User,None] = User.query.filter_by(
            email=email, is_verified=True, is_active=True, is_deleted=False).first()
        if not user:
            return jsonify({"error": "Invalid Credentials"}), 400
        # generate the token
        token:str = secrets.token_urlsafe(32)
        # key for store in redis
        redis_key = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        # store the token in the redis with expiration time of 10 minutes
        redis_client.setex(redis_key, timedelta(minutes=10), str(user.id))
        # generate the reset link
        reset_link:str = get_reset_password_url(token)
        current_app.logger.info(reset_link)
        # html message for send mail to user email
        html_message:str = render_template(
            "reset_password_email.html",
            subject="Reset Link Password",
            reset_link=reset_link,
            user_name=user.username,
        )
        # send email with link
        send_mail.delay(user.email, html_message, "Reset Link Password")

        return jsonify({"message": "Link sent successfully, please check your email"}), 200


class ResetPassword(MethodView):
    """Api for reset password takes the new password and confirm password"""
    reset_password_schema = ResetPasswordSchema()

    def post(self, token) -> Tuple[Union[dict, str], int]:
        data :dict = request.get_json()
        # takes the new password and confirm password
        new_password:str = data.get("new_password")
        confirm_password:str = data.get("confirm_password")
        # validate and loads the data
        user_data, errors = validate_and_load(self.reset_password_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400
        redis_key : str = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        # get the user_id from the redis
        user_id = redis_client.get(redis_key)

        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 400
        # get the user object from the user id
        user : Union[User,None] = get_user(user_id)
        # check the passwoed
        if user.check_password(new_password):
            return jsonify({"error": "new and old password not be same"}), 400
        # check the password matches with the confirm-password
        if new_password != confirm_password:
            return jsonify({"error": "new password and confirm password must be equal"}), 400

        # set the new password entered by the user
        try:

            user.set_password(data["new_password"])
            db.session.commit()
            # delete the redis key
            redis_client.delete(redis_key)

            return jsonify({"message": "Password reset successfully"}), 200

        except Exception as e:
            # Rollback the transaction in case of an error
            db.session.rollback()
            current_app.logger.error(f"Error during password update: {str(e)}")
            return jsonify({"error": "An error occurred while updating the password"}), 500


class DeactivateAccount(MethodView):
    """An api for account deactivation of the user by the user password"""
    decorators = [jwt_required()]

    def put(self) -> Tuple[Union[dict, str],int]:
        data:dict = request.get_json()
        password : str = data.get("password")
        if not password:
            return jsonify({"error": {"password": "Missing required field"}}), 400
        current_user_id = get_jwt_identity()
        # get the user object
        user : Union[User,None] = get_user(current_user_id)
        # check the password
        if not user.check_password(password):
            return jsonify({"error": "Invalid Credentials"}), 400
        # database operation
        try:
            blacklist_jwt_token()
            user.is_active = False
            db.session.commit()

            return jsonify({"message": "Your account is deactivated ,you can reactivate it by login again"}), 202
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error during account deactivation: {str(e)}")
            return jsonify({"error": "An error occurred while deactivating the account"}), 500


class DeleteAccount(MethodView):
    """An Api for delete the user account"""
    decorators = [jwt_required()]

    def delete(self)-> int :
        # get the user_id by the jwt token
        current_user_id = get_jwt_identity()
        # get the user
        user :Optional[User]= get_user(current_user_id)
        # database opearation of delete
        try:

            blacklist_jwt_token()
            user.soft_delete()
            db.session.commit()
            return jsonify(), 204
        
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error during account deletion: {str(e)}")
            return jsonify({"error": "An error occurred while deleting the account"}), 500
