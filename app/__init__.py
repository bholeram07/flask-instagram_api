from flask import Flask, jsonify
from config import Config
from flask_uuid import UUIDConverter
from app.extensions import db, mail, migrate, jwt, redis_client
from app.blueprints import register_blueprints
import os
import boto3
from app.s3_bucket_config import create_s3_client
import logging


def setup_logging(app):
    # Create logs directory inside instance folder if it doesn't exist
    log_dir = os.path.join(app.instance_path, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Define log file path
    log_file = os.path.join(log_dir, 'flask_api.log')

    # Set up logging configuration
    logger = logging.getLogger()  # Root logger

    # StreamHandler for printing logs to console (print all logs to the terminal)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # Print all logs to the console

    # FileHandler for storing logs in the file (only info and above)
    file_handler = logging.FileHandler(log_file)
    # Store info and above logs in the file
    file_handler.setLevel(logging.INFO)

    # Define log format
    formatter = logging.Formatter('%(levelname)s - %(message)s')

    # Apply formatter to both handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Set the default logging level for the root logger
    # This will capture all logs of DEBUG level and above
    logger.setLevel(logging.DEBUG)

    # Disable Flask's default logs (Werkzeug)
    # werkzeug_log = logging.getLogger('werkzeug')
    # werkzeug_log.setLevel(logging.ERROR)
    
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.url_map.converters["uuid"] = UUIDConverter
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(folder_path)
        
    app.config["REDIS_CLIENT"] = redis_client
    app.config['SECRET_KEY'] = 'dvwLc-YxtZ1zquu6hLLn-HfVO7HAl3J4hu5yTa-l0sfgZAoEA7k2inqRwlMRndgYbAY'
    setup_logging(app)
    initialize_extensions(app)
    register_blueprints(app)
    register_jwt_handlers(app)

    return app
    
def initialize_extensions(app):
    mail.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)


def register_jwt_handlers(app):
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
        return jsonify({"error": "You have to login first"}), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return redis_client.exists(jti)
