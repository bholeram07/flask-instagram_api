from marshmallow import Schema, ValidationError, validates, fields, EXCLUDE


class CommentSchema(Schema):
    """A schema to serialize and deserialize the comment data"""
    id = fields.UUID(dump_only=True)
    user_id = fields.UUID(dump_only=True)
    post_id = fields.UUID(dump_only=True)
    content = fields.String(required=True)


    class Meta:
        unknown = EXCLUDE

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("Content should not be blank.")
