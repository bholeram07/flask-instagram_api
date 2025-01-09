import uuid
from flask import jsonify

def is_valid_uuid(value)->bool:
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
    return False
