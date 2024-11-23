from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import user
from routes.api import api 
from models import db
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
# db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY')  # Replace with a strong secret key
    # jwt = JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)
 
  
    app.register_blueprint(api)
    
    return app

