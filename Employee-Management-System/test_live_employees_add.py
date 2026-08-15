import sys, os, time, re, random
import requests

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

res_login_page = session.get(f"{BASE_URL}/auth/login", timeout=30)
login_html = res_login_page.text

csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', login_html, re.DOTALL) or re.search(r'value="([^"]+)".*?name="csrf_token"', login_html, re.DOTALL)
csrf_token = csrf_match.group(1) if csrf_match else None

login_payload = {"username": "admin", "password": "admin123"}
if csrf_token:
    login_payload["csrf_token"] = csrf_token

session.post(f"{BASE_URL}/auth/login", data=login_payload, timeout=30)

res_add_page = session.get(f"{BASE_URL}/employees/add", timeout=30)
add_html = res_add_page.text

add_csrf_match = re.search(r'name="csrf_token".*?value="([^"]+)"', add_html, re.DOTALL) or re.search(r'value="([^"]+)".*?name="csrf_token"', add_html, re.DOTALL)
add_csrf = add_csrf_match.group(1) if add_csrf_match else csrf_token

dept_options = re.findall(r'<option\s+value="(\d+)">([^<]+)</option>', add_html)
dept_id = dept_options[0][0] if dept_options else "1"

emp_code = f"EMP{random.randint(1000, 9999)}"
emp_email = f"john.{emp_code.lower()}@company.com"

emp_payload = {
    "csrf_token": add_csrf,
    "employee_id": emp_code,
    "first_name": "John",
    "last_name": "Doe",
    "email": emp_email,
    "phone": "+1 555-0199",
    "gender": "Male",
    "department_id": dept_id,
    "designation": "Software Engineer",
    "joining_date": "2024-01-15",
    "salary": "95000",
    "status": "Active",
    "submit": "Save Employee"
}

res_add_post = session.post(f"{BASE_URL}/employees/add", data=emp_payload, timeout=30)
print(f"POST /employees/add Status: {res_add_post.status_code}")
pres = re.findall(r'<pre.*?>(.*?)</pre>', res_add_post.text, re.DOTALL)
print("Extracted pre blocks:\n", pres)
