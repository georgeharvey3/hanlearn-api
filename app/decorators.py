from flask import request, jsonify
from functools import wraps
import jwt

from .models import User
from config import config


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            print("Token is missing")
            return jsonify({"message": "Token is missing"}), 401

        try:
            data = jwt.decode(token, config['dev'].SECRET_KEY)
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            print("Token is invalid")
            return jsonify({"message": "Token is invalid"}), 401

        return f(current_user, *args, **kwargs)

    return decorated
