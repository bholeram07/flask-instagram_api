from flask import jsonify
from app.models.user import User
from app.models.post import Post
from app.uuid_validator import is_valid_uuid

def get_user(user_id):
    """get the user object and validating it by the user id """
    if not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid UUid format"}), 400
    #get the user object
    user = User.query.filter_by(id = user_id,is_deleted = False, is_verified = True,is_active = True).first()
    if not user:
        return jsonify({"error" : "User not found"}),404
    #return the user object
    return user

def get_post(post_id):
    """get the post object and validating it by the post id """
    if not is_valid_uuid(user_id):
        return jsonify({"error": "Invalid UUid format"}), 400
    #get the post object
    post = Post.query.filter_by(
        id=post_id, is_deleted=False).first()
    if not post:
        return jsonify({"error": "Post not found"}), 404
    #return the post
    return post
    
        
    