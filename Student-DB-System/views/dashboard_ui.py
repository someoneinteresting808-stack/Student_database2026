import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
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
        
        # Configure global Treeview font style (14px)
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14), rowheight=30)
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        
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
        self.subjects = [
            {"dept_name": "Computer Science", "subject_name": "CS"},
            {"dept_name": "Mathematics", "subject_name": "MATH"},
            {"dept_name": "Physics", "subject_name": "PHYSICS"},
            {"dept_name": "Business", "subject_name": "MARKETING"}
        ]

        self.editing_student_id = None
        self.editing_username = None

        self.load_departments()
        self.load_subjects()

        self.create_layouts()

    def load_departments(self):
        try:
            rows = self.db.execute_query("SELECT dept_name FROM departments ORDER BY dept_name ASC")
            if rows:
                self.departments = [r["dept_name"] for r in rows]
        except Exception:
            pass

    def load_subjects(self):
        try:
            rows = self.db.execute_query("SELECT dept_name, subject_name FROM subjects ORDER BY dept_name ASC, subject_name ASC")
            if rows:
                self.subjects = [{"dept_name": r["dept_name"], "subject_name": r["subject_name"]} for r in rows]
            else:
                self.subjects = []
        except Exception:
            pass

    def create_layouts(self):
        # 1. Sidebar Panel (260px wide) using customtkinter CTkFrame
        self.sidebar = ctk.CTkFrame(self.root, fg_color="#2A3E5C", width=260, corner_radius=0)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        # Admin Header
        header_title = "SDMS ADMIN" if self.role == "teacher" else "STUDENT PORTAL"
        ctk.CTkLabel(self.sidebar, text=header_title, font=("Arial", 14, "bold"), text_color="#FFFFFF").pack(pady=(40, 50))

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
        self.btn_students = ctk.CTkButton(self.sidebar, text="👤  Manage Students", font=("Arial", 13), text_color="#FFFFFF",
                                         fg_color="#1E2A3C", hover_color="#1A2536", anchor="w", corner_radius=8, height=45,
                                         command=self.show_student_management)
        self.btn_students.pack(fill="x", pady=4, padx=10)

        self.btn_grades = ctk.CTkButton(self.sidebar, text="📊  Manage Grades", font=("Arial", 13), text_color="#FFFFFF",
                                       fg_color="#2A3E5C", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                       command=self.show_grades_management)
        self.btn_grades.pack(fill="x", pady=4, padx=10)

        self.btn_departments = ctk.CTkButton(self.sidebar, text="🏢  Manage Departments", font=("Arial", 13), text_color="#FFFFFF",
                                            fg_color="#2A3E5C", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                            command=self.show_departments_management)
        self.btn_departments.pack(fill="x", pady=4, padx=10)

        self.btn_subjects = ctk.CTkButton(self.sidebar, text="📚  Manage Subjects", font=("Arial", 13), text_color="#FFFFFF",
                                          fg_color="#2A3E5C", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                          command=self.show_subjects_management)
        self.btn_subjects.pack(fill="x", pady=4, padx=10)

        self.btn_reports = ctk.CTkButton(self.sidebar, text="📋  All Student Reports", font=("Arial", 13), text_color="#FFFFFF",
                                         fg_color="#2A3E5C", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                         command=self.show_reports_management)
        self.btn_reports.pack(fill="x", pady=4, padx=10)

        self.btn_accounts = ctk.CTkButton(self.sidebar, text="🔑  Manage Accounts", font=("Arial", 13), text_color="#FFFFFF",
                                         fg_color="#2A3E5C", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                         command=self.show_accounts_management)
        self.btn_accounts.pack(fill="x", pady=4, padx=10)

        # Logout at absolute bottom
        logout_btn = ctk.CTkButton(self.sidebar, text="🚪  Log Out", font=("Arial", 13, "bold"), text_color="#EF4444",
                                  fg_color="transparent", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                  command=self.handle_logout)
        logout_btn.pack(side="bottom", fill="x", pady=(0, 40), padx=10)

        # Maximize right above logout
        self.btn_fullscreen = ctk.CTkButton(self.sidebar, text="🖥️  Maximize Window", font=("Arial", 13), text_color="#FFFFFF",
                                           fg_color="transparent", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                           command=self.toggle_fullscreen)
        self.btn_fullscreen.pack(side="bottom", fill="x", pady=(0, 10), padx=10)

    def create_student_nav(self):
        ctk.CTkLabel(self.sidebar, text=f"Welcome, {self.username}", font=("Arial", 11, "italic"), text_color="#E5E7EB").pack(pady=(0, 30))
        
        self.btn_self = ctk.CTkButton(self.sidebar, text="👤  My Profile & Grades", font=("Arial", 13), text_color="#FFFFFF",
                                     fg_color="#1E2A3C", hover_color="#1A2536", anchor="w", corner_radius=8, height=45)
        self.btn_self.pack(fill="x", pady=4, padx=10)

        # Logout at absolute bottom
        logout_btn = ctk.CTkButton(self.sidebar, text="🚪  Log Out", font=("Arial", 13, "bold"), text_color="#EF4444",
                                  fg_color="transparent", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                  command=self.handle_logout)
        logout_btn.pack(side="bottom", fill="x", pady=(0, 40), padx=10)

        # Maximize right above logout
        self.btn_fullscreen_stud = ctk.CTkButton(self.sidebar, text="🖥️  Maximize Window", font=("Arial", 13), text_color="#FFFFFF",
                                                fg_color="transparent", hover_color="#1E2A3C", anchor="w", corner_radius=8, height=45,
                                                command=self.toggle_fullscreen)
        self.btn_fullscreen_stud.pack(side="bottom", fill="x", pady=(0, 10), padx=10)

    def clear_workspace(self):
        for widget in self.workspace.winfo_children():
            widget.destroy()

    def set_active_button(self, active_btn):
        if self.role == "teacher":
            self.btn_students.configure(fg_color="#2A3E5C")
            self.btn_grades.configure(fg_color="#2A3E5C")
            self.btn_departments.configure(fg_color="#2A3E5C")
            self.btn_subjects.configure(fg_color="#2A3E5C")
            self.btn_reports.configure(fg_color="#2A3E5C")
            self.btn_accounts.configure(fg_color="#2A3E5C")
            active_btn.configure(fg_color="#1E2A3C")

    def toggle_fullscreen(self):
        try:
            current_state = self.root.state()
            if current_state == "zoomed":
                self.root.state("normal")
                self.root.geometry("1440x1024")
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width // 2) - (1440 // 2)
                y = (screen_height // 2) - (1024 // 2)
                self.root.geometry(f"1440x1024+{max(0, x)}+{max(0, y)}")
                if hasattr(self, "btn_fullscreen"):
                    self.btn_fullscreen.configure(text="🖥️  Maximize Window")
                if hasattr(self, "btn_fullscreen_stud"):
                    self.btn_fullscreen_stud.configure(text="🖥️  Maximize Window")
            else:
                self.root.state("zoomed")
                if hasattr(self, "btn_fullscreen"):
                    self.btn_fullscreen.configure(text="🖥️  Restore Window")
                if hasattr(self, "btn_fullscreen_stud"):
                    self.btn_fullscreen_stud.configure(text="🖥️  Restore Window")
        except Exception:
            # Fallback to fullscreen attribute if state('zoomed') is not supported on some platforms
            is_fullscreen = self.root.attributes("-fullscreen")
            new_state = not is_fullscreen
            self.root.attributes("-fullscreen", new_state)
            btn_txt = "🖥️  Restore Window" if new_state else "🖥️  Maximize Window"
            if hasattr(self, "btn_fullscreen"):
                self.btn_fullscreen.configure(text=btn_txt)
            if hasattr(self, "btn_fullscreen_stud"):
                self.btn_fullscreen_stud.configure(text=btn_txt)

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
            tk.Label(scrollable_frame, text=label, font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", pady=(8, 2))
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
        save_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))

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
        edit_btn.pack(side="left", ipady=8, padx=(0, 10))

        delete_btn = tk.Button(grid_btn_frame, text="Delete Selected Row", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=self.delete_student_action)
        delete_btn.pack(side="left", ipady=8)

        self.refresh_student_table()

    def clear_student_fields(self):
        self.editing_student_id = None
        self.editing_username = None
        for label, widget in self.student_entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set("")
            else:
                widget.configure(state="normal")
                widget.delete(0, tk.END)

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

        is_update = (self.editing_student_id is not None)

        valid, err = validate_student_fields(sid, name, email, phone, dept, yr, user, pwd, not is_update)
        if not valid:
            messagebox.showerror("Validation Error", err)
            return

        try:
            if is_update:
                # Edit record
                # Disable FK checks to update keys smoothly
                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 0")
                
                # Update users table (if username was edited)
                self.db.execute_non_query(
                    "UPDATE users SET username = %s WHERE username = %s",
                    (user, self.editing_username)
                )
                
                if pwd.strip():
                    self.db.execute_non_query(
                        "UPDATE users SET password = %s WHERE username = %s",
                        (pwd, user)
                    )
                
                # Update students table
                self.db.execute_non_query(
                    "UPDATE students SET student_id = %s, name = %s, email = %s, phone = %s, department = %s, year_level = %s, username = %s WHERE student_id = %s",
                    (sid, name, email, phone, dept, yr, user, self.editing_student_id)
                )
                
                # Update grades table (cascade update)
                self.db.execute_non_query(
                    "UPDATE grades SET student_id = %s WHERE student_id = %s",
                    (sid, self.editing_student_id)
                )
                
                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 1")
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
        except Exception as e:
            # Local simulation fallback
            if is_update:
                for x in self.local_students:
                    if x["student_id"] == self.editing_student_id:
                        x["student_id"] = sid
                        x["name"] = name
                        x["email"] = email
                        x["phone"] = phone
                        x["department"] = dept
                        x["year_level"] = yr
                        x["username"] = user
                        if pwd.strip():
                            x["password"] = pwd
                for g in self.local_grades:
                    if g["student_id"] == self.editing_student_id:
                        g["student_id"] = sid
            else:
                self.local_students.append({
                    "student_id": sid, "name": name, "email": email, "phone": phone, "department": dept, "year_level": yr, "username": user, "password": pwd
                })
            messagebox.showinfo("Success (Local)", f"Student profile record saved locally/manually: {e}")
            self.clear_student_fields()
            self.refresh_student_table()

    def edit_student_action(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a student row to edit from the database matrix table grid.")
            return

        vals = self.student_tree.item(sel[0], "values")
        self.clear_student_fields()
        
        self.editing_student_id = vals[0]
        self.editing_username = vals[6]
        
        self.student_entries["Student ID *"].configure(state="normal")
        self.student_entries["Account Username *"].configure(state="normal")
        
        self.student_entries["Student ID *"].insert(0, vals[0])
        self.student_entries["Full Name *"].insert(0, vals[1])
        self.student_entries["Email Address *"].insert(0, vals[2])
        self.student_entries["Phone Number *"].insert(0, vals[3])
        self.student_entries["Department"].set(vals[4])
        self.student_entries["Year Level"].set(vals[5])
        self.student_entries["Account Username *"].insert(0, vals[6])

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
        target_frame = tk.Frame(self.workspace, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        target_frame.pack(fill="x", padx=20, pady=(20, 10), ipady=12)

        tk.Label(target_frame, text="  Select Target Student:", font=("Arial", 14, "bold"), bg="#FFFFFF", fg="#2A3E5C").pack(side="left", padx=5)
        
        # Typable Student active selection combo
        self.grade_student_combo = ttk.Combobox(target_frame, font=("Arial", 14), width=35)
        self.grade_student_combo.pack(side="left", padx=10)
        self.grade_student_combo.bind("<KeyRelease>", self.on_student_combo_type)
        self.grade_student_combo.bind("<<ComboboxSelected>>", self.on_student_combo_selected)

        # Top Sorters / Filters
        tk.Label(target_frame, text="Filter Dept:", font=("Arial", 14), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(15, 2))
        self.grade_dept_filter = ttk.Combobox(target_frame, values=["All Departments"] + self.departments, state="readonly", font=("Arial", 14), width=15)
        self.grade_dept_filter.pack(side="left", padx=5)
        self.grade_dept_filter.set("All Departments")
        self.grade_dept_filter.bind("<<ComboboxSelected>>", lambda e: [self.populate_grade_combobox(), self.refresh_grades_ledger()])

        tk.Label(target_frame, text="Year:", font=("Arial", 14), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(10, 2))
        self.grade_year_filter = ttk.Combobox(target_frame, values=["All Years"] + self.years, state="readonly", font=("Arial", 14), width=15)
        self.grade_year_filter.pack(side="left", padx=5)
        self.grade_year_filter.set("All Years")
        self.grade_year_filter.bind("<<ComboboxSelected>>", lambda e: [self.populate_grade_combobox(), self.refresh_grades_ledger()])

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
        tk.Label(left_entry_card, text="Academic Scores Input Board", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))

        tk.Label(left_entry_card, text="Subject Name:", font=("Arial", 14), fg="#4B5563", bg="#FFFFFF").pack(fill="x", padx=25, pady=(15, 2), anchor="w")
        self.subject_combo = ttk.Combobox(left_entry_card, values=self.subjects, state="readonly", font=("Arial", 14))
        self.subject_combo.pack(fill="x", padx=25, ipady=3, pady=(0, 15))
        if self.subjects:
            self.subject_combo.set(self.subjects[0])

        tk.Label(left_entry_card, text="Subject Numerical Score (0-100):", font=("Arial", 14), fg="#4B5563", bg="#FFFFFF").pack(fill="x", padx=25, pady=(5, 2), anchor="w")
        self.sub_score_entry = tk.Entry(left_entry_card, font=("Arial", 14), bd=1, relief="solid")
        self.sub_score_entry.pack(fill="x", padx=25, ipady=5, pady=(0, 25))

        # Register button
        register_grade_btn = tk.Button(left_entry_card, text="⚡  Calculate & Save Grades", font=("Arial", 14, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=self.save_grade_action)
        register_grade_btn.pack(fill="x", padx=25, ipady=10, side="bottom", pady=30)

        # Right Metrics Summary Cards Frame
        metrics_frame = tk.Frame(right_panel_container, bg="#F3F4F6")
        metrics_frame.pack(fill="x", pady=(0, 15))

        card_a = tk.Frame(metrics_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_a.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(card_a, text="CUMULATIVE PERCENTAGE", font=("Arial", 12, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=(12, 5))
        self.txt_percentage_var = tk.StringVar(value="0.00%")
        tk.Label(card_a, textvariable=self.txt_percentage_var, font=("Arial", 28, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(0, 12))

        card_b = tk.Frame(metrics_frame, bg="#FFFFFF", bd=1, relief="solid")
        card_b.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(card_b, text="SCALED GPA SCORE", font=("Arial", 12, "bold"), fg="#9CA3AF", bg="#FFFFFF").pack(pady=(12, 5))
        self.txt_gpa_var = tk.StringVar(value="0.00 / 4.00")
        tk.Label(card_b, textvariable=self.txt_gpa_var, font=("Arial", 28, "bold"), fg="#10B981", bg="#FFFFFF").pack(pady=(0, 12))

        # Right Data Grid Ledger
        ledger_wrapper = tk.Frame(right_panel_container, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        ledger_wrapper.pack(fill="both", expand=True)

        label_ledger = tk.Label(ledger_wrapper, text="Academic Scores Ledger Summary Matrix", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF")
        label_ledger.pack(pady=10, fill="x")

        self.grades_tree = ttk.Treeview(ledger_wrapper, columns=("StudentID", "StudentName", "SubjectsScores", "Percentage", "GPA"), show="headings")
        self.grades_tree.heading("StudentID", text="Student ID")
        self.grades_tree.heading("StudentName", text="Student Name")
        self.grades_tree.heading("SubjectsScores", text="Dynamic Subjects & Grades List")
        self.grades_tree.heading("Percentage", text="Average Percentage")
        self.grades_tree.heading("GPA", text="GPA Rating")

        self.grades_tree.column("StudentID", width=90, anchor="center")
        self.grades_tree.column("StudentName", width=140, anchor="w")
        self.grades_tree.column("SubjectsScores", width=380, anchor="w")
        self.grades_tree.column("Percentage", width=130, anchor="center")
        self.grades_tree.column("GPA", width=100, anchor="center")

        self.grades_tree.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Button row below grades ledger
        grid_btn_frame = tk.Frame(ledger_wrapper, bg="#FFFFFF")
        grid_btn_frame.pack(fill="x", padx=15, pady=(0, 15))

        delete_grade_btn = tk.Button(grid_btn_frame, text="🗑️  Delete Selected Grade", font=("Arial", 14, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=self.delete_grade_action)
        delete_grade_btn.pack(side="right")

        self.populate_grade_combobox()
        self.refresh_grades_ledger()

    def populate_grade_combobox(self, match_str=""):
        dept_val = self.grade_dept_filter.get()
        year_val = self.grade_year_filter.get()
        
        try:
            query = "SELECT student_id, name FROM students WHERE 1=1"
            params = []
            if dept_val and dept_val != "All Departments":
                query += " AND department = %s"
                params.append(dept_val)
            if year_val and year_val != "All Years":
                query += " AND year_level = %s"
                params.append(year_val)
                
            if match_str:
                query += " AND (student_id LIKE %s OR name LIKE %s)"
                params.extend([f"%{match_str}%", f"%{match_str}%"])
                
            query += " ORDER BY name ASC"
            list_s = self.db.execute_query(query, tuple(params))
        except Exception:
            # Fallback local
            list_s = []
            for s in self.local_students:
                match_d = (not dept_val or dept_val == "All Departments" or s["department"] == dept_val)
                match_y = (not year_val or year_val == "All Years" or s["year_level"] == year_val)
                match_m = (not match_str or match_str.lower() in s["student_id"].lower() or match_str.lower() in s["name"].lower())
                if match_d and match_y and match_m:
                    list_s.append(s)

        box_vals = [f"{s.get('student_id', s.get('ID'))} - {s.get('name', s.get('Name'))}" for s in list_s]
        self.grade_student_combo['values'] = box_vals
        if box_vals and not match_str:
            self.grade_student_combo.set(box_vals[0])
            self.on_student_combo_selected(None)
        elif not box_vals:
            self.grade_student_combo.set("")
            self.txt_percentage_var.set("0.00%")
            self.txt_gpa_var.set("0.00 / 4.00")

    def on_student_combo_type(self, event):
        val = self.grade_student_combo.get()
        self.populate_grade_combobox(val)

    def on_student_combo_selected(self, event):
        val = self.grade_student_combo.get()
        if not val or " - " not in val:
            return
        sid = val.split(" - ")[0]
        self.update_student_gpa_cards(sid)
        self.update_subject_dropdown_for_student(sid)

    def update_subject_dropdown_for_student(self, sid):
        dept = None
        try:
            res = self.db.execute_query("SELECT department FROM students WHERE student_id = %s", (sid,))
            if res:
                dept = res[0]["department"]
        except Exception:
            for s in self.local_students:
                if s["student_id"] == sid:
                    dept = s["department"]
                    break
        
        filtered_subs = []
        if dept:
            for sub in self.subjects:
                if isinstance(sub, dict):
                    if sub.get("dept_name") == dept:
                        filtered_subs.append(sub.get("subject_name"))
                else:
                    filtered_subs.append(str(sub))
        
        self.subject_combo['values'] = filtered_subs
        if filtered_subs:
            self.subject_combo.set(filtered_subs[0])
        else:
            self.subject_combo.set("")

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
        subj = self.subject_combo.get().strip().upper()
        score_str = self.sub_score_entry.get().strip()

        valid, err = validate_grade_fields(subj, score_str)
        if not valid:
            messagebox.showerror("Validation Error", err)
            return

        score = float(score_str)

        try:
            # ON DUPLICATE KEY UPDATE upsert transaction syntax standard
            upsert_q = "INSERT INTO grades (student_id, subject_name, score) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE score=%s"
            self.db.execute_non_query(upsert_q, (sid, subj, score, score))
            messagebox.showinfo("Success", f"Grade registered successfully for Subject {subj}.")
        except Exception as e:
            # Local simulation fallback check & update
            updated = False
            for x in self.local_grades:
                if x["student_id"] == sid and x["subject_name"].upper() == subj:
                    x["score"] = score
                    updated = True
                    break
            if not updated:
                self.local_grades.append({"student_id": sid, "subject_name": subj, "score": score})
            messagebox.showinfo("Success (Local)", f"Grade registered locally: {e}")

        self.sub_score_entry.delete(0, tk.END)
        self.update_student_gpa_cards(sid)
        self.refresh_grades_ledger()

    def refresh_grades_ledger(self):
        for row in self.grades_tree.get_children():
            self.grades_tree.delete(row)

        dept_val = self.grade_dept_filter.get()
        year_val = self.grade_year_filter.get()

        try:
            # Aggregate subjects, percentage, and GPA for all students
            q_students = "SELECT student_id, name FROM students WHERE 1=1"
            params = []
            if dept_val and dept_val != "All Departments":
                q_students += " AND department = %s"
                params.append(dept_val)
            if year_val and year_val != "All Years":
                q_students += " AND year_level = %s"
                params.append(year_val)
            q_students += " ORDER BY name ASC"
            student_list = self.db.execute_query(q_students, tuple(params))
        except Exception:
            student_list = []
            for s in self.local_students:
                match_d = (not dept_val or dept_val == "All Departments" or s["department"] == dept_val)
                match_y = (not year_val or year_val == "All Years" or s["year_level"] == year_val)
                if match_d and match_y:
                    student_list.append(s)

        for student in student_list:
            sid = student.get("student_id", student.get("ID"))
            sname = student.get("name", student.get("Name"))
            
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
                sn = r.get("subject_name")
                sc = float(r.get("score"))
                scores.append(sc)
                sub_strings.append(f"{sn}: {sc:.0f}")

            list_desc = " | ".join(sub_strings)
            avg_p = calculate_percentage(scores)
            gpa = map_gpa(avg_p)

            self.grades_tree.insert("", "end", values=(sid, sname, list_desc, f"{avg_p:.2f}%", f"{gpa:.2f} / 4.00"))

    def delete_grade_action(self):
        sel = self.grades_tree.selection()
        if not sel:
            messagebox.showwarning("Selection Required", "Please select a student row from the grades ledger.")
            return
        
        vals = self.grades_tree.item(sel[0], "values")
        sid = vals[0]
        sname = vals[1]
        
        # Get all grades for this student
        try:
            rows = self.db.execute_query("SELECT subject_name, score FROM grades WHERE student_id = %s", (sid,))
        except Exception:
            rows = [x for x in self.local_grades if x["student_id"] == sid]
            
        if not rows:
            messagebox.showinfo("No Grades", f"No grades found for student {sname}.")
            return
            
        # Create pop-up window
        popup = tk.Toplevel(self.root)
        popup.title(f"Manage Grades - {sname}")
        popup.geometry("350x230")
        popup.resizable(False, False)
        popup.configure(bg="#F3F4F6")
        
        # Center popup
        px = self.root.winfo_x() + (self.root.winfo_width() // 2) - 175
        py = self.root.winfo_y() + (self.root.winfo_height() // 2) - 115
        popup.geometry(f"350x230+{px}+{py}")
        
        tk.Label(popup, text=f"Manage Grades for {sname}", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#F3F4F6").pack(pady=10)
        tk.Label(popup, text="Select Subject Grade to Delete:", font=("Arial", 11), fg="#4B5563", bg="#F3F4F6").pack(pady=5)
        
        grade_vals = [f"{r['subject_name']} - {float(r['score']):.0f}" for r in rows]
        combo = ttk.Combobox(popup, values=grade_vals, state="readonly", font=("Arial", 11))
        combo.pack(pady=5, fill="x", padx=40)
        if grade_vals:
            combo.set(grade_vals[0])
            
        def do_delete():
            sel_grade = combo.get()
            if not sel_grade:
                return
            sub_name = sel_grade.split(" - ")[0]
            try:
                self.db.execute_non_query("DELETE FROM grades WHERE student_id = %s AND subject_name = %s", (sid, sub_name))
            except Exception:
                self.local_grades = [x for x in self.local_grades if not (x["student_id"] == sid and x["subject_name"] == sub_name)]
            messagebox.showinfo("Success", f"Grade for {sub_name} deleted successfully.")
            popup.destroy()
            self.update_student_gpa_cards(sid)
            self.refresh_grades_ledger()
            
        btn = tk.Button(popup, text="🗑️  Delete Grade", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=do_delete)
        btn.pack(pady=20, fill="x", padx=40, ipady=5)


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

        tk.Label(profile_card, text="🎓 " + name.upper() + "  |  ACADEMIC PORTAL SHEET", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(5, 10))

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

        # Filters Bar Frame
        filter_bar = tk.Frame(container_frame, bg="#FFFFFF")
        filter_bar.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(filter_bar, text="Sort By:", font=("Arial", 11), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(5, 2))
        self.report_sort_filter = ttk.Combobox(filter_bar, values=[
            "Default", "Highest Scores First", "Lowest Scores First", "Alphabetically (A-Z)", "Alphabetically (Z-A)"
        ], state="readonly", font=("Arial", 11), width=20)
        self.report_sort_filter.pack(side="left", padx=5)
        self.report_sort_filter.set("Default")
        self.report_sort_filter.bind("<<ComboboxSelected>>", lambda e: self.populate_master_report_table())

        tk.Label(filter_bar, text="Dept:", font=("Arial", 10), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(15, 2))
        self.report_dept_filter = ttk.Combobox(filter_bar, values=["All Departments"] + self.departments, state="readonly", font=("Arial", 10), width=18)
        self.report_dept_filter.pack(side="left", padx=5)
        self.report_dept_filter.set("All Departments")
        self.report_dept_filter.bind("<<ComboboxSelected>>", lambda e: self.populate_master_report_table())

        tk.Label(filter_bar, text="Year:", font=("Arial", 10), bg="#FFFFFF", fg="#4B5563").pack(side="left", padx=(15, 2))
        self.report_year_filter = ttk.Combobox(filter_bar, values=["All Years"] + self.years, state="readonly", font=("Arial", 10), width=15)
        self.report_year_filter.pack(side="left", padx=5)
        self.report_year_filter.set("All Years")
        self.report_year_filter.bind("<<ComboboxSelected>>", lambda e: self.populate_master_report_table())

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

        dept_val = self.report_dept_filter.get()
        year_val = self.report_year_filter.get()

        try:
            q_students = "SELECT student_id, name, department, year_level FROM students WHERE 1=1"
            params = []
            if dept_val and dept_val != "All Departments":
                q_students += " AND department = %s"
                params.append(dept_val)
            if year_val and year_val != "All Years":
                q_students += " AND year_level = %s"
                params.append(year_val)
            student_list = self.db.execute_query(q_students, tuple(params))
        except Exception:
            student_list = []
            for s in self.local_students:
                match_d = (not dept_val or dept_val == "All Departments" or s.get("department") == dept_val)
                match_y = (not year_val or year_val == "All Years" or s.get("year_level") == year_val)
                if match_d and match_y:
                    student_list.append(s)

        report_data = []
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

            report_data.append({
                "id": sid,
                "name": name,
                "dept": dept,
                "year": yr,
                "desc": list_desc,
                "percentage": avg_p,
                "gpa": gpa,
                "has_scores": bool(scores)
            })

        sort_val = self.report_sort_filter.get()
        if sort_val == "Highest Scores First":
            report_data.sort(key=lambda x: x["percentage"], reverse=True)
        elif sort_val == "Lowest Scores First":
            report_data.sort(key=lambda x: x["percentage"])
        elif sort_val == "Alphabetically (A-Z)":
            report_data.sort(key=lambda x: x["name"].lower())
        elif sort_val == "Alphabetically (Z-A)":
            report_data.sort(key=lambda x: x["name"].lower(), reverse=True)

        for r in report_data:
            self.report_tree.insert("", "end", values=(
                r["id"], r["name"], r["dept"], r["year"], r["desc"],
                f"{r['percentage']:.2f}%" if r["has_scores"] else "-",
                f"{r['gpa']:.2f}" if r["has_scores"] else "0.00"
            ))

    def show_departments_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_departments)

        # Left / Right Split Layout
        left_panel = tk.Frame(self.workspace, bg="#FFFFFF", width=380, highlightthickness=1, highlightbackground="#E5E7EB")
        left_panel.pack(side="left", fill="both", padx=20, pady=20)
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(self.workspace, bg="#F3F4F6")
        right_panel.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # Left Form
        tk.Label(left_panel, text="Manage Department", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))
        
        tk.Label(left_panel, text="Department Name *", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", padx=20, pady=(15, 2))
        self.dept_name_entry = tk.Entry(left_panel, font=("Arial", 11), bd=1, relief="solid")
        self.dept_name_entry.pack(fill="x", padx=20, ipady=5, pady=(0, 25))

        btn_frame = tk.Frame(left_panel, bg="#FFFFFF")
        btn_frame.pack(fill="x", side="bottom", pady=25, padx=20)

        self.editing_dept_name = None
        
        def save_dept():
            name = self.dept_name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Department name cannot be empty.")
                return
            
            try:
                if self.editing_dept_name:
                    # Update department name
                    self.db.execute_non_query("UPDATE departments SET dept_name = %s WHERE dept_name = %s", (name, self.editing_dept_name))
                    # Cascade update students
                    self.db.execute_non_query("UPDATE students SET department = %s WHERE department = %s", (name, self.editing_dept_name))
                    messagebox.showinfo("Success", "Department updated successfully.")
                else:
                    # Insert new department
                    self.db.execute_non_query("INSERT INTO departments (dept_name) VALUES (%s)", (name,))
                    messagebox.showinfo("Success", "Department added successfully.")
            except Exception as e:
                # Local
                if self.editing_dept_name:
                    if self.editing_dept_name in self.departments:
                        self.departments.remove(self.editing_dept_name)
                    self.departments.append(name)
                    for s in self.local_students:
                        if s["department"] == self.editing_dept_name:
                            s["department"] = name
                else:
                    self.departments.append(name)
                messagebox.showinfo("Success (Local)", f"Saved locally: {e}")
                
            self.dept_name_entry.delete(0, tk.END)
            self.editing_dept_name = None
            self.load_departments()
            refresh_depts()

        save_btn = tk.Button(btn_frame, text="Save Department", font=("Arial", 11, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=save_dept)
        save_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))

        def clear_dept():
            self.dept_name_entry.delete(0, tk.END)
            self.editing_dept_name = None
            
        clear_btn = tk.Button(btn_frame, text="Clear", font=("Arial", 11, "bold"), bg="#9CA3AF", fg="#FFFFFF", bd=0, cursor="hand2", command=clear_dept)
        clear_btn.pack(side="right", fill="x", expand=True, ipady=8, padx=(5, 0))

        # Right Tree view
        tree_frame = tk.Frame(right_panel, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        tree_frame.pack(fill="both", expand=True)
        
        tk.Label(tree_frame, text="Department Records Directory", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=10)

        self.dept_tree = ttk.Treeview(tree_frame, columns=("DeptName",), show="headings")
        self.dept_tree.heading("DeptName", text="Department Name")
        self.dept_tree.column("DeptName", anchor="w")
        self.dept_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Buttons under Treeview
        tree_btn_frame = tk.Frame(right_panel, bg="#F3F4F6")
        tree_btn_frame.pack(fill="x", pady=10)

        def edit_dept():
            sel = self.dept_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a department.")
                return
            val = self.dept_tree.item(sel[0], "values")[0]
            self.dept_name_entry.delete(0, tk.END)
            self.dept_name_entry.insert(0, val)
            self.editing_dept_name = val

        edit_btn = tk.Button(tree_btn_frame, text="Edit Selected", font=("Arial", 11, "bold"), bg="#2A3E5C", fg="#FFFFFF", bd=0, cursor="hand2", command=edit_dept)
        edit_btn.pack(side="left", ipady=8, padx=(0, 10))

        def delete_dept():
            sel = self.dept_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a department.")
                return
            val = self.dept_tree.item(sel[0], "values")[0]
            
            ans = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete department '{val}'?")
            if not ans:
                return
                
            try:
                self.db.execute_non_query("DELETE FROM departments WHERE dept_name = %s", (val,))
                # Set students belonging to this department to 'Unassigned'
                self.db.execute_non_query("UPDATE students SET department = 'Unassigned' WHERE department = %s", (val,))
                messagebox.showinfo("Success", "Department deleted successfully.")
            except Exception as e:
                if val in self.departments:
                    self.departments.remove(val)
                for s in self.local_students:
                    if s["department"] == val:
                        s["department"] = "Unassigned"
                messagebox.showinfo("Success (Local)", f"Deleted locally: {e}")

            self.load_departments()
            refresh_depts()

        delete_btn = tk.Button(tree_btn_frame, text="Delete Selected", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=delete_dept)
        delete_btn.pack(side="left", ipady=8)

        def refresh_depts():
            for item in self.dept_tree.get_children():
                self.dept_tree.delete(item)
            for d in self.departments:
                self.dept_tree.insert("", "end", values=(d,))

        refresh_depts()

    def show_subjects_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_subjects)

        # Configure larger Treeview font style (14px)
        style = ttk.Style()
        style.configure("Subjects.Treeview", font=("Arial", 14), rowheight=30)
        style.configure("Subjects.Treeview.Heading", font=("Arial", 14, "bold"))

        # Left / Right Split Layout (width 380 for 14px font)
        left_panel = tk.Frame(self.workspace, bg="#FFFFFF", width=380, highlightthickness=1, highlightbackground="#E5E7EB")
        left_panel.pack(side="left", fill="both", padx=20, pady=20)
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(self.workspace, bg="#F3F4F6")
        right_panel.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # Left Form
        tk.Label(left_panel, text="Manage Subject", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))
        
        tk.Label(left_panel, text="Choose Department *", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", padx=20, pady=(15, 2))
        self.subject_dept_combo = ttk.Combobox(left_panel, values=self.departments, state="readonly", font=("Arial", 11))
        self.subject_dept_combo.pack(fill="x", padx=20, ipady=4, pady=(0, 15))
        if self.departments:
            self.subject_dept_combo.set(self.departments[0])

        tk.Label(left_panel, text="Subject Name * (CAPITALS)", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", padx=20, pady=(5, 2))
        self.subject_name_entry = tk.Entry(left_panel, font=("Arial", 11), bd=1, relief="solid")
        self.subject_name_entry.pack(fill="x", padx=20, ipady=6, pady=(0, 25))
        
        def force_caps(e):
            pos = self.subject_name_entry.index(tk.INSERT)
            val = self.subject_name_entry.get().upper()
            self.subject_name_entry.delete(0, tk.END)
            self.subject_name_entry.insert(0, val)
            self.subject_name_entry.icursor(pos)
        self.subject_name_entry.bind("<KeyRelease>", force_caps)

        btn_frame = tk.Frame(left_panel, bg="#FFFFFF")
        btn_frame.pack(fill="x", side="bottom", pady=25, padx=20)

        self.editing_subject_name = None
        self.editing_subject_dept = None
        
        def save_subject():
            dept = self.subject_dept_combo.get().strip()
            name = self.subject_name_entry.get().strip().upper()
            if not dept or not name:
                messagebox.showerror("Error", "Department and Subject Name cannot be empty.")
                return
            
            try:
                if self.editing_subject_name and self.editing_subject_dept:
                    # Update subject name for this department
                    self.db.execute_non_query("UPDATE subjects SET subject_name = %s WHERE dept_name = %s AND subject_name = %s", (name, self.editing_subject_dept, self.editing_subject_name))
                    # Cascade update grades for this department's students
                    self.db.execute_non_query("UPDATE grades SET subject_name = %s WHERE subject_name = %s AND student_id IN (SELECT student_id FROM students WHERE department = %s)", (name, self.editing_subject_name, self.editing_subject_dept))
                    messagebox.showinfo("Success", "Subject updated successfully.")
                else:
                    # Insert new subject
                    self.db.execute_non_query("INSERT INTO subjects (dept_name, subject_name) VALUES (%s, %s)", (dept, name))
                    messagebox.showinfo("Success", "Subject added successfully.")
            except Exception as e:
                # Local Simulation Fallback
                if self.editing_subject_name and self.editing_subject_dept:
                    for sub in self.subjects:
                        if sub["dept_name"] == self.editing_subject_dept and sub["subject_name"] == self.editing_subject_name:
                            sub["subject_name"] = name
                            break
                    for g in self.local_grades:
                        s_ids = [s["student_id"] for s in self.local_students if s["department"] == self.editing_subject_dept]
                        if g["subject_name"] == self.editing_subject_name and g["student_id"] in s_ids:
                            g["subject_name"] = name
                else:
                    self.subjects.append({"dept_name": dept, "subject_name": name})
                messagebox.showinfo("Success (Local)", f"Saved locally: {e}")
                
            self.subject_name_entry.delete(0, tk.END)
            self.editing_subject_name = None
            self.editing_subject_dept = None
            self.load_subjects()
            refresh_subjects()

        save_btn = tk.Button(btn_frame, text="Save Subject", font=("Arial", 11, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=save_subject)
        save_btn.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 5))

        def clear_subject():
            self.subject_name_entry.delete(0, tk.END)
            self.editing_subject_name = None
            self.editing_subject_dept = None
            
        clear_btn = tk.Button(btn_frame, text="Clear", font=("Arial", 11, "bold"), bg="#9CA3AF", fg="#FFFFFF", bd=0, cursor="hand2", command=clear_subject)
        clear_btn.pack(side="right", fill="x", expand=True, ipady=10, padx=(5, 0))

        # Right Tree view
        tree_frame = tk.Frame(right_panel, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        tree_frame.pack(fill="both", expand=True)
        
        self.subjects_header_lbl = tk.Label(tree_frame, text="Subject Directory - Computer Science", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF")
        self.subjects_header_lbl.pack(pady=10)

        self.subject_tree = ttk.Treeview(tree_frame, columns=("SubName",), show="headings", style="Subjects.Treeview")
        self.subject_tree.heading("SubName", text="Subject Name")
        self.subject_tree.column("SubName", anchor="w")
        self.subject_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Buttons under Treeview
        tree_btn_frame = tk.Frame(right_panel, bg="#F3F4F6")
        tree_btn_frame.pack(fill="x", pady=10)

        def edit_subject():
            sel = self.subject_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a subject.")
                return
            vals = self.subject_tree.item(sel[0], "values")
            name = vals[0]
            dept = self.subject_dept_combo.get().strip()
            self.subject_name_entry.delete(0, tk.END)
            self.subject_name_entry.insert(0, name)
            self.editing_subject_name = name
            self.editing_subject_dept = dept

        edit_btn = tk.Button(tree_btn_frame, text="Edit Selected", font=("Arial", 11, "bold"), bg="#2A3E5C", fg="#FFFFFF", bd=0, cursor="hand2", command=edit_subject)
        edit_btn.pack(side="left", ipady=10, padx=(0, 10))

        def delete_subject():
            sel = self.subject_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a subject.")
                return
            vals = self.subject_tree.item(sel[0], "values")
            name = vals[0]
            dept = self.subject_dept_combo.get().strip()
            
            ans = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete subject '{name}' from department '{dept}'?")
            if not ans:
                return
                
            try:
                self.db.execute_non_query("DELETE FROM subjects WHERE dept_name = %s AND subject_name = %s", (dept, name))
                # Cascade delete grades for this subject
                self.db.execute_non_query("DELETE FROM grades WHERE subject_name = %s AND student_id IN (SELECT student_id FROM students WHERE department = %s)", (name, dept))
                messagebox.showinfo("Success", "Subject deleted successfully.")
            except Exception as e:
                self.subjects = [x for x in self.subjects if not (x["dept_name"] == dept and x["subject_name"] == name)]
                s_ids = [s["student_id"] for s in self.local_students if s["department"] == dept]
                self.local_grades = [x for x in self.local_grades if not (x["subject_name"] == name and x["student_id"] in s_ids)]
                messagebox.showinfo("Success (Local)", f"Deleted locally: {e}")

            self.load_subjects()
            refresh_subjects()

        delete_btn = tk.Button(tree_btn_frame, text="Delete Selected", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=delete_subject)
        delete_btn.pack(side="left", ipady=10)

        def refresh_subjects():
            dept = self.subject_dept_combo.get().strip()
            self.subjects_header_lbl.configure(text=f"Subject Directory - {dept}")
            for item in self.subject_tree.get_children():
                self.subject_tree.delete(item)
            for s in self.subjects:
                if s.get("dept_name") == dept:
                    self.subject_tree.insert("", "end", values=(s.get("subject_name"),))

        self.subject_dept_combo.bind("<<ComboboxSelected>>", lambda e: refresh_subjects())
        refresh_subjects()

    def show_accounts_management(self):
        self.clear_workspace()
        self.set_active_button(self.btn_accounts)

        # Left / Right Split Layout
        left_panel = tk.Frame(self.workspace, bg="#FFFFFF", width=380, highlightthickness=1, highlightbackground="#E5E7EB")
        left_panel.pack(side="left", fill="both", padx=20, pady=20)
        left_panel.pack_propagate(False)

        right_panel = tk.Frame(self.workspace, bg="#F3F4F6")
        right_panel.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        # Left Form
        tk.Label(left_panel, text="Manage Student Account", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=(20, 15))
        
        tk.Label(left_panel, text="Account Username *", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.acc_username_entry = tk.Entry(left_panel, font=("Arial", 11), bd=1, relief="solid")
        self.acc_username_entry.pack(fill="x", padx=20, ipady=5, pady=(0, 15))

        tk.Label(left_panel, text="Account Password *", font=("Arial", 11), fg="#4B5563", bg="#FFFFFF", anchor="w").pack(fill="x", padx=20, pady=(10, 2))
        self.acc_password_entry = tk.Entry(left_panel, font=("Arial", 11), bd=1, relief="solid")
        self.acc_password_entry.pack(fill="x", padx=20, ipady=5, pady=(0, 20))

        btn_frame = tk.Frame(left_panel, bg="#FFFFFF")
        btn_frame.pack(fill="x", side="bottom", pady=25, padx=20)

        self.editing_account_username = None
        self.editing_account_sid = None
        
        def save_account():
            user = self.acc_username_entry.get().strip()
            pwd = self.acc_password_entry.get().strip()
            if not user or not pwd:
                messagebox.showerror("Error", "Username and Password cannot be empty.")
                return
                
            if not self.editing_account_sid:
                messagebox.showerror("Error", "Please select a student account from the table to update/assign credentials.")
                return
            
            try:
                # Check if username is already taken by someone else
                check_user = self.db.execute_query("SELECT username FROM users WHERE username = %s AND username != %s", (user, self.editing_account_username or ""))
                if check_user:
                    messagebox.showerror("Error", f"Username '{user}' is already taken.")
                    return

                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 0")
                if self.editing_account_username:
                    # Update users table
                    self.db.execute_non_query("UPDATE users SET username = %s, password = %s WHERE username = %s", (user, pwd, self.editing_account_username))
                    # Update students table
                    self.db.execute_non_query("UPDATE students SET username = %s WHERE student_id = %s", (user, self.editing_account_sid))
                else:
                    # Create new user
                    self.db.execute_non_query("INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')", (user, pwd))
                    # Link to student
                    self.db.execute_non_query("UPDATE students SET username = %s WHERE student_id = %s", (user, self.editing_account_sid))
                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 1")
                messagebox.showinfo("Success", "Account credentials saved successfully.")
            except Exception as e:
                # Local
                for s in self.local_students:
                    if s["student_id"] == self.editing_account_sid:
                        s["username"] = user
                        s["password"] = pwd
                messagebox.showinfo("Success (Local)", f"Saved account details locally: {e}")
                
            self.acc_username_entry.delete(0, tk.END)
            self.acc_password_entry.delete(0, tk.END)
            self.editing_account_username = None
            self.editing_account_sid = None
            refresh_accounts()

        save_btn = tk.Button(btn_frame, text="Save Account", font=("Arial", 11, "bold"), bg="#10B981", fg="#FFFFFF", bd=0, cursor="hand2", command=save_account)
        save_btn.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 5))

        def clear_account():
            self.acc_username_entry.delete(0, tk.END)
            self.acc_password_entry.delete(0, tk.END)
            self.editing_account_username = None
            self.editing_account_sid = None
            
        clear_btn = tk.Button(btn_frame, text="Clear", font=("Arial", 11, "bold"), bg="#9CA3AF", fg="#FFFFFF", bd=0, cursor="hand2", command=clear_account)
        clear_btn.pack(side="right", fill="x", expand=True, ipady=8, padx=(5, 0))

        # Right Tree view
        tree_frame = tk.Frame(right_panel, bg="#FFFFFF", highlightthickness=1, highlightbackground="#E5E7EB")
        tree_frame.pack(fill="both", expand=True)
        
        tk.Label(tree_frame, text="Student Credentials Matrix Directory", font=("Arial", 14, "bold"), fg="#2A3E5C", bg="#FFFFFF").pack(pady=10)

        self.acc_tree = ttk.Treeview(tree_frame, columns=("StudentID", "Name", "Department", "Username", "Password"), show="headings")
        self.acc_tree.heading("StudentID", text="StudentID")
        self.acc_tree.heading("Name", text="Full Name")
        self.acc_tree.heading("Department", text="Department")
        self.acc_tree.heading("Username", text="Username")
        self.acc_tree.heading("Password", text="Password (Cleartext)")
        
        self.acc_tree.column("StudentID", width=70, anchor="center")
        self.acc_tree.column("Name", width=120, anchor="w")
        self.acc_tree.column("Department", width=120, anchor="center")
        self.acc_tree.column("Username", width=110, anchor="center")
        self.acc_tree.column("Password", width=110, anchor="center")
        
        self.acc_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Buttons under Treeview
        tree_btn_frame = tk.Frame(right_panel, bg="#F3F4F6")
        tree_btn_frame.pack(fill="x", pady=10)

        def edit_account():
            sel = self.acc_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a student account row to edit.")
                return
            vals = self.acc_tree.item(sel[0], "values")
            self.acc_username_entry.delete(0, tk.END)
            self.acc_password_entry.delete(0, tk.END)
            
            self.editing_account_sid = vals[0]
            self.editing_account_username = vals[3] if vals[3] != "-" else None
            
            if vals[3] != "-":
                self.acc_username_entry.insert(0, vals[3])
            if vals[4] != "-":
                self.acc_password_entry.insert(0, vals[4])

        edit_btn = tk.Button(tree_btn_frame, text="Edit Selected", font=("Arial", 11, "bold"), bg="#2A3E5C", fg="#FFFFFF", bd=0, cursor="hand2", command=edit_account)
        edit_btn.pack(side="left", ipady=8, padx=(0, 10))

        def delete_account():
            sel = self.acc_tree.selection()
            if not sel:
                messagebox.showwarning("Selection Required", "Please select a student account row.")
                return
            vals = self.acc_tree.item(sel[0], "values")
            sid = vals[0]
            user = vals[3]
            
            if user == "-":
                messagebox.showwarning("No Account", "This student has no associated user account login to delete.")
                return
                
            ans = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete login account '{user}' for student {vals[1]}?")
            if not ans:
                return
                
            try:
                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 0")
                self.db.execute_non_query("DELETE FROM users WHERE username = %s", (user,))
                self.db.execute_non_query("UPDATE students SET username = NULL WHERE student_id = %s", (sid,))
                self.db.execute_non_query("SET FOREIGN_KEY_CHECKS = 1")
                messagebox.showinfo("Success", "Account deleted successfully.")
            except Exception as e:
                for s in self.local_students:
                    if s["student_id"] == sid:
                        s["username"] = ""
                        s["password"] = ""
                messagebox.showinfo("Success (Local)", f"Deleted locally: {e}")

            refresh_accounts()

        delete_btn = tk.Button(tree_btn_frame, text="Delete Selected", font=("Arial", 11, "bold"), bg="#EF4444", fg="#FFFFFF", bd=0, cursor="hand2", command=delete_account)
        delete_btn.pack(side="left", ipady=8)

        def refresh_accounts():
            for item in self.acc_tree.get_children():
                self.acc_tree.delete(item)
                
            try:
                rows = self.db.execute_query(
                    "SELECT s.student_id, s.name, s.department, s.username, u.password "
                    "FROM students s "
                    "LEFT JOIN users u ON s.username = u.username"
                )
            except Exception:
                rows = []
                for s in self.local_students:
                    rows.append({
                        "student_id": s["student_id"],
                        "name": s["name"],
                        "department": s["department"],
                        "username": s.get("username", "-"),
                        "password": s.get("password", "-")
                    })
                    
            for r in rows:
                sid = r.get("student_id")
                name = r.get("name")
                dept = r.get("department")
                user = r.get("username") or "-"
                pwd = r.get("password") or "-"
                self.acc_tree.insert("", "end", values=(sid, name, dept, user, pwd))

        refresh_accounts()

    def handle_logout(self):
        ans = messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of the active user session?")
        if ans:
            self.logout_cb()
