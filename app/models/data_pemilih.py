import os

from app import db
from app.utils.helpers import generate_random_string, encrypt_text, decrypt_text, pagination_response

class DataPemilih(db.Model):
    __tablename__ = 'data_pemilih'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    province_code = db.Column(db.String(2), db.ForeignKey('provinces.code'), nullable=False)
    city_code = db.Column(db.String(5), db.ForeignKey('cities.code'), nullable=False)
    subdistrict_code = db.Column(db.String(8), db.ForeignKey('subdistricts.code'), nullable=False)
    ward_code = db.Column(db.String(13), db.ForeignKey('wards.code'), nullable=True)
    village_code = db.Column(db.String(20), db.ForeignKey('villages.code'), nullable=True)
    s3_file = db.Column(db.String(255), nullable=False)
    nik = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    address = db.Column(db.Text, nullable=True)
    no_phone = db.Column(db.String(20))
    no_tps = db.Column(db.String(20))
    is_party_member = db.Column(db.Boolean, default=False)
    relation_to_candidate = db.Column(db.String(50))
    confirmation_status = db.Column(db.String(20))
    category = db.Column(db.String(20))
    positioning_to_candidate = db.Column(db.String(50))
    expectation_to_candidate = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    
    def to_dict(self):
        fernet_key = os.getenv('FERNET_KEY')
        return {
            'id': self.id,
            'client_code': self.client_code,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'province_code': self.province_code,
            'city_code': self.city_code,
            'subdistrict_code': self.subdistrict_code,
            'ward_code': self.ward_code,
            'village_code': self.village_code,
            's3_file': self.s3_file,
            'nik': decrypt_text(self.nik, fernet_key),
            'name': self.name,
            'birth_date': self.birth_date,
            'gender': self.gender,
            'address': self.address,
            'no_phone': self.no_phone,
            'no_tps': self.no_tps,
            'is_party_member': self.is_party_member,
            'relation_to_candidate': self.relation_to_candidate,
            'confirmation_status': self.confirmation_status,
            'category': self.category,
            'positioning_to_candidate': self.positioning_to_candidate,
            'expectation_to_candidate': self.expectation_to_candidate,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }