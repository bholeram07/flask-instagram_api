from itsdangerous import URLSafeTimedSerializer


def generate_verification_token(email, secret_key):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt='email-confirm-salt')
