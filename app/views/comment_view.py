from flask import jsonify, request, Blueprint, current_app
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment_schema import CommentSchema
from app.schemas.comment_reply_schema import ReplyCommentSchema
from app.custom_pagination import CustomPagination
from app.extensions import db
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from sqlalchemy import desc
from app.pagination_response import paginate_and_serialize
from uuid import UUID
from datetime import datetime
from sqlalchemy import func
from app.response.comment_response import comment_respose
# from app.permissions.permission import Permission



class CommentApi(MethodView):
    decorators = [jwt_required()]
    comment_schema = CommentSchema()
    reply_comment_schema = ReplyCommentSchema()
    def __init__(self):
        self.current_user_id = get_jwt_identity()

    def post(self):
        """
        Creates a new comment. Requires user authentication.
        This api allows the user to create a comment by providing a  content and post id .
        """
        data = request.json
        post_id = data.get("post_id")
        parent_comment_id = data.get("comment_id")
        content = data.get("content")
        # fetch the post through post id
        if post_id:
            if not is_valid_uuid(post_id):
                return jsonify({"error": "Invalid uuid format"}), 400
            post = Post.query.filter_by(id=post_id, is_deleted=False).first()
            if not post:
                return jsonify({"error": "Post does not exist"}), 404
            if post.is_enable_comment == False:
                return jsonify({"error": "Post owner diable the comment on this post"}), 404

            comment_data, error = validate_and_load(self.comment_schema, data)
            comment = Comment(
                post_id=post_id, user_id=self.current_user_id, content=content)
            db.session.add(comment)
            db.session.commit()
            #retun the serialize data
            return jsonify(self.comment_schema.dump(comment)), 201
        
        if parent_comment_id:
            if not is_valid_uuid(parent_comment_id):
                return jsonify({"error":"Not a valid uuid format"}),400
            comment_data, errors = validate_and_load(
                self.reply_comment_schema, data)
            if errors:
                return jsonify({"errors": errors}), 400
            comment = Comment.query.filter_by(
                id=parent_comment_id, is_deleted=False).first()
            if not comment:
                return jsonify({"error": "This comment not exist"}), 404
            if not content:
                return jsonify({"error": "Provide content for reply"}), 400
            reply_comment = Comment(
                parent=parent_comment_id,
                content=content,
                user_id=self.current_user_id
            )
            db.session.add(reply_comment)
            db.session.commit()
            response = {
                "id": reply_comment.id,
                "content": "This is the reply on the comment",
                "replied_by": reply_comment.user_id,
                "parent_comment": {
                    "id": comment.id,
                    "content": comment.content
                },

            }
            return jsonify(response),200
            


    def get(self, post_id=None, comment_id=None):
        """
        Retrieves comments on a specific post or by comment ID, with reply counts for each comment.
        """
        if comment_id:
            if not is_valid_uuid(comment_id):
                return jsonify({"error": "Invalid uuid format"}), 400
            comment = Comment.query.filter_by(
                id=comment_id, is_deleted=False).first()
            if not comment:
                return jsonify({"errors": "Comment not exist"}), 404
            # Add reply_count to a single comment
            reply_count = Comment.query.filter_by(
                parent=comment_id, is_deleted=False).count()
            comment_data = self.comment_schema.dump(comment)
            comment_data["reply_count"] = reply_count
            return jsonify(comment_data), 200

        if post_id:
            if not is_valid_uuid(post_id):
                return jsonify({"error": "Invalid uuid format"}), 400
            post = Post.query.filter_by(id=post_id, is_deleted=False).first()
            if not post:
                return jsonify({"error": "Post does not exist"}), 404

            page_number = request.args.get('page', default=1, type=int)
            page_size = request.args.get('size', default=5, type=int)
            offset = (page_number - 1) * page_size

            # Fetch paginated comments
            comments = Comment.query.filter_by(
                post_id=post_id, is_deleted=False
            ).order_by(desc(Comment.created_at)).offset(offset).limit(page_size).all()
    
            serialized_comments = comment_respose(comments,self.comment_schema)
            return paginate_and_serialize(serialized_comments,page_number,page_size)

        return jsonify({"error": "Post id is required"}), 400


    def put(self, comment_id):
        ''' 
        Update a comment only a comment author and post owner can delete it
        '''
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400

        # check the user is owner of the comment or not
        comment = Comment.query.filter_by(user_id=self.current_user_id,
                                          id=comment_id, is_deleted=False
                                          ).first()

        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404

        data = request.json
        # serialize the data
        comment_update_data, errors = validate_and_load(
            self.comment_schema, data)
        if errors:
            return jsonify({"errors": errors})

        comment.content = comment_update_data.get("content")
        db.session.commit()

        return jsonify(self.comment_schema.dump(comment_update_data)), 202

    def delete(self, comment_id):
        """
        Delete a comment only a post owner or comment owner can delete it
        """
        if not is_valid_uuid(comment_id):
            return jsonify({"error": "Invalid uuid format"}), 400
        comment = Comment.query.filter_by(
            id=comment_id, is_deleted=False
        ).first()
        if not comment:
            return jsonify({"error": "Comment does not exist"}), 404
        # get the post through the comment object
        post_id = comment.post_id
        post = Post.query.get(post_id)
        # check if the user is comment owner or the post owner
        if comment.user_id != UUID(self.current_user_id) and post.user != UUID(self.current_user_id):
            return jsonify({"error": "Comment not exist"}), 404

        # soft deletion
        comment.is_deleted = True
        comment.deleted_at = datetime.now()
        db.session.commit()

        return jsonify(), 204
