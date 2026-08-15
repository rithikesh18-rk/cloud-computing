from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.profile import profile_bp
from app.profile.forms import ProfileUpdateForm, ChangePasswordForm
from app.models import safe_commit
from app.extensions import db
from app.utils import save_profile_picture

@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    emp = current_user.employee
    profile_form = ProfileUpdateForm()
    password_form = ChangePasswordForm()

    # Pre-populate profile form for GET requests
    if request.method == 'GET' and emp:
        profile_form.first_name.data = emp.first_name
        profile_form.last_name.data = emp.last_name
        profile_form.phone.data = emp.phone
        profile_form.address.data = emp.address
        profile_form.city.data = emp.city
        profile_form.state.data = emp.state
        profile_form.country.data = emp.country
        profile_form.pincode.data = emp.pincode

    # Profile details update
    if 'submit_profile' in request.form or (profile_form.validate_on_submit() and not password_form.is_submitted()):
        if emp:
            emp.first_name = profile_form.first_name.data.strip() if profile_form.first_name.data else emp.first_name
            emp.last_name = profile_form.last_name.data.strip() if profile_form.last_name.data else emp.last_name
            emp.phone = profile_form.phone.data.strip() if profile_form.phone.data else None
            emp.address = profile_form.address.data.strip() if profile_form.address.data else None
            emp.city = profile_form.city.data.strip() if profile_form.city.data else None
            emp.state = profile_form.state.data.strip() if profile_form.state.data else None
            emp.country = profile_form.country.data.strip() if profile_form.country.data else None
            emp.pincode = profile_form.pincode.data.strip() if profile_form.pincode.data else None

            if profile_form.profile_image.data:
                picture_file = save_profile_picture(profile_form.profile_image.data)
                emp.profile_image = picture_file

            success, error_msg = safe_commit()
            if success:
                flash('Your profile details have been updated!', 'success')
                return redirect(url_for('profile.index'))
            else:
                flash(f'Failed to update profile: {error_msg}', 'danger')
        else:
            flash('No associated employee profile found to update.', 'warning')

    # Password change
    if 'submit_password' in request.form or password_form.validate_on_submit():
        if not password_form.old_password.data or not current_user.check_password(password_form.old_password.data):
            flash('Incorrect current password.', 'danger')
        else:
            current_user.set_password(password_form.new_password.data)
            success, error_msg = safe_commit()
            if success:
                flash('Your password has been changed successfully!', 'success')
                return redirect(url_for('profile.index'))
            else:
                flash(f'Failed to change password: {error_msg}', 'danger')

    return render_template(
        'profile/index.html',
        profile_form=profile_form,
        password_form=password_form,
        employee=emp
    )

