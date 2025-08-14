from Packages.database import Database
from customtkinter import set_appearance_mode, set_default_color_theme, CTk, CTkLabel
from tkinter import StringVar
from Packages.ui import UiManager
class DeviceManagementSystem(CTk):
    def __init__(self):
        super().__init__()
        self.root = self
        self.title("Device Management System")
        self.geometry("1200x700")
        self.minsize(900, 600)
        self.db = Database()
        self.ui_manager = UiManager(self.root)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI components"""
        set_appearance_mode("dark")
        set_default_color_theme("blue")
        # Set up status bar
        self.status_var = StringVar()
        self.status_var.set("Ready")
        self.statusbar = CTkLabel(self.root, textvariable=self.status_var, anchor="w")
        self.statusbar.pack(side="bottom", fill="x")
        # Create menu bar
        self.ui_manager.create_menu()
        
        # Create main layout
        self.ui_manager.create_sidebar()
        self.ui_manager.create_main_frame()

    def run(self):
        """Run the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DeviceManagementSystem()
    app.run()