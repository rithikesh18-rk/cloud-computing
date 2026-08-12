from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import date
from app.dashboard import dashboard_bp
from app.models import Employee, Department, Attendance, Leave
from app.extensions import db

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    today = date.today()
    
    total_employees = Employee.query.count()
    total_departments = Department.query.count()
    present_today = Attendance.query.filter_by(attendance_date=today, status='Present').count()
    absent_today = Attendance.query.filter_by(attendance_date=today, status='Absent').count()
    pending_leaves = Leave.query.filter_by(status='Pending').count()
    
    # Department breakdown for chart
    dept_stats = db.session.query(
        Department.department_name, func.count(Employee.id)
    ).join(Employee, Employee.department_id == Department.id, isouter=True)\
     .group_by(Department.department_name).all()
    
    dept_labels = [dept for dept, count in dept_stats] if dept_stats else []
    dept_counts = [count for dept, count in dept_stats] if dept_stats else []

    # Attendance summary breakdown for chart
    att_stats = db.session.query(
        Attendance.status, func.count(Attendance.id)
    ).group_by(Attendance.status).all()

    att_labels = [st for st, cnt in att_stats] if att_stats else ['Present', 'Absent', 'On Leave']
    att_counts = [cnt for st, cnt in att_stats] if att_stats else [present_today, absent_today, pending_leaves]

    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
    recent_leaves = Leave.query.order_by(Leave.applied_date.desc()).limit(5).all()

    return render_template(
        'dashboard/index.html',
        total_employees=total_employees,
        total_departments=total_departments,
        present_today=present_today,
        absent_today=absent_today,
        pending_leaves=pending_leaves,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        att_labels=att_labels,
        att_counts=att_counts,
        recent_employees=recent_employees,
        recent_leaves=recent_leaves
    )
