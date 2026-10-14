from datetime import timedelta
from flask_jwt_extended import create_access_token
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_jwt_extended import jwt_required
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from jwt.exceptions import PyJWTError



def generate_token(username):  # for user authentication

    token = create_access_token(
        identity=username,
        expires_delta=timedelta(hours=1)  # token will expire after 1 hour
    )

    return token



def verify_token(token):

    try:                 # can fail bcs token expired/modified/invalid signature etc
        decoded = decode_token(token)

        return {
            "valid": True,
            "user": decoded["sub"]  # the subject of the token, usually the username
        } 

    except (JWTExtendedException, PyJWTError):  # catch JWT specific exceptions, including raw PyJWT decode errors (malformed/tampered tokens)

        return {
            "valid": False,
            "user": None
        }


def login_required(fn):

    @wraps(fn)
    def wrapper(*args, **kwargs):

        verify_jwt_in_request()

        return fn(*args, **kwargs)

    return wrapper




