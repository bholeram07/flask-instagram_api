from flask import Flask, jsonify
from config import Config
from flask_uuid import UUIDConverter
from app.extensions import db, mail, migrate, jwt, redis_client
import os
import boto3
from app.s3_bucket_config import create_s3_client
import logging
from flask_swagger_ui import get_swaggerui_blueprint

# Swagger UI configuration
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/swagger.yaml'  # Our API url (can of course be a local resource)

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Flask API"
    }
)


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
    
    
def create_app(test_config=None):
    """A function to create and initialize the flask app"""
    # initialize the flask app
    app = Flask(__name__)
    app.static_folder = 'static'
    # initialize the configuration define in the config file
    app.config.from_object(Config)
    # Set timezone
    os.environ['TZ'] = app.config['TIMEZONE']
    #for testing
    if test_config:
        app.config.update(test_config)
    app.url_map.converters["uuid"] = UUIDConverter
    # config the redis client
    app.config["REDIS_CLIENT"] = redis_client
    # set up the logger
    setup_logging(app)
    # setup_logging(app)
    initialize_extensions(app)
    # import the blueprint and register with app
    from app.blueprints import register_blueprints
    register_blueprints(app)
    # register the jwt handlers
    register_jwt_handlers(app)
    # Register Swagger UI blueprint
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app


def initialize_extensions(app):
    """An function to initialize the db, mail, jwt and migrate """
    mail.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)


def register_jwt_handlers(app):
    """function to register jwt handlers"""
    # check the jwt token validation
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
