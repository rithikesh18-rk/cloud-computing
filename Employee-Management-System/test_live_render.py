import sys, os, time, re
import urllib.request
import urllib.parse
import http.cookiejar

BASE_URL = "https://employee-management-system-bv3y.onrender.com"

# Set up cookie handler for persistent session management
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

results = []

def record(endpoint, status, latency, health, note=""):
    results.append({
        "endpoint": endpoint,
        "status": status,
        "latency": f"{latency:.2f}s",
        "health": health,
        "note": note
    })

print(f"=== Starting Live Diagnostic for {BASE_URL} ===")

# 1. Warm-Up & Reachability Check GET /
start_time = time.time()
try:
    req = urllib.request.Request(f"{BASE_URL}/", headers={"User-Agent": "Mozilla/5.0"})
    res = opener.open(req, timeout=90)
    latency = time.time() - start_time
    status = res.getcode()
    health = "Healthy" if status in [200, 302] else "Degraded"
    record("GET /", status, latency, health, f"Final URL: {res.geturl()}")
    print(f"[+] GET / -> {status} in {latency:.2f}s")
except urllib.error.HTTPError as e:
    latency = time.time() - start_time
    health = "Redirect/Auth" if e.code in [302, 401] else "Error"
    record("GET /", e.code, latency, health, f"HTTPError: {e.reason}")
    print(f"[!] GET / -> {e.code} in {latency:.2f}s")
except Exception as e:
    latency = time.time() - start_time
    record("GET /", "Fail", latency, "Unreachable", str(e))
    print(f"[!] GET / -> Exception: {e}")

# 2. GET /auth/login
start_time = time.time()
csrf_token = None
login_html = ""
try:
    req = urllib.request.Request(f"{BASE_URL}/auth/login", headers={"User-Agent": "Mozilla/5.0"})
    res = opener.open(req, timeout=30)
    latency = time.time() - start_time
    status = res.getcode()
    login_html = res.read().decode('utf-8', errors='ignore')
    
    # Extract CSRF token if present
    match = re.search(r'name="csrf_token"\s+type="hidden"\s+value="([^"]+)"', login_html)
    if not match:
        match = re.search(r'value="([^"]+)"\s+id="csrf_token"', login_html)
    if match:
        csrf_token = match.group(1)
        
    health = "Healthy" if status == 200 and ("login" in login_html.lower() or csrf_token) else "Degraded"
    record("GET /auth/login", status, latency, health, "CSRF Token Found" if csrf_token else "No CSRF Token")
    print(f"[+] GET /auth/login -> {status} in {latency:.2f}s (CSRF: {'Yes' if csrf_token else 'No'})")
except Exception as e:
    latency = time.time() - start_time
    record("GET /auth/login", getattr(e, 'code', 'Fail'), latency, "Error", str(e))
    print(f"[!] GET /auth/login -> {e}")

# 3. Static Asset Check (CSS/JS)
for asset in ["/static/css/style.css", "/static/js/main.js"]:
    start_time = time.time()
    try:
        req = urllib.request.Request(f"{BASE_URL}{asset}", headers={"User-Agent": "Mozilla/5.0"})
        res = opener.open(req, timeout=15)
        latency = time.time() - start_time
        status = res.getcode()
        health = "Healthy" if status == 200 else "404 Missing"
        record(f"GET {asset}", status, latency, health, "Static file loaded")
        print(f"[+] GET {asset} -> {status} in {latency:.2f}s")
    except Exception as e:
        latency = time.time() - start_time
        status = getattr(e, 'code', 'Fail')
        record(f"GET {asset}", status, latency, "404 Missing", str(e))
        print(f"[!] GET {asset} -> {status}")

# 4. POST /auth/login (Simulated Session)
start_time = time.time()
login_success = False
try:
    post_data = {"username": "admin", "password": "admin123"}
    if csrf_token:
        post_data["csrf_token"] = csrf_token
    encoded_data = urllib.parse.urlencode(post_data).encode('utf-8')
    
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=encoded_data, headers={
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    })
    res = opener.open(req, timeout=30)
    latency = time.time() - start_time
    status = res.getcode()
    final_url = res.geturl()
    
    login_success = ("dashboard" in final_url or status == 200)
    health = "Healthy" if login_success else "Login Failed"
    record("POST /auth/login", status, latency, health, f"Redirected to: {final_url}")
    print(f"[+] POST /auth/login -> {status} in {latency:.2f}s (Redirect: {final_url})")
except Exception as e:
    latency = time.time() - start_time
    record("POST /auth/login", getattr(e, 'code', 'Fail'), latency, "Failed", str(e))
    print(f"[!] POST /auth/login -> {e}")

# 5. Protected Endpoints Audit
protected_endpoints = [
    "/dashboard",
    "/employees/",
    "/departments/",
    "/attendance/",
    "/leave/"
]

for ep in protected_endpoints:
    start_time = time.time()
    try:
        req = urllib.request.Request(f"{BASE_URL}{ep}", headers={"User-Agent": "Mozilla/5.0"})
        res = opener.open(req, timeout=20)
        latency = time.time() - start_time
        status = res.getcode()
        content = res.read().decode('utf-8', errors='ignore')
        
        is_protected_access = (res.geturl().endswith(ep) or status == 200)
        health = "Healthy" if status == 200 else "Degraded"
        record(f"GET {ep}", status, latency, health, f"Loaded ({len(content)} bytes)")
        print(f"[+] GET {ep} -> {status} in {latency:.2f}s")
    except Exception as e:
        latency = time.time() - start_time
        status = getattr(e, 'code', 'Fail')
        health = "302 Redirect" if status == 302 else "Error"
        record(f"GET {ep}", status, latency, health, str(e))
        print(f"[!] GET {ep} -> {status}")

print("\n=== SUMMARY TABLE ===")
print(f"{'Endpoint':<25} | {'Status':<8} | {'Latency':<8} | {'Health':<12} | {'Notes'}")
print("-" * 75)
for r in results:
    print(f"{r['endpoint']:<25} | {str(r['status']):<8} | {r['latency']:<8} | {r['health']:<12} | {r['note']}")
