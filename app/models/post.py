from app.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from sqlalchemy import func
from app.models.user import User
# users = User()

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'))
    title = db.Column(db.String(40), nullable=False)
    content = db.Column(db.String(50), nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=func.now())  # Use func.now() for current timestamp
    updated_at = db.Column(db.DateTime, onupdate=func.now(), default=func.now()) 