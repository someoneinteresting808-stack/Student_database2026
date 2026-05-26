import tkinter as tk
from views.login_ui import LoginUI
from views.dashboard_ui import DashboardUI

class StudentDBApp:
    def __init__(self):
        self.root = tk.Tk()
        self.username = None
        self.role = None
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
