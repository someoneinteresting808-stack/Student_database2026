import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import DBManager

class DBSetupUI:
    def __init__(self, root, on_success_callback):
        self.root = root
        self.on_success = on_success_callback
        self.db = DBManager()
        
        self.root.title("Database Connection Setup")
        self.root.geometry("480x540")
        self.root.resizable(False, False)
        
        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (480 // 2)
        y = (screen_height // 2) - (540 // 2)
        self.root.geometry(f"480x540+{x}+{y}")
        
        self.create_widgets()

    def create_widgets(self):
        # Card style container
        card = ctk.CTkFrame(self.root, width=420, height=480, corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center")
        
        # Header Label
        header = ctk.CTkLabel(card, text="DATABASE SETUP", font=("Arial", 16, "bold"), text_color="#2A3E5C")
        header.pack(pady=(25, 10))
        
        info_lbl = ctk.CTkLabel(card, text="Could not connect to local MySQL server.\nPlease configure database credentials:", 
                                font=("Arial", 12, "italic"), text_color="#EF4444", justify="center")
        info_lbl.pack(pady=(0, 15))
        
        # Username Entry
        self.user_entry = ctk.CTkEntry(card, width=340, height=40, placeholder_text="MySQL Username", font=("Arial", 14))
        self.user_entry.pack(pady=(5, 10))
        self.user_entry.insert(0, self.db.config.get("user", "root"))
        
        # Password Entry
        self.password_entry = ctk.CTkEntry(card, width=340, height=40, placeholder_text="MySQL Password", show="*", font=("Arial", 14))
        self.password_entry.pack(pady=(0, 20))
        self.password_entry.insert(0, self.db.config.get("password", ""))
        
        # Connect & Test Button
        connect_btn = ctk.CTkButton(card, text="CONNECT & SAVE", font=("Arial", 14, "bold"), width=340, height=40,
                                    corner_radius=8, fg_color="#10B981", hover_color="#059669",
                                    command=self.handle_setup)
        connect_btn.pack(pady=(0, 10))
        
        # Offline Mode Button
        offline_btn = ctk.CTkButton(card, text="RUN IN OFFLINE MODE", font=("Arial", 14, "bold"), width=340, height=40,
                                     corner_radius=8, fg_color="#9CA3AF", hover_color="#4B5563",
                                     command=self.handle_offline)
        offline_btn.pack()

    def handle_setup(self):
        user = self.user_entry.get().strip()
        password = self.password_entry.get()
        
        if not user:
            messagebox.showerror("Validation Error", "Username is a required field.")
            return
            
        host = self.db.config.get("host", "localhost")
        port = self.db.config.get("port", 3306)
        
        self.db.update_config(host, user, password, "student_db")
        self.db.config["port"] = port
        
        config_dict = self.db.config.copy()
        config_dict["port"] = port
        self.db.save_config(config_dict)
        
        success, err = self.db.check_and_setup()
        if success:
            messagebox.showinfo("Success", "Successfully connected and initialized the MySQL Database!")
            self.on_success()
        else:
            messagebox.showerror("Connection Failed", f"Could not connect using the provided credentials:\n{err}")

    def handle_offline(self):
        ans = messagebox.askyesno("Confirm Offline Mode", 
                                  "Are you sure you want to run the application in Offline Mode?\n"
                                  "Any data changes will only persist in memory and not be saved to MySQL.")
        if ans:
            self.on_success()
