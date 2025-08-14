import sqlite3
from tkinter.messagebox import showerror, showinfo
from datetime import datetime, timedelta
from tkinter.filedialog import asksaveasfilename
import csv
import os
import tempfile
import webbrowser
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('DB/device_inventory.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    def create_tables(self):
        """Create all necessary database tables if they don't exist"""
        cursor = self.conn.cursor()
        # Categories table with added color field for reporting visualization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT DEFAULT '#3498db'
            )
        ''')
        # Products table with additional fields for more detailed information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                brand TEXT,
                model TEXT,
                specs TEXT,
                image_path TEXT,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        # Inventory table with location and condition fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER DEFAULT 0,
                price REAL,
                cost REAL,
                sku TEXT UNIQUE,
                location TEXT,
                condition TEXT,
                reorder_point INTEGER DEFAULT 5,
                last_restock_date TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        # Enhanced sales table with customer information and payment method
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER,
                sale_date TIMESTAMP,
                quantity INTEGER,
                sale_price REAL,
                description TEXT,
                customer_name TEXT,
                customer_email TEXT,
                payment_method TEXT,
                invoice_number TEXT,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id)
            )
        ''')
        # Add suppliers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                website TEXT,
                notes TEXT
            )
        ''')
        # Add purchase orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchase_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                order_date TIMESTAMP,
                expected_delivery TIMESTAMP,
                status TEXT,
                total_amount REAL,
                notes TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        # Add purchase order items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS po_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                po_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                unit_cost REAL,
                FOREIGN KEY (po_id) REFERENCES purchase_orders (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        self.conn.commit()
    def export(self, export_type, file_path):
        try:
            cursor = self.conn.cursor()
            
            if export_type == "products":
                cursor.execute('''
                    SELECT p.name, c.name as category, p.brand, p.model, p.specs, p.image_path
                    FROM products p
                    JOIN categories c ON p.category_id = c.id
                    ORDER BY c.name, p.name
                ''')
                headers = ["name", "category", "brand", "model", "specs", "image_path"]
                
            elif export_type == "inventory":
                cursor.execute('''
                    SELECT p.name, i.quantity, i.price, i.cost, i.sku, 
                           i.location, i.condition, i.reorder_point
                    FROM inventory i
                    JOIN products p ON i.product_id = p.id
                    ORDER BY p.name
                ''')
                headers = ["product", "quantity", "price", "cost", "sku", 
                          "location", "condition", "reorder_point"]
                
            elif export_type == "categories":
                cursor.execute('''
                    SELECT name, description, color
                    FROM categories
                    ORDER BY name
                ''')
                headers = ["name", "description", "color"]
                
            elif export_type == "suppliers":
                cursor.execute('''
                    SELECT name, contact_person, email, phone, address, website, notes
                    FROM suppliers
                    ORDER BY name
                ''')
                headers = ["name", "contact_person", "email", "phone", 
                          "address", "website", "notes"]
                
            elif export_type == "sales":
                cursor.execute('''
                    SELECT p.name, s.sale_date, s.quantity, s.sale_price, 
                           s.customer_name, s.customer_email, s.payment_method, 
                           s.invoice_number, s.description
                    FROM sales s
                    JOIN inventory i ON s.inventory_id = i.id
                    JOIN products p ON i.product_id = p.id
                    ORDER BY s.sale_date DESC
                ''')
                headers = ["product", "sale_date", "quantity", "sale_price", 
                          "customer_name", "customer_email", "payment_method", 
                          "invoice_number", "description"]
                
            elif export_type == "orders":
                cursor.execute('''
                    SELECT po.id as po_number, s.name as supplier, po.order_date, 
                           po.expected_delivery, po.status, po.total_amount, po.notes
                    FROM purchase_orders po
                    JOIN suppliers s ON po.supplier_id = s.id
                    ORDER BY po.order_date DESC
                ''')
                headers = ["po_number", "supplier", "order_date", 
                          "expected_delivery", "status", "total_amount", "notes"]
                
                # Export order items separately
                items_path = os.path.splitext(file_path)[0] + "_items.csv"
                cursor.execute('''
                    SELECT po.id as po_number, p.name as product, poi.quantity, poi.unit_cost
                    FROM po_items poi
                    JOIN purchase_orders po ON poi.po_id = po.id
                    JOIN products p ON poi.product_id = p.id
                    ORDER BY po.id, p.name
                ''')
                items_headers = ["po_number", "product", "quantity", "unit_cost"]
                
                with open(items_path, 'w', newline='', encoding='utf-8') as items_file:
                    writer = csv.writer(items_file)
                    writer.writerow(items_headers)
                    writer.writerows(cursor.fetchall())
                
            else:
                showerror("Error", f"Unknown export type: {export_type}")
                return
                
            # Write main export file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(cursor.fetchall())
                
            message = f"Exported {export_type} data successfully to {file_path}"
            if export_type == "orders":
                message += f"\nOrder items exported to {items_path}"
                
            showinfo("Success", message)
            
        except Exception as e:
            showerror("Error", f"Failed to export data: {str(e)}")

    def backup(self, backup_path):
        import shutil
        """Backup the database to a specified path"""
        if backup_path:
            try:
                # Close current connection
                self.conn.close()
                
                # Copy file
                shutil.copy2('device_inventory.db', backup_path)
                
                # Reopen connection
                self.db = Database()
                
                showinfo("Success", f"Database backed up successfully to {backup_path}")
            except Exception as e:
                showerror("Error", f"Failed to backup database: {str(e)}")
                # Try to reopen connection if backup failed
                self.db = Database()
            
    def export_report(self, report_type):
        """Export the current report to CSV"""
        file_path = asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Report As",
            initialfile=f"{report_type.replace(' ', '_')}_Report_{datetime.now().strftime('%d-%m-%Y')}.csv"
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
                           AVG(DATEDIFF(po.expected_delivery, po.order_date)) as avg_delivery_days,
                           COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as received_count
                    FROM suppliers s
                    LEFT JOIN purchase_orders po ON s.id = po.supplier_id
                    GROUP BY s.name
                    ORDER BY total_spend DESC
                ''')
                headers = ["Supplier", "Orders", "Total Spend", "Avg Delivery Days", "Received"]
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(cursor.fetchall())
                
            showinfo("Success", f"Report exported successfully to {file_path}")
            
        except Exception as e:
            showerror("Error", f"Failed to export report: {str(e)}")
    
    def print_report(self, report_type):
        """Print the current report"""
        try:
            # Create a temporary HTML file with the report content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{report_type} Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    tr:nth-child(even) {{ background-color: #f9f9f9; }}
                </style>
            </head>
            <body>
                <h1>{report_type} Report</h1>
                <p>Generated on {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
                <table>
            """
            
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
                           AVG(DATEDIFF(po.expected_delivery, po.order_date)) as avg_delivery_days,
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
                for value in row:
                    # Format numeric values
                    if isinstance(value, (float, int)):
                        if value == int(value):
                            display_value = str(int(value))
                        else:
                            display_value = f"{value:.2f}"
                        
                        # Add dollar sign for monetary values
                        if headers[self.col_idx] in ["Price", "Cost", "Profit", "Total", "Value", "Total Spend"]:
                            display_value = f"${display_value}"
                        elif headers[self.col_idx] == "Margin %":
                            display_value = f"{display_value}%"
                    else:
                        display_value = str(value) if value is not None else "N/A"
                    
                    html_content += f"<td>{display_value}</td>"
                html_content += "</tr>"
            
            html_content += """
                </table>
            </body>
            </html>
            """
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write(html_content)
                temp_path = temp_file.name
            
            # Open in default browser for printing
            webbrowser.open(temp_path)
            
        except Exception as e:
            showerror("Error", f"Failed to generate print preview: {str(e)}")

    def get_inventory_item(self, inventory_id):
        """Retrieve inventory item details with product and category info"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                i.id, i.sku, p.name, c.name, i.quantity, 
                i.price, i.cost, i.location, i.condition, i.reorder_point
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE i.id = ?
        ''', (inventory_id,))
        return cursor.fetchone()

    def edit_inventory_item(self,inventory_id, new_quantity,new_price,new_cost,sku_entry,location_entry,new_reorder,condition_combo):
        # Update database
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE inventory 
            SET quantity = ?, price = ?, cost = ?, sku = ?,
                location = ?, condition = ?, reorder_point = ?
            WHERE id = ?
        ''', (
            new_quantity, new_price, new_cost, sku_entry,
            location_entry, condition_combo, new_reorder,
            inventory_id
        ))
        
        self.conn.commit()

    def generate_report(self, report_type):
        # Generate report based on type
        cursor = self.db.conn.cursor()
        
        if report_type == "Inventory Summary":
            # Inventory summary report
            cursor.execute('''
                SELECT p.name, c.name as category, i.quantity, i.price, 
                       (i.quantity * i.price) as value, i.location
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                ORDER BY c.name, p.name
            ''')
            
            # Create table
            headers = ["Product", "Category", "Quantity", "Price", "Value", "Location"]
            
        elif report_type == "Low Stock Alert":
            # Low stock report
            cursor.execute('''
                SELECT p.name, c.name as category, i.quantity, i.reorder_point, 
                       i.location, (i.quantity * i.price) as value
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                JOIN categories c ON p.category_id = c.id
                WHERE i.quantity <= i.reorder_point
                ORDER BY i.quantity
            ''')
            
            # Create table
            headers = ["Product", "Category", "Current Qty", "Reorder Point", "Location", "Value"]
            
        elif report_type == "Sales Report":
            # Sales report
            cursor.execute('''
                SELECT s.sale_date, p.name, s.quantity, s.sale_price, 
                       (s.quantity * s.sale_price) as total, s.customer_name
                FROM sales s
                JOIN inventory i ON s.inventory_id = i.id
                JOIN products p ON i.product_id = p.id
                WHERE s.sale_date >= ?
                ORDER BY s.sale_date DESC
            ''', (datetime.now() - timedelta(days=30),))
            
            # Create table
            headers = ["Date", "Product", "Qty", "Price", "Total", "Customer"]
            
        elif report_type == "Category Analysis":
            # Category analysis report
            cursor.execute('''
                SELECT c.name, COUNT(p.id) as product_count, SUM(i.quantity) as total_quantity,
                       SUM(i.quantity * i.price) as total_value
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                LEFT JOIN inventory i ON p.id = i.product_id
                GROUP BY c.name
                ORDER BY total_value DESC
            ''')
            
            # Create table
            headers = ["Category", "Products", "Total Qty", "Total Value"]
            
        elif report_type == "Profit Margin Analysis":
            # Profit margin analysis
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
            
            # Create table
            headers = ["Product", "Category", "Price", "Cost", "Profit", "Margin %"]
            
        elif report_type == "Supplier Performance":
            # Supplier performance report
            cursor.execute('''
                SELECT s.name, COUNT(po.id) as order_count, 
                       SUM(po.total_amount) as total_spend,
                       AVG(DATEDIFF(po.expected_delivery, po.order_date)) as avg_delivery_days,
                       COUNT(CASE WHEN po.status = 'Received' THEN 1 END) as received_count
                FROM suppliers s
                LEFT JOIN purchase_orders po ON s.id = po.supplier_id
                GROUP BY s.name
                ORDER BY total_spend DESC
            ''')
            # Create table
            headers = ["Supplier", "Orders", "Total Spend", "Avg Delivery Days", "Received"]
        return headers, cursor.fetchall()
    
    def get_categories(self):
        """Get all category names from the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        return categories
    
    def show_inventory_dashboard(self):
        # Query for metrics
        cursor = self.conn.cursor()
        
        # Total inventory value
        cursor.execute("SELECT SUM(quantity * price) FROM inventory")
        total_value = cursor.fetchone()[0] or 0
        
        # Total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0] or 0
        
        # Low stock items
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity < reorder_point")
        low_stock = cursor.fetchone()[0] or 0
        
        # Recent sales
        cursor.execute("SELECT COUNT(*), SUM(quantity * sale_price) FROM sales WHERE sale_date >= ?", 
                      (datetime.now() - timedelta(days=30),))
        sales_count, sales_value = cursor.fetchone()
        sales_count = sales_count or 0
        sales_value = sales_value or 0

        # Setup matplotlib charts
        # Left chart: Category distribution
        cursor.execute("""
            SELECT c.name, c.color, SUM(i.quantity) 
            FROM categories c
            JOIN products p ON c.id = p.category_id
            JOIN inventory i ON p.id = i.product_id
            GROUP BY c.name
        """)

        # Right chart: Recent sales
        cursor.execute("""
            SELECT DATE(sale_date) as date, SUM(quantity * sale_price) as total
            FROM sales
            WHERE sale_date >= ?
            GROUP BY DATE(sale_date)
            ORDER BY date
        """, (datetime.now() - timedelta(days=10),))
        sales_data = cursor.fetchall()

        # Get recent sales
        cursor.execute("""
            SELECT s.sale_date, p.name, s.quantity, s.sale_price, s.customer_name
            FROM sales s
            JOIN inventory i ON s.inventory_id = i.id
            JOIN products p ON i.product_id = p.id
            ORDER BY s.sale_date DESC
            LIMIT 5
        """)
        recent_sales = cursor.fetchall()

        category_data = cursor.fetchall()
        return total_value, total_products, low_stock, sales_count, sales_value, category_data, sales_data, recent_sales

    def refresh_inventory(self, search_term, category_filter, sort_option):
        
        query = '''
            SELECT i.id, i.sku, p.name, c.name, i.quantity, i.price, i.location
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        '''
        params = []

        if search_term:
            query += " AND (p.name LIKE ? OR i.sku LIKE ?)"
            params.extend(['%' + search_term + '%', '%' + search_term + '%'])

        if category_filter != "All":
            query += " AND c.name = ?"
            params.append(category_filter)

        sort_column = "p.name"
        if sort_option == "Category":
            sort_column = "c.name"
        elif sort_option == "Price":
            sort_column = "i.price"
        elif sort_option == "Quantity":
            sort_column = "i.quantity"

        query += f" ORDER BY {sort_column}"

        cursor = self.conn.cursor()
        cursor.execute(query, params)

        return cursor.fetchall()
    def show_inventory(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        total_items = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(quantity) FROM inventory")
        total_quantity = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(quantity * price) FROM inventory")
        total_value = cursor.fetchone()[0] or 0
        return total_items, total_quantity, total_value
        
    def insert_product(self, category, product_name, brand, model, specs, image_path,
                        quantity, price, cost, sku, location, condition, reorder_point):
        # Begin database transaction
        cursor = self.conn.cursor()  
        try:
            # Get or create category
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
            category_row = cursor.fetchone()
            
            if category_row:
                category_id = category_row[0]
            else:
                cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))
                category_id = cursor.lastrowid
                
            # Insert product
            cursor.execute('''
                INSERT INTO products (
                    category_id, name, brand, model, specs, image_path,
                    created_at, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                category_id, product_name, brand, model, specs, image_path,
                datetime.now(), datetime.now()
            ))
            product_id = cursor.lastrowid
            
            # Insert inventory record
            cursor.execute('''
                INSERT INTO inventory (
                    product_id, quantity, price, cost, sku,
                    location, condition, reorder_point
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product_id, quantity, price, cost, sku,
                location, condition, reorder_point
            ))
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def sell_product(self,inventory_id):
        # Get inventory item details
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT i.id, i.sku, p.name, i.quantity, i.price, i.cost
            FROM inventory i
            JOIN products p ON i.product_id = p.id
            WHERE i.id = ?
        ''', (inventory_id,))
        row = cursor.fetchone()
        return row
    
    def process_sale(self, inventory_id, qty, sale_price, description, customer_name, customer_email, payment, invoice):
        # Add to sales database
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sales (
                inventory_id, sale_date, quantity, sale_price, 
                description, customer_name, customer_email, 
                payment_method, invoice_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            inventory_id, datetime.now(), qty, sale_price, 
            description, customer_name, customer_email, 
            payment, invoice
        ))
        
        # Update inventory
        cursor.execute('''
            UPDATE inventory 
            SET quantity = quantity - ? 
            WHERE id = ?
        ''', (qty, inventory_id))
        
        self.conn.commit()

    def show_categories(self,search_term=None):
        cursor = self.conn.cursor()
        if search_term != None:
            cursor.execute('''
                SELECT c.id, c.name, c.description, c.color, COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                WHERE c.name LIKE ?
                GROUP BY c.id
                ORDER BY c.name
            ''', ('%' + search_term + '%',))
        else:
            cursor.execute('''
                SELECT c.id, c.name, c.description, c.color, COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id
                GROUP BY c.id
                ORDER BY c.name
            ''')
        return cursor.fetchall()

    def add_category(self, new_category):
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (new_category.strip(),))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("Category already exists.")

    def show_suppliers(self,search_term=None):
        cursor = self.conn.cursor()
        if search_term:
            cursor.execute('''
                SELECT id, name, contact_person, email, phone
                FROM suppliers
                WHERE name LIKE ?
                ORDER BY name
            ''', ('%' + search_term + '%',))
        else:
            cursor.execute('''
                SELECT id, name, contact_person, email, phone
                FROM suppliers
                ORDER BY name
            ''')
        return cursor.fetchall()

    def refresh_purchase_table(self, status_filter="All", date_filter="All Time"):
        query = '''
            SELECT po.id, s.name, po.order_date, po.expected_delivery, 
                po.status, po.total_amount, po.notes
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE 1=1
        '''
        params = []
        
        if status_filter != "All":
            query += " AND po.status = ?"
            params.append(status_filter)
            
        if date_filter != "All Time":
            today = datetime.now()
            if date_filter == "This Month":
                start_date = datetime(today.year, today.month, 1)
                query += " AND po.order_date >= ?"
                params.append(start_date.strftime("%d-%m-%Y"))
            elif date_filter == "Last Month":
                if today.month == 1:
                    start_date = datetime(today.year-1, 12, 1)
                else:
                    start_date = datetime(today.year, today.month-1, 1)
                end_date = datetime(today.year, today.month, 1)
                query += " AND po.order_date >= ? AND po.order_date < ?"
                params.extend([start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y")])
            elif date_filter == "This Year":
                start_date = datetime(today.year, 1, 1)
                query += " AND po.order_date >= ?"
                params.append(start_date.strftime("%d-%m-%Y"))
        
        query += " ORDER BY po.order_date DESC"
        
        # Execute query
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()