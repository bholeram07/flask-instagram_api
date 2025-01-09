import pytest
from flask import request
from app.models.user import User
from app.extensions import db
from werkzeug.security import generate_password_hash


@pytest.fixture
def user_data(app):
    """Fixture to create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        password=generate_password_hash("Bhole057p@"),
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



def test_login_success(client, user_data):
    # Send a POST request to the signup endpoint
    response = client.post('/api/login/', json={
        "username_or_email": user_data.email,
        "password": "Bhole057p@"
    })
    assert response.status_code == 200
    assert "access_token" in response.json


def test_login_success_username(client, user_data):
    # Send a POST request to the signup endpoint

    response = client.post('/api/login/', json={
        "username_or_email": user_data.username,
        "password": "Bhole057p@"
    })
    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json
    assert "access_token_expiration_time" in response.json
    assert "refresh_token_expiration_time" in response.json


def test_invalid_credentials(client):
    login_payload = {
        "username_or_email": "test@example.com",
        "password": "Bholep@"
    }
    response = client.post('/api/login/', json=login_payload)
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid credentials'


def test_invalid_username(client):
    login_payload = {
        "username_or_email": "bh@example.com",
        "password": "Bhole057p@"
    }
    response = client.post('api/login/', json=login_payload)
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid credentials'


def test_missing_password(client):
    login_payload = {
        "username_or_email": "bh@example.com",
    }
    response = client.post('api/login/', json=login_payload)
    assert response.status_code == 400
    assert response.json['errors']['password'] == 'Missing data for required field.'


def test_missing_username(client):
    login_payload = {
        "password": "Bhole057p@"
    }
    response = client.post('api/login/', json=login_payload)
    assert response.status_code == 400
    assert response.json['errors']['username_or_email'] == 'Missing data for required field.'


def test_password_not_blank(client):
    login_payload = {
        "password": "",
        "username_or_email": "test@example.com"
    }
    response = client.post('api/login/', json=login_payload)
    assert response.status_code == 400
    assert response.json['errors']['password'] == 'password should not be blank'