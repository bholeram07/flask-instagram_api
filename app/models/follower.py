from app.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id =  db.Column(UUID(as_uuid=True),db.ForeignKey('user.id'),primary_key = True)
    following_id =  db.Column(UUID(as_uuid=True),db.ForeignKey('user.id'), primary_key =True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
