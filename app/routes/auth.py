from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

bp = Blueprint('auth', __name__)


# Authentication decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, bp.app_config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise Exception('User not found')
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated


@bp.route('/signup', methods=['POST'])
# @token_required
# def signup(current_user):
def signup():
    # if current_user.role != 'admin':
    #     return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 400

    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password, email=data['email'],
                    role=data.get('role', 'user'))

    # Generate and store Fernet key
    new_user.generate_fernet_key()

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered. You can now login.'}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password_hash(user.password, data['password']) and user.is_approved:
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.now() + timedelta(hours=24),
            'role': user.role
        }, bp.app_config['JWT_SECRET_KEY'], algorithm="HS256")
        return jsonify({
            'user_id': user.id,
            'token': token,
            'role': user.role
        })

    return jsonify({'message': 'Invalid credentials or user not approved'}), 401