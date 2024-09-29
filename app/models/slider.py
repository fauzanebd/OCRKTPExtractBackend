from app import db

class Slider(db.Model):
    __tablename__ = 'sliders'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    order = db.Column(db.Integer, nullable=False)