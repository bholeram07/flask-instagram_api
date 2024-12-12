from sqlalchemy import desc
from flask.views import MethodView
from flask import jsonify, Blueprint, request, current_app
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.utils.allowed_file import allowed_file
from app.custom_pagination import CustomPagination
from app.uuid_validator import is_valid_uuid
from app.schemas.post_schemas import PostSchema, UpdatePostSchema
from app.models.post import Post
from app.models.user import User
from app.utils.validation import validate_and_load
from app.utils.save_image import save_image
from app.pagination_response import paginate_and_serialize
from datetime import datetime
import os
from uuid import UUID


class PostApi(MethodView):
    post_schema = PostSchema()
    decorators = [jwt_required()]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """
        Creates a new post. Requires user authentication.
        This api allows the user to create a post by providing a image an optional content and title.
        The image is saved in the local folder if provided and valid.
        
        """
        image = request.files.get("image")
        if image:
            image = save_image(image)
        else:
            return ({"error" : "Please Provide image for post"}),400
        
        post_data = request.form
    
        post = Post(
            title=post_data.get("title"),
            caption=post_data.get("caption"),
            image=image,
            user=self.current_user_id,
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(self.post_schema.dump(post)), 201

    def patch(self, post_id):
        """
        Updates an existing post. Only the post owner can update it.
        """

        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400
        
        # Check if the user is owner or not
        post = Post.query.filter_by(user= self.current_user_id,id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post not exist"}), 404

        data = request.json 
    
        if not data:
            return jsonify({"error": "provide data to update"}), 400

        update_post_schema = UpdatePostSchema()

        # serialize and validate the json data
        updated_data, errors = validate_and_load(update_post_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400

        for key, value in updated_data.items():
            setattr(post, key, value)

        db.session.commit()
        return jsonify(self.post_schema.dump(post)), 202

    def get(self, user_id=None, post_id=None):
        """
        Retrieves posts either by a specific user or a specific post.
        """
        if post_id:
            if not is_valid_uuid(post_id):
                return jsonify({"error": "Invalid UUID format"}), 400
            
            #get a post
            post = Post.query.filter_by(id=post_id, is_deleted=False).first()
            if not post:
                return jsonify({"error": "Post not found"}), 404

            return jsonify(self.post_schema.dump(post)), 200
        #takes if user_id else login user
        query_user_id = user_id or self.current_user_id
        query_user = User.query.get(query_user_id)
        
        if not query_user:
            return jsonify({"error" : "user not exist"}),400
        if not is_valid_uuid(query_user_id):
            return jsonify({"error": "Invalid UUID format"}), 400
        
        #fetch the post of the user
        posts = Post.query.filter_by(user=query_user_id, is_deleted=False).all()
        if not posts:
            return jsonify({"error": "No posts exist"}), 404

        # return paginated response
        return paginate_and_serialize(posts, self.post_schema)

    def delete(self, post_id):
        """
        Deletes a post. Only the post owner can delete it.
        """
        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400

        # Check if the post exists, regardless of the user
        post = Post.query.filter_by(user = self.current_user_id,id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        post.is_deleted = True
        post.deleted_at = datetime.now()
        db.session.commit()
        return jsonify(), 204
