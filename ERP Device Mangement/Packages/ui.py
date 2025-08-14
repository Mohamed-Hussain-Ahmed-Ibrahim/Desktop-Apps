from tkinter import Menu
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkToplevel
from customtkinter import CTkScrollableFrame, CTkTabview
from tkinter import filedialog, BOTH, StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter.messagebox import showinfo, showerror
from tkinter.simpledialog import askstring
from datetime import datetime
from Packages.database import Database
import os
from Packages.inventory import inventoryManager
from Packages.products import productsManager
from Packages.categories import Categories
from Packages.suppliers import SuppliersManager
from Packages.purchase_orders import purchaseOrders
from Packages.sales import salesManager
from Packages.reports import reportManager
class UiManager:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.main_frame = CTkFrame(self.root)
        self.inventory = inventoryManager(self.main_frame, self.root)
        self.products = productsManager(self.root, self.main_frame)
        self.status_var = StringVar(value="Welcome to Device Management System")
        self.categories = Categories(self.root, self.main_frame)
        self.suppliers = SuppliersManager(self.root, self.main_frame)
        self.purchase_orders = purchaseOrders(self.root, self.main_frame)
        self.sales = salesManager(self.root, self.main_frame)
        self.reports = reportManager(self.root, self.main_frame)
    def create_menu(self):
        """Create application menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Data", command=self.import_data)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Reports menu
        reports_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        reports_menu.add_command(label="Inventory Summary", command=lambda: self.generate_report("Inventory Summary"))
        reports_menu.add_command(label="Low Stock Alert", command=lambda: self.generate_report("Low Stock Alert"))
        reports_menu.add_command(label="Sales Report", command=lambda: self.generate_report("Sales Report"))
        reports_menu.add_command(label="Category Analysis", command=lambda: self.generate_report("Category Analysis"))
        reports_menu.add_command(label="Profit Margin Analysis", command=lambda: self.generate_report("Profit Margin Analysis"))
        
        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)

    def create_sidebar(self):
        """Create sidebar with navigation buttons"""
        self.sidebar = CTkFrame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Logo and title
        CTkLabel(self.sidebar, text="Device\nManagement", font=("Arial", 20, "bold")).pack(pady=20)
        # Navigation buttons
        buttons = [
            ("Inventory", self.inventory.show_inventory),
            ("Add Product", self.products.show_add_product),
            ("Categories", self.categories.show_categories),
            ("Suppliers", self.suppliers.show_suppliers),
            ("Purchase Orders", self.purchase_orders.show_purchase_orders),
            ("Sales", self.sales.show_sales),
            ("Dashboard", self.show_dashboard),
            ("Reports", self.reports.show_reports),
        ]
        
        for text, command in buttons:
            CTkButton(self.sidebar, text=text, command=command).pack(pady=5, padx=20, fill="x")
    
    def create_main_frame(self):
        """Create main content frame"""
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.show_dashboard()  # Show dashboard initially
    
    def show_dashboard(self):
        """Display dashboard with key metrics and charts"""
        self.clear_main_frame()
        
        # Dashboard title
        CTkLabel(self.main_frame, text="Dashboard", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Create top metrics frame
        metrics_frame = CTkFrame(self.main_frame)
        metrics_frame.pack(fill="x", padx=20, pady=10)
        
        total_value, total_products, low_stock, sales_count, sales_value, category_data, sales_data, recent_sales = self.db.show_inventory_dashboard()
        
        # Create metric widgets
        metrics = [
            {"title": "Total Inventory Value", "value": f"${total_value:,.2f}"},
            {"title": "Total Products", "value": str(total_products)},
            {"title": "Low Stock Items", "value": str(low_stock)},
            {"title": "Monthly Sales", "value": f"${sales_value:,.2f}"}
        ]
        
        for i, metric in enumerate(metrics):
            metric_box = CTkFrame(metrics_frame)
            metric_box.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            CTkLabel(metric_box, text=metric["title"], font=("Arial", 12)).pack(pady=(10,5))
            CTkLabel(metric_box, text=metric["value"], font=("Arial", 16, "bold")).pack(pady=(0,10))
        
        metrics_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Create charts frame
        charts_frame = CTkFrame(self.main_frame)
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)   
        left_frame = CTkFrame(charts_frame)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        if category_data:
            fig1, ax1 = plt.subplots(figsize=(4, 3), dpi=100)
            labels = [row[0] for row in category_data]
            sizes = [row[2] for row in category_data]
            colors = [row[1] for row in category_data]
            
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            ax1.set_title("Inventory by Category")
            
            canvas1 = FigureCanvasTkAgg(fig1, master=left_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            CTkLabel(left_frame, text="No category data available").pack(pady=50)
        
        right_frame = CTkFrame(charts_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        if sales_data:
            fig2, ax2 = plt.subplots(figsize=(4, 3), dpi=100)
            dates = [row[0] for row in sales_data]
            values = [row[1] for row in sales_data]
            
            ax2.bar(dates, values, color='#3498db')
            ax2.set_title("Recent Sales")
            ax2.set_ylabel("Sales Amount ($)")
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            canvas2 = FigureCanvasTkAgg(fig2, master=right_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=BOTH, expand=True)
        else:
            CTkLabel(right_frame, text="No recent sales data available").pack(pady=50)
        
        charts_frame.grid_columnconfigure((0,1), weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Recent activity section
        activity_frame = CTkFrame(self.main_frame)
        activity_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(activity_frame, text="Recent Activity", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        
        if recent_sales:
            for sale in recent_sales:
                sale_date, product_name, quantity, price, customer = sale
                activity_text = f"{sale_date}: Sold {quantity} x {product_name} to {customer or 'Customer'} for ${price:.2f} each"
                CTkLabel(activity_frame, text=activity_text).pack(anchor="w", padx=20, pady=2)
        else:
            CTkLabel(activity_frame, text="No recent activity").pack(anchor="w", padx=20, pady=10)

    def import_data(self):
        """Import data from CSV"""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select CSV File to Import"
        )
        
        if not file_path:
            return
            
        try:
            # Determine import type based on filename
            filename = os.path.basename(file_path).lower()
            
            if 'product' in filename:
                self.import_products(file_path)
            elif 'inventory' in filename:
                self.import_inventory(file_path)
            elif 'category' in filename:
                self.import_categories(file_path)
            elif 'supplier' in filename:
                self.import_suppliers(file_path)
            elif 'sale' in filename:
                self.import_sales(file_path)
            elif 'order' in filename:
                self.import_purchase_orders(file_path)
            else:
                showerror("Error", "Could not determine import type from filename. Please include 'product', 'inventory', 'category', 'supplier', 'sale', or 'order' in the filename.")
                
        except Exception as e:
            showerror("Error", f"Failed to import data: {str(e)}")

    def export_data(self):
        """Export data to CSV"""
        export_type = askstring(
            "Export Data",
            "What would you like to export?\n(products, inventory, categories, suppliers, sales, orders)",
            parent=self.root
        )
        
        if not export_type:
            return
            
        export_type = export_type.lower().strip()
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title=f"Save {export_type.capitalize()} Data As",
            initialfile=f"{export_type}_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        
        if not file_path:
            return
        else:
            self.db.export(export_type, file_path)

    def backup_database(self):
        """Create a backup of the database"""
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database Files", "*.db"), ("All Files", "*.*")],
            title="Save Database Backup As",
            initialfile=f"device_inventory_backup_{datetime.now().strftime('%Y%m%d')}.db"
        )
        if not backup_path:
            return
        else:
            self.db.backup(backup_path)
            showinfo("Backup Successful", f"Database backup created at {backup_path}")

    def create_report_table(self, parent, headers, data):
        """Create a formatted table for reports"""
        # Header row
        header_frame = CTkFrame(parent)
        header_frame.pack(fill="x", pady=(0,5))
        
        for i, header in enumerate(headers):
            CTkLabel(header_frame, text=header, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="w")
            header_frame.grid_columnconfigure(i, weight=1)
        
        # Data rows
        for row_idx, row_data in enumerate(data, start=1):
            row_frame = CTkFrame(parent)
            row_frame.pack(fill="x", pady=2)
            
            for col_idx, value in enumerate(row_data):
                # Format numeric values
                if isinstance(value, (float, int)):
                    if value == int(value):
                        display_value = str(int(value))
                    else:
                        display_value = f"{value:.2f}"
                    
                    # Add dollar sign for monetary values
                    if headers[col_idx] in ["Price", "Cost", "Profit", "Total", "Value", "Total Spend"]:
                        display_value = f"${display_value}"
                    elif headers[col_idx] == "Margin %":
                        display_value = f"{display_value}%"
                else:
                    display_value = str(value) if value is not None else "N/A"
                
                CTkLabel(row_frame, text=display_value).grid(row=0, column=col_idx, padx=5, pady=5, sticky="w")
                row_frame.grid_columnconfigure(col_idx, weight=1)

    def generate_report(self, report_type):
        """Generate and display a report"""
        # Create a new window for the report
        report_window = CTkToplevel(self.root)
        report_window.title(f"{report_type} Report")
        report_window.geometry("1000x700")
        report_window.grab_set()
        
        # Header
        header_frame = CTkFrame(report_window)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(header_frame, text=f"{report_type} Report", font=("Arial", 20, "bold")).pack(side="left")
        
        # Add export button
        export_frame = CTkFrame(header_frame)
        export_frame.pack(side="right")
        
        CTkButton(export_frame, text="Export to CSV", 
                     command=lambda: self.db.export_report(report_type)).pack(side="left", padx=5)
        CTkButton(export_frame, text="Print", 
                     command=lambda: self.db.print_report(report_type)).pack(side="left", padx=5)
        
        # Content frame
        content_frame = CTkScrollableFrame(report_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        headers, data = self.db.generate_report(report_type)
        if not data:
            CTkLabel(content_frame, text="No data available for this report.", font=("Arial", 14)).pack(pady=20)
            return
        else:
            self.create_report_table(content_frame, headers, data)
    def show_user_guide(self):
        """Display the user guide/documentation"""
        guide_window = CTkToplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("800x600")
        
        # Create tabs
        tabview = CTkTabview(guide_window)
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        tabview.add("Getting Started")
        tabview.add("Inventory")
        tabview.add("Sales")
        tabview.add("Purchase Orders")
        tabview.add("Reports")
        
        # Getting Started tab
        start_frame = CTkScrollableFrame(tabview.tab("Getting Started"))
        start_frame.pack(fill="both", expand=True)
        
        CTkLabel(start_frame, text="Welcome to Device Management System", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        CTkLabel(start_frame, text="This application helps you manage your device inventory, sales, and purchase orders.", wraplength=700).pack(anchor="w", pady=5)
        
        CTkLabel(start_frame, text="Key Features:", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        features = [
            "📦 Inventory management with stock tracking",
            "💰 Sales recording with customer details",
            "🛒 Purchase order creation and tracking",
            "📊 Comprehensive reporting and analytics",
            "📈 Dashboard with key metrics and charts",
            "🔄 Data import/export capabilities"
        ]
        
        for feature in features:
            CTkLabel(start_frame, text=feature, wraplength=700).pack(anchor="w", pady=2, padx=20)
        
        # Inventory tab
        inv_frame = CTkScrollableFrame(tabview.tab("Inventory"))
        inv_frame.pack(fill="both", expand=True)
        
        CTkLabel(inv_frame, text="Inventory Management", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        CTkLabel(inv_frame, text="The Inventory section allows you to:", wraplength=700).pack(anchor="w", pady=5)
        
        inv_features = [
            "1. View all products in your inventory",
            "2. Add new products with detailed specifications",
            "3. Edit existing product information",
            "4. Track stock levels and set reorder points",
            "5. Manage product categories",
            "6. Record product sales"
        ]
        
        for feature in inv_features:
            CTkLabel(inv_frame, text=feature, wraplength=700).pack(anchor="w", pady=2, padx=20)
        
        # Sales tab
        sales_frame = CTkScrollableFrame(tabview.tab("Sales"))
        sales_frame.pack(fill="both", expand=True)
        
        CTkLabel(sales_frame, text="Sales Management", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        CTkLabel(sales_frame, text="The Sales section allows you to:", wraplength=700).pack(anchor="w", pady=5)
        
        sales_features = [
            "1. Record sales transactions",
            "2. Track customer information",
            "3. View sales history",
            "4. Generate sales reports",
            "5. Analyze sales performance by product or category"
        ]
        
        for feature in sales_features:
            CTkLabel(sales_frame, text=feature, wraplength=700).pack(anchor="w", pady=2, padx=20)
        
        # Purchase Orders tab
        po_frame = CTkScrollableFrame(tabview.tab("Purchase Orders"))
        po_frame.pack(fill="both", expand=True)
        
        CTkLabel(po_frame, text="Purchase Order Management", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        CTkLabel(po_frame, text="The Purchase Orders section allows you to:", wraplength=700).pack(anchor="w", pady=5)
        
        po_features = [
            "1. Create new purchase orders",
            "2. Manage supplier information",
            "3. Track order status (Pending, Ordered, Received, Cancelled)",
            "4. View order history",
            "5. Generate order reports"
        ]
        
        for feature in po_features:
            CTkLabel(po_frame, text=feature, wraplength=700).pack(anchor="w", pady=2, padx=20)
        
        # Reports tab
        reports_frame = CTkScrollableFrame(tabview.tab("Reports"))
        reports_frame.pack(fill="both", expand=True)
        
        CTkLabel(reports_frame, text="Reporting", font=("Arial", 16, "bold")).pack(anchor="w", pady=10)
        CTkLabel(reports_frame, text="The Reports section provides:", wraplength=700).pack(anchor="w", pady=5)
        
        report_features = [
            "1. Inventory summary reports",
            "2. Low stock alerts",
            "3. Sales reports by date range",
            "4. Category performance analysis",
            "5. Profit margin reports",
            "6. Supplier performance evaluation",
            "7. Export reports to CSV for further analysis"
        ]
        
        for feature in report_features:
            CTkLabel(reports_frame, text=feature, wraplength=700).pack(anchor="w", pady=2, padx=20)

    def show_about(self):
        """Display about dialog"""
        about_window = CTkToplevel(self.root)
        about_window.title("About Device Management System")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        # Logo and title
        logo_frame = CTkFrame(about_window)
        logo_frame.pack(pady=20)
        
        # You can replace this with your actual logo
        CTkLabel(logo_frame, text="📱💻", font=("Arial", 40)).pack()
        CTkLabel(logo_frame, text="Device Management System", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Version info
        info_frame = CTkFrame(about_window)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(info_frame, text="Version: 1.0.0").pack(anchor="w", pady=2)
        CTkLabel(info_frame, text="Developed by: Your Company").pack(anchor="w", pady=2)
        CTkLabel(info_frame, text="Copyright © 2023").pack(anchor="w", pady=2)
        
        # Description
        desc_frame = CTkFrame(about_window)
        desc_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(desc_frame, 
                    text="A comprehensive solution for managing device inventory, sales, and purchases.",
                    wraplength=400).pack(anchor="w", pady=5)
        
        # Close button
        button_frame = CTkFrame(about_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        CTkButton(button_frame, text="Close", command=about_window.destroy).pack()

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
           
        