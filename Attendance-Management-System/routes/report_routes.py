from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for, jsonify
from datetime import datetime, timedelta
from models import db
from models.user import User
from models.department import Department
from models.subject import Subject
from models.attendance import Attendance, AttendanceRecord
from utils.helpers import faculty_or_admin_required
from utils.pdf_exporter import generate_pdf_report
from utils.excel_exporter import generate_excel_report

report_bp = Blueprint('report', __name__, url_prefix='/reports')

def get_report_data(report_type, start_date=None, end_date=None, dept_id=None, subj_id=None, student_id=None):
    """
    Computes report headers, data rows, and summary statistics based on filters.
    """
    headers = []
    rows = []
    summary = {}
    title = "Attendance Report"
    subtitle = ""

    today = datetime.utcnow().date()

    if report_type == 'daily':
        target_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else today
        title = f"Daily Attendance Report - {target_date.strftime('%d %b %Y')}"
        headers = ["#", "Department", "Subject", "Year & Sec", "Total Students", "Present", "Absent", "Percentage"]
        
        query = Attendance.query.filter_by(attendance_date=target_date)
        if dept_id:
            query = query.filter_by(department_id=dept_id)
        sessions = query.all()

        total_sessions = len(sessions)
        tot_students = sum(len(s.records) for s in sessions)
        tot_present = sum(sum(1 for r in s.records if r.status == 'Present') for s in sessions)

        for idx, s in enumerate(sessions, 1):
            tot = len(s.records)
            pres = sum(1 for r in s.records if r.status == 'Present')
            absent = tot - pres
            pct = round((pres / tot * 100), 1) if tot > 0 else 0
            rows.append([
                idx,
                s.department.code if s.department else 'N/A',
                s.subject.name if s.subject else 'N/A',
                f"{s.year} - {s.section}",
                tot,
                pres,
                absent,
                f"{pct}%"
            ])

        summary = {
            "Total Class Sessions": total_sessions,
            "Total Attendance Records": tot_students,
            "Overall Present Count": tot_present,
            "Overall Attendance Percentage": f"{round((tot_present/tot_students*100), 1)}%" if tot_students > 0 else "0%"
        }

    elif report_type == 'weekly':
        e_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else today
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else (e_date - timedelta(days=6))
        title = f"Weekly Attendance Report ({s_date.strftime('%b %d')} to {e_date.strftime('%b %d, %Y')})"
        headers = ["Date", "Department", "Subject", "Year & Sec", "Total Students", "Present", "Absent", "Percentage"]

        query = Attendance.query.filter(Attendance.attendance_date >= s_date, Attendance.attendance_date <= e_date)
        if dept_id:
            query = query.filter_by(department_id=dept_id)
        sessions = query.order_by(Attendance.attendance_date.desc()).all()

        tot_students = sum(len(s.records) for s in sessions)
        tot_present = sum(sum(1 for r in s.records if r.status == 'Present') for s in sessions)

        for s in sessions:
            tot = len(s.records)
            pres = sum(1 for r in s.records if r.status == 'Present')
            absent = tot - pres
            pct = round((pres / tot * 100), 1) if tot > 0 else 0
            rows.append([
                s.attendance_date.strftime('%Y-%m-%d'),
                s.department.code if s.department else 'N/A',
                s.subject.name if s.subject else 'N/A',
                f"{s.year} - {s.section}",
                tot,
                pres,
                absent,
                f"{pct}%"
            ])

        summary = {
            "Date Range": f"{s_date} to {e_date}",
            "Total Sessions": len(sessions),
            "Overall Attendance Percentage": f"{round((tot_present/tot_students*100), 1)}%" if tot_students > 0 else "0%"
        }

    elif report_type == 'monthly':
        e_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else today
        s_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else (e_date - timedelta(days=30))
        title = f"Monthly Attendance Summary ({s_date.strftime('%b %d')} - {e_date.strftime('%b %d, %Y')})"
        headers = ["Student ID", "Roll Number", "Full Name", "Department", "Total Classes", "Present", "Absent", "Percentage"]

        # Aggregate student attendance over the period
        students_query = User.query.filter_by(role='student')
        if dept_id:
            students_query = students_query.filter_by(department_id=dept_id)
        students = students_query.all()

        for st in students:
            recs = AttendanceRecord.query.join(Attendance).filter(
                AttendanceRecord.student_id == st.id,
                Attendance.attendance_date >= s_date,
                Attendance.attendance_date <= e_date
            ).all()

            tot = len(recs)
            pres = sum(1 for r in recs if r.status == 'Present')
            absent = tot - pres
            pct = round((pres / tot * 100), 1) if tot > 0 else 0
            rows.append([
                st.user_id_code,
                st.roll_number or 'N/A',
                st.full_name,
                st.department.code if st.department else 'N/A',
                tot,
                pres,
                absent,
                f"{pct}%"
            ])

        summary = {
            "Report Period": f"{s_date} to {e_date}",
            "Total Students Evaluated": len(students)
        }

    elif report_type == 'student':
        student = User.query.get(student_id) if student_id else None
        if student:
            title = f"Individual Student Attendance Report - {student.full_name}"
            subtitle = f"ID: {student.user_id_code} | Roll No: {student.roll_number} | Dept: {student.department.name if student.department else 'N/A'} | Year: {student.year} ({student.section})"
            headers = ["Date", "Subject Code", "Subject Name", "Status", "Remarks"]

            records = AttendanceRecord.query.filter_by(student_id=student.id).join(Attendance).order_by(Attendance.attendance_date.desc()).all()
            tot = len(records)
            pres = sum(1 for r in records if r.status == 'Present')
            pct = round((pres / tot * 100), 1) if tot > 0 else 0

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
                "Attendance Percentage": f"{pct}%",
                "Eligibility Status": "Eligible" if pct >= 75 else "Warning: Shortage (< 75%)"
            }
        else:
            headers = ["Message"]
            rows = [["Please select a valid student."]]

    elif report_type == 'subject':
        subject = Subject.query.get(subj_id) if subj_id else None
        if subject:
            title = f"Subject-Wise Attendance Report - {subject.name} ({subject.code})"
            subtitle = f"Department: {subject.department.name} | Year: {subject.year}"
            headers = ["Roll Number", "Student Name", "Total Classes", "Present", "Absent", "Percentage"]

            students = User.query.filter_by(role='student', department_id=subject.department_id, year=subject.year).all()
            for st in students:
                recs = AttendanceRecord.query.join(Attendance).filter(
                    AttendanceRecord.student_id == st.id,
                    Attendance.subject_id == subject.id
                ).all()

                tot = len(recs)
                pres = sum(1 for r in recs if r.status == 'Present')
                absent = tot - pres
                pct = round((pres / tot * 100), 1) if tot > 0 else 0

                rows.append([
                    st.roll_number or 'N/A',
                    st.full_name,
                    tot,
                    pres,
                    absent,
                    f"{pct}%"
                ])

            summary = {
                "Subject": f"{subject.name} ({subject.code})",
                "Total Enrolled Students": len(students)
            }
        else:
            headers = ["Message"]
            rows = [["Please select a subject."]]

    elif report_type == 'department':
        dept = Department.query.get(dept_id) if dept_id else None
        if dept:
            title = f"Department-Wise Attendance Performance - {dept.name} ({dept.code})"
            headers = ["Year", "Total Students", "Total Classes", "Average Attendance %"]

            years = ['1st Year', '2nd Year', '3rd Year', '4th Year']
            for y in years:
                st_count = User.query.filter_by(role='student', department_id=dept.id, year=y).count()
                sessions = Attendance.query.filter_by(department_id=dept.id, year=y).all()

                tot_recs = sum(len(s.records) for s in sessions)
                tot_pres = sum(sum(1 for r in s.records if r.status == 'Present') for s in sessions)
                avg_pct = round((tot_pres / tot_recs * 100), 1) if tot_recs > 0 else 0

                rows.append([
                    y,
                    st_count,
                    len(sessions),
                    f"{avg_pct}%"
                ])

            summary = {
                "Department": dept.name,
                "Total Students": User.query.filter_by(role='student', department_id=dept.id).count()
            }
        else:
            headers = ["Message"]
            rows = [["Please select a department."]]

    return title, subtitle, headers, rows, summary

@report_bp.route('/')
@faculty_or_admin_required
def index():
    departments = Department.query.order_by(Department.name).all()
    subjects = Subject.query.order_by(Subject.name).all()
    students = User.query.filter_by(role='student').order_by(User.full_name).all()

    report_type = request.args.get('type', 'daily')
    start_date = request.args.get('start_date', datetime.utcnow().strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
    dept_id = request.args.get('department_id', type=int)
    subj_id = request.args.get('subject_id', type=int)
    student_id = request.args.get('student_id', type=int)

    title, subtitle, headers, rows, summary = get_report_data(
        report_type, start_date, end_date, dept_id, subj_id, student_id
    )

    return render_template(
        'reports/index.html',
        departments=departments,
        subjects=subjects,
        students=students,
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        selected_dept=dept_id,
        selected_subj=subj_id,
        selected_student=student_id,
        title=title,
        subtitle=subtitle,
        headers=headers,
        rows=rows,
        summary=summary
    )

@report_bp.route('/export/pdf')
@faculty_or_admin_required
def export_pdf():
    report_type = request.args.get('type', 'daily')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    dept_id = request.args.get('department_id', type=int)
    subj_id = request.args.get('subject_id', type=int)
    student_id = request.args.get('student_id', type=int)

    title, subtitle, headers, rows, summary = get_report_data(
        report_type, start_date, end_date, dept_id, subj_id, student_id
    )

    pdf_buffer = generate_pdf_report(title, subtitle, headers, rows, summary)
    filename = f"{report_type}_attendance_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf"

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )

@report_bp.route('/export/excel')
@faculty_or_admin_required
def export_excel():
    report_type = request.args.get('type', 'daily')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    dept_id = request.args.get('department_id', type=int)
    subj_id = request.args.get('subject_id', type=int)
    student_id = request.args.get('student_id', type=int)

    title, subtitle, headers, rows, summary = get_report_data(
        report_type, start_date, end_date, dept_id, subj_id, student_id
    )

    excel_buffer = generate_excel_report(title, subtitle, headers, rows, summary)
    filename = f"{report_type}_attendance_report_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"

    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
