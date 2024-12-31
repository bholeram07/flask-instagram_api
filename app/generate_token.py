from itsdangerous import URLSafeTimedSerializer

#token generation function
def generate_verification_token(email, secret_key):
    """generate a random token by the inbuilt function of flask"""
    #make the object of urlsafetimedserializer, pass the secret key
    serializer = URLSafeTimedSerializer(secret_key)
    #generate the token by serializing and pass the email
    return serializer.dumps(email, salt="email-verification")
