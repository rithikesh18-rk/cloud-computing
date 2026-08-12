-- MySQL Schema Script for Attendance Management System
-- Database: attendance_db

CREATE DATABASE IF NOT EXISTS attendance_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE attendance_db;

-- 1. College Settings Table
CREATE TABLE IF NOT EXISTS college_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    college_name VARCHAR(255) NOT NULL DEFAULT 'Apex Institute of Technology',
    college_logo VARCHAR(255) DEFAULT 'default_logo.png',
    address TEXT,
    contact_number VARCHAR(50),
    email_address VARCHAR(100),
    principal_name VARCHAR(100),
    academic_year VARCHAR(20) DEFAULT '2025-2026',
    semester VARCHAR(20) DEFAULT 'Semester 1',
    theme VARCHAR(20) DEFAULT 'light',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Users Table (Admin, Faculty, Student)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id_code VARCHAR(50) UNIQUE NOT NULL, -- e.g., STU2026001, FAC001, ADMIN001
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    profile_image VARCHAR(255) DEFAULT 'default_avatar.png',
    phone_number VARCHAR(20),

    -- Student specific fields
    roll_number VARCHAR(50),
    department_id INT,
    year VARCHAR(10), -- '1st Year', '2nd Year', '3rd Year', '4th Year'
    section VARCHAR(10), -- 'A', 'B', 'C'

    -- Faculty specific fields
    designation VARCHAR(50),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);

-- 4. Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL,
    year VARCHAR(10) NOT NULL,
    semester VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- 5. Attendance Session Table
CREATE TABLE IF NOT EXISTS attendances (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    subject_id INT NOT NULL,
    year VARCHAR(10) NOT NULL,
    section VARCHAR(10) NOT NULL,
    attendance_date DATE NOT NULL,
    marked_by_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (marked_by_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_session (department_id, subject_id, year, section, attendance_date)
);

-- 6. Attendance Records (Student Present/Absent state)
CREATE TABLE IF NOT EXISTS attendance_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL DEFAULT 'Present',
    remarks VARCHAR(255),
    FOREIGN KEY (attendance_id) REFERENCES attendances(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_session (attendance_id, student_id)
);

-- Default Seed Data
INSERT INTO college_settings (id, college_name, college_logo, address, contact_number, email_address, principal_name, academic_year)
VALUES (1, 'Apex Institute of Technology', 'default_logo.png', '123 Education Boulevard, Tech City', '+1 (555) 019-2834', 'info@apextech.edu', 'Dr. Robert Harrison', '2025-2026')
ON DUPLICATE KEY UPDATE id=1;

-- Default Admin User (Password: admin123)
-- Password hash generated via werkzeug pbkdf2:sha256
INSERT INTO users (user_id_code, full_name, email, password_hash, role)
VALUES ('ADMIN001', 'System Administrator', 'admin@college.com', 'scrypt:32768:8:1$KqJ62gG1v5tUqK9k$84d0b67bf915ce36ddb61d36bb9e46a782a2bfbf8dcdbdceceea4aa6ce12384a569df5d688ffbe1ae3d1d2ffb5ffad05c7edbf2fbdf24abfbabfbabfbabfbabf', 'admin')
ON DUPLICATE KEY UPDATE user_id_code='ADMIN001';
