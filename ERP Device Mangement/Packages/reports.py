from Packages.database import Database
from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkToplevel, CTkScrollableFrame
from datetime import datetime, timedelta
from tkinter.messagebox import showerror, showinfo
from tkinter.filedialog import asksaveasfilename
import webbrowser
import tempfile
import csv
import locale

# Get system default encoding
system_encoding = locale.getpreferredencoding()

class reportManager:
    def __init__(self, root, main_frame):
        self.db = Database()
        self.main_frame = main_frame
        self.root = root  # Ensure root is properly stored

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

    def show_reports(self):
        """Display reports page"""
        self.clear_main_frame()
    
        # Header frame
        header_frame = CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        CTkLabel(header_frame, text="Reports", 
                font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Reports container
        reports_container = CTkFrame(self.main_frame)
        reports_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        reports_container.grid_columnconfigure(0, weight=1)
        reports_container.grid_rowconfigure(0, weight=1)

        # Scrollable frame for reports
        scroll_frame = CTkScrollableFrame(reports_container)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        reports = [
            {
                "title": "Inventory Summary",
                "description": "Overview of current inventory levels and values",
                "icon": "📊"
            },
            {
                "title": "Low Stock Alert",
                "description": "Products that need to be reordered soon",
                "icon": "⚠️"
            },
            {
                "title": "Sales Report",
                "description": "Detailed sales analysis by period",
                "icon": "💰"
            },
            {
                "title": "Category Analysis",
                "description": "Performance by product category",
                "icon": "📈"
            },
            {
                "title": "Profit Margin Analysis",
                "description": "Profitability by product and category",
                "icon": "💵"
            },
            {
                "title": "Supplier Performance",
                "description": "Evaluation of supplier reliability and pricing",
                "icon": "🚚"
            }
        ]
        
        # Create a grid layout for report cards (2 columns)
        for i, report in enumerate(reports):
            row = i // 2
            col = i % 2
            
            card = CTkFrame(scroll_frame)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            
            CTkLabel(card, text=report["icon"], font=("Arial", 24)).pack(pady=(10,5))
            CTkLabel(card, text=report["title"], font=("Arial", 16, "bold")).pack()
            CTkLabel(card, text=report["description"], wraplength=200).pack(pady=5, padx=10)
            
            CTkButton(card, text="Generate", 
                     command=lambda r=report["title"]: self.generate_report(r)).pack(pady=10)

        # Configure grid weights for the scrollable frame
        for i in range((len(reports) + 1) // 2):
            scroll_frame.grid_rowconfigure(i, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(1, weight=1)

    def generate_report(self, report_type):
        """Generate and display a report"""
        try:
            # Create a new window for the report
            report_window = CTkToplevel(self.root)
            report_window.title(f"{report_type} Report")
            report_window.geometry("1000x700")
            report_window.grab_set()
            
            # Header
            header_frame = CTkFrame(report_window)
            header_frame.pack(fill="x", padx=20, pady=10)
            
            CTkLabel(header_frame, text=f"{report_type} Report", 
                    font=("Arial", 20, "bold")).pack(side="left")
            
            # Add export button
            export_frame = CTkFrame(header_frame)
            export_frame.pack(side="right")
            
            CTkButton(export_frame, text="Export to CSV", 
                     command=lambda: self.export_report(report_type)).pack(side="left", padx=5)
            CTkButton(export_frame, text="Print", 
                     command=lambda: self.print_report(report_type)).pack(side="left", padx=5)
            
            # Content frame
            content_frame = CTkScrollableFrame(report_window)
            content_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Generate report based on type
            cursor = self.db.conn.cursor()
            
            if report_type == "Inventory Summary":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.price, 
                           (i.quantity * i.price) as value, i.location
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY c.name, p.name
                ''')
                headers = ["Product", "Category", "Quantity", "Price", "Value", "Location"]
                
            elif report_type == "Low Stock Alert":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.reorder_point, 
                           i.location, (i.quantity * i.price) as value
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.quantity <= i.reorder_point
                    ORDER BY i.quantity
                ''')
                headers = ["Product", "Category", "Current Qty", "Reorder Point", "Location", "Value"]
                
            elif report_type == "Sales Report":
                cursor.execute('''
                    SELECT s.sale_date, p.name, s.quantity, s.sale_price, 
                           (s.quantity * s.sale_price) as total, s.customer_name
                    FROM sales s
                    JOIN inventory i ON s.inventory_id = i.id
                    JOIN products p ON i.product_id = p.id
                    WHERE s.sale_date >= ?
                    ORDER BY s.sale_date DESC
                ''', (datetime.now() - timedelta(days=30),))
                headers = ["Date", "Product", "Qty", "Price", "Total", "Customer"]
                
            elif report_type == "Category Analysis":
                cursor.execute('''
                    SELECT c.name, COUNT(p.id) as product_count, SUM(i.quantity) as total_quantity,
                           SUM(i.quantity * i.price) as total_value
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id
                    LEFT JOIN inventory i ON p.id = i.product_id
                    GROUP BY c.name
                    ORDER BY total_value DESC
                ''')
                headers = ["Category", "Products", "Total Qty", "Total Value"]
                
            elif report_type == "Profit Margin Analysis":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.price, i.cost, 
                           (i.price - i.cost) as profit, 
                           ((i.price - i.cost) / i.price * 100) as margin_percent
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.price > 0 AND i.cost > 0
                    ORDER BY margin_percent DESC
                ''')
                headers = ["Product", "Category", "Price", "Cost", "Profit", "Margin %"]
                
            elif report_type == "Supplier Performance":
                cursor.execute('''
                    SELECT s.name, COUNT(po.id) as order_count, 
                           SUM(po.total_amount) as total_spend,
                           AVG(julianday(po.expected_delivery) - julianday(po.order_date)) as avg_delivery_days,
                           COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as received_count
                    FROM suppliers s
                    LEFT JOIN purchase_orders po ON s.id = po.supplier_id
                    GROUP BY s.name
                    ORDER BY total_spend DESC
                ''')
                headers = ["Supplier", "Orders", "Total Spend", "Avg Delivery Days", "Received"]
            
            # Create table
            self.create_report_table(content_frame, headers, cursor.fetchall())
            
        except Exception as e:
            showerror("Error", f"Failed to generate report: {str(e)}")

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

    def export_report(self, report_type):
        """Export the current report to CSV"""
        file_path = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Report As",
            initialfile=f"{report_type.replace(' ', '_')}_Report_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if not file_path:
            return
            
        try:
            cursor = self.db.conn.cursor()
            
            if report_type == "Inventory Summary":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.price, 
                           (i.quantity * i.price) as value, i.location
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY c.name, p.name
                ''')
                headers = ["Product", "Category", "Quantity", "Price", "Value", "Location"]
                
            elif report_type == "Low Stock Alert":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.reorder_point, 
                           i.location, (i.quantity * i.price) as value
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.quantity <= i.reorder_point
                    ORDER BY i.quantity
                ''')
                headers = ["Product", "Category", "Current Qty", "Reorder Point", "Location", "Value"]
                
            elif report_type == "Sales Report":
                cursor.execute('''
                    SELECT s.sale_date, p.name, s.quantity, s.sale_price, 
                           (s.quantity * s.sale_price) as total, s.customer_name
                    FROM sales s
                    JOIN inventory i ON s.inventory_id = i.id
                    JOIN products p ON i.product_id = p.id
                    WHERE s.sale_date >= ?
                    ORDER BY s.sale_date DESC
                ''', (datetime.now() - timedelta(days=30),))
                headers = ["Date", "Product", "Qty", "Price", "Total", "Customer"]
                
            elif report_type == "Category Analysis":
                cursor.execute('''
                    SELECT c.name, COUNT(p.id) as product_count, SUM(i.quantity) as total_quantity,
                           SUM(i.quantity * i.price) as total_value
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id
                    LEFT JOIN inventory i ON p.id = i.product_id
                    GROUP BY c.name
                    ORDER BY total_value DESC
                ''')
                headers = ["Category", "Products", "Total Qty", "Total Value"]
                
            elif report_type == "Profit Margin Analysis":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.price, i.cost, 
                           (i.price - i.cost) as profit, 
                           ((i.price - i.cost) / i.price * 100) as margin_percent
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.price > 0 AND i.cost > 0
                    ORDER BY margin_percent DESC
                ''')
                headers = ["Product", "Category", "Price", "Cost", "Profit", "Margin %"]
                
            elif report_type == "Supplier Performance":
                cursor.execute('''
                    SELECT s.name, COUNT(po.id) as order_count, 
                           SUM(po.total_amount) as total_spend,
                           AVG(julianday(po.expected_delivery) - julianday(po.order_date)) as avg_delivery_days,
                           COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as received_count
                    FROM suppliers s
                    LEFT JOIN purchase_orders po ON s.id = po.supplier_id
                    GROUP BY s.name
                    ORDER BY total_spend DESC
                ''')
                headers = ["Supplier", "Orders", "Total Spend", "Avg Delivery Days", "Received"]
            
            # Write to CSV
            try:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    writer.writerows(cursor.fetchall())
            except UnicodeEncodeError:
                with open(file_path, 'w', newline='', encoding=system_encoding, errors='replace') as csvfile:   
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    writer.writerows(cursor.fetchall())
            showinfo("Success", f"Report exported successfully to {file_path}")
            
        except Exception as e:
            showerror("Error", f"Failed to export report: {str(e)}")

    

    def print_report(self, report_type):
        """Print the current report"""
        def has_arabic(text):
            return any('\u0600' <= char <= '\u06FF' for char in str(text))
        try:
            # Create a temporary HTML file with the report content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{report_type} Report</title>
                <style>
                    body {{ font-family: Segoe UI, Tahoma, Arial Unicode MS, Arial, sans-serif; margin: 20px; direction: auto;}}
                    h1 {{ color: #333; text-align: center;}}
                    p {{ color: #666; text-align: center;}}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body>
                <h1>{report_type} Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                <table>
            """
            
            cursor = self.db.conn.cursor()
            headers = []
            
            if report_type == "Inventory Summary":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.price, 
                           (i.quantity * i.price) as value, i.location
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY c.name, p.name
                ''')
                headers = ["Product", "Category", "Quantity", "Price", "Value", "Location"]
                
            elif report_type == "Low Stock Alert":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.quantity, i.reorder_point, 
                           i.location, (i.quantity * i.price) as value
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.quantity <= i.reorder_point
                    ORDER BY i.quantity
                ''')
                headers = ["Product", "Category", "Current Qty", "Reorder Point", "Location", "Value"]
                
            elif report_type == "Sales Report":
                cursor.execute('''
                    SELECT s.sale_date, p.name, s.quantity, s.sale_price, 
                           (s.quantity * s.sale_price) as total, s.customer_name
                    FROM sales s
                    JOIN inventory i ON s.inventory_id = i.id
                    JOIN products p ON i.product_id = p.id
                    WHERE s.sale_date >= ?
                    ORDER BY s.sale_date DESC
                ''', (datetime.now() - timedelta(days=30),))
                headers = ["Date", "Product", "Qty", "Price", "Total", "Customer"]
                
            elif report_type == "Category Analysis":
                cursor.execute('''
                    SELECT c.name, COUNT(p.id) as product_count, SUM(i.quantity) as total_quantity,
                           SUM(i.quantity * i.price) as total_value
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id
                    LEFT JOIN inventory i ON p.id = i.product_id
                    GROUP BY c.name
                    ORDER BY total_value DESC
                ''')
                headers = ["Category", "Products", "Total Qty", "Total Value"]
                
            elif report_type == "Profit Margin Analysis":
                cursor.execute('''
                    SELECT p.name, c.name as category, i.price, i.cost, 
                           (i.price - i.cost) as profit, 
                           ((i.price - i.cost) / i.price * 100) as margin_percent
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    JOIN categories c ON p.category_id = c.id
                    WHERE i.price > 0 AND i.cost > 0
                    ORDER BY margin_percent DESC
                ''')
                headers = ["Product", "Category", "Price", "Cost", "Profit", "Margin %"]
                
            elif report_type == "Supplier Performance":
                cursor.execute('''
                    SELECT s.name, COUNT(po.id) as order_count, 
                           SUM(po.total_amount) as total_spend,
                           AVG(julianday(po.expected_delivery) - julianday(po.order_date)) as avg_delivery_days,
                           COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as received_count
                    FROM suppliers s
                    LEFT JOIN purchase_orders po ON s.id = po.supplier_id
                    GROUP BY s.name
                    ORDER BY total_spend DESC
                ''')
                headers = ["Supplier", "Orders", "Total Spend", "Avg Delivery Days", "Received"]
            
            # Add table headers
            html_content += "<tr>"
            for header in headers:
                html_content += f"<th>{header}</th>"
            html_content += "</tr>"
            
            # Add table rows
            for row in cursor.fetchall():
                html_content += "<tr>"
                for col_idx, value in enumerate(row):
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
                    
                    text_direction = "rtl" if has_arabic(display_value) else "ltr"
                    html_content += f'<td dir="{text_direction}">{display_value}</td>'
                html_content += "</tr>"
                
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                temp_path = temp_file.name
            
            # Open in default browser for printing
            webbrowser.open(temp_path)
            
        except Exception as e:
            showerror("Error", f"Failed to generate print preview: {str(e)}")