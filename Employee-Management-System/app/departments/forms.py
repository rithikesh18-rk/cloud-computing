from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, ValidationError
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
        if department_code.data != self.original_code:
            dept = Department.query.filter_by(department_code=department_code.data).first()
            if dept:
                raise ValidationError('Department code already exists.')
