from app.views.like_view import LikeAPi
from flask import Blueprint

like_api = Blueprint("like_api", __name__)
like_api.add_url_rule(
    "/posts/like/", view_func=LikeAPi.as_view("like_api"), methods=["POST",]
)
like_api.add_url_rule(
    "/posts/<post_id>/like/", view_func=LikeAPi.as_view("get_post_like"), methods=["GET"]
)
