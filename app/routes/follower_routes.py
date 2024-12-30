from flask import Blueprint
from app.views.follower_views import FollowApi,FollowingApi
from app.views.follow_request_view import FollowrequestAccept,FollowRequestWithdraw

follower_api = Blueprint("follower_api", __name__,url_prefix="/users")

follower_api.add_url_rule(
    "/follow/", view_func=FollowApi.as_view("follow_post"), methods=["POST"]
)
follower_api.add_url_rule(
    "/<user_id>/follow/", view_func=FollowApi.as_view("follow_delete"), methods=["DELETE"]
)

follower_api.add_url_rule(
    "/follower/", view_func=FollowApi.as_view("followers_list"), methods=["GET"]
)
follower_api.add_url_rule(
    "/<user_id>/follower/", view_func=FollowApi.as_view("user_followers_list"), methods=["GET"]
)

follower_api.add_url_rule(
    "/following/", view_func=FollowingApi.as_view("following_list"), methods=["GET"]
)
follower_api.add_url_rule(
    "/<user_id>/following/", view_func=FollowingApi.as_view("user_following_list"), methods=["GET"]
)
follower_api.add_url_rule(
    "/follow-request/",
    view_func=FollowrequestAccept.as_view("follow_request_accept"),
    methods=["POST"]
)
