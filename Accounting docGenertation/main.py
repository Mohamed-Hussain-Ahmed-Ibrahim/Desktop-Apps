from customtkinter import CTk, set_appearance_mode, set_default_color_theme, CTkFont
from customtkinter import CTkFrame, CTkButton, CTkLabel
from tkinter.messagebox import showerror
import os
import sys
from Packages.database_manager import DatabaseManager
from Packages.inventory_management import InventoryModule
from Packages.accounting_payroll import AccountingModule
from Packages.document_generation import DocumentModule

class CompanyManagementApp:
    """
    Main application class that manages the overall GUI structure and navigation.
    Uses CustomTkinter for modern UI components and handles module switching.
    """ 
    def __init__(self):
        # Set CustomTkinter appearance
        set_appearance_mode("light")
        set_default_color_theme("blue")
        
        # Initialize main window
        self.root = CTk()
        self.root.title("Company Management System")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # Initialize database
        try:
            self.db = DatabaseManager()
        except Exception as e:
            showerror("Database Error", f"Failed to initialize database: {e}")
            sys.exit(1)
        
        # Initialize UI components
        self.setup_ui()
        self.setup_modules()
        
        # Show inventory module by default
        self.show_module("inventory")

    def setup_ui(self):
        """Setup the main UI layout with navigation sidebar and content area."""
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create navigation sidebar
        self.sidebar = CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_rowconfigure(6, weight=1)  # Space at bottom
        
        # Company logo/title
        self.logo_label = CTkLabel(
            self.sidebar, 
            text="Company\nManagement", 
            font=CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("inventory", "📦 Inventory", self.show_inventory),
            ("accounting", "💰 Accounting", self.show_accounting),
            ("documents", "📄 Documents", self.show_documents)
        ]
        
        for i, (key, text, command) in enumerate(nav_items, start=1):
            btn = CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=160,
                height=40,
                corner_radius=6
            )
            btn.grid(row=i, column=0, padx=20, pady=5)
            self.nav_buttons[key] = btn
        
        # System info label
        self.info_label = CTkLabel(
            self.sidebar,
            text="Version 1.0\n© 2025 EasyTest Company",
            font=CTkFont(size=10),
            text_color="gray"
        )
        self.info_label.grid(row=7, column=0, padx=20, pady=20, sticky="s")
        
        # Main content area
        self.main_frame = CTkFrame(self.root, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

    
    def setup_modules(self):
        """Initialize all application modules."""
        try:
            self.modules = {
                'inventory': InventoryModule(self.main_frame, self.db),
                'accounting': AccountingModule(self.main_frame, self.db),
                'documents': DocumentModule(self.main_frame, self.db)
            }
        except Exception as e:
            showerror("Module Error", f"Failed to initialize modules: {e}")
    
    def show_module(self, module_name):
        """
        Display the specified module and hide others.
        
        Args:
            module_name: Name of the module to show
        """
        try:
            # Hide all modules first
            for module in self.modules.values():
                module.hide()
            
            # Update button states
            for key, btn in self.nav_buttons.items():
                if key == module_name:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color=("gray70", "gray30"))
            
            # Show selected module
            if module_name in self.modules:
                self.modules[module_name].show()
            else:
                showerror("Error",f"Module {module_name} not found!")
        
        except Exception as e:
            showerror("Error", f"Failed to load module: {e}")
    
    def show_inventory(self):
        """Show inventory management module."""
        self.show_module("inventory")
    
    def show_accounting(self):
        """Show accounting & payroll module."""
        self.show_module("accounting")
    
    def show_documents(self):
        """Show document generation module."""
        self.show_module("documents")
    
    def show_admin(self):
        """Show admin dashboard module."""
        self.show_module("admin")
    
    def on_closing(self):
        """Handle application closing event."""
        try:
            # Save any pending changes
            for module in self.modules.values():
                if hasattr(module, 'save_changes'):
                    module.save_changes()
            
            # Close database connection
            if hasattr(self.db, 'close'):
                self.db.close()
            
            self.root.destroy()
            
        except Exception as e:
            showerror("Error",f"Error during cleanup: {e}")
            self.root.destroy()
    
    def run(self):
        """Start the application main loop."""
        # Set close protocol
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        try:
            # Start the GUI event loop
            self.root.mainloop()
        except Exception as e:
            showerror("Application Error", f"An unexpected error occurred: {e}")


def main():
    """Main entry point for the application."""
    try:
        # Create and run the application
        app = CompanyManagementApp()
        app.run()
    except Exception as e:
        showerror("Fatal Error", f"Failed to start application: {e}")


if __name__ == "__main__":
    main()