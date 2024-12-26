from flask import jsonify,request
from flask_restful import MethodView
from flask_jwt_extended import get_jwt_identity,jwt_required
from app.uuid_validator import is_valid_uuid
from app.utils.validation import validate_and_load
from app.schemas.comment_reply_schema import ReplyCommentSchema
from app.pagination_response import paginate_and_serialize
from app.models.comment import Comment
from app.extensions import db
class ReplyCommentApi(MethodView):
    decorators = [jwt_required()]
    reply_comment_schema = ReplyCommentSchema()
    
    def __init__(self):
        self.current_user_id = get_jwt_identity()
    
    def post(self):
        data = request.json
        parent_comment_id = data.get("comment_id")
        content = data.get("content")
        is_valid_uuid(parent_comment_id)
        comment_data , errors = validate_and_load(self.reply_comment_schema,data)
        if errors:
            return jsonify({"errors":errors}),400
        comment = Comment.query.filter_by(id = parent_comment_id,is_deleted = False).first()
        if not comment :
            return jsonify({"error":"This comment not exist"}),404
        if not content:
            return jsonify({"error":"Provide content for reply"}),400
        reply_comment = Comment(
            parent = parent_comment_id,
            content = content,
            user_id = self.current_user_id
        )
        db.session.add(reply_comment)
        db.session.commit()
        response = {
            "id": reply_comment.id,
            "content": "This is the reply on the comment",
            "parent_comment": {
                "id": comment.id,
                "content": comment.content
            },
            "replied_by": {
                "id": reply_comment.user_id
            }
        }
        return jsonify(response),201 
    
    def get(self,comment_id):
        if not comment_id:
            return ({"error" : "Please Provide comment id "}),400
        is_valid_uuid(comment_id)
        reply_comment = Comment.query.filter_by(parent = comment_id,is_deleted = False).all()
        page_number = request.args.get('page', default=1, type=int)
        page_size = request.args.get('size', default=5, type=int)
        offset = (page_number - 1) * page_size
        # fetch the likes on the comment
        reply_comment = Comment.query.filter_by(
            parent=comment_id, is_deleted=False).offset(offset).limit(page_size).all()
      
        reply_data = []
        # generate a dynamic response
        for reply in reply_comment:
            reply_data.append({
                "id": reply.id,
                "content": reply.content,
                "replied_by" : reply.user_id
            })
        # apply the pagination
        item = paginate_and_serialize(
            reply_data, page_number, page_size), 200

        return item

        
        

    
         
        