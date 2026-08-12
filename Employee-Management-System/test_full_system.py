"""
Complete Employee Management System Verification Suite (Modules 3-13)
Tests all routes, CRUD operations, relationships, role-based authorization, and properties.
"""
from datetime import date, time, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Department, Employee, Attendance, Leave, init_database

def test_full_system():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        print("1. Initializing clean database...")
        db.drop_all()
        init_database(app)

        # Verify Admin User
        admin = User.query.filter_by(username='admin').first()
        assert admin is not None, "Admin user creation failed!"
        assert admin.check_password('admin123'), "Admin password verification failed!"
        assert admin.is_admin is True, "Admin role check failed!"
        print(f" -> Default Admin verified: {admin}")

        # 2. Test Department CRUD
        print("2. Testing Department CRUD...")
        eng_dept = Department(department_name='Engineering & Tech', department_code='ENG', description='Software development')
        hr_dept = Department(department_name='Human Resources', department_code='HR', description='People operations')
        db.session.add_all([eng_dept, hr_dept])
        db.session.commit()
        assert Department.query.count() == 2, "Department insertion failed!"
        print(f" -> Departments created: {[d.department_name for d in Department.query.all()]}")

        # 3. Test Employee CRUD
        print("3. Testing Employee CRUD...")
        emp1 = Employee(
            employee_id='EMP101',
            first_name='Rachel',
            last_name='Green',
            email='rachel.green@company.com',
            phone='+1 555-1001',
            gender='Female',
            date_of_birth=date(1993, 5, 5),
            designation='Lead Frontend Engineer',
            joining_date=date(2023, 2, 1),
            salary=92000.00,
            status='Active',
            department=eng_dept
        )
        emp2 = Employee(
            employee_id='EMP102',
            first_name='Ross',
            last_name='Geller',
            email='ross.geller@company.com',
            phone='+1 555-1002',
            gender='Male',
            date_of_birth=date(1990, 10, 18),
            designation='HR Specialist',
            joining_date=date(2022, 11, 15),
            salary=80000.00,
            status='Active',
            department=hr_dept
        )
        db.session.add_all([emp1, emp2])
        db.session.commit()
        
        assert emp1.full_name == "Rachel Green"
        assert eng_dept.employee_count == 1
        assert hr_dept.employee_count == 1
        print(f" -> Employees created: {emp1.full_name} ({emp1.employee_id}), {emp2.full_name} ({emp2.employee_id})")

        # 4. Test Employee User Account
        print("4. Testing Employee User Account & Linkage...")
        emp_user = User(username='rachel', email='rachel.green@company.com', role='Employee')
        emp_user.set_password('rachel123')
        db.session.add(emp_user)
        db.session.commit()
        
        assert emp_user.employee.id == emp1.id, "User to Employee linkage failed!"
        print(f" -> Employee account linked successfully: {emp_user} -> {emp_user.employee.full_name}")

        # 5. Test Attendance Management
        print("5. Testing Attendance Management...")
        att1 = Attendance(
            employee=emp1,
            attendance_date=date.today(),
            check_in=time(9, 0, 0),
            check_out=time(17, 30, 0),
            status='Present',
            remarks='On time'
        )
        att2 = Attendance(
            employee=emp1,
            attendance_date=date.today() - timedelta(days=1),
            check_in=time(9, 30, 0),
            check_out=time(17, 30, 0),
            status='Late',
            remarks='Traffic delay'
        )
        db.session.add_all([att1, att2])
        db.session.commit()

        assert att1.worked_hours == 8.5
        assert emp1.attendance_percentage == 100.0
        print(f" -> Attendance records logged. Worked hours: {att1.worked_hours}h. Attendance rate: {emp1.attendance_percentage}%")

        # 6. Test Leave Management
        print("6. Testing Leave Management...")
        leave_app = Leave(
            employee=emp1,
            leave_type='Casual Leave',
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 12),
            reason='Family event',
            status='Pending'
        )
        db.session.add(leave_app)
        db.session.commit()

        assert leave_app.total_days == 3
        assert emp1.pending_leaves_count == 1
        print(f" -> Leave applied: {leave_app.leave_type} ({leave_app.total_days} days). Status: {leave_app.status}")

        # Approve Leave
        leave_app.status = 'Approved'
        db.session.commit()
        assert emp1.approved_leaves_count == 1
        print(f" -> Leave approved successfully. Approved count: {emp1.approved_leaves_count}")

        # 7. Test Route & App Endpoints via Flask Test Client
        print("7. Testing Endpoints via Flask Test Client...")
        client = app.test_client()

        # Login test
        res_login = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        assert res_login.status_code == 200
        print(" -> Admin login request successful.")

        # Test Dashboard Endpoint
        res_dash = client.get('/dashboard')
        assert res_dash.status_code == 200, f"Dashboard returned status {res_dash.status_code}"
        print(" -> Dashboard route accessed successfully.")

        # Test Departments Endpoint
        res_depts = client.get('/departments/')
        assert res_depts.status_code == 200, f"Departments returned status {res_depts.status_code}"
        print(" -> Departments route accessed successfully.")

        # Test Employees Endpoint
        res_emps = client.get('/employees/')
        assert res_emps.status_code == 200, f"Employees returned status {res_emps.status_code}"
        print(" -> Employees directory accessed successfully.")

        # Test Attendance Endpoint
        res_att = client.get('/attendance/')
        assert res_att.status_code == 200, f"Attendance returned status {res_att.status_code}"
        print(" -> Attendance route accessed successfully.")

        # Test Leave Endpoint
        res_leave = client.get('/leave/')
        assert res_leave.status_code == 200, f"Leave returned status {res_leave.status_code}"
        print(" -> Leave route accessed successfully.")

        # Test Profile Endpoint
        res_prof = client.get('/profile/')
        assert res_prof.status_code == 200, f"Profile returned status {res_prof.status_code}"
        print(" -> Profile route accessed successfully.")

        print("\n==================================================")
        print("  ALL SYSTEM MODULES (3-13) VERIFIED SUCCESSFULLY! ")
        print("==================================================")

if __name__ == '__main__':
    test_full_system()
