from tkinter.messagebox import showerror, showinfo, askyesno
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkEntry
from customtkinter import CTkTextbox, CTkRadioButton, CTkToplevel
from tkinter.ttk import Treeview, Style, Scrollbar
from tkinter import Menu, StringVar, END
from Packages.database import Database
class Categories:
    def __init__(self, root, main_frame):
        self.root = root
        self.main_frame = main_frame
        self.categories = []
        self.db = Database()  # Assuming Database class is defined in Packages.database

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable

    def show_categories(self):
        """Display category management page with Treeview table"""
        self.clear_main_frame()
        
        # Configure main frame grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
        
        # Header frame
        header_frame = CTkFrame(self.main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20,10))
        header_frame.grid_columnconfigure(1, weight=1)  # Middle space expands
        
        CTkLabel(header_frame, text="Category Management", 
                    font=("Arial", 24, "bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        CTkButton(header_frame, text="+ Add Category", 
                    command=self.add_category).grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        # Search and filter frame
        search_frame = CTkFrame(self.main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)  # Left side expands
        
        # Left side - search container
        search_left = CTkFrame(search_frame)
        search_left.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        search_left.grid_columnconfigure(0, weight=1)  # Search entry expands
        
        self.search_entry_cat = CTkEntry(search_left, placeholder_text="Search categories...")
        self.search_entry_cat.grid(row=0, column=0, sticky="ew", padx=5, pady=10)
        self.search_entry_cat.bind("<Return>", lambda e: self.refresh_categories_table())
        
        CTkButton(search_left, text="Search", 
                    command=self.refresh_categories_table).grid(row=0, column=1, padx=5, pady=10)
        
        # Create table container frame
        table_frame = CTkFrame(self.main_frame)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize the table
        self.create_categories_treeview(table_frame)
        
        # Summary frame
        summary_frame = CTkFrame(self.main_frame)
        summary_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        
        try:
            total_categories = len(self.db.show_categories())
            
            # Configure summary frame columns
            summary_frame.grid_columnconfigure(0, weight=1)
            
            CTkLabel(summary_frame, text=f"Total Categories: {total_categories}", 
                        font=("Arial", 12, "bold")).grid(row=0, column=0, padx=20, pady=10)
            
        except Exception as e:
            CTkLabel(summary_frame, text=f"Error loading summary: {str(e)}", 
                        fg_color="red").grid(row=0, column=0, padx=20, pady=10, sticky="ew")

    def create_categories_treeview(self, parent_frame):
        """Create the Treeview table for categories display"""
        
        # Create Treeview with scrollbars
        tree_container = CTkFrame(parent_frame)
        tree_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        tree_container.grid_columnconfigure(0, weight=1)
        tree_container.grid_rowconfigure(0, weight=1)
        
        # Define columns - remove "Actions" since we'll handle it differently
        columns = ("Name", "Description", "Color", "Product Count")
        
        # Create Treeview
        self.categories_tree = Treeview(tree_container, columns=columns, show='tree headings', height=15)
        self.categories_tree.grid(row=0, column=0, sticky="nsew")
        
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
        self.categories_tree.heading('#0', text='ID', anchor='center')
        self.categories_tree.column('#0', width=50, minwidth=50, anchor='center', stretch=False)
        
        column_widths = {
            "Name": 200,
            "Description": 300,
            "Color": 100,
            "Product Count": 100
        }
        
        for col in columns:
            self.categories_tree.heading(col, text=col, anchor='center')
            self.categories_tree.column(col, width=column_widths[col], minwidth=50, anchor='center')
        
        # Add scrollbars
        v_scrollbar = Scrollbar(tree_container, orient="vertical", command=self.categories_tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.categories_tree.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = Scrollbar(tree_container, orient="horizontal", command=self.categories_tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.categories_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind events
        self.categories_tree.bind('<Double-1>', self.on_cat_tree_double_click)
        self.categories_tree.bind('<Button-3>', self.on_cat_tree_right_click)
        
        # Load initial data
        self.refresh_categories_table()

    def refresh_categories_table(self):
        """Update the Treeview with current categories data"""
        if not hasattr(self, 'categories_tree'):
            return
        
        # Clear existing data
        for item in self.categories_tree.get_children():
            self.categories_tree.delete(item)
        
        # Get search term
        search_term = self.search_entry_cat.get().strip() if hasattr(self, 'search_entry_cat') else ""
        
        try:
            # Get categories from database
            categories = self.db.show_categories(search_term)
            
            if not categories:
                self.categories_tree.insert('', 'end', text='', values=('No categories found', '', '', ''))
                return
            
            # Add categories to tree
            for cat_id, name, description, color, product_count in categories:
                try:
                    color_options = {
                                        "#3498db": "Blue",
                                        "#2ecc71": "Green",
                                        "#e74c3c": "Red",
                                        "#f39c12": "Orange",
                                        "#9b59b6": "Purple",
                                        "#1abc9c": "Turquoise",
                                        "#34495e": "Dark Blue",
                                        "#7f8c8d": "Gray"
                                    }
                    # Create a colored square for the color column
                    color_display = color_options[color]
                    
                    # Insert the item
                    item = self.categories_tree.insert('', 'end', 
                        text=str(cat_id),
                        values=(
                            str(name),
                            str(description or ""),
                            color_display,
                            str(product_count)
                        ))
                    
                    # Apply color to the row if available
                    if color:
                        self.categories_tree.tag_configure(f"color_{cat_id}", background=color)
                        self.categories_tree.item(item, tags=(f"color_{cat_id}",))
                    
                except Exception as e:
                    showerror("Error",f"Error processing category row: {e}")
                    continue
        
        except Exception as e:
            showerror("Error",f"Error refreshing categories table: {e}")
            self.categories_tree.insert('', 'end', text='Error', values=(f'Failed to load: {str(e)}', '', '', ''))

    def on_cat_tree_double_click(self, event):
        """Handle double-click on category tree item"""
        try:
            item = self.categories_tree.identify_row(event.y)
            if item:
                cat_id = self.categories_tree.item(item, 'text')
                if cat_id and cat_id != 'Error' and cat_id != '':
                    self.edit_category(int(cat_id))
        except Exception as e:
            showerror("Error",f"Error handling double-click: {e}")

    def on_cat_tree_right_click(self, event):
        """Handle right-click on category tree item"""
        try:
            item = self.categories_tree.identify_row(event.y)
            if item:
                self.categories_tree.selection_set(item)
                cat_id = self.categories_tree.item(item, 'text')
                if cat_id and cat_id != 'Error' and cat_id != '':
                    self.show_cat_context_menu(event, int(cat_id))
        except Exception as e:
            showerror("Error",f"Error handling right-click: {e}")

    def show_cat_context_menu(self, event, cat_id):
        """Show context menu on right-click for categories"""
        context_menu = Menu(self.categories_tree, tearoff=0, bg='#2b2b2b', fg='white', 
                            activebackground='#1f538d', activeforeground='white')
        
        context_menu.add_command(label="Edit Category", command=lambda: self.edit_category(cat_id))
        
        # Only enable delete if product count is 0
        product_count = self.get_product_count_for_category(cat_id)
        if product_count == 0:
            context_menu.add_command(label="Delete Category", 
                                command=lambda: self.delete_category(cat_id, 0))
        else:
            context_menu.add_command(label="Delete Category (disabled)", 
                                state="disabled")
        
        context_menu.add_separator()
        context_menu.add_command(label="Cancel", command=context_menu.destroy)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def get_product_count_for_category(self, cat_id):
        """Helper function to get product count for a category"""
        try:
            categories = self.db.show_categories()
            for category in categories:
                if category[0] == cat_id:
                    return category[4]  # product_count is at index 4
            return 0
        except Exception:
            return 0

    def add_category(self):
        """Open window to add a new category"""
        add_window = CTkToplevel(self.root)
        add_window.title("Add Category")
        add_window.geometry("500x450")
        add_window.grab_set()  # Make window modal
        
        CTkLabel(add_window, text="Add New Category", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Form fields
        form_frame = CTkFrame(add_window)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Name field
        name_frame = CTkFrame(form_frame)
        name_frame.pack(fill="x", pady=5)
        CTkLabel(name_frame, text="Category Name:").pack(side="left", padx=5)
        name_entry = CTkEntry(name_frame)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # Description field
        desc_frame = CTkFrame(form_frame)
        desc_frame.pack(fill="x", pady=5)
        CTkLabel(desc_frame, text="Description:").pack(side="left", padx=5, anchor="n")
        desc_text = CTkTextbox(desc_frame, height=100)
        desc_text.pack(side="left", padx=5, fill="both", expand=True)
        
        # Color picker
        color_frame = CTkFrame(form_frame)
        color_frame.pack(fill="x", pady=5)
        CTkLabel(color_frame, text="Color:").pack(side="left", padx=5)
        
        # Create a simple color selection
        color_var = StringVar(value="#3498db")  # Default blue
        
        color_options = [
            ("#3498db", "Blue"),
            ("#2ecc71", "Green"),
            ("#e74c3c", "Red"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Turquoise"),
            ("#34495e", "Dark Blue"),
            ("#7f8c8d", "Gray")
        ]
        
        color_select_frame = CTkFrame(color_frame)
        color_select_frame.pack(side="left", fill="x", expand=True)
        
        for i, (color_code, color_name) in enumerate(color_options):
            radio_btn = CTkRadioButton(color_select_frame, text=color_name, 
                                        variable=color_var, value=color_code)
            radio_btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="w")
        
        # Button frame
        button_frame = CTkFrame(add_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_category():
            try:
                name = name_entry.get().strip()
                if not name:
                    showerror("Error", "Category name is required")
                    return
                    
                description = desc_text.get("1.0", END).strip()
                color = color_var.get()
                
                cursor = self.db.conn.cursor()
                cursor.execute("INSERT INTO categories (name, description, color) VALUES (?, ?, ?)",
                            (name, description, color))
                self.db.conn.commit()
                
                showinfo("Success", f"Category '{name}' added successfully")
                add_window.destroy()
                
                # Refresh categories display
                self.show_categories()
                
            except sqlite3.IntegrityError:
                showerror("Error", "A category with this name already exists")
            except Exception as e:
                showerror("Error", f"Failed to add category: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", width=100, fg_color="gray", 
                    command=add_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Category", width=150, 
                    command=save_category).pack(side="right", padx=10)
    
    def edit_category(self, category_id):
        """Open window to edit an existing category"""
        edit_window = CTkToplevel(self.root)
        edit_window.title("Edit Category")
        edit_window.geometry("500x450")
        edit_window.grab_set()  # Make window modal
        
        # Get category data
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name, description, color FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        
        if not row:
            showerror("Error", "Category not found")
            edit_window.destroy()
            return
            
        name, description, color = row
        
        CTkLabel(edit_window, text=f"Edit Category: {name}", font=("Arial", 16, "bold")).pack(pady=20)
        
        # Form fields
        form_frame = CTkFrame(edit_window)
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Name field
        name_frame = CTkFrame(form_frame)
        name_frame.pack(fill="x", pady=5)
        CTkLabel(name_frame, text="Category Name:").pack(side="left", padx=5)
        name_entry = CTkEntry(name_frame)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        name_entry.insert(0, name)
        
        # Description field
        desc_frame = CTkFrame(form_frame)
        desc_frame.pack(fill="x", pady=5)
        CTkLabel(desc_frame, text="Description:").pack(side="left", padx=5,  anchor="n")
        desc_text = CTkTextbox(desc_frame, height=100)
        desc_text.pack(side="left", padx=5, fill="both", expand=True)
        if description:
            desc_text.insert("1.0", description)
        
        # Color picker
        color_frame = CTkFrame(form_frame)
        color_frame.pack(fill="x", pady=5)
        CTkLabel(color_frame, text="Color:").pack(side="left", padx=5)
        
        # Create a simple color selection
        color_var = StringVar(value=color or "#3498db")
        
        color_options = [
            ("#3498db", "Blue"),
            ("#2ecc71", "Green"),
            ("#e74c3c", "Red"),
            ("#f39c12", "Orange"),
            ("#9b59b6", "Purple"),
            ("#1abc9c", "Turquoise"),
            ("#34495e", "Dark Blue"),
            ("#7f8c8d", "Gray")
        ]
        
        color_select_frame = CTkFrame(color_frame)
        color_select_frame.pack(side="left", fill="x", expand=True)
        
        for i, (color_code, color_name) in enumerate(color_options):
            radio_btn = CTkRadioButton(color_select_frame, text=color_name, 
                                          variable=color_var, value=color_code)
            radio_btn.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="w")
        
        # Button frame
        button_frame = CTkFrame(edit_window)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def save_changes():
            try:
                new_name = name_entry.get().strip()
                if not new_name:
                    showerror("Error", "Category name is required")
                    return
                    
                new_description = desc_text.get("1.0", END).strip()
                new_color = color_var.get()
                
                cursor = self.db.conn.cursor()
                cursor.execute('''
                    UPDATE categories 
                    SET name = ?, description = ?, color = ?
                    WHERE id = ?
                ''', (new_name, new_description, new_color, category_id))
                self.db.conn.commit()
                
                showinfo("Success", f"Category updated successfully")
                edit_window.destroy()
                
                # Refresh categories display
                self.show_categories()
                
            except sqlite3.IntegrityError:
                showerror("Error", "A category with this name already exists")
            except Exception as e:
                showerror("Error", f"Failed to update category: {str(e)}")
        
        CTkButton(button_frame, text="Cancel", fg_color="gray", 
                     command=edit_window.destroy).pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Changes",
                     command=save_changes).pack(side="right", padx=10)
    
    def delete_category(self, category_id, product_count):
        """Delete a category after confirmation"""
        if product_count > 0:
            showerror("Cannot Delete", 
                                f"This category contains {product_count} products. " +
                                "Reassign the products before deleting.")
            return
            
        # Get category name
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        
        if not row:
            showerror("Error", "Category not found")
            return
            
        category_name = row[0]
        
        # Confirm deletion
        if askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete the category '{category_name}'?"):
            try:
                cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.db.conn.commit()
                showinfo("Success", f"Category '{category_name}' deleted successfully")
                
                # Refresh categories display
                self.show_categories()
                
            except Exception as e:
                showerror("Error", f"Failed to delete category: {str(e)}")