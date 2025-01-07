from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from app.models.user import User
from app.models.post import Post
from app.models.likes import Like
from app.models.base import BaseModel


class Comment(BaseModel,db.Model):
    """
    Comment model that creates a comment table in the database with the defined column
    """
    __tablename__ = "comment"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id",ondelete = "CASCADE"))
    post_id = db.Column(UUID(as_uuid=True), db.ForeignKey("post.id",ondelete = "CASCADE"))
    content = db.Column(db.Text, nullable=False)  # size
    parent = db.Column(UUID(as_uuid=True), nullable = True)

    #relationships
    likes = db.relationship('Like', backref='liked_comment', lazy=True,overlaps="post")
    post = db.relationship("Post", backref = "comment_on_post", lazy = True, overlaps="likes")
  
    def __str__(self):
        return f"{self.content} by {self.user_id}"
