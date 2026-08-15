import sys, os, time, re, random
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar), NoRedirectHandler())

print(f"=== Live Diagnostic (No Redirect) on {BASE_URL} ===")

# Step 1: Login
req_login_page = urllib.request.Request(f"{BASE_URL}/auth/login", headers={"User-Agent": "Mozilla/5.0"})
res_login_page = opener.open(req_login_page, timeout=30)
login_html = res_login_page.read().decode('utf-8', errors='ignore')

csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', login_html)
csrf_token = csrf_match.group(1) if csrf_match else None

login_data = {"username": "admin", "password": "admin123"}
if csrf_token:
    login_data["csrf_token"] = csrf_token

req_login = urllib.request.Request(f"{BASE_URL}/auth/login", data=urllib.parse.urlencode(login_data).encode('utf-8'), headers={"User-Agent": "Mozilla/5.0"})
try:
    res_login = opener.open(req_login, timeout=30)
    print(f"[1] Login Response Code: {res_login.getcode()} (Location: {res_login.headers.get('Location')})")
except urllib.error.HTTPError as e:
    print(f"[1] Login Response Code: {e.code} (Location: {e.headers.get('Location')})")

# Step 2: GET /employees/add
req_add = urllib.request.Request(f"{BASE_URL}/employees/add", headers={"User-Agent": "Mozilla/5.0"})
res_add = opener.open(req_add, timeout=30)
add_html = res_add.read().decode('utf-8', errors='ignore')
print(f"[2] GET /employees/add Status: {res_add.getcode()}")

add_csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', add_html)
add_csrf = add_csrf_match.group(1) if add_csrf_match else csrf_token

dept_options = re.findall(r'<option\s+value="(\d+)">([^<]+)</option>', add_html)
print(f" -> Rendered Department Options: {dept_options}")
dept_id = dept_options[0][0] if dept_options else "1"

# Step 3: POST /employees/add
emp_id = f"EMP{random.randint(1000, 9999)}"
emp_email = f"john.{emp_id.lower()}@company.com"

print(f"\n[3] Submitting POST /employees/add ({emp_id})...")
emp_form = {
    "csrf_token": add_csrf,
    "employee_id": emp_id,
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

try:
    req_post = urllib.request.Request(f"{BASE_URL}/employees/add", data=urllib.parse.urlencode(emp_form).encode('utf-8'), headers={
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    res_post = opener.open(req_post, timeout=30)
    print(f" -> POST Response Code: {res_post.getcode()} (Location: {res_post.headers.get('Location')})")
except urllib.error.HTTPError as e:
    print(f" -> POST Response Code: {e.code} (Location: {e.headers.get('Location')})")
    body = e.read().decode('utf-8', errors='ignore')
    print(" -> Response Error Body:\n", body[:600])
