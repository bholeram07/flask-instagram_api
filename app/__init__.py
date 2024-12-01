from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_sqlalchemy import SQLAlchemy
from celery import Celery, Task
from flask_uuid import UUIDConverter
from app.db import db
from app.models.user import User
from app.models.post import Post
from app.routes.user_api import api
from app.routes.post_api import post_api
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_mail import Mail
import os
import redis
migrate = Migrate()
mail = Mail()


celery = None

def create_celery_app(app=None):
    global celery
    if app is None:
        app = create_app()  
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    return celery


def create_app():
    app = Flask(__name__)
    app.url_map.converters['uuid'] = UUIDConverter
    app.config.from_object(Config)
    app.config.from_object('config.Config')
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    create_celery_app(app)
    app.config["PROPAGATE_EXCEPTIONS"] =True
    app.config["API_TITLE"] = "Instagram Rest Api"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"]="/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"]= "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  
    app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASS')
    UPLOAD_FOLDER ='/uploads'
    app.config['UPLOAD_FOLDER'] =UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}
    app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)
    app.register_blueprint(post_api)
    
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    BLACKLIST_KEY = "blacklisted_tokens"
    app.config['REDIS_CLIENT'] = redis_client
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
       jti = jwt_payload['jti']
       return redis_client.exists(jti)
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