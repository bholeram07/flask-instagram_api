from flask import Blueprint, jsonify, request, current_app, render_template
from app.models.user import db, User
import datetime
from app.utils.jwt_utils import add_to_blocklist
from flask import app
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
    get_jwt
)
from datetime import timedelta
from flask_restful import Resource, Api
from app.utils.tasks import send_mail

api = Blueprint("api", __name__)


@api.route("/signup", methods=["POST"])
def create_user():
    user_schema = SignupSchema()
    if request.is_json:
        data = request.get_json()
        file = None
    else:
        data = request.form
        file = request.files.get("image")

    if "email" not in data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400
    new_user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )
    file = request.files.get("image")
    image_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(image_path)

    existing_user = User.query.filter(
        (User.email == data["email"]) | (User.username == data["username"])
    ).first()
    if existing_user:
        if existing_user.email == data["email"]:
            return jsonify({"error": "email already exists"}), 409
        if existing_user.username == data["username"]:
            return jsonify({"error": "Username already exists"}), 409
    try:
        user_data = user_schema.load(data)
    except ValidationError as e:
        first_error = next(iter(e.messages.values()))[0]
        return jsonify({"error": first_error}), 400

    new_user.set_password(user_data["password"])
    db.session.add(new_user)
    db.session.commit()
    user_dict = user_schema.dump(new_user)
    user_dict.pop("password", None)
    send_mail.delay(data["email"])
    return jsonify({"data": user_dict}), 201


@api.route("/users/profile", defaults={"user_id": None}, methods=["GET", "PUT"])
@api.route("/users/<uuid:user_id>/profile", methods=["GET"])
@jwt_required()
def user_profile(user_id=None):
    profile_schema = ProfileSchema()
    current_user_id = get_jwt_identity()
    if request.method == "GET":
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "user not found"})
        else:
            if not current_user_id:
                return jsonify({"error": "Unauthorized"}), 403
            user = User.query.get_or_404(current_user_id)
        try:
            profile_data = profile_schema.dump(user)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        return jsonify(profile_data)

    elif request.method == "PUT":
        if not current_user_id:
            return jsonify({"error": "Unauthorized"}), 403
        user = User.query.get_or_404(current_user_id)
        data = request.json
        try:
            updated_data = profile_schema.dump(user)
            if "username" in data:
                user.username = data.get("username")
            if "bio" in data:
                user.bio = data.get("bio")
            if "profile_image" in data:
                user.profile_image = data.get("profile_image")
            db.session.commit()
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        return jsonify(updated_data), 202


@api.route("/login", methods=["POST"])
def login_user():
    login_schema = LoginSchema()
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Invalid JSON format, please send a valid JSON."}), 400

    if "email" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400
    try:
        user_data = login_schema.validate(data)
    except ValidationError as err:
        return jsonify({"error": err.messages})
    user = User.query.filter_by(email=data["email"]).first()
    if not user:
        return jsonify({"error": "This email is not registered"})
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


@api.route("/update-password", methods=["PUT"])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    update_password_schema = UpdatePasswordSchema()
    data = request.json
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    if not "current_password" in data or not "new_password" in data:
        return jsonify({"error": "Invalid data"}), 400

    current_password = data["current_password"]
    new_password = data["new_password"]

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User Not found"}), 404

    if not user.check_password(data["current_password"]):
        return jsonify({"error": "Incorrect Current Password"}), 401
    try:
        user_data = update_password_schema.load(data)
    except ValidationError as e:
        first_error = next(iter(e.messages.values()))[0]
        return jsonify({"error": first_error}), 400

    if current_password == new_password:
        return jsonify({"error": "old and new password not be same"}),400

    user.set_password(data["new_password"])             
    jti = get_jwt()["jti"]
    expires_in = get_jwt()["exp"] - get_jwt()["iat"]
    redis_client = current_app.config["REDIS_CLIENT"]
    redis_client.setex(jti, expires_in, "blacklisted")

    return jsonify({"detail": "Password Update Successfully"}), 200


@api.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    expires_in = get_jwt()["exp"] - get_jwt()["iat"]
    redis_client = current_app.config['REDIS_CLIENT']
    redis_client.setex(jti, expires_in, "blacklisted")
    return jsonify(), 204
 

@api.route("/reset-password/send-mail", methods=["POST"])
def send_mail_reset_password():
    data = request.json
    email = data.get('email')
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


@api.route("/reset-password/<uuid:user_id>/", methods=["POST","GET"])
def reset_password(user_id):
    print(user_id)
    user = User.query.get(user_id)
    data = request.json
    if not data or "new_password" not in data:
        return jsonify({"error": "New password is required"}), 400
    new_password = data.get("new_password")
    if not new_password:
        return jsonify({"error": "New password cannot be empty"}), 400
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if user.check_password(data.get('new_password')):
        return (
            jsonify({"error": "new password must be diffrent from existing password"}),
            401,
        )

    if data["new_password"] != data["confirm_password"]:
        return jsonify({"error": "password and confirm password must be same"}), 400
    user.set_password(data["new_password"])
    return jsonify({"detail": "Password reset successfully"}), 200
