import requests, re, random

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

r1 = session.get("https://employee-management-system-bv3y.onrender.com/auth/login")
csrf1 = re.search(r'name="csrf_token".*?value="([^"]+)"', r1.text).group(1)

r2 = session.post("https://employee-management-system-bv3y.onrender.com/auth/login", data={"username": "admin", "password": "admin123", "csrf_token": csrf1})
print("Login status:", r2.status_code)

r3 = session.get("https://employee-management-system-bv3y.onrender.com/employees/add")
print("GET /employees/add status:", r3.status_code)
csrf2 = re.search(r'name="csrf_token".*?value="([^"]+)"', r3.text).group(1)

emp_code = f"EMP{random.randint(1000, 9999)}"
payload = {
    "csrf_token": csrf2,
    "employee_id": emp_code,
    "first_name": "Test",
    "last_name": "User",
    "email": f"test.{emp_code.lower()}@domain.com",
    "phone": "+1 555-0199",
    "gender": "Male",
    "department_id": "1",
    "designation": "Developer",
    "joining_date": "2024-01-15",
    "salary": "85000",
    "status": "Active",
    "submit": "Save Employee"
}

r4 = session.post("https://employee-management-system-bv3y.onrender.com/employees/add", data=payload, allow_redirects=False)
print("POST status (no redirect):", r4.status_code)
print("Headers:", r4.headers)
if r4.status_code == 500:
    print("Full Body:\n", r4.text)
