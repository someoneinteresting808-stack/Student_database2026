# Assembly and Deployment Manual (Step-by-Step Stepwise Construct)

Welcome to the **Student Database Management System (SDMS) Desktop Application** codebase. This guide details how to assemble, install, configure, map, and deploy the entire modular decoupled system in a production or research development workspace.

---

## 📂 System File Architecture Overview
The repository is modularly decoupled across files to support multiple developers working concurrently on Git branches without merge conflicts:

```
Student-DB-System/
├── main.py                     # Primary Application orchestrator & transition manager
├── CONSTRUCT.md                # This Stepwise Assembly and Database Setup Manual
├── database/
│   ├── schema.sql              # Clean DDL scripts for setting up tables and admin users
│   └── db_manager.py           # Thread-safe MySQL transactional connection wrappers
├── views/
│   ├── login_ui.py             # Screen 1: Access Control Card Component
│   └── dashboard_ui.py         # App workspaces: Screen 2, Screen 3, Student view, master ledgers
└── utils/
    ├── validation.py           # Validation engines (re-useable regexes, ranges & checks)
    └── calculations.py         # GPA scales calculators and aggregate math utilities
```

---

## 🛠️ Phase 1: Local System Preparation and Dependency Installation

Before firing up the Tkinter frames, make sure Python 3.8+ is installed. Follow these quick steps to set up the development package:

```bash
# 1. Create a clean isolated virtual environment
python3 -m venv venv

# 2. Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows powershell:
.\venv\Scripts\Activate.ps1

# 3. Import relevant MySQL Python connectors and graphic assets packages
pip install mysql-connector-python
```

---

## 🗄️ Phase 2: MySQL Database Server Launch and Configuration

The backend of the platform relies on **MySQL Server**. Configure and start it in your localhost using XAMPP, Docker, or native services:

### Option A: Local native CLI Setup
Start the database CLI daemon as the systems admin and feed the schemas:

```bash
# Connect to your local MySQL engine instance
mysql -u root -p
```

### Option B: Executing SQL Schema file
We provide the schema structure inside `/database/schema.sql`. You can load this file directly using your favorite GUI (e.g. phpMyAdmin, DBeaver) or load via command prompt:

```bash
mysql -u root -p < database/schema.sql
```

This sets up:
1. `students` profile ledger table.
2. `grades` records containing custom subjects and score digits (0-100).
3. `users` access accounts for separate Roles: `teacher` (teachers/admins) and `student` (individual students).
4. One baseline administrator account preinstalls with Credentials:
   - **Username**: `admin`
   - **Password**: `admin`
   - **Access Role**: `teacher`

---

## 🚀 Phase 3: Launching and Running the Application
Run the entry point `main.py` directly:

```bash
python main.py
```

### 🔁 Thread-Safe Runtime with Local Simulation Fallbacks
*Crucial Dev Option:* The engine manager contains fallback mechanisms. If your local workspace is missing a running MySQL server, the application automatically handles exceptions and activates **Local Simulation Mode**, using full-fidelity lists to perform student entry, grades registration, search filters, and profile mapping instantly in RAM! This ensures developers can review the entire TKinter application interface, calculate GPA scores, search student records, and toggle roles with absolute zero setup.

---

## 📋 Comprehensive Functional Features Mapping

### 1. Access Control (login_ui.py)
- Features a clean 450x500 white card container built on a light gray landscape workspace.
- Enforces character restrictions, password masking, and credentials checks on database levels.
- Segregates interfaces cleanly depending on user login types (`teacher` redirects to Admin Center; student username redirects to personal portfolio sheet).

### 2. Live Profile Management (dashboard_ui.py)
- Offers dual combobox filters: **Sort/Filter by Department** and **Sort/Filter by Year Level** instantly running query-rebuild events on Treeview grid matrices.
- Offers instant, on-key-up text searches filtering matching Full Name or registration IDs.
- Includes a dedicated student user profile account creation system directly integrated within the Add Studet profile panel. Teachers can specify username and matching credentials.

### 3. Dynamic Grades board (dashboard_ui.py & calculations.py)
- Supports typed entry for courses/subjects making them robustly dynamic! Input automatically filters and sanitizes course titles to **Uppercase alphanumeric values** and validates whether a similar grade report has already been created for that student.
- Typable ComboBox search bar binds key release actions to order matching student records instantly as the teacher types letters.
- Card metrics display real-time reactive variable assignments, calculating overall percentage average and converting GPA scores securely on the standard 4.0 scale:
  - `>= 90.0%` ➔ `4.00`
  - `>= 80.0%` ➔ `3.00`
  - `>= 70.0%` ➔ `2.00`
  - `>= 60.0%` ➔ `1.00`
  - `< 60.0%` ➔ `0.00`

### 4. Student Portfolio Screen (dashboard_ui.py)
- Fully isolated page layout hiding all input elements, sidebars, filter items, and database write action keys from student viewports.
- Renders cumulative percentage metrics, calculated cumulative GPA scales, and individual subject grade details table lists.
