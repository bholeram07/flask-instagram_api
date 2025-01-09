from flask import Blueprint
from app.views.auth_view import Signup, Login, ResetPassword, ResetPasswordSendMail, UpdatePassword,Logout,DeactivateAccount,DeleteAccount



user_api = Blueprint("user_api", __name__)

user_api.add_url_rule(
    "/signup/", view_func=Signup.as_view("signup_api"), methods=["POST"]
)
user_api.add_url_rule(
    "/login/", view_func=Login.as_view("login_api"), methods=["POST"])
user_api.add_url_rule(
    "/logout/", view_func=Logout.as_view("logout_api"), methods=["DELETE"]
)
user_api.add_url_rule(
    "/update-password/",
    view_func=UpdatePassword.as_view("update_password_api"),
    methods=["PUT"],
)

user_api.add_url_rule(
    "/reset-password/send-mail/",
    view_func=ResetPasswordSendMail.as_view(
        "reset_password_send_mail_api"
    ), methods=['POST']
)

user_api.add_url_rule(
    "/reset-password/<token>/",
    view_func=ResetPassword.as_view("reset_password_api"),
    methods=["POST"],
)
user_api.add_url_rule(
    "/accounts/deactivate/",
    view_func=DeactivateAccount.as_view("deactivate_account"),methods =["PUT"]
)
user_api.add_url_rule(
    "/accounts/",
    view_func=DeleteAccount.as_view("delete_account"),methods =["DELETE"]    
)
