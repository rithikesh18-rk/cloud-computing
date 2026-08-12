from . import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    marked_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='attendances')
    subject = db.relationship('Subject', backref='attendances')
    marked_by = db.relationship('User', foreign_keys=[marked_by_id])
    records = db.relationship('AttendanceRecord', backref='attendance', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('department_id', 'subject_id', 'year', 'section', 'attendance_date', name='unique_attendance_session'),
    )

    def to_dict(self):
        total_students = len(self.records)
        present_count = sum(1 for r in self.records if r.status == 'Present')
        absent_count = total_students - present_count
        percentage = round((present_count / total_students * 100), 2) if total_students > 0 else 0

        return {
            'id': self.id,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else 'N/A',
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else 'N/A',
            'subject_code': self.subject.code if self.subject else '',
            'year': self.year,
            'section': self.section,
            'attendance_date': self.attendance_date.strftime('%Y-%m-%d'),
            'marked_by': self.marked_by.full_name if self.marked_by else 'System',
            'total_students': total_students,
            'present_count': present_count,
            'absent_count': absent_count,
            'percentage': percentage
        }


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendances.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='Present') # 'Present' or 'Absent'
    remarks = db.Column(db.String(255), nullable=True)

    __table_args__ = (
        db.UniqueConstraint('attendance_id', 'student_id', name='unique_student_attendance_record'),
    )

    @classmethod
    def get_consecutive_absents(cls, student_id):
        records = cls.query.filter_by(student_id=student_id).join(Attendance).order_by(Attendance.attendance_date.desc()).all()
        consecutive = 0
        for r in records:
            if r.status == 'Absent':
                consecutive += 1
            else:
                break
        return consecutive

    def to_dict(self):
        return {
            'id': self.id,
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else '',
            'roll_number': self.student.roll_number if self.student else '',
            'register_number': self.student.register_number if self.student else '',
            'user_id_code': self.student.user_id_code if self.student else '',
            'status': self.status,
            'remarks': self.remarks or ''
        }
