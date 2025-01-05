from flask import jsonify, request
from flask_restful import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.schemas.like_schema import LikeSchema
from app.schemas.comment_schema import CommentSchema
from app.pagination_response import paginate_and_serialize
from app.models.likes import Like
from app.models.comment import Comment


class UserActivity(MethodView):
    """
    An API to get the activity of the user, such as likes and comments.
    """
    decorators = [jwt_required(
    )]  # Ensure the user is authenticated before accessing this endpoint.
    like_schema = LikeSchema()  # Schema for serializing like data.
    comment_schema = CommentSchema()  # Schema for serializing comment data.

    def get(self):
        """
        Retrieve user activity based on the type specified in the request arguments.
        If 'type=likes', the user's liked posts are returned.
        If 'type=comments', the user's comments are returned.
        """
        current_user_id = get_jwt_identity()  # Get the currently authenticated user's ID.
        # Get the activity type from query parameters.
        activity_type = request.args.get('type', default='likes', type=str)
        # Retrieve pagination parameters.
        offset, page_size, page_number = get_limit_offset(request)

        # Determine the type of activity to fetch.
        if activity_type == 'likes':
            return self.get_likes(current_user_id, offset, page_size, page_number)
        elif activity_type == 'comments':
            return self.get_comments(current_user_id, offset, page_size, page_number)
        else:
            # Return error for invalid activity type.
            return jsonify({"error": "Invalid activity type"}), 400

    def get_likes(self, user_id, offset, limit, page_number):
        """
        Fetch the user's likes with pagination.
        """
        likes = Like.query.filter_by(user=user_id).offset(
            offset).limit(limit).all()  # Query likes by the user.
        # Serialize and return the paginated data.
        return paginate_and_serialize(likes, self.like_schema, page_number, limit)

    def get_comments(self, user_id, offset, limit, page_number):
        """
        Fetch the user's comments with pagination.

        :param user_id: ID of the current user.
        :param offset: Offset for pagination.
        """
        comments = Comment.query.filter_by(user_id=user_id, is_deleted=False).offset(
            offset).limit(limit).all()  # Query active comments by the user.
        # Serialize and return the paginated data.
        return paginate_and_serialize(comments, self.comment_schema, page_number, limit)
