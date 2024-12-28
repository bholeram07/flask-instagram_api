from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
from sqlalchemy import func
from app.models.user import User
from app.models.base import BaseModel


class Post(BaseModel,db.Model):
    """
    A post model that create a post table in the database
    """
    __tablename__ = "post"
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    title = db.Column(db.String(40), nullable=True)
    caption = db.Column(db.Text, nullable=True)
    image_or_video = db.Column(db.String(255), nullable=True)
    is_enable_comment = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    #relationships
    likes = relationship("Like", backref="post_likes",lazy = "dynamic")
    comments = relationship("Comment" , backref="post_commment",lazy= "dynamic")
    # comments = relationship("Comment" , backref="commented_post", lazy = "dynamic")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __str__(self):
        return f"{self.content} by {self.user}"
