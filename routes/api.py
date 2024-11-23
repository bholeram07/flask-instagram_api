from flask import Blueprint, jsonify, request
from models.user import db, User 
from schemas.user_schema import SignupSchema
from marshmallow import ValidationError
from datetime import timedelta

api = Blueprint('api', __name__)
@api.route('/signup', methods=['POST'])
def create_user():
    user_schema = SignupSchema()
    data = request.json
    user_data = user_schema.load(data)

    
    new_user = User(
        username = data['username'],
        email = data['email'],
    )
    existing_email =  User.query.filter_by(email=data['email']).first()
    existing_username = User.query.filter_by(username = data['username']).first()
    if existing_email :
        return jsonify({"error" : "email already exists"}),409
    if existing_username :
        return jsonify({"error" : "Username already exists"}),409
    new_user._set_password = user_data['password']
    db.session.add(new_user)
    db.session.commit()
    user_dict = user_schema.dump(new_user)
    user_dict.pop('password', None) 
    return jsonify({"data" : user_dict}),201

