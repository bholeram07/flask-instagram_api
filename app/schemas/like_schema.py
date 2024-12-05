from marshmallow import Schema,validates,ValidationError,fields

class LikeSchema(Schema):
    post = fields.UUID(dump_only=True)
    user = fields.UUID(dump_only=True)
    id = fields.UUID(dump_only=True)
    created = fields.DateTime(dump_only=True)