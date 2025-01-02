import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    # Create a test app instance
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


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
        db.session.rollback()
