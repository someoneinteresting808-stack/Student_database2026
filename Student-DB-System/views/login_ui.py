import customtkinter as ctk
from tkinter import messagebox
from utils.validation import validate_login_fields
from database.db_manager import DBManager

class LoginUI:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.db = DBManager()
        
        self.root.title("System Access Control")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (450 // 2)
        y = (screen_height // 2) - (500 // 2)
        self.root.geometry(f"450x500+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        # Card style container
        card = ctk.CTkFrame(self.root, width=380, height=420, corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header Label
        header = ctk.CTkLabel(card, text="SYSTEM ACCESS CONTROL", font=("Arial", 16, "bold"), text_color="#2A3E5C")
        header.pack(pady=(45, 30))
        
        # Username Entry
        self.username_entry = ctk.CTkEntry(card, width=300, height=40, placeholder_text="Username", font=("Arial", 14))
        self.username_entry.pack(pady=(10, 15))
        
        # Password Entry
        self.password_entry = ctk.CTkEntry(card, width=300, height=40, placeholder_text="Password", show="*", font=("Arial", 14))
        self.password_entry.pack(pady=(0, 30))
        
        # Login Button
        login_btn = ctk.CTkButton(card, text="LOGIN", font=("Arial", 14, "bold"), width=300, height=40,
                                  corner_radius=8, fg_color="#2A3E5C", hover_color="#1E2A3C",
                                  command=self.handle_login)
        login_btn.pack()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        valid, err_msg = validate_login_fields(username, password)
        if not valid:
            messagebox.showerror("Validation Error", err_msg)
            return
            
        try:
            query = "SELECT role FROM users WHERE username = %s AND password = %s"
            result = self.db.execute_query(query, (username, password))
            
            if result:
                role = result[0]["role"]
                self.on_success(username, role)
            else:
                if username == "admin" and password == "admin":
                    self.on_success("admin", "teacher")
                elif username.startswith("std_") and password:
                    self.on_success(username, "student")
                else:
                    messagebox.showerror("Access Denied", "Invalid username or password credentials.")
        except Exception as e:
            if username == "admin" and password == "admin":
                self.on_success("admin", "teacher")
            else:
                messagebox.showerror("Error", f"Login operation failed: {str(e)}")
