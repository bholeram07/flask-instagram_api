from flask import Blueprint, jsonify, request
from models.user import db, User 
from schemas.user_schema import SignupSchema,LoginSchema
from marshmallow import ValidationError
from flask_jwt_extended import create_access_token,get_jwt_identity,jwt_required
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

@api.route('/login',methods=['POST'])
def login_user():
    login_schema = LoginSchema()
    data = request.json  
    try:
        user_data = login_schema.load(data)
    except ValidationError as err:
        return jsonify({"error" : err.messages})
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error" : "This email is not registered"})
    if not user.check_password(user_data['password']):
        return jsonify({"error": "Invalid password"}), 401
       
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
    return jsonify({"data":{
        "access_token": access_token
    }}), 200


@api.route('/update-password',methods=['POST'])
@jwt_required()
def update_password():
    user_id = get_jwt_identity()
    data = request.json
    if not user_id:
        return jsonify({"error":"Unauthorized"}),403
    if not 'current_password' in data or  not 'new_password' in data:
        return jsonify({"error":"Invalid data"}),400
    current_password = data['current_password']
    new_password = data['new_password']
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error":"User Not found"}),404
    
    if not user.check_password(data['current_password']):
        return jsonify({"error" :"Incorrect Current Password"}),401
        
    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({"detail" : "Password Update Successfully"}),200    