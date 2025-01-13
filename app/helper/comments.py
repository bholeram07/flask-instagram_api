from app.models.comment import Comment
from flask import jsonify
from app.utils.validation import validate_and_load
from typing import List,Dict
from app.uuid_validator import is_valid_uuid
from app.models.post import Post
from app.models.user import User
from app.extensions import db


def create_reply( parent_comment_id: str, content: str, data: dict, current_user_id,reply_comment_schema) -> dict:
    """
        Create a reply to an existing comment.
        """
    if not is_valid_uuid(parent_comment_id):
        return jsonify({"error": "Invalid UUID format"}), 400

    comment_data, errors = validate_and_load(
        reply_comment_schema, data)
    if errors:
        return jsonify({"errors": errors}), 400

    parent_comment: Optional[Comment] = Comment.query.filter_by(
        id=parent_comment_id, is_deleted=False).first()
    if not parent_comment:
        return jsonify({"error": "Comment does not exist"}), 404
    if not content:
        return jsonify({"error": "Provide content for reply"}), 400

    reply_comment: Optional[Comment] = Comment(
        parent=parent_comment_id, content=content, user_id=current_user_id)
    db.session.add(reply_comment)
    db.session.commit()

    response = {
        "id": reply_comment.id,
        "content": reply_comment.content,
        "author": reply_comment.user_id,
        "parent_comment": {
            "id": parent_comment.id,
            "content": parent_comment.content
        },
    }
    return jsonify(response), 200



def create_comment(post_id: str, content: str, data: dict, current_user_id, comment_schema) -> dict:
    """
    Create a new comment on a post.
    """
    if not is_valid_uuid(post_id):
        return jsonify({"error": "Invalid UUID format"}), 400

    post: Optional[Post] = Post.query.filter_by(
        id=post_id, is_deleted=False).first()
    if not post:
        return jsonify({"error": "Post does not exist"}), 404
    if not post.is_enable_comment:
        return jsonify({"error": "Post owner disabled comments on this post"}), 404

    comment_data, error = validate_and_load(comment_schema, data)
    if error:
        return jsonify({"errors": error}), 400

    comment: Optional[Comment] = Comment(
        post_id=post_id, user_id=current_user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    response = {
        "id": comment.id,
        "content": comment.content,
        "author": comment.user_id,
        "post" : post_id
    }
    return jsonify(response), 201



def get_replies_data(replies: List[Comment] , reply_comment_schema) -> List[Dict]:
    """
    Helper function to get data of replies to a comment.
    """
    reply_data = []
    for reply in replies:
        reply_info = reply_comment_schema.dump(reply)
        author = User.query.filter_by(id=reply.user_id).first()
        reply_info["author"] = {
            "id": author.id, "username": author.username}
        reply_data.append(reply_info)
    return reply_data
