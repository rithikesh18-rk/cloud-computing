# 🎓 Attendance Management System

A full-stack, responsive **Attendance Management System** built with **Python Flask**, **MySQL**, **Bootstrap 5**, **JavaScript (ES6)**, and **HTML5/CSS3**.

---

## 🌟 Key Features

1. **Authentication & Role-Based Access Control**:
   - **Admin Login**, **Faculty Login**, and **Student Login**.
   - Password hashing using `werkzeug.security` (`pbkdf2` / `scrypt`).
   - Role-protected routes and session management.

2. **College Branding Customization (Settings)**:
   - Dynamic College Settings page for Admin to update **College Name**, **Logo**, **Address**, **Contact Number**, **Email**, **Principal Name**, and **Academic Year**.
   - Customizations dynamically propagate to Login screen, Navigation Bar, Dashboards, Attendance sheets, Reports, PDF exports, and Excel exports.

3. **Student Account Management**:
   - Auto-generated Student ID (`STU20260001`).
   - Admin CRUD operations: Add, Edit, Delete, Reset Password.
   - Dynamic fields stored in MySQL: Name, Email (unique), Password, Roll Number, Department, Year, Section, Phone.

4. **Faculty, Department & Subject Management**:
   - Faculty accounts for class attendance marking.
   - Department and course subject mappings per academic year/semester.

5. **Attendance Module**:
   - Dynamic roster grid filtering by Department, Year, Section, Subject, and Date.
   - Interactive Present/Absent marking with bulk "Mark All Present" & "Mark All Absent" toggles.
   - View, edit, or delete past attendance records.

6. **Analytics & PDF/Excel Reports**:
   - Reports: **Daily**, **Weekly**, **Monthly**, **Student-wise**, **Subject-wise**, **Department-wise**.
   - Percentage calculation with eligibility flags (< 75% shortage warning).
   - Export to **PDF** (using ReportLab with dynamic College Header & Logo) and **Excel** (`.xlsx` using OpenPyXL).
   - Interactive Chart.js analytics graphs on Dashboard.

7. **Student Portal**:
   - Student view showing overall attendance percentage, subject breakdown, recent class records, exam eligibility status, and downloadable PDF report.

---

## 📂 Project Structure

```text
project Attendance Management System/
│── app.py                       # Main application entry point
│── config.py                    # App configuration & DB settings
│── schema.sql                   # MySQL database creation script
│── requirements.txt             # Dependency requirements
│── README.md                    # Project documentation & instructions
│── database/
│   └── db_setup.py              # DB connector, fallback & default seeder
│── models/
│   ├── __init__.py              # SQLAlchemy database object
│   ├── user.py                  # User (Admin, Faculty, Student) model
│   ├── department.py            # Department model
│   ├── subject.py               # Subject model
│   ├── attendance.py           # Attendance & AttendanceRecord models
│   └── settings.py             # College Settings model
│── routes/
│   ├── __init__.py
│   ├── auth_routes.py           # Login, logout, session routes
│   ├── admin_routes.py          # Dashboard, CRUDs, settings routes
│   ├── attendance_routes.py     # Attendance marking, viewing, editing, deleting
│   ├── report_routes.py         # Reports analytics, PDF & Excel export handlers
│   └── student_routes.py        # Student portal routes
│── utils/
│   ├── __init__.py
│   ├── helpers.py               # Auth decorators & helper functions
│   ├── pdf_exporter.py          # ReportLab PDF generator
│   └── excel_exporter.py        # OpenPyXL Excel builder
│── static/
│   ├── css/
│   │   └── custom.css           # Modern custom styling, badges, glassmorphism
│   ├── js/
│   │   ├── main.js              # Form validation & tooltips
│   │   ├── attendance.js        # Dynamic AJAX filters & attendance toggles
│   │   └── reports.js           # Chart.js integration & report filters
│   └── uploads/                 # Dynamically uploaded logos & assets
│── templates/
│   ├── base.html                # Master layout wrapper with dynamic navbar & footer
│   ├── auth/
│   │   └── login.html           # Login screen with dynamic branding
│   ├── admin/
│   │   ├── dashboard.html       # Overview dashboard & charts
│   │   ├── students.html        # Student management table & CRUD modals
│   │   ├── faculty.html         # Faculty management table & CRUD modals
│   │   ├── departments.html     # Department & subject management
│   │   └── settings.html        # College Customization form
│   ├── attendance/
│   │   ├── mark.html            # Attendance marking roster
│   │   ├── view.html            # Attendance history & deletion
│   │   └── edit.html            # Modify past attendance session
│   ├── reports/
│   │   └── index.html           # Reports center & download actions
│   └── student/
│       └── dashboard.html       # Student personal attendance dashboard
```

---

## 💻 Installation & Setup

### Prerequisites
- **Python 3.10+** installed.
- **MySQL Server** (optional, automatic SQLite fallback included for development).

### 1. Clone / Extract Repository
Ensure you are in the project root directory:
```bash
cd "project Attendance Management System"
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```
Or on Windows:
```bash
py -3 -m pip install -r requirements.txt
```

### 3. Database Setup

#### Option A: MySQL Database Setup (Production Mode)
1. Open MySQL Workbench or MySQL Command Line Client.
2. Execute the included SQL script:
   ```sql
   mysql -u root -p < schema.sql
   ```
3. Environment variables (Optional):
   - `MYSQL_USER` (Default: `root`)
   - `MYSQL_PASSWORD` (Default: `root`)
   - `MYSQL_HOST` (Default: `localhost`)
   - `MYSQL_PORT` (Default: `3306`)
   - `MYSQL_DB` (Default: `attendance_db`)

#### Option B: Automatic SQLite Fallback (Development / Out-of-the-Box Mode)
If a local MySQL server is not detected or credentials are not configured, the system automatically initializes a local database file at `database/attendance.db` without requiring manual database installation.

---

## 🌐 Live Demo

**Live Website:** https://attendance-management-system-1-3fey.onrender.com/

Click the link above to access the Attendance Management System.

---

## 🔑 Default Accounts (Created Automatically)

| Role | Email Address | Default Password | Features Accessible |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@college.com` | `admin123` | Dashboard, Student CRUD, Faculty CRUD, Dept/Subject CRUD, Settings, Attendance, Reports, PDF/Excel Exports |
| **Faculty** | `faculty@college.com` | `faculty123` | Dashboard, Mark Attendance, View & Edit Logs, Reports |
| **Student** | `student@college.com` | `student123` | Student Portal, Personal Attendance %, Subject Breakdown, Download PDF Report |

---

## 🔒 Security Best Practices Implemented

- **Password Security**: Passwords hashed securely using `werkzeug.security`.
- **SQL Injection Prevention**: Built entirely with SQLAlchemy ORM parametrized queries preventing raw SQL string concatenation vulnerabilities.
- **Role-Based Authorization**: Route guards preventing unauthorized URL access.
- **Form Input Sanitization**: Cleaned inputs, secure file uploads, and unique email constraints.
