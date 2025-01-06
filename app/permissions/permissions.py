from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.user import User
from functools import wraps  # Correctly import wraps
from flask import request, jsonify
from app.models.post import Post
from app.models.comment import Comment
from app.uuid_validator import is_valid_uuid
from app.models.story import Story
global target_user


class Permission:
    @staticmethod
    @jwt_required()  # Ensure JWT is validated before getting identity
    def get_current_user_id():
        """Retrieve the current user's ID from the JWT."""
        return get_jwt_identity()

    @staticmethod
    def can_access_user(target_user):
        """Check if the current user can access the target user's resource."""
        # Get user ID from JWT
        current_user_id = Permission.get_current_user_id()
        if not current_user_id:
            return False
        # fetch the user from the current_user_id
        current_user = User.query.get(current_user_id)
        if target_user == current_user:
            return True

        # If the account is public or If the current user is a follower, allow access allow access
        if not target_user.is_private or current_user.is_follower(target_user):
            return True

        # Deny access otherwise
        return False

    @staticmethod
    def user_permission_required(view_func):
        """Decorator to enforce user access permissions."""

        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # Assuming user_id is passed in the route
            # get the id's from the request data or the routes
            data = {}
            if request.is_json:
                data = request.get_json() or {}
            user_id = data.get('user_id') or kwargs.get('user_id')
            post_id = data.get('post_id') or kwargs.get('post_id')
            comment_id = data.get('comment_id') or kwargs.get('comment_id')
            story_id = data.get('story_id') or kwargs.get("story_id")
            current_user_id = Permission.get_current_user_id()

            target_user = None
            # if post_id is taken
            if user_id:
                target_user = User.query.get(user_id)
            if post_id:
                if not is_valid_uuid(post_id):
                    return jsonify({"error": "Invalid uuid format"}), 400
                post = Post.query.filter_by(
                    id=post_id, is_deleted=False).first()
                if not post:
                    return jsonify({"error": "Post not found"}), 404
                # pass the user of the post
                target_user = User.query.get(post.user)
            # if the comment id is taken
            if comment_id:
                # fetch the comment
                if not is_valid_uuid(comment_id):
                    return jsonify({"error": "Invalid uuid format"}), 400
                comment = Comment.query.filter_by(
                    id=comment_id, is_deleted=False).first()
                if not comment:
                    return jsonify({"error": "comment not exist"}), 404
                # pass the user of the comment
                target_user = User.query.get(comment.user_id)
            # if the story id is taken
            if story_id:
                # fetch the story
                if not is_valid_uuid(story_id):
                    return jsonify({"error": "Invalid UUID format"}), 400
                story = Story.query.filter_by(
                    id=story_id, is_deleted=False).first()
                if not story:
                    return jsonify({"error": "Story does not exist"}), 404
                # pass the user of the story
                target_user = User.query.get(story.story_owner)
                
            if target_user == None:
                return view_func(*args, **kwargs)
            # permission denied
            if not Permission.can_access_user(target_user):
                return jsonify({"error": "Can't access user account is private"}), 403

            # Proceed if permission is granted
            return view_func(*args, **kwargs)

        return wrapped_view
