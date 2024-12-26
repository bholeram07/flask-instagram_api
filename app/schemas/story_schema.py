from marshmallow import validates,ValidationError,fields,Schema

class StorySchema(Schema):
    id = fields.UUID(dump_only=True)
    story_owner = fields.UUID(dump_only=True)
    content = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    
    @validates("content")
    def validate_content(self, value):
        if not isinstance(value, str):
            raise ValidationError(
                "Invalid input type. Content must be a string.")
        if not value.strip():
            raise ValidationError("Content should not be blank.")
       
