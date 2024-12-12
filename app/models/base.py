from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.utils.ist_time import current_time_ist

class BaseModel(db.Model):
    
    # Indicates that this model should not be created in the database.
    __abstract__ = True

    id = db.Column(UUID(as_uuid=True), primary_key=True,
                   default=uuid.uuid4, unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=current_time_ist, nullable=False)
    updated_at = db.Column(db.DateTime, default=current_time_ist,
                           onupdate=current_time_ist, nullable=False)