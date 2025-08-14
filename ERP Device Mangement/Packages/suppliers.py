from Packages.database import Database
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry
from customtkinter import CTkScrollableFrame, CTkTextbox, CTkToplevel
from tkinter import Menu, END
from tkinter.messagebox import showerror, showinfo, askyesno
from tkinter.ttk import Treeview, Scrollbar, Style
import unicodedata
class SuppliersManager:
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

    def show_suppliers(self):
        """Display suppliers management page with Treeview table"""
        self.clear_main_frame()
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
        
        # Header frame
        header_frame = CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)  # Middle space expands
        
        CTkLabel(header_frame, text="Supplier Management", 
                    font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        CTkButton(header_frame, text="+ Add Supplier", 
                    command=self.add_supplier).grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Search and filter frame
        search_frame = CTkFrame(self.main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)  # Left side expands
        
        # Left side - search container
        search_left = CTkFrame(search_frame)
        search_left.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_left.grid_columnconfigure(0, weight=1)  # Search entry expands
        
        self.search_entry_supp = CTkEntry(search_left, placeholder_text="Search suppliers...")
        self.search_entry_supp.grid(row=0, column=0, sticky="ew", padx=5, pady=10)
        self.search_entry_supp.bind("<Return>", lambda e: self.refresh_suppliers_table())
        
        CTkButton(search_left, text="Search", 
                    command=self.refresh_suppliers_table).grid(row=0, column=1, padx=5, pady=10)
        
        # Create table container frame
        table_frame = CTkFrame(self.main_frame)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize the table
        self.create_suppliers_treeview(table_frame)
        
        # Summary frame
        summary_frame = CTkFrame(self.main_frame)
        summary_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        try:
            total_suppliers = len(self.db.show_suppliers())
            
            # Configure summary frame columns
            summary_frame.grid_columnconfigure(0, weight=1)
            
            CTkLabel(summary_frame, text=f"Total Suppliers: {total_suppliers}", 
                        font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=10)
            
        except Exception as e:
            CTkLabel(summary_frame, text=f"Error loading summary: {str(e)}", 
                        fg_color="red").grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    def create_suppliers_treeview(self, parent_frame):
        """Create the Treeview table for suppliers display"""
        
        # Create Treeview with scrollbars
        tree_container = CTkFrame(parent_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Define columns
        columns = ("Name", "Contact Person", "Contact Info")
        
        # Create Treeview
        self.suppliers_tree = Treeview(tree_container, columns=columns, show='tree headings', height=15)
        self.suppliers_tree.grid(row=0, column=0, sticky="nsew")
        
        # Configure Treeview style for dark theme
        style = Style()
        style.theme_use('clam')
        
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
        
        style.map("Treeview",
                background=[('selected', '#1f538d')])
        
        # Configure columns
        self.suppliers_tree.heading('#0', text='ID', anchor='center')
        self.suppliers_tree.column('#0', width=50, minwidth=50, anchor='center', stretch=False)
        
        column_widths = {
            "Name": 250,
            "Contact Person": 200,
            "Contact Info": 300
        }
        
        for col in columns:
            self.suppliers_tree.heading(col, text=col, anchor='center')
            self.suppliers_tree.column(col, width=column_widths[col], minwidth=50, anchor='center')  # Left align content
        
        # Add scrollbars
        v_scrollbar = Scrollbar(tree_container, orient="vertical", command=self.suppliers_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.suppliers_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = Scrollbar(tree_container, orient="horizontal", command=self.suppliers_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.suppliers_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.suppliers_tree.bind('<Double-1>', self.on_supplier_tree_double_click)
        self.suppliers_tree.bind('<Button-3>', self.on_supplier_tree_right_click)
        
        # Load initial data
        self.refresh_suppliers_table()

    def refresh_suppliers_table(self):
        """Update the Treeview with current suppliers data"""
        if not hasattr(self, 'suppliers_tree'):
            return
        
        # Clear existing data
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Get search term
        search_term = self.search_entry_supp.get().strip() if hasattr(self, 'search_entry_supp') else ""
        
        try:
            # Get suppliers from database
            suppliers = self.db.show_suppliers(search_term)
            
            if not suppliers:
                self.suppliers_tree.insert('', 'end', text='', values=('No suppliers found', '', ''))
                return
            
            # Add suppliers to tree
            for supplier_id, name, contact_person, email, phone in suppliers:
                try:
                    # Format contact info
                    contact_info = f"{email or ''}"
                    if phone:
                        if email:
                            contact_info += f" | {phone}"
                        else:
                            contact_info = phone
                    
                    # Insert the item
                    item = self.suppliers_tree.insert('', 'end', 
                        text=str(supplier_id),
                        values=(
                            str(name),
                            str(contact_person or ""),
                            contact_info
                        ))
                    
                except Exception as e:
                    showerror("Error",f"Error processing supplier row: {e}")
                    continue
        
        except Exception as e:
            showerror("Error",f"Error refreshing suppliers table: {e}")
            self.suppliers_tree.insert('', 'end', text='Error', values=(f'Failed to load: {str(e)}', '', ''))

    def on_supplier_tree_double_click(self, event):
        """Handle double-click on supplier tree item"""
        try:
            item = self.suppliers_tree.identify_row(event.y)
            if item:
                supplier_id = self.suppliers_tree.item(item, 'text')
                if supplier_id and supplier_id != 'Error' and supplier_id != '':
                    self.edit_supplier(int(supplier_id))
        except Exception as e:
            showerror("Error",f"Error handling double-click: {e}")

    def on_supplier_tree_right_click(self, event):
        """Handle right-click on supplier tree item"""
        try:
            item = self.suppliers_tree.identify_row(event.y)
            if item:
                self.suppliers_tree.selection_set(item)
                supplier_id = self.suppliers_tree.item(item, 'text')
                if supplier_id and supplier_id != 'Error' and supplier_id != '':
                    self.show_supplier_context_menu(event, int(supplier_id))
        except Exception as e:
            print(f"Error handling right-click: {e}")

    def show_supplier_context_menu(self, event, supplier_id):
        """Show context menu on right-click for suppliers"""
        context_menu = Menu(self.suppliers_tree, tearoff=0, bg='#2b2b2b', fg='white', 
                            activebackground='#1f538d', activeforeground='white')
        
        context_menu.add_command(label="Edit Supplier", 
                            command=lambda: self.edit_supplier(supplier_id))
        context_menu.add_command(label="Delete Supplier", 
                            command=lambda: self.delete_supplier(supplier_id))
        context_menu.add_separator()
        context_menu.add_command(label="Cancel", command=context_menu.destroy)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
      
    def add_field(self, parent, label_text, placeholder=""):
        frame = CTkFrame(parent)
        frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(frame, text=label_text, width=120).pack(side="left", padx=5)
        entry = CTkEntry(frame, placeholder_text=placeholder)
        entry.pack(side="left", padx=5, fill="x", expand=True)
        return entry
        
    def validate_multilingual_input(self, event):
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

    def add_supplier(self):
        """Open window to add a new supplier"""
        add_window = CTkToplevel(self.root)
        add_window.title("Add Supplier")
        add_window.geometry("600x500")
        add_window.grab_set()  # Make window modal
        
        CTkLabel(add_window, text="Add New Supplier", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Form fields
        form_frame = CTkScrollableFrame(add_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add all fields
        name_entry = self.add_field(form_frame, "Company Name:", "Supplier name")
        name_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        name_entry.configure(font=("Arial", 16))  # Right-align for RTL
        contact_entry = self.add_field(form_frame, "Contact Person:", "Name of contact")
        contact_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        contact_entry.configure(font=("Arial", 16))  # Right-align for RTL
        email_entry = self.add_field(form_frame, "Email:", "Email address")
        phone_entry = self.add_field(form_frame, "Phone:", "Phone number")
        address_frame = CTkFrame(form_frame)
        address_frame.pack(fill="x", pady=5)
        CTkLabel(address_frame, text="Address:", width=120).pack(side="left", padx=5, anchor="n")
        address_text = CTkTextbox(address_frame, height=80)
        address_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        address_text.configure(font=("Arial", 16))  # Right-align for RTL
        address_text.pack(side="left", padx=5, fill="both", expand=True)
        website_entry = self.add_field(form_frame, "Website:", "Company website")
        notes_frame = CTkFrame(form_frame)
        notes_frame.pack(fill="x", pady=5)
        CTkLabel(notes_frame, text="Notes:", width=120).pack(side="left", padx=5, anchor="n")
        notes_text = CTkTextbox(notes_frame, height=100)
        notes_text.pack(side="left", padx=5, fill="both", expand=True)
        notes_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        notes_text.configure(font=("Arial", 16))  # Right-align for RTL
        # Button frame
        button_frame = CTkFrame(add_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_supplier():
            try:
                name = name_entry.get().strip()
                if not name:
                    showerror("Error", "Supplier name is required")
                    return
                    
                contact_person = contact_entry.get().strip()
                email = email_entry.get().strip()
                phone = phone_entry.get().strip()
                address = address_text.get("1.0", END).strip()
                website = website_entry.get().strip()
                notes = notes_text.get("1.0", END).strip()
                
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    INSERT INTO suppliers (
                        name, contact_person, email, phone, address, website, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, contact_person, email, phone, address, website, notes))
                self.db.conn.commit()
                
                showinfo("Success", f"Supplier '{name}' added successfully")
                add_window.destroy()
                
                # Refresh suppliers display
                self.show_suppliers()
                
            except Exception as e:
                showerror("Error", f"Failed to add supplier: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                     command=add_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Supplier", width=150, 
                     command=save_supplier).pack(side="right", padx=10)
    
    def edit_supplier(self, supplier_id):
        """Open window to edit an existing supplier"""
        edit_window = CTkToplevel(self.root)
        edit_window.title("Edit Supplier")
        edit_window.geometry("600x500")
        edit_window.grab_set()  # Make window modal
        
        # Get supplier data
        cursor = self.db.conn.cursor()
        cursor.execute('''
            SELECT name, contact_person, email, phone, address, website, notes
            FROM suppliers
            WHERE id = ?
        ''', (supplier_id,))
        row = cursor.fetchone()
        
        if not row:
            showerror("Error", "Supplier not found")
            edit_window.destroy()
            return
            
        name, contact_person, email, phone, address, website, notes = row
        
        CTkLabel(edit_window, text=f"Edit Supplier: {name}", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Form fields
        form_frame = CTkScrollableFrame(edit_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add all fields with existing data
        name_entry = self.add_field(form_frame, "Company Name:", name)
        name_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        name_entry.configure(font=("Arial", 16))  # Right-align for RTL
        contact_entry = self.add_field(form_frame, "Contact Person:", contact_person or "")
        contact_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        contact_entry.configure(font=("Arial", 16))  # Right-align for RTL
        email_entry = self.add_field(form_frame, "Email:", email or "")
        phone_entry = self.add_field(form_frame, "Phone:", phone or "")
        
        address_frame = CTkFrame(form_frame)
        address_frame.pack(fill="x", pady=5)
        CTkLabel(address_frame, text="Address:", width=120).pack(side="left", padx=5, anchor="n")
        address_text = CTkTextbox(address_frame, height=80)
        address_text.pack(side="left", padx=5, fill="both", expand=True)
        address_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        address_text.configure(font=("Arial", 12))  # Right-align for RTL
        if address:
            address_text.insert("1.0", address)
        
        website_entry = self.add_field(form_frame, "Website:", website or "")
        
        notes_frame = CTkFrame(form_frame)
        notes_frame.pack(fill="x", pady=5)
        CTkLabel(notes_frame, text="Notes:", width=120).pack(side="left", padx=5, anchor="n")
        notes_text = CTkTextbox(notes_frame, height=100)
        notes_text.pack(side="left", padx=5, fill="both", expand=True)
        if notes:
            notes_text.insert("1.0", notes)
        
        # Button frame
        button_frame = CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            try:
                new_name = name_entry.get().strip()
                if not new_name:
                    showerror("Error", "Supplier name is required")
                    return
                    
                new_contact = contact_entry.get().strip()
                new_email = email_entry.get().strip()
                new_phone = phone_entry.get().strip()
                new_address = address_text.get("1.0", END).strip()
                new_website = website_entry.get().strip()
                new_notes = notes_text.get("1.0", END).strip()
                
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE suppliers
                    SET name = ?, contact_person = ?, email = ?, phone = ?,
                        address = ?, website = ?, notes = ?
                    WHERE id = ?
                ''', (new_name, new_contact, new_email, new_phone, 
                     new_address, new_website, new_notes, supplier_id))
                self.db.conn.commit()
                
                showinfo("Success", f"Supplier updated successfully")
                edit_window.destroy()
                
                # Refresh suppliers display
                self.show_suppliers()
                
            except Exception as e:
                showerror("Error", f"Failed to update supplier: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                     command=edit_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Changes", width=150, 
                     command=save_changes).pack(side="right", padx=10)
    
    def delete_supplier(self, supplier_id):
        """Delete a supplier after confirmation"""
        # Get supplier name
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        
        if not row:
            showerror("Error", "Supplier not found")
            return
            
        supplier_name = row[0]
        
        # Check if there are any purchase orders for this supplier
        cursor.execute("SELECT COUNT(*) FROM purchase_orders WHERE supplier_id = ?", (supplier_id,))
        order_count = cursor.fetchone()[0]
        
        if order_count > 0:
            if not askyesno("Warning", 
                                      f"This supplier has {order_count} purchase orders. " +
                                      "Deleting it may affect reports and history. Continue?"):
                return
        
        # Confirm deletion
        if askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete the supplier '{supplier_name}'?"):
            try:
                cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
                self.db.conn.commit()
                showinfo("Success", f"Supplier '{supplier_name}' deleted successfully")
                
                # Refresh suppliers display
                self.show_suppliers()
                
            except Exception as e:
                showerror("Error", f"Failed to delete supplier: {str(e)}")