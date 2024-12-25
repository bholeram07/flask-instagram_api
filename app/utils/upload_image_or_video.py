from flask import current_app,jsonify
from app.extensions import db
from app.utils.s3_utils import get_s3_client
from botocore.exceptions import ClientError
import re


class PostImageVideo:
    def __init__(self, post, file, user_id):
        self.post = post
        self.file = file
        self.user_id = user_id
        self.bucket_name = current_app.config['S3_BUCKET_NAME']
        self.s3_client = get_s3_client()

    @staticmethod
    def get_image_path(url):
        pattern = r"posts/([^/]+)/(.+)$"
        match = re.search(pattern, url)
        if match:
            folder_id = match.group(1)  # Extract the folder ID
            file_name = match.group(2)  # Extract the file name
            new_path = f"posts/{folder_id}/{file_name}"
            return new_path
        return None

    def upload_image_or_video(self):
        new_file_key = f"posts/{self.user_id}/{self.file.filename}"
        new_file_url = f"{current_app.config['S3_ENDPOINT_URL']}/{self.bucket_name}/{new_file_key}"
        try:
            self.s3_client.upload_fileobj(
                Fileobj=self.file, Bucket=self.bucket_name, Key=new_file_key)
            self.post.image_or_video = new_file_url
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error in uploading: {e}")
            raise

    def update_image_or_video(self):
        self.delete_image_or_video()
        self.upload_image_or_video()

    def delete_image_or_video(self):
        
        exist_image_or_video = self.post.image_or_video
        file_key = self.get_image_path(exist_image_or_video)
        if file_key:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=file_key)
            except Exception as e:
                current_app.logger.error(f"Error in deleting: {e}")
                raise
