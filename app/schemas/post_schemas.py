from marshmallow import (
    Schema,
    fields,
    ValidationError,
    validates,
    validates_schema,
    validate,
)


class PostSchema(Schema):
    """A schema class to serialize and deserialize the post data using marshmallow"""
    id = fields.UUID(dump_only=True)
    user = fields.UUID(dump_only=True)
    caption = fields.Str()
    title = fields.Str()
    is_enable_comment = fields.Boolean(required=False)
    image_or_video = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates("title")
    def validate_title(self, value):
        """A function to validate the title of the post"""
        if not value.strip():
            raise ValidationError("Title should not be blank.")
        if value.isdigit():
            raise ValidationError("Title should not be purely numerical.")

    @validates("content")
    def validate_content(self, value):
        """A function to validate the content of the post"""
        if not value.strip():
            raise ValidationError("Content should not be blank.")


class UpdatePostSchema(Schema):
    """A schema class to serialize and deserialize the post data provide for update using marshmallow"""
    title = fields.Str(required=False)
    caption = fields.Str(required=False)
    image_or_video = fields.Str(required= False)
    is_enable_comment = fields.Boolean(required=False)
