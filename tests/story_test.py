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


class TestStoryApi:
    """Class-based tests for Story API CRUD operations."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data):
        """Setup for each test."""
        self.client = client
        self.user_data = user_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def create_story(self):
        """Helper function to create a story."""
        data = {
            "content": "This is story Content"
        }

        response = self.client.post(
            '/api/story/',
            data=data,
            headers=self.headers
        )
        return response.json['id']

    def test_create_story(self):
        """Test creating a story with text content."""
        data = {
            "content": "This is story Content"
        }

        response = self.client.post(
            '/api/story/',
            data=data,
            headers=self.headers
        )
        assert response.status_code == 201
        assert response.json["content"] == "This is story Content"

    def test_create_story_image(self):
        """Test creating a story with image content."""
        image = BytesIO(b"test image content")
        image.filename = "test_image.jpg"
        files = {
            'content': (image, "test_image.jpg")
        }
        response = self.client.post(
            '/api/story/',
            data=files,
            content_type='multipart/form-data',
            headers=self.headers
        )
        assert response.status_code == 201

    def test_missing_content(self):
        """Test creating a story without content."""
        data = {
            "content": ""
        }
        response = self.client.post(
            '/api/story/',
            data=data,
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["errors"]["content"] == "Missing required field"

    def test_get_story(self):
        """Test retrieving a story by its ID."""
        story_id = self.create_story()

        response = self.client.get(
            f'/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json["id"] == story_id

    def test_get_invalid_story(self):
        """Test retrieving a story with an invalid ID."""
        story_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb20'
        response = self.client.get(
            f'/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"

    def test_get_nonexistent_story(self):
        """Test retrieving a non-existent story."""
        story_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb204'
        response = self.client.get(
            f'/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "story not exist"

    def test_delete_story(self):
        """Test deleting a story by its ID."""
        story_id = self.create_story()

        response = self.client.delete(
            f'/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 204

    def test_delete_nonexistent_story(self):
        """Test deleting a non-existent story."""
        story_id = '2ed0a99e-54ea-46f2-aded-2e8230ecb204'
        response = self.client.delete(
            f'/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "Story not exist"

    def test_delete_invalid_story_id(self):
        """Test deleting a story with an invalid ID."""
        response = self.client.delete(
            '/api/story/{story_id}/',
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"
 
