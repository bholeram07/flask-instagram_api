from app.utils.s3_utils import get_s3_client
from flask import current_app
from botocore.exceptions import ClientError
from app.extensions import db
def get_image_path(url):
    pattern = r"posts/([^/]+)/(.+)$"
    match = re.search(pattern, url)
    if match:
        folder_id = match.group(1)  # Extract the folder ID
        file_name = match.group(2)  # Extract the file name
        new_path = f"story/{folder_id}/{file_name}"
        return new_path
    return None


def story_upload(file, story,user_id):
    bucket_name = current_app.config['S3_BUCKET_NAME']
    s3_client = get_s3_client()
    if file:
        new_file_key = f"story/{user_id}/{file.filename}"
        try:
            s3_client.upload_fileobj(file, bucket_name, new_file_key)
            new_file_url = f"{current_app.config['S3_ENDPOINT_URL']}/{current_app.config['S3_BUCKET_NAME']}/{new_file_key}"
        except ClientError as e:
            print(e)

        # Update database: Set profile_pic to None
        story.content = new_file_url
        db.session.commit()
        
