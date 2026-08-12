from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.departments import departments_bp
from app.departments.forms import DepartmentForm
from app.models import Department, Employee
from app.extensions import db
from app.auth.decorators import admin_required

@departments_bp.route('/')
@login_required
def index():
    departments = Department.query.order_by(Department.created_at.desc()).all()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    form = DepartmentForm()
    if form.validate_on_submit():
        dept = Department(
            department_name=form.department_name.data,
            department_code=form.department_code.data.upper(),
            description=form.description.data
        )
        db.session.add(dept)
        db.session.commit()
        flash(f'Department "{dept.department_name}" created successfully!', 'success')
        return redirect(url_for('departments.index'))
    return render_template('departments/add_edit.html', form=form, title='Add Department', is_edit=False)

@departments_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    dept = Department.query.get_or_404(id)
    form = DepartmentForm(original_code=dept.department_code, obj=dept)
    if form.validate_on_submit():
        dept.department_name = form.department_name.data
        dept.department_code = form.department_code.data.upper()
        dept.description = form.description.data
        db.session.commit()
        flash(f'Department "{dept.department_name}" updated successfully!', 'success')
        return redirect(url_for('departments.index'))
    return render_template('departments/add_edit.html', form=form, title=f'Edit Department - {dept.department_name}', is_edit=True, dept=dept)

@departments_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    dept = Department.query.get_or_404(id)
    if len(dept.employees) > 0:
        flash(f'Cannot delete department "{dept.department_name}" because it still has {len(dept.employees)} assigned employees.', 'danger')
        return redirect(url_for('departments.index'))
    name = dept.department_name
    db.session.delete(dept)
    db.session.commit()
    flash(f'Department "{name}" deleted successfully.', 'info')
    return redirect(url_for('departments.index'))
