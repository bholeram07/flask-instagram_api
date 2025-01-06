import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash
from io import BytesIO


@pytest.fixture
def user_data(app):
    """Fixture to create a sample user for testing."""
    user = User(
        username="test_user",
        email="user@example.com",
        password=generate_password_hash("Bhole057p@1"),
        is_verified=True,
        is_deleted=False,
        is_active=True
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


class TestProfile:
    @pytest.fixture(autouse=True)
    def setup(self, client, user_data):
        """Setup for each test."""
        self.client = client
        self.user_data = user_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_get_user_profile(self):

        response = self.client.get(
            f'/api/users/profile/',
            headers=self.headers
        )

        assert response.status_code == 200

    def test_get_user_profile_user_id(self):
        user_id = self.user_data.id

        response = self.client.get(
            f'/api/users/{user_id}/profile/',
            headers=self.headers
        )

        assert response.status_code == 200

    def test_update_user_profile(self):
        data = {
            "bio": "this is the profile of don",
            "other_social": "http://gkmit",
            "username": "bholerampatidar"
        }
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image': (image, "test_image.jpg")
        }

        response = self.client.patch(
            '/api/users/profile/',
            data={**data, **files},
            content_type='multipart/form-data',
            headers=self.headers
        )
        assert response.status_code == 202
        assert response.json["username"] == "bholerampatidar"

    def test_update_user_profile_only_image(self, user_data):
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image_or_video': (image, "test_image.jpg")
        }

        response = self.client.patch(
            '/api/users/profile/',
            data=files,
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 202

    def test_update_user_profile_delete_image(self, user_data):
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image_or_video': ""
        }

        response = self.client.patch(
            '/api/users/profile/',
            data=files,
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 202
        assert response.json["profile_pic"] == None

    def test_update_user_profile_provide_data(self, user_data):

        data = {

        }

        response = self.client.patch(
            '/api/users/profile/',
            data=data,
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Provide data to update"
