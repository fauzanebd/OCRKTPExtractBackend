import datetime

from app import db

class ExtractedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(16), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    prov_kab = db.Column(db.String(100), nullable=False)
    rt_rw = db.Column(db.String(10), nullable=False)
    tempat_lahir = db.Column(db.String(50), nullable=False)
    tgl_lahir = db.Column(db.Date, nullable=False)
    pekerjaan = db.Column(db.String(50), nullable=False)
    s3_filename = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    reported_by = db.Column(db.String(80), nullable=False)
    reported_at = db.Column(db.DateTime, default=datetime.datetime.now())