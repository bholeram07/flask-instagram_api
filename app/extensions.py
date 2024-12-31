from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import redis

#creation of object of required extension in flask i.e db
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
jwt = JWTManager()

#register the redis client
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)
