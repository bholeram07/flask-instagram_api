from app.db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token
import datetime

class User(db.Model):
        id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        username = db.Column(db.String(80), nullable=False, unique=True)
        first_name = db.Column(db.String(15),nullable = True)
        last_name = db.Column(db.String(20),nullable=True)
        bio = db.Column(db.String(120),nullable = True)
        profile_image = db.Column(db.LargeBinary,nullable =True)
        email = db.Column(db.String(120), nullable=False, unique=True)
        _password = db.Column(db.String(255),nullable = False)
        
        created_at = db.Column(db.DateTime, server_default=db.func.now())
        updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
        
        @property
        def password(self):
            raise AttributeError("Password is not readable")  # Prevent direct access

        @password.setter
        def password(self, raw_password):
            self._password = generate_password_hash(raw_password)

        def check_password(self, raw_password):
            return check_password_hash(self._password, raw_password)

        def set_password(self, raw_password):
            self.password = raw_password  
        def to_dict(self):
            """Convert user object to a dictionary for JSON serialization."""
            return {
                'id': self.id,
                'username': self.username,
               
                'email': self.email
            }

        