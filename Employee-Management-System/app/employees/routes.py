from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.employees import employees_bp
from app.employees.forms import EmployeeForm
from app.models import Employee, Department, safe_commit
from app.extensions import db
from app.utils import save_profile_picture
from app.auth.decorators import admin_required

@employees_bp.route('/')
@login_required
def index():
    search_query = request.args.get('search', '', type=str)
    department_filter = request.args.get('department', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    page = request.args.get('page', 1, type=int)

    query = Employee.query

    if search_query:
        query = query.filter(
            (Employee.first_name.ilike(f'%{search_query}%')) |
            (Employee.last_name.ilike(f'%{search_query}%')) |
            (Employee.email.ilike(f'%{search_query}%')) |
            (Employee.employee_id.ilike(f'%{search_query}%')) |
            (Employee.designation.ilike(f'%{search_query}%'))
        )

    if department_filter:
        query = query.join(Department).filter(Department.department_name == department_filter)

    if status_filter:
        query = query.filter(Employee.status == status_filter)

    pagination = query.order_by(Employee.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
    employees = pagination.items
    departments = Department.query.order_by(Department.department_name.asc()).all()
    statuses = ['Active', 'Inactive']

    return render_template(
        'employees/index.html',
        employees=employees,
        pagination=pagination,
        search_query=search_query,
        department_filter=department_filter,
        status_filter=status_filter,
        departments=departments,
        statuses=statuses
    )

@employees_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    try:
        departments = Department.query.order_by(Department.department_name.asc()).all()
        form = EmployeeForm()
        form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.department_name) for d in departments]

        if form.validate_on_submit():
            picture_file = 'default.jpg'
            if form.profile_image.data:
                picture_file = save_profile_picture(form.profile_image.data)

            dept_id = form.department_id.data if form.department_id.data and form.department_id.data != 0 else None

            employee = Employee(
                employee_id=form.employee_id.data.strip().upper(),
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                email=form.email.data.strip().lower(),
                phone=form.phone.data.strip() if form.phone.data else None,
                gender=form.gender.data,
                date_of_birth=form.date_of_birth.data,
                address=form.address.data.strip() if form.address.data else None,
                city=form.city.data.strip() if form.city.data else None,
                state=form.state.data.strip() if form.state.data else None,
                country=form.country.data.strip() if form.country.data else None,
                pincode=form.pincode.data.strip() if form.pincode.data else None,
                department_id=dept_id,
                designation=form.designation.data.strip(),
                joining_date=form.joining_date.data,
                salary=form.salary.data,
                status=form.status.data,
                profile_image=picture_file
            )
            db.session.add(employee)
            success, error_msg = safe_commit()
            if success:
                flash(f'Employee {employee.full_name} added successfully!', 'success')
                return redirect(url_for('employees.index'))
            else:
                flash(f'Failed to add employee: {error_msg}', 'danger')

        return render_template('employees/add_edit.html', form=form, title='Add New Employee', is_edit=False)
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
        return redirect(url_for('employees.index'))

@employees_bp.route('/<int:id>')
@login_required
def view(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/view.html', employee=employee)

@employees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    try:
        employee = Employee.query.get_or_404(id)
        departments = Department.query.order_by(Department.department_name.asc()).all()
        form = EmployeeForm(original_id=employee.employee_id, original_email=employee.email, obj=employee)
        form.department_id.choices = [(0, 'Select Department')] + [(d.id, d.department_name) for d in departments]
        
        if request.method == 'GET' and employee.department_id:
            form.department_id.data = employee.department_id

        if form.validate_on_submit():
            if form.profile_image.data:
                picture_file = save_profile_picture(form.profile_image.data)
                employee.profile_image = picture_file

            dept_id = form.department_id.data if form.department_id.data and form.department_id.data != 0 else None

            employee.employee_id = form.employee_id.data.strip().upper()
            employee.first_name = form.first_name.data.strip()
            employee.last_name = form.last_name.data.strip()
            employee.email = form.email.data.strip().lower()
            employee.phone = form.phone.data.strip() if form.phone.data else None
            employee.gender = form.gender.data
            employee.date_of_birth = form.date_of_birth.data
            employee.address = form.address.data.strip() if form.address.data else None
            employee.city = form.city.data.strip() if form.city.data else None
            employee.state = form.state.data.strip() if form.state.data else None
            employee.country = form.country.data.strip() if form.country.data else None
            employee.pincode = form.pincode.data.strip() if form.pincode.data else None
            employee.department_id = dept_id
            employee.designation = form.designation.data.strip()
            employee.joining_date = form.joining_date.data
            employee.salary = form.salary.data
            employee.status = form.status.data
            
            success, error_msg = safe_commit()
            if success:
                flash(f'Employee {employee.full_name} updated successfully!', 'success')
                return redirect(url_for('employees.view', id=employee.id))
            else:
                flash(f'Failed to update employee: {error_msg}', 'danger')

        return render_template('employees/add_edit.html', form=form, title=f'Edit {employee.full_name}', is_edit=True, employee=employee)
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
        return redirect(url_for('employees.index'))

@employees_bp.route('/delete/<int:id>', methods=['POST'])
@employees_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    try:
        employee = Employee.query.get_or_404(id)
        name = employee.full_name
        db.session.delete(employee)
        success, error_msg = safe_commit()
        if success:
            flash(f'Employee {name} deleted successfully.', 'info')
        else:
            flash(f'Failed to delete employee: {error_msg}', 'danger')
        return redirect(url_for('employees.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'An unexpected error occurred while deleting employee: {str(e)}', 'danger')
        return redirect(url_for('employees.index'))


