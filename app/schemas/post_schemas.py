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
    caption = fields.Str()
    title = fields.Str()
    is_enable_comment = fields.Boolean(required = False)
    image_or_video = fields.Str(required=True)
    created_at =fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    

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
    caption = fields.Str(validate=validate.Length(min=1), required=False)
    is_enable_comment = fields.Boolean(required=False)
