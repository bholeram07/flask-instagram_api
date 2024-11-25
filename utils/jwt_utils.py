

from datetime import datetime
from flask_jwt_extended import decode_token
from flask_jwt_extended import get_jwt

def add_to_blocklist(token):
    jti = decode_token(token)["jti"]
    new_blocked_token = TokenBlocklist(jti=jti, created_at=datetime.utcnow())
    db.session.add(new_blocked_token)
    db.session.commit()
    
    


def is_token_blacklisted(jti):
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None
