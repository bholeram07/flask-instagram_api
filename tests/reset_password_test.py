import pytest
from unittest.mock import MagicMock
from flask import Flask, jsonify
from app.views.auth_view import ResetPassword
from app.models.user import User  # Adjust based on your actual model
from app.extensions import db
# Assuming you're using SQLAlchemy
from werkzeug.security import generate_password_hash
import secrets


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

    # Add the user to the database
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    return user


@pytest.fixture
def mock_redis(app, user_data):
    redis_client = app.config['REDIS_CLIENT']
    # Simulating a valid user_id in Redis
    redis_client.get.return_value = user_data.id
    redis_client.delete.return_value = None
    return redis_client


def test_reset_password_success(client, mock_redis, user_data):
    data = {
        "new_password": "Bhole057p@",
        "confirm_password": "Bhole057p@"
    }

    # Mock the get_user function to return a user with ID "1"

    token = secrets.token_urlsafe(32)
    # Send the request to the reset password endpoint
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 200
    assert response.json == {"message": "Password reset successfully"}


def test_new_password_same(client, mock_redis, user_data):
    data = {
        "new_password": "Bhole057p@1",
        "confirm_password": "Bhole057p@"
    }

    # Mock the get_user function to return a user with ID "1"

    token = secrets.token_urlsafe(32)
    # Send the request to the reset password endpoint
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 400
    assert response.json["error"] == "new and old password not be same"


def test_confirm_password_equal(client, mock_redis, user_data):
    data = {
        "new_password": "Bhole057p@",
        "confirm_password": "Bhole057p@1"
    }
    token = secrets.token_urlsafe(32)
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 400
    assert response.json["error"] == "new password and confirm password must be equal"


def test_missing_field(client, mock_redis, user_data):
    data = {

        "confirm_password": "Bhole057p@1"
    }
    token = secrets.token_urlsafe(32)
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 400
    assert response.json["errors"]["new_password"] == "Missing data for required field."


def test_missing_field_confirm_password(client, mock_redis, user_data):
    data = {

        "new_password": "Bhole057p@1"
    }
    token = secrets.token_urlsafe(32)
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 400
    assert response.json["errors"]["confirm_password"] == "Missing data for required field."


def test_blank_field(client, mock_redis, user_data):
    data = {

        "new_password": "",
        "confirm_password": "Bhole057p@1"
    }
    token = secrets.token_urlsafe(32)
    response = client.post('/api/reset-password/{token}/', json=data)

    assert response.status_code == 400
    assert response.json["errors"]["new_password"] == "new password should not be blank."
