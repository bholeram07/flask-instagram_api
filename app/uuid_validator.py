import uuid
import uuid

def is_valid_uuid(value):
    # If the value is already a UUID object, return True
    if isinstance(value, uuid.UUID):
        return True
    try:
        # Try converting it to a UUID if it's not already a UUID object
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False
