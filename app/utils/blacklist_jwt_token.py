from flask import current_app
from flask_jwt_extended import get_jwt


def blacklist_jwt_token():
    """Blacklists the current JWT by storing it in Redis."""
    jti = get_jwt()["jti"]
    expires_in = get_jwt()["exp"] - get_jwt()["iat"]
    redis_client = current_app.config["REDIS_CLIENT"]
    redis_client.setex(jti, expires_in, "blacklisted")
