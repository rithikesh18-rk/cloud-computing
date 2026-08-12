from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TimeField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from app.models import Employee
from datetime import date

class AttendanceForm(FlaskForm):
    employee_id = SelectField('Employee', coerce=int, validators=[DataRequired()])
    attendance_date = DateField('Date', default=date.today, validators=[DataRequired()])
    check_in = TimeField('Check In Time', validators=[Optional()])
    check_out = TimeField('Check Out Time', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Half Day', 'Half Day'),
        ('Late', 'Late')
    ], validators=[DataRequired()])
    remarks = StringField('Remarks / Notes', validators=[Optional()])
    submit = SubmitField('Save Attendance Record')

    def set_employee_choices(self):
        employees = Employee.query.order_by(Employee.first_name.asc()).all()
        self.employee_id.choices = [(e.id, f"{e.full_name} ({e.employee_id})") for e in employees]
