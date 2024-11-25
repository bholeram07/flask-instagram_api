from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import user
from models.user import TokenBlocklist
from routes.api import api 
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_mail import Mail
import os
# db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  # Replace with a strong secret key
    
    # Initialize JWTManager
    jwt = JWTManager(app)
    
    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)

    # Custom JWT error handlers
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
