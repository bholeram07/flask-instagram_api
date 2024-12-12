from flask import Blueprint
from app.views.post_view import PostApi


post_api = Blueprint("post_api", __name__)

post_view = PostApi.as_view("post_api")
post_api.add_url_rule(
    "/posts/", view_func=post_view, methods=["GET", "POST",]
)
post_api.add_url_rule(
    "/posts/<post_id>", view_func=post_view, methods=["GET", "PATCH", "DELETE"]
)
post_api.add_url_rule(
    "/users/<user_id>/posts/", view_func=post_view, methods=["GET"]
)
