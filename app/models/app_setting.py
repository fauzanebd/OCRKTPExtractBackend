from app import db

class AppSetting(db.Model):
    __tablename__ = 'app_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    client_code = db.Column(db.String(255), db.ForeignKey('clients.client_code'), nullable=False)
    value = db.Column(db.Text, nullable=False)



