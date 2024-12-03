import os
from flask import jsonify
class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the project
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')      # Upload folder path
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    BLACKLIST_KEY = "blacklisted_tokens"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False