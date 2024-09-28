from app import db
from cryptography.fernet import Fernet

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')
    fernet_key = db.Column(db.String(255), nullable=True)

    def generate_fernet_key(self):
        key = Fernet.generate_key()
        self.fernet_key = key.decode()  # Store as string in database
        return key

    def get_fernet_key(self):
        if self.fernet_key:
            return self.fernet_key.encode()  # Return as bytes
        return None