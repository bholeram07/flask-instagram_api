from flask import app,jsonify,Blueprint,request
from marshmallow import ValidationError
from datetime import timedelta
from app.schemas.post_schemas import PostSchema
from app.models.post import Post
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.db import db

post_api = Blueprint("post_api", __name__)
@post_api.route('/posts',methods = ['POST','GET','PUT','DELETE'])
@jwt_required()
def posts(post_id=None):
    post_schema = PostSchema()

    if request.method == "POST":
        data = request.json
        current_user_id = get_jwt_identity()
        if not current_user_id:
            "User not found"
        print(data)
        print(current_user_id)
     
        # print(post)
        try:
            post_data = post_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        # new_post = Post(**post)
        post = Post(
        title=data.get('title'),
        content=data.get('content'),
        user=current_user_id
    )
        db.session.add(post)
        db.session.commit()

        # Serialize the created post for the response
        result = post_schema.dump(post)
        return jsonify({"data": result}), 201
            
            
    

