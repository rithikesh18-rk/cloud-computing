from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime
from models import db
from models.user import User
from models.department import Department
from models.subject import Subject
from models.attendance import Attendance, AttendanceRecord
from utils.helpers import faculty_or_admin_required, login_required

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/mark', methods=['GET', 'POST'])
@faculty_or_admin_required
def mark():
    departments = Department.query.order_by(Department.name).all()

    if request.method == 'POST':
        department_id = request.form.get('department_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        year = request.form.get('year', '').strip()
        section = request.form.get('section', '').strip()
        date_str = request.form.get('attendance_date', '').strip()

        if not department_id or not subject_id or not year or not section or not date_str:
            flash('All filter fields (Department, Subject, Year, Section, Date) are required.', 'danger')
            return redirect(url_for('attendance.mark'))

        try:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'danger')
            return redirect(url_for('attendance.mark'))

        # Check if attendance session already exists
        existing_session = Attendance.query.filter_by(
            department_id=department_id,
            subject_id=subject_id,
            year=year,
            section=section,
            attendance_date=attendance_date
        ).first()

        marked_by_id = session.get('user_id')

        if existing_session:
            att_session = existing_session
            att_session.marked_by_id = marked_by_id
        else:
            att_session = Attendance(
                department_id=department_id,
                subject_id=subject_id,
                year=year,
                section=section,
                attendance_date=attendance_date,
                marked_by_id=marked_by_id
            )
            db.session.add(att_session)
            db.session.commit()

        # Extract student attendance statuses from form
        # Form inputs: status_<student_id> = 'Present' or 'Absent'
        students = User.query.filter_by(
            role='student',
            department_id=department_id,
            year=year,
            section=section
        ).all()

        for student in students:
            status = request.form.get(f'status_{student.id}', 'Absent')
            remarks = request.form.get(f'remarks_{student.id}', '').strip()

            rec = AttendanceRecord.query.filter_by(
                attendance_id=att_session.id,
                student_id=student.id
            ).first()

            if rec:
                rec.status = status
                rec.remarks = remarks
            else:
                rec = AttendanceRecord(
                    attendance_id=att_session.id,
                    student_id=student.id,
                    status=status,
                    remarks=remarks
                )
                db.session.add(rec)

        db.session.commit()
        flash('Attendance saved successfully!', 'success')
        return redirect(url_for('attendance.view_sessions'))

    return render_template('attendance/mark.html', departments=departments, today_date=datetime.utcnow().strftime('%Y-%m-%d'))

@attendance_bp.route('/view')
@faculty_or_admin_required
def view_sessions():
    departments = Department.query.order_by(Department.name).all()

    department_id = request.args.get('department_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('attendance_date', '').strip()

    query = Attendance.query

    if department_id:
        query = query.filter_by(department_id=department_id)
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if date_str:
        try:
            d = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=d)
        except ValueError:
            pass

    sessions = query.order_by(Attendance.attendance_date.desc(), Attendance.id.desc()).all()
    subjects = Subject.query.order_by(Subject.name).all()

    return render_template(
        'attendance/view.html',
        sessions=sessions,
        departments=departments,
        subjects=subjects,
        selected_dept=department_id,
        selected_subj=subject_id,
        selected_date=date_str
    )

@attendance_bp.route('/edit/<int:session_id>', methods=['GET', 'POST'])
@faculty_or_admin_required
def edit_session(session_id):
    att_session = Attendance.query.get_or_404(session_id)

    if request.method == 'POST':
        records = AttendanceRecord.query.filter_by(attendance_id=att_session.id).all()
        for rec in records:
            status = request.form.get(f'status_{rec.student_id}', 'Absent')
            remarks = request.form.get(f'remarks_{rec.student_id}', '').strip()
            rec.status = status
            rec.remarks = remarks

        db.session.commit()
        flash('Attendance session updated successfully.', 'success')
        return redirect(url_for('attendance.view_sessions'))

    records = AttendanceRecord.query.filter_by(attendance_id=att_session.id).all()
    return render_template('attendance/edit.html', session_data=att_session, records=records)

@attendance_bp.route('/delete/<int:session_id>', methods=['POST'])
@faculty_or_admin_required
def delete_session(session_id):
    att_session = Attendance.query.get_or_404(session_id)
    db.session.delete(att_session)
    db.session.commit()
    flash('Attendance session deleted successfully.', 'info')
    return redirect(url_for('attendance.view_sessions'))


# --------------------------------------------------------------------------
# DYNAMIC AJAX APIs FOR FRONTEND FILTERS
# --------------------------------------------------------------------------
@attendance_bp.route('/api/subjects')
@login_required
def api_subjects():
    dept_id = request.args.get('department_id', type=int)
    year = request.args.get('year', '').strip()

    query = Subject.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if year:
        query = query.filter_by(year=year)

    subjects = query.order_by(Subject.name).all()
    return jsonify([s.to_dict() for s in subjects])

@attendance_bp.route('/api/students')
@login_required
def api_students():
    dept_id = request.args.get('department_id', type=int)
    year = request.args.get('year', '').strip()
    section = request.args.get('section', '').strip()

    if not dept_id or not year or not section:
        return jsonify([])

    students = User.query.filter_by(
        role='student',
        department_id=dept_id,
        year=year,
        section=section
    ).order_by(User.roll_number, User.full_name).all()

    return jsonify([s.to_dict() for s in students])
