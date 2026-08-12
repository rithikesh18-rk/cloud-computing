from functools import wraps
from flask import session, redirect, url_for, flash, request
from models.user import User
from models.settings import CollegeSettings

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to perform this action.', 'warning')
                return redirect(url_for('auth.login'))
            user_role = session.get('user_role')
            if user_role not in roles:
                flash('Access Denied: You do not have permission to view this resource.', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('admin')(f)

def faculty_or_admin_required(f):
    return role_required('admin', 'faculty')(f)

def student_required(f):
    return role_required('student')(f)

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def allowed_file(filename, allowed_extensions={'png', 'jpg', 'jpeg', 'gif', 'svg'}):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
