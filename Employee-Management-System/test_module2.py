"""
Module 2 Database Models Verification Test
Tests Department, Employee, Attendance, Leave models, relationships, validations, and properties.
"""
from datetime import date, time
from app import create_app
from app.extensions import db
from app.models import User, Department, Employee, Attendance, Leave, init_database, safe_commit

def run_tests():
    app = create_app()
    with app.app_context():
        print("1. Re-creating database schema...")
        db.drop_all()  # Ensure clean schema for Module 2 models
        init_database(app)

        print("2. Testing Department creation...")
        dept = Department(
            department_name='Test Software Engineering',
            department_code='TEST_ENG',
            description='Department for testing Module 2'
        )
        db.session.add(dept)
        db.session.commit()
        print(f" -> Department created: {dept} (ID: {dept.id})")

        print("3. Testing Employee creation & Relationship to Department...")
        emp = Employee(
            employee_id='TEST_EMP001',
            first_name='Alex',
            last_name='Turner',
            email='alex.turner.test@example.com',
            phone='+1 555-9999',
            gender='Male',
            date_of_birth=date(1995, 4, 12),
            designation='Senior Developer',
            joining_date=date(2023, 1, 15),
            salary=95000.00,
            status='Active',
            department=dept
        )
        db.session.add(emp)
        db.session.commit()
        
        print(f" -> Employee created: {emp} (Full Name: {emp.full_name})")
        assert emp.full_name == "Alex Turner", "Full name property check failed!"
        assert emp.department.department_code == "TEST_ENG", "Department relationship check failed!"
        assert emp in dept.employees, "Department.employees list check failed!"
        assert dept.employee_count >= 1, "Department.employee_count property failed!"
        print(f" -> Department employee_count property: {dept.employee_count}")

        print("4. Testing Attendance model & worked_hours property...")
        att = Attendance(
            employee=emp,
            attendance_date=date.today(),
            check_in=time(9, 0, 0),
            check_out=time(17, 30, 0),
            status='Present',
            remarks='On time'
        )
        db.session.add(att)
        db.session.commit()
        print(f" -> Attendance record created: {att}")
        print(f" -> Worked hours: {att.worked_hours} hours")
        assert att.worked_hours == 8.5, f"Expected 8.5 worked hours, got {att.worked_hours}"
        assert att in emp.attendances, "Employee.attendances relationship check failed!"

        print("5. Testing Leave model & total_days property...")
        leave_rec = Leave(
            employee=emp,
            leave_type='Casual Leave',
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 5),
            reason='Personal vacation',
            status='Pending'
        )
        db.session.add(leave_rec)
        db.session.commit()
        print(f" -> Leave record created: {leave_rec}")
        print(f" -> Total leave days: {leave_rec.total_days} days")
        assert leave_rec.total_days == 5, f"Expected 5 leave days, got {leave_rec.total_days}"
        assert leave_rec in emp.leaves, "Employee.leaves relationship check failed!"

        print("6. Testing Salary & Joining Date Validations...")
        try:
            invalid_emp = Employee(
                employee_id='INVALID_SAL',
                first_name='Test',
                last_name='User',
                email='invalid_sal@example.com',
                designation='Tester',
                joining_date=date(2023, 1, 1),
                salary=-5000.00
            )
            print(" -> ERROR: Negative salary was not caught by validation!")
            assert False, "Negative salary should have raised ValueError"
        except ValueError as ve:
            print(f" -> Passed negative salary validation: {ve}")

        try:
            future_emp = Employee(
                employee_id='FUTURE_JOIN',
                first_name='Future',
                last_name='User',
                email='future_join@example.com',
                designation='Tester',
                joining_date=date(2099, 1, 1),
                salary=50000.00
            )
            print(" -> ERROR: Future joining date was not caught by validation!")
            assert False, "Future joining date should have raised ValueError"
        except ValueError as ve:
            print(f" -> Passed future joining date validation: {ve}")

        print("7. Testing Error Handling & Transaction Rollback...")
        dup_user = User(username='admin', email='duplicate_admin@example.com')
        dup_user.set_password('123456')
        db.session.add(dup_user)
        success, error_msg = safe_commit()
        assert not success, "Duplicate username should fail safe_commit!"
        print(f" -> safe_commit correctly handled duplicate username error: {error_msg}")

        print("\n==================================================")
        print("  MODULE 2 DATABASE MODELS VERIFICATION PASSED!  ")
        print("==================================================")

if __name__ == '__main__':
    run_tests()
