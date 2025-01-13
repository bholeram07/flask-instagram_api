from flask import jsonify
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.uuid_validator import is_valid_uuid
from typing import Optional
from app.exceptions import NotFoundError,BadRequest
from sqlalchemy.orm import joinedload
from app.models.story import Story


def get_user(user_id)-> Optional[User]:
    """get the user object and validating it by the user id """
    if not is_valid_uuid(user_id):
        raise BadRequest("Invalid uuid format")
    #get the user object
    user : Optional[User] = User.query.filter_by(id = user_id,is_deleted = False, is_verified = True,is_active = True).first()
    if not user:
        raise NotFoundError("User not found")
    #return the user object
    return user

def get_post_user(post_id):
    if not is_valid_uuid(post_id):
        raise BadRequest("Invalid uuid format")
    post = (
        Post.query.options(joinedload(Post.owner)).filter(
            Post.id == post_id, Post.is_deleted == False).join(User, User.id == Post.user)
        .filter(User.is_active == True, User.is_verified == True, User.is_deleted == False)
        .first()
    )
    if not post:
        raise NotFoundError("Post not found")
    return post.owner

def get_comment_post(comment_id):
    if not is_valid_uuid(comment_id):
        raise BadRequest("Invalid uuid format")
    comment = (
            Comment.query.options(joinedload(Comment.user)).filter(Comment.id == comment_id, Comment.is_deleted == False).join(User, User.id == Comment.user_id)
            .filter(User.is_active == True, User.is_verified == True, User.is_deleted == False)
            .first()
            )
    
    if not comment:
        raise NotFoundError("comment not exist")
    if comment.parent:
        parent = Comment.query.filter_by(id = comment.parent, is_deleted = False).first()
        return parent.user
    if comment.post_id:
        return comment.post.owner

 
    


# fetch the story
def get_story_user(story_id):
    if not is_valid_uuid(story_id):
        raise BadRequest("Invalid uuid format")
    story = Story.query.options(joinedload(Story.user)).filter(
        Story.id == story_id, Story.is_deleted == False).join(User, User.id == Story.story_owner).filter(User.is_active == True, User.is_verified == True, User.is_deleted == False).first()
    
    
    if not story:
        raise NotFoundError("Story does not exist")
    return story.user


def get_post_or_404(post_id, user_id=None):
    """
    Retrieve a Post object or raise a 404 error.
    - If `post_id` is provided, retrieve the specific post.
    - If `user_id` is provided, retrieve all posts by the user.
    """
    if not is_valid_uuid(post_id):
        raise BadRequest("Invalid uuid format")
    post = None
    if post_id:
        post = Post.query.filter_by(id = post_id,is_deleted = False).first()
        if not post:
            raise NotFoundError("Post does not exist")
    elif post_id and user_id:
        post = Post.query.filter_by(id=post_id, user = user_id,is_deleted=False).first()
        if not post:
            raise NotFoundError("Post does not exist")
    else:
        raise NotFound("Post ID must be provided.")

    return post


def get_comment_or_404(comment_id, user_id=None):
    """
    Retrieve a Post object or raise a 404 error.
    - If `post_id` is provided, retrieve the specific post.
    - If `user_id` is provided, retrieve all posts by the user.
    """
    if not is_valid_uuid(comment_id):
        raise BadRequest("Invalid uuid format")
    comment = None
    if comment_id:
        comment = Comment.query.filter_by(id=comment_id, is_deleted=False).first()
        if not comment:
            raise NotFoundError("Comment does not exist")
    elif comment_id and user_id:
        comment = Comment.query.filter_by(
            id=comment_id, user=user_id, is_deleted=False).first()
        if not comment:
            raise NotFoundError("Comment does not exist")
    else:
        raise NotFound("Comment ID must be provided.")

    return comment
