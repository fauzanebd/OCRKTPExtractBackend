
import logging
from flask import Blueprint, request, jsonify
from app.models.data_pemilih import DataPemilih
from app import db
import os
from datetime import datetime
from app.services import ocr_service, s3_service
from app.utils.helpers import generate_random_string, encrypt_text, decrypt_text, pagination_response
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
        
        # Extract data using OCR
        data_pemilih = ocr_service.ocr_service.extract_ktp_data(file_data, current_user.id)
        
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

@bp.route('/data-pemilih/save_data', methods=['POST'])
@token_required
def save_data(current_user):
    data = request.get_json()

    fernet_key = os.getenv('FERNET_KEY')
    encrypted_nik = encrypt_text(data['nik'], fernet_key)
    logging.debug(f"Stored encrypted NIK (first 10 chars): {encrypted_nik[:10]}...")
    
    try:
        client_code = os.getenv('CLIENT_CODE')
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
            name=data.get('name', ''),
            birth_date=data.get('birth_date', datetime.now().strftime('%Y-%m-%d')),
            gender=data.get('gender', 'L'),
            address=data.get('address', 'asdasd'),
            no_phone=data.get('no_phone', ''),
            no_tps=data.get('no_tps', ''),
            is_party_member=data.get('is_party_member', False),
            relation_to_candidate=data.get('relation_to_candidate', ''),
            confirmation_status=data.get('confirmation_status', ''),
            category=data.get('category', ''),
            positioning_to_candidate=data.get('positioning_to_candidate', ''),
            expectation_to_candidate=data.get('expectation_to_candidate', '')
        )

        db.session.add(ktp_data)
        db.session.commit()

        return jsonify({"message": "Data saved successfully", "id": ktp_data.id}), 200
    except Exception as e:
        db.session.rollback()
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
            
        if current_user.role == 'enumerator' or hierarchy == 1:
            query = query.filter(DataPemilih.user_id == current_user.id)
        
        total = query.count()
            
        entries = query.limit(limit).offset(offset).all()
        entry_list = [entry.to_dict() for entry in entries]
        
        return pagination_response(entry_list, total, limit, page)
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    
@bp.route('/data-pemilih/update_data', methods=['POST'])
@token_required
def update_data(current_user):
    data = request.get_json()
    
    try:
        doc_id = data.pop('id', None)
        
        if not doc_id:
            return jsonify({"error": True, "message": "No id provided"}), 400

        entry = DataPemilih.query.filter_by(id=doc_id, reported_by=current_user.username).first()

        if not entry:
            return jsonify({"error": True, "message": "No matching document found"}), 404

        for key, value in data.items():
            setattr(entry, key, value)

        db.session.commit()
        return jsonify({"message": "Data updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
