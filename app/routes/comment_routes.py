from flask import Blueprint
from app.views.comment_view import CommentApi

comment_api = Blueprint("comment_api", __name__)

comment_view = CommentApi.as_view("comment_api")
comment_api.add_url_rule(
    "/comments/<comment_id>", view_func=comment_view, methods=["GET", "POST", "PUT", "DELETE"]
)
comment_api.add_url_rule(
    "/posts/<post_id>/comments/", view_func=comment_view, methods=["GET"]
)
