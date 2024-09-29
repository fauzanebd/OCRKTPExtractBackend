from app import db

class Province(db.Model):
    __tablename__ = 'provinces'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Regency(db.Model):
    __tablename__ = 'regencies'
    id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey('provinces.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Subdistrict(db.Model):
    __tablename__ = 'subdistricts'
    id = db.Column(db.Integer, primary_key=True)
    regency_id = db.Column(db.Integer, db.ForeignKey('regencies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class UrbanVillage(db.Model):
    __tablename__ = 'urban_villages'
    id = db.Column(db.Integer, primary_key=True)
    subdistrict_id = db.Column(db.Integer, db.ForeignKey('subdistricts.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class Village(db.Model):
    __tablename__ = 'villages'
    id = db.Column(db.Integer, primary_key=True)
    urban_village_id = db.Column(db.Integer, db.ForeignKey('urban_villages.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)