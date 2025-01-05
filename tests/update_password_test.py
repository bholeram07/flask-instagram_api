import pytest
from flask_jwt_extended import create_access_token
from app.models.user import User
from app.extensions import db
# Import your actual User model and db object
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

    # Add the user to the database
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

    yield user
    with app.app_context():
        db.session.rollback()
        db.session.close()

def test_update_password_success(client, user_data):
    """Test successful password update."""
    # Generate a valid access token for the test user
    access_token = create_access_token(identity=user_data.id)
    response = client.put(
        "/api/update-password/",
        json={
            "current_password": "Bhole057p@1",
            "new_password": "Bhole057p@",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 202

    assert response.json["message"] == "Password updated successfully"


def test_incorrect_password(client, user_data):
    access_token = create_access_token(identity=user_data.id)
    response = client.put(
        "/api/update-password/",
        json={
            "current_password": "Bhole057p",
            "new_password": "Bhole057p",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(response.json)
    assert response.status_code == 401
    assert response.json["error"] == "Invalid credentials"


def test_missing_field(client, user_data):
    access_token = create_access_token(identity=user_data.id)
    response = client.put(
        "/api/update-password/",
        json={
            "new_password": "Bhole057p",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json["errors"]["current_password"] == "Missing data for required field"


def test_password_not_same(client, user_data):
    access_token = create_access_token(identity=user_data.id)
    response = client.put(
        "/api/update-password/",
        json={
            "current_password": "Bhole057p@1",
            "new_password": "Bhole057p@1",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json["error"] == "Old and new passwords must not be the same"


def test_missing_field_new_password(client, user_data):
    access_token = create_access_token(identity=user_data.id)
    response = client.put(
        "/api/update-password/",
        json={
            "current_password": "Bhole057p@1",

        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 400
    assert response.json["errors"]["new_password"] == "Missing data for required field."
