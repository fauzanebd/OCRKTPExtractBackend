import os
from datetime import datetime
from app import db
from app.utils.helpers import decrypt
from app.models.locations import Province, City, Subdistrict, Ward, Village 

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
    village_code = db.Column(db.String(100), nullable=True)
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
    dpt_id = db.Column(db.Integer, db.ForeignKey('dpts.id'), nullable=True)
    
    def to_dict(self):
        province = Province.query.filter_by(code=self.province_code).first()
        city = City.query.filter_by(code=self.city_code).first()
        subdistrict = Subdistrict.query.filter_by(code=self.subdistrict_code).first()
        ward = None
        if self.ward_code:
            ward = Ward.query.filter_by(code=self.ward_code).first()
        
        enc_key = os.getenv('ENCRYPTION_KEY').encode('utf-8')
    
        return {
            'id': self.id,
            'client_code': self.client_code,
            'user_id': self.user_id,
            'model_id': self.model_id,
            'province_code': self.province_code,
            'province_name': province.name if province else '',
            'city_code': self.city_code,
            'city_name': city.name if city else '',
            'subdistrict_code': self.subdistrict_code,
            'subdistrict_name': subdistrict.name if subdistrict else '',
            'ward_code': self.ward_code,
            'ward_name': ward.name if ward else '',
            'village_code': self.village_code,
            's3_file': self.s3_file,
            'nik': decrypt(self.nik, enc_key),
            'name': self.name,
            'birth_date': self.birth_date.strftime('%d-%m-%Y') if self.birth_date else None,
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
            'updated_at': self.updated_at,
            'dpt_id': self.dpt_id
        }