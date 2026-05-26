import tkinter as tk
from tkinter import ttk, messagebox
from utils.validation import validate_student_fields, validate_grade_fields
from utils.calculations import calculate_percentage, map_gpa
from database.db_manager import DBManager

class DashboardUI:
    def __init__(self, root, username, role, logout_callback):
        self.root = root
        self.username = username
        self.role = role
        self.logout_cb = logout_callback
        self.db = DBManager()
        
        self.root.title("Student Database Management System")
        self.root.geometry("1440x1024")
        self.root.configure(bg="#F3F4F6")
        
        # Center the dashboard
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (1440 // 2)
        y = (screen_height // 2) - (1024 // 2)
        self.root.geometry(f"1440x1024+{max(0, x)}+{max(0, y)}")

        # Local state storage fallbacks for instant preview offline simulation
        self.local_students = [
            {"student_id": "001", "name": "Alice Smith", "email": "alice@univ.edu", "phone": "555-0192", "department": "Computer Science", "year_level": "First Year", "username": "std_alice", "password": "gpa"},
            {"student_id": "002", "name": "Bob Jones", "email": "bob@univ.edu", "phone": "555-0143", "department": "Mathematics", "year_level": "Second Year", "username": "std_bob", "password": "gpa"},
            {"student_id": "003", "name": "Charlie Brown", "email": "charlie@univ.edu", "phone": "555-0155", "department": "Physics", "year_level": "Third Year", "username": "std_charlie", "password": "gpa"}
        ]
        self.local_grades = [
            {"student_id": "001", "subject_name": "MATH", "score": 90.0},
            {"student_id": "001", "subject_name": "PHYSICS", "score": 85.0},
            {"student_id": "001", "subject_name": "CS", "score": 95.0},
            {"student_id": "001", "subject_name": "ENGLISH", "score": 88.0},
            
            {"student_id": "002", "subject_name": "MATH", "score": 75.0},
            {"student_id": "002", "subject_name": "PHYSICS", "score": 80.0},
            {"student_id": "002", "subject_name": "CS", "score": 72.0},
            {"student_id": "002", "subject_name": "ENGLISH", "score": 85.0}
        ]

        self.departments = ["Computer Science", "Mathematics", "Physics", "Chemistry", "Engineering", "Business"]
        self.years = ["First Year", "Second Year", "Third Year", "Fourth Year"]

        self.create_layouts()

    def create_layouts(self):
        # 1. Sidebar Panel (260px wide)
        self.sidebar = tk.Frame(self.root, bg="#2A3E5C", width=260)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        # Admin Header
        header_title = "SDMS ADMIN" if self.role == "teacher" else "STUDENT PORTAL"
        tk.Label(self.sidebar, text=header_title, font=("Arial", 16, "bold"), fg="#FFFFFF", bg="#2A3E5C").pack(pady=(40, 50))

        # Main Workspace Container
        self.workspace = tk.Frame(self.root, bg="#F3F4F6")
        self.workspace.pack(fill="both", expand=True, side="right")

        if self.role == "teacher":
            self.create_teacher_nav()
            self.show_student_management()
        else:
            self.create_student_nav()
            self.show_student_self_view()

    def create_teacher_nav(self):
        # Sidebar Menu Items
        self.btn_students = tk.Button(self.sidebar, text="👤  Manage Students", font=("Arial", 12), fg="#FFFFFF", bg="#1E2A3C",
                                      activebackground="#1E2A3C", activeforeground="#FFFFFF", bd=0, anchor="w", padx=25, cursor="hand2",
                                      command=self.show_student_management)
        self.btn_students.pack(fill="x", pady=5)

        self.btn_grades = tk.Button(self.sidebar, text="📊  Manage Grades", font=("Arial", 12), fg="#FFFFFF", bg="#2A3E5C",
                                    activebackground="#1E2A3C", activeforeground="#FFFFFF", bd=0, anchor="w", padx=25, cursor="hand2",
                                    command=self.show_grades_management)
        self.btn_grades.pack(fill="x", pady=5)

        self.btn_reports = tk.Button(self.sidebar, text="📋  All Student Reports", font=("Arial", 12), fg="#FFFFFF", bg="#2A3E5C",
                                     activebackground="#1E2A3C", activeforeground="#FFFFFF", bd=0, anchor="w", padx=25, cursor="hand2",
                                     command=self.show_reports_management)
        self.btn_reports.pack(fill="x", pady=5)

        # Logout at absolute bottom
        logout_btn = tk.Button(self.sidebar, text="🚪  Log Out", font=("Arial", 12, "bold"), fg="#EF4444", bg="#2A3E5C",
                               activebackground="#2A3E5C", activeforeground="#EF4444", bd=0, anchor="w", padx=25, cursor="hand2",
                               command=self.handle_logout)
        logout_btn.pack(side="bottom", fill="x", pady=40)

    def create_student_nav(self):
        tk.Label(self.sidebar, text=f"Welcome, {self.username}", font=("Arial", 10, "italic"), fg="#E5E7EB", bg="#2A3E5C").pack(pady=(0, 30))
        
        self.btn_self = tk.Button(self.sidebar, text="👤  My Profile & Grades", font=("Arial", 12), fg="#FFFFFF", bg="#1E2A3C",
                                  activebackground="#1E2A3C", activeforeground="#FFFFFF", bd=0, anchor="w", padx=25, cursor="hand2")
        self.btn_self.pack(fill="x", pady=5)

        logout_btn = tk.Button(self.sidebar, text="🚪  Log Out", font=("Arial", 12, "bold"), fg="#EF4444", bg="#2A3E5C",
                               activebackground="#2A3E5C", activeforeground="#EF4444", bd=0, anchor="w", padx=25, cursor="hand2",
                               command=self.handle_logout)
        logout_btn.pack(side="bottom", fill="x", pady=40)

    def clear_workspace(self):
        for widget in self.workspace.winfo_children():
            widget.destroy()

    def set_active_button(self, active_btn):
        if self.role == "teacher":
            self.btn_students.configure(bg="#2A3E5C")
            self.btn_grades.configure(bg="#2A3E5C")
            self.btn_reports.configure(bg="#2A3E5C")
            active_btn.configure(bg="#1E2A3C")

    # ==========================
    # SCREEN 2: STUDENT PROFILE MANAGEMENT
    # ==========================
    def show_student_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_students)

        # Master Grid Layer
        form_col = tk.Frame(self.workspace, bg="#FFFFFF", width=380, highlightthickness=1, highlightbackground="#E5E7EB")
        form_col.pack(side="left", fill="both", padx=20, pady=20)
        form_col.pack_propagate(False)

        grid_col = tk.Frame(self.workspace, bg="#F3F4F6")
        grid_col.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # LEFT Profile Input Form
        tk.Label(form_col, text="Add / Update Student", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))

        labels = ["Student ID *", "Full Name *", "Email Address *", "Phone Number *", "Department", "Year Level", "Account Username *", "Account Password *"]
        self.student_entries = {}

        scrollable_frame = tk.Frame(form_col, bg="#FFFFFF")
        scrollable_frame.pack(fill="both", expand=True, padx=20)

        for label in labels:
            tk.Label(scrollable_frame, text=label, font=("Arial", 10), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", pady=(8, 2))
            if label == "Department":
                combo = ttk.Combobox(scrollable_frame, values=self.departments, state="readonly", font=("Arial", 11))
                combo.pack(fill="x", ipady=3)
                combo.set(self.departments[0])
                self.student_entries[label] = combo
            elif label == "Year Level":
                combo = ttk.Combobox(scrollable_frame, values=self.years, state="readonly", font=("Arial", 11))
                combo.pack(fill="x", ipady=3)
                combo.set(self.years[0])
                self.student_entries[label] = combo
            elif label == "Account Password *":
                entry = tk.Entry(scrollable_frame, show="*", font=("Arial", 11), bd=1, relief="solid")
                entry.pack(fill="x", ipady=5)
                self.student_entries[label] = entry
            else:
                entry = tk.Entry(scrollable_frame, font=("Arial", 11), bd=1, relief="solid")
                entry.pack(fill="x", ipady=5)
                self.student_entries[label] = entry

        # Buttons Container
        btn_frame = tk.Frame(form_col, bg="#FFFFFF")
        btn_frame.pack(fill="x", side="bottom", pady=25, padx=20)

        save_btn = tk.Button(btn_frame, text="Save Student", font=("Arial", 11, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=self.save_student_action)
        save_btn.pack(side="left", fill="x", expand=True, marginRight=5, ipady=8, padx=(0, 5))

        clear_btn = tk.Button(btn_frame, text="Clear Fields", font=("Arial", 11, "bold"), bg="#9CA3AF", fg="#FFFFFF", bd=0, cursor="hand2", command=self.clear_student_fields)
        clear_btn.pack(side="right", fill="x", expand=True, ipady=8, padx=(5, 0))

        # RIGHT Data Presentation Area
        # Top Search & Filter Bar Group
        filter_bar_frame = tk.Frame(grid_col, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        filter_bar_frame.pack(fill="x", pady=(0, 15), ipady=8)

        # Left aligned search
        tk.Label(filter_bar_frame, text="  🔍 Search:", font=("Arial", 11), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=5)
        self.search_entry = tk.Entry(filter_bar_frame, font=("Arial", 11), bd=1, relief="solid")
        self.search_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_students_action())

        # Department Sorter Combobox
        tk.Label(filter_bar_frame, text="Dept:", font=("Arial", 10), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(15, 2))
        self.dept_filter = ttk.Combobox(filter_bar_frame, values=["All Cases"] + self.departments, state="readonly", font=("Arial", 10), width=15)
        self.dept_filter.pack(side="left", padx=5)
        self.dept_filter.set("All Cases")
        self.dept_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_students_action())

        # Year Level Sorter Combobox
        tk.Label(filter_bar_frame, text="Year:", font=("Arial", 10), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(10, 2))
        self.year_filter = ttk.Combobox(filter_bar_frame, values=["All Cases"] + self.years, state="readonly", font=("Arial", 10), width=15)
        self.year_filter.pack(side="left", padx=5)
        self.year_filter.set("All Cases")
        self.year_filter.bind("<<ComboboxSelected>>", lambda e: self.filter_students_action())

        # Main Tree Grid
        self.student_tree = ttk.Treeview(grid_col, columns=("ID", "Name", "Email", "Phone", "Department", "Year", "Username"), show="headings")
        self.student_tree.heading("ID", text="ID")
        self.student_tree.heading("Name", text="Full Name")
        self.student_tree.heading("Email", text="Email Address")
        self.student_tree.heading("Phone", text="Phone Number")
        self.student_tree.heading("Department", text="Department")
        self.student_tree.heading("Year", text="Year")
        self.student_tree.heading("Username", text="Username")

        self.student_tree.column("ID", width=70, anchor="center")
        self.student_tree.column("Name", width=160, anchor="w")
        self.student_tree.column("Email", width=180, anchor="w")
        self.student_tree.column("Phone", width=120, anchor="center")
        self.student_tree.column("Department", width=140, anchor="center")
        self.student_tree.column("Year", width=110, anchor="center")
        self.student_tree.column("Username", width=100, anchor="center")

        self.student_tree.pack(fill="both", expand=True, pady=(0, 15))

        # Bottom Row Action Buttons
        grid_btn_frame = tk.Frame(grid_col, bg="#F3F4F6")
        grid_btn_frame.pack(fill="x")

        edit_btn = tk.Button(grid_btn_frame, text="Edit Selected Row", font=("Arial", 11, "bold"), bg="#2A3E5C", fg="#FFFFFF", bd=0, cursor="hand2", command=self.edit_student_action)
        edit_btn.pack(side="left", px=15, ipady=8, padx=(0, 10))

        delete_btn = tk.Button(grid_btn_frame, text="Delete Selected Row", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=self.delete_student_action)
        delete_btn.pack(side="left", ipady=8)

        self.refresh_student_table()

    def clear_student_fields(self):
        for label, widget in self.student_entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.delete(0, tk.END)
        self.student_entries["Student ID *"].configure(state="normal")

    def refresh_student_table(self, dataset=None):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)

        if dataset is None:
            # Query MySQL
            try:
                query = "SELECT s.student_id, s.name, s.email, s.phone, s.department, s.year_level, s.username FROM students s"
                dataset = self.db.execute_query(query)
            except Exception:
                dataset = self.local_students

        if dataset:
            for s in dataset:
                self.student_tree.insert("", "end", values=(s.get("student_id", s.get("ID")), s.get("name", s.get("Name")), s.get("email", s.get("Email")), s.get("phone", s.get("Phone")), s.get("department", s.get("Department")), s.get("year_level", s.get("Year")), s.get("username", s.get("Username"))))

    def save_student_action(self):
        sid = self.student_entries["Student ID *"].get().strip()
        name = self.student_entries["Full Name *"].get().strip()
        email = self.student_entries["Email Address *"].get().strip()
        phone = self.student_entries["Phone Number *"].get().strip()
        dept = self.student_entries["Department"].get()
        yr = self.student_entries["Year Level"].get()
        user = self.student_entries["Account Username *"].get().strip()
        pwd = self.student_entries["Account Password *"].get()

        # Determine if we're doing a creation or update
        is_update = False
        try:
            q = "SELECT student_id FROM students WHERE student_id = %s"
            is_update = bool(self.db.execute_query(q, (sid,)))
        except Exception:
            is_update = any(x["student_id"] == sid for x in self.local_students)

        valid, err = validate_student_fields(sid, name, email, phone, dept, yr, user, pwd, not is_update)
        if not valid:
            messagebox.showerror("Validation Error", err)
            return

        try:
            if is_update:
                # Edit record
                # Update Student personal data
                query1 = "UPDATE students SET name=%s, email=%s, phone=%s, department=%s, year_level=%s WHERE student_id=%s"
                self.db.execute_non_query(query1, (name, email, phone, dept, yr, sid))
                # Update password if provided
                if pwd.strip():
                    # For simplicity, fetch the user tied to student and modify password
                    query_user = "SELECT username FROM students WHERE student_id=%s"
                    res = self.db.execute_query(query_user, (sid,))
                    if res and res[0]["username"]:
                        query2 = "UPDATE users SET password=%s WHERE username=%s"
                        self.db.execute_non_query(query2, (pwd, res[0]["username"]))
            else:
                # Transaction: add user account, then add student
                ops = [
                    ("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (user, pwd, "student")),
                    ("INSERT INTO students (student_id, name, email, phone, department, year_level, username) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                     (sid, name, email, phone, dept, yr, user))
                ]
                self.db.execute_transaction(ops)
            
            messagebox.showinfo("Success", f"Student profile record saved successfully.")
            self.clear_student_fields()
            self.refresh_student_table()
        except Exception:
            # Local simulation fallback
            if is_update:
                for x in self.local_students:
                    if x["student_id"] == sid:
                        x["name"] = name
                        x["email"] = email
                        x["phone"] = phone
                        x["department"] = dept
                        x["year_level"] = yr
            else:
                self.local_students.append({
                    "student_id": sid, "name": name, "email": email, "phone": phone, "department": dept, "year_level": yr, "username": user, "password": pwd
                })
            messagebox.showinfo("Success (Local)", "Student profile record saved locally.")
            self.clear_student_fields()
            self.refresh_student_table()

    def edit_student_action(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a student row to edit from the database matrix table grid.")
            return

        vals = self.student_tree.item(sel[0], "values")
        self.clear_student_fields()
        
        self.student_entries["Student ID *"].insert(0, vals[0])
        self.student_entries["Student ID *"].configure(state="readonly")
        self.student_entries["Full Name *"].insert(0, vals[1])
        self.student_entries["Email Address *"].insert(0, vals[2])
        self.student_entries["Phone Number *"].insert(0, vals[3])
        self.student_entries["Department"].set(vals[4])
        self.student_entries["Year Level"].set(vals[5])
        self.student_entries["Account Username *"].insert(0, vals[6])
        self.student_entries["Account Username *"].configure(state="disabled")

    def delete_student_action(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a row first.")
            return

        sid = self.student_tree.item(sel[0], "values")[0]
        user = self.student_tree.item(sel[0], "values")[6]
        
        ans = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student profile {sid} permanently from the dataset?")
        if not ans:
            return

        try:
            # Cascading delete handles students and grades, but we must delete user account manually
            ops = [
                ("DELETE FROM students WHERE student_id = %s", (sid,)),
                ("DELETE FROM users WHERE username = %s", (user,))
            ]
            self.db.execute_transaction(ops)
            messagebox.showinfo("Deleted", "Student profile has been deleted completely.")
            self.refresh_student_table()
        except Exception:
            self.local_students = [x for x in self.local_students if x["student_id"] != sid]
            self.local_grades = [x for x in self.local_grades if x["student_id"] != sid]
            messagebox.showinfo("Deleted (Local)", "Student deleted locally.")
            self.refresh_student_table()

    def filter_students_action(self):
        search_q = self.search_entry.get().strip().lower()
        dept_f = self.dept_filter.get()
        year_f = self.year_filter.get()

        try:
            # Build database filter query
            query = "SELECT s.student_id, s.name, s.email, s.phone, s.department, s.year_level, s.username FROM students s WHERE 1=1"
            params = []
            if search_q:
                query += " AND (s.student_id LIKE %s OR s.name LIKE %s)"
                params.append(f"%{search_q}%")
                params.append(f"%{search_q}%")
            if dept_f != "All Cases":
                query += " AND s.department = %s"
                params.append(dept_f)
            if year_f != "All Cases":
                query += " AND s.year_level = %s"
                params.append(year_f)
            
            results = self.db.execute_query(query, tuple(params))
            self.refresh_student_table(results)
        except Exception:
            # Fallback local filter
            filtered = []
            for s in self.local_students:
                match_s = not search_q or (search_q in s["student_id"].lower() or search_q in s["name"].lower())
                match_d = dept_f == "All Cases" or s["department"] == dept_f
                match_y = year_f == "All Cases" or s["year_level"] == year_f
                if match_s and match_d and match_y:
                    filtered.append(s)
            self.refresh_student_table(filtered)


    # ==========================
    # SCREEN 3: ACADEMIC GRADES WORKSPACE
    # ==========================
    def show_grades_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_grades)

        # 1. Target Student selection Panel
        target_frame = tk.Frame(self.workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        target_frame.pack(fill="x", padx=20, pady=(20, 10), ipady=12)

        tk.Label(target_frame, text="  Select Target Student:", font=("Arial", 11, "bold"), bg="#FFFFFF", fg="#2A3E5C").pack(side="left", padx=5)
        
        # Typable Student active selection combo
        self.grade_student_combo = ttk.Combobox(target_frame, font=("Arial", 11), width=45)
        self.grade_student_combo.pack(side="left", padx=10)
        self.grade_student_combo.bind("<KeyRelease>", self.on_student_combo_type)
        self.grade_student_combo.bind("<<ComboboxSelected>>", self.on_student_combo_selected)

        # 2. Main Entry Columns Setup
        workspace_body = tk.Frame(self.workspace, bg="#F3F4F6")
        workspace_body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Left entry column (white card)
        left_entry_card = tk.Frame(workspace_body, bg="#FFFFFF", width=400, highlightthickness=1, highlightbackground="#E5E7EB")
        left_entry_card.pack(side="left", fill="both", padx=(0, 15))
        left_entry_card.pack_propagate(False)

        # Right output & metric summary ledgers
        right_panel_container = tk.Frame(workspace_body, bg="#F3F4F6")
        right_panel_container.pack(side="right", fill="both", expand=True)

        # Left fields layout
        tk.Label(left_entry_card, text="Academic Scores Input Board", font=("Arial", 13, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))

        tk.Label(left_entry_card, text="Subject Name (CAPITALS only):", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF").pack(fill="x", padx=25, pady=(15, 2), anchor="w")
        self.sub_name_entry = tk.Entry(left_entry_card, font=("Arial", 11), bd=1, relief="solid")
        self.sub_name_entry.pack(fill="x", padx=25, ipady=5, pady=(0, 15))
        self.sub_name_entry.bind("<KeyRelease>", self.force_capital_subject)

        tk.Label(left_entry_card, text="Subject Numerical Score (0-100):", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF").pack(fill="x", padx=25, pady=(5, 2), anchor="w")
        self.sub_score_entry = tk.Entry(left_entry_card, font=("Arial", 11), bd=1, relief="solid")
        self.sub_score_entry.pack(fill="x", padx=25, ipady=5, pady=(0, 25))

        # Register button
        register_grade_btn = tk.Button(left_entry_card, text="⚡  Calculate & Save Grades", font=("Arial", 11, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=self.save_grade_action)
        register_grade_btn.pack(fill="x", padx=25, ipady=10, side="bottom", pady=30)

        # Right Metrics Summary Cards Frame
        metrics_frame = tk.Frame(right_panel_container, bg="#F3F4F6")
        metrics_frame.pack(fill="x", pady=(0, 15))

        card_a = tk.Frame(metrics_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_a.pack(side="left", fill="both", expand=True, marginRight=10, padx=(0, 10))
        tk.Label(card_a, text="CUMULATIVE PERCENTAGE", font=("Arial", 10, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=(12, 5))
        self.txt_percentage_var = tk.StringVar(value="0.00%")
        tk.Label(card_a, textvariable=self.txt_percentage_var, font=("Arial", 28, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(0, 12))

        card_b = tk.Frame(metrics_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_b.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(card_b, text="SCALED GPA SCORE", font=("Arial", 10, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=(12, 5))
        self.txt_gpa_var = tk.StringVar(value="0.00 / 4.00")
        tk.Label(card_b, textvariable=self.txt_gpa_var, font=("Arial", 28, "bold"), fg="#10B981", bg="#FFFFFF").pack(pady=(0, 12))

        # Right Data Grid Ledger
        ledger_wrapper = tk.Frame(right_panel_container, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        ledger_wrapper.pack(fill="both", expand=True)

        label_ledger = tk.Label(ledger_wrapper, text="Academic Scores Ledger Summary Matrix", font=("Arial", 12, "bold"), fg="#2A3E5C", bg="#FFFFFF")
        label_ledger.pack(pady=10, fill="x")

        self.grades_tree = ttk.Treeview(ledger_wrapper, columns=("StudentID", "SubjectsScores", "Percentage", "GPA"), show="headings")
        self.grades_tree.heading("StudentID", text="Student ID")
        self.grades_tree.heading("SubjectsScores", text="Dynamic Subjects & Grades List")
        self.grades_tree.heading("Percentage", text="Average Percentage")
        self.grades_tree.heading("GPA", text="GPA Rating")

        self.grades_tree.column("StudentID", width=120, anchor="center")
        self.grades_tree.column("SubjectsScores", width=420, anchor="w")
        self.grades_tree.column("Percentage", width=160, anchor="center")
        self.grades_tree.column("GPA", width=120, anchor="center")

        self.grades_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.populate_grade_combobox()
        self.refresh_grades_ledger()

    def force_capital_subject(self, event):
        pos = self.sub_name_entry.index(tk.INSERT)
        val = self.sub_name_entry.get().upper()
        self.sub_name_entry.delete(0, tk.END)
        self.sub_name_entry.insert(0, val)
        self.sub_name_entry.icursor(pos)

    def populate_grade_combobox(self, match_str=""):
        try:
            if match_str:
                query = "SELECT student_id, name FROM students WHERE student_id LIKE %s OR name LIKE %s ORDER BY name ASC"
                list_s = self.db.execute_query(query, (f"%{match_str}%", f"%{match_str}%"))
            else:
                query = "SELECT student_id, name FROM students ORDER BY name ASC"
                list_s = self.db.execute_query(query)
        except Exception:
            # Fallback local
            if match_str:
                list_s = [x for x in self.local_students if match_str.lower() in x["student_id"].lower() or match_str.lower() in x["name"].lower()]
            else:
                list_s = self.local_students

        box_vals = [f"{s.get('student_id', s.get('ID'))} - {s.get('name', s.get('Name'))}" for s in list_s]
        self.grade_student_combo['values'] = box_vals
        if box_vals and not match_str:
            self.grade_student_combo.set(box_vals[0])
            self.on_student_combo_selected(None)

    def on_student_combo_type(self, event):
        val = self.grade_student_combo.get()
        self.populate_grade_combobox(val)

    def on_student_combo_selected(self, event):
        val = self.grade_student_combo.get()
        if not val or " - " not in val:
            return
        sid = val.split(" - ")[0]
        self.update_student_gpa_cards(sid)

    def update_student_gpa_cards(self, sid):
        all_grades = []
        try:
            q = "SELECT score FROM grades WHERE student_id = %s"
            rows = self.db.execute_query(q, (sid,))
            all_grades = [float(r["score"]) for r in rows]
        except Exception:
            all_grades = [float(x["score"]) for x in self.local_grades if x["student_id"] == sid]

        if all_grades:
            percentage = calculate_percentage(all_grades)
            gpa = map_gpa(percentage)
            self.txt_percentage_var.set(f"{percentage:.2f}%")
            self.txt_gpa_var.set(f"{gpa:.2f} / 4.00")
        else:
            self.txt_percentage_var.set("0.00%")
            self.txt_gpa_var.set("0.00 / 4.00")

    def save_grade_action(self):
        combo_val = self.grade_student_combo.get()
        if not combo_val or " - " not in combo_val:
            messagebox.showerror("Error", "Please select a valid active student.")
            return
        
        sid = combo_val.split(" - ")[0]
        subj = self.sub_name_entry.get().strip().upper()
        score_str = self.sub_score_entry.get().strip()

        valid, err = validate_grade_fields(subj, score_str)
        if not valid:
            messagebox.showerror("Validation Error", err)
            return

        score = float(score_str)

        try:
            # Check duplicate / similar
            check_q = "SELECT score FROM grades WHERE student_id = %s AND UPPER(subject_name) = %s"
            dup = self.db.execute_query(check_q, (sid, subj))
            if dup:
                messagebox.showerror("Duplicate Subject", f"A score for subject {subj} already exists for this student profile.")
                return

            # ON DUPLICATE KEY UPDATE upsert transaction syntax standard
            upsert_q = "INSERT INTO grades (student_id, subject_name, score) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE score=%s"
            self.db.execute_non_query(upsert_q, (sid, subj, score, score))
            
            messagebox.showinfo("Success", f"Grade registered successfully for Subject {subj}.")
        except Exception:
            # Local simulation fallback duplicate check
            any_dup = any(x["student_id"] == sid and x["subject_name"].upper() == subj for x in self.local_grades)
            if any_dup:
                messagebox.showerror("Duplicate Subject", f"A score for subject {subj} already exists locally.")
                return
            self.local_grades.append({"student_id": sid, "subject_name": subj, "score": score})
            messagebox.showinfo("Success (Local)", "Grade registered locally.")

        self.sub_name_entry.delete(0, tk.END)
        self.sub_score_entry.delete(0, tk.END)
        self.update_student_gpa_cards(sid)
        self.refresh_grades_ledger()

    def refresh_grades_ledger(self):
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        try:
            # Aggregate subjects, percentage, and GPA for all students
            q_students = "SELECT student_id, name FROM students"
            student_list = self.db.execute_query(q_students)
        except Exception:
            student_list = self.local_students

        for student in student_list:
            sid = student.get("student_id", student.get("ID"))
            
            try:
                g_q = "SELECT subject_name, score FROM grades WHERE student_id = %s"
                rows = self.db.execute_query(g_q, (sid,))
            except Exception:
                rows = [x for x in self.local_grades if x["student_id"] == sid]

            if not rows:
                continue

            sub_strings = []
            scores = []
            for r in rows:
                sn = r.get("subject_name", r.get("subject_name"))
                sc = float(r.get("score"))
                scores.append(sc)
                sub_strings.append(f"{sn}: {sc:.0f}")

            list_desc = " | ".join(sub_strings)
            avg_p = calculate_percentage(scores)
            gpa = map_gpa(avg_p)

            self.grades_tree.insert("", "end", values=(sid, list_desc, f"{avg_p:.2f}%", f"{gpa:.2f} / 4.00"))


    # ==========================
    # SCREEN 4: MY PROFILE (STUDENT ONLY MODE)
    # ==========================
    def show_student_self_view(self):
        self.clear_workspace()

        # Target Student ID
        profile_card = tk.Frame(self.workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        profile_card.pack(fill="x", padx=30, pady=20, ipady=15)

        # Get Student Profile
        name = "Unknown Student"
        email = ""
        phone = ""
        dept = ""
        yr = ""
        sid = ""

        try:
            q_profile = "SELECT * FROM students WHERE username = %s"
            p_res = self.db.execute_query(q_profile, (self.username,))
            if p_res:
                name = p_res[0]["name"]
                email = p_res[0]["email"]
                phone = p_res[0]["phone"]
                dept = p_res[0]["department"]
                yr = p_res[0]["year_level"]
                sid = p_res[0]["student_id"]
        except Exception:
            # Search locally
            for s in self.local_students:
                if s["username"] == self.username:
                    name = s["name"]
                    email = s["email"]
                    phone = s["phone"]
                    dept = s["department"]
                    yr = s["year_level"]
                    sid = s["student_id"]
                    break
            if not sid:
                # Use default first student
                s = self.local_students[0]
                name = s["name"]
                email = s["email"]
                phone = s["phone"]
                dept = s["department"]
                yr = s["year_level"]
                sid = s["student_id"]

        tk.Label(profile_card, text=f"🎓 {name.upper()}  |  ACADEMIC PORTAL SHEET", font=("Arial", 16, "bold"), fg="#2A3E5C", bg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(5, 10))

        # Profile detail items
        meta_frame = tk.Frame(profile_card, bg="#FFFFFF")
        meta_frame.pack(fill="x", padx=15)

        details = [
            f"Student ID: {sid}", f"Department: {dept}", f"Academic Year: {yr}",
            f"Email Addr: {email}", f"Phone Number: {phone}"
        ]
        for d in details:
            lbl = tk.Label(meta_frame, text=d, font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w")
            lbl.pack(side="left", padx=15)

        # Bottom Columns Panel
        metrics_self_frame = tk.Frame(self.workspace, bg="#F3F4F6")
        metrics_self_frame.pack(fill="x", padx=30, pady=10)

        # Sub card Percentage
        card_p = tk.Frame(metrics_self_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_p.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(card_p, text="CUMULATIVE PERCENTAGE AVERAGE", font=("Arial", 10, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=10)
        
        # Sub card GPA
        card_g = tk.Frame(metrics_self_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_g.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(card_g, text="OVERALL SCALED GPA SCORE", font=("Arial", 10, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=10)

        lbl_p_var = tk.Label(card_p, text="0.00%", font=("Arial", 28, "bold"), fg="#2A3E5C", bg="#FFFFFF")
        lbl_p_var.pack(pady=(0, 10))

        lbl_g_var = tk.Label(card_g, text="0.00 / 4.00", font=("Arial", 28, "bold"), fg="#10B981", bg="#FFFFFF")
        lbl_g_var.pack(pady=(0, 10))

        # Ledger Details List
        ledger_panel = tk.Frame(self.workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        ledger_panel.pack(fill="both", expand=True, padx=30, pady=15)

        tk.Label(ledger_panel, text="Academic Grades Details Sheets", font=("Arial", 12, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=10)

        my_tree = ttk.Treeview(ledger_panel, columns=("Subject", "Grade", "Status"), show="headings")
        my_tree.heading("Subject", text="Subject Course")
        my_tree.heading("Grade", text="Subject Score")
        my_tree.heading("Status", text="Result Status")
        my_tree.column("Subject", anchor="w", width=300)
        my_tree.column("Grade", anchor="center", width=200)
        my_tree.column("Status", anchor="center", width=200)
        my_tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Fetch active records
        scores = []
        try:
            g_q = "SELECT subject_name, score FROM grades WHERE student_id = %s"
            rows = self.db.execute_query(g_q, (sid,))
        except Exception:
            rows = [x for x in self.local_grades if x["student_id"] == sid]

        for r in rows:
            sub = r.get("subject_name")
            sc = float(r.get("score"))
            status = "PASS" if sc >= 60.0 else "FAIL"
            scores.append(sc)
            my_tree.insert("", "end", values=(sub, f"{sc:.2f}", status))

        if scores:
            avg_p = calculate_percentage(scores)
            g_rate = map_gpa(avg_p)
            lbl_p_var.configure(text=f"{avg_p:.2f}%")
            lbl_g_var.configure(text=f"{g_rate:.2f} / 4.00")


    # ==========================
    # SCREEN 5: ALL DATA STUDENT TRANSCRIPT matrix
    # ==========================
    def show_reports_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_reports)

        container_frame = tk.Frame(self.workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        container_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container_frame, text="All Students Master Transcript Ledgers Report", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=15)

        # Create reports treeview
        self.report_tree = ttk.Treeview(container_frame, columns=("ID", "Name", "Department", "Year", "GradesSummary", "Percentage", "GPA"), show="headings")
        self.report_tree.heading("ID", text="StudentID")
        self.report_tree.heading("Name", text="Full Name")
        self.report_tree.heading("Department", text="Department")
        self.report_tree.heading("Year", text="Year")
        self.report_tree.heading("GradesSummary", text="Grades Breakdown")
        self.report_tree.heading("Percentage", text="Average %")
        self.report_tree.heading("GPA", text="GPA Scale")

        self.report_tree.column("ID", width=70, anchor="center")
        self.report_tree.column("Name", width=140, anchor="w")
        self.report_tree.column("Department", width=130, anchor="center")
        self.report_tree.column("Year", width=100, anchor="center")
        self.report_tree.column("GradesSummary", width=360, anchor="w")
        self.report_tree.column("Percentage", width=90, anchor="center")
        self.report_tree.column("GPA", width=90, anchor="center")

        self.report_tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.populate_master_report_table()

    def populate_master_report_table(self):
        for row in self.report_tree.get_children():
            self.report_tree.delete(row)

        try:
            q_students = "SELECT student_id, name, department, year_level FROM students"
            student_list = self.db.execute_query(q_students)
        except Exception:
            student_list = self.local_students

        for student in student_list:
            sid = student.get("student_id", student.get("ID"))
            name = student.get("name", student.get("Name"))
            dept = student.get("department", student.get("Department"))
            yr = student.get("year_level", student.get("Year"))

            try:
                g_q = "SELECT subject_name, score FROM grades WHERE student_id = %s"
                rows = self.db.execute_query(g_q, (sid,))
            except Exception:
                rows = [x for x in self.local_grades if x["student_id"] == sid]

            row_text_grades = []
            scores = []
            for r in rows:
                sn = r.get("subject_name")
                sc = float(r.get("score"))
                scores.append(sc)
                row_text_grades.append(f"{sn}:{sc:.0f}")

            list_desc = " | ".join(row_text_grades) if row_text_grades else "No grades registered"
            avg_p = calculate_percentage(scores) if scores else 0.0
            gpa = map_gpa(avg_p) if scores else 0.00

            self.report_tree.insert("", "end", values=(sid, name, dept, yr, list_desc, f"{avg_p:.2f}%" if scores else "-", f"{gpa:.2f}" if scores else "0.00"))

    def handle_logout(self):
        ans = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the active user session?")
        if ans:
            self.logout_cb()
