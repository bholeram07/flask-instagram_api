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


class TestPostApi:
    """Class-based tests for Post API CRUD operations."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data):
        """Setup for each test."""
        self.client = client
        self.user_data = user_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def create_post(self):
        data = {
            "title": "Test Title",
            "caption": "Test Caption"
        }
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image_or_video': (image, "test_image.jpg")
        }

        response = self.client.post(
            '/api/posts/',
            data={**data, **files},
            content_type='multipart/form-data',
            headers=self.headers
        )

        return response.json["id"]

    def test_create_post_success(self):
        """Test creating a post with valid data and file."""
        data = {
            "title": "Test Title",
            "caption": "Test Caption"
        }
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image_or_video': (image, "test_image.jpg")
        }

        response = self.client.post(
            '/api/posts/',
            data={**data, **files},
            content_type='multipart/form-data',
            headers=self.headers
        )

        print(response.json)
        assert response.status_code == 201
        assert response.json["title"] == "Test Title"
        assert response.json["caption"] == "Test Caption"

    def test_missing_image_or_video(self):
        """Test creating a post without providing an image or video."""
        data = {
            "title": "Test Title",
            "caption": "Test Caption"
        }

        response = self.client.post(
            '/api/posts/',
            data=data,
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Please provide an image or video for post"

    def test_blank_image_or_video(self):
        """Test creating a post with an empty image or video field."""
        data = {
            "title": "Test Title",
            "caption": "Test Caption"
        }
        files = {
            'image_or_video': ""  # Blank file
        }

        response = self.client.post(
            '/api/posts/',
            data={**files, **data},
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Please provide an image or video for post"

    def test_update_post(self):
        post_id = self.create_post()
        updated_data = {
            "title": "Updated Title",
            "caption": "Updated Caption"
        }
        response = self.client.patch(
            f'/api/posts/{post_id}',
            json=updated_data,
            headers=self.headers
        )
        print(response.json)
        assert response.status_code == 202
        assert response.json["title"] == "Updated Title"
        assert response.json["caption"] == "Updated Caption"

    def test_update_post_not_found(self):
        post_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb203'
        updated_data = {
            "title": "Updated Title",
            "caption": "Updated Caption"
        }
        response = self.client.patch(
            f'/api/posts/{post_id}',
            json=updated_data,
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "Post does not exist"

    def test_update_post_no_permission(self):
        """Test updating a post created by another user."""
        another_user_token = create_access_token(
            identity=999999)  # Simulate another user
        print(another_user_token)
        headers = {"Authorization": f"Bearer {another_user_token}"}

        post_id = self.create_post()
       # Create a post as the current user

        updated_data = {
            "title": "Updated Title",
            "caption": "Updated Caption"
        }

        response = self.client.patch(
            f'/api/posts/{post_id}/',
            json=updated_data,
            headers=headers
        )

        # print(response.json)
        assert response.status_code == 404

    def test_provide_data_for_update(self):
        post_id = self.create_post()
        updated_data = {

        }
        response = self.client.patch(
            f'/api/posts/{post_id}',
            json=updated_data,
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Provide data to update"

    def test_only_image_data_for_update(self):
        post_id = self.create_post()
        print(post_id)
        image = BytesIO(b"test image content")  # Simulate an image file
        image.filename = "test_image.jpg"
        files = {
            'image_or_video': (image, "test_image.jpg")
        }

        response = self.client.patch(
            f'/api/posts/{post_id}',
            data=files,
            content_type='multipart/form-data',
            headers=self.headers
        )

        print(response.json)
        assert response.status_code == 202
        assert response.json["title"] == "Test Title"
        assert response.json["caption"] == "Test Caption"

    def test_only_data_for_update(self):
        post_id = self.create_post()
        data = {
            "title": "this is title",
            "caption": "this is caption"
        }

        response = self.client.patch(
            f'/api/posts/{post_id}',
            data=data,
            content_type='multipart/form-data',
            headers=self.headers
        )

        assert response.status_code == 202

    def test_delete_post_success(self):
        post_id = self.create_post()

        response = self.client.delete(
            f'/api/posts/{post_id}',
            headers=self.headers
        )
        assert response.status_code == 204

    def test_delete_post_no_permission(self):

        another_user_token = create_access_token(
            identity=999999)  # Simulate another user
        print(another_user_token)
        headers = {"Authorization": f"Bearer {another_user_token}"}

        post_id = self.create_post()
       # Create a post as the current user

        response = self.client.delete(
            f'/api/posts/{post_id}/',
            headers=headers
        )

        # print(response.json)
        assert response.status_code == 404

    def test_delete_post_not_exist(self):
        post_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb203'

        response = self.client.delete(
            f'/api/posts/{post_id}',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "Post does not exist"

    def test_get_post_success(self):
        post_id = self.create_post()
        response = self.client.get(
            f'/api/posts/{post_id}',
            headers=self.headers
        )

        assert response.status_code == 200
        assert "title" in response.json
        assert response.json["id"] == post_id

    def test_get_post_not_exist(self):
        post_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb202'
        response = self.client.get(
            f'/api/posts/{post_id}',
            headers=self.headers
        )
        assert response.status_code == 404
