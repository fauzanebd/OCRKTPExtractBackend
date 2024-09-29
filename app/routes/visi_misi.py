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
from app.utils.helpers import success_response

bp = Blueprint('visi_misi', __name__)

@bp.route('/visi-misi', methods=['GET'])
@token_required
def visi_misi(current_user):
    try:
        client_code = os.getenv('CLIENT_CODE')
        visi_misi = VisiMisi.query.filter_by(client_code=client_code).first()
        if not visi_misi:
            return jsonify({'message': 'Visi Misi not found'}), 404
        
        return success_response(visi_misi.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error getting visi misi: {str(e)}")
        return jsonify({'message': 'Error getting visi misi'}), 500