import re
from botocore.exceptions import ClientError
from flask import current_app
from app.extensions import db
from app.utils.s3_utils import get_s3_client
from app.constraints import get_s3_file_url
from typing import Optional
import uuid


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
        unique_id = uuid.uuid4().hex
        new_file_key: str = f"story/{user_id}/{unique_id}_{file.filename}"
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


def delete_story_from_s3(story) -> None:
    """
    Deletes the S3 object associated with a story if the content contains an S3 URL.

    Args:
        story: The story object containing the content.

    Returns:
        None
    """
    content = story.content
    bucket_name = current_app.config['S3_BUCKET_NAME']
    s3_endpoint_url = current_app.config['S3_ENDPOINT_URL']
    s3_client = get_s3_client()

    # Check if the content contains an S3 URL matching the upload format
    if content and content.startswith(f"{s3_endpoint_url}/{bucket_name}/"):
        try:
            # Extract the file key from the content URL
            file_key = content.split(f"{s3_endpoint_url}/{bucket_name}/")[-1]

            # Delete the file from S3
            s3_client.delete_object(Bucket=bucket_name, Key=file_key)
            current_app.logger.info(
                f"Successfully deleted S3 object: {file_key}")

        except ClientError as e:
            current_app.logger.error(f"Failed to delete S3 object: {e}")
        except IndexError:
            current_app.logger.warning(
                "S3 URL is malformed or does not match the expected structure.")
    else:
        current_app.logger.info(
            "Content does not contain an S3 URL, skipping S3 deletion.")

