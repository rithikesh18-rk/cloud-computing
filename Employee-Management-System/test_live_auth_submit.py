import sys, os, time, re
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

# Set up cookie jar for session tracking across redirect
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print(f"=== Testing Live POST /auth/login Authentication against {BASE_URL} ===")

# Step 1: GET /auth/login to fetch page & CSRF token
print("[1] Fetching login page & CSRF token...")
start_t = time.time()
req_get = urllib.request.Request(f"{BASE_URL}/auth/login", headers={"User-Agent": "Mozilla/5.0"})
res_get = opener.open(req_get, timeout=30)
get_latency = time.time() - start_t
get_html = res_get.read().decode('utf-8', errors='ignore')

# Extract CSRF token
match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', get_html)
if not match:
    match = re.search(r'value="([^"]+)"\s+id="csrf_token"', get_html)
csrf_token = match.group(1) if match else None

print(f" -> GET /auth/login status: {res_get.getcode()} ({get_latency:.2f}s)")
print(f" -> CSRF Token extracted: {csrf_token}")

# Step 2: POST /auth/login with admin / admin123
print("\n[2] Submitting POST /auth/login with credentials (admin / admin123)...")
post_data = {
    "username": "admin",
    "password": "admin123"
}
if csrf_token:
    post_data["csrf_token"] = csrf_token

encoded_post = urllib.parse.urlencode(post_data).encode('utf-8')
start_t = time.time()
req_post = urllib.request.Request(f"{BASE_URL}/auth/login", data=encoded_post, headers={
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
})

res_post = opener.open(req_post, timeout=30)
post_latency = time.time() - start_t
post_status = res_post.getcode()
final_url = res_post.geturl()
post_html = res_post.read().decode('utf-8', errors='ignore')

print(f" -> POST /auth/login status: {post_status} ({post_latency:.2f}s)")
print(f" -> Redirected URL: {final_url}")
print(f" -> Session cookies stored: {[c.name for c in cookie_jar]}")

print("\n=== DASHBOARD HTML PAYLOAD SAMPLE ===")
print(post_html[:600])

if post_status == 200 and ("dashboard" in final_url or "Workforce Dashboard" in post_html or "Welcome back" in post_html):
    print("\nSUCCESS: Live authentication succeeded with HTTP 200 and redirected to Dashboard!")
else:
    print(f"\nWARNING: Unexpected response status {post_status} or URL {final_url}")
