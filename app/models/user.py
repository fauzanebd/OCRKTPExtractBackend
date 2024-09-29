from app import db
from cryptography.fernet import Fernet    

from app import db

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
    # fernet_key = db.Column(db.LargeBinary, nullable=True) 

    # def generate_fernet_key(self):
    #     key = Fernet.generate_key()
    #     self.fernet_key = key
    #     return key

    # def get_fernet_key(self):
    #     return self.fernet_ke
    
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
        return {
            'id': self.id,
            'client_code': self.client_code,
            'avatar': self.avatar,
            'name': self.name,
            'username': self.username,
            'no_phone': self.no_phone,
            'nasional': self.nasional,
            'province_code': self.province_code,
            'city_code': self.city_code,
            'subdistrict_code': self.subdistrict_code,
            'ward_code': self.ward_code,
            'village_code': self.village_code,
            'is_enumerator': self.is_enumerator,
            'role': self.role,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    def get_hierarchy_value(self):
        if self.province_code is None:
            return 6
        elif self.city_code is None:
            return 5
        elif self.subdistrict_code is None:
            return 4
        elif self.ward_code is None:
            return 3
        elif self.village_code is None:
            return 2
        else:
            return 1