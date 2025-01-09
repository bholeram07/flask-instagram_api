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
            story=post_data.id,
            user=user_data.id
        )
        db.session.add(like)
        likes.append(like)
    db.session.commit()
    return likes
