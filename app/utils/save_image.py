import os
from werkzeug.utils import secure_filename
from flask import current_app
from app.utils.allowed_file import allowed_file


def save_image(image):
    """
    Saves the image to the server if the file is allowed.

    """
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        return image_path
    return None
