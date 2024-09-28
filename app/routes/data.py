
import logging
from flask import Blueprint, request, jsonify
from app.models.extracted_data import ExtractedData
from app import db
import jwt
from app.services import ocr_service, s3_service
from app.utils.helpers import generate_random_string, encrypt_text, decrypt_text
from app.routes.auth import token_required
from datetime import datetime, timedelta
from functools import wraps

bp = Blueprint('data', __name__)


@bp.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": True, "message": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": True, "message": "No selected file"}), 400
    
    # try:
    file_data = file.read()
    
    # Extract data using OCR
    extracted_data = ocr_service.ocr_service.extract_ktp_data(file_data)
    
    # Generate a unique filename
    random_string = generate_random_string(12)
    s3_filename = f"ktp_nik_{extracted_data.get('nik', 'unknown')}_{random_string}.jpg"
    
    # Upload to S3
    if s3_service.s3_service.upload_file(file_data, s3_filename):
        extracted_data['s3_filename'] = s3_filename
        return jsonify({
            "error": False,
            "message": "OCR Success!",
            "data": extracted_data
        }), 200
    else:
        return jsonify({"error": True, "message": "Failed to upload file to S3"}), 500
    
    # except Exception as e:
    #     return jsonify({"error": True, "message": str(e)}), 500

@bp.route('/save_data', methods=['POST'])
@token_required
def save_data(current_user):
    data = request.get_json()

    encrypted_nik = encrypt_text(data['nik'], current_user.get_fernet_key())
    logging.debug(f"Stored encrypted NIK (first 10 chars): {encrypted_nik[:10]}...")
    
    # try:
    ktp_data = ExtractedData(
        nik=encrypted_nik,
        nama=data['nama'],
        alamat=data['alamat'],
        prov_kab=data['prov_kab'],
        rt_rw=data['rt_rw'],
        tempat_lahir=data['tempat_lahir'],
        tgl_lahir=datetime.strptime(data['tgl_lahir'], '%Y-%m-%d').date(),
        pekerjaan=data['pekerjaan'],
        s3_filename=data['s3_filename'],
        phone_number=data.get('phone_number', ''),
        reported_by=current_user.username
    )

    db.session.add(ktp_data)
    db.session.commit()

    return jsonify({"message": "Data saved successfully", "id": ktp_data.id}), 200
    # except Exception as e:
    #     db.session.rollback()
    #     return jsonify({"error": True, "message": str(e)}), 500
    

@bp.route('/entries', methods=['GET'])
@token_required
def check_entries(current_user):
    # try:
    entries = ExtractedData.query.filter_by(reported_by=current_user.username).all()
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
    # except Exception as e:
    #     return jsonify({"error": True, "message": str(e)}), 500
    
@bp.route('/update_data', methods=['POST'])
@token_required
def update_data(current_user):
    data = request.get_json()
    
    try:
        doc_id = data.pop('id', None)
        
        if not doc_id:
            return jsonify({"error": True, "message": "No id provided"}), 400

        entry = ExtractedData.query.filter_by(id=doc_id, reported_by=current_user.username).first()

        if not entry:
            return jsonify({"error": True, "message": "No matching document found"}), 404

        for key, value in data.items():
            setattr(entry, key, value)

        db.session.commit()
        return jsonify({"message": "Data updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": True, "message": str(e)}), 500
