from flask import jsonify,request
from flask_restful import MethodView
from flask_jwt_extended import jwt_required,get_jwt_identity
from app.schemas.like_schema import LikeSchema
from app.schemas.comment_schema import CommentSchema
from app.pagination_response import paginate_and_serialize
from app.models.user import User
from app.models.likes import Like
from app.models.comment import Comment

class UserActivity(MethodView):
    decorators = [jwt_required()]
    like_schema = LikeSchema()
    comment_schema = CommentSchema()
    """An api to get the activity of the user """
    def get(self):
        current_user_id = get_jwt_identity()
        activity_type = request.args.get('type', default='likes', type=str)
        page_number = request.args.get('page', default=1, type=int)
        page_size = request.args.get('size', default=5, type=int)
        offset = (page_number - 1) * page_size
        if activity_type == 'likes':
            # Query for likes
            likes = Like.query.filter_by(user=current_user_id).offset(
                offset).limit(page_size).all()
            return paginate_and_serialize(likes, self.like_schema, page_number, page_size)
        elif activity_type == 'comments':
            # Query for comments
            comments = Comment.query.filter_by(
                user_id=current_user_id,is_deleted = False).offset(offset).limit(page_size).all()
            return paginate_and_serialize(comments, self.comment_schema, page_number, page_size)
        else:
            return jsonify({"error": "Invalid activity type"}), 400
