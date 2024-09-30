from flask import Blueprint, request, jsonify
from app.models.user import User
from app import db
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.routes.auth import token_required
from app.utils.helpers import pagination_response

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
        new_user = User(
            username=data['username'], 
            password=hashed_password,
            role=data.get('role', 'user'),
            client_code=data.get('client_code', ''),
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

@bp.route('/users/get-subordinate', methods=['GET'])
@token_required    
def get_user_subordinate(current_user):
    try:
        q = request.args.get('q')
        limit = request.args.get('limit', 10)
        page = request.args.get('page', 1)
        offset = (int(page) - 1) * int(limit)
        province_code = request.args.get('province_code')
        city_code = request.args.get('city_code')
        subdistrict_code = request.args.get('subdistrict_code')
        ward_code = request.args.get('ward_code')
        village_code = request.args.get('village_code')
        
        query = User.query
        hierarchy = current_user.get_hierarchy_value()
        
        if q:
            query = query.filter(User.name.ilike(f"%{q}%"))
        if province_code:
            if hierarchy > 6 and current_user.province_code != province_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(User.province_code == province_code)
        if city_code:
            if hierarchy > 5 and current_user.city_code != city_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(User.city_code == city_code)
        if subdistrict_code:
            if hierarchy > 4 and current_user.subdistrict_code != subdistrict_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(User.subdistrict_code == subdistrict_code)
        if ward_code:
            if hierarchy > 3 and current_user.ward_code != ward_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(User.ward_code == ward_code)
        if village_code:
            if hierarchy > 2 and current_user.village_code != village_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(User.village_code == village_code)
            
        if current_user.role == 'enumerator' or hierarchy == 1:
            return jsonify({'message': 'Unauthorized'}), 401
        
        total = query.count()   
        users = query.limit(limit).offset(offset).all()
        
        data_res = [user.public_fields() for user in users]
        
        return pagination_response(data_res, total, limit, page)
        
    except Exception as e:
        current_app.logger.error(f"Error getting user's subordinate: {str(e)}")
        return jsonify({'message': 'Error getting user\'s subordinate'}), 500
