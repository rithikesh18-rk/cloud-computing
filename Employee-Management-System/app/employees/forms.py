from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, ValidationError
from sqlalchemy import func
from app.models import Employee, Department
from datetime import date, datetime

class SafeDateField(DateField):
    """Subclass of DateField that safely handles str vs date objects and multiple date formats without raising exceptions."""
    def __init__(self, label=None, validators=None, format='%Y-%m-%d', **kwargs):
        super(SafeDateField, self).__init__(label, validators, format=format, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = ' '.join(valuelist).strip()
            if not date_str:
                self.data = None
                return
            for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d'):
                try:
                    self.data = datetime.strptime(date_str, fmt).date()
                    return
                except ValueError:
                    pass
            self.data = None

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        if self.data:
            if isinstance(self.data, (date, datetime)):
                return self.data.strftime('%Y-%m-%d')
            return str(self.data)
        return ''


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
    ], validate_choice=False, validators=[Optional()])
    date_of_birth = SafeDateField('Date of Birth', validators=[Optional()])
    address = TextAreaField('Address', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    state = StringField('State', validators=[Optional()])
    country = StringField('Country', validators=[Optional()])
    pincode = StringField('Pincode', validators=[Optional()])
    
    department_id = SelectField('Department', coerce=safe_coerce, validate_choice=False, validators=[Optional()])
    designation = StringField('Designation / Job Title *', validators=[DataRequired()])
    joining_date = SafeDateField('Joining Date *', validators=[DataRequired()])

    salary = FloatField('Annual Salary ($) *', validators=[DataRequired()])
    status = SelectField('Employment Status *', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive')
    ], default='Active', validate_choice=False, validators=[DataRequired()])
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
        if employee_id.data and isinstance(employee_id.data, str):
            code = employee_id.data.strip().upper()
            orig = self.original_id.strip().upper() if self.original_id else None
            if code != orig:
                try:
                    emp = Employee.query.filter(func.upper(Employee.employee_id) == code).first()
                    if emp:
                        raise ValidationError('Employee ID already exists.')
                except Exception:
                    pass

    def validate_email(self, email):
        if email.data and isinstance(email.data, str):
            email_val = email.data.strip().lower()
            orig = self.original_email.strip().lower() if self.original_email else None
            if email_val != orig:
                try:
                    emp = Employee.query.filter(func.lower(Employee.email) == email_val).first()
                    if emp:
                        raise ValidationError('An employee with this email already exists.')
                except Exception:
                    pass

    def validate_salary(self, salary):
        if salary.data is not None and isinstance(salary.data, (int, float)) and salary.data < 0:
            raise ValidationError('Salary cannot be negative.')

    def validate_joining_date(self, joining_date):
        if joining_date.data and isinstance(joining_date.data, date) and joining_date.data > date.today():
            raise ValidationError('Joining date cannot be in the future.')

