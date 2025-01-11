from marshmallow import Schema, validates, ValidationError, fields


class LikeSchema(Schema):
    """A schema class to serialize and deserialize the like data using marshmallow"""
    post = fields.UUID(dump_only=True)
    user = fields.UUID(dump_only=True)
    id = fields.UUID(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
