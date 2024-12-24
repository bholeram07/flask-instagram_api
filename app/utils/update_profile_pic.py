from botocore.exceptions import ClientError
from flask import current_app
from app.extensions import db
from app.utils.s3_utils import get_s3_client
import re

def get_image_path(url):
    pattern = r"profile_pics/([^/]+)/(.+)$"
    match = re.search(pattern, url)
    if match:
        folder_id = match.group(1)  # Extract the folder ID
        file_name = match.group(2)  # Extract the file name

        # Construct the desired path
        new_path = f"profile_pics/{folder_id}/{file_name}"
        return new_path

def update_profile_pic(user, file):
    """
    Updates the user's profile picture.
    """
    # Current profile pic URL from the database
    current_profile_pic = user.profile_pic
    bucket_name = current_app.config['S3_BUCKET_NAME']
    s3_client = get_s3_client()
    print(file)
    # Case 1: User submitted an empty profile picture (delete existing)
    if not file:
        if current_profile_pic:
            file_key = get_image_path(current_profile_pic)
            print(file_key)
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            except ClientError as e:
                print(e)

        # Update database: Set profile_pic to None
        user.profile_pic = None
        db.session.commit() 
        return user.profile_pic

    # Case 2: User uploaded a new profile picture
    if file:
        #delete the old image of the user
        if current_profile_pic:
            file_key = get_image_path(current_profile_pic)
            print(file_key)
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            except ClientError as e:
                print("error")
        
        #define the path of the new file   
        new_file_key = f"profile_pics/{user.id}/{file.filename}"
        # Upload the new file to S3
        try:
            s3_client.upload_fileobj(file, bucket_name, new_file_key)
            new_file_url = f"{current_app.config['S3_ENDPOINT_URL']}/{current_app.config['S3_BUCKET_NAME']}/{new_file_key}"
            
            # Update database with the new profile picture URL
            user.profile_pic = new_file_url
            db.session.commit() # Commit the changes to the database

        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            raise e
