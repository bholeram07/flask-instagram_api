from app.views.like_view import LikeAPi
from flask import Blueprint

like_api = Blueprint("like_api", __name__)
like_api.add_url_rule(
    "/posts/like/", view_func=LikeAPi.as_view("like_api"), methods=["GET", "POST",]
)
