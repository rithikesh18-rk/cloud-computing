# Cloud Computing Projects

This repository contains full-stack web application projects developed for the **Cloud Computing** subject. Each project is organized into its own self-contained directory with its complete source code, configuration files, templates, assets, dependencies, and project documentation.

---

## 🌐 Live Deployments & Application Access

🚀 **Live Demo:** [https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/)

| Project | Local Development URL | Live Production URL |
| :--- | :--- | :--- |
| **Employee Management System** | `http://127.0.0.1:5000` | 🚀 [https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/) |
| **Attendance Management System** | `http://127.0.0.1:5000` | Local Deployment |
| **Cloud-Based AQI Predictor** | `http://127.0.0.1:8501` (Dashboard)<br>`http://127.0.0.1:8000` (API) | Local / Docker Deployment |

---

## Projects

### 1. Attendance Management System

- **Description:** A full-stack, responsive attendance management web application built for educational institutions. It features multi-role authentication (Admin, Faculty, Student), dynamic college branding customization (logo, address, contact, academic year), student and faculty CRUD management, interactive class attendance marking with bulk toggles, attendance percentage calculations with shortage (< 75%) warnings, Chart.js dashboard analytics, dynamic report generation, and downloadable PDF & Excel export capabilities.
- **Technologies Used:**
  - **Backend:** Python, Flask, Flask-SQLAlchemy, Werkzeug
  - **Database:** MySQL (via PyMySQL) with automatic SQLite fallback (`database/attendance.db`)
  - **Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5, Chart.js
  - **Exporting & Media:** ReportLab (PDF export), OpenPyXL (Excel `.xlsx` export), Pillow (Image processing)
  - **Deployment / Server:** Gunicorn
- **Original GitHub Repository:**
  https://github.com/rithikesh18-rk/Attendance-Management-System

---

### 2. Employee Management System

- **Live Demo:** 🚀 [https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/)
- **Description:** A comprehensive Flask-based Human Resource (HR) management system designed to manage employee lifecycle records, company department hierarchies, daily attendance tracking, and employee leave workflows. It includes admin authentication, individual employee profile management, search and filtering tools, visual dashboard analytics, case-insensitive validation, database transaction safety (`safe_commit`), and automated deployment configuration for cloud hosting on Render.
- **Technologies Used:**
  - **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms, PyMySQL, Cryptography, python-dotenv, email-validator
  - **Database:** MySQL (via PyMySQL with connection pooling `pool_pre_ping: True`) with automatic SQLite fallback (`sqlite:///instance/employee_system.db`)
  - **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js
  - **Deployment & Infrastructure:** Render (`render.yaml`), Gunicorn (`Procfile`), `runtime.txt`
- **Original GitHub Repository:**
  https://github.com/rithikesh18-rk/employee-management-system

---

### 3. Cloud-Based Air Quality Index (AQI) Predictor

- **Description:** A high-accuracy Machine Learning atmospheric pollution prediction platform with real-time EPA-standard health advisories. Powered by an XGBoost Regressor model ($R^2 = 0.9991$), FastAPI REST API backend with Pydantic validation, Streamlit interactive web dashboard with dynamic pollutant threshold gauges, and containerized Docker setup.
- **Technologies Used:**
  - **Machine Learning:** Python, XGBoost Regressor, Scikit-Learn, Pandas, NumPy, Joblib
  - **Backend & Cloud API:** FastAPI, Uvicorn, Pydantic v2, CORS Middleware
  - **Frontend Dashboard:** Streamlit, Plotly, HTML5/CSS3 Custom Components
  - **DevOps & Containerization:** Docker, Docker Compose, GitHub Actions CI/CD pipeline

---

## Repository Structure

```text
cloud-computing/
│
├── Attendance-Management-System/
│   ├── database/
│   │   └── db_setup.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── attendance.py
│   │   ├── department.py
│   │   ├── settings.py
│   │   ├── subject.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── admin_routes.py
│   │   ├── attendance_routes.py
│   │   ├── auth_routes.py
│   │   ├── report_routes.py
│   │   └── student_routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── custom.css
│   │   ├── js/
│   │   │   ├── attendance.js
│   │   │   ├── main.js
│   │   │   └── reports.js
│   │   └── uploads/
│   │       └── logo_1723467645.png
│   ├── templates/
│   │   ├── admin/
│   │   │   ├── dashboard.html
│   │   │   ├── departments.html
│   │   │   ├── faculty.html
│   │   │   ├── settings.html
│   │   │   └── students.html
│   │   ├── attendance/
│   │   │   ├── edit.html
│   │   │   ├── mark.html
│   │   │   └── view.html
│   │   ├── auth/
│   │   │   └── login.html
│   │   ├── reports/
│   │   │   └── index.html
│   │   ├── student/
│   │   │   └── dashboard.html
│   │   └── base.html
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── excel_exporter.py
│   │   ├── helpers.py
│   │   └── pdf_exporter.py
│   ├── app.py
│   ├── config.py
│   ├── README.md
│   ├── requirements.txt
│   └── schema.sql
│
├── Employee-Management-System/
│   ├── app/
│   │   ├── attendance/
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── auth/
│   │   │   ├── forms.py
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── dashboard/
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── departments/
│   │   │   ├── forms.py
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── employees/
│   │   │   ├── forms.py
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── leave/
│   │   │   ├── forms.py
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── profile/
│   │   │   ├── forms.py
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── style.css
│   │   │   └── js/
│   │   │       └── main.js
│   │   ├── templates/
│   │   │   ├── attendance/
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── departments/
│   │   │   ├── employees/
│   │   │   ├── errors/
│   │   │   ├── leave/
│   │   │   ├── profile/
│   │   │   └── base.html
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── Procfile
│   ├── README.md
│   ├── render.yaml
│   ├── requirements.txt
│   ├── run.py
│   ├── test_full_system.py
│   └── test_module2.py
│
└── README.md
```

---

## Author

Rithikesh S
