from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from datetime import datetime,timezone
from app.models.user import User
import uuid

class Story(BaseModel,db.Model):
    """
    A story model that creates a story table in the databases
    """
    __tablename__ = "story"
    story_owner = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id", ondelete="CASCADE"))
    content = db.Column(db.Text,nullable  = False)
    
    user = db.relationship("User", backref="user_story", viewonly= True)

    
    #represantation method
    def __str__(self):
        return f"story {self.content} posted by {self.story_owner}"
    
    #method to get the username of the story owner
    @staticmethod
    def get_username(story_owner):
        user = User.query.filter_by(id = story_owner).first()
        return f"{user.username}"
        
    


class StoryView(BaseModel,db.Model):
    __tablename__ = "story_view"
    story_id = db.Column(UUID(as_uuid=True),db.ForeignKey("story.id",ondelete = "CASCADE"),nullable = False)
    viewer_id = db.Column(UUID(as_uuid=True),db.ForeignKey("user.id",ondelete = "CASCADE"), nullable = False)
    story_owner = db.Column(UUID(as_uuid=True),db.ForeignKey("user.id",ondelete = "CASCADE"), nullable = False)
    
    def __str__(self):
        return f"story {self.story_id} viewed by {self.viewer_id}"
    
    @staticmethod
    def get_username(viewer_id):
        user = User.query.filter_by(id = viewer_id).first()
        return f"{user.username}"
    
    @staticmethod
    def get_content(story_id):
        story = Story.query.filter_by(id = story_id).first()
        return f"{story.content}"
        
        
    
    
    
