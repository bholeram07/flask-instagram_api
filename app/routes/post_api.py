from flask import app, jsonify, Blueprint, request,current_app
from marshmallow import ValidationError
from datetime import timedelta
from app.schemas.post_schemas import PostSchema
from app.models.post import Post
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.custom_pagination import CustomPagination

post_api = Blueprint("post_api", __name__)



@post_api.route("/posts", methods=["POST", "GET"])
@post_api.route("/posts/<uuid:post_id>", methods=["PUT", "DELETE", "GET"])
@post_api.route("/users/<uuid:user_id>/posts", methods=["GET"])
@post_api.route("/users/<uuid:user_id>/posts/<uuid:post_id>",methods = ["GET","PUT","DELETE"])
@jwt_required()
def posts(post_id=None, user_id=None):
    redis_client = current_app.config['REDIS_CLIENT']
    post_schema = PostSchema()
    current_user_id = get_jwt_identity()

    if request.method == "POST":
        data = request.json
        current_user_id = get_jwt_identity()
        if not current_user_id:
            "User not found"
        print(data)
        print(current_user_id)
        try:
            post_data = post_schema.load(data)
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        post = Post(
            title=data.get("title"), content=data.get("content"), user=current_user_id
        )
        db.session.add(post)
        db.session.commit()
        result = post_schema.dump(post)
        return jsonify({"data": result}), 201

    if request.method == "PUT":
        data = request.json
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({"error":"Please Provide Post"})
        if not post_id:
            return jsonify({"error": "Please Provide Post id"})
        post = Post.query.filter_by(user=user_id, id=post,is_deleted = False)
        if post == None:
            return jsonify({"error": "Post not exist"}), 204

        try:
            updated_data = post_schema.load(data)
            updated_data["title"] = data.get("title")
            updated_data["content"] = data.get("content")
            db.session.commit()
        except ValidationError as e:
            first_error = next(iter(e.messages.values()))[0]
            return jsonify({"error": first_error}), 400
        return jsonify({"data": updated_data}), 202

    if request.method == "GET":
        current_user_id = get_jwt_identity()
        if post_id and user_id:
            user = User.query.get(user_id)
            if user == None:
                return jsonify({"error" : "User not found"}),404
            post = Post.query.filter_by(user = user.id,id = post_id,is_deleted = False).first()
            if post == None:
                return jsonify({"error": "Post Not exist"}),404
            post_data = post_schema.dump(post)
            return jsonify({"data": post_data}), 200
            
        if post_id:
            post = Post.query.get_or_404(post_id)
            post_data = post_schema.dump(post)
            return jsonify({"data": post_data}), 200   
          
        elif user_id:
            posts = Post.query.filter_by(user=current_user_id).all()
            
        else:
            posts = Post.query.filter_by(user=current_user_id).all()
            
        if posts == None:
            return jsonify({"error": "Post not exist for the user"})
        page = request.args.get('page',1,type = int)
        per_page = request.args.get('per_page',10,type = int)
        paginator = CustomPagination(posts,page,per_page)
        paginated_data = paginator.paginate()
        paginated_data["items"] = post_schema.dump(paginated_data["items"], many=True)
        return jsonify({"data": paginated_data}), 200
    
    if request.method == "DELETE":
        current_user_id = get_jwt_identity()
        if not post_id:
            return jsonify({"error": "Post id is requiered"})

        post = Post.query.filter_by(user=current_user_id, id=post_id, is_deleted = False).first()
        if post == None:
            return jsonify({"error": "Post not exist"}), 404
        post.is_deleted = True
        db.session.commit()
        return jsonify(), 204
