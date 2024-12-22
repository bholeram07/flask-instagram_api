from flask import Flask, jsonify
from config import Config
from flask_uuid import UUIDConverter
from app.extensions import db, mail, migrate, jwt, redis_client
from app.blueprints import register_blueprints
import os
import boto3
from app.s3_bucket_config import create_s3_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    app.url_map.converters["uuid"] = UUIDConverter
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(folder_path)
        
    app.config["REDIS_CLIENT"] = redis_client
    app.config['SECRET_KEY'] = 'dvwLc-YxtZ1zquu6hLLn-HfVO7HAl3J4hu5yTa-l0sfgZAoEA7k2inqRwlMRndgYbAY'

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
