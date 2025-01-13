from app.models.user import User
from app.models.base import BaseModel
from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid



class FollowRequest(db.Model):
    __tablename__ = 'follow_request'


    id = db.Column(UUID(as_uuid=True), primary_key=True,
               default=uuid.uuid4, unique=True, nullable=False)
    follower_id  = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    following_id  = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    # 'pending', 'accepted', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Soft delete columns
    

    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id])
    following = db.relationship('User', foreign_keys=[following_id])

    