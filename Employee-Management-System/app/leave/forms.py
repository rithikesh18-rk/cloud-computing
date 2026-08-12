from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from datetime import date

class LeaveForm(FlaskForm):
    leave_type = SelectField('Leave Type', choices=[
        ('Casual Leave', 'Casual Leave'),
        ('Sick Leave', 'Sick Leave'),
        ('Earned Leave', 'Earned Leave'),
        ('Maternity/Paternity Leave', 'Maternity/Paternity Leave')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    reason = TextAreaField('Reason for Leave', validators=[DataRequired()])
    submit = SubmitField('Submit Leave Application')

    def validate_end_date(self, end_date):
        if self.start_date.data and end_date.data:
            if end_date.data < self.start_date.data:
                raise ValidationError('End date cannot be earlier than start date.')
