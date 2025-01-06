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
from app.permissions.permissions import Permission
from app.utils.get_validate_user import get_user
from app.utils.get_limit_offset import get_limit_offset


class PostApi(MethodView):
    # Schema for serializing post data
    post_schema = PostSchema()
    decorators = [jwt_required()]

    def __init__(self):
        # Get the ID of the currently authenticated user
        self.current_user_id = get_jwt_identity()

    def post(self):
        """
        Create a new post.
        Requires user authentication.
        - Accepts form data for title, caption, and an optional image or video.
        - Saves the uploaded media and creates a database record.
        """
        # Extract post data from the request
        post_data = request.form

        # create the post instance
        post = Post(
            title=post_data.get("title"),
            caption=post_data.get("caption"),
            user=self.current_user_id,
        )

        # get the image or video from the request
        file = request.files

        if file:
            # Handle file upload if provided
            image_or_video = file.get("image_or_video")

            if image_or_video:
                # call the PostImageVideo class to upload the image or video
                post_image_video_obj = PostImageVideo(
                    post, image_or_video, self.current_user_id)
                post_image_video_obj.upload_image_or_video()

            # if image or video is not provided
            else:
                return ({"error": "Please provide an image or video for post"}), 400

        # if file is not provided
        else:
            return ({"error": "Please provide an image or video for post"}), 400

        try:
            # Add the new post to the database
            db.session.add(post)
            db.session.commit()
            return jsonify(self.post_schema.dump(post)), 201
        except Exception as e:
            current_app.logger.error(f"Error creating post: {str(e)}")
            return {"error": "An error occurred while creating the post"}, 500

    def patch(self, post_id):
        """
        Update an existing post.
        Only the post owner can perform updates.
        """
        # Validate the post ID
        if not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400

        # Fetch the post by ID
        post = Post.query.filter_by(
            id=post_id, user=self.current_user_id, is_deleted=False).first()

        # if post does not exist
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        file = request.files
        data = None
        image_or_video = None
        try:
            # Extract request data (form or JSON)
            data = request.form or request.json
        except Exception as e:
            # if file is not provided
            if not file:
                return jsonify({"error": "Provide data to update"}), 400

        # if no data or file is provided
        if not data and not file:
            return jsonify({"error": "Provide data to update"}), 400
        if file:
            # Handle media update if provided
            image_or_video = file.get("image_or_video")

            # if image or video is provided
            if image_or_video:
                post_image_video_obj = PostImageVideo(
                    post, image_or_video, self.current_user_id)
                post_image_video_obj.update_image_or_video()

            # if image or video is not provided
            else:
                return jsonify({"error": "Provide data to update"}), 400

        if image_or_video and not data:
            return jsonify(self.post_schema.dump(post)), 202

        update_post_schema = UpdatePostSchema()
        # Validate and load updated data
        updated_data, errors = validate_and_load(update_post_schema, data)

        if errors:
            return jsonify({"errors": errors}), 400

        # atomic transactions
        try:
            # Apply updates to the post and save changes
            for key, value in updated_data.items():
                setattr(post, key, value)
                post.updated_at = datetime.now()
                db.session.commit()
            return jsonify(self.post_schema.dump(post)), 202
        except Exception as e:
            current_app.logger.error(f"Error updating post: {str(e)}")
            return jsonify({"error": "An error occurred while updating the post"}), 500

    @Permission.user_permission_required
    def get(self, post_id):
        """
        Retrieve a specific post by its ID.
        Requires appropriate user permissions.
        """
        # if not post_id or not valid uuid
        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Please provide a valid post ID"}), 400

        # fetch the post by post_id
        post = Post.query.filter_by(id=post_id, is_deleted=False).first()
        # if post does not exist
        if not post:
            return jsonify({"error": "Post does not exist"}), 400

        return jsonify(self.post_schema.dump(post)), 200

    def delete(self, post_id):
        """
        Soft-delete a post by marking it as deleted.
        Only the post owner can perform this operation.
        """
        # Validate the post ID
        if not post_id or not is_valid_uuid(post_id):
            return jsonify({"error": "Invalid or missing post ID"}), 400

        # Fetch the post by ID
        post = Post.query.filter_by(
            user=self.current_user_id, id=post_id, is_deleted=False).first()

        # if post not exist
        if not post:
            return jsonify({"error": "Post does not exist"}), 404

        # atomic transactions
        try:
            # Delete associated media and mark the post as deleted
            post_image_video_obj = PostImageVideo(
                post, post.image_or_video, self.current_user_id)
            post_image_video_obj.delete_image_or_video()
            post.is_deleted = True
            post.deleted_at = datetime.now()
            db.session.commit()
            return jsonify(), 204

        except Exception as e:
            current_app.logger.error(f"Error deleting post: {str(e)}")
            return jsonify({"error": "An error occurred while deleting the post"}), 500


class UserPostListApi(MethodView):
    # Schema for serializing post data
    post_schema = PostSchema()
    # Apply JWT authentication and permission checks to all methods
    decorators = [jwt_required(), Permission.user_permission_required]

    def __init__(self):
        # Get the ID of the currently authenticated user
        self.current_user_id = get_jwt_identity()

    def get(self, user_id=None):
        """
        Retrieve a list of posts for a specific user.
        If no user ID is provided, fetch posts for the current user.
        """
        # if user_id is provided
        if not is_valid_uuid(user_id):
            return jsonify({"error": "Invalid user ID format"}), 400

        query_user_id = user_id or self.current_user_id
        query_user = get_user(query_user_id)
        if not query_user:
            return jsonify({"error": "User does not exist"}), 404

        # Paginate the results
        page, offset, page_size = get_limit_offset()

        posts = Post.query.filter_by(user=query_user_id, is_deleted=False).order_by(
            desc(Post.created_at)).offset(offset).limit(page_size).all()

        # serialize the posts
        serialized_post = post_response(posts, self.post_schema)

        return paginate_and_serialize(serialized_post, page, page_size)
