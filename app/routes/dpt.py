from flask import Blueprint, request, jsonify
from app.models.visi_misi import VisiMisi
from app import db
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.routes.auth import token_required
from app.utils.helpers import success_response, pagination_response
from app.models.dpt import DPT

bp = Blueprint('dpt', __name__)

@bp.route('/dpt', methods=['GET'])
@token_required
def get_dpt(current_user):
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
        
        hierarchy = current_user.get_hierarchy_value()
        query = DPT.query
        
        if q:
           query = query.filter(DPT.name.ilike(f"%{q}%"))
           
        if current_user.is_enumerator:
          locations = current_user.get_user_location()
          query = query.filter(DPT.ward_code == locations['ward_code'])
        else:
          if province_code:
            if hierarchy == 'province':
              query = query.filter(DPT.province_code == province_code)
            else:
              return jsonify({'message': 'Unauthorized'}), 401
          if city_code:
            if hierarchy == 'city':
              query = query.filter(DPT.city_code == city_code)
            else:
              return jsonify({'message': 'Unauthorized'}), 401
          if subdistrict_code:
            if hierarchy == 'subdistrict':
              query = query.filter(DPT.subdistrict_code == subdistrict_code)
            else:
              return jsonify({'message': 'Unauthorized'}), 401
          if ward_code:
            if hierarchy == 'ward':
              query = query.filter(DPT.ward_code == ward_code)
            else:
              return jsonify({'message': 'Unauthorized'}), 401
          if village_code:
            if hierarchy == 'village':
              query = query.filter(DPT.village_code == village_code)
            else:
              return jsonify({'message': 'Unauthorized'}), 401
            
        total = query.count()
        
        dpts = query.limit(limit).offset(offset).all()
        dpts = [dpt.to_dict() for dpt in dpts]
        
        return pagination_response(dpts, total, limit, page)
    except Exception as e:
        current_app.logger.error(f"Error getting dpt: {str(e)}")
        return jsonify({'message': 'Error getting dpt'}), 500