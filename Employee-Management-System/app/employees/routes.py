from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.employees import employees_bp
from app.employees.forms import EmployeeForm
from app.models import Employee, Department
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
    form = EmployeeForm()
    if form.validate_on_submit():
        picture_file = 'default.jpg'
        if form.profile_image.data:
            picture_file = save_profile_picture(form.profile_image.data)

        employee = Employee(
            employee_id=form.employee_id.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            phone=form.phone.data,
            gender=form.gender.data,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            country=form.country.data,
            pincode=form.pincode.data,
            department_id=form.department_id.data,
            designation=form.designation.data,
            joining_date=form.joining_date.data,
            salary=form.salary.data,
            status=form.status.data,
            profile_image=picture_file
        )
        db.session.add(employee)
        db.session.commit()
        flash(f'Employee {employee.full_name} added successfully!', 'success')
        return redirect(url_for('employees.index'))

    return render_template('employees/add_edit.html', form=form, title='Add New Employee', is_edit=False)

@employees_bp.route('/<int:id>')
@login_required
def view(id):
    employee = Employee.query.get_or_404(id)
    return render_template('employees/view.html', employee=employee)

@employees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(original_id=employee.employee_id, original_email=employee.email, obj=employee)
    
    if form.validate_on_submit():
        if form.profile_image.data:
            picture_file = save_profile_picture(form.profile_image.data)
            employee.profile_image = picture_file

        employee.employee_id = form.employee_id.data
        employee.first_name = form.first_name.data
        employee.last_name = form.last_name.data
        employee.email = form.email.data
        employee.phone = form.phone.data
        employee.gender = form.gender.data
        employee.date_of_birth = form.date_of_birth.data
        employee.address = form.address.data
        employee.city = form.city.data
        employee.state = form.state.data
        employee.country = form.country.data
        employee.pincode = form.pincode.data
        employee.department_id = form.department_id.data
        employee.designation = form.designation.data
        employee.joining_date = form.joining_date.data
        employee.salary = form.salary.data
        employee.status = form.status.data
        
        db.session.commit()
        flash(f'Employee {employee.full_name} updated successfully!', 'success')
        return redirect(url_for('employees.view', id=employee.id))

    return render_template('employees/add_edit.html', form=form, title=f'Edit {employee.full_name}', is_edit=True, employee=employee)

@employees_bp.route('/delete/<int:id>', methods=['POST'])
@employees_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete(id):
    employee = Employee.query.get_or_404(id)
    name = employee.full_name
    db.session.delete(employee)
    db.session.commit()
    flash(f'Employee {name} deleted successfully.', 'info')
    return redirect(url_for('employees.index'))
