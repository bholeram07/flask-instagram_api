from app.views.like_view import PostLikeAPi,CommentLikeApi,StorylikeApi
from flask import Blueprint

like_api = Blueprint("like_api", __name__)
like_api.add_url_rule(
    "/posts/like/", view_func=PostLikeAPi.as_view("like_api"), methods=["POST",]
)
like_api.add_url_rule(
    "/posts/<post_id>/like/", view_func=PostLikeAPi.as_view("get_post_like"), methods=["GET"]
)
like_api.add_url_rule(
    "/comments/<comment_id>/like/", view_func=CommentLikeApi.as_view("create_like_comment"), methods=["POST","GET"]
)
like_api.add_url_rule(
    "/story/<story_id>/like/", view_func=StorylikeApi.as_view("story_like"), methods=["POST", "GET"]
)
