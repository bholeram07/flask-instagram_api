from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy
from celery import Celery, Task

# Create a single instance of SQLAlchemy
db = SQLAlchemy()
from app.models.user import User
from app.models.user import TokenBlocklist
from app.routes.api import api 
from app.models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_mail import Mail
import os
# db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  # Replace with a strong secret key
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
    print(os.getenv('EMAIL_PASS'))
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')

    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error_string):
        return jsonify({"error": "Authorization header is missing or invalid"}), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(error_string):
        return jsonify({"error": "Invalid token"}), 422

    @jwt.revoked_token_loader
    def custom_revoked_token_response(jwt_header, jwt_payload):
        return jsonify({"error": "You have to login again"}), 401

    # Blacklist token loader
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']  # Extract the unique identifier (jti) from the JWT
        # Check if the token is blacklisted in the database
        return db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar() is not None

    return app


def make_celery(app):
    """Initialize Celery with Flask app context."""
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Task class that runs tasks with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery