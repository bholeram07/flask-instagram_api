from marshmallow import Schema, fields, ValidationError, validates, validates_schema
import re


class SignupSchema(Schema):
    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True,unique = True)
    password = fields.Str(required=True)

    @validates("password")
    def validate_password(self, password):
        if not password.strip():
           raise ValidationError(" password should not be blank.")
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[!@#$%^&*()_]", password):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        if not re.search(r"[1-9]", password):
            raise ValidationError("Password must contain at least one numerical value")

        if not re.search(r"[a-z]", password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[A-Z]", password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return password
    
    @validates("username")
    def validate_username(self, value):
        if not value.strip():
            raise ValidationError("Username should not be blank.")


class ProfileSchema(Schema):
    id = fields.UUID()
    username = fields.Str(required=False)
    profile_pic = fields.Str(required=False)
    bio = fields.Str(required=False)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    
    @validates("password")
    def validate_password(self, password):
        if not password.strip():
           raise ValidationError("password should not be blank.")


class UpdatePasswordSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True)
    @validates("new_password")
    def validate_password(self, new_password):
        if not new_password.strip():
           raise ValidationError("new password should not be blank.")
    
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[!@#$%^&*()_]", new_password):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        if not re.search(r"[1-9]", new_password):
            raise ValidationError("Password must contain at least one numerical value")

        if not re.search(r"[a-z]", new_password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[A-Z]", new_password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return new_password


class ResetPasswordSchema(Schema):
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)
    
    @validates("new_password")
    def validate_password(self, new_password):
        if not new_password.strip():
           raise ValidationError("new password should not be blank.")
    
        if len(new_password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[!@#$%^&*()_]", new_password):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        if not re.search(r"[1-9]", new_password):
            raise ValidationError("Password must contain at least one numerical value")

        if not re.search(r"[a-z]", new_password):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"[A-Z]", new_password):
            raise ValidationError(
                "Password must contain at least one uppercase letter."
            )

        return new_password