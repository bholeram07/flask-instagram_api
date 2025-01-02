from flask import jsonify, request
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.story import Story, StoryView
from app.schemas.story_schema import StorySchema
from app.extensions import db
from app.utils.validation import validate_and_load
from app.custom_pagination import CustomPagination
from app.pagination_response import paginate_and_serialize
from app.utils.upload_story_content import story_upload
from app.uuid_validator import is_valid_uuid
from datetime import datetime
import uuid
from app.permissions.permissions import Permission


class UserStory(MethodView):
    """An api for upload a story if content is provided """
    decorators = [jwt_required()]
    # call to the schema
    story_schema = StorySchema()

    def __init__(self):
        self.current_user_id = get_jwt_identity()
    # story creation function

    def post(self):
        # initialize the story owner
        story = Story(
            story_owner=self.current_user_id,
        )
        # get the file
        file = request.files
        if file:
            content = file.get("content")
            if content:
                story_upload(content, story, self.current_user_id)
            else:
                return jsonify({"errors": {"content": "Missing required field"}}), 400
        # if the content is text and not the image or video
        else:
            data = request.form or request.json
            content = data.get("content")
            # handle the content
            if content == None or not content.strip():
                return jsonify({"errors": {"content": "Missing required field"}}), 400
            story.content = content
        # database operation
        try:
            db.session.add(story)
            db.session.commit()
            return jsonify(self.story_schema.dump(story)), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error" : "some error occured during uploading the story please try again"}),500
            
    @Permission.user_permission_required
    def get(self, story_id):
        """function to get the story of the user by story id"""
        if not story_id:
            return jsonify({"error": "story_id is required"})
        # check uuid validation
        if not is_valid_uuid(story_id):
            return jsonify({"error": "Invalid uuid format"}), 400
        # get the story
        story = Story.query.filter_by(id=story_id, is_deleted=False).first()
        if not story:
            return jsonify({"error": "story not exist"}),404

        if str(story.story_owner) != str(self.current_user_id):
            story_view = StoryView.query.filter_by(
                viewer_id=self.current_user_id).first()
            if not story_view:
                story_view = StoryView(
                    story_id=story.id,
                    viewer_id=self.current_user_id,
                    story_owner=story.story_owner
                )
                db.session.add(story_view)
                db.session.commit()

        if not story:
            return jsonify({"errors": "No story found of this user"}), 404
        story_data = {
            "id": story.id,
            "content": story.content,
            "owner": {
                "username": Story.get_username(story.story_owner),
                "user_id": story.story_owner
            }
        }
        # return the story
        return jsonify(story_data), 200

    def delete(self, story_id):
        """function to delete the story of the user by story id only owner can accessed"""
        if not story_id:
            return jsonify({"error": "story_id is required"}), 400
        # check uuid validation
        if not is_valid_uuid(story_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        story = Story.query.filter_by(
            id=story_id, is_deleted=False, story_owner=self.current_user_id).first()
        if not story:
            return jsonify({"error": "Story not exist"}), 404
        try:
            db.session.delete(story)
            db.session.commit()
            return jsonify(), 204
        except Exception as e:
            return jsonify({"error" : "Some error occured during deleting the story"}),500


class GetStoryView(MethodView):
    """An Api for getting the views on the story only accessed by the owner of the story"""
    decorators = [jwt_required()]
    # call to the schema
    story_schema = StorySchema()

    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def get(self, story_id=None):
        # A function to get the story view
        if story_id:
            if not is_valid_uuid(story_id):
                return jsonify({"error": "Invalid UUid Format"})
            page_number = request.args.get('page', default=1, type=int)
            page_size = request.args.get('size', default=5, type=int)
            # Calculate offset
            offset = (page_number - 1) * page_size

            # Query database with limit and offset
            story_views = StoryView.query.filter_by(
                story_owner=self.current_user_id, story_id=story_id).offset(
                offset).limit(page_size).all()
        else:
            page_number = request.args.get('page', default=1, type=int)
            page_size = request.args.get('size', default=5, type=int)
            offset = (page_number - 1) * page_size
            story_views = StoryView.query.filter_by(
                story_owner=self.current_user_id).offset(
                offset).limit(page_size).all()

        story_view_data = []
        for view in story_views:
            story_view_data.append({
                "story_id": view.story_id,
                "viewer_id": view.viewer_id,
                "viewer_name": StoryView.get_username(view.viewer_id),
                "content": StoryView.get_content(view.story_id)
            })

        return paginate_and_serialize(story_view_data, page_number, page_size)
