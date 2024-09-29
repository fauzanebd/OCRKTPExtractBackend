from app import db

class Province(db.Model):
    __tablename__ = 'provinces'
    code = db.Column(db.String(2), primary_key=True, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name
        }

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    province_code = db.Column(db.String(2), db.ForeignKey('provinces.code'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(5), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'province_code': self.province_code,
            'name': self.name,
            'code': self.code
        }

class Subdistrict(db.Model):
    __tablename__ = 'subdistricts'
    id = db.Column(db.Integer, primary_key=True)
    city_code = db.Column(db.String(5), db.ForeignKey('cities.code'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(8), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'city_code': self.city_code,
            'name': self.name,
            'code': self.code
        }

class Ward(db.Model):
    __tablename__ = 'wards'
    id = db.Column(db.Integer, primary_key=True)
    subdistrict_code = db.Column(db.String(8), db.ForeignKey('subdistricts.code'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(13), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subdistrict_code': self.subdistrict_code,
            'name': self.name,
            'code': self.code
        }

class Village(db.Model):
    __tablename__ = 'villages'
    id = db.Column(db.Integer, primary_key=True)
    ward_code = db.Column(db.String(10), db.ForeignKey('wards.code'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'ward_code': self.ward_code,
            'name': self.name,
            'code': self.code
        }