# document_generation.py
from customtkinter import CTkFrame, CTkLabel, CTkFont, CTkCheckBox
from customtkinter import CTkButton, CTkEntry, CTkScrollableFrame
from tkinter import StringVar, BooleanVar, IntVar
from tkinter.filedialog import asksaveasfilename 
from tkinter.messagebox import showerror, showinfo, showwarning
from PIL import Image, ImageTk
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
import os
from Packages.database_manager import DatabaseManager

class DocumentModule:
    """
    Document Generation Module
    - Search devices by description/name/model
    - Display devices in a list with quantity selection
    - Build a document containing a table with device details and images
    - Optionally add 14% tax to totals
    """
    def __init__(self, parent, database: DatabaseManager):
        self.parent = parent
        self.db = database
        self.main_container = CTkFrame(parent)
        self.devices_data = []
        self.quantity_vars = []
        self.setup_ui()
    
    def setup_ui(self):
        """Build the UI."""
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Title
        title = CTkLabel(self.main_container, text="Document Generation", font=CTkFont(size=20, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Search frame
        search_frame = CTkFrame(self.main_container)
        search_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(1, weight=1)
        
        CTkLabel(search_frame, text="Search Description:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_var = StringVar()
        search_entry = CTkEntry(search_frame, textvariable=self.search_var, width=300)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        search_btn = CTkButton(search_frame, text="Search Devices", command=self.search_and_display)
        search_btn.grid(row=0, column=2, padx=10, pady=5)
        
        # Devices display frame with scrollable view
        self.devices_frame = CTkScrollableFrame(self.main_container, height=300)
        self.devices_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.devices_frame.grid_columnconfigure(0, weight=1)
        
        # Generation controls frame
        controls_frame = CTkFrame(self.main_container)
        controls_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.tax_var = BooleanVar(value=False)
        tax_cb = CTkCheckBox(controls_frame, text="Include 14% Tax", variable=self.tax_var)
        tax_cb.grid(row=0, column=0, padx=10, pady=5)
        
        self.generate_btn = CTkButton(controls_frame, text="Generate Document", 
                                         command=self.generate_document, state="disabled")
        self.generate_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Summary label
        self.summary_label = CTkLabel(controls_frame, text="No devices selected")
        self.summary_label.grid(row=0, column=2, padx=20, pady=5)
    
    def search_devices(self, keyword: str):
        """Search devices in DB."""
        return self.db.search_devices(keyword)
    
    def search_and_display(self):
        """Search devices and display them in the list."""
        keyword = self.search_var.get().strip()
        if not keyword:
            showwarning("Warning", "Please enter a device description or keyword.")
            return
        
        devices = self.search_devices(keyword)
        if not devices:
            showinfo("No Results", "No devices found matching your description.")
            self.clear_devices_display()
            return
        
        self.display_devices(devices)
    
    def clear_devices_display(self):
        """Clear the devices display frame."""
        for widget in self.devices_frame.winfo_children():
            widget.destroy()
        self.devices_data = []
        self.quantity_vars = []
        self.generate_btn.configure(state="disabled")
        self.update_summary()
    
    def display_devices(self, devices):
        """Display devices in a selectable list with quantity controls."""
        self.clear_devices_display()
        self.devices_data = devices
        self.quantity_vars = []
        
        # Header
        header_frame = CTkFrame(self.devices_frame)
        header_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        
        CTkLabel(header_frame, text="Device", font=CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        CTkLabel(header_frame, text="Details", font=CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        CTkLabel(header_frame, text="Cost", font=CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5)
        CTkLabel(header_frame, text="Quantity", font=CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5)
        
        # Device rows
        for i, device in enumerate(devices):
            device_frame = CTkFrame(self.devices_frame)
            device_frame.grid(row=i+1, column=0, padx=5, pady=2, sticky="ew")
            device_frame.grid_columnconfigure(1, weight=1)
            
            # Device image (thumbnail)
            img_label = CTkLabel(device_frame, text="No Image", width=60, height=60)
            img_path = device.get("image_path", "")
            if img_path and os.path.exists(img_path):
                try:
                    pil_image = Image.open(img_path)
                    pil_image.thumbnail((60, 60), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(pil_image)
                    img_label.configure(image=photo, text="")
                    img_label.image = photo  # Keep a reference
                except Exception:
                    pass  # Use default "No Image" text
            img_label.grid(row=0, column=0, padx=10, pady=5)
            
            # Device details
            details_frame = CTkFrame(device_frame)
            details_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
            
            name_label = CTkLabel(details_frame, text=device.get('device_name', 'Unknown'), 
                                     font=CTkFont(weight="bold"))
            name_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
            
            model_label = CTkLabel(details_frame, text=f"Model: {device.get('model', 'N/A')}")
            model_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
            
            # Cost
            cost = float(device.get('cost', 0))
            cost_label = CTkLabel(device_frame, text=f"${cost:.2f}")
            cost_label.grid(row=0, column=2, padx=10, pady=5)
            
            # Quantity spinner
            qty_var = IntVar(value=0)
            self.quantity_vars.append(qty_var)
            
            qty_frame = CTkFrame(device_frame)
            qty_frame.grid(row=0, column=3, padx=10, pady=5)
            
            minus_btn = CTkButton(qty_frame, text="-", width=30, 
                                     command=lambda idx=i: self.decrease_quantity(idx))
            minus_btn.grid(row=0, column=0, padx=2, pady=2)
            
            qty_label = CTkLabel(qty_frame, textvariable=qty_var, width=40)
            qty_label.grid(row=0, column=1, padx=2, pady=2)
            
            plus_btn = CTkButton(qty_frame, text="+", width=30,
                                   command=lambda idx=i: self.increase_quantity(idx))
            plus_btn.grid(row=0, column=2, padx=2, pady=2)
            
            # Bind quantity change to update summary
            qty_var.trace_add("write", lambda *args: self.update_summary())
        
        self.update_summary()
    
    def increase_quantity(self, device_index):
        """Increase quantity for a device."""
        current_val = self.quantity_vars[device_index].get()
        self.quantity_vars[device_index].set(current_val + 1)
    
    def decrease_quantity(self, device_index):
        """Decrease quantity for a device."""
        current_val = self.quantity_vars[device_index].get()
        if current_val > 0:
            self.quantity_vars[device_index].set(current_val - 1)
    
    def update_summary(self):
        """Update the summary and enable/disable generate button."""
        total_items = sum(var.get() for var in self.quantity_vars)
        total_cost = sum(var.get() * float(self.devices_data[i].get('cost', 0)) 
                        for i, var in enumerate(self.quantity_vars))
        
        if self.tax_var.get():
            total_cost *= 1.14
        
        if total_items > 0:
            self.summary_label.configure(text=f"Items: {total_items} | Total: ${total_cost:.2f}")
            self.generate_btn.configure(state="normal")
        else:
            self.summary_label.configure(text="No devices selected")
            self.generate_btn.configure(state="disabled")
    
    def get_selected_devices(self):
        """Get devices with quantities > 0."""
        selected = []
        for i, qty_var in enumerate(self.quantity_vars):
            qty = qty_var.get()
            if qty > 0:
                device_copy = self.devices_data[i].copy()
                device_copy['quantity'] = qty
                selected.append(device_copy)
        return selected
    
    def generate_document(self):
        """Generate PDF document with selected devices."""
        selected_devices = self.get_selected_devices()
        
        if not selected_devices:
            showwarning("Warning", "Please select at least one device with quantity > 0.")
            return
        
        # Ask where to save PDF
        save_path = asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Document"
        )
        if not save_path:
            return
        
        try:
            self._build_pdf(save_path, selected_devices)
            showinfo("Success", f"Document saved to {save_path}")
        except Exception as e:
            showerror("Error", f"Failed to create document: {e}")
    
    def _build_pdf(self, file_path: str, devices):
        """Build the PDF file with reportlab."""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Add company logo (adjust path and size)
        logo_path = "company_logo.png"  # Change to your logo path
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=5.5*inch, height=1.5*inch)
            elements.append(logo)

        elements.append(Paragraph("Device Report", styles['Title']))
        elements.append(Spacer(1, 0.1 * inch))

        # Table header
        data = [["Device Name", "Image & Model", "Unit Cost", "Quantity", "Total"]]

        grand_total = 0
        for dev in devices:
            img_path = dev.get("image_path") or ""
            if os.path.exists(img_path) and os.path.isfile(img_path):
                img = Image(img_path, width=1.0*inch, height=1.0*inch)
            else:
                img = Paragraph("No Image", styles['Normal'])

            # Create model text
            model_text = Paragraph(dev['model'], styles['Normal'])

            # Stack image and model vertically
            img_and_model = [img, model_text]

            unit_cost = float(dev['cost'])
            qty = dev['quantity']
            line_total = unit_cost * qty
            grand_total += line_total

            data.append([
                dev['device_name'],
                img_and_model,
                f"${unit_cost:.2f}",
                str(qty),
                f"${line_total:.2f}"
            ])

        # Add subtotal row
        data.append(["", "", "", "Subtotal:", f"${grand_total:.2f}"])
        
        # Add tax row if applicable
        if self.tax_var.get():
            tax_amount = grand_total * 0.14
            final_total = grand_total * 1.14
            data.append(["", "", "", "Tax (14%):", f"${tax_amount:.2f}"])
            data.append(["", "", "", "Total:", f"${final_total:.2f}"])

        table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.0*inch, 0.8*inch, 1.0*inch])
        
        # Calculate number of data rows (excluding header and totals)
        num_device_rows = len(devices)
        
        table_style = [
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),  # Header
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (2,1), (-1,-1), "RIGHT"),  # Right align numbers
        ]
        
        # Style the totals section
        totals_start_row = num_device_rows + 1
        table_style.extend([
            ("BACKGROUND", (3, totals_start_row), (-1, -1), colors.lightblue),
            ("FONTNAME", (3, totals_start_row), (-1, -1), "Helvetica-Bold"),
        ])
        
        table.setStyle(TableStyle(table_style))
        elements.append(table)
        
        doc.build(elements)
    
    def show(self):
        self.main_container.grid(row=0, column=0, sticky="nsew")
    
    def hide(self):
        self.main_container.grid_forget()