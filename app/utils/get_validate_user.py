from flask import jsonify
from app.models.user import User
from app.models.post import Post
from app.uuid_validator import is_valid_uuid

def get_user(user_id):
    if not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid UUid format"}), 400
    
    user = User.query.filter_by(id = user_id,is_deleted = False, is_verified = True,is_active = True).first()
    if not user:
        return jsonify({"error" : "User not found"}),404
  
    return user

def get_post(post_id):
    if not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid UUid format"}), 400

    post = Post.query.filter_by(
        id=post_id, is_deleted=False).first()
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return post
    
        
    