from app.extensions import db
from app.models.post import Post
from app.models.user import User
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from app.models.base import BaseModel
import uuid


class Like(BaseModel,db.Model):
    """
    A like model that creates a like table in the databases 
    """
    __tablename__ = "like"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id",ondelete = "CASCADE"),nullable = False)
    post = db.Column(UUID(as_uuid=True), db.ForeignKey("post.id",ondelete = "CASCADE"),nullable = True)
    story = db.Column(UUID(as_uuid=True), db.ForeignKey("story.id",ondelete = "CASCADE"),nullable = True)
    comment = db.Column(UUID(as_uuid=True), db.ForeignKey("comment.id",ondelete = "CASCADE"), nullable = True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __str__(self):
        return f"liked on {self.post} by {self.user}"

