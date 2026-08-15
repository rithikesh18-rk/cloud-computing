from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.leave import leave_bp
from app.leave.forms import LeaveForm
from app.models import Leave, Employee, safe_commit
from app.extensions import db
from app.auth.decorators import admin_required

@leave_bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '', type=str)
    
    query = Leave.query

    if current_user.role == 'Employee':
        emp = current_user.employee
        if not emp:
            flash('No associated employee profile found.', 'warning')
            return render_template('leave/index.html', leaves=[])
        query = query.filter_by(employee_id=emp.id)

    if status_filter:
        query = query.filter(Leave.status == status_filter)

    leaves = query.order_by(Leave.applied_date.desc()).all()
    return render_template('leave/index.html', leaves=leaves, status_filter=status_filter)

@leave_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    emp = current_user.employee
    if not emp and current_user.role != 'Admin':
        flash('You must have an employee profile linked to apply for leave.', 'danger')
        return redirect(url_for('dashboard.index'))

    form = LeaveForm()
    if form.validate_on_submit():
        # Target employee: either current_user's linked employee or first available if admin testing
        target_emp = emp or Employee.query.first()
        if not target_emp:
            flash('No employee records exist in the system to assign leave to.', 'danger')
            return redirect(url_for('leave.index'))

        leave_req = Leave(
            employee_id=target_emp.id,
            leave_type=form.leave_type.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            reason=form.reason.data.strip() if form.reason.data else None,
            status='Pending'
        )
        db.session.add(leave_req)
        success, error_msg = safe_commit()
        if success:
            flash('Leave application submitted successfully!', 'success')
            return redirect(url_for('leave.index'))
        else:
            flash(f'Failed to submit leave application: {error_msg}', 'danger')

    return render_template('leave/apply.html', form=form)

@leave_bp.route('/approve/<int:id>', methods=['POST'])
@admin_required
def approve(id):
    leave_req = Leave.query.get_or_404(id)
    leave_req.status = 'Approved'
    success, error_msg = safe_commit()
    if success:
        emp_name = leave_req.employee.full_name if leave_req.employee else f"Employee #{leave_req.employee_id}"
        flash(f'Leave application #{leave_req.id} for {emp_name} has been APPROVED.', 'success')
    else:
        flash(f'Failed to approve leave: {error_msg}', 'danger')
    return redirect(url_for('leave.index'))

@leave_bp.route('/reject/<int:id>', methods=['POST'])
@admin_required
def reject(id):
    leave_req = Leave.query.get_or_404(id)
    leave_req.status = 'Rejected'
    success, error_msg = safe_commit()
    if success:
        emp_name = leave_req.employee.full_name if leave_req.employee else f"Employee #{leave_req.employee_id}"
        flash(f'Leave application #{leave_req.id} for {emp_name} has been REJECTED.', 'info')
    else:
        flash(f'Failed to reject leave: {error_msg}', 'danger')
    return redirect(url_for('leave.index'))

