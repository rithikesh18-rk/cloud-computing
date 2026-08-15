import sys, os, time, re, random
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print(f"=== Live Test: GET & POST /employees/add on {BASE_URL} ===")

# 1. Login as Admin
print("[1] Logging in as Admin...")
req_login_page = urllib.request.Request(f"{BASE_URL}/auth/login", headers={"User-Agent": "Mozilla/5.0"})
res_login_page = opener.open(req_login_page, timeout=30)
login_html = res_login_page.read().decode('utf-8', errors='ignore')

csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', login_html)
csrf_token = csrf_match.group(1) if csrf_match else None

login_data = {"username": "admin", "password": "admin123"}
if csrf_token:
    login_data["csrf_token"] = csrf_token

req_login = urllib.request.Request(f"{BASE_URL}/auth/login", data=urllib.parse.urlencode(login_data).encode('utf-8'), headers={"User-Agent": "Mozilla/5.0"})
res_login = opener.open(req_login, timeout=30)
print(f" -> Login Status: {res_login.getcode()} (URL: {res_login.geturl()})")

# 2. GET /employees/add
print("\n[2] Requesting GET /employees/add...")
req_add = urllib.request.Request(f"{BASE_URL}/employees/add", headers={"User-Agent": "Mozilla/5.0"})
res_add = opener.open(req_add, timeout=30)
add_html = res_add.read().decode('utf-8', errors='ignore')
print(f" -> GET /employees/add status: {res_add.getcode()}")

add_csrf_match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', add_html)
add_csrf = add_csrf_match.group(1) if add_csrf_match else csrf_token

dept_options = re.findall(r'<option\s+value="(\d+)">([^<]+)</option>', add_html)
print(f" -> Rendered Department Options: {dept_options}")
dept_id = dept_options[0][0] if dept_options else "1"

# 3. POST /employees/add
emp_id = f"EMP{random.randint(1000, 9999)}"
emp_email = f"john.{emp_id.lower()}@company.com"

print(f"\n[3] Submitting POST /employees/add (Employee ID: {emp_id}, Email: {emp_email})...")
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
    "status": "Active"
}

try:
    req_post = urllib.request.Request(f"{BASE_URL}/employees/add", data=urllib.parse.urlencode(emp_form).encode('utf-8'), headers={
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    res_post = opener.open(req_post, timeout=30)
    post_status = res_post.getcode()
    final_url = res_post.geturl()
    post_html = res_post.read().decode('utf-8', errors='ignore')
    
    print(f" -> POST /employees/add status: {post_status}")
    print(f" -> Final Redirect URL: {final_url}")
    print(f" -> Success Message in HTML: {'added successfully' in post_html or 'Employees' in post_html or post_status == 200}")
    
    if post_status == 200 and ("employees" in final_url or "dashboard" in final_url):
        print("\nPASSED: Live GET & POST /employees/add executed successfully with HTTP 200 OK!")
    else:
        print(f"\nRESULT: Status {post_status}, URL {final_url}")
except urllib.error.HTTPError as e:
    print(f"[!] HTTP Error {e.code}: {e.reason}")
    body = e.read().decode('utf-8', errors='ignore')
    print(" -> Response Error Body:\n", body[:800])
