from flask import Blueprint, jsonify, request
from models.user import db, User
import datetime

from schemas.user_schema import SignupSchema, LoginSchema
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
    create_refresh_token,
)
from datetime import timedelta
from blacklist import blacklisted_tokens
from flask_restful import Resource, Api


api = Blueprint("api", __name__)


@api.route("/signup", methods=["POST"])
def create_user():
    user_schema = SignupSchema()
    try:
        data = request.get_json()
    except:
        return jsonify({"error": "Invalid JSON format, please send a valid JSON."}), 400

    if "email" not in data or "username" not in data or "password" not in data:
        return jsonify({"error": "Invalid data"}), 400
    new_user = User(
        username=data["username"], email=data["email"], password=data["password"]
    )
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
    return jsonify({"data": user_dict}), 201


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
        identity=user.id, expires_delta=timedelta(hours=1)
    )
    refresh_token = create_refresh_token(
        identity=user.id, expires_delta=timedelta(days=1)
    )
    access_token_expiration = datetime.datetime.utcnow() + timedelta(hours=1)
    refresh_token_expiration = datetime.datetime.utcnow() + timedelta(days=1)
    return (
        jsonify(
            {
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "access_token_expiration_time": access_token_expiration,
                    "refresh_token_expiration_time": refresh_token_expiration,
                }
            }
        ),
        200,
    )


@api.route("/update-password", methods=["POST"])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    data = request.json

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if not "current_password" in data or not "new_password" in data:
        return jsonify({"error": "Invalid data"}), 400

    current_password = data["current_password"]
    new_password = data["new_password"]

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User Not found"}), 404

    if not user.check_password(data["current_password"]):
        return jsonify({"error": "Incorrect Current Password"}), 401

    user.set_password(data["new_password"])
    db.session.commit()
    return jsonify({"detail": "Password Update Successfully"}), 200


@api.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blacklisted_tokens.add(jti)
    return jsonify({"detail": "Successfully logged out."}), 200
