from marshmallow import Schema,fields,ValidationError,validates,validates_schema

class PostSchema(Schema):
    id  = fields.UUID(dump_only=True)
    user = fields.UUID(dump_only=True)
    content = fields.Str(required=True)
    title = fields.Str(required=True)
    image = fields.Str(dump_only=True)
    @validates("title")
    def validate_title(self,value):
        if not value.strip():
            raise ValidationError("Title should not be blank.")
        if value.isdigit():
            raise ValidationError("Title should not be purely numerical.")
        
    @validates("content")
    def validate_title(self,value):
        if not value.strip():
            raise ValidationError("Content should not be blank.")
       
    
    

    
