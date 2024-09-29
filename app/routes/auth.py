from flask import Blueprint, request, jsonify
from app.models.user import User
from app.models.locations import Province, City, Subdistrict, Ward, Village
from app import db
import jwt
import os
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
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Authorization header is missing!'}), 401
        
        try:
            # Check if the Authorization header starts with 'Bearer '
            if not auth_header.startswith('Bearer '):
                raise ValueError('Invalid token format')
            
            # Extract the token (remove 'Bearer ' prefix)
            token = auth_header.split(' ')[1]
            
            # Decode the token
            data = jwt.decode(token, bp.app_config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise Exception('User not found')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except (jwt.InvalidTokenError, ValueError):
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        
        return f(current_user, *args, **kwargs)

    return decorated


@bp.route('/signup', methods=['POST'])
# @token_required
# def signup(current_user):
def signup():
    try:
        if current_user.role != 'admin':
            return jsonify({'message': 'Unauthorized'}), 401
        data = request.get_json()
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400

        hashed_password = generate_password_hash(data['password'])
        client_code = os.getenv('CLIENT_CODE')
        new_user = User(
            username=data['username'], 
            password=hashed_password, 
            role=data.get('role', 'user'), 
            client_code=client_code,
            name=data.get('name', ''),
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'User registered. You can now login.'}), 200
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({'message': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401

        locations = user.get_user_locations()
        province = Province.query.filter_by(code=locations['province_code']).first()
        city = City.query.filter_by(code=locations['city_code']).first()
        subdistrict = Subdistrict.query.filter_by(code=locations['subdistrict_code']).first()
        ward = Ward.query.filter_by(code=locations['ward_code']).first()
        village = Village.query.filter_by(code=locations['village_code']).first()

        if user and check_password_hash(user.password, data['password']):
            token = jwt.encode({
                'user_id': user.id,
                'exp': datetime.now() + timedelta(hours=24),
                'role': user.role
            }, bp.app_config['JWT_SECRET_KEY'], algorithm="HS256")
            return jsonify({
                'user': user.public_fields({
                    'province': province.name if province else None,
                    'city': city.name if city else None,
                    'subdistrict': subdistrict.name if subdistrict else None,
                    'ward': ward.name if ward else None,
                }),
                'token': token,
            })

        return jsonify({'message': 'Invalid credentials or user not approved'}), 401
    
    except Exception as e:
        current_app.logger.error(str(e))
        return jsonify({'message': str(e)}), 500