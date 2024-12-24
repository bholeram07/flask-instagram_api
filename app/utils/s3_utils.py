import boto3
from flask import current_app


def get_s3_client():
    """
    Initializes and returns an S3 client for MinIO
    """
    return boto3.client(
        's3',
        endpoint_url=current_app.config['S3_ENDPOINT_URL'],
        aws_access_key_id=current_app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=current_app.config['S3_SECRET_KEY']
    )
