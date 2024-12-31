from app.utils.s3_utils import get_s3_client
from flask import current_app
from botocore.exceptions import ClientError
from app.extensions import db
<<<<<<< Updated upstream
=======
from app.constraints import get_s3_file_url
>>>>>>> Stashed changes


def get_image_path(url):
    """A function to get the image path"""
    #pattern
    pattern = r"posts/([^/]+)/(.+)$"
    #regix expression to find the pattern in the url
    match = re.search(pattern, url)
    if match:
        folder_id = match.group(1)  # Extract the folder ID
        file_name = match.group(2)  # Extract the file name
        new_path = f"story/{folder_id}/{file_name}"
        return new_path
    return None


def story_upload(file, story, user_id):
    """Upload the story image or video on the s3"""
    # get the buckent name
    bucket_name = current_app.config['S3_BUCKET_NAME']
    # get the s3 client
    s3_client = get_s3_client()
    if file:
        # generate a new file name that is in story folder , user id folder and store the image or video
        new_file_key = f"story/{user_id}/{file.filename}"
        try:
            # upload the content on s3 client
            s3_client.upload_fileobj(file, bucket_name, new_file_key)
            # generate the new file url
            new_file_url = f"{current_app.config['S3_ENDPOINT_URL']}/{current_app.config['S3_BUCKET_NAME']}/{new_file_key}"
        except ClientError as e:
            print(e)

        # Update database: Set profile_pic to None
        story.content = new_file_url
        db.session.commit()
