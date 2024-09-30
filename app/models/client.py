from app import db

class Client(db.Model):
  __tablename__ = 'clients'
  id = db.Column(db.Integer, primary_key=True)
  client_code = db.Column(db.String(255), nullable=False, unique=True)
  name = db.Column(db.String(100), nullable=False)
  