import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash
from io import BytesIO
from app.models.story import Story
from app.models.likes import Like
import uuid


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


@pytest.fixture
def story_data(app, user_data):
    """Fixture to create a sample story for testing."""
    story = Story(
        content="bhole.jpg",
        is_deleted=False,
    )
    with app.app_context():
        db.session.add(story)
        db.session.commit()
        db.session.refresh(story)
    return story


@pytest.fixture
def create_likes(user_data, story_data):
    """
    Fixture to create likes for a post in the database.

    Args:
        user_data: The user who likes the post.
        post_data: The post to be liked.

    Returns:
        A list of created likes.
    """
    likes = []
    for i in range(10):  # Create 10 likes for testing
        like = Like(
            id=uuid.uuid4(),
            story=story_data.id,
            user=user_data.id
        )
        db.session.add(like)
        likes.append(like)
    db.session.commit()
    return likes


class TestStoryLikeApi:
    """Class-based tests for Post Like API operations."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data, story_data):
        """Setup for each test."""
        self.client = client
        self.user_data = user_data
        self.story_data = story_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_like_story(self):
        """Test liking a post."""
        data = {"story_id": str(self.story_data.id)}

        response = self.client.post(
            '/api/story/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 201
        assert response.json["story_id"] == str(self.story_data.id)

    def test_unlike_story(self):
        """Test unliking a previously liked post."""
        # Like the post first
        data = {"story_id": str(self.story_data.id)}
        self.client.post('/api/story/toggle-like/',
                         json=data, headers=self.headers)
        response = self.client.post('/api/story/toggle-like/',
                                    json=data, headers=self.headers)
        assert response.status_code == 200
        assert response.json["message"] == "Story unliked"

    def test_invalid_story_id(self):
        """Test liking with an invalid post ID."""
        data = {"story_id": "invalid-uuid"}

        response = self.client.post(
            '/api/story/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid UUID format"

    def test_story_not_exist(self):
        """Test liking a post that does not exist."""
        data = {"story_id": str(uuid.uuid4())}  # Random UUID

        response = self.client.post(
            '/api/story/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Story does not exist"

    def test_get_likes_valid_post(self, create_likes):
        """Test fetching likes for a valid post with likes."""
        response = self.client.get(
            f'/api/story/{self.story_data.id}/like/',
            headers=self.headers
        )
        assert response.status_code == 200

    def test_get_likes_invalid_story_id(self):
        """Test fetching likes without providing a post ID."""
        response = self.client.get(
            '/api/story/1234/like/',
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid UUID format"

    def test_get_likes_nonexistent_story(self):
        """Test fetching likes for a non-existent post."""
        response = self.client.get(
            f'/api/story/{uuid.uuid4()}/like/',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "Story does not exist"

    def test_like_already_liked_story(self):
        """Test liking a story that is already liked."""
        data = {"story_id": str(self.story_data.id)}
        self.client.post('/api/story/toggle-like/', json=data, headers=self.headers)
        response = self.client.post('/api/story/toggle-like/', json=data, headers=self.headers)
        assert response.status_code == 200
        assert response.json["message"] == "Story unliked"



    def test_like_story_missing_story_id(self):
        """Test liking a story with missing story_id."""
        data = {}
        response = self.client.post('/api/story/toggle-like/', json=data, headers=self.headers)
        assert response.status_code == 400
        assert response.json["error"] == "Invalid UUID format"