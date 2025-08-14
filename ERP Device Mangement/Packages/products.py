from customtkinter import CTkScrollableFrame, CTkInputDialog, CTkComboBox
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter import StringVar, filedialog, END
from customtkinter import CTkFrame, CTkEntry, CTkButton, CTkLabel, CTkTextbox
from tkinter.messagebox import showerror,showinfo
from Packages.database import Database
import sqlite3
class productsManager:
    def __init__(self, root, main_frame):
        self.root = root
        self.db = Database()
        self.main_frame = main_frame

    def clear_main_frame(self):
        """Clear all widgets from the main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)  # Make table container expandable
            
    def show_add_product(self):
        """Display add product form"""
        self.clear_main_frame()
        
        CTkLabel(self.main_frame, text="Add New Product", font=("Arial", 24, "bold")).pack(pady=20)
        
        # Create scrollable form
        form_frame = CTkScrollableFrame(self.main_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Product details section
        product_frame = CTkFrame(form_frame)
        product_frame.pack(fill="x", pady=10)
        
        CTkLabel(product_frame, text="Product Details", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        
        # Helper function to create form fields
        def add_field(parent, label_text, placeholder=""):
            frame = CTkFrame(parent)
            frame.pack(fill="x", pady=5, padx=10)
            CTkLabel(frame, text=label_text, width=120).pack(side="left", padx=5)
            entry = CTkEntry(frame, placeholder_text=placeholder)
            entry.pack(side="left", padx=5, fill="x", expand=True)
            return entry
        
        
        # Category dropdown
        category_frame = CTkFrame(product_frame)
        category_frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(category_frame, text="Category:", width=120).pack(side="left", padx=5)
        
        categories = self.db.get_categories()
        category_var = StringVar(value=categories[0] if categories else "")
        category_dropdown = AutocompleteCombobox(category_frame, completevalues=categories, textvariable=category_var)
        category_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        
        # Add "New Category" button
        def add_field(parent, label_text, placeholder=""):
            frame = CTkFrame(parent)
            frame.pack(fill="x", pady=5, padx=10)
            CTkLabel(frame, text=label_text, width=120).pack(side="left", padx=5)
            entry = CTkEntry(frame, placeholder_text=placeholder)
            entry.pack(side="left", padx=5, fill="x", expand=True)
            return frame, entry  # Return both frame and entry
        # Add "New Category" button
        def add_new_category():
            dialog = CTkInputDialog(text="Enter new category name:", title="New Category")
            new_category = dialog.get_input()
            if new_category and new_category.strip():
                try:
                    self.db.add_category(new_category)
                    
                    # Update category dropdown
                    categories = self.db.get_categories()
                    category_dropdown.configure(completevalues=categories)
                    category_var.set(new_category.strip())
                    
                except sqlite3.IntegrityError:
                    showerror("Error", "Category already exists.")
                except Exception as e:
                    showerror("Error", f"Failed to add category: {str(e)}")
        CTkButton(category_frame, text="+", width=30, command=add_new_category).pack(side="left", padx=5)
        
        # Then update all field creations to use tuple unpacking:
        name_frame, name_entry = add_field(product_frame, "Product Name:", "Enter product name")
        brand_frame, brand_entry = add_field(product_frame, "Brand:", "Brand name")
        model_frame, model_entry = add_field(product_frame, "Model:", "Model number")
        
        # Specifications field
        specs_frame = CTkFrame(product_frame)
        specs_frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(specs_frame, text="Specifications:", width=120).pack(side="left", padx=5, anchor="n")
        specs_text = CTkTextbox(specs_frame, height=100)
        specs_text.pack(side="left", padx=5, fill="both", expand=True)
        
        # Image selection
        image_frame = CTkFrame(product_frame)
        image_frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(image_frame, text="Product Image:", width=120).pack(side="left", padx=5)
        image_path_var = StringVar()
        image_path_entry = CTkEntry(image_frame, textvariable=image_path_var)
        image_path_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        def select_image():
            file_path = filedialog.askopenfilename(
                title="Select Product Image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if file_path:
                image_path_var.set(file_path)
                
        CTkButton(image_frame, text="Browse...", command=select_image).pack(side="left", padx=5)
        
        # Inventory details section
        inventory_frame = CTkFrame(form_frame)
        inventory_frame.pack(fill="x", pady=10)
        
        CTkLabel(inventory_frame, text="Inventory Details", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        # Auto-generate SKU button
        def generate_sku():
            # Get current values
            category = category_var.get() if category_var.get() else "PROD"
            brand = brand_entry.get().strip()
            model = model_entry.get().strip()
            
            # Create SKU components
            cat_code = ''.join([c[0] for c in category.split()][:3]).upper()
            brand_code = brand[:3].upper() if brand else "XXX"
            
            # Get a random number for uniqueness
            import random
            unique_id = str(random.randint(1000, 9999))
            
            # Generate SKU
            sku = f"{cat_code}-{brand_code}-{unique_id}"
            self.sku_entry.delete(0, END)
            self.sku_entry.insert(0, sku)
        # Inventory fields
        sku_frame, self.sku_entry = add_field(inventory_frame, "SKU:", "Enter SKU/Barcode")
        CTkButton(sku_frame, text="Generate", width=80, command=generate_sku).pack(side="left", padx=5)
        quantity_frame, self.quantity_entry = add_field(inventory_frame, "Quantity:", "Initial quantity")
        price_frame, self.price_entry = add_field(inventory_frame, "Price ($):", "Selling price")
        cost_frame, self.cost_entry = add_field(inventory_frame, "Cost ($):", "Purchase cost")
        location_frame, self.location_entry = add_field(inventory_frame, "Location:", "Storage location")
        
        
        # Condition dropdown
        condition_frame = CTkFrame(inventory_frame)
        condition_frame.pack(fill="x", pady=5, padx=10)
        CTkLabel(condition_frame, text="Condition:", width=120).pack(side="left", padx=5)
        condition_dropdown = CTkComboBox(condition_frame, 
                                            values=["New", "Like New", "Very Good", "Good", "Fair", "Poor"])
        condition_dropdown.pack(side="left", padx=5, fill="x", expand=True)
        condition_dropdown.set("New")
        
        reorder_frame, reorder_entry = add_field(inventory_frame, "Reorder Point:", "Min quantity before reordering")
        
        # Buttons
        button_frame = CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=20, pady=20)
        
        def clear_form():
            for entry in [name_entry, brand_entry, model_entry, self.sku_entry, 
                        self.quantity_entry, self.price_entry, self.cost_entry, self.location_entry, 
                        reorder_entry]:
                entry.delete(0, END)
            specs_text.delete("1.0", END)
            image_path_var.set("")
            condition_dropdown.set("New")
            category_var.set(categories[0] if categories else "")
        
        def save_product():
            try:
                # Validate required fields
                product_name = name_entry.get().strip()
                if not product_name:
                    showerror("Error", "Product name is required")
                    return
                    
                category = category_var.get().strip()
                if not category:
                    showerror("Error", "Category is required")
                    return
                
                # Validate numeric fields
                try:
                    quantity = int(self.quantity_entry.get()) if self.quantity_entry.get() else 0
                    price = float(self.price_entry.get()) if self.price_entry.get() else 0
                    cost = float(self.cost_entry.get()) if self.cost_entry.get() else 0
                    reorder_point = int(reorder_entry.get()) if reorder_entry.get() else 5
                except ValueError:
                    showerror("Error", "Please enter valid numbers for quantity, price, cost, and reorder point")
                    return
                    
                # Get other fields
                brand = brand_entry.get().strip()
                model = model_entry.get().strip()
                specs = specs_text.get("1.0", END).strip()
                image_path = image_path_var.get().strip()
                sku = self.sku_entry.get().strip()
                location = self.location_entry.get().strip()
                condition = condition_dropdown.get()
                
                self.db.insert_product(category, product_name, brand, model, specs, image_path,
                        quantity, price, cost, sku, location, condition, reorder_point)
                showinfo("Success", f"Product '{product_name}' added successfully")
                clear_form()
                    
            except Exception as e:
                showerror("Error", f"Failed to add product: {str(e)}")
        
        CTkButton(button_frame, text="Clear", command=clear_form, width=100, fg_color="gray").pack(side="left", padx=10)
        CTkButton(button_frame, text="Save Product", command=save_product, width=150).pack(side="right", padx=10) 