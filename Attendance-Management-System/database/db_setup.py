import os
from sqlalchemy import create_engine
from models import db
from models.settings import CollegeSettings
from models.user import User
from models.department import Department
from models.subject import Subject
from models.attendance import Attendance, AttendanceRecord
from datetime import datetime, timedelta

def verify_and_configure_database(app):
    """
    Checks if primary MySQL database connection is accessible.
    If MySQL server is unavailable or invalid credentials, falls back to SQLite smoothly.
    """
    primary_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    try:
        # Quick connection test
        test_engine = create_engine(primary_uri, connect_args={'connect_timeout': 3})
        conn = test_engine.connect()
        conn.close()
        test_engine.dispose()
        print("Connected successfully to Primary MySQL Database.")
    except Exception as e:
        print(f"Primary MySQL connection not available: {e}")
        print("Using local SQLite database fallback (database/attendance.db)...")
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLITE_DATABASE_URI']

def init_db(app):
    """Create all schema tables and seed default data."""
    with app.app_context():
        db.create_all()
        seed_initial_data()

def seed_initial_data():
    """Seed default settings, admin user, departments, subjects, faculty and students if empty."""
    # 1. College Settings
    CollegeSettings.get_settings()

    # 2. Default Admin User
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            user_id_code='ADMIN001',
            full_name='System Administrator',
            email='admin@college.com',
            role='admin',
            phone_number='+1 (555) 010-9999'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Default admin created: admin@college.com / admin123")

    # 3. Seed Sample Departments if none exist
    if Department.query.count() == 0:
        cs_dept = Department(code='CSE', name='Computer Science & Engineering')
        ec_dept = Department(code='ECE', name='Electronics & Communication')
        me_dept = Department(code='MECH', name='Mechanical Engineering')
        db.session.add_all([cs_dept, ec_dept, me_dept])
        db.session.commit()

        # Seed Sample Subjects
        s1 = Subject(code='CS101', name='Data Structures & Algorithms', department_id=cs_dept.id, year='1st Year', semester='Semester 1')
        s2 = Subject(code='CS201', name='Database Management Systems', department_id=cs_dept.id, year='2nd Year', semester='Semester 3')
        s3 = Subject(code='EC101', name='Digital Electronics', department_id=ec_dept.id, year='1st Year', semester='Semester 1')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

        # Seed Sample Faculty
        fac1 = User(
            user_id_code='FAC001',
            full_name='Dr. Alan Turing',
            email='faculty@college.com',
            role='faculty',
            phone_number='+1 (555) 321-4567',
            designation='Senior Professor',
            department_id=cs_dept.id
        )
        fac1.set_password('faculty123')
        db.session.add(fac1)

        # Seed Sample Students
        st1 = User(
            user_id_code='STU20260001',
            full_name='John Doe',
            email='student@college.com',
            role='student',
            phone_number='+1 (555) 888-1111',
            roll_number='2026-CS-001',
            department_id=cs_dept.id,
            year='2nd Year',
            section='A'
        )
        st1.set_password('student123')

        st2 = User(
            user_id_code='STU20260002',
            full_name='Jane Smith',
            email='janesmith@college.com',
            role='student',
            phone_number='+1 (555) 888-2222',
            roll_number='2026-CS-002',
            department_id=cs_dept.id,
            year='2nd Year',
            section='A'
        )
        st2.set_password('student123')

        st3 = User(
            user_id_code='STU20260003',
            full_name='Michael Brown',
            email='michael@college.com',
            role='student',
            phone_number='+1 (555) 888-3333',
            roll_number='2026-CS-003',
            department_id=cs_dept.id,
            year='2nd Year',
            section='A'
        )
        st3.set_password('student123')

        db.session.add_all([st1, st2, st3])
        db.session.commit()

        # Seed sample attendance session
        today = datetime.utcnow().date()
        att = Attendance(
            department_id=cs_dept.id,
            subject_id=s2.id,
            year='2nd Year',
            section='A',
            attendance_date=today,
            marked_by_id=fac1.id
        )
        db.session.add(att)
        db.session.commit()

        rec1 = AttendanceRecord(attendance_id=att.id, student_id=st1.id, status='Present')
        rec2 = AttendanceRecord(attendance_id=att.id, student_id=st2.id, status='Present')
        rec3 = AttendanceRecord(attendance_id=att.id, student_id=st3.id, status='Absent', remarks='Medical Leave')
        db.session.add_all([rec1, rec2, rec3])

        # Yesterday attendance session
        yesterday = today - timedelta(days=1)
        att_prev = Attendance(
            department_id=cs_dept.id,
            subject_id=s2.id,
            year='2nd Year',
            section='A',
            attendance_date=yesterday,
            marked_by_id=fac1.id
        )
        db.session.add(att_prev)
        db.session.commit()

        r1 = AttendanceRecord(attendance_id=att_prev.id, student_id=st1.id, status='Present')
        r2 = AttendanceRecord(attendance_id=att_prev.id, student_id=st2.id, status='Absent')
        r3 = AttendanceRecord(attendance_id=att_prev.id, student_id=st3.id, status='Present')
        db.session.add_all([r1, r2, r3])

        db.session.commit()
        print("Database seeded with sample departments, subjects, faculty, students, and attendance records.")
    else:
        db.session.commit()
