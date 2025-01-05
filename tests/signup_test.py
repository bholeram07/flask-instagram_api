import pytest
from flask import url_for, request


@pytest.fixture
def signup_payload():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Bhole057p@"
    }


def test_signup_success(client, signup_payload):
    # Send a POST request to the signup endpoint
    response = client.post(
        '/api/signup/', json=signup_payload)

    # Assert the status code is 201 Created
    print(response.json)
    assert response.status_code == 200


def test_username_already_exists(client, signup_payload):
    # Simulate an existing user
    client.post('/api/signup/', json=signup_payload)

    # Try to signup with the same username again
    response = client.post('/api/signup/', json=signup_payload)

    assert response.status_code == 409
    # assert response.json['error'] == 'Username already exists'


def test_exist_email(client, signup_payload):
    client.post('api/signup/', json=signup_payload)
    # Try to signup with the same username again
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 409


def test_password_blank(client):
    signup_payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": ""
    }
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 400
    assert response.json['errors']['password'] == "Password should not be blank"


def test_email(client):
    signup_payload = {
        "username": "testuser",
        "email": "testexample",
        "password": "Bhole057p@"
    }
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 400
    assert response.json['errors']['email'] == "Not a valid email address."


def test_missing_username(client):
    signup_payload = {
        "email": "testexample",
        "password": "Bhole057p@"
    }
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 400
    assert response.json['errors']['username'] == "Missing data for required field."


def test_missing_password(client):
    signup_payload = {
        "email": "testexample",
        "username": "testuser"
    }
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 400
    assert response.json['errors']['password'] == "Missing data for required field."


def test_missing_email(client):
    signup_payload = {
        "username": "testuser",
        "password": "Bhole@057p@"
    }
    response = client.post('/api/signup/', json=signup_payload)
    assert response.status_code == 400
    assert response.json['errors']['email'] == "Missing data for required field."
