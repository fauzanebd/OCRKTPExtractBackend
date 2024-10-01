from app import db
from app.services.s3_service import S3Service

class VisiMisi(db.Model):
    __tablename__ = 'visi_misi'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        image_url = S3Service().get_presigned_url(self.image)
        return {
            'id': self.id,
            'client_code': self.client_code,
            'image': image_url,
            'text': self.text
        }