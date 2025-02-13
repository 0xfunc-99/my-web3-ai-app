from functools import wraps
import jwt
import datetime
from flask import request, jsonify
import os
import hashlib
import logging

logger = logging.getLogger(__name__)

# In a production environment, these should be stored securely (e.g., in a database with hashed passwords)
ADMIN_CREDENTIALS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest()  # Default password: admin123
}

# JWT Configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')  # Change in production
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION = datetime.timedelta(hours=1)

def generate_token(username):
    """Generate a JWT token for authenticated admin"""
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + TOKEN_EXPIRATION,
            'iat': datetime.datetime.utcnow(),
            'sub': username
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    except Exception as e:
        logger.error(f"Token generation error: {str(e)}")
        return None

def verify_token(token):
    """Verify the JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None

def admin_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                logger.warning("Invalid Authorization header format")
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            logger.warning("No token provided")
            return jsonify({'error': 'Token is missing'}), 401

        # Verify token
        admin_username = verify_token(token)
        if not admin_username:
            logger.warning("Invalid token")
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Add admin username to request context
        request.admin_username = admin_username
        return f(*args, **kwargs)

    return decorated

def verify_admin_credentials(username, password):
    """Verify admin credentials"""
    if username not in ADMIN_CREDENTIALS:
        return False
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return ADMIN_CREDENTIALS[username] == hashed_password

def change_admin_password(username, new_password):
    """Change admin password"""
    if username not in ADMIN_CREDENTIALS:
        return False
    
    ADMIN_CREDENTIALS[username] = hashlib.sha256(new_password.encode()).hexdigest()
    return True 