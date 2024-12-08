from app.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from sqlalchemy import func
from app.models.user import User


class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, onupdate=func.now(), default=func.now())

    def __str__(self):
        return f"{self.content} by {self.user}"
