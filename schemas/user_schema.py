from marshmallow import Schema, fields,ValidationError,validates,validates_schema
import re

class  SignupSchema(Schema):
    id = fields.UUID()
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required = True)
    
    
    @validates("password")
    def validate_password(self, password):
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
    
        if not re.search(r"[!@#$%^&*()_]", password):
            raise ValidationError("Password must contain at least one special character.")
        
        if not re.search(r"[1-9]",password):
            raise ValidationError("Password must contain at least one numerical value")
       
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
       
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        return password
    
class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    
    
    