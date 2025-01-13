import re
from marshmallow import Schema, fields, validates, ValidationError


def validate_password_rules(password):
    """
    Validates the password against multiple rules and returns a list of errors.
    """
    errors = []
    

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[!@#$%^&*()_]", password):
        errors.append("Password must contain at least one special character.")
    if not re.search(r"[1-9]", password):
        errors.append("Password must contain at least one numerical value.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")

    return errors
