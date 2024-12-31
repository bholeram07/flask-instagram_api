from flask import current_app, jsonify
from app.extensions import db
from app.utils.s3_utils import get_s3_client
from botocore.exceptions import ClientError
<<<<<<< Updated upstream
=======
from app.constraints import get_s3_file_url
>>>>>>> Stashed changes
import re


class PostImageVideo:
    """A class to handle the upload,update and deletiion of the post on s3"""

    def __init__(self, post, file, user_id):
        self.post = post
        self.file = file
        self.user_id = user_id
        self.bucket_name = current_app.config['S3_BUCKET_NAME']
        self.s3_client = get_s3_client()

    # fuction to get the image path
    @staticmethod
    def get_image_path(url):
        """A function to get the image path"""
        pattern = r"posts/([^/]+)/(.+)$"
        # use the regix epression to find the pattern in the url
        match = re.search(pattern, url)
        if match:
            folder_id = match.group(1)  # Extract the folder ID
            file_name = match.group(2)  # Extract the file name
            new_path = f"posts/{folder_id}/{file_name}"
            return new_path
        return None

    def upload_image_or_video(self):
        """A function to upload the post to the s3"""
        # define the new file name that are in post folder, in the user_id folder
        new_file_key = f"posts/{self.user_id}/{self.file.filename}"
        # get the file url with the new file key
        new_file_url = f"{current_app.config['S3_ENDPOINT_URL']}/{self.bucket_name}/{new_file_key}"

        try:
            # upload the object to the s3
            self.s3_client.upload_fileobj(
                Fileobj=self.file, Bucket=self.bucket_name, Key=new_file_key)
            # set the url in the database
            self.post.image_or_video = new_file_url
            db.session.commit()
        except Exception as e:
            current_app.logger.error(f"Error in uploading: {e}")
            raise

    def update_image_or_video(self):
        """Function to update the post on the s3"""
        # delete the existing post
        self.delete_image_or_video()
        # upload the new file
        self.upload_image_or_video()

    def delete_image_or_video(self):
        """Function for deletion of the post on the s3"""
        exist_image_or_video = self.post.image_or_video
        # get the file path from get image path
        file_key = self.get_image_path(exist_image_or_video)
        if file_key:
            try:
                # delete the object
                self.s3_client.delete_object(
                    Bucket=self.bucket_name, Key=file_key)
            except Exception as e:
                current_app.logger.error(f"Error in deleting: {e}")
                raise
