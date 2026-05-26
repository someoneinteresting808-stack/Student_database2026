CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(100) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_level VARCHAR(50) NOT NULL,
    username VARCHAR(100),
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    subject_name VARCHAR(100) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    UNIQUE KEY unique_student_subject (student_id, subject_name),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

INSERT INTO users (username, password, role) 
VALUES ('admin', 'admin', 'teacher')
ON DUPLICATE KEY UPDATE username=username;
