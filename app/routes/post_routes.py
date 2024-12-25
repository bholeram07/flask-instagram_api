from flask import Blueprint
from app.views.post_view import PostApi,UserPostListApi


post_api = Blueprint("post_api", __name__)

post_view = PostApi.as_view("post_api")
user_post_list = UserPostListApi.as_view("user_post")
post_api.add_url_rule(
    "/posts/", view_func=post_view, methods=["POST",]
)
post_api.add_url_rule(
    "/posts/<post_id>", view_func=post_view, methods=["GET", "PATCH", "DELETE"]
)

post_api.add_url_rule(
    "/users/<user_id>/posts/", view_func=user_post_list, methods=["GET"]
)
post_api.add_url_rule(
    "/posts/", view_func=user_post_list, methods=["GET"]
)
