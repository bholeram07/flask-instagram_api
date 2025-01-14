from marshmallow import validates,ValidationError,fields,Schema

class StorySchema(Schema):
    """A schema class to serialize and deserialize the story data using marshmallow"""
    id = fields.UUID(dump_only=True)
    owner = fields.UUID(dump_only=True)
    content = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates("content")
    def validate_content(self, value):
        """A function to validate the content of the story"""
        if not isinstance(value, str):
            raise ValidationError(
                "Invalid input type. Content must be a string.")
        if not value.strip():
            raise ValidationError("Content should not be blank.")
       
