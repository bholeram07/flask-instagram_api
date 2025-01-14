from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime,timezone
from app.models.user import User
from app.utils.ist_time import current_time_ist
import uuid

class Story(BaseModel,db.Model):
    """
    A story model that creates a story table in the databases
    """
    __tablename__ = "story"
    owner = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    content = db.Column(db.Text,nullable  = False)
    
    user = db.relationship("User", backref="stories", viewonly= True)
    story_view = db.relationship("StoryView", backref="story", viewonly=True)
    likes = db.relationship(
        "Like",
        backref="story_like",
        lazy="dynamic",
        cascade="all, delete-orphan",  # Ensures related objects are removed
        passive_deletes=True          # Aligns with database `ON DELETE CASCADE`
    )
    
    def soft_delete(self):
        super().soft_delete()  # Soft delete the user

        for view in self.story_view :
            db.session.delete(view)
            
        for likes in self.likes:
            db.session.delete(likes)
        db.session.commit()

    
    #represantation method
    def __str__(self):
        return f"story {self.content} posted by {self.story_owner}"
    
  

class StoryView(db.Model):
    __tablename__ = "story_view"
    id = db.Column(UUID(as_uuid=True), primary_key=True,
                                               default=uuid.uuid4, unique=True, nullable=False)
    
    story_id = db.Column(UUID(as_uuid=True),db.ForeignKey("story.id",ondelete = "CASCADE"),nullable = False)
    viewer_id = db.Column(UUID(as_uuid=True),db.ForeignKey("user.id",ondelete = "CASCADE"), nullable = False)
    viewed_at = db.Column(
        db.DateTime(timezone=True), default=current_time_ist)
    story_owner = db.Column(UUID(as_uuid=True),db.ForeignKey("user.id",ondelete = "CASCADE"), nullable = False)
    
    story_obj = db.relationship("Story", backref="stories_view", viewonly=True)

        
    def __str__(self):
        return f"story {self.story_id} viewed by {self.viewer_id}"
    
    @staticmethod
    def get_username(viewer_id):
        user = User.query.filter_by(id = viewer_id).first()
        return f"{user.username}"
    

        
        
    
    
    
