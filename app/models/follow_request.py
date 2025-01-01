from app.models.user import User
from app.models.base import BaseModel
from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID



class FollowRequest(db.Model):
    __tablename__ = 'follow_request'

    id = db.Column(db.Integer, primary_key=True)
    follower_id  = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    following_id  = db.Column(
        UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    # 'pending', 'accepted', 'rejected'
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Soft delete columns
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    follower = db.relationship('User', foreign_keys=[follower_id])
    following = db.relationship('User', foreign_keys=[following_id])

    # def __repr__(self):
    #     return f"<FollowRequest(follower_id={self.follower_id}, followed_id={self.followed_id}, status={self.status})>"
    