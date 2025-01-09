from marshmallow import ValidationError
from typing import Tuple, Any, Dict


def validate_and_load(schema: Any, data: Dict[str, Any]) -> Tuple[Any, Dict[str, str]]:
    """
    Validates and deserializes input data using the provided schema.
    """
    try:
        return schema.load(data), None
    except ValidationError as err:
        # Format error messages
        formatted_errors = {field: " ".join(
            messages) for field, messages in err.messages.items()}
        return None, formatted_errors
