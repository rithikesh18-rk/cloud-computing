import sys, os, time, re, random
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print(f"=== Testing Live GET & POST /employees/add on {BASE_URL} ===")

# 1. Login as Admin
print("[1] Logging in as Admin...")
req_login_page = urllib.request.Request(f"{BASE_URL}/auth/login", headers={"User-Agent": "Mozilla/5.0"})
res_login_page = opener.open(req_login_page, timeout=30)
login_html = res_login_page.read().decode('utf-8', errors='ignore')

csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', login_html)
if not csrf_match:
    csrf_match = re.search(r'value="([^"]+)"\s+id="csrf_token"', login_html)
csrf_token = csrf_match.group(1) if csrf_match else None

login_data = {
    "username": "admin",
    "password": "admin123"
}
if csrf_token:
    login_data["csrf_token"] = csrf_token

req_login = urllib.request.Request(f"{BASE_URL}/auth/login", data=urllib.parse.urlencode(login_data).encode('utf-8'), headers={"User-Agent": "Mozilla/5.0"})
res_login = opener.open(req_login, timeout=30)
print(f" -> Admin Login status: {res_login.getcode()} (URL: {res_login.geturl()})")

# 2. GET /employees/add
print("\n[2] Fetching GET /employees/add form...")
req_add_page = urllib.request.Request(f"{BASE_URL}/employees/add", headers={"User-Agent": "Mozilla/5.0"})
start_t = time.time()
res_add_page = opener.open(req_add_page, timeout=30)
add_latency = time.time() - start_t
add_html = res_add_page.read().decode('utf-8', errors='ignore')

add_csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', add_html)
if not add_csrf_match:
    add_csrf_match = re.search(r'value="([^"]+)"\s+id="csrf_token"', add_html)
add_csrf_token = add_csrf_match.group(1) if add_csrf_match else csrf_token

print(f" -> GET /employees/add status: {res_add_page.getcode()} ({add_latency:.2f}s)")
print(f" -> Form Title in HTML: {'Add New Employee' in add_html or 'Employee' in add_html}")

# Extract Department option values from HTML
dept_options = re.findall(r'<option\s+value="(\d+)">([^<]+)</option>', add_html)
print(f" -> Department dropdown choices rendered in live HTML: {dept_options}")
dept_id_value = dept_options[0][0] if dept_options else "0"

# 3. POST /employees/add
emp_code = f"TEST{random.randint(1000, 9999)}"
emp_email = f"test.{emp_code.lower()}@company.com"

print(f"\n[3] Submitting POST /employees/add (ID: {emp_code}, Email: {emp_email})...")
new_emp_data = {
    "employee_id": emp_code,
    "first_name": "Diagnostic",
    "last_name": "Tester",
    "email": emp_email,
    "phone": "+1 555-9999",
    "gender": "Other",
    "department_id": dept_id_value,
    "designation": "Automation Engineer",
    "joining_date": "2024-01-15",
    "salary": "85000.00",
    "status": "Active"
}
if add_csrf_token:
    new_emp_data["csrf_token"] = add_csrf_token

start_t = time.time()
req_post_add = urllib.request.Request(f"{BASE_URL}/employees/add", data=urllib.parse.urlencode(new_emp_data).encode('utf-8'), headers={"User-Agent": "Mozilla/5.0"})
res_post_add = opener.open(req_post_add, timeout=30)
post_add_latency = time.time() - start_t
post_add_status = res_post_add.getcode()
final_url = res_post_add.geturl()

print(f" -> POST /employees/add status: {post_add_status} ({post_add_latency:.2f}s)")
print(f" -> Final URL: {final_url}")

if post_add_status == 200:
    print("\nSUCCESS: GET & POST /employees/add executed cleanly with HTTP 200 OK!")
else:
    print(f"\nWARNING: Unexpected status {post_add_status}")
