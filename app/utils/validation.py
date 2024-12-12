from marshmallow import ValidationError


def validate_and_load(schema, data):
    """
    Validates and deserializes input data using the provided schema..
    """
    try:
        return schema.load(data), None
    except ValidationError as err:
        formatted_errors = {field: " ".join(
            messages) for field, messages in err.messages.items()}
        return None, formatted_errors
