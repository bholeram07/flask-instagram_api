from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import func
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models.follower import Follow
from app.models.base import BaseModel
from datetime import datetime

class User(BaseModel,db.Model):
    """
    A User model that create a user table in the database
    """
    username = db.Column(db.String(80), nullable=False, unique=True)
    bio = db.Column(db.String(255), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    is_verified  = db.Column(db.Boolean, default = False)
    is_active = db.Column(db.Boolean, default= True)
    is_deleted = db.Column(db.Boolean, default = False)
    other_social = db.Column(db.Text,nullable = True)
    is_private = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    username_change_count = db.Column(db.Integer)
    username_change_timestamp = db.Column(db.DateTime(timezone=True),default=None)
    
    #relationships
    posts = relationship("Post", backref="user_post",lazy="dynamic")
    comments = relationship("Comment", backref="user_comment", lazy= "dynamic")
    likes = relationship("Like",backref="user_likes",lazy="dynamic")
    

    following = db.relationship(
        "Follow",
        foreign_keys=[Follow.follower_id],
        backref=db.backref("follower", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    followers = db.relationship(
        "Follow",
        foreign_keys=[Follow.following_id],
        backref=db.backref("following", lazy="joined"),
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    #method that check the password with existing password by check password hash
    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def set_password(self, raw_password):
        """method to set the password of the user in hash"""
        self.password = generate_password_hash(raw_password)  
        db.session.commit()
        

    def is_follower(self, target_user):
        """
        Check if this user is following the target_user.
        :param target_user: The User instance to check against.
        :return: Boolean indicating if self is following target_user.
        """
        return (
            self.following.filter_by(following_id=target_user.id).count() > 0
        )
        


    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}
