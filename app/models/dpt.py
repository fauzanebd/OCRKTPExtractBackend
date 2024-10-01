from datetime import datetime
from app import db
from app.utils.helpers import decrypt
from app.models.locations import Province, City, Subdistrict, Ward, Village 

class DPT(db.Model):
  __tablename__ = 'dpts'
  id = db.Column(db.Integer, primary_key=True)
  province_code = db.Column(db.String(2), db.ForeignKey('provinces.code'), nullable=False)
  city_code = db.Column(db.String(5), db.ForeignKey('cities.code'), nullable=False)
  subdistrict_code = db.Column(db.String(8), db.ForeignKey('subdistricts.code'), nullable=False)
  ward_code = db.Column(db.String(13), db.ForeignKey('wards.code'), nullable=True)
  village_code = db.Column(db.String(255), db.ForeignKey('villages.code'), nullable=True)
  tps_no = db.Column(db.String(20), nullable=True)
  nik = db.Column(db.String(255), unique=True, nullable=True)
  name = db.Column(db.String(100), nullable=False)
  gender = db.Column(db.String(10), nullable=True)
  age = db.Column(db.Integer, nullable=True)
  address = db.Column(db.Text, nullable=True)
  rt = db.Column(db.String(10), nullable=True)
  rw = db.Column(db.String(10), nullable=True)
  
  def to_dict(self):
    province = Province.query.filter_by(code=self.province_code).first()
    city = City.query.filter_by(code=self.city_code).first()
    subdistrict = Subdistrict.query.filter_by(code=self.subdistrict_code).first()
    
    return {
      'id': self.id,
      'province_code': self.province_code,
      'province_name': province.name if province else '',
      'city_code': self.city_code,
      'city_name': city.name if city else '',
      'subdistrict_code': self.subdistrict_code,
      'subdistrict_name': subdistrict.name if subdistrict else '',
      'ward_code': self.ward_code,
      'village_code': self.village_code,
      'nik': self.nik,
      'name': self.name,
      'tps_no': self.tps_no,
      'age': self.age,
      'address': self.address,
      'rt': self.rt,
      'rw': self.rw
    }
  