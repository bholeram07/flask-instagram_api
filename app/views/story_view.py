from flask import jsonify, request
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime
import uuid

from app.models.story import Story, StoryView
from app.schemas.story_schema import StorySchema
from app.extensions import db
from app.utils.validation import validate_and_load
from app.custom_pagination import CustomPagination
from app.pagination_response import paginate_and_serialize
from app.utils.upload_story_content import story_upload
from app.uuid_validator import is_valid_uuid
from app.permissions.permissions import Permission


class UserStory(MethodView):
    """An API for uploading a story if content is provided"""
    decorators = [jwt_required()]
    story_schema = StorySchema()

    def __init__(self):
        # Initialize the current user ID from the JWT
        self.current_user_id = get_jwt_identity()

    def post(self):
        """Story creation function"""
        # Create a story instance with the current user as the owner
        story = Story(
            story_owner=self.current_user_id,
        )
        # Get the file data from the request
        file = request.files
        if file:
            content = file.get("content")
            if content:
                # Upload the content (image/video) to the storage
                story_upload(content, story, self.current_user_id)
            else:
                # Handle missing content in the file upload
                return jsonify({"errors": {"content": "Missing required field"}}), 400
        # If the content is text, retrieve it from the request data
        else:
            data = request.form or request.json
            content = data.get("content")
            if content is None or not content.strip():
                # Return error if no content is provided
                return jsonify({"errors": {"content": "Missing required field"}}), 400
            story.content = content
        # Save the story to the database
        try:
            db.session.add(story)
            db.session.commit()
            return jsonify(self.story_schema.dump(story)), 201
        except Exception as e:
            # Handle database errors
            db.session.rollback()
            return jsonify({"error": "some error occurred during uploading the story please try again"}), 500

    @Permission.user_permission_required
    def get(self, story_id):
        """Function to get the story of the user by story ID"""
        if not story_id:
            return jsonify({"error": "story_id is required"}), 400

        if not is_valid_uuid(story_id):
            # Ensure the provided story ID is a valid UUID
            return jsonify({"error": "Invalid UUID format"}), 400

        story = Story.query.filter_by(id=story_id, is_deleted=False).first()
        if not story:
            # Handle case where the story doesn't exist
            return jsonify({"error": "Story does not exist"}), 404

        if str(story.story_owner) != str(self.current_user_id):
            # Add a view record if the story is viewed by someone else
            try:
                story_view = StoryView.query.filter_by(
                    viewer_id=self.current_user_id).first()
                if not story_view:
                    story_view = StoryView(
                        story_id=story.id,
                        viewer_id=self.current_user_id,
                        story_owner=story.story_owner
                    )
                    db.session.add(story_view)
            except Exception as e:
                # Handle database errors during viewing
                db.session.rollback()
                return jsonify({"error": "Some error occurred during viewing the story"}), 500

        # Prepare and return the story data
        story_data = {
            "id": story.id,
            "content": story.content,
            "owner": {
                "username": Story.get_username(story.story_owner),
                "user_id": story.story_owner
            }
        }
        return jsonify(story_data), 200

    def delete(self, story_id):
        """Function to delete the story of the user by story ID (only owner can access)"""
        if not story_id:
            return jsonify({"error": "story_id is required"}), 400

        if not is_valid_uuid(story_id):
            # Ensure the provided story ID is a valid UUID
            return jsonify({"error": "Invalid UUID format"}), 400

        story = Story.query.filter_by(
            id=story_id, is_deleted=False, story_owner=self.current_user_id).first()
        if not story:
            # Handle case where the story doesn't exist
            return jsonify({"error": "Story does not exist"}), 404

        try:
            # Delete the story from the database
            db.session.delete(story)
            db.session.commit()
            return jsonify(), 204
        except Exception as e:
            # Handle database errors during deletion
            db.session.rollback()
            return jsonify({"error": "Some error occurred during deleting the story"}), 500


class GetStoryView(MethodView):
    """An API for getting the views on the story (only accessed by the owner of the story)"""
    decorators = [jwt_required()]
    story_schema = StorySchema()

    def __init__(self):
        # Initialize the current user ID from the JWT
        self.current_user_id = get_jwt_identity()

    def get(self, story_id=None):
        """Function to get the story view"""
        if not is_valid_uuid(story_id):
            # Ensure the provided story ID is a valid UUID
            return jsonify({"error": "Invalid UUID format"}), 400

        # Retrieve the total count of views for the story
        total_views_count = StoryView.query.filter_by(
            story_owner=self.current_user_id, story_id=story_id).count()
        page_number = request.args.get('page', default=1, type=int)
        page_size = request.args.get('size', default=5, type=int)
        offset = (page_number - 1) * page_size

        # Paginate the views for the story
        story_views = StoryView.query.filter_by(
            story_owner=self.current_user_id, story_id=story_id).offset(offset).limit(page_size).all()

        # Serialize the story view data
        story_view_data = [
            {
                "viewer_id": view.viewer_id,
                "viewer_name": StoryView.get_username(view.viewer_id),
                "content": StoryView.get_content(view.story_id)
            }
            for view in story_views
        ]

        # Return paginated and serialized data
        return paginate_and_serialize(story_view_data, page_number, page_size, views_count=total_views_count, story_id=story_id)
