from .. import db
from datetime import datetime

class SSIP(db.Model):
    __tablename__ = 'ssip'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_ssip_student'))
    project_type = db.Column(db.String(50))  # Type of SSIP project
    fund_required = db.Column(db.Float)  # Amount of funding required
    objective = db.Column(db.Text)  # Project objective
    methodology = db.Column(db.Text)  # Project methodology
    expected_outcome = db.Column(db.Text)  # Expected outcomes
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User model
    student = db.relationship('User', backref='ssip_projects')

    def __repr__(self):
        return f'<SSIP {self.title}>'
