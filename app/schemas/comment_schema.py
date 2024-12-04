from marshmallow import Schema,ValidationError , validates,fields

class CommentSchema(Schema):
    id = fields.UUID(dump_only = True)
    user_id = fields.UUID(dump_only = True)
    post_id = fields.UUID(dump_only = True)
    content = fields.Str(required = True)
    
    @validates('content')
    def validate_content(self,value):
        if not value.strip():
           raise ValidationError("Content should not be blank.")
    
        
        
    
        
    