import jwt
import uuid
from datetime import datetime, timedelta
from django.conf import settings

def generate_token():
    """Generate a unique token for email verification or password reset"""
    return str(uuid.uuid4())

def generate_verification_token(user_id):
    """Generate a JWT token for email verification"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'type': 'email_verification'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token, token_type):
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload['type'] != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None