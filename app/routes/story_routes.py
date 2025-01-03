from flask import Blueprint
from app.views.story_view import UserStory,GetStoryView

user_story_api = Blueprint("user_story",__name__)

user_story_api.add_url_rule("/story/",view_func=UserStory.as_view("user_story"),methods = ["POST","GET"])
user_story_api.add_url_rule("/story/<story_id>/", view_func=UserStory.as_view("user_story_get"),methods = ["GET","DELETE"])
user_story_api.add_url_rule(
    "/story/<story_id>/", view_func=GetStoryView.as_view("story_view"), methods=["GET"]
    )

user_story_api.add_url_rule(
    "/story/views", view_func=GetStoryView.as_view("get_all_story_view"), methods=["GET"]
)
