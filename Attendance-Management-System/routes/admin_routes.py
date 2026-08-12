import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.department import Department
from models.subject import Subject
from models.attendance import Attendance, AttendanceRecord
from models.settings import CollegeSettings
from utils.helpers import admin_required, faculty_or_admin_required, allowed_file, get_current_user
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@faculty_or_admin_required
def dashboard():
    total_students = User.query.filter_by(role='student').count()
    total_faculty = User.query.filter_by(role='faculty').count()
    total_departments = Department.query.count()
    total_subjects = Subject.query.count()

    today = datetime.utcnow().date()
    today_attendance = Attendance.query.filter_by(attendance_date=today).all()

    today_marked_count = len(today_attendance)
    today_present = 0
    today_total_records = 0

    for att in today_attendance:
        today_total_records += len(att.records)
        today_present += sum(1 for r in att.records if r.status == 'Present')

    today_absent = today_total_records - today_present
    today_percentage = round((today_present / today_total_records * 100), 1) if today_total_records > 0 else 0

    recent_sessions = Attendance.query.order_by(Attendance.created_at.desc()).limit(5).all()
    departments = Department.query.all()

    # Department-wise student distribution for charts
    dept_stats = []
    for d in departments:
        dept_stats.append({
            'name': d.code,
            'count': User.query.filter_by(role='student', department_id=d.id).count()
        })

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_departments=total_departments,
        total_subjects=total_subjects,
        today_marked_count=today_marked_count,
        today_present=today_present,
        today_absent=today_absent,
        today_total_records=today_total_records,
        today_percentage=today_percentage,
        recent_sessions=recent_sessions,
        dept_stats=dept_stats
    )

# --------------------------------------------------------------------------
# STUDENTS CRUD
# --------------------------------------------------------------------------
@admin_bp.route('/students')
@admin_required
def students():
    students_list = User.query.filter_by(role='student').order_by(User.id.desc()).all()
    departments = Department.query.order_by(Department.name).all()
    new_student_id = User.generate_student_id()
    return render_template('admin/students.html', students=students_list, departments=departments, new_student_id=new_student_id)

@admin_bp.route('/students/add', methods=['POST'])
@admin_required
def add_student():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    roll_number = request.form.get('roll_number', '').strip()
    register_number = request.form.get('register_number', '').strip()
    department_id = request.form.get('department_id', type=int)
    year = request.form.get('year', '').strip()
    section = request.form.get('section', '').strip()
    phone_number = request.form.get('phone_number', '').strip()

    if not full_name or not email or not password or not roll_number or not department_id:
        flash('Full Name, Email, Password, Roll Number, and Department are required.', 'danger')
        return redirect(url_for('admin.students'))

    # Check unique email
    if User.query.filter_by(email=email).first():
        flash('A student or user with this email address already exists.', 'danger')
        return redirect(url_for('admin.students'))

    student_id_code = User.generate_student_id()
    student = User(
        user_id_code=student_id_code,
        full_name=full_name,
        email=email,
        role='student',
        phone_number=phone_number,
        roll_number=roll_number,
        register_number=register_number,
        department_id=department_id,
        year=year,
        section=section
    )
    student.set_password(password)

    db.session.add(student)
    db.session.commit()

    flash(f'Student {full_name} ({student_id_code}) created successfully.', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/edit/<int:id>', methods=['POST'])
@admin_required
def edit_student(id):
    student = User.query.get_or_404(id)
    if student.role != 'student':
        flash('Invalid target account.', 'danger')
        return redirect(url_for('admin.students'))

    email = request.form.get('email', '').strip().lower()
    existing_email = User.query.filter(User.email == email, User.id != id).first()
    if existing_email:
        flash('Email address is already in use by another account.', 'danger')
        return redirect(url_for('admin.students'))

    student.full_name = request.form.get('full_name', '').strip()
    student.email = email
    student.roll_number = request.form.get('roll_number', '').strip()
    student.register_number = request.form.get('register_number', '').strip()
    student.department_id = request.form.get('department_id', type=int)
    student.year = request.form.get('year', '').strip()
    student.section = request.form.get('section', '').strip()
    student.phone_number = request.form.get('phone_number', '').strip()

    db.session.commit()
    msg = f'Student details for {student.full_name} updated successfully.'
    # AJAX JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(status='success', message=msg)
    # Normal HTML flow
    flash(msg, 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/reset_password/<int:id>', methods=['POST'])
@admin_required
def reset_student_password(id):
    student = User.query.get_or_404(id)
    new_password = request.form.get('new_password', '').strip()
    if not new_password:
        flash('Password cannot be empty.', 'danger')
        return redirect(url_for('admin.students'))

    student.set_password(new_password)
    db.session.commit()
    flash(f'Password for student {student.full_name} reset successfully.', 'success')
    return redirect(url_for('admin.students'))

@admin_bp.route('/students/delete/<int:id>', methods=['POST'])
@admin_required
def delete_student(id):
    student = User.query.get_or_404(id)
    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {name} deleted successfully.', 'info')
    return redirect(url_for('admin.students'))

# --------------------------------------------------------------------------
# FACULTY CRUD
# --------------------------------------------------------------------------
@admin_bp.route('/faculty')
@admin_required
def faculty():
    faculty_list = User.query.filter_by(role='faculty').order_by(User.id.desc()).all()
    departments = Department.query.order_by(Department.name).all()
    new_faculty_id = User.generate_faculty_id()
    return render_template('admin/faculty.html', faculty_list=faculty_list, departments=departments, new_faculty_id=new_faculty_id)

@admin_bp.route('/faculty/add', methods=['POST'])
@admin_required
def add_faculty():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    department_id = request.form.get('department_id', type=int)
    designation = request.form.get('designation', '').strip()
    phone_number = request.form.get('phone_number', '').strip()

    if not full_name or not email or not password:
        flash('Full Name, Email, and Password are required.', 'danger')
        return redirect(url_for('admin.faculty'))

    if User.query.filter_by(email=email).first():
        flash('An account with this email address already exists.', 'danger')
        return redirect(url_for('admin.faculty'))

    faculty_id_code = User.generate_faculty_id()
    fac = User(
        user_id_code=faculty_id_code,
        full_name=full_name,
        email=email,
        role='faculty',
        department_id=department_id,
        designation=designation,
        phone_number=phone_number
    )
    fac.set_password(password)
    db.session.add(fac)
    db.session.commit()

    flash(f'Faculty member {full_name} created successfully.', 'success')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/edit/<int:id>', methods=['POST'])
@admin_required
def edit_faculty(id):
    fac = User.query.get_or_404(id)
    email = request.form.get('email', '').strip().lower()
    existing_email = User.query.filter(User.email == email, User.id != id).first()
    if existing_email:
        flash('Email address is already used by another account.', 'danger')
        return redirect(url_for('admin.faculty'))

    fac.full_name = request.form.get('full_name', '').strip()
    fac.email = email
    fac.department_id = request.form.get('department_id', type=int)
    fac.designation = request.form.get('designation', '').strip()
    fac.phone_number = request.form.get('phone_number', '').strip()

    db.session.commit()
    flash(f'Faculty member {fac.full_name} updated successfully.', 'success')
    return redirect(url_for('admin.faculty'))

@admin_bp.route('/faculty/delete/<int:id>', methods=['POST'])
@admin_required
def delete_faculty(id):
    fac = User.query.get_or_404(id)
    name = fac.full_name
    db.session.delete(fac)
    db.session.commit()
    flash(f'Faculty member {name} deleted.', 'info')
    return redirect(url_for('admin.faculty'))

# --------------------------------------------------------------------------
# DEPARTMENTS & SUBJECTS
# --------------------------------------------------------------------------
@admin_bp.route('/departments')
@admin_required
def departments():
    dept_list = Department.query.order_by(Department.name).all()
    subject_list = Subject.query.order_by(Subject.name).all()
    return render_template('admin/departments.html', departments=dept_list, subjects=subject_list)

@admin_bp.route('/departments/add', methods=['POST'])
@admin_required
def add_department():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()

    if not code or not name:
        flash('Department Code and Name are required.', 'danger')
        return redirect(url_for('admin.departments'))

    if Department.query.filter_by(code=code).first():
        flash('Department code already exists.', 'danger')
        return redirect(url_for('admin.departments'))

    dept = Department(code=code, name=name)
    db.session.add(dept)
    db.session.commit()

    flash(f'Department {name} ({code}) added.', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/edit/<int:id>', methods=['POST'])
@admin_required
def edit_department(id):
    dept = Department.query.get_or_404(id)
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()

    existing = Department.query.filter(Department.code == code, Department.id != id).first()
    if existing:
        flash('Department code already exists.', 'danger')
        return redirect(url_for('admin.departments'))

    dept.code = code
    dept.name = name
    db.session.commit()
    flash('Department updated.', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/delete/<int:id>', methods=['POST'])
@admin_required
def delete_department(id):
    dept = Department.query.get_or_404(id)
    name = dept.name
    db.session.delete(dept)
    db.session.commit()
    flash(f'Department {name} deleted.', 'info')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/subjects/add', methods=['POST'])
@admin_required
def add_subject():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    department_id = request.form.get('department_id', type=int)
    year = request.form.get('year', '').strip()
    semester = request.form.get('semester', '').strip()

    if not code or not name or not department_id or not year:
        flash('Subject Code, Name, Department, and Year are required.', 'danger')
        return redirect(url_for('admin.departments'))

    if Subject.query.filter_by(code=code).first():
        flash('Subject code already exists.', 'danger')
        return redirect(url_for('admin.departments'))

    sub = Subject(code=code, name=name, department_id=department_id, year=year, semester=semester)
    db.session.add(sub)
    db.session.commit()

    flash(f'Subject {name} ({code}) added.', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@admin_required
def delete_subject(id):
    sub = Subject.query.get_or_404(id)
    name = sub.name
    db.session.delete(sub)
    db.session.commit()
    flash(f'Subject {name} deleted.', 'info')
    return redirect(url_for('admin.departments'))

# --------------------------------------------------------------------------
# COLLEGE CUSTOMIZATION SETTINGS
# --------------------------------------------------------------------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    col_settings = CollegeSettings.get_settings()

    if request.method == 'POST':
        col_settings.college_name = request.form.get('college_name', '').strip()
        col_settings.address = request.form.get('address', '').strip()
        col_settings.contact_number = request.form.get('contact_number', '').strip()
        col_settings.email_address = request.form.get('email_address', '').strip()
        col_settings.principal_name = request.form.get('principal_name', '').strip()
        col_settings.academic_year = request.form.get('academic_year', '').strip()
        col_settings.semester = request.form.get('semester', 'Semester 1').strip()
        col_settings.working_days = request.form.get('working_days', 180, type=int)
        col_settings.holidays_list = request.form.get('holidays_list', '').strip()
        col_settings.min_attendance_percentage = request.form.get('min_attendance_percentage', 75.0, type=float)
        col_settings.theme = request.form.get('theme', 'light').strip()

        # Handle Logo File Upload
        if 'college_logo' in request.files:
            file = request.files['college_logo']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = int(datetime.utcnow().timestamp())
                new_filename = f"logo_{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
                
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(file_path)
                col_settings.college_logo = new_filename

        db.session.commit()
        flash('College settings updated successfully! All pages & headers have been updated.', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', settings=col_settings)
