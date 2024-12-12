from flask import Blueprint
from app.routes.auth_routes import user_api
from app.routes.post_routes import post_api
from app.routes.comment_routes import comment_api
from app.routes.like_routes import like_api
from app.routes.follower_routes import follower_api


def register_blueprints(app):
    '''The blueprints of the api'''
    api_blueprint = Blueprint("api", __name__, url_prefix="/api")

    api_blueprint.register_blueprint(user_api)
    api_blueprint.register_blueprint(post_api)
    api_blueprint.register_blueprint(comment_api)
    api_blueprint.register_blueprint(like_api)
    api_blueprint.register_blueprint(follower_api)

    app.register_blueprint(api_blueprint)
