import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.models.follow_request import FollowRequest
from app.models.follower import Follow
from app.extensions import db
from werkzeug.security import generate_password_hash
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
        is_active=True,
        is_private=True
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user

@pytest.fixture
def user_data_second(app):
    """Fixture to create a sample user for testing."""
    user = User(
        username="test_user3",
        email="user3@example.com",
        password=generate_password_hash("Bhole057p@1"),
        is_verified=True,
        is_deleted=False,
        is_active=True,
        is_private=False
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


@pytest.fixture
def another_user_data(app):
    """Fixture to create a sample user for testing."""
    user = User(
        username="test_user2",
        email="user2@example.com",
        password=generate_password_hash("Bhole057p@1"),
        is_verified=True,
        is_deleted=False,
        is_active=True,
        is_private=True
    )
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    return user


@pytest.fixture
def follow_request_data(app, another_user_data,user_data):
    """Fixture to create a sample follow request for testing."""
    follow_request = FollowRequest(
        follower_id=another_user_data.id,
        following_id=user_data.id
    )
    with app.app_context():
        db.session.add(follow_request)
        db.session.commit()
        db.session.refresh(follow_request)
    return follow_request


class TestFollowRequestAcceptApi:
    """Class-based tests for Follow Request Accept API operations."""

    @pytest.fixture(autouse=True)
    def setup(self, client, user_data,another_user_data, user_data_second,follow_request_data):
        """Setup for each test."""
        self.client = client
        self.another_user_data = another_user_data
        self.user_data_second = user_data_second
        self.user_data = user_data
        self.follow_request_data = follow_request_data
        self.access_token = create_access_token(identity=self.user_data.id)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def test_accept_follow_request(self):
        """Test accepting a follow request."""
        data = {"user_id": str(self.another_user_data.id)}
        response = self.client.post(
            '/api/users/follow-request/',
            json=data,
            headers=self.headers,
            query_string={"action": "accept"}
        )
        assert response.status_code == 201
        assert response.json["message"] == "Follow request accepted; now the user is your follower"

    def test_reject_follow_request(self):
        """Test rejecting a follow request."""
        data = {"user_id": str(self.another_user_data.id)}
        response = self.client.post(
            '/api/users/follow-request/',
            json=data,
            headers=self.headers,
            query_string={"action": "reject"}
        )
        assert response.status_code == 200
        assert response.json["message"] == "Follow request rejected"

    def test_invalid_action(self):
        """Test providing an invalid action."""
        data = {"user_id": str(self.another_user_data.id)}
        response = self.client.post(
            '/api/users/follow-request/',
            json=data,
            headers=self.headers,
            query_string={"action": "invalid_action"}
        )
        assert response.status_code == 400
        assert response.json["error"] == "Invalid action"

    def test_user_not_found(self):
        """Test accepting a follow request that does not exist."""
        data = {"user_id": str(uuid.uuid4())}
        response = self.client.post(
            '/api/users/follow-request/',
            json=data,
            headers=self.headers,
            query_string={"action": "accept"}
        )
        assert response.status_code == 404
        assert response.json["error"] == "User not found"


    def test_accept_follow_request_public_account(self):
        """Test accepting a follow request with a public account."""
        # Set user as public
        access_token = create_access_token(identity=self.user_data_second.id)
        headers = {"Authorization": f"Bearer {access_token}"}

        # Should print False
        print(f"User account is private: {self.user_data_second.is_private}")

        data = {"user_id": str(self.another_user_data.id)}
       

        response = self.client.post(
            '/api/users/follow-request/',
            json=data,
            headers=headers,
            query_string={"action": "accept"}
        )
        print(response.json)
        # print("Response:", response.json)  # Debug output

        # Ensure it returns a 400 when the account is public
        assert response.status_code == 400
        assert response.json["error"] == "You can't implement this request; your account is public"
