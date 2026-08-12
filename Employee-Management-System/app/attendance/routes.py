from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date
from app.attendance import attendance_bp
from app.attendance.forms import AttendanceForm
from app.models import Attendance, Employee
from app.extensions import db
from app.auth.decorators import admin_required

@attendance_bp.route('/')
@login_required
def index():
    date_filter = request.args.get('date', '', type=str)
    
    query = Attendance.query

    # If current user is an Employee, restrict view to own attendance
    if current_user.role == 'Employee':
        emp = current_user.employee
        if not emp:
            flash('No associated employee record found for your user account.', 'warning')
            return render_template('attendance/index.html', attendances=[], percentage=100.0)
        query = query.filter_by(employee_id=emp.id)

    if date_filter:
        try:
            filter_dt = date.fromisoformat(date_filter)
            query = query.filter(Attendance.attendance_date == filter_dt)
        except ValueError:
            pass

    attendances = query.order_by(Attendance.attendance_date.desc()).all()
    
    # Calculate attendance percentage
    percentage = 100.0
    if current_user.role == 'Employee' and current_user.employee:
        percentage = current_user.employee.attendance_percentage

    return render_template('attendance/index.html', attendances=attendances, date_filter=date_filter, percentage=percentage)

@attendance_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    form = AttendanceForm()
    form.set_employee_choices()
    
    if form.validate_on_submit():
        # Check if record for this date and employee already exists
        existing = Attendance.query.filter_by(
            employee_id=form.employee_id.data,
            attendance_date=form.attendance_date.data
        ).first()
        if existing:
            flash('An attendance record already exists for this employee on the selected date.', 'danger')
            return render_template('attendance/add_edit.html', form=form, title='Mark Attendance', is_edit=False)

        att = Attendance(
            employee_id=form.employee_id.data,
            attendance_date=form.attendance_date.data,
            check_in=form.check_in.data,
            check_out=form.check_out.data,
            status=form.status.data,
            remarks=form.remarks.data
        )
        db.session.add(att)
        db.session.commit()
        flash('Attendance record saved successfully!', 'success')
        return redirect(url_for('attendance.index'))

    return render_template('attendance/add_edit.html', form=form, title='Mark Attendance', is_edit=False)

@attendance_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    att = Attendance.query.get_or_404(id)
    form = AttendanceForm(obj=att)
    form.set_employee_choices()

    if form.validate_on_submit():
        att.employee_id = form.employee_id.data
        att.attendance_date = form.attendance_date.data
        att.check_in = form.check_in.data
        att.check_out = form.check_out.data
        att.status = form.status.data
        att.remarks = form.remarks.data
        db.session.commit()
        flash('Attendance record updated successfully!', 'success')
        return redirect(url_for('attendance.index'))

    return render_template('attendance/add_edit.html', form=form, title='Edit Attendance Record', is_edit=True, att=att)

@attendance_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    att = Attendance.query.get_or_404(id)
    db.session.delete(att)
    db.session.commit()
    flash('Attendance record deleted successfully.', 'info')
    return redirect(url_for('attendance.index'))
