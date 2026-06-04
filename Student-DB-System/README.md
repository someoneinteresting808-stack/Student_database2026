# 🎓 STUDENT DATABASE MANAGEMENT SYSTEM (SDMS)

Welcome to the **Student Database Management System (SDMS)**. This is a complete, modular, and production-ready desktop application built with **Python 3**, **Tkinter (with ttk)**, and **MySQL**. It uses a highly modern, flat-UI layout incorporating a clean, professional dark/light palette to maximize visual contrast and user engagement.

---

## 🚀 1. PREREQUISITES AND LOCAL SETUP

To run this desktop application locally, follow these setup steps to prepare your system environment:

### Step 1: Install Python 3
Ensure you have **Python 3.8 or higher** installed on your workstation. You can check your current Python version by running:
```bash
python --version
```

### Step 2: Establish a Virtual Environment (Recommended)
Isolate your package dependencies inside a local virtual environment:
```bash
# Create the environment
python -m venv venv

# Activate the environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Required Dependencies
Install the standard thread-safe MySQL driver for Python:
```bash
pip install mysql-connector-python
```

---

## 🗄️ 2. MYSQL DATABASE SETUP PART

The application relies on a MySQL server to persist student records, course grades, and user login credentials. 

### Step 1: Start your MySQL Server
Ensure your local MySQL service is running via **XAMPP**, **Docker**, **WampServer**, or as a standalone background service on port **3306**.

### Step 2: Feed the SQL Schema
The database and basic tables are configured through database queries written inside `database/schema.sql`. You can load this file directly by running:
```bash
mysql -u root -p < database/schema.sql
```
Alternatively, open your MySQL administration client (such as phpMyAdmin, DBeaver, or MySQL Workbench) and run the full queries manually.

### Initial Seed Administrator User:
The schema automatically seeds a default teacher (administrator) user into the `users` table:
- **Username**: `admin`
- **Password**: `admin`
- **Role**: `teacher`

---

## 🐍 3. RUNNING THE APPLICATION

Once the database is configured, launch the desktop application by executing the orchestrator entry point:
```bash
python main.py
```

### 🔁 Thread-Safe Runtime & Local Offline Fallback Mode
If your workspace does not have a running MySQL instance, the application **automatically switches to Local Offline Simulation Mode** instead of crashing. This fallback maps operations to internal state arrays in RAM with zero disruption, providing a seamless visual test experience for evaluation.

---

## 📂 4. MODULAR FILE BREAKDOWN

The application is completely decoupled to adhere to standard software engineering patterns and Git workflow processes:

### A. Database Connection Layer (`database/db_manager.py`)
- Employs a thread-safe Singleton connection wrapper incorporating Python's `threading.Lock` to guarantee safe concurrent reads and writes.
- Manages connection context blocks with structured `try/except` transactional safeguards.

### B. Access Control UI (`views/login_ui.py`)
- Standardizes a 450x500 access card layout with fields for username and masked password strings.
- Authenticates inputs directly against database records, transitioning seamlessly to the target dashboard on success.

### C. Dashboard Panels UI (`views/dashboard_ui.py`)
- Configures the primary 1440x1024 workspace.
- **Manage Students View**: Controls personal profiles (ID, Name, Email, Phone, Dept, Year) alongside a system connection panel where teachers register credentials passwords for individual students.
- **Manage Grades View**: Accepts uppercase sanitized course codes and grades. Calculates real-time cumulative averages and dynamically outputs GPAs mapped to standard 4.0 scales.
- **Student Profile View**: A highly restricted workspace showing only the current student's personal metrics, PASSED subjects, and cumulative scores.
- **Reports Ledger View**: Displays all students' aggregated subjects transcript matrices.

### D. Form Validators (`utils/validation.py`)
- Strictly checks that input values are not empty.
- Regulates email strings to contain the `@` character.
- Limits phone values to digits.
- Limits subjective grades to numerical ranges between `0` and `100`.

### E. Analytics GPA Calculator (`utils/calculations.py`)
- Converts total subject results to overall percentage arrays.
- Maps percentages to standardized 4.0 scale intervals:
  - Percentage `>= 90.0%` ➔ `4.00`
  - Percentage `>= 80.0%` ➔ `3.00`
  - Percentage `>= 70.0%` ➔ `2.00`
  - Percentage `>= 60.0%` ➔ `1.00`
  - Percentage `< 60.0%` ➔ `0.00`
