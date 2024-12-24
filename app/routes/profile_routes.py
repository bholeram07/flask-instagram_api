from app.views.user_profile_view import UserProfile
from flask import Blueprint
 

user_profile = Blueprint("user_profile", __name__)

user_profile.add_url_rule(
    "/users/profile/", view_func=UserProfile.as_view("profile_api"), methods=["PATCH", "GET"]
)

user_profile.add_url_rule(
    "/users/<user_id>/profile/",
    view_func=UserProfile.as_view("user_profile_api"),
    methods=["GET"]
)
