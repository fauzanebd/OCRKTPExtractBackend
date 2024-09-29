from flask import Blueprint, request, jsonify
from app.models.locations import Province, City, Subdistrict, Ward, Village
from app import db
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.routes.auth import token_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from app.utils.helpers import pagination_response

bp = Blueprint('locations', __name__)

@bp.route('/locations/provinces', methods=['GET'])
@token_required
def get_provinces(current_user):
    try:
        q = request.args.get('q')
        code = request.args.get('code')
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        query = Province.query
        if q:
            query = query.filter(Province.name.ilike(f"%{q}%"))
        if code:
            query = query.filter(Province.code == code)
        
        total = query.count()
        provinces = query.order_by(Province.name).limit(limit).offset(offset).all()
        
        return pagination_response([province.to_dict() for province in provinces], total, limit, page)
    except ValueError as ve:
        current_app.logger.error(f"Invalid parameter: {str(ve)}")
        return jsonify({'message': 'Invalid parameter'}), 400
    except SQLAlchemyError as se:
        current_app.logger.error(f"Database error: {str(se)}")
        return jsonify({'message': 'Database error'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_provinces: {str(e)}")
        return jsonify({'message': 'Unexpected error occurred'}), 500
  

@bp.route('/locations/cities', methods=['GET'])
@token_required
def get_cities(current_user):
  try:
    q = request.args.get('q')
    province_code = request.args.get('province_code')
    limit = request.args.get('limit', 10)
    page = request.args.get('page', 1)
    offset = (int(page) - 1) * int(limit)
    
    cities = City.query
    if q:
        cities = cities.filter(City.name.ilike(f"%{q}%"))
    if province_code:
        cities = cities.filter(City.province_code == province_code)
    
    total = cities.count()
    cities = cities.order_by(City.name).limit(limit).offset(offset).all()
    return pagination_response([city.to_dict() for city in cities], total, limit, page)
  except ValueError as ve:
    current_app.logger.error(f"Invalid parameter: {str(ve)}")
    return jsonify({'message': 'Invalid parameter'}), 400
  except SQLAlchemyError as se:
    current_app.logger.error(f"Database error: {str(se)}")
    return jsonify({'message': 'Database error'}), 500
  except Exception as e:
    current_app.logger.error(f"Unexpected error in get_provinces: {str(e)}")
    return jsonify({'message': 'Unexpected error occurred'}), 500
  
@bp.route('/locations/subdistricts', methods=['GET'])
@token_required
def get_subdistricts(current_user):
  try:
    q = request.args.get('q')
    city_code = request.args.get('city_code')
    limit = request.args.get('limit', 10)
    page = request.args.get('page', 1)
    offset = (int(page) - 1) * int(limit)
    
    subdistricts = Subdistrict.query
    if q:
        subdistricts = subdistricts.filter(Subdistrict.name.ilike(f"%{q}%"))
    if city_code:
        subdistricts = subdistricts.filter(Subdistrict.city_code == city_code)
    
    total = subdistricts.count()
    subdistricts = subdistricts.order_by(Subdistrict.name).limit(limit).offset(offset).all()
    
    return pagination_response([subdistrict.to_dict() for subdistrict in subdistricts], total, limit, page)
  except ValueError as ve:
    current_app.logger.error(f"Invalid parameter: {str(ve)}")
    return jsonify({'message': 'Invalid parameter'}), 400
  except SQLAlchemyError as se:
    current_app.logger.error(f"Database error: {str(se)}")
    return jsonify({'message': 'Database error'}), 500
  except Exception as e:
    current_app.logger.error(f"Unexpected error in get_provinces: {str(e)}")
    return jsonify({'message': 'Unexpected error occurred'}), 500
  
@bp.route('/locations/wards', methods=['GET'])
@token_required
def get_wards(current_user):
  try:
    q = request.args.get('q')
    subdistrict_code = request.args.get('subdistrict_code')
    limit = request.args.get('limit', 10)
    page = request.args.get('page', 1)
    offset = (int(page) - 1) * int(limit)
    
    wards = Ward.query
    if q:
        wards = wards.filter(Ward.name.ilike(f"%{q}%"))
    if subdistrict_code:
        wards = wards.filter(Ward.subdistrict_code == subdistrict_code)
    
    total = wards.count()
    wards = wards.order_by(Ward.name).limit(limit).offset(offset).all()
    
    return pagination_response([ward.to_dict() for ward in wards], total, limit, page)
  except ValueError as ve:
    current_app.logger.error(f"Invalid parameter: {str(ve)}")
    return jsonify({'message': 'Invalid parameter'}), 400
  except SQLAlchemyError as se:
    current_app.logger.error(f"Database error: {str(se)}")
    return jsonify({'message': 'Database error'}), 500
  except Exception as e:
    current_app.logger.error(f"Unexpected error in get_provinces: {str(e)}")
    return jsonify({'message': 'Unexpected error occurred'}), 500
      
