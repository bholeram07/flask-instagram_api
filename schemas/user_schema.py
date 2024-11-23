from marshmallow import Schema, fields,ValidationError,validates,validates_schema
import re

class  SignupSchema(Schema):
    id = fields.UUID()
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required = True)
    
    
    @validates("password")
    def validate_password(self,data):
        if len(data)<8:
            raise ValidationError("Password must be length of 8")
        if re.search("!@#$%^&*()_",data):
            raise ValidationError("password must be contain atleast one special character")
        if re.search('a-z',data):
            raise ValidationError("Password must be contain atleast one lower character")   
        if re.search('A-Z',data):
            raise ValidationError("Password must be atleast one upper case character")
        return data
    
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    
    
    