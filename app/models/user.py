from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import datetime
from app.models.follower import Follow


class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80), nullable=False, unique=True)
    bio = db.Column(db.String(120), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )
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


    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)  
        db.session.commit()


    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}
