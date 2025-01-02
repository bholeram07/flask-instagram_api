from app.views.like_view import PostLikeAPi,CommentLikeApi,StorylikeApi
from flask import Blueprint

like_api = Blueprint("like_api", __name__)
like_api.add_url_rule(
    "/posts/toggle-like/", view_func=PostLikeAPi.as_view("like_api"), methods=["POST",]
)
like_api.add_url_rule(
    "/posts/<post_id>/like/", view_func=PostLikeAPi.as_view("get_post_like"), methods=["GET"]
)
like_api.add_url_rule(
    "/comments/<comment_id>/like/", view_func=CommentLikeApi.as_view("get_like_comment"), methods=["GET"]
)
like_api.add_url_rule(
    "/comments/toggle-like/", view_func=CommentLikeApi.as_view("create_like_comment"), methods=["POST"]
)
like_api.add_url_rule(
    "/story/<story_id>/like/", view_func=StorylikeApi.as_view("story_like_get"), methods=["GET"]
)
like_api.add_url_rule(
    "/story/toggle-like/", view_func=StorylikeApi.as_view("story_like_create"), methods=["POST"]
)
