from sqlalchemy import desc
from flask.views import MethodView
from flask import jsonify, Blueprint, request, current_app
from marshmallow import ValidationError
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.custom_pagination import CustomPagination
from app.uuid_validator import is_valid_uuid
from app.schemas.post_schemas import PostSchema, UpdatePostSchema
from app.models.post import Post
from app.models.user import User
from app.utils.validation import validate_and_load
from app.utils.upload_image_or_video import PostImageVideo
from app.pagination_response import paginate_and_serialize
from datetime import datetime
import os
from uuid import UUID
from app.response.post_response import post_response
from app.permissions.permission import Permission


class PostApi(MethodView):
    post_schema = PostSchema()
    decorators = [jwt_required()]
    

    # @Permission.user_permission_required

    def __init__(self):
        self.current_user_id = get_jwt_identity()
    
    def post(self):
        """
        Creates a new post. Requires user authentication.
        This api allows the user to create a post by providing a image an optional content and title.
        The image is saved in the local folder if provided and valid.
        
        """
       
        post_data = request.form
        post = Post(
            title=post_data.get("title"),
            caption=post_data.get("caption"),
            user=self.current_user_id,
        )
        file = request.files
      
        if file:
            image_or_video = file.get("video_or_image")
            if image_or_video:
                post_image_video_obj = PostImageVideo(post, image_or_video, self.current_user_id)
                post_image_video_obj.upload_image_or_video()
            else:
                return ({"error": "Please Provide image for post"}), 400
        else:
            return ({"error": "Please Provide image or video for post"}), 400

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
        #get the data
        data = request.form or request.json
        file = request.files
        #handle and save the image in s3 and databasae
        if file:
            image_or_video = file.get("image_or_video")
            if image_or_video :
                #update the image or video on the s3 
                try:
                    post_image_video_obj = PostImageVideo(post, image_or_video, self.current_user_id)
                    post_image_video_obj.update_image_or_video()
                except Exception as e:
                    return jsonify({"error": f"The error occured in uploading {e}"}),400
                
        if not data:
            return jsonify({"error": "provide data to update"}), 400
        #update post schema
        update_post_schema = UpdatePostSchema()

        # serialize and validate the json data
        updated_data, errors = validate_and_load(update_post_schema, data)
        if errors:
            return jsonify({"errors": errors}), 400
         
        for key, value in updated_data.items():
            setattr(post, key, value)

        db.session.commit()
        return jsonify(self.post_schema.dump(post)), 202
    # @permission_required("post_id")

    @Permission.user_permission_required
    def get(self, post_id):
        """
        Retrieves a specific post by post id .
        """
        if not post_id:
            return jsonify({"error" : "Please provide post id"}),400
        
        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid UUID format"}), 400
        #get a post
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        if not post:
            return jsonify({"error": "Post not found"}), 404

        return jsonify(self.post_schema.dump(post)), 200
       

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
        #delete the post_image from the s3
        post_image_video_obj = PostImageVideo(post, post.image_or_video, self.current_user_id)
        post_image_video_obj.delete_image_or_video()
        #database operation
        post.is_deleted = True
        post.deleted_at = datetime.now()
        db.session.commit()
        return jsonify(), 204


class UserPostListApi(MethodView):
    post_schema = PostSchema()
    decorators = [jwt_required(),Permission.user_permission_required]

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self,user_id=None):
        # takes if user_id else login user
        query_user_id = user_id or self.current_user_id
        query_user = User.query.filter_by(id = query_user_id, is_active = True, is_deleted = False).first()
        if not query_user:
            return jsonify({"error": "user not exist"}), 400
        if not is_valid_uuid(query_user_id):
            return jsonify({"error": "Invalid UUID format"}), 400

        # fetch the post of the user
        page_number = request.args.get('page', default=1, type=int)
        page_size = request.args.get('size', default=5, type=int)
        # Calculate offset
        offset = (page_number - 1) * page_size
        
        # Query database with limit and offset
        posts = Post.query.filter_by(user=query_user_id, is_deleted=False).offset(
            offset).limit(page_size).all()
       
        serialized_post = post_response(posts,self.post_schema)
        
        return paginate_and_serialize(serialized_post,page_number,page_size)
