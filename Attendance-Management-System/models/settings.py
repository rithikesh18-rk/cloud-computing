from . import db
from datetime import datetime

class CollegeSettings(db.Model):
    __tablename__ = 'college_settings'

    id = db.Column(db.Integer, primary_key=True)
    college_name = db.Column(db.String(255), nullable=False, default='Prathyusha Engineering College')
    college_logo = db.Column(db.String(255), default='default_logo.png')
    address = db.Column(db.Text, default='Tiruvallur, Tamil Nadu, India')
    contact_number = db.Column(db.String(50), default='+1 (555) 019-2834')
    email_address = db.Column(db.String(100), default='info@apextech.edu')
    principal_name = db.Column(db.String(100), default='Dr. Robert Harrison')
    academic_year = db.Column(db.String(20), default='2025-2026')
    semester = db.Column(db.String(20), default='Semester 1')
    working_days = db.Column(db.Integer, default=180)
    holidays_list = db.Column(db.Text, default='Sunday, National Holidays, Festive Breaks')
    min_attendance_percentage = db.Column(db.Float, default=75.0)
    theme = db.Column(db.String(20), default='light') # 'light', 'dark'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_settings(cls):
        settings = cls.query.get(1)
        if not settings:
            settings = cls(
                id=1,
                college_name='Prathyusha Engineering College',
                college_logo='default_logo.png',
                address='Tiruvallur, Tamil Nadu, India',
                contact_number='+1 (555) 019-2834',
                email_address='info@apextech.edu',
                principal_name='Dr. Robert Harrison',
                academic_year='2025-2026',
                semester='Semester 1',
                working_days=180,
                holidays_list='Sunday, National Holidays, Festive Breaks',
                min_attendance_percentage=75.0,
                theme='light'
            )
            db.session.add(settings)
            db.session.commit()
        return settings
