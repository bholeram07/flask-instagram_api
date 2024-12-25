from flask import Blueprint
from app.routes.auth_routes import user_api
from app.routes.post_routes import post_api
from app.routes.comment_routes import comment_api
from app.routes.like_routes import like_api
from app.routes.profile_routes import user_profile
from app.routes.follower_routes import follower_api
from app.routes.user_activity_routes import user_activity_view
from app.views.verify_email import auth # Import your blueprint



def register_blueprints(app):
    '''The blueprints of the api'''
    api_blueprint = Blueprint("api", __name__, url_prefix="/api")
   

    app.register_blueprint(auth, url_prefix='/auth')

    api_blueprint.register_blueprint(user_api)
    api_blueprint.register_blueprint(post_api)
    api_blueprint.register_blueprint(comment_api)
    api_blueprint.register_blueprint(like_api)
    api_blueprint.register_blueprint(follower_api)
    api_blueprint.register_blueprint(user_profile)
    api_blueprint.register_blueprint(user_activity_view)

    app.register_blueprint(api_blueprint)
