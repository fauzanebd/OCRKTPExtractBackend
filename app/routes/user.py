from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.routes.auth import token_required

bp = Blueprint('user', __name__)

@bp.route('/users/create-user', methods=['POST'])
@token_required
def create_user(current_user):
    try:
        data = request.get_json()
        if current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        hashed_password = generate_password_hash(data['password'])
        # get client_code from .env
        client_code = os.getenv('CLIENT_CODE')
        new_user = User(
            username=data['username'], 
            password=hashed_password,
            role=data.get('role', 'user'),
            client_code=data.get(client_code, ''),
            name=data.get('name', ''),
            no_phone=data.get('no_phone', ''),
            nasional=data.get('nasional', False),
            province_code=data.get('province_code', None),
            city_code=data.get('city_code', None),
            subdistrict_code=data.get('subdistrict_code', None),
            ward_code=data.get('ward_code', None),
            village_code=data.get('village_code', None),
            is_enumerator=data.get('is_enumerator', False)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User created!'}), 200
    except Exception as e:
        current_app.logger.error(f"Error creating user: {str(e)}")
        return jsonify({'message': 'Error creating user'}), 500
