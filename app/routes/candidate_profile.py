from flask import Blueprint, request, jsonify
from app.models.candidate_profile import CandidateProfile
from app import db
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.routes.auth import token_required
from app.utils.helpers import success_response

bp = Blueprint('candidate_profile', __name__)

@bp.route('/candidate_profile', methods=['GET'])
@token_required
def candidate_profile(current_user):
    try:
        client_code = request.args.get('client_code')
        candidate_profile = CandidateProfile.query.filter_by(client_code=client_code).first()
        if not candidate_profile:
            return jsonify({'message': 'Candidate Profile not found'}), 404
        
        return success_response('Success', candidate_profile.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error getting candidate profile: {str(e)}")
        return jsonify({'message': 'Error getting candidate profile'}), 500