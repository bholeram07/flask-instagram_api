import boto3


def create_s3_client(app):
    """Configuration of the s3 bucket"""
    s3_client = boto3.client(
        's3',
        endpoint_url=app.config['S3_ENDPOINT_URL'],
        aws_access_key_id=app.config['S3_ACCESS_KEY'],
        aws_secret_access_key=app.config['S3_SECRET_KEY']
    )
    # return the client
    return s3_client
