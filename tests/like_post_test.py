import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash
from io import BytesIO
from app.models.post import Post
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
def post_data(app, user_data):
    """Fixture to create a sample user for testing."""
    post = Post(
        title="test_user",
        image_or_video="bhole.jpg",
        caption="this is the post",
        is_deleted=False,
    )
    with app.app_context():
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
    return post


@pytest.fixture
def create_likes(user_data, post_data):
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
            post=post_data.id,
            user=user_data.id
        )
        db.session.add(like)
        likes.append(like)
    db.session.commit()
    return likes


class TestPostLikeApi:
    """Class-based tests for Post Like API operations."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data, post_data):
        """Setup for each test."""
        self.client = client
        self.user_data = user_data
        self.post_data = post_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_like_post(self):
        """Test liking a post."""
        data = {"post_id": str(self.post_data.id)}

        response = self.client.post(
            '/api/posts/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 201
        assert response.json["post"]["id"] == str(self.post_data.id)
        assert response.json["user"]["id"] == str(self.user_data.id)
        assert "liked_at" in response.json

    def test_unlike_post(self):
        """Test unliking a previously liked post."""
        # Like the post first
        data = {"post_id": str(self.post_data.id)}
        self.client.post('/api/posts/toggle-like/',
                         json=data, headers=self.headers)

        # Unlike the post
        response = self.client.post(
            '/api/posts/toggle-like/', json=data, headers=self.headers)

        assert response.status_code == 200
        assert response.json["message"] == "Post unliked"

    def test_invalid_post_id(self):
        """Test liking with an invalid post ID."""
        data = {"post_id": "invalid-uuid"}

        response = self.client.post(
            '/api/posts/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"

    def test_post_not_exist(self):
        """Test liking a post that does not exist."""
        data = {"post_id": str(uuid.uuid4())}  # Random UUID

        response = self.client.post(
            '/api/posts/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Post not found"

    def test_get_likes_valid_post(self, create_likes):
        """Test fetching likes for a valid post with likes."""
        response = self.client.get(
            f'/api/posts/{self.post_data.id}/like/',
            headers=self.headers
        )
        assert response.status_code == 200
        assert "likes_count" in response.json
        assert response.json["items"][0]["post"] == str(self.post_data.id)

    def test_get_likes_invalid_post_id(self):
        """Test fetching likes without providing a post ID."""
        response = self.client.get(
            '/api/posts/1234/like/',
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"

    def test_get_likes_nonexistent_post(self):
        """Test fetching likes for a non-existent post."""
        response = self.client.get(
            f'/api/posts/{uuid.uuid4()}/like/',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "Post not found"