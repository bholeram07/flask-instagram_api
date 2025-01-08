from flask import jsonify
from dotenv import load_dotenv
import os

load_dotenv()
class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the project   
    PROPAGATE_EXCEPTIONS = True
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    BROKER_URL = os.getenv('BROKER_URL')
    RESULT_BACKEND = os.getenv('RESULT_BACKEND')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    BLACKLIST_KEY = os.getenv('BLACKLIST_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TEST_DATABASE_URI = os.getenv("TEST_DATABASE_URI")
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    TIMEZONE = 'Asia/Kolkata'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY')
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
   