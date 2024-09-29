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