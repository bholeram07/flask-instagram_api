from flask import Blueprint
from app.views.comment_view import CommentApi
from app.views.comment_reply_view import ReplyCommentApi

comment_api = Blueprint("comment_api", __name__)

comment_view = CommentApi.as_view("comment_api")
comment_api.add_url_rule(
    "/comments/", view_func=comment_view, methods=["POST"]
)
comment_api.add_url_rule(
    "/comments/<comment_id>", view_func=comment_view, methods=["GET", "PUT", "DELETE"]
)
comment_api.add_url_rule(
    "/posts/<post_id>/comments/", view_func=comment_view, methods=["GET"]
)

comment_api.add_url_rule(
     "/comments/<comment_id>/reply", view_func=ReplyCommentApi.as_view("reply_comment"), methods=["GET"]
)


