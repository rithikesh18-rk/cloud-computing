from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_id_code = db.Column(db.String(50), unique=True, nullable=False) # e.g. STU2026001, FAC001, ADMIN001
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'faculty', 'student'
    # Profile & contact attributes
    profile_image = db.Column(db.String(255), default='default_avatar.png')
    phone_number = db.Column(db.String(20), nullable=True)

    # Student-specific attributes
    roll_number = db.Column(db.String(50), nullable=True)
    register_number = db.Column(db.String(50), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    year = db.Column(db.String(10), nullable=True)     # '1st Year', '2nd Year', '3rd Year', '4th Year'
    section = db.Column(db.String(10), nullable=True)  # 'A', 'B', 'C'

    # Faculty-specific attributes
    designation = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def generate_student_id(cls):
        year = datetime.utcnow().year
        last_student = cls.query.filter(cls.role == 'student').order_by(cls.id.desc()).first()
        next_num = 1
        if last_student and last_student.user_id_code.startswith(f"STU{year}"):
            try:
                next_num = int(last_student.user_id_code[7:]) + 1
            except ValueError:
                next_num = last_student.id + 1
        elif last_student:
            next_num = last_student.id + 1
        return f"STU{year}{next_num:04d}"

    @classmethod
    def generate_faculty_id(cls):
        last_faculty = cls.query.filter(cls.role == 'faculty').order_by(cls.id.desc()).first()
        next_num = (last_faculty.id + 1) if last_faculty else 1
        return f"FAC{next_num:03d}"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id_code': self.user_id_code,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'profile_image': self.profile_image or 'default_avatar.png',
            'phone_number': self.phone_number or '',
            'roll_number': self.roll_number or '',
            'register_number': self.register_number or '',
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else 'N/A',
            'department_code': self.department.code if self.department else '',
            'year': self.year or '',
            'section': self.section or '',
            'designation': self.designation or '',
            'created_at': self.created_at.strftime('%Y-%m-%d') if self.created_at else ''
        }
