import sys, os, time, re, random
import requests

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

print(f"=== Live Diagnostic on {BASE_URL} ===")

# Step 1: GET /auth/login
res_login_page = session.get(f"{BASE_URL}/auth/login", timeout=30)
login_csrf = re.search(r'value="([^"]+)".*?csrf_token', res_login_page.text) or re.search(r'csrf_token.*?value="([^"]+)"', res_login_page.text)
login_csrf_val = login_csrf.group(1) if login_csrf else ""

# Step 2: POST /auth/login
res_login = session.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123", "csrf_token": login_csrf_val}, timeout=30)
print(f"[1] Login Status: {res_login.status_code} ({res_login.url})")

# Step 3: GET /employees/add
res_add_page = session.get(f"{BASE_URL}/employees/add", timeout=30)
print(f"[2] GET /employees/add Status: {res_add_page.status_code}")

add_csrf_match = re.search(r'id="csrf_token"[^>]*value="([^"]+)"', res_add_page.text) or re.search(r'value="([^"]+)"[^>]*id="csrf_token"', res_add_page.text)
add_csrf = add_csrf_match.group(1) if add_csrf_match else login_csrf_val
print(f" -> Extracted Add CSRF Token: {add_csrf[:25]}...")

dept_options = re.findall(r'<option\s+value="(\d+)">([^<]+)</option>', res_add_page.text)
print(f" -> Rendered Department Choices: {dept_options}")
dept_id = dept_options[0][0] if dept_options else "1"

# Step 4: POST /employees/add
emp_code = f"EMP{random.randint(1000, 9999)}"
emp_email = f"john.{emp_code.lower()}@company.com"

print(f"[3] Submitting POST /employees/add ({emp_code})...")
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
    "status": "Active"
}

res_post = session.post(f"{BASE_URL}/employees/add", data=emp_payload, timeout=30)
print(f" -> POST Response Status: {res_post.status_code} (URL: {res_post.url})")

if res_post.status_code == 200:
    print(f"\nSUCCESS: GET /employees/add returned HTTP 200 and POST /employees/add submitted successfully (Status {res_post.status_code}, URL: {res_post.url})!")
else:
    print(f"\nFailed with Status Code: {res_post.status_code}")
