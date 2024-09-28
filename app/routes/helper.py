from flask import Blueprint, jsonify


bp = Blueprint('helper', __name__)


@bp.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({'status': 'ok'}), 200