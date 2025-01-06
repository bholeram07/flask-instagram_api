import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.follower import Follow
from app.models.follow_request import FollowRequest
from app.extensions import db
from werkzeug.security import generate_password_hash


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

    yield user
    with app.app_context():
        db.session.rollback()
        db.session.close()


@pytest.fixture
def another_user(app):
    """Fixture to create another sample user for testing."""
    user = User(
        username="another_user",
        email="another@example.com",
        password=generate_password_hash("Bhole057p@2"),
        is_verified=True,
        is_deleted=False,
        is_active=True,
        is_private=False
    )

    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    yield user
    with app.app_context():
        db.session.rollback()
        db.session.close()


def test_follow_user(client, user_data, another_user):
    """Test following a user."""
    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": another_user.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    assert response.json["message"] == f"You are now following {another_user.username}"


def test_unfollow_user(client, user_data, another_user):
    """Test unfollowing a user."""
    # First, follow the user
    follow = Follow(follower_id=user_data.id, following_id=another_user.id)
    with client.application.app_context():
        db.session.add(follow)
        db.session.commit()

    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": another_user.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json["message"] == "Unfollowed"


def test_follow_private_user(client, user_data, another_user):
    """Test sending a follow request to a private user."""
    another_user.is_private = True
    with client.application.app_context():
        another_user.is_private = True
        db.session.commit()

    # Verify that the user is marked as private
    assert another_user.is_private is True

    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": another_user.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 201



def test_withdraw_follow_request(client, user_data, another_user):
    """Test withdrawing a follow request."""
    another_user.is_private = True
    with client.application.app_context():
        db.session.commit()

    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": another_user.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response = client.post(
        "/api/users/follow/",
        json={"user_id": another_user.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200



def test_follow_user_not_exist(client, user_data):
    """Test following a non-existent user."""
    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": "2cc1bb98-d729-4146-9482-85bfd88fee4c"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json["error"] == "User does not exist"


def test_follow_self(client, user_data):
    """Test trying to follow oneself."""
    access_token = create_access_token(identity=user_data.id)
    response = client.post(
        "/api/users/follow/",
        json={"user_id": user_data.id},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json["error"] == "You cant follow yourself"
