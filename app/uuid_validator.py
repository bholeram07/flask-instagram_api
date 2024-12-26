import uuid
from flask import jsonify

def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return jsonify({"error":"Not a valid uuid format"})
