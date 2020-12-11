from flask import request, jsonify, make_response
import jwt
import datetime
from functools import wraps

from ..models import User
from .. import db
from . import auth
from ..decorators import token_required
from config import config


@auth.route('/api/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first() is not None:
        return make_response(jsonify({"message": "EMAIL_EXISTS"}, 400))

    user = User(
        email=data['email'],
        username=data['email'],
        password=data['password'])
    db.session.add(user)
    db.session.commit()
    
    return make_response(jsonify({"message": "CREATED"}), 201)


@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if user is None:
        return make_response(jsonify({"message": "No Such Account"}), 400)
    
    if not user.verify_password(data['password']):
        return make_response(jsonify({"message": "Invalid Password"}), 400)

    exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    
    token = jwt.encode({"id": user.id, "exp": exp}, config['dev'].SECRET_KEY)

    return make_response(jsonify({
        'token' : token.decode('UTF-8'), 
        'user_id': user.id,
        'expires_at': exp.strftime("%Y-%m-%dT%H:%M:%SZ")}), 200)
