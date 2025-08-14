from tkinter.messagebox import showerror, showinfo, showwarning
from tkinter.filedialog import asksaveasfilename
from datetime import datetime, timedelta
from tkinter import StringVar, END, Menu, Scrollbar
from tkinter.ttk import Treeview, Style
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkTextbox
from customtkinter import CTkButton, CTkToplevel, CTkComboBox
from ttkwidgets.autocomplete import AutocompleteCombobox
from Packages.products import productsManager
from Packages.database import Database
import csv
import locale

# Get system default encoding
system_encoding = locale.getpreferredencoding()
class salesManager:
    def __init__(self, root, main_frame):
        self.db = Database()
        self.root = root
        self.main_frame = main_frame
        self.products = productsManager(self.root, self.main_frame)

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable

    def show_sales(self):
        """Display sales management page with ttk widgets"""
        self.clear_main_frame()
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
        Style().configure("TFrame", background="transparent")
        # Header frame
        header_frame = CTkFrame(self.main_frame, bg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="n", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)  # Middle space expands
        
        CTkLabel(header_frame, text="Sales Management", bg_color="transparent",
                font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="e")
        
        # Filter frame
        filter_frame = CTkFrame(self.main_frame, bg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        CTkLabel(filter_frame, text="Date Range:", bg_color="transparent").grid(row=0, column=0, padx=5)
        self.date_filter = CTkComboBox(filter_frame, values=["All Time", "Today", "This Week", "This Month", "This Year"])
        self.date_filter.grid(row=0, column=1, padx=5)
        self.date_filter.set("All Time")
        self.date_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_sales_table())
        
        CTkLabel(filter_frame, text="Product:", bg_color="transparent").grid(row=0, column=2, padx=5)
        self.product_filter = AutocompleteCombobox(filter_frame)
        self.product_filter.grid(row=0, column=3, padx=5, sticky="ew")
        
        # Get products for filter
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM products ORDER BY name")
        self.product_filter.configure(completevalues=[row[0] for row in cursor.fetchall()])
        self.product_filter.bind("<Return>", lambda e: self.refresh_sales_table())
        
        CTkButton(filter_frame, text="Apply Filters", 
                command=lambda: self.refresh_sales_table()).grid(row=0, column=4, padx=10)
        
        # Create table container frame
        table_frame = CTkFrame(self.main_frame, bg_color="transparent")
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize the table
        self.create_sales_treeview(table_frame)
        
        # Summary frame
        self.summary_frame = CTkFrame(self.main_frame, bg_color="transparent")
        self.summary_frame.grid(row=3, column=0, sticky="n", padx=20, pady=10)
        
        # Load initial data
        self.refresh_sales_table()

    def create_sales_treeview(self, parent_frame):
        """Create the Treeview table for sales display"""
        # Create Treeview with scrollbars
        tree_container = CTkFrame(parent_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Define columns
        columns = ("ID", "Date", "Customer", "Product", "Quantity", "Unit Price", "Total", "Status")
        
        # Create Treeview
        self.sales_tree = Treeview(tree_container, columns=columns, show='headings', height=15)
        
        # Configure Treeview style
        style = Style()
        style.theme_use('clam')
        style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading",
                    background="#1f538d",
                    foreground="white",
                    font=("Arial", 10, "bold"))
        style.map("Treeview", background=[('selected', '#1f538d')])
        
        # Configure columns
        column_widths = {
            "ID": 80,
            "Date": 120,
            "Customer": 150,
            "Product": 200,
            "Quantity": 80,
            "Unit Price": 100,
            "Total": 100,
            "Status": 100
        }
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
            self.sales_tree.column(col, width=column_widths[col], anchor='center')
        
        # Add scrollbars
        v_scroll = Scrollbar(tree_container, orient="vertical", command=self.sales_tree.yview)
        h_scroll = Scrollbar(tree_container, orient="horizontal", command=self.sales_tree.xview)
        self.sales_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.sales_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.sales_tree.bind('<Double-1>', self.on_sale_double_click)
        self.sales_tree.bind('<Button-3>', self.on_sale_right_click)

    def on_sale_double_click(self, event):
        """Handle double-click on sale item"""
        item = self.sales_tree.selection()
        if item:
            sale_id = self.sales_tree.item(item, 'values')[0]
            self.show_sale_details(sale_id)

    def on_sale_right_click(self, event):
        """Handle right-click on sale item"""
        item = self.sales_tree.identify_row(event.y)
        if item:
            self.sales_tree.selection_set(item)
            sale_id = self.sales_tree.item(item, 'values')[0]
            status = self.sales_tree.item(item, 'values')[-1]
            self.show_sale_context_menu(event, sale_id, status)

    def show_sale_context_menu(self, event, sale_id, status):
        """Show context menu for sales"""
        menu = Menu(self.sales_tree, tearoff=0)
        menu.configure(bg="#2b2b2b", fg="white", activebackground="#1f538d", activeforeground="white")
        
        menu.add_command(label="View Details", command=lambda: self.show_sale_details(sale_id))
        
        if status == "Pending":
            menu.add_command(label="Mark as Completed", command=lambda: self.update_sale_status(sale_id, "Completed"))
            menu.add_command(label="Cancel Sale", command=lambda: self.update_sale_status(sale_id, "Cancelled"))
        
        menu.add_separator()
        menu.add_command(label="Close", command=menu.destroy)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def update_sale_status(self, sale_id, new_status):
        """Update sale status in database"""
        try:
            self.db.conn.execute("UPDATE sales SET status=? WHERE id=?", (new_status, sale_id))
            self.db.conn.commit()
            self.refresh_sales_table()
            showinfo("Success", f"Sale #{sale_id} status updated to {new_status}")
        except Exception as e:
            showerror("Error", f"Failed to update sale status: {str(e)}")
    
    def refresh_sales_table(self, date_range=None, product_filter=None):
        """Refresh the sales table using the existing sales table structure"""
        # Use current filter values if none provided
        if date_range is None:
            date_range = self.date_filter.get()
        if product_filter is None:
            product_filter = self.product_filter.get()
        
        # Clear existing data
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # Build query using the existing sales table structure
        query = '''
            SELECT s.id, s.sale_date, p.name, s.quantity, s.sale_price, 
                COALESCE(s.customer_name, 'Walk-in'), 
                (s.quantity * s.sale_price) as total
            FROM sales s
            JOIN inventory i ON s.inventory_id = i.id
            JOIN products p ON i.product_id = p.id
            WHERE 1=1
        '''
        params = []
        
        # Date filtering
        today = datetime.now().date()
        if date_range == "Today":
            query += " AND DATE(s.sale_date) = ?"
            params.append(today)
        elif date_range == "This Week":
            start_date = today - timedelta(days=today.weekday())
            query += " AND DATE(s.sale_date) BETWEEN ? AND ?"
            params.extend([start_date, today])
        elif date_range == "This Month":
            query += " AND strftime('%m-%Y', s.sale_date) = strftime('%m-%Y', 'now')"
        elif date_range == "This Year":
            query += " AND strftime('%Y', s.sale_date) = strftime('%Y', 'now')"
        
        # Product filtering - removed reference to p.sku which doesn't exist
        if product_filter:
            query += " AND p.name LIKE ?"
            params.append(f"%{product_filter}%")
        
        query += " ORDER BY s.sale_date DESC, s.id DESC"
        
        # Execute query with error handling
        try:
            cursor = self.db.conn.cursor()
            cursor.execute(query, params)
            sales_data = cursor.fetchall()
            
            # Add sales to treeview
            total_sales = 0
            
            for sale_id, sale_date, product_name, quantity, sale_price, customer_name, total in sales_data:
                # Format values
                sale_date_str = sale_date.split(" ")[0] if sale_date else "N/A"
                
                # Insert item
                self.sales_tree.insert("", "end", 
                    values=(
                        sale_id,
                        sale_date_str,
                        customer_name,
                        product_name,
                        quantity,
                        f"${sale_price:.2f}",
                        f"${total:.2f}",
                        "Completed"  # Default status
                    ),
                    tags=(str(sale_id),))  # Tag with sale ID for event handling
                
                total_sales += total
            
            # Update summary
            self.update_sales_summary(total_sales, len(sales_data))
            
        except Exception as e:
            showerror("Database Error", f"Failed to load sales data:\n{str(e)}")
            self.sales_tree.insert("", "end", values=("Error", "Loading failed", "", "", "", "", "", ""))

    def validate_multilingual_input(self, event):
        import unicodedata
        # Allow all control and navigation keys
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 
                        'Home', 'End', 'Tab', 'Return', 'Enter', 'Shift_L', 'Shift_R',
                        'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
            return None
        
        # Skip if no character (some key events don't produce characters)
        if not event.char:
            return "break"
        
        # Allow common punctuation and symbols
        if event.char in (' ', '\t', '\n', '،', '؛', '؟', '.', ',', '!', '?', '(', ')', '-', '_', '\'', '"', ':', ';'):
            return None
        
        # Check if character is either:
        # 1. Basic Latin (English) - Unicode block 0000-007F
        # 2. Arabic character (including Persian and extended Arabic)
        try:
            char_code = ord(event.char)
            char_name = unicodedata.name(event.char)
            
            # Allow English (basic Latin) or Arabic/Persian characters
            is_english = 0x0000 <= char_code <= 0x007F
            is_arabic = (char_name.startswith('ARABIC') or 
                        char_name.startswith('PERSIAN') or 
                        char_name.startswith('EXTENDED ARABIC'))
            
            if not (is_english or is_arabic):
                return "break"
                
        except ValueError:  # Character not found in Unicode database
            return "break"
        
        return None
    def show_sale_details(self, sale_id):
        """Display details of a specific sale"""
        try:
            # Get sale details from database
            cursor = self.db.conn.cursor()
            cursor.execute('''
                SELECT s.id, s.sale_date, p.name, s.quantity, s.sale_price, 
                    s.customer_name, s.customer_email, s.payment_method,
                    (s.quantity * s.sale_price) as total, s.description
                FROM sales s
                JOIN inventory i ON s.inventory_id = i.id
                JOIN products p ON i.product_id = p.id
                WHERE s.id = ?
            ''', (sale_id,))
            
            sale_data = cursor.fetchone()
            
            if not sale_data:
                showerror("Error", "Sale not found")
                return
                
            # Create details window
            detail_window = CTkToplevel(self.root)
            detail_window.title(f"Sale Details - #{sale_id}")
            detail_window.geometry("600x400")
            
            # Display sale information
            CTkLabel(detail_window, text=f"Sale #{sale_id}", font=("Arial", 16, "bold")).pack(pady=10)
            
            info_frame =CTkFrame(detail_window)
            info_frame.pack(fill="x", padx=20, pady=10)
            
            # Left column
            left_frame = CTkFrame(info_frame)
            left_frame.pack(side="left", fill="both", expand=True)
            
            CTkLabel(left_frame, text=f"Date: {sale_data[1]}").pack(anchor="w")
            CTkLabel(left_frame, text=f"Product: {sale_data[2]}").pack(anchor="w")
            CTkLabel(left_frame, text=f"Quantity: {sale_data[3]}").pack(anchor="w")
            
            # Right column
            right_frame = CTkFrame(info_frame)
            right_frame.pack(side="right", fill="both", expand=True)
            
            CTkLabel(right_frame, text=f"Price: ${sale_data[4]:.2f}").pack(anchor="w")
            CTkLabel(right_frame, text=f"Total: ${sale_data[8]:.2f}").pack(anchor="w")
            CTkLabel(right_frame, text=f"Payment: {sale_data[7] or 'Not specified'}").pack(anchor="w")
            
            # Customer info
            cust_frame = CTkFrame(detail_window)
            cust_frame.pack(fill="x", padx=20, pady=10)
            
            CTkLabel(cust_frame, text="Customer Information", font=("Arial", 12, "bold")).pack(anchor="w")
            CTkLabel(cust_frame, text=f"Name: {sale_data[5] or 'Walk-in'}").pack(anchor="w")
            CTkLabel(cust_frame, text=f"Email: {sale_data[6] or 'Not provided'}").pack(anchor="w")
            
            # Notes/description
            if sale_data[9]:
                notes_frame = CTkFrame(detail_window)
                notes_frame.pack(fill="x", padx=20, pady=10)
                
                CTkLabel(notes_frame, text="Notes:", font=("Arial", 12, "bold")).pack(anchor="w")
                notes_text = CTkTextbox(notes_frame, height=4, wrap="word", bg_color="#2b2b2b")
                notes_text.pack(fill="x")
                notes_text.insert("1.0", sale_data[9])
                notes_text.configure(state="disabled")
                notes_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
                notes_text.configure(font=("Arial", 16))  # Right-align for RTL
            
            # Close button
            CTkButton(detail_window, text="Close", command=detail_window.destroy).pack(pady=10)
            
        except Exception as e:
            showerror("Error", f"Failed to load sale details:\n{str(e)}")

    def update_sales_summary(self, total_amount, transaction_count):
        """Update the summary frame with sales metrics"""
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        # Create summary metrics
        metrics = [
            ("Total Sales", f"${total_amount:,.2f}"),
            ("Transactions", f"{transaction_count}"),
            ("Avg. Sale", f"${total_amount/transaction_count:,.2f}" if transaction_count > 0 else "$0.00")
        ]
        
        # Display metrics
        for i, (label, value) in enumerate(metrics):
            metric_frame = CTkFrame(self.summary_frame, bg_color="#333333")
            metric_frame.grid(row=0, column=i, padx=20, pady=10)
            
            CTkLabel(metric_frame, text=label, bg_color="#333333",
                    font=("Arial", 10, "bold")).pack(anchor="center")
            CTkLabel(metric_frame, text=value, bg_color="#333333",
                    font=("Arial", 12)).pack(anchor="center")
        
        # Add export button
        export_btn = CTkButton(self.summary_frame, text="Export to CSV", bg_color="transparent", 
                            command=self.export_sales_data)
        export_btn.grid(row=0, column=len(metrics), padx=20)

    # Simple version - Just export whatever data your refresh_sales_table uses
    def export_sales_data_simple(self):
        """Simple export function using the same data as your table"""
        try:
            # Get current filter values
            date_range = self.date_filter.get() if hasattr(self, 'date_filter') else "All Time"
            product_filter = self.product_filter.get() if hasattr(self, 'product_filter') else "All Products"
            
            # Use a simple SELECT * query from your main sales table
            cursor = self.db.conn.cursor()
            
            # Find your sales table name
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%sales%'")
            tables = cursor.fetchall()
            
            if not tables:
                # Try other common names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                all_tables = [row[0] for row in cursor.fetchall()]
                showinfo("Info",f"Available tables: {all_tables}")
                
                # Use the first table that might contain sales data
                possible_names = ['transactions', 'orders', 'receipts', 'invoices', 'inventory']
                sales_table = None
                for name in possible_names:
                    if name in all_tables:
                        sales_table = name
                        break
                
                if not sales_table:
                    sales_table = all_tables[0] if all_tables else 'sales'
            else:
                sales_table = tables[0][0]
            
            # Simple query - just get all data
            query = f"SELECT * FROM {sales_table}"
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Get column names
            cursor.execute(f"PRAGMA table_info({sales_table})")
            columns = [row[1] for row in cursor.fetchall()]
            
            if not results:
                showwarning("No Data", "No sales data found in the database.")
                return
            
            # Prompt for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save Sales Report As",
                initialname=f"sales_export_{datetime.now().strftime('%d-%m-%Y_%H%M')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write column headers
                    writer.writerow(columns)
                    
                    # Write all data
                    for row in results:
                        writer.writerow([str(cell) if cell is not None else '' for cell in row])
                    
                    # Add summary
                    writer.writerow([])
                    writer.writerow(['SUMMARY'])
                    writer.writerow(['Total Records:', len(results)])
                    writer.writerow(['Export Date:', datetime.now().strftime("%d-%m-%Y %H:%M")])
                
                showinfo("Export Successful", 
                                f"Data exported successfully!\n\nFile: {file_path}\nRecords: {len(results)}")
        
        except Exception as e:
            showerror("Export Error", f"Failed to export data:\n{str(e)}")

    def export_sales_data(self):
        """Export current filtered sales data to CSV"""
        try:
            # Get current filter values
            date_range = self.date_filter.get() if hasattr(self, 'date_filter') else "All Time"
            product_filter = self.product_filter.get() if hasattr(self, 'product_filter') else ""
            
            # First check what columns exist in the sales table
            cursor = self.db.conn.cursor()
            cursor.execute("PRAGMA table_info(sales)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Build the query based on available columns
            query = '''
                SELECT 
                    s.id,
                    s.sale_date,
                    COALESCE(s.customer_name, 'Walk-in') as customer,
                    p.name as product,
                    s.quantity,
                    s.sale_price,
                    (s.quantity * s.sale_price) as total
            '''
            
            # Add status column only if it exists
            if 'status' in columns:
                query += ', s.status'
            else:
                query += ', "Completed" as status'
                
            query += '''
                FROM sales s
                JOIN inventory i ON s.inventory_id = i.id
                JOIN products p ON i.product_id = p.id
                WHERE 1=1
            '''
            
            params = []
            
            # Date filtering
            today = datetime.now().date()
            if date_range == "Today":
                query += " AND DATE(s.sale_date) = ?"
                params.append(today)
            elif date_range == "This Week":
                start_date = today - timedelta(days=today.weekday())
                query += " AND DATE(s.sale_date) BETWEEN ? AND ?"
                params.extend([start_date, today])
            elif date_range == "This Month":
                query += " AND strftime('%m-%Y', s.sale_date) = strftime('%m-%Y', 'now')"
            elif date_range == "This Year":
                query += " AND strftime('%Y', s.sale_date) = strftime('%Y', 'now')"
            
            # Product filtering
            if product_filter:
                query += " AND p.name LIKE ?"
                params.append(f"%{product_filter}%")
            
            query += " ORDER BY s.sale_date DESC, s.id DESC"
            
            # Execute query
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            if not results:
                showwarning("No Data", "No sales data found for the selected filters.")
                return
            
            # Prompt for save location
            file_path = asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save Sales Report As",
                initialfile=f"sales_export_{datetime.now().strftime('%d-%m-%Y_%H%M')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    headers = [
                        "Sale ID", "Date", "Customer", "Product", 
                        "Quantity", "Unit Price", "Total Amount", "Status"
                    ]
                    writer.writerow(headers)
                    
                    # Write data rows
                    for row in results:
                        # Format the data properly
                        formatted_row = [
                            str(row[0]),  # ID
                            str(row[1]).split()[0] if row[1] else "N/A",  # Date
                            str(row[2]),  # Customer
                            str(row[3]),  # Product
                            str(row[4]),  # Quantity
                            f"${float(row[5]):.2f}" if row[5] else "$0.00",  # Unit Price
                            f"${float(row[6]):.2f}" if row[6] else "$0.00",  # Total
                            str(row[7]) if len(row) > 7 else "Completed"  # Status
                        ]
                        writer.writerow(formatted_row)
                    
                    # Add summary row
                    writer.writerow([])  # Empty row
                    writer.writerow(["SUMMARY"])
                    writer.writerow(["Total Records:", len(results)])
                    writer.writerow(["Export Date:", datetime.now().strftime("%d-%m-%Y %H:%M")])
                    writer.writerow(["Filters Applied:", f"Date: {date_range}, Product: {product_filter}"])
                    
                    # Calculate totals
                    total_amount = sum(float(row[6]) if row[6] else 0 for row in results)
                    total_quantity = sum(int(row[4]) if row[4] else 0 for row in results)
                    writer.writerow(["Total Sales Amount:", f"${total_amount:.2f}"])
                    writer.writerow(["Total Items Sold:", total_quantity])
                
                showinfo("Export Successful", 
                        f"Sales data exported successfully!\n\nFile saved to:\n{file_path}\n\nRecords exported: {len(results)}")
        
        except Exception as e:
            showerror("Export Error", f"Failed to export sales data:\n{str(e)}")

    # Alternative version if your database structure is different
    def export_sales_data_alternative(self):
        """Alternative export function for different database structure"""
        try:
            # Get current filter values
            date_range = self.date_filter.get() if hasattr(self, 'date_filter') else "All Time"
            product_filter = self.product_filter.get() if hasattr(self, 'product_filter') else "All Products"
            
            # Use the same method as your refresh_sales_table to get data
            # This ensures consistency
            sales_data = self.get_filtered_sales_data(date_range, product_filter)
            
            if not sales_data:
                showwarning("No Data", "No sales data found for the selected filters.")
                return
            
            # Prompt for save location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save Sales Report As",
                initialname=f"sales_report_{datetime.now().strftime('%d-%m-%Y_%H%M')}.csv"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers (adjust based on your data structure)
                    headers = [
                        "Sale ID", "Date", "Customer", "Product", 
                        "Quantity", "Unit Price", "Total Amount", "Status"
                    ]
                    writer.writerow(headers)
                    
                    # Write data
                    for row in sales_data:
                        writer.writerow(row)
                    
                    # Add summary
                    writer.writerow([])
                    writer.writerow(["SUMMARY"])
                    writer.writerow(["Total Records:", len(sales_data)])
                    writer.writerow(["Export Date:", datetime.now().strftime("%d-%m-%Y %H:%M")])
                
                showinfo("Export Successful", 
                                f"Sales data exported successfully to:\n{file_path}")
        
        except Exception as e:
            showerror("Export Error", f"Failed to export sales data:\n{str(e)}")

    def get_filtered_sales_data(self, date_range, product_filter):
        """Helper method to get filtered sales data - implement based on your database structure"""
        try:
            # This should match exactly what your refresh_sales_table method does
            # Replace this with your actual database query logic
            
            # Example implementation:
            query = "SELECT * FROM sales WHERE 1=1"
            params = []
            
            # Add your specific filtering logic here
            # This should match your refresh_sales_table method
            
            cursor = self.db.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            showerror("Error", f"Failed to get sales data: {e}")
            return []