from sqlalchemy.exc import SQLAlchemyError
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import jsonify, current_app
from app import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint, jsonify, current_app
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from app.models.user import User
from app.utils.get_validate_user import get_user


auth = Blueprint('auth', __name__)


@auth.route('/verify-email/<token>', methods=['POST'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        # Deserializing the token, validating it with a max age of 1 hour
        email = serializer.loads(
            token, salt="email-verification", max_age=3600)

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        if user:
            # If the user is found and not verified, set them as verified
            if not user.is_verified:
                user.is_verified = True
                db.session.commit()
                return jsonify({"message": "Email successfully verified!"}), 200

            # If the user is already verified
            return jsonify({"message": "Email already verified"}), 400

        # If the user is not found
        return jsonify({"error": "User not found"}), 404

    except SignatureExpired:
        return jsonify({"error": "The token has expired. Please request a new one."}), 400

    except BadSignature:
        return jsonify({"error": "Invalid token. Please check your email link."}), 400

    except SQLAlchemyError as e:
        # Handle database-related errors
        return jsonify({"error": "A database error occurred.", "details": str(e)}), 500

    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
