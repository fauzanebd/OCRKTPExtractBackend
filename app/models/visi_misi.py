from app import db

class VisiMisi(db.Model):
    __tablename__ = 'visi_misi'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_code': self.client_code,
            'image': self.image,
            'text': self.text
        }