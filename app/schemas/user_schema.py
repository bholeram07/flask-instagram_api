from marshmallow import Schema, fields, ValidationError, validates, validates_schema,EXCLUDE
from app.utils.validate_password import validate_password_rules
import re


class SignupSchema(Schema):
    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True,unique = True)
    password = fields.Str(required=True)
    
    @validates("password")
    def validate_password(self, password):
        if not password.strip():
            raise ValidationError("Password should not be blank.")
    
        # If there are errors, raise a single ValidationError with all messages
        errors = validate_password_rules(password)
        
        # Raise ValidationError if there are any errors
        if errors:
            raise ValidationError(errors)
            
        return password

    
    @validates("username")
    def validate_username(self, value):
        if not value.strip():
            raise ValidationError("Username should not be blank")
          


class ProfileSchema(Schema):
    id = fields.UUID()
    username = fields.Str(required=False)
    profile_pic = fields.Str(required=False)
    bio = fields.Str(required=False)
    other_social = fields.Str(required=False)
    is_private = fields.Boolean(required=False)



class LoginSchema(Schema):
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True)

    
    @validates("password")
    def validate_password(self, password):
        if not password.strip():
           raise ValidationError("password should not be blank")
       
    @validates("username_or_email")
    def validate_username_or_email(self, username_or_email):
        if not username_or_email:
            raise ValidationError("Either email or username must be provided.")


class UpdatePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    
    @validates("current_password")
    def validate_current_password(self,current_password):
        if not current_password.strip():
           raise ValidationError("Current password should not be blank.")
        
    @validates("new_password")
    def validate_password(self, new_password):
        if not new_password.strip():
           raise ValidationError("new password should not be blank.")
    
        errors = validate_password_rules(new_password)
        if errors:
            raise ValidationError(errors)
        
        return new_password


class ResetPasswordSchema(Schema):
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)
    
    @validates("new_password")
    def validate_password(self, new_password):
        if not new_password.strip():
           raise ValidationError("new password should not be blank.")
    
        errors = validate_password_rules(new_password)
        if errors:
            raise ValidationError(errors)
            

        return new_password