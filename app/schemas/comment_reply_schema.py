from marshmallow import Schema, ValidationError, validates, fields, EXCLUDE


class ReplyCommentSchema(Schema):
    id = fields.UUID(dump_only=True)
    comment_id = fields.UUID(required=True)
    content = fields.String(required=True)

    class Meta:
        unknown = EXCLUDE

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("Content should not be blank.")
