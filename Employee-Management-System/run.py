from app import create_app
from app.extensions import db
from app.models import User, Department, Employee, init_database
from datetime import date

app = create_app()

def seed_initial_data():
    with app.app_context():
        # Ensure database tables and default admin account exist
        init_database()

        # Create sample departments if none exist
        if Department.query.count() == 0:
            eng_dept = Department(department_name='Engineering', department_code='ENG', description='Software & Tech Development')
            hr_dept = Department(department_name='Human Resources', department_code='HR', description='People & Talent Management')
            fin_dept = Department(department_name='Finance', department_code='FIN', description='Accounting & Payroll')
            
            db.session.add_all([eng_dept, hr_dept, fin_dept])
            db.session.commit()
            print(" -> Seeded sample departments: Engineering, HR, Finance.")

        # Create sample employees if none exist
        if Employee.query.count() == 0:
            eng_dept = Department.query.filter_by(department_code='ENG').first()
            hr_dept = Department.query.filter_by(department_code='HR').first()
            fin_dept = Department.query.filter_by(department_code='FIN').first()

            sample_employees = [
                Employee(
                    employee_id='EMP001',
                    first_name='John',
                    last_name='Doe',
                    email='john.doe@company.com',
                    phone='+1 555-0101',
                    department=eng_dept,
                    designation='Software Engineer',
                    salary=95000.00,
                    joining_date=date(2023, 1, 15),
                    status='Active'
                ),
                Employee(
                    employee_id='EMP002',
                    first_name='Sarah',
                    last_name='Smith',
                    email='sarah.smith@company.com',
                    phone='+1 555-0102',
                    department=hr_dept,
                    designation='HR Manager',
                    salary=85000.00,
                    joining_date=date(2022, 6, 1),
                    status='Active'
                ),
                Employee(
                    employee_id='EMP003',
                    first_name='Michael',
                    last_name='Johnson',
                    email='michael.j@company.com',
                    phone='+1 555-0103',
                    department=fin_dept,
                    designation='Financial Analyst',
                    salary=78000.00,
                    joining_date=date(2024, 3, 10),
                    status='Active'
                )
            ]
            db.session.add_all(sample_employees)
            db.session.commit()
            print(" -> Seeded 3 sample employees.")

if __name__ == '__main__':
    seed_initial_data()
    print("Starting Flask application on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
