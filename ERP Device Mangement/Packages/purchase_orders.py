from Packages.database import Database
from customtkinter import CTkLabel, CTkTextbox, CTkScrollableFrame, CTkToplevel
from customtkinter import CTkFrame, CTkButton, CTkComboBox, CTkEntry
from tkinter import StringVar, END, Menu, Scrollbar
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter.messagebox import showerror, showinfo, askyesno
from datetime import datetime, timedelta
from tkinter.ttk import Treeview, Style
import csv
from tkinter.filedialog import asksaveasfilename
import locale

# Get system default encoding
system_encoding = locale.getpreferredencoding()
class purchaseOrders:
    def __init__(self, root, main_frame):
        self.root = root
        self.main_frame = main_frame
        self.db = Database()

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable

    def show_purchase_orders(self):
        """Display purchase order management page with Treeview table"""
        self.clear_main_frame()
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
        
        # Header frame
        header_frame = CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)  # Middle space expands
        
        CTkLabel(header_frame, text="Purchase Order Management", 
                    font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        CTkButton(header_frame, text="+ Create Purchase Order", 
                    command=self.create_purchase_order).grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Filter frame
        filter_frame = CTkFrame(self.main_frame)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        CTkLabel(filter_frame, text="Status:").grid(row=0, column=0, padx=5)
        self.status_filter = CTkComboBox(filter_frame, values=["All", "Pending", "Ordered", "Received", "Cancelled"])
        self.status_filter.grid(row=0, column=1, padx=5)
        self.status_filter.set("All")
        
        CTkLabel(filter_frame, text="Date Range:").grid(row=0, column=2, padx=5)
        self.date_filter = CTkComboBox(filter_frame, values=["All Time", "This Month", "Last Month", "This Year"])
        self.date_filter.grid(row=0, column=3, padx=5)
        self.date_filter.set("All Time")
        
        CTkButton(filter_frame, text="Apply Filters", 
                    command=lambda: self.refresh_po_table()).grid(row=0, column=4, padx=10)
        
        CTkButton(filter_frame, text="Export Data", 
          command=self.export_purchase_orders).grid(row=0, column=5, padx=10)

        # Create table container frame
        table_frame = CTkFrame(self.main_frame)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize the table
        self.create_po_treeview(table_frame)
        
        # Load initial data
        self.refresh_po_table()

    def create_po_treeview(self, parent_frame):
        """Create the Treeview table for purchase orders"""
        
        # Create Treeview with scrollbars
        tree_container = CTkFrame(parent_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Define columns
        columns = ("PO #", "Supplier", "Order Date", "Expected Delivery", "Status", "Amount")
        
        # Create Treeview
        self.po_tree = Treeview(tree_container, columns=columns, show='tree headings', height=15)
        self.po_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure Treeview style for dark theme
        style = Style()
        style.theme_use('clam')
        
        # Base style configuration
        style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="#ffffff",
                    rowheight=30,
                    fieldbackground="#2b2b2b",
                    bordercolor="#404040",
                    borderwidth=0)
        
        style.configure("Treeview.Heading",
                    background="#1f538d",
                    foreground="#ffffff",
                    font=("Arial", 10, "bold"))
        
        # Configure tag colors for different statuses
        style.configure("Pending.Treeview", background="#34495e")
        style.configure("Ordered.Treeview", background="#2c3e50")
        style.configure("Received.Treeview", background="#27ae60")
        style.configure("Cancelled.Treeview", background="#c0392b")
        
        # Selected item style
        style.map("Treeview",
                background=[('selected', '#1f538d')])
        
        # Configure columns
        self.po_tree.heading('#0', text='ID', anchor='center')
        self.po_tree.column('#0', width=50, minwidth=50, anchor='center', stretch=False)
        
        column_widths = {
            "PO #": 100,
            "Supplier": 200,
            "Order Date": 120,
            "Expected Delivery": 120,
            "Status": 100,
            "Amount": 100
        }
        
        for col in columns:
            self.po_tree.heading(col, text=col, anchor='center')
            self.po_tree.column(col, width=column_widths[col], minwidth=50, anchor='center')
        
        # Add scrollbars
        v_scrollbar = Scrollbar(tree_container, orient="vertical", command=self.po_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.po_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = Scrollbar(tree_container, orient="horizontal", command=self.po_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.po_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.po_tree.bind('<Double-1>', self.on_po_tree_double_click)
        self.po_tree.bind('<Button-3>', self.on_po_tree_right_click)

    def refresh_po_table(self):
        """Update the Treeview with current purchase order data"""
        if not hasattr(self, 'po_tree'):
            return
        
        # Clear existing data
        for item in self.po_tree.get_children():
            self.po_tree.delete(item)
        
        # Build query based on filters
        status_filter = self.status_filter.get()
        date_filter = self.date_filter.get()
        
        orders = self.db.refresh_purchase_table(status_filter, date_filter)
        
        # Add purchase orders to tree
        for order in orders:
            try:
                # Handle both cases where notes may or may not be included
                if len(order) == 6:
                    po_id, supplier_name, order_date, expected_delivery, status, total_amount = order
                else:
                    po_id, supplier_name, order_date, expected_delivery, status, total_amount, _ = order
                
                # Format dates
                order_date_str = order_date.split(" ")[0] if order_date else "N/A"
                expected_date_str = expected_delivery.split(" ")[0] if expected_delivery else "N/A"
                
                # Insert the item with status-specific tag
                item = self.po_tree.insert('', 'end', 
                    text=str(po_id),
                    values=(
                        f"PO-{po_id}",
                        str(supplier_name),
                        order_date_str,
                        expected_date_str,
                        status,
                        f"${total_amount:.2f}" if total_amount else "$0.00"
                    ))
                
                # Apply status-specific styling using tags
                self.po_tree.item(item, tags=(status,))
                
            except Exception as e:
                showerror("Error", f"Error processing purchase order row: {e}")
                continue
                
    def on_po_tree_double_click(self, event):
        """Handle double-click on purchase order tree item"""
        try:
            item = self.po_tree.identify_row(event.y)
            if item:
                po_id = self.po_tree.item(item, 'text')
                if po_id and po_id != 'Error' and po_id != '':
                    self.view_purchase_order(int(po_id))
        except Exception as e:
            showerror("Error",f"Error handling double-click: {e}")

    def on_po_tree_right_click(self, event):
        """Handle right-click on purchase order tree item"""
        try:
            item = self.po_tree.identify_row(event.y)
            if item:
                self.po_tree.selection_set(item)
                po_id = self.po_tree.item(item, 'text')
                status = self.po_tree.item(item, 'tags')[0]
                if po_id and po_id != 'Error' and po_id != '':
                    self.show_po_context_menu(event, int(po_id), status)
        except Exception as e:
            showerror("Error",f"Error handling right-click: {e}")

    def show_po_context_menu(self, event, po_id, status):
        """Show context menu on right-click for purchase orders"""
        context_menu = Menu(self.po_tree, tearoff=0, bg='#2b2b2b', fg='white', 
                            activebackground='#1f538d', activeforeground='white')
        
        context_menu.add_command(label="View Details", 
                            command=lambda: self.view_purchase_order(po_id))
        context_menu.add_command(label="Edit", 
                            command=lambda: self.edit_purchase_order(po_id))
        
        # Only show delete for pending orders
        if status == "Pending":
            context_menu.add_command(label="Delete", 
                                command=lambda: self.delete_purchase_order(po_id))
        else:
            context_menu.add_command(label="Delete (disabled)", 
                                state="disabled")
        
        context_menu.add_separator()
        context_menu.add_command(label="Cancel", command=context_menu.destroy)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def create_purchase_order(self):
        """Create a new purchase order"""
        # Check if there are suppliers
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        if cursor.fetchone()[0] == 0:
            showerror("Error", "You need to add suppliers before creating purchase orders")
            return
        
        # Create purchase order window
        po_window = CTkToplevel(self.root)
        po_window.title("Create Purchase Order")
        po_window.geometry("800x700")
        po_window.grab_set()  # Make window modal
        
        CTkLabel(po_window, text="Create Purchase Order", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Main content with two columns
        content_frame = CTkFrame(po_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - PO details
        left_frame = CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        CTkLabel(left_frame, text="Purchase Order Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        # Get suppliers for dropdown
        cursor.execute("SELECT id, name FROM suppliers ORDER BY name")
        suppliers = [(row[0], row[1]) for row in cursor.fetchall()]
        supplier_names = [name for _, name in suppliers]
        
        # Supplier selection
        supplier_frame = CTkFrame(left_frame)
        supplier_frame.pack(fill="x", pady=5)
        CTkLabel(supplier_frame, text="Supplier:").pack(side="left", padx=5)
        supplier_var = StringVar()
        supplier_dropdown = CTkComboBox(supplier_frame, variable=supplier_var, values=supplier_names)
        supplier_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Order date
        order_date_frame = CTkFrame(left_frame)
        order_date_frame.pack(fill="x", pady=5)
        CTkLabel(order_date_frame, text="Order Date:").pack(side="left", padx=5)
        order_date_entry = CTkEntry(order_date_frame)
        order_date_entry.pack(side="left", padx=5, fill="x", expand=True)
        order_date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))
        
        # Expected delivery
        delivery_frame = CTkFrame(left_frame)
        delivery_frame.pack(fill="x", pady=5)
        CTkLabel(delivery_frame, text="Expected Delivery:").pack(side="left", padx=5)
        delivery_entry = CTkEntry(delivery_frame)
        delivery_entry.pack(side="left", padx=5, fill="x", expand=True)
        delivery_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime("%d-%m-%Y"))
        
        # Status
        status_frame = CTkFrame(left_frame)
        status_frame.pack(fill="x", pady=5)
        CTkLabel(status_frame, text="Status:").pack(side="left", padx=5)
        status_var = StringVar(value="Pending")
        status_dropdown = CTkComboBox(status_frame, variable=status_var, 
                                         values=["Pending", "Ordered", "Received", "Cancelled"])
        status_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Notes
        notes_frame = CTkFrame(left_frame)
        notes_frame.pack(fill="x", pady=5)
        CTkLabel(notes_frame, text="Notes:").pack(side="left", padx=5, anchor="n")
        notes_text = CTkTextbox(notes_frame, height=100)
        notes_text.pack(side="left", padx=5, fill="both", expand=True)
        notes_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        notes_text.configure(font=("Arial", 16))  # Right-align for RTL
        
        # Right side - Order items
        right_frame = CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        CTkLabel(right_frame, text="Order Items", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        # Product selection
        self.product_frame = CTkFrame(right_frame)
        self.product_frame.pack(fill="x", pady=5)
        
        # Get products for dropdown
        cursor.execute('''
            SELECT p.id, p.name, p.brand, p.model, i.price, i.cost
            FROM products p
            JOIN inventory i ON p.id = i.product_id
            ORDER BY p.name
        ''')
        self.products = cursor.fetchall()
        
        CTkLabel(self.product_frame, text="Product:").pack(side="left", padx=5)
        self.product_var = StringVar()
        product_dropdown = AutocompleteCombobox(
            self.product_frame, 
            completevalues=[f"{p[1]} ({p[2]} {p[3]})" for p in self.products],
            textvariable=self.product_var
        )
        product_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Quantity and unit cost
        quantity_frame = CTkFrame(right_frame)
        quantity_frame.pack(fill="x", pady=5)
        CTkLabel(quantity_frame, text="Quantity:").pack(side="left", padx=5)
        self.quantity_entry = CTkEntry(quantity_frame)
        self.quantity_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.quantity_entry.insert(0, "1")
        
        cost_frame = CTkFrame(right_frame)
        cost_frame.pack(fill="x", pady=5)
        CTkLabel(cost_frame, text="Unit Cost:").pack(side="left", padx=5)
        self.cost_entry = CTkEntry(cost_frame)
        self.cost_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Update cost when product is selected
        def update_cost(event=None):
            selected = self.product_var.get()
            if selected:
                for p in self.products:
                    if f"{p[1]} ({p[2]} {p[3]})" == selected:
                        self.cost_entry.delete(0, END)
                        self.cost_entry.insert(0, f"{p[5] or p[4]*0.8:.2f}")  # Default to 80% of price if cost not set
                        break
        
        product_dropdown.bind("<<ComboboxSelected>>", update_cost)
        
        # Add item button
        add_button = CTkButton(right_frame, text="Add Item", command=self.add_po_item)
        add_button.pack(pady=10)
        
        # Items table
        items_header = CTkFrame(right_frame)
        items_header.pack(fill="x", pady=(10,5))
        headers = ["Product", "Qty", "Unit Cost", "Total", ""]
        for i, text in enumerate(headers):
            CTkLabel(items_header, text=text, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        self.po_items_frame = CTkScrollableFrame(right_frame)
        self.po_items_frame.pack(fill="both", expand=True)
        
        # Summary
        summary_frame = CTkFrame(right_frame)
        summary_frame.pack(fill="x", pady=10)
        self.total_label = CTkLabel(summary_frame, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(side="right", padx=10)
        
        # Store items data
        self.po_items = []
        
        # Button frame
        button_frame = CTkFrame(po_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_purchase_order():
            try:
                # Validate inputs
                supplier_name = supplier_var.get()
                if not supplier_name:
                    showerror("Error", "Please select a supplier")
                    return
                
                # Find supplier ID
                supplier_id = None
                for s_id, s_name in suppliers:
                    if s_name == supplier_name:
                        supplier_id = s_id
                        break
                
                if not supplier_id:
                    showerror("Error", "Invalid supplier selected")
                    return
                
                order_date = order_date_entry.get()
                try:
                    datetime.strptime(order_date, "%d-%m-%Y")
                except ValueError:
                    showerror("Error", "Invalid order date format (YYYY-MM-DD)")
                    return
                
                expected_delivery = delivery_entry.get()
                try:
                    datetime.strptime(expected_delivery, "%d-%m-%Y")
                except ValueError:
                    showerror("Error", "Invalid delivery date format (YYYY-MM-DD)")
                    return
                
                status = status_var.get()
                notes = notes_text.get("1.0", END).strip()
                
                if not self.po_items:
                    showerror("Error", "Please add at least one item to the order")
                    return
                
                # Calculate total amount
                total_amount = sum(item['total'] for item in self.po_items)
                
                cursor = self.db.conn.cursor()
                
                try:
                    # Insert purchase order
                    cursor.execute('''
                        INSERT INTO purchase_orders (
                            supplier_id, order_date, expected_delivery, 
                            status, total_amount, notes
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        supplier_id, order_date, expected_delivery,
                        status, total_amount, notes
                    ))
                    po_id = cursor.lastrowid
                    
                    # Insert order items
                    for item in self.po_items:
                        cursor.execute('''
                            INSERT INTO po_items (
                                po_id, product_id, quantity, unit_cost
                            ) VALUES (?, ?, ?, ?)
                        ''', (
                            po_id, item['product_id'], item['quantity'], item['unit_cost']
                        ))
                    
                    self.db.conn.commit()
                    showinfo("Success", f"Purchase order #{po_id} created successfully")
                    po_window.destroy()
                    self.refresh_po_table()
                    
                except Exception as e:
                    self.db.conn.rollback()
                    raise e
                
            except Exception as e:
                showerror("Error", f"Failed to create purchase order: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                     command=po_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Order", width=150, 
                     command=save_purchase_order).pack(side="right", padx=10)

    def add_po_item(self):
        """Add an item to the purchase order"""
        try:
            selected_product = self.product_var.get()
            if not selected_product:
                showerror("Error", "Please select a product")
                return
                
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                showerror("Error", "Quantity must be positive")
                return
                
            unit_cost = float(self.cost_entry.get())
            if unit_cost <= 0:
                showerror("Error", "Unit cost must be positive")
                return
                
            # Find product in products list
            product_id = None
            product_name = ""
            for p in self.products:
                if f"{p[1]} ({p[2]} {p[3]})" == selected_product:
                    product_id = p[0]
                    product_name = p[1]
                    break
                    
            if not product_id:
                showerror("Error", "Invalid product selected")
                return
                
            # Check if product already in order
            for item in self.po_items:
                if item['product_id'] == product_id:
                    showerror("Error", "This product is already in the order")
                    return
                    
            # Add to items list
            total = quantity * unit_cost
            self.po_items.append({
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'unit_cost': unit_cost,
                'total': total
            })
            
            # Add to items table
            self.refresh_po_items_table()
            
            # Clear selection
            self.product_var.set("")
            self.quantity_entry.delete(0, END)
            self.quantity_entry.insert(0, "1")
            self.cost_entry.delete(0, END)
            
        except ValueError:
            showerror("Error", "Please enter valid numbers for quantity and cost")
    
    def refresh_po_items_table(self):
        """Refresh the PO items table display"""
        # Clear existing items
        for widget in self.po_items_frame.winfo_children():
            widget.destroy()
            
        # Add items
        for idx, item in enumerate(self.po_items):
            row = CTkFrame(self.po_items_frame)
            row.pack(fill="x", pady=2)
            
            CTkLabel(row, text=item['product_name']).grid(row=0, column=0, padx=5, sticky="w")
            CTkLabel(row, text=str(item['quantity'])).grid(row=0, column=1, padx=5, sticky="w")
            CTkLabel(row, text=f"${item['unit_cost']:.2f}").grid(row=0, column=2, padx=5, sticky="w")
            CTkLabel(row, text=f"${item['total']:.2f}").grid(row=0, column=3, padx=5, sticky="w")
            
            # Remove button
            remove_btn = CTkButton(row, text="Remove", width=80, fg_color="#e74c3c", hover_color="#c0392b",
                                     command=lambda i=idx: self.remove_po_item(i))
            remove_btn.grid(row=0, column=4, padx=5, sticky="e")
            
        # Update total
        total = sum(item['total'] for item in self.po_items)
        self.total_label.configure(text=f"Total: ${total:.2f}")
    
    def remove_po_item(self, index):
        """Remove an item from the purchase order"""
        if 0 <= index < len(self.po_items):
            self.po_items.pop(index)
            self.refresh_po_items_table()
    
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

    def view_purchase_order(self, po_id):
        """View details of a purchase order using CTk widgets"""
        view_window = CTkToplevel(self.root)
        view_window.title(f"Purchase Order #{po_id}")
        view_window.geometry("800x600")
        view_window.grab_set()
        
        # Create style for the Treeview
        style = Style()
        style.theme_use('clam')
        
        # Header
        header_frame = CTkFrame(view_window)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(header_frame, 
                text=f"Purchase Order #{po_id}", 
                font=("Arial", 18, "bold")).pack(side="left")
        
        # Status colors
        status_colors = {
            "Pending": "#f39c12",  # orange
            "Ordered": "#3498db",  # blue
            "Received": "#2ecc71",  # green
            "Cancelled": "#e74c3c"  # red
        }
        
        # Get PO data
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT po.id, s.name, po.order_date, po.expected_delivery, 
                po.status, po.total_amount, po.notes
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.id = ?
        ''', (po_id,))
        po_data = cursor.fetchone()
        
        if not po_data:
            showerror("Error", "Purchase order not found")
            view_window.destroy()
            return
            
        po_id, supplier_name, order_date, expected_delivery, status, total_amount, notes = po_data
        
        # Status label with color
        status_label = CTkLabel(header_frame, 
                            text=status, 
                            font=("Arial", 14),
                            fg_color=status_colors.get(status, "#2b2b2b"),
                            corner_radius=5)
        status_label.pack(side="right", padx=10)
        
        # Details frame
        details_frame = CTkFrame(view_window)
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Supplier info
        supplier_frame = CTkFrame(details_frame)
        supplier_frame.pack(fill="x", pady=5)
        CTkLabel(supplier_frame, 
                text="Supplier:", 
                font=("Arial", 12, "bold")).pack(side="left", padx=5)
        CTkLabel(supplier_frame, 
                text=supplier_name, 
                font=("Arial", 12)).pack(side="left", padx=5)
        
        # Dates
        dates_frame = CTkFrame(details_frame)
        dates_frame.pack(fill="x", pady=5)
        
        order_date_frame = CTkFrame(dates_frame)
        order_date_frame.pack(side="left", padx=10)
        CTkLabel(order_date_frame, text="Order Date:",bg_color="#333333").pack(anchor="w")
        CTkLabel(order_date_frame, text=order_date, bg_color="#333333").pack(anchor="w")
        
        delivery_frame = CTkFrame(dates_frame)
        delivery_frame.pack(side="left", padx=10)
        CTkLabel(delivery_frame, text="Expected Delivery:", bg_color="#333333").pack(anchor="w")
        CTkLabel(delivery_frame, text=expected_delivery, bg_color="#333333").pack(anchor="w")
        
        # Notes
        if notes:
            notes_frame = CTkFrame(details_frame)
            notes_frame.pack(fill="x", pady=5)
            CTkLabel(notes_frame, text="Notes:").pack(anchor="w")
            
            notes_text = CTkTextbox(notes_frame, height=4, wrap="word")
            notes_text.pack(fill="x", pady=5)
            notes_text.insert("1.0", notes)
            notes_text.configure(state="disabled")
            notes_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
            notes_text.configure(font=("Arial", 16))  # Right-align for RTL
        
        # Items frame
        items_frame = CTkFrame(view_window)
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        CTkLabel(items_frame, text="Order Items").pack(anchor="w", pady=5)
        
        # Items table
        table_frame = CTkFrame(items_frame)
        table_frame.pack(fill="both", expand=True)
        
        # Create Treeview for items
        columns = ("Product", "Quantity", "Unit Cost", "Total")
        items_tree = Treeview(table_frame, columns=columns, show="headings", height=6)
        
        # Configure style for the Treeview
        style.configure("PO.Treeview",
                    background="#2b2b2b",
                    foreground="white",
                    fieldbackground="#2b2b2b",
                    rowheight=25)
        style.configure("PO.Treeview.Heading",
                    background="#1f538d",
                    foreground="white",
                    font=("Arial", 10, "bold"))
        
        items_tree.configure(style="PO.Treeview")
        
        # Configure columns
        for col in columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=150, anchor="center")
        
        # Add scrollbars
        v_scroll = Scrollbar(table_frame, orient="vertical", command=items_tree.yview)
        h_scroll = Scrollbar(table_frame, orient="horizontal", command=items_tree.xview)
        items_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        items_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Get items
        cursor.execute('''
            SELECT p.name, poi.quantity, poi.unit_cost, (poi.quantity * poi.unit_cost) as total
            FROM po_items poi
            JOIN products p ON poi.product_id = p.id
            WHERE poi.po_id = ?
            ORDER BY p.name
        ''', (po_id,))
        
        # Add items to Treeview
        for name, qty, unit_cost, total in cursor.fetchall():
            items_tree.insert("", "end", values=(
                name,
                qty,
                f"${unit_cost:.2f}",
                f"${total:.2f}"
            ))
        
        # Footer with total
        footer_frame = CTkFrame(items_frame)
        footer_frame.pack(fill="x", pady=10)
        
        CTkLabel(footer_frame, text="Total:").pack(side="left", padx=10)
        CTkLabel(footer_frame, text=f"${total_amount:.2f}").pack(side="right", padx=10)
        
        # Button frame
        button_frame = CTkFrame(view_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        CTkButton(button_frame, text="Close", 
                command=view_window.destroy).pack(side="right", padx=10)
        
        # Configure window background
        view_window.configure(bg="#2b2b2b")

    def edit_purchase_order(self, po_id):
        """Edit an existing purchase order"""
        # Check if PO exists and is editable
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT status FROM purchase_orders WHERE id = ?", (po_id,))
        row = cursor.fetchone()
        
        if not row:
            showerror("Error", "Purchase order not found")
            return
            
        status = row[0]
        if status != "Pending":
            showerror("Error", "Only pending orders can be edited")
            return
            
        # Create edit window (similar to create window but with existing data)
        edit_window = CTkToplevel(self.root)
        edit_window.title(f"Edit Purchase Order #{po_id}")
        edit_window.geometry("800x700")
        edit_window.grab_set()
        
        CTkLabel(edit_window, text=f"Edit Purchase Order #{po_id}", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Get PO data
        cursor.execute('''
            SELECT po.supplier_id, s.name, po.order_date, po.expected_delivery, 
                   po.status, po.total_amount, po.notes
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.id = ?
        ''', (po_id,))
        po_data = cursor.fetchone()
        
        if not po_data:
            showerror("Error", "Purchase order not found")
            edit_window.destroy()
            return
            
        supplier_id, supplier_name, order_date, expected_delivery, status, total_amount, notes = po_data
        
        # Get suppliers for dropdown
        cursor.execute("SELECT id, name FROM suppliers ORDER BY name")
        suppliers = [(row[0], row[1]) for row in cursor.fetchall()]
        supplier_names = [name for _, name in suppliers]
        
        # Get PO items
        cursor.execute('''
            SELECT poi.id, poi.product_id, p.name, p.brand, p.model, 
                   poi.quantity, poi.unit_cost, (poi.quantity * poi.unit_cost) as total
            FROM po_items poi
            JOIN products p ON poi.product_id = p.id
            WHERE poi.po_id = ?
            ORDER BY p.name
        ''', (po_id,))
        po_items = cursor.fetchall()
        
        # Main content with two columns
        content_frame = CTkFrame(edit_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - PO details
        left_frame = CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        CTkLabel(left_frame, text="Purchase Order Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        # Supplier selection
        supplier_frame = CTkFrame(left_frame)
        supplier_frame.pack(fill="x", pady=5)
        CTkLabel(supplier_frame, text="Supplier:").pack(side="left", padx=5)
        supplier_var = StringVar(value=supplier_name)
        supplier_dropdown = CTkComboBox(supplier_frame, variable=supplier_var, values=supplier_names)
        supplier_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Order date
        order_date_frame = CTkFrame(left_frame)
        order_date_frame.pack(fill="x", pady=5)
        CTkLabel(order_date_frame, text="Order Date:").pack(side="left", padx=5)
        order_date_entry = CTkEntry(order_date_frame)
        order_date_entry.pack(side="left", padx=5, fill="x", expand=True)
        order_date_entry.insert(0, order_date)
        
        # Expected delivery
        delivery_frame = CTkFrame(left_frame)
        delivery_frame.pack(fill="x", pady=5)
        CTkLabel(delivery_frame, text="Expected Delivery:").pack(side="left", padx=5)
        delivery_entry = CTkEntry(delivery_frame)
        delivery_entry.pack(side="left", padx=5, fill="x", expand=True)
        delivery_entry.insert(0, expected_delivery)
        
        # Status
        status_frame = CTkFrame(left_frame)
        status_frame.pack(fill="x", pady=5)
        CTkLabel(status_frame, text="Status:").pack(side="left", padx=5)
        status_var = StringVar(value=status)
        status_dropdown = CTkComboBox(status_frame, variable=status_var, 
                                         values=["Pending", "Ordered", "Received", "Cancelled"])
        status_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Notes
        notes_frame = CTkFrame(left_frame)
        notes_frame.pack(fill="x", pady=5)
        CTkLabel(notes_frame, text="Notes:").pack(side="left", padx=5, anchor="n")
        notes_text = CTkTextbox(notes_frame, height=100)
        notes_text.pack(side="left", padx=5, fill="both", expand=True)
        notes_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        notes_text.configure(font=("Arial", 16))  # Right-align for RTL
        if notes:
            notes_text.insert("1.0", notes)
        
        # Right side - Order items
        right_frame = CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        CTkLabel(right_frame, text="Order Items", font=("Arial", 14, "bold")).pack(anchor="w", pady=10)
        
        # Product selection
        self.product_frame = CTkFrame(right_frame)
        self.product_frame.pack(fill="x", pady=5)
        
        # Get products for dropdown
        cursor.execute('''
            SELECT p.id, p.name, p.brand, p.model, i.price, i.cost
            FROM products p
            JOIN inventory i ON p.id = i.product_id
            ORDER BY p.name
        ''')
        self.products = cursor.fetchall()
        
        CTkLabel(self.product_frame, text="Product:").pack(side="left", padx=5)
        self.product_var = StringVar()
        product_dropdown = AutocompleteCombobox(
            self.product_frame, 
            completevalues=[f"{p[1]} ({p[2]} {p[3]})" for p in self.products],
            textvariable=self.product_var
        )
        product_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Quantity and unit cost
        quantity_frame = CTkFrame(right_frame)
        quantity_frame.pack(fill="x", pady=5)
        CTkLabel(quantity_frame, text="Quantity:").pack(side="left", padx=5)
        self.quantity_entry = CTkEntry(quantity_frame)
        self.quantity_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.quantity_entry.insert(0, "1")
        
        cost_frame = CTkFrame(right_frame)
        cost_frame.pack(fill="x", pady=5)
        CTkLabel(cost_frame, text="Unit Cost:").pack(side="left", padx=5)
        self.cost_entry = CTkEntry(cost_frame)
        self.cost_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Update cost when product is selected
        def update_cost(event=None):
            selected = self.product_var.get()
            if selected:
                for p in self.products:
                    if f"{p[1]} ({p[2]} {p[3]})" == selected:
                        self.cost_entry.delete(0, END)
                        self.cost_entry.insert(0, f"{p[5] or p[4]*0.8:.2f}")  # Default to 80% of price if cost not set
                        break
        
        product_dropdown.bind("<<ComboboxSelected>>", update_cost)
        
        # Add item button
        add_button = CTkButton(right_frame, text="Add Item", command=lambda: self.add_po_item_edit(
            self.product_var, self.quantity_entry, self.cost_entry, self.products, edit_window))
        add_button.pack(pady=10)
        
        # Items table
        items_header = CTkFrame(right_frame)
        items_header.pack(fill="x", pady=(10,5))
        headers = ["Product", "Qty", "Unit Cost", "Total", ""]
        for i, text in enumerate(headers):
            CTkLabel(items_header, text=text, font=("Arial", 12, "bold")).grid(row=0, column=i, padx=5, pady=5, sticky="w")
        
        self.po_items_edit_frame = CTkScrollableFrame(right_frame)
        self.po_items_edit_frame.pack(fill="both", expand=True)
        
        # Summary
        summary_frame = CTkFrame(right_frame)
        summary_frame.pack(fill="x", pady=10)
        self.total_edit_label = CTkLabel(summary_frame, text=f"Total: ${total_amount:.2f}", font=("Arial", 14, "bold"))
        self.total_edit_label.pack(side="right", padx=10)
        
        # Store items data
        self.po_items_edit = []
        for item in po_items:
            self.po_items_edit.append({
                'id': item[0],
                'product_id': item[1],
                'product_name': item[2],
                'quantity': item[5],
                'unit_cost': item[6],
                'total': item[7]
            })
        
        # Refresh items table
        self.refresh_po_items_edit_table()
        
        # Button frame
        button_frame = CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            try:
                # Validate inputs
                supplier_name = supplier_var.get()
                if not supplier_name:
                    showerror("Error", "Please select a supplier")
                    return
                
                # Find supplier ID
                new_supplier_id = None
                for s_id, s_name in suppliers:
                    if s_name == supplier_name:
                        new_supplier_id = s_id
                        break
                
                if not new_supplier_id:
                    showerror("Error", "Invalid supplier selected")
                    return
                
                new_order_date = order_date_entry.get()
                try:
                    datetime.strptime(new_order_date, "%d-%m-%Y")
                except ValueError:
                    showerror("Error", "Invalid order date format (YYYY-MM-DD)")
                    return
                
                new_expected_delivery = delivery_entry.get()
                try:
                    datetime.strptime(new_expected_delivery, "%d-%m-%Y") 
                except ValueError:
                    showerror("Error", "Invalid delivery date format (YYYY-MM-DD)")
                    return
                
                new_status = status_var.get()
                new_notes = notes_text.get("1.0", END).strip()
                
                if not self.po_items_edit:
                    showerror("Error", "Please add at least one item to the order")
                    return
                
                # Calculate total amount
                new_total_amount = sum(item['total'] for item in self.po_items_edit)
                cursor = self.db.conn.cursor()
                
                try:
                    # Update purchase order
                    cursor.execute('''
                        UPDATE purchase_orders
                        SET supplier_id = ?, order_date = ?, expected_delivery = ?, 
                            status = ?, total_amount = ?, notes = ?
                        WHERE id = ?
                    ''', (
                        new_supplier_id, new_order_date, new_expected_delivery,
                        new_status, new_total_amount, new_notes, po_id
                    ))
                    
                    # Delete existing items
                    cursor.execute("DELETE FROM po_items WHERE po_id = ?", (po_id,))
                    
                    # Insert updated items
                    for item in self.po_items_edit:
                        cursor.execute('''
                            INSERT INTO po_items (
                                po_id, product_id, quantity, unit_cost
                            ) VALUES (?, ?, ?, ?)
                        ''', (
                            po_id, item['product_id'], item['quantity'], item['unit_cost']
                        ))
                    
                    self.db.conn.commit()
                    showinfo("Success", f"Purchase order #{po_id} updated successfully")
                    edit_window.destroy()
                    self.refresh_po_table()
                    
                except Exception as e:
                    self.db.conn.rollback()
                    raise e
                
            except Exception as e:
                showerror("Error", f"Failed to update purchase order: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                     command=edit_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Changes", width=150, 
                     command=save_changes).pack(side="right", padx=10)
    
    def add_po_item_edit(self, product_var, quantity_entry, cost_entry, products, window):
        """Add an item to the purchase order during editing"""
        try:
            selected_product = product_var.get()
            if not selected_product:
                showerror("Error", "Please select a product")
                return
                
            quantity = int(quantity_entry.get())
            if quantity <= 0:
                showerror("Error", "Quantity must be positive")
                return
                
            unit_cost = float(self.cost_entry.get())
            if unit_cost <= 0:
                showerror("Error", "Unit cost must be positive")
                return
                
            # Find product in products list
            product_id = None
            product_name = ""
            for p in products:
                if f"{p[1]} ({p[2]} {p[3]})" == selected_product:
                    product_id = p[0]
                    product_name = p[1]
                    break
                    
            if not product_id:
                showerror("Error", "Invalid product selected")
                return
                
            # Check if product already in order
            for item in self.po_items_edit:
                if item['product_id'] == product_id:
                    showerror("Error", "This product is already in the order")
                    return
                    
            # Add to items list
            total = quantity * unit_cost
            self.po_items_edit.append({
                'product_id': product_id,
                'product_name': product_name,
                'quantity': quantity,
                'unit_cost': unit_cost,
                'total': total
            })
            
            # Add to items table
            self.refresh_po_items_edit_table()
            
            # Clear selection
            self.product_var.set("")
            self.quantity_entry.delete(0, END)
            self.quantity_entry.insert(0, "1")
            self.cost_entry.delete(0, END)
            
            # Update window to ensure proper display
            window.update()
            
        except ValueError:
            showerror("Error", "Please enter valid numbers for quantity and cost")
    
    def refresh_po_items_edit_table(self):
        """Refresh the PO items table display during editing"""
        # Clear existing items
        for widget in self.po_items_edit_frame.winfo_children():
            widget.destroy()
            
        # Add items
        for idx, item in enumerate(self.po_items_edit):
            row = CTkFrame(self.po_items_edit_frame)
            row.pack(fill="x", pady=2)
            
            CTkLabel(row, text=item['product_name']).grid(row=0, column=0, padx=5, sticky="w")
            CTkLabel(row, text=str(item['quantity'])).grid(row=0, column=1, padx=5, sticky="w")
            CTkLabel(row, text=f"${item['unit_cost']:.2f}").grid(row=0, column=2, padx=5, sticky="w")
            CTkLabel(row, text=f"${item['total']:.2f}").grid(row=0, column=3, padx=5, sticky="w")
            
            # Remove button
            remove_btn = CTkButton(row, text="Remove", width=80, fg_color="#e74c3c", hover_color="#c0392b",
                                     command=lambda i=idx: self.remove_po_item_edit(i))
            remove_btn.grid(row=0, column=4, padx=5, sticky="e")
            
        # Update total
        total = sum(item['total'] for item in self.po_items_edit)
        self.total_edit_label.configure(text=f"Total: ${total:.2f}")
    
    def remove_po_item_edit(self, index):
        """Remove an item from the purchase order during editing"""
        if 0 <= index < len(self.po_items_edit):
            self.po_items_edit.pop(index)
            self.refresh_po_items_edit_table()
    
    def delete_purchase_order(self, po_id):
        """Delete a purchase order after confirmation"""
        # Get PO details for confirmation
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT po.id, s.name, po.order_date, po.total_amount
            FROM purchase_orders po
            JOIN suppliers s ON po.supplier_id = s.id
            WHERE po.id = ?
        ''', (po_id,))
        po_data = cursor.fetchone()
        
        if not po_data:
            showerror("Error", "Purchase order not found")
            return
            
        po_id, supplier_name, order_date, total_amount = po_data
        
        # Confirm deletion
        if askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete purchase order #{po_id} from {supplier_name} ({order_date})?"):
            try:
                # Begin transaction
                cursor = self.db.conn.cursor()
                
                # Delete PO items first
                cursor.execute("DELETE FROM po_items WHERE po_id = ?", (po_id,))
                
                # Then delete the PO
                cursor.execute("DELETE FROM purchase_orders WHERE id = ?", (po_id,))
                
                self.db.conn.commit()
                showinfo("Success", f"Purchase order #{po_id} deleted successfully")
                
                # Refresh PO list
                self.refresh_po_table()
                
            except Exception as e:
                self.db.conn.rollback()
                showerror("Error", f"Failed to delete purchase order: {str(e)}")

    def export_purchase_orders(self):
        """Export the filtered purchase orders to a CSV file with products"""
        try:
            # Get current filters from the UI
            status_filter = self.status_filter.get()
            date_filter = self.date_filter.get()
            
            # Get the filtered data that's currently displayed in the table
            orders = self.db.refresh_purchase_table(status_filter, date_filter)
            
            if not orders:
                showerror("Error", "No data to export with current filters")
                return
                
            # Ask user for save location
            filename = asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Save Purchase Orders As"
            )
            
            if not filename:  # User cancelled
                return
                
            # Write to CSV with proper encoding for Arabic
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write UTF-8 BOM header for Excel compatibility
                csvfile.write('\ufeff')
                
                # Write header with product details
                writer.writerow([
                    "PO Number", "Supplier", "Order Date", "Expected Delivery",
                    "Status", "Total Amount", "Notes",  # Notes column included
                    "Product Name", "Quantity", "Unit Cost", "Product Total"
                ])
                
                # Get database cursor
                cursor = self.db.conn.cursor()
                
                # Write data
                for order in orders:
                    # First ensure we're getting all 7 fields including notes
                    if len(order) == 6:  # If notes aren't included in the query result
                        po_id, supplier_name, order_date, expected_delivery, status, total_amount = order
                        notes = ""  # Default empty if notes not available
                    else:  # If notes are included (7 fields)
                        po_id, supplier_name, order_date, expected_delivery, status, total_amount, notes = order
                    
                    # Get products for this PO
                    cursor.execute('''
                        SELECT p.name, poi.quantity, poi.unit_cost, 
                            (poi.quantity * poi.unit_cost) as total
                        FROM po_items poi
                        JOIN products p ON poi.product_id = p.id
                        WHERE poi.po_id = ?
                        ORDER BY p.name
                    ''', (po_id,))
                    products = cursor.fetchall()
                    
                    if products:
                        # Write each product as a separate row
                        for i, (product_name, quantity, unit_cost, product_total) in enumerate(products):
                            if i == 0:  # First product - write PO details
                                writer.writerow([
                                    f"PO-{po_id}",
                                    supplier_name,
                                    order_date.split(" ")[0] if order_date else "N/A",
                                    expected_delivery.split(" ")[0] if expected_delivery else "N/A",
                                    status,
                                    f"${total_amount:.2f}" if total_amount else "$0.00",
                                    notes if notes else "",  # Include notes here
                                    product_name,
                                    quantity,
                                    f"${unit_cost:.2f}",
                                    f"${product_total:.2f}"
                                ])
                            else:  # Additional products - leave PO details empty
                                writer.writerow([
                                    "", "", "", "", "", "", "",
                                    product_name,
                                    quantity,
                                    f"${unit_cost:.2f}",
                                    f"${product_total:.2f}"
                                ])
                    else:  # No products - just write PO info
                        writer.writerow([
                            f"PO-{po_id}",
                            supplier_name,
                            order_date.split(" ")[0] if order_date else "N/A",
                            expected_delivery.split(" ")[0] if expected_delivery else "N/A",
                            status,
                            f"${total_amount:.2f}" if total_amount else "$0.00",
                            notes if notes else "",  # Include notes here
                            "No products", "", "", ""
                        ])
                
            showinfo("Success", f"Filtered purchase orders exported successfully to:\n{filename}")
            
        except Exception as e:
            showerror("Error", f"Failed to export purchase orders: {str(e)}")