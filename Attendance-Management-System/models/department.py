from . import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    students = db.relationship('User', backref='department', lazy=True, foreign_keys='User.department_id')
    subjects = db.relationship('Subject', backref='department', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'student_count': len(self.students) if self.students else 0,
            'subject_count': len(self.subjects) if self.subjects else 0
        }
