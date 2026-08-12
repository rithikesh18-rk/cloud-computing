# Employee Management System


A full-featured, Flask-based HR management application designed for managing employees, departments, attendance tracking, and leave management efficiently with interactive analytics and a responsive UI.

---

## 🌐 Live Demo

🚀 **Live Website:** [https://employee-management-system-bv3y.onrender.com/](https://employee-management-system-bv3y.onrender.com/)

---

## ✨ Features

- **🔐 Admin Authentication:** Secure login and logout system for administrative access control.
- **👨‍💼 Employee Management:** Complete CRUD operations for employee records, job roles, and contact info.
- **🏢 Department Management:** Organize company hierarchy by creating and managing departments and designations.
- **👤 Employee Profiles:** Detailed individual employee profile views with comprehensive background details.
- **📅 Attendance Tracking:** Real-time daily attendance logging and status monitoring.
- **📝 Leave Management:** Streamlined leave requests submission, approval, and status tracking workflow.
- **📊 Dashboard Analytics:** Visual dashboard displaying statistics, department metrics, and attendance overview.
- **🔍 Search and Filtering:** Quick search bar and dynamic filtering across employees and departments.
- **📱 Responsive Bootstrap UI:** Clean, modern, dynamic, mobile-friendly interface built with Bootstrap 5.

---

## 🛠️ Technology Stack

### Backend
- **Python**
- **Flask**
- **SQLAlchemy**

### Database
- **SQLite**

### Frontend
- **HTML**
- **CSS**
- **Bootstrap 5**
- **JavaScript**

### Deployment
- **Render**
- **Gunicorn**

---

## 📁 Project Structure

```text
Employee Management System/
├── app/
│   ├── attendance/         # Attendance tracking blueprint & views
│   ├── auth/               # Authentication routes & logic
│   ├── dashboard/          # Analytics & dashboard blueprint
│   ├── departments/        # Department management blueprint
│   ├── employees/          # Employee CRUD blueprint
│   ├── leave/              # Leave request handling blueprint
│   ├── profile/            # Employee profile views
│   ├── static/             # CSS, JS, and asset files
│   ├── templates/          # HTML templates
│   ├── config.py           # Application configuration
│   ├── extensions.py       # Flask extensions initialization
│   ├── models.py           # Database models
│   └── utils.py            # Helper and utility functions
├── Procfile                # Gunicorn process declaration for Render
├── render.yaml             # Render infrastructure blueprint
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

---

## ⚙️ Installation Steps

1. **Clone repository:**
   ```bash
   git clone repository_url
   cd "Employee Management System"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run application:**
   ```bash
   python run.py
   ```

---

## 🔑 Default Admin Credentials

- **Username:** `admin`
- **Password:** `admin123`

---

## 🚀 Deployment

The application is deployed on **Render** and automatically builds and deploys updates directly from the GitHub repository.

---

## 🖼️ Screenshots

(Add application screenshots here)

---

## 🧑‍💻 Author

Developed by: **rithikesh18-rk**
