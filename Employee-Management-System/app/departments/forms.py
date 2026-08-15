from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from sqlalchemy import func
from app.models import Department

class DepartmentForm(FlaskForm):
    department_name = StringField('Department Name', validators=[DataRequired()])
    department_code = StringField('Department Code', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Save Department')

    def __init__(self, original_code=None, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        self.original_code = original_code

    def validate_department_code(self, department_code):
        if department_code.data:
            code = department_code.data.strip().upper()
            orig = self.original_code.strip().upper() if self.original_code else None
            if code != orig:
                dept = Department.query.filter(func.upper(Department.department_code) == code).first()
                if dept:
                    raise ValidationError('Department code already exists.')

