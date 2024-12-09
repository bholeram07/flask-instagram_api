from flask import Blueprint
from app.views.follower_view import FollowApi

follower_api = Blueprint("follower_api", __name__)


follower_view = FollowApi.as_view("follower_api")
follower_api.add_url_rule(
    "/follow/", view_func=follower_view, methods=["POST"]
)
follower_api.add_url_rule(
    "/<user_id>/follow/", view_func=follower_view, methods=["DELETE"]
)
follower_api.add_url_rule(
    "/follower/", view_func=follower_view, methods=["GET"]
)
follower_api.add_url_rule(
    "/<user_id>/follower/", view_func=follower_view, methods=["GET"]
)

follower_api.add_url_rule(
    "/api/users/following/", view_func=follower_view, methods=["GET"]
)
follower_api.add_url_rule(
    "/api/users/<user_id>/following/", view_func=follower_view, methods=["GET"]
)
