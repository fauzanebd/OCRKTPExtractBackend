from app import db
from cryptography.fernet import Fernet   
from app.models.locations import Province, City, Subdistrict, Ward, Village 
from app.models.client import Client

from app import db
from enum import Enum

class Hierarchy(Enum):
    ADMIN = 99
    NASIONAL = 6
    PROVINCE = 5
    CITY = 4
    SUBDISTRICT = 3
    WARD = 2
    VILLAGE = 1
    TPS = 0
    ENUMERATOR = -1

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255))
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    no_phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)
    nasional = db.Column(db.Boolean, default=False)
    province_code = db.Column(db.String(2), db.ForeignKey('provinces.code'), nullable=True)
    city_code = db.Column(db.String(5), db.ForeignKey('cities.code'), nullable=True)
    subdistrict_code = db.Column(db.String(8), db.ForeignKey('subdistricts.code'), nullable=True)
    ward_code = db.Column(db.String(13), db.ForeignKey('wards.code'), nullable=True)
    village_code = db.Column(db.String(20), db.ForeignKey('villages.code'), nullable=True)
    is_enumerator = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    tps_no = db.Column(db.Integer, nullable=True)
    
    def public_fields(self, locations=None):
        province = Province.query.filter_by(code=self.province_code).first()
        city = City.query.filter_by(code=self.city_code).first()
        subdistrict = Subdistrict.query.filter_by(code=self.subdistrict_code).first()
        ward = Ward.query.filter_by(code=self.ward_code).first()
        client = Client.query.filter_by(code=self.client_code).first()
        
        return {
            'id': self.id,
            'client_code': self.client_code,
            'client_name': client.name if client else '',
            'avatar': self.avatar,
            'name': self.name,
            'username': self.username,
            'no_phone': self.no_phone,
            'nasional': self.nasional,
            'province_code': self.province_code,
            'province_name': province.name if province else '',
            'city_code': self.city_code,
            'city_name': city.name if city else '',
            'subdistrict_code': self.subdistrict_code,
            'subdistrict_name': subdistrict.name if subdistrict else '',
            'ward_code': self.ward_code,
            'ward_name': ward.name if ward else '',
            'village_code': self.village_code,
            'is_enumerator': self.is_enumerator,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'hierarchy_value': self.get_hierarchy_value().value,
            'hierarchy': self.get_user_hierarchy(),
            'locations': locations,
            'tps_no': self.tps_no
        }
    
    def get_user_hierarchy(self):
        if self.province_code:
            return 'province'
        elif self.city_code:
            return 'city'
        elif self.subdistrict_code:
            return 'subdistrict'
        elif self.ward_code:
            return 'ward'
        elif self.village_code:
            return 'village'
        else:
            return 'nasional'
    
    def get_user_locations(self):
        return {
            'province_code': self.province_code,
            'city_code': self.city_code,
            'subdistrict_code': self.subdistrict_code,
            'ward_code': self.ward_code,
            'village_code': self.village_code
        }
        
    def to_dict(self):
        province = Province.query.filter_by(code=self.province_code).first()
        city = City.query.filter_by(code=self.city_code).first()
        subdistrict = Subdistrict.query.filter_by(code=self.subdistrict_code).first()
        ward = Ward.query.filter_by(code=self.ward_code).first()
        client = Client.query.filter_by(code=self.client_code).first()
        
        return {
            'id': self.id,
            'client_code': self.client_code,
            'client_name': client.name if client else '',
            'avatar': self.avatar,
            'name': self.name,
            'username': self.username,
            'no_phone': self.no_phone,
            'nasional': self.nasional,
            'province_code': self.province_code,
            'province_name': province.name if province else '',
            'city_code': self.city_code,
            'city_name': city.name if city else '',
            'subdistrict_code': self.subdistrict_code,
            'subdistrict_name': subdistrict.name if subdistrict else '',
            'ward_code': self.ward_code,
            'ward_name': ward.name if ward else '',
            'village_code': self.village_code,
            'is_enumerator': self.is_enumerator,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tps_no': self.tps_no
        }
        
    def get_hierarchy_value(self):
        if self.is_enumerator:
            return Hierarchy.ENUMERATOR
        
        if self.role == 'admin':
            return Hierarchy.ADMIN
        
        if self.province_code is None:
            return Hierarchy.NASIONAL
        elif self.city_code is None:
            return Hierarchy.PROVINCE
        elif self.subdistrict_code is None:
            return Hierarchy.CITY
        elif self.ward_code is None:
            return Hierarchy.SUBDISTRICT
        elif self.tps_no is None:
            return Hierarchy.WARD
        else:
            return Hierarchy.TPS