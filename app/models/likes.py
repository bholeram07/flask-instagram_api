from app.db import db
from app.models.post import Post
from app.models.user import User
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
import uuid


class Like(db.Model):
    __tablename__ = "like"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    post = db.Column(UUID(as_uuid=True), db.ForeignKey("post.id"))
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __str__(self):
        return f"liked on {self.post} by {self.user}"
