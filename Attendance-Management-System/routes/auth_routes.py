import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from models import db
from models.user import User
from models.settings import CollegeSettings
from utils.helpers import login_required, get_current_user, allowed_file
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both email address and password.', 'danger')
            return redirect(url_for('auth.login'))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['user_code'] = user.user_id_code
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            session['user_email'] = user.email

            flash(f'Welcome back, {user.full_name}!', 'success')

            if user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role in ['admin', 'faculty']:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email address or password. Please try again.', 'danger')

    settings = CollegeSettings.get_settings()
    return render_template('auth/login.html', settings=settings)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@login_required
def dashboard():
    role = session.get('user_role')
    if role == 'student':
        return redirect(url_for('student.dashboard'))
    else:
        return redirect(url_for('admin.dashboard'))

# --------------------------------------------------------------------------
# PROFILE & ACCOUNT MANAGEMENT (For Admin, Faculty, Student)
# --------------------------------------------------------------------------
@auth_bp.route('/profile')
@login_required
def profile():
    user = get_current_user()
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    user = get_current_user()
    email = request.form.get('email', '').strip().lower()
    phone_number = request.form.get('phone_number', '').strip()

    if not email:
        flash('Email address cannot be empty.', 'danger')
        return redirect(url_for('auth.profile'))

    existing = User.query.filter(User.email == email, User.id != user.id).first()
    if existing:
        flash('This email address is already in use by another account.', 'danger')
        return redirect(url_for('auth.profile'))

    user.email = email
    user.phone_number = phone_number
    session['user_email'] = email

    db.session.commit()
    flash('Profile details updated successfully.', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile/change_password', methods=['POST'])
@login_required
def change_password():
    user = get_current_user()
    current_password = request.form.get('current_password', '').strip()
    new_password = request.form.get('new_password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()

    if not user.check_password(current_password):
        flash('Incorrect current password.', 'danger')
        return redirect(url_for('auth.profile'))

    if not new_password or len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'danger')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('New password and confirmation do not match.', 'danger')
        return redirect(url_for('auth.profile'))

    user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully.', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    user = get_current_user()
    if 'profile_photo' in request.files:
        file = request.files['profile_photo']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = int(datetime.utcnow().timestamp())
            new_filename = f"avatar_{user.id}_{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)
            
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)
            user.profile_image = new_filename
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
            return redirect(url_for('auth.profile'))

    flash('Invalid image file. Supported formats: PNG, JPG, JPEG, GIF, SVG.', 'danger')
    return redirect(url_for('auth.profile'))
