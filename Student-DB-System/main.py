import customtkinter as ctk
from views.login_ui import LoginUI
from views.dashboard_ui import DashboardUI
from views.db_setup_ui import DBSetupUI
from database.db_manager import DBManager

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class StudentDBApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.username = None
        self.role = None
        self.check_database()

    def check_database(self):
        db = DBManager()
        success, err = db.check_and_setup()
        if not success:
            self.show_database_setup()
        else:
            self.show_login_screen()

    def show_database_setup(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.setup_manager = DBSetupUI(self.root, self.on_setup_completed)

    def on_setup_completed(self):
        self.show_login_screen()

    def show_login_screen(self):
        # Clear child elements
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Initialize login view
        self.login_manager = LoginUI(self.root, self.on_login_success)

    def on_login_success(self, username, role):
        self.username = username
        self.role = role
        self.show_main_dashboard()

    def show_main_dashboard(self):
        # Clear login state items
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Initialize dashboard workspace view
        self.dashboard_manager = DashboardUI(self.root, self.username, self.role, self.handle_logout)

    def handle_logout(self):
        self.username = None
        self.role = None
        self.show_login_screen()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StudentDBApp()
    app.run()
