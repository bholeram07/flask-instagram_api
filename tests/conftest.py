import pytest
from app import create_app
from app.extensions import db
from flask import Flask



@pytest.fixture
def app():
    # Create a standalone Flask app instance for testing
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'postgresql://flask_user:1234@localhost/flask_test_db',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    # Initialize database and set testing configurations

    # Print configuration details for debugging
    print(f"Using database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    with app.app_context():
        print("Creating tables...")
        print(db)
        db.create_all()  # Create all tables in the test database

    # Yield the app instance for testing
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()

    # Cleanup after the tests
 

@pytest.fixture
def client(app):
    # Create a test client
    return app.test_client()


@pytest.fixture(autouse=True)
def _db(app):
    """Rollback any changes made to the database after each test."""
    # Use transaction rollback to maintain test isolation
    with app.app_context():
        # Begin a transaction for each test
        db.session.begin()
        yield db
        # db.session.rollback()


 # Return the user object for use in tests
