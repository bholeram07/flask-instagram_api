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

    return user


def test_delete_account(client, user_data):
    """Test successful password update."""
    # Generate a valid access token for the test user
    access_token = create_access_token(identity=user_data.id)
    response = client.delete(
        "/api/accounts/delete/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
   
