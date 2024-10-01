
import logging
from flask import Blueprint, request, jsonify
from app.models.data_pemilih import DataPemilih
from app.models.dpt import DPT
from app import db
import os
from datetime import datetime
from app.services import ocr_service, s3_service
from app.utils.helpers import generate_random_string, encrypt_text, decrypt_text, pagination_response, success_response, encrypt
from app.routes.auth import token_required
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('data', __name__)


@bp.route('/data-pemilih/upload', methods=['POST'])
@token_required
def upload_image(current_user):
    if 'image' not in request.files:
        return jsonify({"error": True, "message": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": True, "message": "No selected file"}), 400
    
    try:
        file_data = file.read()
        filename = file.filename
        # get client_code from query string
        client_code = request.args.get('client_code')
        
        # Extract data using OCR
        data_pemilih = ocr_service.ocr_service.extract_ktp_data(file_data, filename, current_user.id, client_code)
        
        # Generate a unique filename
        random_string = generate_random_string(24)
        s3_filename = f"{random_string}.png"
        
        # Upload to S3
        if s3_service.s3_service.upload_file(file_data, s3_filename):
            data_pemilih['s3_file'] = s3_filename
            return jsonify({
                "error": False,
                "message": "OCR Success!",
                "data": data_pemilih
            }), 200
        else:
            return jsonify({"error": True, "message": "Failed to upload file to S3"}), 500
    
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

@bp.route('/data-pemilih/check_dpt', methods=['POST'])
@token_required
def check_dpt(current_user):
    data = request.get_json()
    
    try:
        ward_code = data.get('ward_code', None)
        name = data.get('name', '').upper()
        gender = data.get('gender')
        
        dpts = []
        if ward_code is not None:
            dpts = DPT.query.filter_by(ward_code=ward_code, name=name, gender=gender).all()
        
        return jsonify({
            "message": "Success", 
            "potential_dpt": [dpt.to_dict() for dpt in dpts],
            "is_valid_dpt": len(dpts) == 1
        }), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 5001

@bp.route('/data-pemilih/save_data', methods=['POST'])
@token_required
def save_data(current_user):
    data = request.get_json()

    enc_key = os.getenv('ENCRYPTION_KEY').encode('utf-8')
    encrypted_nik = encrypt(data['nik'], enc_key)
    logging.debug(f"Stored encrypted NIK (first 10 chars): {encrypted_nik[:10]}...")
    
    if 'birth_date' in data and data['birth_date']:
        birth_date = datetime.strptime(data['birth_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
    else:
        birth_date = None
        
    ward_code = data.get('ward_code', None)
    name = data.get('name', '').upper()
    dpts = []
    if ward_code is not None:
        dpts = DataPemilih.query.filter_by(ward_code=ward_code, name=name).all()
    
    try:
        client_code = request.args.get('client_code')
        ktp_data = DataPemilih(
            client_code=client_code,
            user_id=current_user.id,
            model_id=data.get('model_id', 1),
            province_code=data.get('province_code', current_user.province_code),
            city_code=data.get('city_code', current_user.city_code),
            subdistrict_code=data.get('subdistrict_code', current_user.subdistrict_code),
            ward_code=data.get('ward_code', current_user.ward_code),
            village_code=data.get('village_code', None),
            s3_file=data.get('s3_file', ''),
            nik=encrypted_nik,
            name=name,
            birth_date=birth_date,
            gender=data.get('gender', 'L'),
            address=data.get('address', 'asdasd'),
            no_phone=data.get('no_phone', ''),
            no_tps=data.get('no_tps', ''),
            is_party_member=data.get('is_party_member', False),
            relation_to_candidate=data.get('relation_to_candidate', ''),
            confirmation_status=data.get('confirmation_status', ''),
            category=data.get('category', ''),
            positioning_to_candidate=data.get('positioning_to_candidate', ''),
            expectation_to_candidate=data.get('expectation_to_candidate', ''),
            dpt_id=data.get('dpt_id', None)
        )

        db.session.add(ktp_data)
        db.session.commit()

        return jsonify({
            "message": "Data saved successfully", 
            "id": ktp_data.id,
            "potential_dpt": [dpt.to_dict() for dpt in dpts],
            "is_valid_dpt": len(dpts) == 0
        }), 200
    except Exception as e:
        db.session.rollback()
        # handle unique constraint violation
        if 'unique constraint' in str(e):
            return jsonify({"error": True, "message": "NIK already exists"}), 400
        return jsonify({"error": True, "message": str(e)}), 500
    

@bp.route('/data-pemilih', methods=['GET'])
@token_required
def get_data_pemilih(current_user):
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
        query = DataPemilih.query
        
        if q:
            query = query.filter(DataPemilih.name.ilike(f"%{q}%"))
        if province_code:
            if hierarchy > 6 and current_user.province_code != province_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(DataPemilih.province_code == province_code)
        if city_code:
            if hierarchy > 5 and current_user.city_code != city_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(DataPemilih.city_code == city_code)
        if subdistrict_code:
            if hierarchy > 4 and current_user.subdistrict_code != subdistrict_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(DataPemilih.subdistrict_code == subdistrict_code)
        if ward_code:
            if hierarchy > 3 and current_user.ward_code != ward_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(DataPemilih.ward_code == ward_code)
        if village_code:
            if hierarchy > 2 and current_user.village_code != village_code:
                return jsonify({'message': 'Unauthorized'}), 401
            query = query.filter(DataPemilih.village_code == village_code)
            
        if current_user.is_enumerator or hierarchy == 1:
            query = query.filter(DataPemilih.user_id == current_user.id)
        
        total = query.count()
            
        entries = query.order_by(DataPemilih.created_at.desc()).limit(limit).offset(offset).all()
        entry_list = [entry.to_dict() for entry in entries]
        
        return pagination_response(entry_list, total, limit, page)
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    
@bp.route('/data-pemilih/<int:id>', methods=['DELETE'])
@token_required
def delete_data(current_user, id):
    try:
        data_pemilih = DataPemilih.query.get(id)
        if not data_pemilih:
            return jsonify({"error": True, "message": "Data not found"}), 404
        
        db.session.delete(data_pemilih)
        db.session.commit()
        
        return jsonify({"message": "Data deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
    
@bp.route('/data-pemilih/update_data', methods=['POST'])
@token_required
def update_data(current_user):
    data = request.get_json()
    
    try:
        data_pemilih = DataPemilih.query.get(data['id'])
        if not data_pemilih:
            return jsonify({"error": True, "message": "Data not found"}), 404
        
        encrypted_nik = data_pemilih.nik
        if data.get('nik'):
            enc_key = os.getenv('ENCRYPTION_KEY').encode('utf-8')
            encrypted_nik = encrypt(data['nik'], enc_key)
            
        if 'birth_date' in data and data['birth_date']:
            birth_date = datetime.strptime(data['birth_date'], '%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            birth_date = None
        
        data_pemilih.name = data.get('name', data_pemilih.name)
        data_pemilih.birth_date = birth_date
        data_pemilih.province_code = data.get('province_code', data_pemilih.province_code)
        data_pemilih.city_code = data.get('city_code', data_pemilih.city_code)
        data_pemilih.subdistrict_code = data.get('subdistrict_code', data_pemilih.subdistrict_code)
        data_pemilih.ward_code = data.get('ward_code', data_pemilih.ward_code)
        data_pemilih.village_code = data.get('village_code', data_pemilih.village_code)
        data_pemilih.nik = encrypted_nik
        data_pemilih.gender = data.get('gender', data_pemilih.gender)
        data_pemilih.address = data.get('address', data_pemilih.address)
        data_pemilih.no_phone = data.get('no_phone', data_pemilih.no_phone)
        data_pemilih.no_tps = data.get('no_tps', data_pemilih.no_tps)
        data_pemilih.is_party_member = data.get('is_party_member', data_pemilih.is_party_member)
        data_pemilih.relation_to_candidate = data.get('relation_to_candidate', data_pemilih.relation_to_candidate)
        data_pemilih.confirmation_status = data.get('confirmation_status', data_pemilih.confirmation_status)
        data_pemilih.category = data.get('category', data_pemilih.category)
        data_pemilih.positioning_to_candidate = data.get('positioning_to_candidate', data_pemilih.positioning_to_candidate)
        data_pemilih.expectation_to_candidate = data.get('expectation_to_candidate', data_pemilih.expectation_to_candidate)
        
        db.session.commit()
        
        return success_response("Data updated successfully", data_pemilih.to_dict())
    
    except Exception as e:
        db.session.rollback()
        # handle unique constraint violation
        if 'unique constraint' in str(e):
            return jsonify({"error": True, "message": "NIK already exists"}), 400
        return jsonify({"error": True, "message": str(e)}), 500
