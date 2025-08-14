from customtkinter import CTkLabel, CTkButton, CTkFrame, CTkEntry
from customtkinter import CTkComboBox, CTkToplevel, CTkCheckBox, CTkTextbox
from tkinter import Menu, BooleanVar
from tkinter.ttk import Treeview, Style, Scrollbar
from tkinter.messagebox import showerror, showinfo
from tkinter import END
from datetime import datetime
from Packages.database import Database
from Packages.products import productsManager
class inventoryManager:
    def __init__(self, main_frame, root):
        self.db = Database()
        self.main_frame = main_frame
        self.root = root
        self.products = productsManager(self.root, self.main_frame)
    def show_inventory(self):
        """Display inventory management page with Treeview table"""
        self.clear_main_frame()
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
        
        # Header frame
        header_frame = CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)  # Middle space expands
        
        CTkLabel(header_frame, text="Inventory Management", 
                    font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        CTkButton(header_frame, text="+ Add New Item", 
                   command=self.products.show_add_product).grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Search and filter frame
        search_frame = CTkFrame(self.main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)  # Left side expands
        
        # Left side - search container
        search_left = CTkFrame(search_frame)
        search_left.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_left.grid_columnconfigure(0, weight=1)  # Search entry expands
        
        self.search_entry = CTkEntry(search_left, placeholder_text="Search products...")
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=5, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.refresh_inventory_table())
        
        CTkButton(search_left, text="Search", 
                    command=self.refresh_inventory_table).grid(row=0, column=1, padx=5, pady=10)
        
        # Right side - filters container
        filter_right = CTkFrame(search_frame)
        filter_right.grid(row=0, column=1, sticky="e", pady=10)
        
        # Category filter
        CTkLabel(filter_right, text="Category:").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        
        self.category_filter = CTkComboBox(filter_right, values=["All"] + self.db.get_categories())
        self.category_filter.set("All")
        self.category_filter.grid(row=0, column=1, padx=5, pady=10)
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory_table())
        
        # Sort filter
        CTkLabel(filter_right, text="Sort by:").grid(row=0, column=2, padx=5, pady=10, sticky="e")
        
        self.sort_option = CTkComboBox(filter_right, values=["Name", "Category", "Price", "Quantity"])
        self.sort_option.set("Name")
        self.sort_option.grid(row=0, column=3, padx=5, pady=10)
        self.sort_option.bind("<<ComboboxSelected>>", lambda e: self.refresh_inventory_table())
        
        # Create table container frame
        table_frame = CTkFrame(self.main_frame)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize the table
        self.create_inventory_treeview(table_frame)
        
        # Summary frame
        summary_frame = CTkFrame(self.main_frame)
        summary_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        try:
            total_items, total_quantity, total_value = self.db.show_inventory()
            
            # Configure summary frame columns
            summary_frame.grid_columnconfigure(0, weight=1)
            summary_frame.grid_columnconfigure(1, weight=1) 
            summary_frame.grid_columnconfigure(2, weight=1)
            
            CTkLabel(summary_frame, text=f"Total Items: {total_items}", 
                        font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=10)
            CTkLabel(summary_frame, text=f"Total Quantity: {total_quantity}", 
                        font=("Arial", 12, "bold")).grid(row=0, column=1, padx=20, pady=10)
            CTkLabel(summary_frame, text=f"Total Value: ${total_value:,.2f}", 
                        font=("Arial", 12, "bold")).grid(row=0, column=2, padx=20, pady=10)
            
        except Exception as e:
            CTkLabel(summary_frame, text=f"Error loading summary: {str(e)}", 
                        fg_color="red").grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable


    def create_inventory_treeview(self, parent_frame):
        """Create the Treeview table for inventory display"""
        
        # Create Treeview with scrollbars
        tree_container = CTkFrame(parent_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Define columns
        columns = ("SKU", "Product", "Category", "Quantity", "Price", "Location")
        
        # Create Treeview
        self.inventory_tree = Treeview(tree_container, columns=columns, show='tree headings', height=15)
        self.inventory_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure Treeview style for dark theme
        style = Style()
        style.theme_use('clam')
        
        # Configure colors to match CustomTkinter dark theme
        style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="#ffffff",
                    rowheight=25,
                    fieldbackground="#2b2b2b",
                    bordercolor="#404040",
                    borderwidth=0)
        
        style.configure("Treeview.Heading",
                    background="#1f538d",
                    foreground="#ffffff",
                    font=("Arial", 10, "bold"))
        
        style.map("Treeview",
                background=[('selected', '#1f538d')])
        
        # Configure columns
        self.inventory_tree.heading('#0', text='ID', anchor='center')
        self.inventory_tree.column('#0', width=50, minwidth=50, anchor='center')
        
        column_widths = {
            "SKU": 100,
            "Product": 250,
            "Category": 120,
            "Quantity": 80,
            "Price": 80,
            "Location": 150
        }
        
        for col in columns:
            self.inventory_tree.heading(col, text=col, anchor='center')
            self.inventory_tree.column(col, width=column_widths[col], minwidth=50, anchor='center')
        
        # Add scrollbars
        v_scrollbar = Scrollbar(tree_container, orient="vertical", command=self.inventory_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.inventory_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = Scrollbar(tree_container, orient="horizontal", command=self.inventory_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.inventory_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind double-click event
        self.inventory_tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Bind right-click event for context menu
        self.inventory_tree.bind('<Button-3>', self.on_tree_right_click)
        
        # Load initial data
        self.refresh_inventory_table()

    def refresh_inventory_table(self):
        """Update the Treeview with current data and filters"""
        if not hasattr(self, 'inventory_tree'):
            return
        
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        # Get filter values
        search_term = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""
        category_filter = self.category_filter.get() if hasattr(self, 'category_filter') else "All"
        sort_option = self.sort_option.get() if hasattr(self, 'sort_option') else "Name"

        try:
            # Get filtered products from database
            products = self.db.refresh_inventory(search_term, category_filter, sort_option)
            
            if not products:
                # Show "No data" message
                self.inventory_tree.insert('', 'end', text='', values=('No data found', '', '', '', '', ''))
                return
            
            # Add products to tree
            for product in products:
                try:
                    inventory_id, sku, product_name, category_name, quantity, price, location = product
                    
                    # Format data for display
                    values = (
                        str(sku),
                        str(product_name),
                        str(category_name),
                        str(quantity),
                        f"${price:.2f}",
                        str(location or "Main Storage")
                    )
                    
                    # Insert item
                    item = self.inventory_tree.insert('', 'end', text=str(inventory_id), values=values)
                    
                    # Apply low stock highlighting
                    if quantity <= 5:
                        self.inventory_tree.set(item, 'Quantity', f"{quantity} ⚠️")
                        # Note: Full row highlighting requires more complex styling in ttk
                    
                except Exception as e:
                    showerror("Error", f"Error processing product row: {str(e)}\n{product}")
                    continue
        
        except Exception as e:
            showerror("Error", f"Error refreshing table: {e}")
            # Show error in table
            self.inventory_tree.insert('', 'end', text='Error', values=(f'Failed to load: {str(e)}', '', '', '', '', ''))

    def on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        try:
            item = self.inventory_tree.selection()[0]
            inventory_id = self.inventory_tree.item(item, 'text')
            
            if inventory_id and inventory_id != 'Error' and inventory_id != '':
                self.show_action_dialog(int(inventory_id))
                
        except (IndexError, ValueError) as e:
            showerror("Error", f"Error handling double-click: {e}")

    def on_tree_right_click(self, event):
        """Handle right-click on tree item"""
        try:
            # Select the item under cursor
            item = self.inventory_tree.identify_row(event.y)
            if item:
                self.inventory_tree.selection_set(item)
                inventory_id = self.inventory_tree.item(item, 'text')
                
                if inventory_id and inventory_id != 'Error' and inventory_id != '':
                    self.show_context_menu(event, int(inventory_id))
                    
        except ValueError as e:
            showerror("Error", f"Error handling right-click: {e}")
        except Exception as e:
            showerror("Error", f"Error handling right-click: {e}")  

    def show_context_menu(self, event, inventory_id):
        """Show context menu on right-click"""
        context_menu = Menu(self.inventory_tree, tearoff=0, bg='#2b2b2b', fg='white', 
                            activebackground='#1f538d', activeforeground='white')
        
        context_menu.add_command(label="Edit Item", command=lambda: self.edit_inventory_item(inventory_id))
        context_menu.add_command(label="Sell Item", command=lambda: self.sell_device(inventory_id))
        context_menu.add_separator()
        context_menu.add_command(label="Cancel", command=lambda: context_menu.destroy())
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def edit_inventory_item(self, inventory_id):
        """Open a window to edit an inventory item"""
        edit_window = CTkToplevel(self.root)
        edit_window.title("Edit Inventory Item")
        edit_window.geometry("600x700")
        edit_window.grab_set()  # Make window modal
        
        # Get inventory item data
        row = self.db.get_inventory_item(inventory_id)
        if not row:
            showerror("Error", "Inventory item not found")
            edit_window.destroy()
            return
            
        # Unpack row data - matches the columns returned by get_inventory_item
        (inv_id, sku, product_name, category_name, quantity, 
        price, cost, location, condition, reorder_point) = row
        
        # Product info (non-editable)
        info_frame = CTkFrame(edit_window)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(info_frame, text=f"Editing: {product_name}", 
                font=("Arial", 16, "bold")).pack(anchor="w", pady=(10,5))
        CTkLabel(info_frame, text=f"Category: {category_name}").pack(anchor="w")
        
        # Editable inventory details
        details_frame = CTkFrame(edit_window)
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Add all fields with proper validation
        self.sku_entry = self.add_field(details_frame, "SKU:", sku)
        self.quantity_entry = self.add_field(details_frame, "Quantity:", str(quantity))
        self.price_entry = self.add_field(details_frame, "Price ($):", f"{price:.2f}" if price else "0.00")
        self.cost_entry = self.add_field(details_frame, "Cost ($):", f"{cost:.2f}" if cost else "0.00")
        self.location_entry = self.add_field(details_frame, "Location:", location)
        
        # Condition dropdown
        condition_frame = CTkFrame(details_frame)
        condition_frame.pack(fill="x", pady=5)
        CTkLabel(condition_frame, text="Condition:").pack(side="left", padx=5)
        self.condition_combo = CTkComboBox(
            condition_frame, 
            values=["New", "Like New", "Very Good", "Good", "Fair", "Poor"]
        )
        self.condition_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.condition_combo.set(condition if condition else "New")
        
        self.reorder_entry = self.add_field(details_frame, "Reorder Point:", str(reorder_point))
        
        # Button frame
        button_frame = CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            try:
                # Validate inputs
                new_quantity = int(self.quantity_entry.get())
                new_price = float(self.price_entry.get())
                new_cost = float(self.cost_entry.get())
                new_reorder = int(self.reorder_entry.get())
                
                if any(val < 0 for val in [new_quantity, new_price, new_cost, new_reorder]):
                    showerror("Invalid Input", "Negative values are not allowed")
                    return
                    
                # Update inventory item
                self.db.edit_inventory_item(inv_id,new_quantity,new_price,new_cost,self.sku_entry.get(),self.location_entry.get(),new_reorder,self.condition_combo.get())
                
                showinfo("Success", "Inventory item updated successfully.")
                edit_window.destroy()
                self.refresh_inventory_table()
                
            except ValueError:
                showerror("Input Error", "Please enter valid numbers for quantity, price, cost and reorder point")
            except Exception as e:
                showerror("Error", f"Failed to update inventory: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                command=edit_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Changes", width=150, 
                command=save_changes).pack(side="right", padx=10)

    def add_field(self, parent, label_text, default_value="", placeholder=""):
        """Helper method to create labeled entry fields"""
        frame = CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(frame, text=label_text, width=120).pack(side="left", padx=5)
        entry = CTkEntry(frame, placeholder_text=placeholder)
        if default_value:
            entry.insert(0, str(default_value))
        entry.pack(side="left", padx=5, fill="x", expand=True)
        return entry
    
        
    def show_action_dialog(self, inventory_id):
        """Show dialog with action options"""
        dialog = CTkToplevel(self.main_frame)
        dialog.title("Item Actions")
        dialog.geometry("350x180")
        dialog.transient(self.main_frame)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"350x180+{x}+{y}")
        
        CTkLabel(dialog, text=f"Actions for Item ID: {inventory_id}", 
                    font=("Arial", 16, "bold")).pack(pady=20)
        
        button_frame = CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        CTkButton(button_frame, text="Edit Item", width=100, height=35,
                    command=lambda: [dialog.destroy(), self.edit_inventory_item(inventory_id)]).pack(side="left", padx=10)
        CTkButton(button_frame, text="Sell Item", width=100, height=35,
                    command=lambda: [dialog.destroy(), self.sell_device(inventory_id)]).pack(side="left", padx=10)
        CTkButton(button_frame, text="Cancel", width=100, height=35,
                    command=dialog.destroy).pack(side="left", padx=10)

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

    def sell_device(self, inventory_id):
        """Create a window to sell a device from inventory"""
        sell_window = CTkToplevel(self.root)
        sell_window.title("Sell Device")
        sell_window.geometry("500x850")
        sell_window.resizable(False, False)
        sell_window.grab_set()  # Make window modal
        
        row = self.db.sell_product(inventory_id)
        
        if not row:
            showerror("Error", "Inventory item not found.")
            sell_window.destroy()
            return
            
        inv_id, sku, product_name, quantity, price, cost = row
        
        # Calculate profit margin
        profit_margin = ((price - (cost or 0)) / price * 100) if price > 0 and cost else 0
        
        # Header with product info
        header_frame = CTkFrame(sell_window)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(header_frame, text=f"Selling: {product_name}", 
                    font=("Arial", 16, "bold")).pack(anchor="w", pady=(10,5))
        CTkLabel(header_frame, text=f"SKU: {sku}").pack(anchor="w")
        CTkLabel(header_frame, text=f"Available Quantity: {quantity}").pack(anchor="w", pady=5)
        CTkLabel(header_frame, text=f"Unit Price: ${price:.2f}").pack(anchor="w")
        CTkLabel(header_frame, text=f"Profit Margin: {profit_margin:.1f}%").pack(anchor="w")
        
        # Transaction details
        details_frame = CTkFrame(sell_window)
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Sale details
        CTkLabel(details_frame, text="Sale Details", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10,5))
        
        # Quantity input
        quantity_frame = CTkFrame(details_frame)
        quantity_frame.pack(fill="x", pady=5)
        CTkLabel(quantity_frame, text="Quantity:").pack(side="left", padx=5)
        self.quantity_entry = CTkEntry(quantity_frame)
        self.quantity_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.quantity_entry.insert(0, "1")
        
        # Custom price option
        price_frame = CTkFrame(details_frame)
        price_frame.pack(fill="x", pady=5)
        price_var = BooleanVar(value=False)
        price_check = CTkCheckBox(price_frame, text="Custom Price", variable=price_var)
        price_check.pack(side="left", padx=5)
        
        custom_price_entry = CTkEntry(price_frame)
        custom_price_entry.pack(side="left", padx=5, fill="x", expand=True)
        custom_price_entry.insert(0, f"{price:.2f}")
        custom_price_entry.configure(state="disabled")
        
        def toggle_price_entry():
            if price_var.get():
                custom_price_entry.configure(state="normal")
            else:
                custom_price_entry.configure(state="disabled")
                custom_price_entry.delete(0, END)
                custom_price_entry.insert(0, f"{price:.2f}")
                
        price_check.configure(command=toggle_price_entry)
        
        # Sale note
        CTkLabel(details_frame, text="Sale Note:").pack(anchor="w", padx=5, pady=(10,5))
        note_textbox = CTkTextbox(details_frame, height=80)
        note_textbox.pack(fill="x", padx=5, pady=5)
        note_textbox.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        note_textbox.configure(font=("Arial", 16))  # Right-align for RTL
        
        # Customer information
        customer_frame = CTkFrame(sell_window)
        customer_frame.pack(fill="x", padx=20, pady=10)
        
        CTkLabel(customer_frame, text="Customer Information", font=("Arial", 14, "bold")).pack(anchor="w", pady=(10,5))
        
        # Customer name
        name_frame = CTkFrame(customer_frame)
        name_frame.pack(fill="x", pady=5)
        CTkLabel(name_frame, text="Customer Name:").pack(side="left", padx=5)
        customer_name_entry = CTkEntry(name_frame)
        customer_name_entry.pack(side="left", padx=5, fill="x", expand=True)
        customer_name_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        customer_name_entry.configure(font=("Arial", 16))  # Right-align for RTL
        # Customer email
        email_frame = CTkFrame(customer_frame)
        email_frame.pack(fill="x", pady=5)
        CTkLabel(email_frame, text="Customer Email:").pack(side="left", padx=5)
        customer_email_entry = CTkEntry(email_frame)
        customer_email_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Payment method
        payment_frame = CTkFrame(customer_frame)
        payment_frame.pack(fill="x", pady=5)
        CTkLabel(payment_frame, text="Payment Method:").pack(side="left", padx=5)
        payment_method = CTkComboBox(payment_frame, values=["Cash", "Credit Card", "Debit Card", "Bank Transfer", "Check", "Other"])
        payment_method.pack(side="left", padx=5, fill="x", expand=True)
        payment_method.set("Cash")
    
        # Invoice number
        invoice_frame = CTkFrame(customer_frame)
        invoice_frame.pack(fill="x", pady=5)
        CTkLabel(invoice_frame, text="Invoice Number:").pack(side="left", padx=5)
        invoice_entry = CTkEntry(invoice_frame)
        invoice_entry.pack(side="left", padx=5, fill="x", expand=True)
        # Generate a suggested invoice number (current date + random number)
        suggested_invoice = f"INV-{datetime.now().strftime('%d-%m-%Y')}-{inventory_id}"
        invoice_entry.insert(0, suggested_invoice)
        
        # Summary frame
        summary_frame = CTkFrame(sell_window)
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        total_label = CTkLabel(summary_frame, text="Total: $0.00", font=("Arial", 16, "bold"))
        total_label.pack(pady=10)
    
        # Update total when quantity changes
        def update_total(*args):
            try:
                qty = int(self.quantity_entry.get())
                unit_price = float(custom_price_entry.get())
                total = qty * unit_price
                total_label.configure(text=f"Total: ${total:.2f}")
            except ValueError:
                total_label.configure(text="Total: $0.00")
        
        self.quantity_entry.bind("<KeyRelease>", update_total)
        custom_price_entry.bind("<KeyRelease>", update_total)
        
        # Initialize with default values
        update_total()
        
        # Button frame
        button_frame = CTkFrame(sell_window)
        button_frame.pack(fill="x", padx=20, pady=20)
    
        def process_sale():
            try:
                # Validate inputs
                qty = int(self.quantity_entry.get())
                if qty <= 0:
                    showerror("Invalid Quantity", "Please enter a positive quantity.")
                    return
                    
                if qty > quantity:
                    showerror("Insufficient Stock", f"Only {quantity} items available in stock.")
                    return
                    
                sale_price = float(custom_price_entry.get())
                if sale_price < 0:
                    showerror("Invalid Price", "Price cannot be negative.")
                    return
                    
                # Get other inputs
                description = note_textbox.get("1.0", END).strip()
                customer_name = customer_name_entry.get().strip()
                customer_email = customer_email_entry.get().strip()
                payment = payment_method.get()
                invoice = invoice_entry.get().strip()
                
                self.db.process_sale(inventory_id, qty, sale_price, description, customer_name, customer_email, payment, invoice)
                showinfo("Success", f"Sale completed successfully. Invoice: {invoice}")
                sell_window.destroy()
                
                # Refresh inventory display
                self.refresh_inventory_table()
                
            except ValueError as e:
                showerror("Input Error", f"Please check your inputs: {str(e)}")
            except Exception as e:
                showerror("Error", f"An error occurred: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                    command=sell_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Complete Sale", width=150, 
                    command=process_sale).pack(side="right", padx=10)