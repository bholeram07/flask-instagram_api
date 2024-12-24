from datetime import timedelta
from flask import Blueprint, jsonify, request, current_app, render_template
from app.models.user import db, User
from app.models.follower import Follow
from app.models.post import Post
from app.utils.allowed_file import allowed_file
from flask_restful import MethodView
from flask import Flask, jsonify
from flask import url_for
import requests
from app.utils.get_user_location import get_user_location
import secrets
import boto3
from config import Config
from werkzeug.utils import secure_filename
from app.generate_token import generate_verification_token

import datetime
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
from app.utils.tasks import send_mail,send_location_mail
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from app.utils.save_image import save_image
import os
from app.utils.validation import validate_and_load


class Signup(MethodView):
    """Api for user signup takes the username ,email and password"""
    signup_schema = SignupSchema()

    def post(self):
        print("i am in signup")
        # get the data
        data = request.get_json()
        print(data)
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        # if not password:
        #     return jsonify({"error": {
        #         "password":"Missing required field"}
        #                     }), 400
            
        # Check if the username or email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Another account is using this email"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "This username is not available please try another"}),400

        # validate the data
        user_data, errors = validate_and_load(self.signup_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400
        # Generate a verification token
        token = generate_verification_token(
            email, current_app.config['SECRET_KEY'])

        # Save temporary data
        user = User(email=email, username=username)
        # set the password
        user.set_password(password)
        db.session.add(user)

        # # Commit the changes
        db.session.commit()

        # # Generate the verification URL
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        # current_app.logger.info(verify_url)

        # Render the email template with the verification URL and username
        # html_message = render_template(
        #         'verify_email.html',
        #         username=username,
        #         verification_url=verify_url
        #     )
        # # Send the verification email
        # send_mail(email, html_message, "Please Verify Your Email")

        return jsonify({"message": "Verification email sent. Please check your email to complete signup."}), 200


class Login(MethodView):
    """ API for login takes the username or email and password"""
    # schema for login
    login_schema = LoginSchema()

    def post(self):
        # get the requested data
        data = request.get_json()
        username_or_email = data.get("username_or_email")
     
        # validate and loads the data
        user_data, errors = validate_and_load(self.login_schema, data)
        if errors:
            return jsonify({"errors": errors}),400

        if username_or_email:
            user = User.query.filter((User.username== username_or_email)|(User.email == username_or_email),User.is_verified == True,User.is_deleted==False) .first()
      
        # check user
        if not user:
            return jsonify({"error": "This email or username is not registered"}), 400
        if user.is_active == False:
            user.is_active = True
            db.session.commit()
        # check the user's password
        if not user.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        user_ip = request.remote_addr
        location = get_user_location(user_ip)
        # generate the token on valid credentials
        # access token
        access_token = create_access_token(
            identity=user.id, expires_delta=timedelta(hours=1)
        )
        # refresh token
        refresh_token = create_refresh_token(
            identity=user.id, expires_delta=timedelta(days=1)
        )
        # html_message = render_template(
        #     'login_activity.html',
        #     username=user.username,
        #     location = location,
        #     current_year=2024
        # )
        # send_location_mail(user.email,html_message)
        # expiration time of refresh and access token
        access_token_expiration = datetime.utcnow() + timedelta(hours=1)
        refresh_token_expiration = datetime.utcnow() + timedelta(days=1)
        return (
            jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "access_token_expiration_time": access_token_expiration,
                    "refresh_token_expiration_time": refresh_token_expiration,
                }
            ),
            200,
        )
        
class UpdatePassword(MethodView):
    """Api for password updation takes a current password and new password"""
    decorators = [jwt_required()]
    update_password_schema = UpdatePasswordSchema()

    def put(self):
        # get the user_id from the jwt token
        user_id = get_jwt_identity()
        # get the data
        data = request.json
        # validate and serialize the data
        user_data, errors = validate_and_load(
            self.update_password_schema, data)
        if errors:
            return jsonify({"errors" : errors}),400
        current_password = data["current_password"]
        new_password = data["new_password"]
        # get the user object by user_id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User Not found"}), 404
        # check the password
        if not user.check_password(data["current_password"]):
            return jsonify({"error": "Invalid credentials"}), 401
        # check with current password
        if current_password == new_password:
            return jsonify({"error": "old and new password not be same"}), 400
        # set the new password given by the user
        user.set_password(data["new_password"])
        # get the jwt id
        jti = get_jwt()["jti"]
        # set the expiration time
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]
        # get the redis_client
        redis_client = current_app.config["REDIS_CLIENT"]
        # store the token in the redis
        redis_client.setex(jti, expires_in, "blacklisted")

        return jsonify({"message": "Password Update Successfully"}), 200


class Logout(MethodView):
    """Api for the logout the user by invalidate the jwt token"""
    decorators = [jwt_required()]

    def delete(self):
        # get the jwt id
        jti = get_jwt()["jti"]
        # set the expiration time of the jwt token
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]
        # get the redis_client
        redis_client = current_app.config["REDIS_CLIENT"]
        # store the token in the redis
        redis_client.setex(jti, expires_in, "blacklisted")
        return jsonify(), 204


class ResetPasswordSendMail(MethodView):
    """An Api for the send the link with the token to user's mail for reset password """

    def post(self):
        data = request.json
        email = data.get("email")
        if not email:
            return jsonify({"error": "Invalid data"}), 400
        # get the user object by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Not registered"}), 400
        # generate the token
        token = secrets.token_urlsafe(32)
        # key for store in redis
        redis_key = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        # store the token in the redis with expiration time of 10 minutes
        redis_client.setex(redis_key, timedelta(minutes=10), str(user.id))
        # generate the reset link
        reset_link = f"http://127.0.0.1:5000/api/reset-password/{token}/"
        current_app.logger.info(reset_link)
        # html message for send mail to user email
        # html_message = render_template(
        #     "reset_password_email.html",
        #     subject="Reset Link Password",
        #     reset_link=reset_link,
        #     user_name=user.username,
        # )
        # # send email with link
        # send_mail(user.email, html_message, "Reset Link Password")

        return jsonify({"message": "Link sent successfully, please check your email"}), 200


class ResetPassword(MethodView):
    """Api for reset password takes the new password and confirm password"""
    reset_password_schema = ResetPasswordSchema()

    def post(self, token):
        data = request.json
        # takes the new password and confirm password
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        # validate and loads the data
        user_data = validate_and_load(self.reset_password_schema,data)
        if errors:
            return jsonify({"errors": errors})
        # check the password matches with the confirm-password
        if new_password != confirm_password:
            return jsonify({"error": "new password and confirm password must be equal"}), 400

        redis_key = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        # get the user_id from the redis
        user_id = redis_client.get(redis_key)

        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 400
        # get the user object from the user id
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        # check the passwoed
        if user.check_password(new_password):
            return jsonify({"error": "new and old password not be same"}), 401
        # set the new password entered by the user
        user.set_password(data["new_password"])
        db.session.commit()
        # delete the redis key
        redis_client.delete(redis_key)

        return jsonify({"message": "Password reset successfully"}), 200
    

class DeactivateAccount(MethodView):
    """An api for account deactivation of the user by the user password"""
    decorators = [jwt_required()]
    
    def put(self):
        data = request.json
        password = data.get("password")
        if not password:
            return jsonify({"error":{"password" : "Missing required field"} }),400
        current_user_id = get_jwt_identity()
        #get the user object
        user = User.query.filter_by(id=current_user_id, is_active=True).first()
        if not user :
            return jsonify({"error":"User not found"}),400
        #check the password
        if not user.check_password(password):
            return jsonify({"error":"Invalid Credentials"}),400
        #database operation
        user.is_active = False
        db.session.commit()
        return jsonify({"message" : "Your account is deactivated ,you can reactivate it by login again"}),202
    
    
class DeleteAccount(MethodView):
    """An Api for delete the user account"""
    decorators = [jwt_required()]
    
    def delete(self):
        #get the user_id by the jwt token
        current_user_id = get_jwt_identity()
        #get the user
        user = User.query.filter_by(id = current_user_id,is_active = True, is_deleted = False).first()
        if not user:
            return jsonify({"error" : "User not exist"}),404
        #database opearation of delete
        user.is_deleted = True
        db.session.commit()
        return jsonify(),204