import pytest
from flask_jwt_extended import create_access_token
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.extensions import db

@pytest.fixture
def user_data(app):
    """Fixture to create a sample user for testing."""
    user = User(
        username="test_user",
        email="user@example.com",
        password="hashed_password",  # Use an actual hashing method
        is_verified=True
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


@pytest.fixture
def post_data(app, user_data):
    """Fixture to create a sample post for testing."""
    post = Post(
        title="Test Post",
        caption="Test Caption",
        user=user_data.id,
        is_enable_comment=True
    )
    with app.app_context():
        db.session.add(post)
        db.session.commit()
        db.session.refresh(post)
    return post


class TestCommentApi:
    """Class-based tests for Comment API."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data, post_data):
        """Setup for each test."""
        self.client = client
        self.user = user_data
        self.post = post_data
        self.access_token = create_access_token(identity=self.user.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_create_comment_success(self):
        """Test creating a comment with valid data."""
        data = {
            "post_id": str(self.post.id),
            "content": "This is a test comment."
        }
        response = self.client.post(
            "/api/comments/",
            json=data,
            headers=self.headers
        )

        assert response.status_code == 201
        assert response.json["content"] == "This is a test comment."
        assert response.json["post"] == str(self.post.id)

    def test_create_comment_invalid_post(self):
        """Test creating a comment with an invalid post ID."""
        data = {
            "post_id": "invalid-uuid",
            "content": "This is a test comment."
        }
        response = self.client.post(
            "/api/comments/",
            json=data,
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"

    def test_create_comment_post_not_found(self):
        """Test creating a comment for a non-existent post."""
        data = {
            "post_id": "2ed0a99e-54ea-46f2-aded-2e8230ecb203",
            "content": "This is a test comment."
        }
        response = self.client.post(
            "/api/comments/",
            json=data,
            headers=self.headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "Post not found"


    def test_create_comment_missing_data(self):
        """Test creating a comment without providing required fields."""
        data = {
            "post_id": str(self.post.id)
        }
        response = self.client.post(
            "/api/comments/",
            json=data,
            headers=self.headers
        )

        assert response.status_code == 400
        assert "content" in response.json["errors"]
