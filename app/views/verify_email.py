
from app import db
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask import Blueprint, request, jsonify, current_app
from flask import Blueprint,jsonify,current_app
from itsdangerous import URLSafeTimedSerializer, BadTimeSignature, SignatureExpired
from app.models.user import User



auth = Blueprint('auth', __name__)


@auth.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        # Deserializing the token, validating it with a max age of 1 hour
        email = serializer.loads(
            token, salt="email-verification", max_age=3600)  # 1-hour expiration

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        # Check if the user exists
        if user:
            # If the user is found and not verified, set them as verified
            if not user.is_verified:
                user.is_verified = True
                db.session.commit()
                return jsonify({"message": "Email successfully verified!"}), 200
            else:
                return jsonify({"message": "Email already verified"}), 200
        else:
            return jsonify({"error": "Invalid token or user not found"}), 400

    except SignatureExpired:
        # If the token has expired
        return jsonify({"error": "The token has expired. Please request a new verification link."}), 400

    except BadTimeSignature:
        # If the token has an invalid signature
        return jsonify({"error": "Invalid token. Please request a new verification link."}), 400

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

    # except Exception as e:
    # return jsonify({"error": "Invalid or expired token"}), 
