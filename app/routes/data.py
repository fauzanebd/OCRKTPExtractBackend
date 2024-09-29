
import logging
from flask import Blueprint, request, jsonify
from app.models.data_pemilih import DataPemilih
from app import db
import jwt
import os
from datetime import datetime
from app.services import ocr_service, s3_service
from app.utils.helpers import generate_random_string, encrypt_text, decrypt_text
from app.routes.auth import token_required
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('data', __name__)


@bp.route('/upload', methods=['POST'])
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
        random_string = generate_random_string(12)
        s3_filename = f"ktp_nik_{data_pemilih.get('nik', 'unknown')}_{random_string}.jpg"
        
        # Upload to S3
        if s3_service.s3_service.upload_file(file_data, s3_filename):
            data_pemilih['s3_filename'] = s3_filename
            return jsonify({
                "error": False,
                "message": "OCR Success!",
                "data": data_pemilih
            }), 200
        else:
            return jsonify({"error": True, "message": "Failed to upload file to S3"}), 500
    
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

@bp.route('/save_data', methods=['POST'])
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
            province_code=data.get('province_code', None),
            city_code=data.get('city_code', None),
            subdistrict_code=data.get('subdistrict_code', None),
            ward_code=data.get('ward_code', None),
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
    

@bp.route('/entries', methods=['GET'])
@token_required
def check_entries(current_user):
    try:
        entries = DataPemilih.query.filter_by(reported_by=current_user.username).all()
        entries_list = [
            {
                'id': entry.id,
                'nik': decrypt_text(entry.nik, current_user.get_fernet_key()),
                'nama': entry.nama,
                'alamat': entry.alamat,
                'prov_kab': entry.prov_kab,
                'rt_rw': entry.rt_rw,
                'tempat_lahir': entry.tempat_lahir,
                'tgl_lahir': entry.tgl_lahir.isoformat(),
                'pekerjaan': entry.pekerjaan,
                's3_filename': entry.s3_filename,
                'phone_number': entry.phone_number,
                'reported_at': entry.reported_at.isoformat()
            }
            for entry in entries
        ]
        for entry in entries_list:
            logging.debug(f"Retrieved and decrypted NIK: {entry['nik'][:10]}...")
        return jsonify({"entries": entries_list}), 200
    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
    
@bp.route('/update_data', methods=['POST'])
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
