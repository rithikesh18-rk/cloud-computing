# Employee Management System

A full-featured, enterprise-grade Flask HR management web application designed for managing employee lifecycles, department hierarchies, daily attendance tracking, and leave request workflows with visual analytics, case-insensitive validation, database transaction safety, dual MySQL/SQLite engine support, and cloud deployment configuration.

---

## 🌐 Live Demo

🚀 **Live Production Deployment:** [https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/)

---

## ✨ Core Features & Highlights

- **🔐 Multi-Role Authentication:** Role-based access control (Admin & Employee roles) powered by Flask-Login and Werkzeug password hashing.
- **👨‍💼 Employee Lifecycle Management:** Complete CRUD operations, job titles, department assignments, joining dates, and profile picture processing (Pillow thumbnail optimization).
- **🏢 Department Hierarchies:** Organize organizational structure with department codes, descriptions, and dynamic employee count metrics.
- **👤 Employee Profiles & Security:** Case-insensitive user account linkage, contact detail updates, and secure password changes.
- **📅 Daily Attendance Tracking:** Attendance logging (Present, Absent, Half Day, Late), worked hours calculations, percentage tracking, and duplicate prevention.
- **📝 Leave Request Workflow:** Streamlined leave applications, automatic day calculations, and Admin approval/rejection pipelines.
- **📊 Analytics & Visual Dashboard:** Real-time metrics cards, Chart.js department breakdowns, and recent workforce activity logs.
- **🛡️ Database Integrity & Transaction Safety:** Case-insensitive uniqueness validations for emails, IDs, and department codes with automatic rollback wrappers (`safe_commit`) preventing unhandled 500 server crashes.
- **⚡ Dual Database Support:** Production-ready MySQL support via PyMySQL with automatic connection pooling (`pool_pre_ping: True`, `pool_recycle: 280`) and SQLite fallback.

---

## 🛠️ Technology Stack

### Backend & Core
- **Python 3.11+**
- **Flask 3.0.3**
- **Flask-SQLAlchemy 3.1.1** (ORMs & Migrations)
- **Flask-Login 0.6.3** (Session & Authentication)
- **Flask-WTF 1.2.1 & WTForms 3.1.2** (CSRF & Form Validation)
- **PyMySQL 1.1.1 & Cryptography 43.0.0** (MySQL Driver & Protocol Encryption)
- **Pillow 10.x** (Profile Image Processing)

### Database Layer
- **MySQL 8.0+ / MariaDB** (Production Database Engine)
- **SQLite 3** (Local Development Fallback)

### Frontend
- **HTML5 & Vanilla CSS3**
- **Bootstrap 5.3.3**
- **JavaScript (ES6)**
- **Chart.js** (Dashboard Analytics)
- **FontAwesome 6** (Icons)

### Infrastructure & Deployment
- **Gunicorn 22.0.0** (WSGI Application Server)
- **Render** (`render.yaml`, `Procfile`, `runtime.txt`)

---

## 📁 Project Structure

```text
Employee-Management-System/
├── app/
│   ├── attendance/         # Attendance tracking blueprint, forms, and routes
│   ├── auth/               # Authentication, login, registration, decorators
│   ├── dashboard/          # Analytics dashboard blueprint
│   ├── departments/        # Department CRUD management blueprint
│   ├── employees/          # Employee directory & CRUD blueprint
│   ├── leave/              # Leave application & approval blueprint
│   ├── profile/            # User profile management blueprint
│   ├── static/             # Assets (CSS, JS, upload directories)
│   ├── templates/          # Jinja2 HTML templates & layout structure
│   ├── config.py           # Application configuration & MySQL/SQLite resolution
│   ├── extensions.py       # SQLAlchemy & LoginManager initialization + SQLite PRAGMA
│   ├── models.py           # Database models (User, Department, Employee, Attendance, Leave)
│   └── utils.py            # Image processing & file utilities
├── .env.example            # Environment variable template
├── Procfile                # Gunicorn process definition for Render
├── render.yaml             # Render deployment configuration
├── requirements.txt        # Python dependency manifest
├── runtime.txt             # Python runtime specification
├── run.py                  # Application entry point & seed initial data
├── test_full_system.py     # System verification test suite
├── test_module2.py         # Database model verification test suite
└── test_mysql_migration.py # MySQL DDL & fallback test suite
```

---

## ⚙️ Local Development & Setup

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/rithikesh18-rk/cloud-computing.git
cd "Employee-Management-System"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` or set environment variables:
```bash
# SQLite Fallback (Default when no URL is set)
python run.py

# Or MySQL Database Connection String
export DATABASE_URL="mysql+pymysql://root:password@localhost:3306/employee_management_db"
python run.py
```

---

## 🔑 Default Credentials

- **Admin Username:** `admin`
- **Admin Password:** `admin123`

---

## 🧪 Testing & Quality Assurance

Run the automated verification test suites to confirm database model integrity, case-insensitivity, and endpoint routes:

```bash
# Test database models & relationship validations
python test_module2.py

# Test full application routes, permissions, and CRUD operations
python test_full_system.py

# Test MySQL configuration, URI transformation, and DDL schema compilation
python test_mysql_migration.py
```

---

## 🚀 Cloud Deployment (Render)

1. Connect your GitHub repository (`cloud-computing`) to **Render**.
2. Select **Web Service** environment.
3. Configure settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
   - **Environment Variables:** Set `DATABASE_URL` (MySQL) or leave default for SQLite.
4. Render automatically builds and deploys using `render.yaml` and `Procfile`.

---

## 🧑‍💻 Author

Developed by: **Rithikesh S** (`rithikesh18-rk`)
