from flask import Blueprint
from app.views.user_activity_view import UserActivity

user_activity_view = Blueprint("user_activity",__name__)

user_activity_view.add_url_rule("/users/activity",view_func=UserActivity.as_view("user_activity"),methods = ["GET"])