from marshmallow import ValidationError
from typing import Tuple, Any, Dict


def validate_and_load(schema: Any, data: Dict[str, Any]) -> Tuple[Any, Dict[str, Any]]:
    """
    Validates and deserializes input data using the provided schema.
    Handles password-related fields differently based on the number of errors.
    """
    try:
        return schema.load(data), None
    except ValidationError as err:
        # Format errors to handle password-related fields differently
        formatted_errors = {
            field: messages if field in {"password", "new_password", "confirm_password"} and len(messages) > 1
            else " ".join(messages)
            for field, messages in err.messages.items()
        }
        return None, formatted_errors
