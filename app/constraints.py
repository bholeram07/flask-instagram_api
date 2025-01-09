
from flask import request,current_app


def get_reset_password_url(token:str)->str:
    """Dynamically generate the reset password URL."""
    return f"{request.host_url}api/reset-password/{token}"

def get_s3_file_url(new_file_key)->str:
    return f"{current_app.config['S3_ENDPOINT_URL']}/{current_app.config['S3_BUCKET_NAME']}/{new_file_key}"


