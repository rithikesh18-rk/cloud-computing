from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, ValidationError
from sqlalchemy import func
from app.models import Employee, Department
from datetime import date

def safe_coerce(val):
    if val is None or val == '' or val == 'None' or val == '0':
        return 0
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

class EmployeeForm(FlaskForm):
    employee_id = StringField('Employee ID *', validators=[DataRequired()])
    first_name = StringField('First Name *', validators=[DataRequired()])
    last_name = StringField('Last Name *', validators=[DataRequired()])
    email = StringField('Email Address *', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    ], validators=[Optional()])
    date_of_birth = DateField('Date of Birth', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    pincode = StringField('Pincode', validators=[Optional()])
    
    department_id = SelectField('Department', coerce=safe_coerce, validators=[Optional()])
    designation = StringField('Designation / Job Title *', validators=[DataRequired()])
    joining_date = DateField('Joining Date *', validators=[DataRequired()])
    salary = FloatField('Annual Salary ($) *', validators=[DataRequired()])
    status = SelectField('Employment Status *', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ], default='Active', validators=[DataRequired()])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only (.jpg, .png, .jpeg, .gif)')
    ])
    submit = SubmitField('Save Employee')

    def __init__(self, original_id=None, original_email=None, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
        self.original_email = original_email
        try:
            departments = Department.query.order_by(Department.department_name.asc()).all()
            self.department_id.choices = [(0, 'Select Department')] + [(d.id, d.department_name) for d in departments]
        except Exception:
            self.department_id.choices = [(0, 'Select Department')]


    def validate_employee_id(self, employee_id):
        if employee_id.data:
            code = employee_id.data.strip().upper()
            orig = self.original_id.strip().upper() if self.original_id else None
            if code != orig:
                emp = Employee.query.filter(func.upper(Employee.employee_id) == code).first()
                if emp:
                    raise ValidationError('Employee ID already exists.')

    def validate_email(self, email):
        if email.data:
            email_val = email.data.strip().lower()
            orig = self.original_email.strip().lower() if self.original_email else None
            if email_val != orig:
                emp = Employee.query.filter(func.lower(Employee.email) == email_val).first()
                if emp:
                    raise ValidationError('An employee with this email already exists.')

    def validate_salary(self, salary):
        if salary.data is not None and salary.data < 0:
            raise ValidationError('Salary cannot be negative.')

    def validate_joining_date(self, joining_date):
        if joining_date.data and joining_date.data > date.today():
            raise ValidationError('Joining date cannot be in the future.')
