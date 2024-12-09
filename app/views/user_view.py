
from flask import Blueprint, jsonify, request, current_app, render_template
from app.models.user import db, User
from app.models.follower import Follow
from app.models.post import Post
from app.utils.allowed_file import allowed_file
from flask_restful import MethodView
from werkzeug.utils import secure_filename
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
import os

class Signup(MethodView):
    user_schema = SignupSchema()

    def post(self):
        data = request.json
        try:
            user_data = self.user_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        existing_user = User.query.filter(
            (User.email == data["email"]) | (User.username == data["username"])
        ).first()

        if existing_user:
            if existing_user.email == data["email"]:
                return jsonify({"error": "Email already exists"}), 409
            if existing_user.username == data["username"]:
                return jsonify({"error": "Username already exists"}), 409

        new_user = User(
            username=data["username"], email=data["email"], password=data["password"]
        )
        new_user.set_password(user_data["password"])
        db.session.add(new_user)
        db.session.commit()

        user_dict = self.user_schema.dump(new_user)
        user_dict.pop("password", None)

        html_message = render_template(
            "welcome_email.html",
            subject="Welcome mail",
            user_name=data["username"],
        )
        send_mail(data["email"], html_message, "Welcome mail")
        return jsonify(user_dict), 201


class UserProfile(MethodView):
    profile_schema = ProfileSchema()
    decorators = [jwt_required()]

    def get(self, user_id=None):
        current_user_id = get_jwt_identity()

        if user_id:
            if not is_valid_uuid(user_id):
                return jsonify({"error": "Invalid UUID format"}), 400
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
        else:
            if not current_user_id:
                return jsonify({"error": "Unauthorized"}), 403
            user = User.query.get(current_user_id)

        try:
            followers_count = Follow.query.filter_by(
                follower_id=user.id).count()
            following_count = Follow.query.filter_by(
                following_id=user.id).count()
            post_count = Post.query.filter_by(
                user=user.id, is_deleted=False).count()

            profile_data = self.profile_schema.dump(user)
            profile_data.update({
                "followers": followers_count,
                "following": following_count,
                "posts": post_count,
            })
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        return jsonify(profile_data)

    def put(self):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error": "Unauthorized"}), 403

        image = request.files.get("profile_pic")
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
        else:
            image_path = None

        data = request.form or request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if "username" in data:
            user.username = data["username"]
        if "bio" in data:
            user.bio = data["bio"]
        if image_path:
            user.profile_pic = image_path

        db.session.commit()

        updated_data = self.profile_schema.dump(user)
        return jsonify(updated_data), 202


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
            return jsonify({"error": "Incorrect password"}), 401

        access_token = create_access_token(
            identity=user.id,
        )
        refresh_token = create_refresh_token(
            identity=user.id, expires_delta=timedelta(days=1)
        )
        access_token_expiration = datetime.datetime.utcnow() + timedelta(hours=1)
        refresh_token_expiration = datetime.datetime.utcnow() + timedelta(days=1)
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
            return jsonify({"error": "Incorrect Password"}), 401

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
        if email == None or email == "":
            return jsonify({"error": "Invalid data"}), 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"error": "Not registered"}), 400

        user_id = user.id
        reset_link = f"http://127.0.0.1:5000/reset-password/{user_id}/"
        html_message = render_template(
            "reset_password_email.html",
            subject="Reset Link Password",
            reset_link=reset_link,
            user_name=user.username,
        )
        send_mail(user.email, html_message, "Reset Link Password")
        return jsonify({"detail": "link sent successfully please check your mail"}), 200


class ResetPassword(MethodView):
    reset_password_schema = ResetPasswordSchema()

    def post(self, user_id):
        user = User.query.get(user_id)
        if user is None:
            return jsonify({"error": "User not found"}), 404

        data = request.json
        try:
            user_data = self.reset_password_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400

        if user.check_password(data.get("new_password")):
            return (
                jsonify(
                    {"error": "new password must be diffrent from existing password"}
                ),
                401,
            )

        if data["new_password"] != data["confirm_password"]:
            return jsonify({"error": "password and confirm password must be same"}), 400

        user.set_password(data["new_password"])
        return jsonify({"detail": "Password reset successfully"}), 200

