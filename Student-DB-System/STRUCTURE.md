# 📂 SYSTEM STRUCTURE AND COMPONENT MAP (SDMS)

This document provides a highly in-depth look into the architectural structure, database relationships, operational layouts, and data pathways of the **Student Database Management System (SDMS)**.

---

## 🗺️ 1. ARCHITECTURAL FILE DIRECTORY STRUCTURE
The codebase follows a strictly modular separation of concerns to prevent code clutter and support scalable product updates:

```
Student-DB-System/
│
├── main.py                     # Primary Application entry point (Initializes TKinter window and routes screens)
├── README.md                   # Installation guidelines, database commands, and execution guide
├── STRUCTURE.md                # [This File] Component connections map and data flows
│
├── database/                   # Database Persistence Directories
│   ├── schema.sql              # Clean DDL queries creating tables, relationships, and administrative logins
│   └── db_manager.py           # Thread-safe Singleton DB Connection client using internal Python Locking
│
├── utils/                      # Standard Utility and Computation Modules
│   ├── validation.py           # Input sanitization, email verification, and score parameter guards
│   └── calculations.py         # Percentage averages calculator and mapped 4.0 GPA scales index
│
└── views/                      # UI Views and Screens Components
    ├── login_ui.py             # System Access Gate (Card login panel with masked fields)
    └── dashboard_ui.py         # Primary Workspaces (Contains all 5 screens and role-based sidebars)
```

---

## 🔁 2. COMPONENT DATA PATHWAYS

The diagram below maps the dynamic execution pathway of events:

```
[User Action on UI Views] ──> [Utils Validation] ──> [Database Connection] ──> [MySQL Server Storage]
         ▲                                                                                 │
         │                                                                                 ▼
[Refreshed Treeview Grids] <── [Utils Calculations] <─────────────────────────────────────┘
```

### Event Lifecycle Workflow (Example: Adding a Student Record)
1. The administrator inputs text inside form fields inside the **Manage Students Panel** (`dashboard_ui.py`) and clicks the "Save Student" button.
2. The UI contacts `utils/validation.py` to confirm fields are fully registered, phone formats match number inputs, and email characters contain `@`.
3. If valid, the UI utilizes `database/db_manager.py` to initiate transactional storage.
4. If MySQL is connected, a safe query executes `INSERT INTO students` and `INSERT INTO users` in a single combined database transaction.
5. Once complete, the table triggers a grid refresh query, reloading all values securely inside the Treeview tables.

---

## 🗄️ 3. DATABASE SCHEMA RELATIONSHIPS

The system persistence layer separates login users, personal profiles, and dynamic academic grades:

```
  ┌───────────────────────┐
  │         USERS         │
  ├───────────────────────┤
  │ username (PK)  Varch  │ <───┐ (FOREIGN KEY username)
  │ password       Varch  │     │ Maps login accounts to profiles and role restrictions
  │ role           Varch  │     │
  └───────────────────────┘     │
             ▲                  │
             │ (Cascade Set)    │
  ┌──────────┴────────────┐     │
  │       STUDENTS        │ ────┘
  ├───────────────────────┤
  │ student_id (PK) Varch │ <───┐ (FOREIGN KEY student_id)
  │ name           Varch  │     │ Cascades on delete (removing student deletes all grades)
  │ email          Varch  │     │
  │ phone          Varch  │     │
  │ department     Varch  │     │
  │ year_level     Varch  │     │
  └───────────────────────┘     │
                                │
  ┌─────────────────────────────┴──────┐
  │               GRADES               │
  ├────────────────────────────────────┤
  │ grade_id (PK, Auto-Increment)  Int │
  │ student_id                    Varch│ (Composite unique index with subject_name)
  │ subject_name                  Varch│
  │ score                        Decim │
  └────────────────────────────────────┘
```

### Constraints and Key Design Principles:
1. **Separation of Profile and Access**: Account credentials reside inside the `users` table, while personal directories live in `students`. This permits teachers to register independent usernames and passwords for student panels without mixing data models.
2. **Cascading Deletions**: Deleting a student profile from the index triggers a cascade purge inside the database, automatically purging all historical grade objects linked to that target ID.
3. **Composite Safe Guards**: The database enforces a `UNIQUE KEY` constraint over the composite pairing of (`student_id`, `subject_name`), ensuring teachers cannot inadvertently add duplicate grade records for the same course on a single student.

---

## 💻 4. DETAILED COMPONENT LAYOUTS

### 1. Screen 1: Access Control Card Panel (`views/login_ui.py`)
- **Layout**: 450x500. Uses a padded layout styling the login field cards in white over standard light gray backgrounds.
- **Role Redirection**: Evaluates username parameters. Setting role `teacher` opens the admin dashboard, while student accounts redirect specifically to personal profile screens.

### 2. Screen 2: Students Registry Profile Grid (`views/dashboard_ui.py`)
- **Layout**: Multi-panel master-split view container with form on the left side and interactive matrix lists on the right side.
- **Interchangeable Filters**: Integrates quick-access select drop-downs sorting students instantly by **Department** or **Year Level** on combobox selections.
- **Real-Time Key Release Filtering**: List searches update listings dynamically on every keystroke, matching both ID codes and complete student names.

### 3. Screen 3: Academic Grades Workspace (`views/dashboard_ui.py`)
- **Layout**: Centered select dropdown with responsive score fields. Calculates and saves grade metrics safely.
- **Course Title Sanitization**: Inputs uppercase characters automatically, keeping databases unified.
- **Metrics Displays**: Incorporates two centered card slots tracking calculated cumulative percentages and GPAs on a 4.0 scale dynamically as subjects are modified.

### 4. Screen 4: Student Portal View (`views/dashboard_ui.py`)
- **Layout**: Clear of all inputs, edit forms, or navigation lists.
- **Structure**: Highlights student status metrics in high-contrast badge headers. Displays pass/fail records, and displays color-coded badges indicating pass rates.

### 5. Screen 5: All Data master reports ledger (`views/dashboard_ui.py`)
- **Structure**: Shows aggregated course lists in horizontal strings for each student, yielding simple multi-subject scrollboards for evaluation.
