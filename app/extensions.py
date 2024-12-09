from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()

redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
