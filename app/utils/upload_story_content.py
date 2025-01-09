import re
from botocore.exceptions import ClientError
from flask import current_app
from app.extensions import db
from app.utils.s3_utils import get_s3_client
from app.constraints import get_s3_file_url
from typing import Optional


def get_image_path(url: str) -> Optional[str]:
    """
    Extracts the image path from the given URL.
    
    Args:
        url: The URL of the story image/video.

    Returns:
        The constructed S3 path, or None if the URL doesn't match the pattern.
    """
    # Pattern to extract the folder ID and file name
    pattern: str = r"posts/([^/]+)/(.+)$"
    match = re.search(pattern, url)
    if match:
        folder_id = match.group(1)  # Extract the folder ID
        file_name = match.group(2)  # Extract the file name
        new_path = f"story/{folder_id}/{file_name}"
        return new_path
    return None


def story_upload(file, story, user_id: str) -> None:
    """
    Uploads the story image or video to S3.

    Args:
        file: The image or video file to upload.
        story: The story object to update with the uploaded content URL.
        user_id: The ID of the user uploading the content.

    Returns:
        None
    """
    bucket_name: str = current_app.config['S3_BUCKET_NAME']
    s3_client = get_s3_client()

    if file:
        # Generate a new file name and store it in the story folder for the user
        new_file_key: str = f"story/{user_id}/{file.filename}"
        try:
            # Upload the content to S3
            s3_client.upload_fileobj(file, bucket_name, new_file_key)
            # Generate the new file URL
            new_file_url: str = get_s3_file_url(new_file_key)

            # Update the database with the new file URL
            story.content = new_file_url
            db.session.commit()

        except ClientError as e:
            current_app.logger.error(f"Failed to upload file to S3: {e}")
