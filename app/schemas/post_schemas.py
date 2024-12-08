from marshmallow import (
    Schema,
    fields,
    ValidationError,
    validates,
    validates_schema,
    validate,
)


class PostSchema(Schema):
    id = fields.UUID(dump_only=True)
    user = fields.UUID(dump_only=True)
    content = fields.Str(required=True)
    title = fields.Str(required=True)
    image = fields.Str(dump_only=True)

    @validates("title")
    def validate_title(self, value):
        if not value.strip():
            raise ValidationError("Title should not be blank.")
        if value.isdigit():
            raise ValidationError("Title should not be purely numerical.")

    @validates("content")
    def validate_content(self, value):
        if not value.strip():
            raise ValidationError("Content should not be blank.")


class UpdatePostSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1), required=False)
    content = fields.Str(validate=validate.Length(min=1), required=False)
