from customtkinter import CTkButton, CTkComboBox, CTkEntry, CTkFont
from customtkinter import CTkFrame, CTkLabel, CTkTextbox
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.messagebox import showerror, showinfo, showwarning, askyesno
from PIL import Image, ImageTk
from datetime import datetime, date
import os

class InventoryModule:
    """
    Inventory Management Module for tracking devices, stock, and sales.
    Handles CRUD operations for devices with image support and search functionality.
    """
    
    def __init__(self, parent, database):
        self.parent = parent
        self.db = database
        self.current_image_path = None
        
        # Create main container
        self.main_container = CTkFrame(parent)
        self.setup_ui()
        self.refresh_device_list()
    
    def setup_ui(self):
        """Setup the inventory management user interface."""
        # Configure grid weights
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = CTkLabel(
            self.main_container,
            text="Inventory Management",
            font=CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        
        # Left panel - Device form
        self.setup_device_form()
        
        # Right panel - Device list and search
        self.setup_device_list()
    
    def setup_device_form(self):
        """Setup the device input form on the left side."""
        # Form container
        form_frame = CTkFrame(self.main_container)
        form_frame.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form title
        form_title = CTkLabel(form_frame, text="Device Information", font=CTkFont(size=16, weight="bold"))
        form_title.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Form fields
        fields = [
            ("Device Name:", "device_name"),
            ("Brand:", "brand"),
            ("Model:", "model"),
            ("Category:", "category"),
            ("Serial Number:", "serial_number"),
            ("Purchase Date:", "purchase_date"),
            ("Cost ($):", "cost"),
            ("Location:", "location")
        ]
        
        self.form_vars = {}
        row = 1
        
        for label_text, var_name in fields:
            label = CTkLabel(form_frame, text=label_text)
            label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
            
            if var_name == "category":
                # Category dropdown
                entry = CTkComboBox(
                    form_frame,
                    values=["Mobile", "Laptop", "Desktop", "Tablet", "Accessory", "Other"],
                    width=200
                )
            elif var_name == "purchase_date":
                # Date entry
                entry = CTkEntry(form_frame, placeholder_text="DD-MM-YYYY", width=200)
            else:
                entry = CTkEntry(form_frame, width=200)
            
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            self.form_vars[var_name] = entry
            row += 1
        
        # Description text area
        desc_label = CTkLabel(form_frame, text="Description:")
        desc_label.grid(row=row, column=0, padx=10, pady=5, sticky="nw")
        
        self.description_text = CTkTextbox(form_frame, height=60, width=200)
        self.description_text.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
        self.description_text.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        self.description_text.configure(font=("Arial", 16))  # Right-align for RTL
        row += 1
        
        # Image section
        img_label = CTkLabel(form_frame, text="Device Image:")
        img_label.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        img_button = CTkButton(form_frame, text="Select Image", command=self.select_image, width=200)
        img_button.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        row += 1
        
        # Image preview
        self.image_label = CTkLabel(form_frame, text="No image selected", width=150, height=100)
        self.image_label.grid(row=row, column=1, padx=10, pady=5)
        row += 1
        
        # Buttons
        button_frame = CTkFrame(form_frame)
        button_frame.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.add_btn = CTkButton(button_frame, text="Add Device", command=self.add_device)
        self.add_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.update_btn = CTkButton(button_frame, text="Update Device", command=self.update_device, state="disabled")
        self.update_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.clear_btn = CTkButton(button_frame, text="Clear Form", command=self.clear_form)
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5)
    
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

    def setup_device_list(self):
        """Setup the device list view on the right side."""
        # List container
        list_frame = CTkFrame(self.main_container)
        list_frame.grid(row=1, column=1, padx=(10, 20), pady=(0, 20), sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(2, weight=1)
        
        # Search section
        search_frame = CTkFrame(list_frame)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = CTkLabel(search_frame, text="Search:")
        search_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.search_var = tk.StringVar()
        search_entry = CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Search devices...")
        search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        search_entry.bind("<Key>", self.validate_multilingual_input)  # Validate on key press
        search_entry.configure(font=("Arial", 16))  # Right-align for RTL
        search_entry.bind("<KeyRelease>", self.on_search)
        
        search_btn = CTkButton(search_frame, text="🔍", width=30, command=self.search_devices)
        search_btn.grid(row=0, column=2, padx=5, pady=10)
        
        # Filter section
        filter_frame = CTkFrame(list_frame)
        filter_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        filter_label = CTkLabel(filter_frame, text="Filter by Status:")
        filter_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.status_filter = CTkComboBox(
            filter_frame,
            values=["All", "Available", "Sold"],
            command=self.filter_devices,
            width=150
        )
        self.status_filter.grid(row=0, column=1, padx=10, pady=10)
        self.status_filter.set("All")
        
        # Device list (TreeView)
        list_container = CTkFrame(list_frame)
        list_container.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # Treeview for device list
        columns = ("ID", "Name", "Brand", "Model", "Category", "Serial", "Cost", "Status", "Location")
        self.device_tree = ttk.Treeview(list_container, columns=columns, show="headings", height=15)
        
        # Configure columns
        column_widths = {"ID": 50, "Name": 120, "Brand": 80, "Model": 100, "Category": 80, 
                        "Serial": 100, "Cost": 80, "Status": 80, "Location": 100}
        
        for col in columns:
            self.device_tree.heading(col, text=col)
            self.device_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.device_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_container, orient="horizontal", command=self.device_tree.xview)
        self.device_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid treeview and scrollbars
        self.device_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.device_tree.bind("<Double-1>", self.on_device_select)
        self.device_tree.bind("<Button-1>", self.on_device_click)
        
        # Action buttons
        action_frame = CTkFrame(list_frame)
        action_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.edit_btn = CTkButton(action_frame, text="Edit Selected", command=self.edit_selected_device)
        self.edit_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.sell_btn = CTkButton(action_frame, text="Sell Device", command=self.sell_selected_device)
        self.sell_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.delete_btn = CTkButton(action_frame, text="Delete Device", command=self.delete_selected_device, 
                                       fg_color="red", hover_color="darkred")
        self.delete_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def select_image(self):
        """Open file dialog to select device image."""
        file_types = [("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        
        if file_path:
            self.current_image_path = file_path
            # Display image preview
            try:
                image = Image.open(file_path)
                image.thumbnail((150, 100))
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            except Exception as e:
                showerror("Error", f"Failed to load image: {e}")
    
    def validate_form(self):
        """Validate form inputs before submission."""
        errors = []
        
        # Check required fields
        required_fields = ["device_name", "brand", "model", "category", "serial_number", "purchase_date", "cost", "location"]
        for field in required_fields:
            value = self.form_vars[field].get().strip()
            if not value:
                errors.append(f"{field.replace('_', ' ').title()} is required")
        
        # Validate date format
        try:
            date_str = self.form_vars["purchase_date"].get().strip()
            datetime.strptime(date_str, "%d-%m-%Y")
        except ValueError:
            errors.append("Purchase date must be in DD-MM-YYYY format")
        
        # Validate cost
        try:
            cost = float(self.form_vars["cost"].get().strip())
            if cost < 0:
                errors.append("Cost must be positive")
        except ValueError:
            errors.append("Cost must be a valid number")
        
        if errors:
            showerror("Validation Error", "\n".join(errors))
            return False
        
        return True
    
    def add_device(self):
        """Add a new device to inventory."""
        if not self.validate_form():
            return
        
        try:
            # Collect form data
            device_data = {}
            for field, entry in self.form_vars.items():
                device_data[field] = entry.get().strip()
            
            device_data["description"] = self.description_text.get("1.0", tk.END).strip()
            device_data["image_path"] = self.current_image_path or ""
            device_data["cost"] = float(device_data["cost"])
            
            # Add to database
            device_id = self.db.add_device(device_data)
            
            if device_id:
                showinfo("Success", "Device added successfully!")
                self.clear_form()
                self.refresh_device_list()
            else:
                showerror("Error", "Failed to add device")
        
        except Exception as e:
            showerror("Error", f"Failed to add device: {e}")
    
    def update_device(self):
        """Update selected device information."""
        if not hasattr(self, 'selected_device_id') or not self.selected_device_id:
            showerror("Error", "No device selected for update")
            return
        
        if not self.validate_form():
            return
        
        try:
            # Collect form data
            device_data = {}
            for field, entry in self.form_vars.items():
                if field != "serial_number":  # Don't update serial number
                    device_data[field] = entry.get().strip()
            
            device_data["description"] = self.description_text.get("1.0", tk.END).strip()
            device_data["image_path"] = self.current_image_path or ""
            device_data["cost"] = float(device_data["cost"])
            
            # Update in database
            self.db.update_device(self.selected_device_id, device_data)
            
            showinfo("Success", "Device updated successfully!")
            self.clear_form()
            self.refresh_device_list()
        
        except Exception as e:
            showerror("Error", f"Failed to update device: {e}")
    
    def clear_form(self):
        """Clear all form inputs."""
        for entry in self.form_vars.values():
            if isinstance(entry, CTkEntry):
                entry.delete(0, tk.END)
            elif isinstance(entry, CTkComboBox):
                entry.set("")
        
        self.description_text.delete("1.0", tk.END)
        self.current_image_path = None
        self.image_label.configure(image="", text="No image selected")
        
        # Reset buttons
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.selected_device_id = None
    
    def refresh_device_list(self):
        """Refresh the device list display."""
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        # Get devices from database
        try:
            devices = self.db.get_devices()
            for device in devices:
                values = (
                    device["id"],
                    device["device_name"],
                    device["brand"],
                    device["model"],
                    device["category"],
                    device["serial_number"],
                    f"${device['cost']:.2f}",
                    device["status"].title(),
                    device["location"]
                )
                self.device_tree.insert("", tk.END, values=values)
        
        except Exception as e:
            showerror("Error", f"Failed to refresh device list: {e}")
    
    def on_search(self, event=None):
        """Handle search input changes."""
        self.search_devices()
    
    def search_devices(self):
        """Search devices based on search term."""
        search_term = self.search_var.get().strip()
        
        # Clear existing items
        for item in self.device_tree.get_children():
            self.device_tree.delete(item)
        
        try:
            if search_term:
                devices = self.db.search_devices(search_term)
            else:
                devices = self.db.get_devices()
            
            for device in devices:
                # Apply status filter
                status_filter = self.status_filter.get().lower()
                if status_filter != "all" and device["status"].lower() != status_filter:
                    continue
                
                values = (
                    device["id"],
                    device["device_name"],
                    device["brand"],
                    device["model"],
                    device["category"],
                    device["serial_number"],
                    f"${device['cost']:.2f}",
                    device["status"].title(),
                    device["location"]
                )
                self.device_tree.insert("", tk.END, values=values)
        
        except Exception as e:
            showerror("Error", f"Search failed: {e}")
    
    def filter_devices(self, choice=None):
        """Filter devices by status."""
        self.search_devices()  # Reuse search logic with filter
    
    def on_device_click(self, event):
        """Handle single click on device list."""
        selection = self.device_tree.selection()
        if selection:
            item = self.device_tree.item(selection[0])
            self.selected_device_id = item['values'][0]
    
    def on_device_select(self, event):
        """Handle double-click on device list to edit."""
        self.edit_selected_device()
    
    def edit_selected_device(self):
        """Load selected device data into form for editing."""
        selection = self.device_tree.selection()
        if not selection:
            showwarning("Warning", "Please select a device to edit")
            return
        
        item = self.device_tree.item(selection[0])
        device_id = item['values'][0]
        
        try:
            # Get device details from database
            devices = self.db.get_devices()
            device = next((d for d in devices if d["id"] == device_id), None)
            
            if not device:
                showerror("Error", "Device not found")
                return
            
            # Load data into form
            self.form_vars["device_name"].delete(0, tk.END)
            self.form_vars["device_name"].insert(0, device["device_name"])
            
            self.form_vars["brand"].delete(0, tk.END)
            self.form_vars["brand"].insert(0, device["brand"])
            
            self.form_vars["model"].delete(0, tk.END)
            self.form_vars["model"].insert(0, device["model"])
            
            self.form_vars["category"].set(device["category"])
            
            self.form_vars["serial_number"].delete(0, tk.END)
            self.form_vars["serial_number"].insert(0, device["serial_number"])
            self.form_vars["serial_number"].configure(state="disabled")  # Don't allow serial number changes
            
            self.form_vars["purchase_date"].delete(0, tk.END)
            self.form_vars["purchase_date"].insert(0, device["purchase_date"])
            
            self.form_vars["cost"].delete(0, tk.END)
            self.form_vars["cost"].insert(0, str(device["cost"]))
            
            self.form_vars["location"].delete(0, tk.END)
            self.form_vars["location"].insert(0, device["location"])
            
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert("1.0", device["description"] or "")
            
            # Load image if available
            if device["image_path"] and os.path.exists(device["image_path"]):
                self.current_image_path = device["image_path"]
                try:
                    image = Image.open(device["image_path"])
                    image.thumbnail((150, 100))
                    photo = ImageTk.PhotoImage(image)
                    self.image_label.configure(image=photo, text="")
                    self.image_label.image = photo
                except:
                    pass
            
            # Update button states
            self.selected_device_id = device_id
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="normal")
        
        except Exception as e:
            showerror("Error", f"Failed to load device data: {e}")
    
    def sell_selected_device(self):
        """Open sell device dialog."""
        selection = self.device_tree.selection()
        if not selection:
            showwarning("Warning", "Please select a device to sell")
            return
        
        item = self.device_tree.item(selection[0])
        device_id = item['values'][0]
        device_name = item['values'][1]
        
        # Open sell dialog
        self.open_sell_dialog(device_id, device_name)
    
    def open_sell_dialog(self, device_id, device_name):
        """Open dialog for selling a device."""
        sell_window = CTkToplevel(self.parent)
        sell_window.title(f"Sell Device - {device_name}")
        sell_window.geometry("400x300")
        sell_window.transient(self.parent)
        sell_window.grab_set()
        
        # Form fields
        fields = [
            ("Sale Price ($):", "sale_price"),
            ("Customer Name:", "customer_name"),
            ("Customer Phone:", "customer_phone"),
            ("Sale Date:", "sale_date"),
            ("Payment Method:", "payment_method")
        ]
        
        form_vars = {}
        for i, (label_text, var_name) in enumerate(fields):
            label = CTkLabel(sell_window, text=label_text)
            label.grid(row=i, column=0, padx=10, pady=10, sticky="w")
            
            if var_name == "payment_method":
                entry = CTkComboBox(sell_window, values=["Cash", "Card", "Bank Transfer"])
                entry.set("Cash")
            elif var_name == "sale_date":
                entry = CTkEntry(sell_window)
                entry.insert(0, date.today().strftime("%d-%m-%Y"))
            else:
                entry = CTkEntry(sell_window)
            
            entry.grid(row=i, column=1, padx=10, pady=10, sticky="ew")
            form_vars[var_name] = entry
        
        # Notes
        notes_label = CTkLabel(sell_window, text="Notes:")
        notes_label.grid(row=len(fields), column=0, padx=10, pady=10, sticky="nw")
        
        notes_text = CTkTextbox(sell_window, height=60)
        notes_text.grid(row=len(fields), column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons
        button_frame = CTkFrame(sell_window)
        button_frame.grid(row=len(fields)+1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        def confirm_sale():
            try:
                # Validate inputs
                sale_price = float(form_vars["sale_price"].get())
                sale_date = form_vars["sale_date"].get()
                
                # Prepare sale data
                sale_data = {
                    "sale_price": sale_price,
                    "customer_name": form_vars["customer_name"].get(),
                    "customer_phone": form_vars["customer_phone"].get(),
                    "sale_date": sale_date,
                    "payment_method": form_vars["payment_method"].get(),
                    "notes": notes_text.get("1.0", tk.END).strip()
                }
                
                # Process sale
                self.db.sell_device(device_id, sale_data)
                
                showinfo("Success", "Device sold successfully!")
                sell_window.destroy()
                self.refresh_device_list()
                
            except ValueError:
                showerror("Error", "Please enter a valid sale price")
            except Exception as e:
                showerror("Error", f"Failed to process sale: {e}")
        
        confirm_btn = CTkButton(button_frame, text="Confirm Sale", command=confirm_sale)
        confirm_btn.grid(row=0, column=0, padx=5, pady=5)
        
        cancel_btn = CTkButton(button_frame, text="Cancel", command=sell_window.destroy)
        cancel_btn.grid(row=0, column=1, padx=5, pady=5)
        
        sell_window.grid_columnconfigure(1, weight=1)
    
    def delete_selected_device(self):
        """Delete selected device after confirmation."""
        selection = self.device_tree.selection()
        if not selection:
            showwarning("Warning", "Please select a device to delete")
            return
        
        item = self.device_tree.item(selection[0])
        device_id = item['values'][0]
        device_name = item['values'][1]
        
        # Confirm deletion
        result = askyesno("Confirm Deletion", 
                                    f"Are you sure you want to delete '{device_name}'?\nThis action cannot be undone.")
        
        if result:
            try:
                self.db.delete_device(device_id)
                showinfo("Success", "Device deleted successfully!")
                self.refresh_device_list()
            except Exception as e:
                showerror("Error", f"Failed to delete device: {e}")
    
    def show(self):
        """Show the inventory module."""
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.refresh_device_list()
    
    def hide(self):
        """Hide the inventory module."""
        self.main_container.grid_remove()