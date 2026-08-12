from flask import Blueprint, render_template, session, redirect, url_for, send_file, flash
from datetime import datetime
from models import db
from models.user import User
from models.attendance import Attendance, AttendanceRecord
from models.subject import Subject
from utils.helpers import student_required, get_current_user
from utils.pdf_exporter import generate_pdf_report

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.route('/dashboard')
@student_required
def dashboard():
    student = get_current_user()
    if not student:
        flash('Student account not found.', 'danger')
        return redirect(url_for('auth.login'))

    records = AttendanceRecord.query.filter_by(student_id=student.id).join(Attendance).order_by(Attendance.attendance_date.desc()).all()

    total_classes = len(records)
    total_present = sum(1 for r in records if r.status == 'Present')
    total_absent = total_classes - total_present
    overall_percentage = round((total_present / total_classes * 100), 1) if total_classes > 0 else 0.0

    # Subject-wise breakdown
    subject_stats = {}
    for r in records:
        subj = r.attendance.subject
        subj_name = subj.name if subj else 'Unknown Subject'
        subj_code = subj.code if subj else 'N/A'

        if subj_code not in subject_stats:
            subject_stats[subj_code] = {
                'name': subj_name,
                'total': 0,
                'present': 0,
                'absent': 0,
                'pct': 0.0
            }

        subject_stats[subj_code]['total'] += 1
        if r.status == 'Present':
            subject_stats[subj_code]['present'] += 1
        else:
            subject_stats[subj_code]['absent'] += 1

    for code, stats in subject_stats.items():
        if stats['total'] > 0:
            stats['pct'] = round((stats['present'] / stats['total'] * 100), 1)

    return render_template(
        'student/dashboard.html',
        student=student,
        total_classes=total_classes,
        total_present=total_present,
        total_absent=total_absent,
        overall_percentage=overall_percentage,
        subject_stats=subject_stats,
        recent_records=records[:10]
    )

@student_bp.route('/export/pdf')
@student_required
def export_pdf():
    student = get_current_user()
    if not student:
        return redirect(url_for('auth.login'))

    title = f"Individual Attendance Report - {student.full_name}"
    subtitle = f"ID: {student.user_id_code} | Roll No: {student.roll_number} | Dept: {student.department.name if student.department else 'N/A'} | Year: {student.year} ({student.section})"
    headers = ["Date", "Subject Code", "Subject Name", "Status", "Remarks"]

    records = AttendanceRecord.query.filter_by(student_id=student.id).join(Attendance).order_by(Attendance.attendance_date.desc()).all()
    tot = len(records)
    pres = sum(1 for r in records if r.status == 'Present')
    pct = round((pres / tot * 100), 1) if tot > 0 else 0

    rows = []
    for r in records:
        rows.append([
            r.attendance.attendance_date.strftime('%Y-%m-%d'),
            r.attendance.subject.code if r.attendance.subject else 'N/A',
            r.attendance.subject.name if r.attendance.subject else 'N/A',
            r.status,
            r.remarks or ''
        ])

    summary = {
        "Student Name": student.full_name,
        "Total Classes Conducted": tot,
        "Total Classes Attended": pres,
        "Overall Attendance Percentage": f"{pct}%",
        "Eligibility Status": "Eligible" if pct >= 75 else "Warning: Shortage (< 75%)"
    }

    pdf_buffer = generate_pdf_report(title, subtitle, headers, rows, summary)
    filename = f"my_attendance_{student.user_id_code}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
