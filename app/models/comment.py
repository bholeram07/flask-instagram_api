from app.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy import func
from app.models.user import User
from app.models.post import Post 


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(UUID(as_uuid=True),primary_key = True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),db.ForeignKey('user.id'))
    post_id = db.Column(UUID(as_uuid=True),db.ForeignKey('post.id'))
    content = db.Column(db.String, nullable = False)
    is_deleted = db.Column(db.Boolean, default= False)
    deleted_at = db.Column(db.DateTime, nullable = True)
    created_at = db.Column(db.DateTime, server_default=func.now())  
    updated_at = db.Column(db.DateTime, onupdate=func.now(), default=func.now()) 
    
    def __str__(self):
        return f"{self.content} by {self.user_id}"
    