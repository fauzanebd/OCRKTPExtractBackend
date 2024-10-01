from app import db

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'
    id = db.Column(db.Integer, primary_key=True)
    client_code = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_code': self.client_code,
            'text': self.text
        }
    