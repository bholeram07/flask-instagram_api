import pytest
import uuid
from app.models.user import  User
from app.models.comment import Comment
from app.models.likes import Like
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from app.extensions import db
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
def comment_data(app, user_data):
    """
    Fixture to create a sample comment for testing.
    """
    comment = Comment(
        content="This is a test comment",
        user_id=user_data.id,
        is_deleted=False,
    )
    with app.app_context():
        db.session.add(comment)
        db.session.commit()
        db.session.refresh(comment)
    return comment


@pytest.fixture
def create_comment_likes(user_data, comment_data):
    """
    Fixture to create likes for a comment in the database.

    Args:
        user_data: The user who likes the comment.
        comment_data: The comment to be liked.

    Returns:
        A list of created likes.
    """
    likes = []
    for i in range(5):  # Create 5 likes for testing
        like = Like(
            id=uuid.uuid4(),
            comment=comment_data.id,
            user=user_data.id
        )
        db.session.add(like)
        likes.append(like)
    db.session.commit()
    return likes


class TestCommentLikeApi:
    """
    Class-based tests for Comment Like API operations.
    """

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data, comment_data):
        """
        Setup for each test.
        """
        self.client = client
        self.user_data = user_data
        self.comment_data = comment_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_like_comment(self):
        """
        Test liking a comment.
        """
        data = {"comment_id": str(self.comment_data.id)}

        response = self.client.post(
            '/api/comments/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 201
  

    def test_unlike_comment(self):
        """
        Test unliking a previously liked comment.
        """
        # Like the comment first
        data = {"comment_id": str(self.comment_data.id)}
        self.client.post('/api/comments/toggle-like/',
                         json=data, headers=self.headers)

        # Unlike the comment
        response = self.client.post(
            '/api/comments/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 200
        assert response.json["message"] == "Comment unliked"

    def test_invalid_comment_id(self):
        """
        Test liking with an invalid comment ID.
        """
        data = {"comment_id": "invalid-uuid"}

        response = self.client.post(
            '/api/comments/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"

    def test_comment_not_exist(self):
        """
        Test liking a comment that does not exist.
        """
        data = {"comment_id": str(uuid.uuid4())}  # Random UUID

        response = self.client.post(
            '/api/comments/toggle-like/',
            json=data,
            headers=self.headers
        )

        assert response.status_code == 404
        assert response.json["error"] == "comment not exist"
    
    def test_get_likes_valid_post(self, create_comment_likes):
        """Test fetching likes for a valid post with likes."""
        response = self.client.get(
            f'/api/comments/{self.comment_data.id}/like/',
            headers=self.headers
        )
        assert response.status_code == 200
        
    def test_get_likes_invalid_post_id(self):
        """Test fetching likes without providing a post ID."""
        response = self.client.get(
            '/api/comments/1234/like/',
            headers=self.headers
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid uuid format"
        
    def test_get_likes_nonexistent_post(self):
        """Test fetching likes for a non-existent post."""
        response = self.client.get(
            f'/api/comments/{uuid.uuid4()}/like/',
            headers=self.headers
        )
        assert response.status_code == 404
        assert response.json["error"] == "comment not exist"
        
    
    
    
