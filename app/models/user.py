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
    other_social = db.Column(db.Text,nullable = True)
    is_private = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    username_change_count = db.Column(db.Integer)
    username_change_timestamp = db.Column(db.DateTime(timezone=True),default=None)
    
    #relationships
    posts = relationship("Post", backref="posts",lazy="dynamic",viewonly=True)
    comments = relationship("Comment", backref="user_comment", lazy= "dynamic",viewonly= True)
    likes = db.relationship(
        "Like",
        backref="user_likes",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    story = relationship(
        "Story", backref="user_story", lazy="dynamic", viewonly=True)

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
    
    __table_args__ = (
        db.Index('idx_id', 'id'),
        db.Index('idx_is_verified_active', 'is_verified', 'is_active'),
    )

    #method that check the password with existing password by check password hash
    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)
    
    def soft_delete(self):
        super().soft_delete()  # Soft delete the user

        # Soft delete related posts
        for post in self.posts:
            post.soft_delete()

        # Soft delete related comments
        for comment in self.comments:
            comment.soft_delete()

        # Soft delete related likes
        for like in self.likes:
            like.soft_delete()
        
        for follower in self.followers:
            db.session.delete(follower)
            
        for following in self.following:
            db.session.delete(following)
        
        db.session.commit()

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
