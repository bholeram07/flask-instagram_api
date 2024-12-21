from datetime import timedelta
from flask import Blueprint, jsonify, request, current_app, render_template
from app.models.user import db, User
from app.models.follower import Follow
from app.models.post import Post
from app.utils.allowed_file import allowed_file
from flask_restful import MethodView
from flask import Flask, jsonify
from flask import url_for

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
from app.utils.tasks import send_mail
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from app.utils.save_image import save_image
import os
from app.utils.s3_utils import create_bucket


def setup_bucket(bucket_name):
    s3_client = current_app.s3_client
    create_bucket(s3_client, bucket_name)

class Signup(MethodView):
    user_schema = SignupSchema()
    def post(self):


        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        # Check if the username or email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 400

        # Generate a verification token
        token = generate_verification_token(
            email, current_app.config['SECRET_KEY'])

        # Save temporary data (example with Redis or a temp table, you can customize this)
        temp_data = {"username": username, "email": email, "password": password}
        # Here, save `temp_data` securely. This could be in Redis or a temporary table.

        # Send verification email
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        # send_email(email, 'Verify Your Email',
        #         f'Click the link to verify your email: {verify_url}')
        print(verify_url)

        return jsonify({"message": "Verification email sent. Please check your email to complete signup."}), 200


    
class Login(MethodView):
    login_schema = LoginSchema()

    def post(self):
        data = request.get_json()
        try:
            user_data = self.login_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            return jsonify({"error": "This email is not registered"}), 400

        if not user.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        access_token = create_access_token(
            identity=user.id,expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=user.id, expires_delta=timedelta(days=1)
        )
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
    decorators = [jwt_required()]
    update_password_schema = UpdatePasswordSchema()

    def put(self):
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.json
        try:
            user_data = self.update_password_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        current_password = data["current_password"]
        new_password = data["new_password"]

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User Not found"}), 404

        if not user.check_password(data["current_password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        if current_password == new_password:
            return jsonify({"error": "old and new password not be same"}), 400

        user.set_password(data["new_password"])
        jti = get_jwt()["jti"]
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]
        redis_client = current_app.config["REDIS_CLIENT"]
        redis_client.setex(jti, expires_in, "blacklisted")

        return jsonify({"detail": "Password Update Successfully"}), 200


class Logout(MethodView):
    decorators = [jwt_required()]

    def delete(self):
        jti = get_jwt()["jti"]
        expires_in = get_jwt()["exp"] - get_jwt()["iat"]
        redis_client = current_app.config["REDIS_CLIENT"]
        redis_client.setex(jti, expires_in, "blacklisted")
        return jsonify(), 204


class ResetPasswordSendMail(MethodView):
    def post(self):
        data = request.json
        email = data.get("email")
        if not email:
            return jsonify({"error": "Invalid data"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Not registered"}), 400

        token = secrets.token_urlsafe(32)

        redis_key = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        redis_client.setex(redis_key, timedelta(minutes=10), str(user.id))

        reset_link = f"http://127.0.0.1:5000/api/reset-password/{token}/"
        html_message = render_template(
            "reset_password_email.html",
            subject="Reset Link Password",
            reset_link=reset_link,
            user_name=user.username,
        )
        send_mail(user.email, html_message, "Reset Link Password")
        
        return jsonify({"detail": "Link sent successfully, please check your email"}), 200


class ResetPassword(MethodView):
    reset_password_schema = ResetPasswordSchema()
    def post(self, token):
        data = request.json
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        try:
            user_data = self.reset_password_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        
        if new_password != confirm_password:
            return jsonify({"error" : "new password and confirm password must be equal"}),400


        redis_key = f"reset_password:{token}"
        redis_client = current_app.config["REDIS_CLIENT"]
        user_id = redis_client.get(redis_key)

        if not user_id:
            return jsonify({"error": "Invalid or expired token"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.set_password(data["new_password"])
        db.session.commit()

        redis_client.delete(redis_key)

        return jsonify({"detail": "Password reset successfully"}), 200
