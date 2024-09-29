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
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=True)
    regency_id = db.Column(db.Integer, db.ForeignKey('regencies.id'), nullable=True)
    subdistrict_id = db.Column(db.Integer, db.ForeignKey('subdistricts.id'), nullable=True)
    urban_village_id = db.Column(db.Integer, db.ForeignKey('urban_villages.id'), nullable=True)
    village_id = db.Column(db.Integer, db.ForeignKey('villages.id'), nullable=True)
    is_enumerator = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())
    # fernet_key = db.Column(db.LargeBinary, nullable=True) 

    # def generate_fernet_key(self):
    #     key = Fernet.generate_key()
    #     self.fernet_key = key
    #     return key

    # def get_fernet_key(self):
    #     return self.fernet_ke