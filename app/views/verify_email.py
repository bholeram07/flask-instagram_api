from app import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from app.models.user import User


auth = Blueprint('auth', __name__)


@auth.route('/verify-email/<token>', methods=['POST'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    # Deserializing the token, validating it with a max age of 1 hour
    email = serializer.loads(
        token, salt="email-verification")  # 1-hour expiration

    # Find the user in the database by email
    user = User.query.filter_by(email=email).first()

    if user:
        
        # If the user is found and not verified, set them as verified
        if not user.is_verified:
            user.is_verified = True
            db.session.commit()
            return jsonify({"message": "Email successfully verified!"}), 200
        #if user is already verified
        else:
            return jsonify({"message": "Email already verified"}), 400
    else:
        return jsonify({"error": "Invalid token or user not found"}), 400
