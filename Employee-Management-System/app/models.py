from datetime import datetime, date, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from sqlalchemy.orm import validates
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.extensions import db, login_manager

# ==============================================================================
# 1. USER MODEL
# ==============================================================================
class User(UserMixin, db.Model):
    """
    User model for authentication and system access.
    Supports role-based access control (Admin or Employee).
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Admin')  # Admin or Employee
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """Hashes and stores the user password using Werkzeug."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies plain text password against stored hash."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'Admin'

    @property
    def employee(self):
        """Finds associated Employee profile by matching email (case-insensitive)."""
        if not self.email:
            return None
        return Employee.query.filter(func.lower(Employee.email) == func.lower(self.email.strip())).first()

    def __repr__(self):
        return f'<User {self.username} (Role: {self.role})>'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback."""
    return User.query.get(int(user_id))


# ==============================================================================
# 2. DEPARTMENT MODEL
# ==============================================================================
class Department(db.Model):
    """
    Department model representing company departments.
    Has a one-to-many relationship with Employee.
    """
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(100), nullable=False)
    department_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: One Department -> Many Employees
    employees = db.relationship('Employee', backref='department', lazy=True)

    @property
    def employee_count(self):
        """Calculates and returns total employees in this department."""
        return len(self.employees)

    def __str__(self):
        return self.department_name

    def __repr__(self):
        return f'<Department {self.department_code} - {self.department_name}>'


# ==============================================================================
# 3. EMPLOYEE MODEL
# ==============================================================================
class Employee(db.Model):
    """
    Employee model representing individual workforce members.
    Foreign key relationship to Department.
    One-to-many relationship with Attendance and Leave records.
    """
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other
    date_of_birth = db.Column(db.Date, nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    designation = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Float, nullable=False, default=0.0)
    profile_image = db.Column(db.String(120), nullable=False, default='default.jpg')
    status = db.Column(db.String(20), nullable=False, default='Active')  # Active / Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Key: Belongs to Department
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    # Relationships: One Employee -> Many Attendances & Leaves
    attendances = db.relationship('Attendance', backref='employee', lazy=True, cascade='all, delete-orphan')
    leaves = db.relationship('Leave', backref='employee', lazy=True, cascade='all, delete-orphan')

    @property
    def full_name(self):
        """Returns the full name of the employee."""
        return f"{self.first_name} {self.last_name}"

    # Aliases for backwards compatibility
    @property
    def employee_code(self):
        return self.employee_id

    @employee_code.setter
    def employee_code(self, value):
        self.employee_id = value

    @property
    def position(self):
        return self.designation

    @position.setter
    def position(self, value):
        self.designation = value

    @property
    def hire_date(self):
        return self.joining_date

    @hire_date.setter
    def hire_date(self, value):
        self.joining_date = value

    @property
    def attendance_percentage(self):
        """Calculates attendance percentage."""
        total = len(self.attendances)
        if total == 0:
            return 100.0
        present = sum(1 for a in self.attendances if a.status in ['Present', 'Late'])
        half_days = sum(0.5 for a in self.attendances if a.status == 'Half Day')
        return round(((present + half_days) / total) * 100.0, 1)

    @property
    def pending_leaves_count(self):
        return sum(1 for l in self.leaves if l.status == 'Pending')

    @property
    def approved_leaves_count(self):
        return sum(1 for l in self.leaves if l.status == 'Approved')

    # Validations
    @validates('salary')
    def validate_salary(self, key, value):
        if value is not None and value < 0:
            raise ValueError('Salary cannot be negative.')
        return value

    @validates('joining_date')
    def validate_joining_date(self, key, value):
        if value is not None:
            check_val = value
            if isinstance(value, str):
                check_val = datetime.strptime(value, '%Y-%m-%d').date()
            if check_val > date.today():
                raise ValueError('Joining date cannot be in the future.')
        return value

    def __repr__(self):
        return f'<Employee {self.employee_id} - {self.full_name}>'


# ==============================================================================
# 4. ATTENDANCE MODEL
# ==============================================================================
class Attendance(db.Model):
    """
    Attendance model tracking daily employee check-ins and check-outs.
    Foreign key relationship to Employee.
    """
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=date.today)
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Present')  # Present, Absent, Half Day, Late
    remarks = db.Column(db.String(255), nullable=True)

    @property
    def worked_hours(self):
        """Calculates total hours worked based on check_in and check_out times."""
        if self.check_in and self.check_out:
            dt_check_in = datetime.combine(date.today(), self.check_in)
            dt_check_out = datetime.combine(date.today(), self.check_out)
            if dt_check_out >= dt_check_in:
                duration = dt_check_out - dt_check_in
            else:
                duration = (dt_check_out + timedelta(days=1)) - dt_check_in
            return round(duration.total_seconds() / 3600.0, 2)
        return 0.0

    def __repr__(self):
        return f'<Attendance Employee #{self.employee_id} on {self.attendance_date}>'


# ==============================================================================
# 5. LEAVE MODEL
# ==============================================================================
class Leave(db.Model):
    """
    Leave model representing employee leave applications and status.
    Foreign key relationship to Employee.
    """
    __tablename__ = 'leaves'

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    leave_type = db.Column(db.String(50), nullable=False)  # Casual Leave, Sick Leave, Earned Leave
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # Pending, Approved, Rejected
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def total_days(self):
        """Calculates total calendar days for the leave period."""
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days
            return max(0, delta + 1)
        return 0

    def __repr__(self):
        return f'<Leave Employee #{self.employee_id} ({self.leave_type}: {self.status})>'


# ==============================================================================
# 7. DATABASE INITIALIZATION & TRANSACTION UTILITIES
# ==============================================================================
def init_database(app=None):
    """
    Automatically creates all database tables if they do not exist
    and seeds the default Admin account if missing.
    """
    def _do_init():
        db.create_all()

        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                role='Admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            try:
                db.session.commit()
                print(" -> [init_database] Default Admin account created: username='admin', password='admin123'")
            except IntegrityError as e:
                db.session.rollback()
                print(f" -> [init_database] Warning: Admin creation failed: {e}")

    if app:
        with app.app_context():
            _do_init()
    else:
        _do_init()


def safe_commit():
    """Helper to commit transactions safely with automatic rollback on error."""
    try:
        db.session.commit()
        return True, None
    except IntegrityError as e:
        db.session.rollback()
        return False, f"Database Integrity Error: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, f"Database Error: {str(e)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Unexpected Error: {str(e)}"
