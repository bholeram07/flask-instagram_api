from botocore.exceptions import ClientError
from flask import current_app
from app.extensions import db
from app.utils.s3_utils import get_s3_client
from app.constraints import get_s3_file_url
import re
from typing import Optional


def get_image_path(url: str) -> Optional[str]:
    """
    Extracts the S3 file path from the given URL.
    """
    pattern: str = r"profile_pics/([^/]+)/(.+)$"
    match = re.search(pattern, url)
    if match:
        folder_id = match.group(1)  # Extract the folder ID
        file_name = match.group(2)  # Extract the file name

        # Construct the desired path
        return f"profile_pics/{folder_id}/{file_name}"
    return None


def update_profile_pic(user: object, file: Optional[object]) -> Optional[str]:
    """
    Updates the user's profile picture.

    Args:
        user: The user object whose profile picture needs to be updated.
        file: The new file object for the profile picture, or None to delete the existing picture.

    Returns:
        The new profile picture URL, or None if the profile picture is deleted.
    """
    # Current profile pic URL from the database
    current_profile_pic: Optional[str] = user.profile_pic
    bucket_name: str = current_app.config['S3_BUCKET_NAME']
    s3_client = get_s3_client()

    # Case 1: User submitted an empty profile picture (delete existing)
    if not file:
        if current_profile_pic:
            file_key = get_image_path(current_profile_pic)
            if file_key:
                try:
                    s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                except ClientError as e:
                    current_app.logger.info(f"Failed to delete S3 object: {e}")

        # Update database: Set profile_pic to None
        user.profile_pic = None
        db.session.commit()
        return user.profile_pic

    # Case 2: User uploaded a new profile picture
    if file:
        # Delete the old image of the user
        if current_profile_pic:
            file_key = get_image_path(current_profile_pic)
            if file_key:
                try:
                    s3_client.delete_object(Bucket=bucket_name, Key=file_key)
                except ClientError as e:
                    current_app.logger.info(f"Failed to delete S3 object: {e}")

        # Define the path of the new file
        new_file_key: str = f"profile_pics/{user.id}/{file.filename}"
        try:
            # Upload the new file to S3
            s3_client.upload_fileobj(file, bucket_name, new_file_key)
            new_file_url: str = get_s3_file_url(new_file_key)

            # Update database with the new profile picture URL
            user.profile_pic = new_file_url
            db.session.commit()  # Commit the changes to the database
            return new_file_url

        except ClientError as e:
            current_app.logger.error(
                f"Failed to upload new profile picture: {e}")
            raise e

    return None
