from customtkinter import CTkFrame, CTkFont, CTkLabel, CTkComboBox
from customtkinter import CTkButton, CTkEntry, CTkToplevel, CTkTextbox
from tkinter import END, StringVar
from tkinter.messagebox import showerror, showinfo, showwarning, askyesno
from tkinter.ttk import Style, Notebook, Scrollbar, Treeview
from tkinter.filedialog import asksaveasfilename
from datetime import datetime, date, timedelta
from calendar import month_name, monthrange
import csv
import locale
import os
# Get system default encoding
system_encoding = locale.getpreferredencoding()
class AccountingModule:
    """
    Professional Accounting & Payroll Module for managing employee salaries, attendance, and payroll processing.
    Features: Employee management, attendance tracking, payroll processing with notes, and comprehensive reporting.
    """
    
    def __init__(self, parent, database):
        self.parent = parent
        self.db = database
        self.selected_employee_id = None
        self._employee_map = {}  # display_name -> id mapping for combos
        
        # Create main container with better styling
        self.main_container = CTkFrame(parent, corner_radius=10)
        self.setup_ui()
        self.refresh_all_data()
    
    def setup_ui(self):
        """Setup the professional accounting and payroll user interface."""
        # Configure grid weights
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Professional header section
        header_frame = CTkFrame(self.main_container, height=80, corner_radius=8)
        header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title with icon placeholder
        title_label = CTkLabel(
            header_frame,
            text="💼 Accounting & Payroll Management System",
            font=CTkFont(size=28, weight="bold"),
            text_color=("gray10", "gray90")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=15, sticky="w")

        style = Style()
        style.theme_use('clam')
        
        self.notebook = Notebook(self.main_container)
        self.notebook.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Setup tabs
        self.setup_employee_tab()
        self.setup_attendance_tab()
        self.setup_payroll_tab()
        self.setup_reports_tab()

    def validate_multilingual_input(self, event):
        """Enhanced multilingual input validation."""
        import unicodedata
        
        # Allow all control and navigation keys
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 
                        'Home', 'End', 'Tab', 'Return', 'Enter', 'Shift_L', 'Shift_R',
                        'Control_L', 'Control_R', 'Alt_L', 'Alt_R'):
            return None
        
        # Skip if no character
        if not event.char:
            return "break"
        
        # Allow common punctuation, numbers, and symbols
        if event.char in (' ', '\t', '\n', '،', '؛', '؟', '.', ',', '!', '?', '(', ')', '-', '_', 
                         '\'', '"', ':', ';', '@', '#', '$', '%', '&', '+', '=', '/', '\\', '|'):
            return None
        
        # Allow digits
        if event.char.isdigit():
            return None
        
        # Check Unicode categories
        try:
            char_code = ord(event.char)
            char_name = unicodedata.name(event.char, '')
            
            # Allow English, Arabic/Persian, and other common scripts
            is_english = 0x0000 <= char_code <= 0x007F
            is_arabic = (char_name.startswith('ARABIC') or 
                        char_name.startswith('PERSIAN') or 
                        char_name.startswith('EXTENDED ARABIC'))
            is_latin_extended = 0x0080 <= char_code <= 0x024F
            
            if not (is_english or is_arabic or is_latin_extended):
                return "break"
                
        except ValueError:
            return "break"
        
        return None

    def setup_employee_tab(self):
        """Setup the enhanced employee management tab."""
        employee_frame = CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(employee_frame, text="👥 Employee Management")
        
        employee_frame.grid_columnconfigure(1, weight=1)
        employee_frame.grid_rowconfigure(0, weight=1)
        
        # Professional employee form (left side)
        form_frame = CTkFrame(employee_frame, corner_radius=8)
        form_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Form header
        form_header = CTkFrame(form_frame, height=50, corner_radius=6)
        form_header.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        form_header.grid_propagate(False)
        
        form_title = CTkLabel(
            form_header, 
            text="Employee Information", 
            font=CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        )
        form_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Enhanced form fields with better styling
        fields = [
            ("Employee Name *:", "employee_name", "entry"),
            ("Position *:", "position", "combo"),
            ("Department:", "department", "combo"),
            ("Base Salary ($) *:", "base_salary", "entry"),
            ("Phone Number:", "phone", "entry"),
            ("Email Address:", "email", "entry"),
            ("Hire Date *:", "hire_date", "entry"),
            ("Emergency Contact:", "emergency_contact", "entry")
        ]
        
        self.employee_vars = {}
        row = 1
        
        for label_text, var_name, field_type in fields:
            # Styled label
            label = CTkLabel(
                form_frame, 
                text=label_text,
                font=CTkFont(size=12, weight="bold" if "*" in label_text else "normal"),
                text_color=("gray20", "gray80")
            )
            label.grid(row=row, column=0, padx=15, pady=8, sticky="w")
            
            # Create appropriate field widget
            if field_type == "combo":
                if var_name == "position":
                    values = ["Manager", "Senior Manager", "Sales Representative", "Senior Sales Rep", 
                             "Accountant", "Senior Accountant", "HR Specialist", "IT Support", 
                             "Marketing Specialist", "Customer Service", "Technician", "Intern", "Other"]
                elif var_name == "department":
                    values = ["Sales", "Accounting", "HR", "IT", "Marketing", "Customer Service", 
                             "Operations", "Management", "Other"]
                else:
                    values = []
                    
                entry = CTkComboBox(
                    form_frame,
                    values=values,
                    width=250,
                    font=CTkFont(size=12),
                    corner_radius=6
                )
            else:
                placeholder = {
                    "hire_date": "YYYY-MM-DD",
                    "base_salary": "e.g., 3000.00",
                    "phone": "e.g., 01027301729",
                    "email": "employee@company.com"
                }.get(var_name, f"Enter {label_text.replace('*:', '').replace(':', '')}")
                
                entry = CTkEntry(
                    form_frame, 
                    placeholder_text=placeholder,
                    width=250,
                    font=CTkFont(size=12),
                    corner_radius=6
                )
                entry.bind("<Key>", self.validate_multilingual_input)
                entry.configure(font=("Arial", 16))  # Right-align for RTL
            
            entry.grid(row=row, column=1, padx=15, pady=8, sticky="ew")
            
            if hasattr(entry, 'bind'):
                entry.bind("<Key>", self.validate_multilingual_input)
                entry.configure(font=("Arial", 16))  # Right-align for RTL
            
            self.employee_vars[var_name] = entry
            row += 1
        
        # Professional button section
        button_frame = CTkFrame(form_frame, corner_radius=6)
        button_frame.grid(row=row, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.add_emp_btn = CTkButton(
            button_frame, 
            text="➕ Add Employee",
            command=self.add_employee,
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("green", "green")
        )
        self.add_emp_btn.grid(row=0, column=0, padx=8, pady=10, sticky="ew")
        
        self.update_emp_btn = CTkButton(
            button_frame,
            text="✏️ Update Employee",
            command=self.update_employee,
            state="disabled",
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("blue", "blue")
        )
        self.update_emp_btn.grid(row=0, column=1, padx=8, pady=10, sticky="ew")
        
        self.clear_emp_btn = CTkButton(
            button_frame,
            text="🔄 Clear Form",
            command=self.clear_employee_form,
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("gray50", "gray50")
        )
        self.clear_emp_btn.grid(row=0, column=2, padx=8, pady=10, sticky="ew")
        
        # Enhanced employee list (right side)
        list_frame = CTkFrame(employee_frame, corner_radius=8)
        list_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)
        
        # List header
        list_header = CTkFrame(list_frame, height=50, corner_radius=6)
        list_header.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        list_header.grid_propagate(False)
        
        list_title = CTkLabel(
            list_header,
            text="Employee Directory",
            font=CTkFont(size=18, weight="bold"),
            text_color=("gray10", "white")
        )
        list_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Professional TreeView
        emp_columns = ("ID", "Name", "Position", "Department", "Salary", "Phone", "Email", "Hire Date", "Status")
        self.employee_tree = Treeview(list_frame, columns=emp_columns, show="headings", height=12)
        
        # Enhanced column configuration
        emp_column_widths = {
            "ID": 50, "Name": 130, "Position": 120, "Department": 100,
            "Salary": 90, "Phone": 120, "Email": 140, "Hire Date": 100, "Status": 80
        }
        
        for col in emp_columns:
            self.employee_tree.heading(col, text=col, anchor="center")
            self.employee_tree.column(col, width=emp_column_widths.get(col, 100), 
                                    minwidth=60, anchor="center")
        
        # Scrollbars
        emp_v_scroll = Scrollbar(list_frame, orient="vertical", command=self.employee_tree.yview)
        emp_h_scroll = Scrollbar(list_frame, orient="horizontal", command=self.employee_tree.xview)
        self.employee_tree.configure(yscrollcommand=emp_v_scroll.set, xscrollcommand=emp_h_scroll.set)
        
        self.employee_tree.grid(row=1, column=0, sticky="nsew")
        emp_v_scroll.grid(row=1, column=1, sticky="ns")
        emp_h_scroll.grid(row=2, column=0, sticky="ew")
        
        # Action buttons
        emp_action_frame = CTkFrame(list_frame, corner_radius=6)
        emp_action_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        emp_action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        edit_emp_btn = CTkButton(
            emp_action_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected_employee,
            font=CTkFont(size=11),
            height=30
        )
        edit_emp_btn.grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        
        deactivate_emp_btn = CTkButton(
            emp_action_frame,
            text="⚠️ Deactivate",
            command=self.deactivate_employee,
            font=CTkFont(size=11),
            height=30,
            fg_color=("orange", "orange")
        )
        deactivate_emp_btn.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        export_emp_btn = CTkButton(
            emp_action_frame,
            text="📊 Export List",
            command=self.export_employee_data,
            font=CTkFont(size=11),
            height=30,
            fg_color=("purple", "purple")
        )
        export_emp_btn.grid(row=0, column=2, padx=5, pady=8, sticky="ew")
        
        # Bind events
        self.employee_tree.bind("<Double-1>", self.on_employee_select)

    def setup_attendance_tab(self):
        """Setup the enhanced attendance tracking tab."""
        attendance_frame = CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(attendance_frame, text="📅 Attendance")
        
        attendance_frame.grid_columnconfigure(0, weight=1)
        attendance_frame.grid_rowconfigure(2, weight=1)
        
        # Professional header
        att_header = CTkFrame(attendance_frame, height=60, corner_radius=6)
        att_header.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        att_header.grid_propagate(False)
        
        att_title = CTkLabel(
            att_header,
            text="⏰ Attendance Management",
            font=CTkFont(size=20, weight="bold"),
            text_color=("gray10", "white")
        )
        att_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Enhanced attendance form
        att_form_frame = CTkFrame(attendance_frame, corner_radius=6)
        att_form_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        att_form_frame.grid_columnconfigure((1, 3, 5, 7, 9), weight=1)
        
        # Form fields with better styling
        fields_config = [
            ("Employee:", "att_employee_var", "att_employee_combo"),
            ("Date:", "att_date_var", "att_date_entry"),
            ("Hours:", "att_hours_var", "att_hours_entry"),
            ("Overtime:", "att_overtime_var", "att_overtime_entry")
        ]
        
        col = 0
        for label_text, var_name, widget_name in fields_config:
            label = CTkLabel(
                att_form_frame,
                text=label_text,
                font=CTkFont(size=12, weight="bold"),
                text_color=("gray20", "gray80")
            )
            label.grid(row=0, column=col, padx=10, pady=15, sticky="w")
            
            if widget_name == "att_employee_combo":
                setattr(self, var_name, StringVar())
                widget = CTkComboBox(
                    att_form_frame,
                    variable=getattr(self, var_name),
                    width=180,
                    font=CTkFont(size=11)
                )
            else:
                setattr(self, var_name, StringVar())
                if "date" in widget_name:
                    getattr(self, var_name).set(date.today().strftime("%Y-%m-%d"))
                    placeholder = "YYYY-MM-DD"
                elif "hours" in widget_name:
                    getattr(self, var_name).set("8.0")
                    placeholder = "8.0"
                elif "overtime" in widget_name:
                    getattr(self, var_name).set("0.0")
                    placeholder = "0.0"
                else:
                    placeholder = ""
                    
                widget = CTkEntry(
                    att_form_frame,
                    textvariable=getattr(self, var_name),
                    placeholder_text=placeholder,
                    width=100,
                    font=CTkFont(size=11)
                )
            
            widget.grid(row=0, column=col+1, padx=10, pady=15, sticky="ew")
            setattr(self, widget_name, widget)
            col += 2
        
        # Record button
        add_att_btn = CTkButton(
            att_form_frame,
            text="📝 Record Attendance",
            command=self.add_attendance,
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("green", "green")
        )
        add_att_btn.grid(row=0, column=col, padx=15, pady=15, sticky="ew")
        
        # Enhanced attendance list
        att_list_frame = CTkFrame(attendance_frame, corner_radius=8)
        att_list_frame.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        att_list_frame.grid_columnconfigure(0, weight=1)
        att_list_frame.grid_rowconfigure(1, weight=1)
        
        # Filter section
        filter_frame = CTkFrame(att_list_frame, corner_radius=6)
        filter_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        filter_frame.grid_columnconfigure(4, weight=1)
        
        filter_label = CTkLabel(
            filter_frame,
            text="🔍 Filter by Employee:",
            font=CTkFont(size=12, weight="bold")
        )
        filter_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.att_filter_var = StringVar()
        self.att_filter_combo = CTkComboBox(
            filter_frame,
            variable=self.att_filter_var,
            command=self.filter_attendance,
            width=200,
            font=CTkFont(size=11)
        )
        self.att_filter_combo.grid(row=0, column=1, padx=10, pady=10)
        
        refresh_att_btn = CTkButton(
            filter_frame,
            text="🔄 Refresh",
            command=self.refresh_attendance,
            font=CTkFont(size=11),
            height=28
        )
        refresh_att_btn.grid(row=0, column=2, padx=15, pady=10)
        
        # Professional TreeView
        att_columns = ("ID", "Employee", "Date", "Hours", "Overtime", "Total Hours", "Status", "Notes")
        self.attendance_tree = Treeview(att_list_frame, columns=att_columns, show="headings", height=10)
        
        att_column_widths = {
            "ID": 50, "Employee": 150, "Date": 100, "Hours": 80,
            "Overtime": 80, "Total Hours": 90, "Status": 80, "Notes": 200
        }
        
        for col in att_columns:
            self.attendance_tree.heading(col, text=col, anchor="center")
            self.attendance_tree.column(col, width=att_column_widths.get(col, 100), 
                                      minwidth=50, anchor="center")
        
        att_v_scroll = Scrollbar(att_list_frame, orient="vertical", command=self.attendance_tree.yview)
        att_h_scroll = Scrollbar(att_list_frame, orient="horizontal", command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscrollcommand=att_v_scroll.set, xscrollcommand=att_h_scroll.set)
        
        self.attendance_tree.grid(row=1, column=0, sticky="nsew")
        att_v_scroll.grid(row=1, column=1, sticky="ns")
        att_h_scroll.grid(row=2, column=0, sticky="ew")

    def setup_payroll_tab(self):
        """Setup the enhanced payroll processing tab with notes functionality."""
        payroll_frame = CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(payroll_frame, text="💰 Payroll")
        
        payroll_frame.grid_columnconfigure(0, weight=1)
        payroll_frame.grid_rowconfigure(3, weight=1)
        
        # Professional header
        payroll_header = CTkFrame(payroll_frame, height=60, corner_radius=6)
        payroll_header.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        payroll_header.grid_propagate(False)
        
        payroll_title = CTkLabel(
            payroll_header,
            text="💰 Payroll Management System",
            font=CTkFont(size=20, weight="bold"),
            text_color=("gray10", "white")
        )
        payroll_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Monthly payroll processing
        process_frame = CTkFrame(payroll_frame, corner_radius=6)
        process_frame.grid(row=1, column=0, padx=15, pady=10, sticky="ew")
        process_frame.grid_columnconfigure(6, weight=1)
        
        process_title = CTkLabel(
            process_frame,
            text="📊 Process Monthly Payroll",
            font=CTkFont(size=16, weight="bold"),
            text_color=("gray10", "white")
        )
        process_title.grid(row=0, column=0, columnspan=7, padx=15, pady=15, sticky="w")
        
        # Month/Year selection with better styling
        month_label = CTkLabel(process_frame, text="Month:", font=CTkFont(size=12, weight="bold"))
        month_label.grid(row=1, column=0, padx=10, pady=15)
        
        self.payroll_month_var = StringVar(value=str(datetime.now().month))
        month_combo = CTkComboBox(
            process_frame,
            variable=self.payroll_month_var,
            values=[f"{i:02d}" for i in range(1, 13)],
            width=70,
            font=CTkFont(size=11)
        )
        month_combo.grid(row=1, column=1, padx=10, pady=15)
        
        year_label = CTkLabel(process_frame, text="Year:", font=CTkFont(size=12, weight="bold"))
        year_label.grid(row=1, column=2, padx=10, pady=15)
        
        self.payroll_year_var = StringVar(value=str(datetime.now().year))
        year_combo = CTkComboBox(
            process_frame,
            variable=self.payroll_year_var,
            values=[str(datetime.now().year - 1), str(datetime.now().year), str(datetime.now().year + 1)],
            width=80,
            font=CTkFont(size=11)
        )
        year_combo.grid(row=1, column=3, padx=10, pady=15)
        
        process_btn = CTkButton(
            process_frame,
            text="⚡ Process Payroll",
            command=self.process_monthly_payroll,
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("green", "green")
        )
        process_btn.grid(row=1, column=4, padx=20, pady=15)
        
        # ENHANCED: Individual payroll adjustment with notes
        adjust_frame = CTkFrame(payroll_frame, corner_radius=6)
        adjust_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        adjust_frame.grid_columnconfigure(7, weight=1)
        
        adjust_title = CTkLabel(
            adjust_frame,
            text="✏️ Payroll Adjustments (with Notes)",
            font=CTkFont(size=16, weight="bold"),
            text_color=("gray10", "white")
        )
        adjust_title.grid(row=0, column=0, columnspan=8, padx=15, pady=15, sticky="w")
        
        # Employee selection
        adj_emp_label = CTkLabel(adjust_frame, text="Employee:", font=CTkFont(size=12, weight="bold"))
        adj_emp_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.adj_employee_var = StringVar()
        self.adj_employee_combo = CTkComboBox(
            adjust_frame,
            variable=self.adj_employee_var,
            width=180,
            font=CTkFont(size=11)
        )
        self.adj_employee_combo.grid(row=1, column=1, padx=10, pady=10)
        
        # Bonus field
        bonus_label = CTkLabel(adjust_frame, text="Bonus ($):", font=CTkFont(size=12, weight="bold"))
        bonus_label.grid(row=1, column=2, padx=10, pady=10)
        
        self.bonus_var = StringVar(value="0.00")
        bonus_entry = CTkEntry(
            adjust_frame,
            textvariable=self.bonus_var,
            width=100,
            font=CTkFont(size=11),
            placeholder_text="0.00"
        )
        bonus_entry.grid(row=1, column=3, padx=10, pady=10)
        
        # Deduction field
        deduction_label = CTkLabel(adjust_frame, text="Deduction ($):", font=CTkFont(size=12, weight="bold"))
        deduction_label.grid(row=1, column=4, padx=10, pady=10)
        
        self.deduction_var = StringVar(value="0.00")
        deduction_entry = CTkEntry(
            adjust_frame,
            textvariable=self.deduction_var,
            width=100,
            font=CTkFont(size=11),
            placeholder_text="0.00"
        )
        deduction_entry.grid(row=1, column=5, padx=10, pady=10)
        
        # NEW: Notes field
        notes_label = CTkLabel(adjust_frame, text="Notes:", font=CTkFont(size=12, weight="bold"))
        notes_label.grid(row=2, column=0, padx=10, pady=10, sticky="nw")
        
        self.adjustment_notes_var = StringVar()
        notes_entry = CTkEntry(
            adjust_frame,
            textvariable=self.adjustment_notes_var,
            width=400,
            font=CTkFont(size=11),
            placeholder_text="Enter reason for bonus/deduction (required for adjustments)"
        )
        notes_entry.grid(row=2, column=1, columnspan=4, padx=10, pady=10, sticky="ew")
        notes_entry.bind("<Key>", self.validate_multilingual_input)
        notes_entry.configure(font=("Arial", 16))  # Right-align for RTL
        
        # Apply button
        adjust_btn = CTkButton(
            adjust_frame,
            text="💾 Apply Adjustment",
            command=self.apply_payroll_adjustment,
            font=CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=6,
            fg_color=("blue", "blue")
        )
        adjust_btn.grid(row=2, column=5, padx=15, pady=10)
        
        # Enhanced payroll records list
        payroll_list_frame = CTkFrame(payroll_frame, corner_radius=8)
        payroll_list_frame.grid(row=3, column=0, padx=15, pady=15, sticky="nsew")
        payroll_list_frame.grid_columnconfigure(0, weight=1)
        payroll_list_frame.grid_rowconfigure(1, weight=1)
        
        # Professional filter section
        payroll_filter_frame = CTkFrame(payroll_list_frame, corner_radius=6)
        payroll_filter_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        payroll_filter_frame.grid_columnconfigure(6, weight=1)
        
        filter_month_label = CTkLabel(
            payroll_filter_frame,
            text="🔍 Filter - Month:",
            font=CTkFont(size=12, weight="bold")
        )
        filter_month_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.filter_month_var = StringVar()
        filter_month_combo = CTkComboBox(
            payroll_filter_frame,
            variable=self.filter_month_var,
            values=["All"] + [f"{i:02d}" for i in range(1, 13)],
            command=self.filter_payroll,
            width=80,
            font=CTkFont(size=11)
        )
        filter_month_combo.set("All")
        filter_month_combo.grid(row=0, column=1, padx=10, pady=10)
        
        filter_year_label = CTkLabel(
            payroll_filter_frame,
            text="Year:",
            font=CTkFont(size=12, weight="bold")
        )
        filter_year_label.grid(row=0, column=2, padx=10, pady=10)
        
        self.filter_year_var = StringVar(value=str(datetime.now().year))
        filter_year_combo = CTkComboBox(
            payroll_filter_frame,
            variable=self.filter_year_var,
            values=[str(datetime.now().year - 1), str(datetime.now().year), str(datetime.now().year + 1)],
            command=self.filter_payroll,
            width=80,
            font=CTkFont(size=11)
        )
        filter_year_combo.grid(row=0, column=3, padx=10, pady=10)
        
        refresh_payroll_btn = CTkButton(
            payroll_filter_frame,
            text="🔄 Refresh",
            command=self.refresh_payroll,
            font=CTkFont(size=11),
            height=28
        )
        refresh_payroll_btn.grid(row=0, column=4, padx=15, pady=10)
        
        # Professional TreeView with enhanced columns
        payroll_columns = ("ID", "Employee", "Month", "Year", "Base Salary", "Bonuses", "Deductions", "Total", "Status", "Last Modified", "Notes")
        self.payroll_tree = Treeview(payroll_list_frame, columns=payroll_columns, show="headings", height=8)
        
        payroll_column_widths = {
            "ID": 50, "Employee": 120, "Month": 60, "Year": 60, "Base Salary": 90,
            "Bonuses": 80, "Deductions": 80, "Total": 90, "Status": 80, "Last Modified": 100, "Notes": 200
        }
        
        for col in payroll_columns:
            self.payroll_tree.heading(col, text=col, anchor="center")
            self.payroll_tree.column(col, width=payroll_column_widths.get(col, 80), 
                                   minwidth=50, anchor="center")
        
        payroll_v_scroll = Scrollbar(payroll_list_frame, orient="vertical", command=self.payroll_tree.yview)
        payroll_h_scroll = Scrollbar(payroll_list_frame, orient="horizontal", command=self.payroll_tree.xview)
        self.payroll_tree.configure(yscrollcommand=payroll_v_scroll.set, xscrollcommand=payroll_h_scroll.set)
        
        self.payroll_tree.grid(row=1, column=0, sticky="nsew")
        payroll_v_scroll.grid(row=1, column=1, sticky="ns")
        payroll_h_scroll.grid(row=2, column=0, sticky="ew")
        
        # Payroll action buttons
        payroll_action_frame = CTkFrame(payroll_list_frame, corner_radius=6)
        payroll_action_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        payroll_action_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        view_details_btn = CTkButton(
            payroll_action_frame,
            text="👁️ View Details",
            command=self.view_payroll_details,
            font=CTkFont(size=11),
            height=30
        )
        view_details_btn.grid(row=0, column=0, padx=5, pady=8, sticky="ew")
        
        mark_paid_btn = CTkButton(
            payroll_action_frame,
            text="✅ Mark as Paid",
            command=self.mark_payroll_paid,
            font=CTkFont(size=11),
            height=30,
            fg_color=("green", "green")
        )
        mark_paid_btn.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        
        export_payroll_btn = CTkButton(
            payroll_action_frame,
            text="📊 Export Payroll",
            command=self.export_payroll_data,
            font=CTkFont(size=11),
            height=30,
            fg_color=("purple", "purple")
        )
        export_payroll_btn.grid(row=0, column=2, padx=5, pady=8, sticky="ew")

    def setup_reports_tab(self):
        """Setup the enhanced reports and analytics tab."""
        reports_frame = CTkFrame(self.notebook, corner_radius=8)
        self.notebook.add(reports_frame, text="📊 Reports")
        
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_rowconfigure(1, weight=1)
        
        # Professional header
        reports_header = CTkFrame(reports_frame, height=60, corner_radius=6)
        reports_header.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        reports_header.grid_propagate(False)
        
        reports_title = CTkLabel(
            reports_header,
            text="📊 Payroll Reports & Analytics Dashboard",
            font=CTkFont(size=20, weight="bold"),
            text_color=("gray10", "white")
        )
        reports_title.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Enhanced reports content
        reports_content = CTkFrame(reports_frame, corner_radius=8)
        reports_content.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        reports_content.grid_columnconfigure(1, weight=1)
        reports_content.grid_rowconfigure(2, weight=1)
        
        # Summary statistics cards
        stats_frame = CTkFrame(reports_content, corner_radius=6)
        stats_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stats cards
        self.stats_cards = {}
        stats_config = [
            ("👥 Total Employees", "total_employees", ("blue", "blue")),
            ("✅ Active Employees", "active_employees", ("green", "green")),
            ("💰 Monthly Payroll", "monthly_payroll", ("orange", "orange")),
            ("📈 YTD Payroll", "ytd_payroll", ("purple", "purple"))
        ]
        
        for i, (title, key, color) in enumerate(stats_config):
            card = CTkFrame(stats_frame, corner_radius=6, fg_color=color)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            
            title_label = CTkLabel(
                card,
                text=title,
                font=CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            title_label.grid(row=0, column=0, padx=15, pady=(15, 5))
            
            value_label = CTkLabel(
                card,
                text="Loading...",
                font=CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            value_label.grid(row=1, column=0, padx=15, pady=(5, 15))
            
            self.stats_cards[key] = value_label
        
        # Report generation section
        report_gen_frame = CTkFrame(reports_content, corner_radius=6)
        report_gen_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        report_gen_frame.grid_columnconfigure(5, weight=1)
        
        report_title = CTkLabel(
            report_gen_frame,
            text="📄 Generate Reports",
            font=CTkFont(size=16, weight="bold"),
            text_color=("gray10", "white")
        )
        report_title.grid(row=0, column=0, columnspan=6, padx=15, pady=15, sticky="w")
        
        # Export buttons with icons
        export_buttons = [
            ("📊 Export Payroll Data", self.export_payroll_data, ("blue", "blue")),
            ("📅 Export Attendance", self.export_attendance_data, ("green", "green")),
            ("👥 Export Employee List", self.export_employee_data, ("orange", "orange")),
            ("📈 Generate Summary Report", self.generate_summary_report, ("purple", "purple"))
        ]
        
        for i, (text, command, color) in enumerate(export_buttons):
            btn = CTkButton(
                report_gen_frame,
                text=text,
                command=command,
                font=CTkFont(size=12, weight="bold"),
                height=35,
                corner_radius=6,
                fg_color=color
            )
            btn.grid(row=1, column=i, padx=10, pady=15, sticky="ew")
        
        # Detailed statistics display
        details_frame = CTkFrame(reports_content, corner_radius=6)
        details_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(0, weight=1)
        
        self.details_text = CTkTextbox(
            details_frame,
            font=CTkFont(size=12),
            corner_radius=6
        )
        self.details_text.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
    
    def refresh_payroll(self, month: str = None, year: str = None):
        """Refresh payroll records with optional month/year filtering."""
        for item in self.payroll_tree.get_children():
            self.payroll_tree.delete(item)
        
        try:
            # Convert year to int if provided
            year_int = int(year) if year else ''
            
            # Get payroll records with optional filtering
            records = self.db.get_payroll_records(month=month, year=year_int)
            
            # Handle case when no records are found
            if records is None:
                records = []
                
            for record in records:
                status_icon = "✅" if record['status'].lower() == 'paid' else "🔄"
                
                values = (
                    record['id'],
                    record['employee_name'],
                    record['month'],
                    record['year'],
                    f"${record['base_salary']:,.2f}",
                    f"${record['bonuses']:,.2f}",
                    f"${record['deductions']:,.2f}",
                    f"${record['total_salary']:,.2f}",
                    f"{status_icon} {record['status'].capitalize()}",
                    record.get('updated_at', 'N/A'),
                    record.get('notes', '')[:50] + "..." if len(record.get('notes', '')) > 50 else record.get('notes', '')
                )
                self.payroll_tree.insert("", END, values=values)
                
        except Exception as e:
            showerror("❌ Error", f"Failed to refresh payroll records: {str(e)}")

    def refresh_all_data(self):
        """Refresh all data displays in the module."""
        self.refresh_employees()
        self.refresh_attendance()
        self.refresh_payroll()
        self.update_employee_combos()

    # Export Methods
    def export_payroll_data(self):
        """Export payroll records (filtered view) to CSV."""
        try:
            # Use currently displayed payroll rows
            rows = []
            for iid in self.payroll_tree.get_children():
                rows.append(self.payroll_tree.item(iid)['values'])
            if not rows:
                showinfo("Export", "No payroll data to export.")
                return
            # Ask user for filename
            path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save Payroll CSV")
            if not path:
                return
            # Use header from tree columns
            headers = ["ID","Employee","Month","Year","Base Salary","Bonuses","Deductions","Total","Status"]
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(r)
            showinfo("Export", f"Payroll data exported to {path}")
        except Exception as e:
            showerror("Error", f"Failed to export payroll data: {e}")
    
    def export_attendance_data(self):
        """Export attendance records (filtered) to CSV."""
        try:
            rows = []
            for iid in self.attendance_tree.get_children():
                rows.append(self.attendance_tree.item(iid)['values'])
            if not rows:
                showinfo("Export", "No attendance data to export.")
                return
            path = asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Save Attendance CSV")
            if not path:
                return
            headers = ["ID","Employee","Date","Hours","Overtime","Notes"]
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                for r in rows:
                    writer.writerow(r)
            showinfo("Export", f"Attendance data exported to {path}")
        except Exception as e:
            showerror("Error", f"Failed to export attendance data: {e}")
    
    # UI helper methods
    def update_employee_combos(self):
        """Update all employee-related combo boxes and internal mapping."""
        try:
            employees = self.db.get_employees(active_only=False)
            display_list = []
            self._employee_map.clear()
            for e in employees:
                disp = f"{e['employee_name']} (ID:{e['id']})"
                display_list.append(disp)
                self._employee_map[disp] = e['id']
            # Add "All" option for filter combos
            att_filter_values = ["All"] + display_list
            self.att_employee_combo.configure(values=display_list)
            self.att_filter_combo.configure(values=att_filter_values)
            self.att_filter_combo.set("All")
            self.adj_employee_combo.configure(values=display_list)
        except Exception as e:
            # Non-fatal: just warn in UI
            print(f"Failed to update employee combos: {e}")

    # ENHANCED EMPLOYEE MANAGEMENT METHODS
    def add_employee(self):
        """Add a new employee with enhanced validation."""
        if not self.validate_employee_form():
            return
        
        try:
            employee_data = {}
            for field, entry in self.employee_vars.items():
                if hasattr(entry, 'get'):
                    value = entry.get().strip()
                    employee_data[field] = value if value else None
            
            # Convert salary to float
            employee_data["base_salary"] = float(employee_data["base_salary"])
            
            # Add creation timestamp
            employee_data["created_at"] = datetime.now().isoformat()
            employee_data["is_active"] = True
            
            employee_id = self.db.add_employee(employee_data)
            
            if employee_id:
                showinfo("✅ Success", f"Employee '{employee_data['employee_name']}' added successfully!\nEmployee ID: {employee_id}")
                self.clear_employee_form()
                self.refresh_employees()
                self.update_employee_combos()
            else:
                showerror("❌ Error", "Failed to add employee to database")
        
        except Exception as e:
            showerror("❌ Error", f"Failed to add employee: {str(e)}")
    
    def validate_employee_form(self):
        """Enhanced employee form validation."""
        errors = []
        
        # Check required fields
        required_fields = {
            "employee_name": "Employee Name",
            "position": "Position", 
            "base_salary": "Base Salary",
            "hire_date": "Hire Date"
        }
        
        for field, label in required_fields.items():
            value = self.employee_vars[field].get().strip()
            if not value:
                errors.append(f"• {label} is required")
        
        # Validate salary
        try:
            salary_str = self.employee_vars["base_salary"].get().strip()
            if salary_str:
                salary = float(salary_str)
                if salary < 0:
                    errors.append("• Base salary must be positive")
                elif salary > 1000000:
                    errors.append("• Base salary seems unreasonably high")
        except ValueError:
            errors.append("• Base salary must be a valid number")
        
        # Validate date
        try:
            date_str = self.employee_vars["hire_date"].get().strip()
            if date_str:
                hire_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if hire_date > date.today():
                    errors.append("• Hire date cannot be in the future")
                elif hire_date < date(1950, 1, 1):
                    errors.append("• Hire date seems unreasonably old")
        except ValueError:
            errors.append("• Hire date must be in YYYY-MM-DD format")
        
        # Validate email if provided
        email = self.employee_vars["email"].get().strip()
        if email and "@" not in email:
            errors.append("• Email address format is invalid")
        
        if errors:
            showerror("❌ Validation Error", "\n".join(errors))
            return False
        
        return True
    
    def update_employee(self):
        """Update selected employee with enhanced feedback."""
        if not self.selected_employee_id:
            showerror("❌ Error", "No employee selected for update")
            return
        
        if not self.validate_employee_form():
            return
        
        try:
            employee_data = {}
            for field, entry in self.employee_vars.items():
                try:
                    if isinstance(entry, CTkEntry):
                        value = entry.get().strip() if entry.get() else ""
                        employee_data[field] = value if value else None
                    elif isinstance(entry, CTkComboBox):
                        value = entry.get().strip() if entry.get() else ""
                        employee_data[field] = value if value else None
                    elif hasattr(entry, 'get'):
                        value = entry.get()
                        if isinstance(value, str):
                            value = value.strip()
                        employee_data[field] = value if value else None
                    else:
                        print(f"Warning: Unknown widget type for field {field}: {type(entry)}")
                        employee_data[field] = None
                except Exception as widget_error:
                    print(f"Warning: Could not get value for field {field}: {widget_error}")
                    employee_data[field] = None
            
            # Validate and convert salary
            try:
                salary_value = employee_data.get("base_salary")
                if salary_value:
                    employee_data["base_salary"] = float(salary_value)
                else:
                    showerror("❌ Error", "Base salary is required")
                    return
            except (ValueError, TypeError) as salary_error:
                showerror("❌ Error", f"Invalid salary value: {salary_error}")
                return
            
            # Add update timestamp
            employee_data["updated_at"] = datetime.now().isoformat()
            
            # Perform the database update
            result = self.db.update_employee(self.selected_employee_id, employee_data)
            
            if result:
                emp_name = employee_data.get("employee_name", "Employee")
                showinfo("✅ Success", f"Employee '{emp_name}' updated successfully!")
                self.clear_employee_form()
                self.refresh_employees()
                self.update_employee_combos()
            else:
                showerror("❌ Error", "Failed to update employee in database")
        
        except Exception as e:
            showerror("❌ Error", f"Failed to update employee: {str(e)}")

    def clear_employee_form(self):
        """Clear the employee form with better state management."""
        try:
            for field, entry in self.employee_vars.items():
                try:
                    if isinstance(entry, CTkEntry):
                        entry.delete(0, END)
                    elif isinstance(entry, CTkComboBox):
                        entry.set("")
                    elif hasattr(entry, 'delete') and hasattr(entry, 'insert'):
                        entry.delete(0, END)
                    elif hasattr(entry, 'set'):
                        entry.set("")
                    else:
                        showerror("Error",f"Warning: Unknown widget type for field {field}: {type(entry)}")
                except Exception as widget_error:
                    showerror("Error",f"Warning: Could not clear field {field}: {widget_error}")
            
            # Reset form state
            self.selected_employee_id = None
            self.add_emp_btn.configure(state="normal", text="➕ Add Employee")
            self.update_emp_btn.configure(state="disabled")
            
        except Exception as e:
            showerror("Error",f"Warning: Error clearing employee form: {e}")

    
    def refresh_employees(self):
        """Refresh employee list with enhanced display."""
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        try:
            employees = self.db.get_employees(active_only=False)
            for emp in employees:
                status = "🟢 Active" if emp["is_active"] else "🔴 Inactive"
                values = (
                    emp["id"],
                    emp["employee_name"],
                    emp["position"],
                    emp.get("department", "N/A"),
                    f"${emp['base_salary']:,.2f}",
                    emp["phone"] or "N/A",
                    emp["email"] or "N/A",
                    emp["hire_date"],
                    status
                )
                self.employee_tree.insert("", END, values=values)
        
        except Exception as e:
            showerror("❌ Error", f"Failed to refresh employee list: {str(e)}")
    
    def on_employee_select(self, event):
        """Enhanced employee selection with better feedback."""
        selection = self.employee_tree.selection()
        if not selection:
            return
        
        item = self.employee_tree.item(selection[0])
        employee_id = item['values'][0]
        
        try:
            employees = self.db.get_employees(active_only=False)
            employee = next((e for e in employees if e["id"] == employee_id), None)
            
            if not employee:
                showwarning("⚠️ Warning", "Employee data not found")
                return
            
            # Load employee data into form
            form_fields = [
                ("employee_name", employee["employee_name"]),
                ("position", employee["position"]),
                ("department", employee.get("department", "")),
                ("base_salary", str(employee["base_salary"])),
                ("phone", employee["phone"] or ""),
                ("email", employee["email"] or ""),
                ("hire_date", employee["hire_date"]),
                ("emergency_contact", employee.get("emergency_contact", ""))
            ]
            
            for field, value in form_fields:
                if field in self.employee_vars:
                    widget = self.employee_vars[field]
                    if isinstance(widget, CTkEntry):
                        widget.delete(0, END)
                        if value:  # Only insert if value is not None/empty
                            widget.insert(0, value)
                    elif isinstance(widget, CTkComboBox):
                        try:
                            # For ComboBox, we need to handle the current values
                            current_values = widget.cget("values")
                            if value and value in current_values:
                                widget.set(value)
                            elif value:
                                # If the value is not in the current values, add it temporarily
                                new_values = list(current_values) + [value]
                                widget.configure(values=new_values)
                                widget.set(value)
                            else:
                                widget.set("")
                        except Exception as e:
                            print(f"Warning: Could not set combobox value for {field}: {e}")
                            # Fallback: try to set it anyway
                            try:
                                widget.set(value if value else "")
                            except:
                                pass
            
            # Update button states
            self.selected_employee_id = employee_id
            self.add_emp_btn.configure(state="disabled", text="🚫 Select Different Action")
            self.update_emp_btn.configure(state="normal")
        
        except Exception as e:
            showerror("❌ Error", f"Failed to load employee data: {str(e)}")
    
    def edit_selected_employee(self):
        """Edit the selected employee with validation."""
        selection = self.employee_tree.selection()
        if selection:
            self.on_employee_select(None)
        else:
            showwarning("⚠️ Warning", "Please select an employee from the list to edit")
    
    def deactivate_employee(self):
        """Deactivate employee with enhanced confirmation."""
        selection = self.employee_tree.selection()
        if not selection:
            showwarning("⚠️ Warning", "Please select an employee to deactivate")
            return
        
        item = self.employee_tree.item(selection[0])
        employee_id = item['values'][0]
        employee_name = item['values'][1]
        current_status = item['values'][8]
        
        if "Inactive" in current_status:
            showinfo("ℹ️ Information", f"Employee '{employee_name}' is already inactive")
            return
        
        result = askyesno(
            "⚠️ Confirm Deactivation", 
            f"Are you sure you want to deactivate employee:\n\n'{employee_name}' (ID: {employee_id})\n\nThis will:\n• Mark them as inactive\n• Remove them from active payroll\n• Keep their historical records"
        )
        
        if result:
            try:
                self.db.execute_query(
                    "UPDATE employees SET is_active=0, updated_at=? WHERE id=?", 
                    (datetime.now().isoformat(), employee_id)
                )
                showinfo("✅ Success", f"Employee '{employee_name}' deactivated successfully!")
                self.refresh_employees()
                self.update_employee_combos()
            except Exception as e:
                showerror("❌ Error", f"Failed to deactivate employee: {str(e)}")
    
    def export_employee_data(self):
        """Export employee data with enhanced formatting."""
        try:
            employees = self.db.get_employees(active_only=False)
            if not employees:
                showinfo("ℹ️ Information", "No employee data to export")
                return
            
            filename = f"employees_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            path = asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Employee Data",
                initialfile=filename
            )
            
            if not path:
                return
            
            headers = ["ID", "Name", "Position", "Department", "Base Salary", "Phone", "Email", 
                      "Hire Date", "Emergency Contact", "Status", "Created Date", "Last Modified"]
            
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for emp in employees:
                    status = "Active" if emp["is_active"] else "Inactive"
                    row = [
                        emp["id"],
                        emp["employee_name"],
                        emp["position"],
                        emp.get("department", "N/A"),
                        emp["base_salary"],
                        emp["phone"] or "N/A",
                        emp["email"] or "N/A",
                        emp["hire_date"],
                        emp.get("emergency_contact", "N/A"),
                        status,
                        emp.get("created_at", "N/A"),
                        emp.get("updated_at", "N/A")
                    ]
                    writer.writerow(row)
            
            showinfo("✅ Success", f"Employee data exported successfully!\n\nFile: {path}\nRecords: {len(employees)}")
        
        except Exception as e:
            showerror("❌ Error", f"Failed to export employee data: {str(e)}")
    
    # ENHANCED ATTENDANCE METHODS
    def add_attendance(self):
        """Add attendance with enhanced validation and status tracking."""
        try:
            employee_display = self.att_employee_var.get()
            if not employee_display:
                showwarning("⚠️ Warning", "Please select an employee")
                return
                
            employee_id = self._employee_map.get(employee_display)
            if not employee_id:
                showerror("❌ Error", "Selected employee not found")
                return
            
            date_str = self.att_date_var.get().strip()
            try:
                attendance_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if attendance_date > date.today():
                    showerror("❌ Error", "Attendance date cannot be in the future")
                    return
            except ValueError:
                showerror("❌ Error", "Date must be in YYYY-MM-DD format")
                return
            
            try:
                hours = float(self.att_hours_var.get())
                overtime = float(self.att_overtime_var.get())
                
                if hours < 0 or hours > 24:
                    showerror("❌ Error", "Regular hours must be between 0 and 24")
                    return
                    
                if overtime < 0 or overtime > 12:
                    showerror("❌ Error", "Overtime hours must be between 0 and 12")
                    return
                    
            except ValueError:
                showerror("❌ Error", "Hours and Overtime must be valid numbers")
                return
            
            # Check for duplicate attendance
            existing = self.db.get_attendance_records(employee_id=employee_id, date_from=date_str, date_to=date_str)
            if existing:
                result = askyesno(
                    "⚠️ Duplicate Found", 
                    f"Attendance already recorded for {employee_display.split(' (')[0]} on {date_str}.\n\nDo you want to update the existing record?"
                )
                if not result:
                    return
            
            total_hours = hours + overtime
            status = "Present" if hours > 0 else "Absent"
            if overtime > 0:
                status += " (OT)"
            
            attendance_data = {
                'employee_id': employee_id,
                'date': date_str,
                'hours_worked': hours,
                'overtime_hours': overtime,
                'total_hours': total_hours,
                'status': status,
                'notes': f'Recorded on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
            }
            
            if existing:
                # Update existing record
                self.db.execute_query("""
                    UPDATE attendance SET hours_worked=?, overtime_hours=?, notes=?, updated_at=?
                    WHERE employee_id=? AND date=?
                """, (hours, overtime, attendance_data['notes'], datetime.now().isoformat(), employee_id, date_str))
                action = "updated"
            else:
                # Add new record
                self.db.add_attendance(attendance_data)
                action = "recorded"
            
            showinfo("✅ Success", f"Attendance {action} successfully!\n\nEmployee: {employee_display.split(' (')[0]}\nDate: {date_str}\nHours: {hours}, Overtime: {overtime}")
            
            # Reset form
            self.att_date_var.set(date.today().strftime("%Y-%m-%d"))
            self.att_hours_var.set("8.0")
            self.att_overtime_var.set("0.0")
            
            self.refresh_attendance()
            
        except Exception as e:
            showerror("❌ Error", f"Failed to add attendance: {str(e)}")
    
    def filter_attendance(self, _=None):
        """Enhanced attendance filtering."""
        try:
            selection = self.att_filter_var.get()
            if not selection or selection == "All":
                self.refresh_attendance()
                return
                
            employee_id = self._employee_map.get(selection)
            if not employee_id:
                showerror("❌ Error", "Selected employee not found")
                return
                
            self.refresh_attendance(employee_id=employee_id)
            
        except Exception as e:
            showerror("❌ Error", f"Failed to filter attendance: {str(e)}")
    
    def refresh_attendance(self, employee_id: int = None, date_from: str = None, date_to: str = None):
        """Enhanced attendance refresh with better display."""
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
            
        try:
            # Apply current filter if no specific employee_id provided
            if employee_id is None:
                selection = self.att_filter_var.get()
                if selection and selection != "All":
                    employee_id = self._employee_map.get(selection)
            
            records = self.db.get_attendance_records(employee_id=employee_id, date_from=date_from, date_to=date_to)
            
            for record in records:
                total_hours = (record.get('hours_worked', 0) or 0) + (record.get('overtime_hours', 0) or 0)
                status_icon = "✅" if record.get('hours_worked', 0) > 0 else "❌"
                
                values = (
                    record['id'],
                    record['employee_name'],
                    record['date'],
                    f"{record.get('hours_worked', 0):.1f}",
                    f"{record.get('overtime_hours', 0):.1f}",
                    f"{total_hours:.1f}",
                    f"{status_icon} {record.get('status', 'Unknown')}",
                    record.get('notes', '')
                )
                self.attendance_tree.insert("", END, values=values)
                
        except Exception as e:
            showerror("❌ Error", f"Failed to refresh attendance: {str(e)}")
    
    # ENHANCED PAYROLL METHODS WITH NOTES
    def apply_payroll_adjustment(self):
        """Enhanced payroll adjustment with comprehensive tracking."""
        try:
            # Validate employee selection
            emp_display = self.adj_employee_var.get()
            if not emp_display:
                showwarning("⚠️ Warning", "Please select an employee")
                return
                
            emp_id = self._employee_map.get(emp_display)
            if not emp_id:
                showerror("❌ Error", "Selected employee not found")
                return
                
            # Validate month/year selection
            try:
                month = int(self.payroll_month_var.get())
                year = int(self.payroll_year_var.get())
                
                if year < datetime.now().year - 2 or year > datetime.now().year + 1:
                    showerror("❌ Error", "Invalid year selected (must be within valid range)")
                    return
                    
                if month < 1 or month > 12:
                    showerror("❌ Error", "Invalid month selected")
                    return
                    
            except ValueError:
                showerror("❌ Error", "Invalid month/year selected")
                return
                
            # Validate bonus/deduction amounts
            try:
                bonus = float(self.bonus_var.get()) if self.bonus_var.get() else 0.0
                deduction = float(self.deduction_var.get()) if self.deduction_var.get().strip() else 0.0
                
                if bonus < 0 or deduction < 0:
                    showerror("❌ Error", "Bonus and deduction must be positive values")
                    return
                    
                if bonus == 0 and deduction == 0:
                    showwarning("⚠️ Warning", "Please enter either a bonus or deduction amount")
                    return
                    
                if bonus > 50000 or deduction > 50000:
                    result = askyesno("⚠️ Large Amount", 
                                               f"The amount seems unusually high.\n\n"
                                               f"Bonus: ${bonus:,.2f}\n"
                                               f"Deduction: ${deduction:,.2f}\n\n"
                                               f"Do you want to continue?")
                    if not result:
                        return
                    
            except ValueError:
                showerror("❌ Error", "Bonus and deduction must be valid numbers")
                return
                
            # Validate notes (mandatory for all adjustments)
            notes = self.adjustment_notes_var.get().strip()
            if not notes:
                showerror("❌ Error", "Notes are required for all adjustments")
                return
                
            if len(notes) < 5:
                showerror("❌ Error", "Please provide more detailed notes (minimum 5 characters)")
                return
                
            # Get or create payroll record
            payroll_records = self.db.get_payroll_records(month=month, year=year)
            existing_record = next((r for r in payroll_records if r['employee_id'] == emp_id), None)
            
            # Get employee data for base salary
            employees = self.db.get_employees(active_only=False)
            employee = next((e for e in employees if e['id'] == emp_id), None)
            
            if not employee:
                showerror("❌ Error", "Employee data not found")
                return
                
            payroll_id = None
            
            # Create payroll record if it doesn't exist
            if not existing_record:
                base_salary = float(employee['base_salary'])
                total_salary = base_salary + bonus - deduction
                
                payroll_data = {
                    'employee_id': emp_id,
                    'month': month,
                    'year': year,
                    'base_salary': base_salary,
                    'bonuses': bonus,
                    'deductions': deduction,
                    'total_salary': total_salary,
                    'payment_date': None,
                    'status': 'pending',
                    'notes': f"Created with adjustment on {datetime.now().strftime('%Y-%m-%d')}:\n{notes}"
                }
                
                payroll_id = self.db.add_payroll_record(payroll_data)
                
                if not payroll_id:
                    showerror("❌ Error", "Failed to create payroll record")
                    return
            else:
                payroll_id = existing_record['id']
                # Update existing payroll record
                success = self.db.update_payroll_with_adjustment(payroll_id, bonus, deduction, notes)
                if not success:
                    showerror("❌ Error", "Failed to update payroll record")
                    return
            
            # Record the adjustment in the adjustments table
            adjustment_data = {
                'payroll_id': payroll_id,
                'employee_id': emp_id,
                'month': month,
                'year': year,
                'bonus': bonus,
                'deduction': deduction,
                'notes': notes,
                'adjusted_by': "Admin",  # In production, use actual logged-in user
                'adjustment_date': datetime.now().isoformat()
            }
            
            adjustment_id = self.db.add_payroll_adjustment(adjustment_data)
            
            if adjustment_id:
                # Show detailed success message
                employee_name = emp_display.split(' (')[0]
                message = f"✅ Payroll adjustment applied successfully!\n\n"
                message += f"Employee: {employee_name}\n"
                message += f"Period: {month_name[month]} {year}\n"
                message += f"Adjustment ID: {adjustment_id}\n\n"
                
                if bonus > 0:
                    message += f"💰 Bonus Added: ${bonus:,.2f}\n"
                if deduction > 0:
                    message += f"💸 Deduction Applied: ${deduction:,.2f}\n"
                    
                message += f"\n📝 Notes: {notes[:100]}{'...' if len(notes) > 100 else ''}\n"
                message += f"🕐 Applied on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
                showinfo("✅ Success", message)
                
                # Reset form
                self.bonus_var.set("0.00")
                self.deduction_var.set("0.00")
                self.adjustment_notes_var.set("")
                
                # Refresh displays
                self.refresh_payroll()
                
                # Ask if user wants to generate adjustment report for employee
                result = askyesno("📊 Generate Report", 
                                           f"Do you want to generate an adjustment report for {employee_name}?\n\n"
                                           f"This report can be used for employee discussion.")
                if result:
                    self.generate_employee_adjustment_report(emp_id, month, year)
                    
            else:
                showerror("❌ Error", "Failed to record adjustment details")
                
        except Exception as e:
            showerror("❌ Error", f"Failed to apply payroll adjustment: {str(e)}")

    def generate_employee_adjustment_report(self, employee_id: int, month: int = None, year: int = None):
        """Generate detailed adjustment report for employee discussion."""
        try:
            # Get employee data
            employees = self.db.get_employees(active_only=False)
            employee = next((e for e in employees if e['id'] == employee_id), None)
            
            if not employee:
                showerror("❌ Error", "Employee not found")
                return
                
            # Get adjustment data
            if month and year:
                adjustments = self.db.get_employee_adjustments(employee_id, month, year)
                period_text = f"{month_name[month]} {year}"
            else:
                # Get all adjustments for current year
                current_year = datetime.now().year
                adjustments = self.db.get_employee_adjustments(employee_id, year=current_year)
                period_text = f"Year {current_year}"
            
            if not adjustments:
                showinfo("ℹ️ Information", f"No adjustments found for {employee['employee_name']} in {period_text}")
                return
                
            # Calculate totals
            total_bonuses = sum(adj.get('bonus', 0) or 0 for adj in adjustments)
            total_deductions = sum(adj.get('deduction', 0) or 0 for adj in adjustments)
            net_adjustment = total_bonuses - total_deductions
            
            # Generate report content
            report_content = self.create_adjustment_report_content(employee, adjustments, period_text, 
                                                                 total_bonuses, total_deductions, net_adjustment)
            
            # Show report in dialog window
            self.show_adjustment_report_dialog(employee['employee_name'], period_text, report_content)
            
        except Exception as e:
            showerror("❌ Error", f"Failed to generate adjustment report: {str(e)}")

    def create_adjustment_report_content(self, employee, adjustments, period_text, total_bonuses, total_deductions, net_adjustment):
        """Create formatted adjustment report content."""
        report = f"""
PAYROLL ADJUSTMENT REPORT
{'=' * 50}

Employee Information:
• Name: {employee['employee_name']}
• Position: {employee['position']}
• Employee ID: {employee['id']}
• Department: {employee.get('department', 'N/A')}

Report Period: {period_text}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{'=' * 50}

ADJUSTMENT SUMMARY:
• Total Bonuses: ${total_bonuses:,.2f}
• Total Deductions: ${total_deductions:,.2f}
• Net Adjustment: ${net_adjustment:,.2f}
• Number of Adjustments: {len(adjustments)}

{'=' * 50}

DETAILED ADJUSTMENT HISTORY:
"""
        
        for i, adj in enumerate(adjustments, 1):
            adj_date = adj.get('adjustment_date', '')
            if adj_date:
                try:
                    adj_date_obj = datetime.fromisoformat(adj_date.replace('Z', '+00:00'))
                    adj_date_formatted = adj_date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    adj_date_formatted = adj_date[:16]  # Fallback formatting
            else:
                adj_date_formatted = 'Unknown'
                
            report += f"""
{i}. Adjustment Date: {adj_date_formatted}
   Period: {month_name[adj.get('month', 1)]} {adj.get('year', '')}
   Adjusted By: {adj.get('adjusted_by', 'Admin')}
   
   Financial Impact:
   • Bonus: ${adj.get('bonus', 0):,.2f}
   • Deduction: ${adj.get('deduction', 0):,.2f}
   • Net Impact: ${(adj.get('bonus', 0) or 0) - (adj.get('deduction', 0) or 0):,.2f}
   
   Reason/Notes:
   {adj.get('notes', 'No notes provided')}
   
   {'-' * 40}
"""
        
        # Add payroll context if available
        if adjustments and adjustments[0].get('base_salary'):
            report += f"""

PAYROLL CONTEXT:
• Base Salary: ${adjustments[0].get('base_salary', 0):,.2f}
• Total Salary (with adjustments): ${adjustments[0].get('total_salary', 0):,.2f}

{'=' * 50}

This report has been generated for discussion purposes and contains
all payroll adjustments made for the specified period.

For questions or clarifications, please contact the HR department.

Report End
{'=' * 50}
"""
        
        return report

    def show_adjustment_report_dialog(self, employee_name, period, report_content):
        """Show adjustment report in a dialog with export functionality."""
        # Create report window
        report_window = CTkToplevel(self.parent)
        report_window.title(f"Adjustment Report - {employee_name}")
        report_window.geometry("900x700")
        report_window.grab_set()
        
        # Main container
        main_frame = CTkFrame(report_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = CTkFrame(main_frame)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        title = CTkLabel(
            header_frame,
            text=f"📊 Adjustment Report - {employee_name}",
            font=CTkFont(size=18, weight="bold")
        )
        title.pack(side="left", padx=15, pady=15)
        
        period_label = CTkLabel(
            header_frame,
            text=f"Period: {period}",
            font=CTkFont(size=14)
        )
        period_label.pack(side="right", padx=15, pady=15)
        
        # Report content
        content_frame = CTkFrame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        report_text = CTkTextbox(
            content_frame,
            font=CTkFont(family="Consolas", size=11),
            wrap="none"
        )
        report_text.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        report_text.insert("1.0", report_content)
        report_text.configure(state="disabled")
        
        # Button frame
        button_frame = CTkFrame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Export buttons
        export_txt_btn = CTkButton(
            button_frame,
            text="💾 Export as Text",
            command=lambda: self.export_adjustment_report(report_content, employee_name, period, "txt"),
            font=CTkFont(size=12, weight="bold"),
            height=35,
            fg_color=("blue", "blue")
        )
        export_txt_btn.grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        
        export_csv_btn = CTkButton(
            button_frame,
            text="📊 Export as CSV",
            command=lambda: self.export_adjustment_report_csv(employee_name, period),
            font=CTkFont(size=12, weight="bold"),
            height=35,
            fg_color=("green", "green")
        )
        export_csv_btn.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        
        print_btn = CTkButton(
            button_frame,
            text="🖨️ Print Report",
            command=lambda: self.print_adjustment_report(report_content),
            font=CTkFont(size=12, weight="bold"),
            height=35,
            fg_color=("purple", "purple")
        )
        print_btn.grid(row=0, column=2, padx=10, pady=15, sticky="ew")

    def export_adjustment_report(self, report_content, employee_name, period, file_format="txt"):
        """Export adjustment report to file."""
        try:
            # Clean employee name for filename
            safe_name = "".join(c for c in employee_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_period = period.replace(' ', '_').replace(',', '')
            
            if file_format.lower() == "txt":
                default_filename = f"Adjustment_Report_{safe_name}_{safe_period}_{datetime.now().strftime('%Y%m%d')}.txt"
                filetypes = [("Text files", "*.txt"), ("All files", "*.*")]
            else:
                default_filename = f"Adjustment_Report_{safe_name}_{safe_period}_{datetime.now().strftime('%Y%m%d')}.pdf"
                filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
            
            file_path = asksaveasfilename(
                defaultextension=f".{file_format}",
                filetypes=filetypes,
                title=f"Export Adjustment Report as {file_format.upper()}",
                initialfile=default_filename
            )
            
            if not file_path:
                return
                
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                f.write(report_content)
                
            showinfo("✅ Export Successful", 
                               f"Adjustment report exported successfully!\n\n"
                               f"File: {file_path}\n"
                               f"Format: {file_format.upper()}")
            
            # Ask if user wants to open the file
            result = askyesno("📂 Open File", "Would you like to open the exported file?")
            if result:
                try:
                    os.startfile(file_path)  # Windows
                except:
                    try:
                        os.system(f"xdg-open '{file_path}'")  # Linux
                    except:
                        try:
                            os.system(f"open '{file_path}'")  # macOS
                        except:
                            pass  # Cannot open file automatically
                            
        except Exception as e:
            showerror("❌ Export Error", f"Failed to export report: {str(e)}")

    def export_adjustment_report_csv(self, employee_name, period):
        """Export adjustment data as CSV for spreadsheet analysis."""
        try:
            # Get employee ID
            emp_id = None
            for display_name, emp_id_val in self._employee_map.items():
                if employee_name in display_name:
                    emp_id = emp_id_val
                    break
                    
            if not emp_id:
                showerror("❌ Error", "Employee not found")
                return
                
            # Get adjustment data
            current_year = datetime.now().year
            adjustments = self.db.get_employee_adjustments(emp_id, year=current_year)
            
            if not adjustments:
                showinfo("ℹ️ Information", "No adjustment data to export")
                return
                
            # Prepare CSV data
            safe_name = "".join(c for c in employee_name if c.isalnum() or c in (' ', '-', '_')).strip()
            default_filename = f"Adjustments_{safe_name}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            file_path = asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Adjustment Data as CSV",
                initialfile=default_filename
            )
            
            if not file_path:
                return
                
            headers = [
                "Date", "Employee", "Month", "Year", "Bonus", "Deduction", 
                "Net Adjustment", "Adjusted By", "Notes", "Base Salary", "Total Salary"
            ]
            
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for adj in adjustments:
                    adj_date = adj.get('adjustment_date', '')
                    if adj_date:
                        try:
                            adj_date_obj = datetime.fromisoformat(adj_date.replace('Z', '+00:00'))
                            formatted_date = adj_date_obj.strftime('%Y-%m-%d %H:%M')
                        except:
                            formatted_date = adj_date[:16]
                    else:
                        formatted_date = 'Unknown'
                        
                    bonus = adj.get('bonus', 0) or 0
                    deduction = adj.get('deduction', 0) or 0
                    net_adjustment = bonus - deduction
                    
                    row = [
                        formatted_date,
                        adj.get('employee_name', ''),
                        adj.get('month', ''),
                        adj.get('year', ''),
                        bonus,
                        deduction,
                        net_adjustment,
                        adj.get('adjusted_by', ''),
                        adj.get('notes', ''),
                        adj.get('base_salary', ''),
                        adj.get('total_salary', '')
                    ]
                    writer.writerow(row)
                    
            showinfo("✅ Export Successful", 
                               f"Adjustment data exported to CSV!\n\n"
                               f"File: {file_path}\n"
                               f"Records: {len(adjustments)}")
                               
        except Exception as e:
            showerror("❌ Export Error", f"Failed to export CSV: {str(e)}")

    def print_adjustment_report(self, report_content):
        """Print adjustment report (opens system print dialog)."""
        try:
            import tempfile
            import subprocess
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(report_content)
                temp_file = f.name
            
            # Try to open with system default application for printing
            try:
                os.startfile(temp_file, "print")  # Windows
            except:
                try:
                    subprocess.run(["lp", temp_file])  # Linux
                except:
                    try:
                        subprocess.run(["lpr", temp_file])  # Alternative Linux
                    except:
                        showinfo("ℹ️ Print", 
                                           f"Please manually print the file:\n{temp_file}")
                        
        except Exception as e:
            showerror("❌ Print Error", f"Failed to print report: {str(e)}")

    def view_all_adjustments(self):
        """View all payroll adjustments across all employees."""
        try:
            # Create adjustments view window
            adj_window = CTkToplevel(self.parent)
            adj_window.title("All Payroll Adjustments")
            adj_window.geometry("1200x800")
            adj_window.grab_set()
            
            # Main container
            main_frame = CTkFrame(adj_window)
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            main_frame.grid_rowconfigure(2, weight=1)
            main_frame.grid_columnconfigure(0, weight=1)
            
            # Header
            header = CTkLabel(
                main_frame,
                text="📊 All Payroll Adjustments",
                font=CTkFont(size=18, weight="bold")
            )
            header.grid(row=0, column=0, pady=(0, 10))
            
            # Filter frame
            filter_frame = CTkFrame(main_frame)
            filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            filter_frame.grid_columnconfigure(4, weight=1)
            
            # Date filters
            CTkLabel(filter_frame, text="From Date:").grid(row=0, column=0, padx=5, pady=10)
            from_date_var = StringVar(value=(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d'))
            from_date_entry = CTkEntry(filter_frame, textvariable=from_date_var, width=120)
            from_date_entry.grid(row=0, column=1, padx=5, pady=10)
            
            CTkLabel(filter_frame, text="To Date:").grid(row=0, column=2, padx=5, pady=10)
            to_date_var = StringVar(value=datetime.now().strftime('%Y-%m-%d'))
            to_date_entry = CTkEntry(filter_frame, textvariable=to_date_var, width=120)
            to_date_entry.grid(row=0, column=3, padx=5, pady=10)
            
            # Employee filter
            CTkLabel(filter_frame, text="Employee:").grid(row=0, column=4, padx=5, pady=10)
            employee_var = StringVar(value="All Employees")
            employee_dropdown = CTkComboBox(
                filter_frame,
                variable=employee_var,
                values=["All Employees"] + sorted(self._employee_map.keys()),
                width=200
            )
            employee_dropdown.grid(row=0, column=5, padx=5, pady=10)
            
            # Filter button
            def apply_filters():
                try:
                    from_date = datetime.strptime(from_date_var.get(), '%Y-%m-%d')
                    to_date = datetime.strptime(to_date_var.get(), '%Y-%m-%d')
                    
                    if from_date > to_date:
                        showerror("❌ Error", "From date cannot be after To date")
                        return
                        
                    selected_employee = employee_var.get()
                    emp_id = None
                    if selected_employee != "All Employees":
                        emp_id = self._employee_map.get(selected_employee)
                    
                    # Get filtered adjustments
                    adjustments = self.db.get_all_adjustments(
                        from_date=from_date,
                        to_date=to_date,
                        employee_id=emp_id
                    )
                    
                    # Update treeview
                    self.update_adjustments_treeview(tree, adjustments)
                    
                except ValueError:
                    showerror("❌ Error", "Invalid date format (use YYYY-MM-DD)")
            
            filter_btn = CTkButton(
                filter_frame,
                text="Apply Filters",
                command=apply_filters,
                width=100
            )
            filter_btn.grid(row=0, column=6, padx=10, pady=10)
            
            # Treeview frame
            tree_frame = CTkFrame(main_frame)
            tree_frame.grid(row=2, column=0, sticky="nsew")
            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)
            
            # Create treeview
            tree = Treeview(
                tree_frame,
                columns=("id", "date", "employee", "period", "bonus", "deduction", "net", "adjusted_by", "notes"),
                show="headings",
                selectmode="browse"
            )
            
            # Configure columns
            tree.heading("id", text="ID")
            tree.heading("date", text="Adjustment Date")
            tree.heading("employee", text="Employee")
            tree.heading("period", text="Pay Period")
            tree.heading("bonus", text="Bonus")
            tree.heading("deduction", text="Deduction")
            tree.heading("net", text="Net")
            tree.heading("adjusted_by", text="Adjusted By")
            tree.heading("notes", text="Notes")
            
            tree.column("id", width=50, anchor="center")
            tree.column("date", width=120, anchor="center")
            tree.column("employee", width=150)
            tree.column("period", width=100, anchor="center")
            tree.column("bonus", width=80, anchor="e")
            tree.column("deduction", width=80, anchor="e")
            tree.column("net", width=80, anchor="e")
            tree.column("adjusted_by", width=100)
            tree.column("notes", width=300)
            
            # Add scrollbars
            vscroll = Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            hscroll = Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky="nsew")
            vscroll.grid(row=0, column=1, sticky="ns")
            hscroll.grid(row=1, column=0, sticky="ew")
            
            # Button frame
            button_frame = CTkFrame(main_frame)
            button_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
            button_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # View details button
            def view_details():
                selected = tree.selection()
                if not selected:
                    showwarning("⚠️ Warning", "Please select an adjustment to view details")
                    return
                    
                item = tree.item(selected[0])
                adj_id = item['values'][0]
                
                # Get full adjustment details
                adjustment = self.db.get_adjustment_details(adj_id)
                if not adjustment:
                    showerror("❌ Error", "Adjustment details not found")
                    return
                
                # Show details dialog
                self.show_adjustment_details(adjustment)
            
            details_btn = CTkButton(
                button_frame,
                text="View Details",
                command=view_details,
                width=150
            )
            details_btn.grid(row=0, column=0, padx=10, pady=10)
            
            # Export button
            def export_adjustments():
                selected = tree.selection()
                if not selected:
                    showwarning("⚠️ Warning", "No adjustments selected for export")
                    return
                    
                items = [tree.item(item)['values'] for item in selected]
                
                # Prepare CSV data
                headers = [
                    "ID", "Adjustment Date", "Employee", "Pay Period", "Bonus", 
                    "Deduction", "Net", "Adjusted By", "Notes"
                ]
                
                file_path = asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Export Selected Adjustments"
                )
                
                if not file_path:
                    return
                    
                try:
                    with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(items)
                        
                    showinfo("✅ Export Successful", 
                                      f"Exported {len(items)} adjustments to:\n{file_path}")
                except Exception as e:
                    showerror("❌ Export Error", f"Failed to export: {str(e)}")
            
            export_btn = CTkButton(
                button_frame,
                text="Export Selected",
                command=export_adjustments,
                width=150
            )
            export_btn.grid(row=0, column=1, padx=10, pady=10)
            
            # Close button
            close_btn = CTkButton(
                button_frame,
                text="Close",
                command=adj_window.destroy,
                width=150,
                fg_color="red"
            )
            close_btn.grid(row=0, column=2, padx=10, pady=10)
            
            # Load initial data (last 90 days)
            initial_adjustments = self.db.get_all_adjustments(
                from_date=datetime.now() - timedelta(days=90),
                to_date=datetime.now()
            )
            self.update_adjustments_treeview(tree, initial_adjustments)
            
        except Exception as e:
            showerror("❌ Error", f"Failed to load adjustments view: {str(e)}")

    def update_adjustments_treeview(self, tree, adjustments):
        """Update the treeview with adjustment data."""
        tree.delete(*tree.get_children())
        
        for adj in adjustments:
            adj_date = adj.get('adjustment_date', '')
            if adj_date:
                try:
                    adj_date_obj = datetime.fromisoformat(adj_date.replace('Z', '+00:00'))
                    formatted_date = adj_date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    formatted_date = adj_date[:16]
            else:
                formatted_date = 'Unknown'
                
            bonus = adj.get('bonus', 0) or 0
            deduction = adj.get('deduction', 0) or 0
            net = bonus - deduction
            
            period = f"{month_name[adj.get('month', 1)]} {adj.get('year', '')}"
            
            tree.insert("", "end", values=(
                adj.get('id', ''),
                formatted_date,
                adj.get('employee_name', ''),
                period,
                f"${bonus:,.2f}",
                f"${deduction:,.2f}",
                f"${net:,.2f}",
                adj.get('adjusted_by', ''),
                (adj.get('notes', '')[:100] + '...') if len(adj.get('notes', '')) > 100 else adj.get('notes', '')
            ))

    def show_adjustment_details(self, adjustment):
        """Show detailed view of a single adjustment."""
        details_window = CTkToplevel(self.parent)
        details_window.title(f"Adjustment Details - ID {adjustment.get('id', '')}")
        details_window.geometry("800x600")
        details_window.grab_set()
        
        # Main frame
        main_frame = CTkFrame(details_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = CTkLabel(
            main_frame,
            text=f"📝 Adjustment Details - ID {adjustment.get('id', '')}",
            font=CTkFont(size=16, weight="bold")
        )
        header.pack(pady=(0, 15))
        
        # Details frame
        details_frame = CTkFrame(main_frame)
        details_frame.pack(fill="x", padx=10, pady=10)
        
        # Employee info
        emp_info = f"{adjustment.get('employee_name', '')} (ID: {adjustment.get('employee_id', '')})"
        CTkLabel(details_frame, text=f"👤 Employee:", font=CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(details_frame, text=emp_info).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Period
        period = f"{month_name[adjustment.get('month', 1)]} {adjustment.get('year', '')}"
        CTkLabel(details_frame, text=f"📅 Pay Period:", font=CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(details_frame, text=period).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Date
        adj_date = adjustment.get('adjustment_date', '')
        if adj_date:
            try:
                adj_date_obj = datetime.fromisoformat(adj_date.replace('Z', '+00:00'))
                formatted_date = adj_date_obj.strftime('%Y-%m-%d %H:%M')
            except:
                formatted_date = adj_date
        else:
            formatted_date = 'Unknown'
            
        CTkLabel(details_frame, text=f"🕒 Adjustment Date:", font=CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(details_frame, text=formatted_date).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Adjusted by
        CTkLabel(details_frame, text=f"👤 Adjusted By:", font=CTkFont(weight="bold")).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(details_frame, text=adjustment.get('adjusted_by', 'Unknown')).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        # Financial frame
        financial_frame = CTkFrame(main_frame)
        financial_frame.pack(fill="x", padx=10, pady=10)
        
        # Bonus
        bonus = adjustment.get('bonus', 0) or 0
        CTkLabel(financial_frame, text="💰 Bonus:", font=CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(financial_frame, text=f"${bonus:,.2f}", font=CTkFont(size=14)).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Deduction
        deduction = adjustment.get('deduction', 0) or 0
        CTkLabel(financial_frame, text="💸 Deduction:", font=CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(financial_frame, text=f"${deduction:,.2f}", font=CTkFont(size=14)).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Net
        net = bonus - deduction
        CTkLabel(financial_frame, text="🧮 Net Adjustment:", font=CTkFont(weight="bold")).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        CTkLabel(financial_frame, text=f"${net:,.2f}", font=CTkFont(size=14, weight="bold")).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Payroll context
        if adjustment.get('base_salary'):
            context_frame = CTkFrame(main_frame)
            context_frame.pack(fill="x", padx=10, pady=10)
            
            CTkLabel(context_frame, text="💼 Payroll Context:", font=CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=5)
            CTkLabel(context_frame, text=f"Base Salary: ${adjustment.get('base_salary', 0):,.2f}").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            CTkLabel(context_frame, text=f"Total Salary: ${adjustment.get('total_salary', 0):,.2f}").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        # Notes frame
        notes_frame = CTkFrame(main_frame)
        notes_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        CTkLabel(notes_frame, text="📝 Notes:", font=CTkFont(weight="bold")).pack(anchor="w", padx=5, pady=5)
        notes_text = CTkTextbox(notes_frame, wrap="word", height=150)
        notes_text.pack(fill="both", expand=True, padx=5, pady=5)
        notes_text.insert("1.0", adjustment.get('notes', 'No notes provided'))
        notes_text.configure(state="disabled")
        
        # Close button
        close_btn = CTkButton(
            main_frame,
            text="Close",
            command=details_window.destroy,
            width=150,
            fg_color="red"
        )
        close_btn.pack(pady=10)

    def process_monthly_payroll(self):
        """Enhanced monthly payroll processing with status tracking."""
        try:
            month = int(self.payroll_month_var.get())
            year = int(self.payroll_year_var.get())
            
            # Validate month/year
            current_date = datetime.now()
            if year < current_date.year - 1 or year > current_date.year + 1:
                showerror("❌ Error", "Invalid year selected (must be within ±1 year)")
                return
                
            if month < 1 or month > 12:
                showerror("❌ Error", "Invalid month selected")
                return
                
            # Check if payroll already processed
            existing = self.db.get_payroll_records(month=month, year=year)
            existing_employee_ids = {p['employee_id'] for p in existing}
            
            # Get active employees
            employees = self.db.get_employees(active_only=True)
            if not employees:
                showwarning("⚠️ Warning", "No active employees found")
                return
                
            created = 0
            for emp in employees:
                if emp['id'] in existing_employee_ids:
                    continue  # skip already processed
                    
                base_salary = float(emp['base_salary'])
                total = base_salary  # default, adjustments can be applied later
                
                payroll_data = {
                    'employee_id': emp['id'],
                    'month': month,
                    'year': year,
                    'base_salary': base_salary,
                    'bonuses': 0,
                    'deductions': 0,
                    'total_salary': total,
                    'payment_date': None,
                    'status': 'pending',
                    'notes': f"Initial payroll processing on {current_date.strftime('%Y-%m-%d')}",
                    'created_at': current_date.isoformat()
                }
                
                self.db.add_payroll_record(payroll_data)
                created += 1
                
            # Show summary
            message_text = f"Payroll processed for {month}/{year}\n\n"
            message_text += f"• Employees processed: {created}\n"
            message_text += f"• Existing records skipped: {len(existing)}\n"
            message_text += f"• Total payroll records: {created + len(existing)}"
            
            showinfo("✅ Payroll Processing Complete", message_text)
            
            # Refresh data
            self.refresh_payroll()
            
        except Exception as e:
            showerror("❌ Error", f"Failed to process payroll: {str(e)}")

    def mark_payroll_paid(self):
        """Mark selected payroll record as paid with payment date."""
        selection = self.payroll_tree.selection()
        if not selection:
            showwarning("⚠️ Warning", "Please select a payroll record to mark as paid")
            return
            
        item = self.payroll_tree.item(selection[0])
        payroll_id = item['values'][0]
        employee_name = item['values'][1]
        month = item['values'][2]
        year = item['values'][3]
        amount = item['values'][7]
        current_status = item['values'][8]
        
        if "paid" in current_status.lower():
            showinfo("ℹ️ Information", f"This payroll record is already marked as paid")
            return
            
        result = askyesno(
            "⚠️ Confirm Payment", 
            f"Mark payroll as paid?\n\nEmployee: {employee_name}\nPeriod: {month}/{year}\nAmount: {amount}\n\nThis will:\n• Update status to 'paid'\n• Record today's date as payment date"
        )
        
        if result:
            try:
                payment_date = date.today().strftime("%Y-%m-%d")
                self.db.execute_query(
                    "UPDATE payroll SET status='paid', payment_date=?, updated_at=? WHERE id=?", 
                    (payment_date, datetime.now().isoformat(), payroll_id)
                )
                
                # Add payment note
                self.db.execute_query(
                    "UPDATE payroll SET notes=CONCAT(COALESCE(notes, ''), ?) WHERE id=?", 
                    (f"\n\nMarked as paid on {payment_date}", payroll_id)
                )
                
                showinfo("✅ Success", f"Payroll marked as paid for {employee_name}")
                self.refresh_payroll()
                
            except Exception as e:
                showerror("❌ Error", f"Failed to mark payroll as paid: {str(e)}")

    def view_payroll_details(self):
        """View detailed payroll information including adjustments."""
        selection = self.payroll_tree.selection()
        if not selection:
            showwarning("⚠️ Warning", "Please select a payroll record to view details")
            return
            
        item = self.payroll_tree.item(selection[0])
        payroll_id = item['values'][0]
        
        try:
            # Get payroll record
            payroll_record = self.db.get_payroll_record_by_id(payroll_id)
            if not payroll_record:
                showerror("❌ Error", "Payroll record not found")
                return
                
            # Get adjustments if any
            adjustments = self.db.get_payroll_adjustments(payroll_id)
            
            # Create detail window
            detail_window = CTkToplevel(self.parent)
            detail_window.title(f"Payroll Details - ID: {payroll_id}")
            detail_window.geometry("800x600")
            detail_window.grab_set()
            
            # Main container
            container = CTkFrame(detail_window)
            container.pack(fill="both", expand=True, padx=20, pady=20)
            container.grid_columnconfigure(0, weight=1)
            container.grid_rowconfigure(1, weight=1)
            
            # Header
            header = CTkFrame(container)
            header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
            
            title = CTkLabel(
                header,
                text=f"💰 Payroll Details - {payroll_record['employee_name']}",
                font=CTkFont(size=18, weight="bold")
            )
            title.pack(side="left", padx=10, pady=10)
            
            # Summary frame
            summary_frame = CTkFrame(container)
            summary_frame.grid(row=1, column=0, sticky="nsew")
            
            # Summary labels
            labels = [
                ("Employee:", payroll_record['employee_name']),
                ("Period:", f"{payroll_record['month']}/{payroll_record['year']}"),
                ("Base Salary:", f"${payroll_record['base_salary']:,.2f}"),
                ("Bonuses:", f"${payroll_record['bonuses']:,.2f}"),
                ("Deductions:", f"${payroll_record['deductions']:,.2f}"),
                ("Total Salary:", f"${payroll_record['total_salary']:,.2f}"),
                ("Status:", payroll_record['status'].capitalize()),
                ("Payment Date:", payroll_record.get('payment_date', 'Not paid')),
                ("Created:", payroll_record.get('created_at', 'N/A')),
                ("Last Updated:", payroll_record.get('updated_at', 'N/A'))
            ]
            
            for i, (label, value) in enumerate(labels):
                lbl = CTkLabel(
                    summary_frame,
                    text=label,
                    font=CTkFont(size=12, weight="bold"),
                    anchor="e"
                )
                lbl.grid(row=i, column=0, padx=5, pady=2, sticky="e")
                
                val = CTkLabel(
                    summary_frame,
                    text=value,
                    font=CTkFont(size=12)
                )
                val.grid(row=i, column=1, padx=5, pady=2, sticky="w")
            
            # Adjustments section if any
            if adjustments:
                adj_frame = CTkFrame(container)
                adj_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
                
                adj_title = CTkLabel(
                    adj_frame,
                    text="📝 Adjustments History",
                    font=CTkFont(size=14, weight="bold")
                )
                adj_title.pack(pady=(5, 10))
                
                for adj in adjustments:
                    adj_text = f"• {adj['adjustment_date'][:10]}: "
                    if adj['bonus'] > 0:
                        adj_text += f"Bonus ${adj['bonus']:.2f} "
                    if adj['deduction'] > 0:
                        adj_text += f"Deduction ${adj['deduction']:.2f} "
                    adj_text += f"(by {adj['adjusted_by']})\n"
                    adj_text += f"   Notes: {adj['notes']}"
                    
                    adj_label = CTkLabel(
                        adj_frame,
                        text=adj_text,
                        font=CTkFont(size=11),
                        justify="left",
                        anchor="w"
                    )
                    adj_label.pack(fill="x", padx=10, pady=2)
            
            # Notes section
            notes_frame = CTkFrame(container)
            notes_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
            
            notes_title = CTkLabel(
                notes_frame,
                text="📄 Notes",
                font=CTkFont(size=14, weight="bold")
            )
            notes_title.pack(pady=(5, 10))
            
            notes_text = CTkTextbox(
                notes_frame,
                height=100,
                font=CTkFont(size=11)
            )
            notes_text.insert("1.0", payroll_record.get('notes', 'No notes available'))
            notes_text.configure(state="disabled")
            notes_text.pack(fill="both", expand=True, padx=10, pady=5)
            
        except Exception as e:
            showerror("❌ Error", f"Failed to load payroll details: {str(e)}")

    def generate_summary_report(self):
        """Generate comprehensive payroll summary report."""
        try:
            # Get current filter values
            month = self.filter_month_var.get()
            year = self.filter_year_var.get()
            
            # Determine date range
            if month and month != "All":
                month = int(month)
                year = int(year)
                date_from = date(year, month, 1)
                last_day = monthrange(year, month)[1]
                date_to = date(year, month, last_day)
                period = f"{month_name[month]} {year}"
            else:
                year = int(year)
                date_from = date(year, 1, 1)
                date_to = date(year, 12, 31)
                period = f"Year {year}"
            
            # Get payroll data
            payroll_data = self.db.get_payroll_records(month=(month if month != "All" else None), year=year)
            
            if not payroll_data:
                showinfo("ℹ️ Information", f"No payroll data found for {period}")
                return
                
            # Calculate totals
            total_payroll = sum(p['total_salary'] for p in payroll_data)
            total_bonuses = sum(p['bonuses'] for p in payroll_data)
            total_deductions = sum(p['deductions'] for p in payroll_data)
            paid_count = sum(1 for p in payroll_data if p['status'].lower() == 'paid')
            
            # Generate report text
            report_text = f"📊 Payroll Summary Report - {period}\n\n"
            report_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            report_text += "="*50 + "\n\n"
            
            report_text += f"• Total Employees: {len(payroll_data)}\n"
            report_text += f"• Paid Employees: {paid_count}\n"
            report_text += f"• Pending Payments: {len(payroll_data) - paid_count}\n"
            report_text += f"• Total Bonuses: ${total_bonuses:,.2f}\n"
            report_text += f"• Total Deductions: ${total_deductions:,.2f}\n"
            report_text += f"• Total Payroll: ${total_payroll:,.2f}\n\n"
            
            report_text += "Employee Breakdown:\n"
            report_text += "-"*50 + "\n"
            
            for emp in sorted(payroll_data, key=lambda x: x['employee_name']):
                report_text += f"\n{emp['employee_name']}:\n"
                report_text += f"  • Base Salary: ${emp['base_salary']:,.2f}\n"
                report_text += f"  • Bonuses: ${emp['bonuses']:,.2f}\n"
                report_text += f"  • Deductions: ${emp['deductions']:,.2f}\n"
                report_text += f"  • Total: ${emp['total_salary']:,.2f}\n"
                report_text += f"  • Status: {emp['status'].capitalize()}\n"
                if emp.get('payment_date'):
                    report_text += f"  • Paid on: {emp['payment_date']}\n"
            
            # Show report in dialog
            report_window = CTkToplevel(self.parent)
            report_window.title(f"Payroll Summary Report - {period}")
            report_window.geometry("900x700")
            
            textbox = CTkTextbox(report_window, font=CTkFont(size=12))
            textbox.pack(fill="both", expand=True, padx=20, pady=20)
            textbox.insert("1.0", report_text)
            textbox.configure(state="disabled")
            
            # Export button
            export_btn = CTkButton(
                report_window,
                text="💾 Export Report",
                command=lambda: self.export_report_text(report_text, f"payroll_report_{period.replace(' ', '_')}"),
                font=CTkFont(size=12, weight="bold"),
                height=35,
                corner_radius=6
            )
            export_btn.pack(pady=10)
            
        except Exception as e:
            showerror("❌ Error", f"Failed to generate report: {str(e)}")

    def export_report_text(self, report_text, default_filename):
        """Export report text to file."""
        try:
            filename = f"{default_filename}_{datetime.now().strftime('%Y%m%d')}.txt"
            path = asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Report As",
                initialfile=filename
            )
            
            if not path:
                return
                
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                f.write(report_text)
                
            showinfo("✅ Success", f"Report exported successfully to:\n{path}")
            
        except Exception as e:
            showerror("❌ Error", f"Failed to export report: {str(e)}")

    # Database helper methods (would be in your database class)
    def get_payroll_record_by_id(self, payroll_id):
        """Get a single payroll record by ID."""
        query = """
            SELECT p.*, e.employee_name 
            FROM payroll p
            JOIN employees e ON p.employee_id = e.id
            WHERE p.id = ?
        """
        return self.db.execute_query(query, (payroll_id,), fetch_one=True)
        
    def get_payroll_adjustments(self, payroll_id):
        """Get all adjustments for a payroll record."""
        query = """
            SELECT * FROM payroll_adjustments
            WHERE payroll_id = ?
            ORDER BY adjustment_date DESC
        """
        return self.db.execute_query(query, (payroll_id,), fetch_all=True)
        
    def get_dashboard_stats(self):
        """Get comprehensive statistics for the dashboard."""
        stats = {}
        
        # Employee stats
        stats['total_employees'] = self.db.execute_query(
            "SELECT COUNT(*) FROM employees", fetch_one=True)[0]
        stats['active_employees'] = self.db.execute_query(
            "SELECT COUNT(*) FROM employees WHERE is_active = 1", fetch_one=True)[0]
        stats['inactive_employees'] = stats['total_employees'] - stats['active_employees']
        
        # Department stats
        dept_stats = self.db.execute_query(
            "SELECT department, COUNT(*) FROM employees GROUP BY department", fetch_all=True)
        stats['department_stats'] = {dept: count for dept, count in dept_stats}
        
        # Salary stats
        salary_stats = self.db.execute_query(
            "SELECT AVG(base_salary), MAX(base_salary), MIN(base_salary) FROM employees WHERE is_active = 1", 
            fetch_one=True)
        stats['avg_salary'] = salary_stats[0] or 0
        stats['max_salary'] = salary_stats[1] or 0
        stats['min_salary'] = salary_stats[2] or 0
        
        # Current month payroll stats
        current_month = datetime.now().month
        current_year = datetime.now().year
        payroll_stats = self.db.execute_query(
            "SELECT SUM(total_salary), COUNT(*) FROM payroll WHERE month = ? AND year = ?", 
            (current_month, current_year), fetch_one=True)
        stats['monthly_payroll'] = payroll_stats[0] or 0
        stats['monthly_payroll_count'] = payroll_stats[1] or 0
        
        # Year-to-date payroll
        ytd_stats = self.db.execute_query(
            "SELECT SUM(total_salary) FROM payroll WHERE year = ?", 
            (current_year,), fetch_one=True)
        stats['ytd_payroll'] = ytd_stats[0] or 0
        
        # Payroll status counts
        status_stats = self.db.execute_query(
            "SELECT status, COUNT(*) FROM payroll GROUP BY status", fetch_all=True)
        stats['pending_payroll'] = sum(count for status, count in status_stats if status.lower() == 'pending')
        stats['paid_payroll'] = sum(count for status, count in status_stats if status.lower() == 'paid')
        
        return stats

    def filter_payroll(self, _=None):
        """Filter payroll records by month and year."""
        try:
            month = self.filter_month_var.get()
            year = self.filter_year_var.get()
            
            if month == "All":
                self.refresh_payroll(year=year)
            else:
                self.refresh_payroll(month=month, year=year)
                
        except Exception as e:
            showerror("❌ Error", f"Failed to filter payroll: {str(e)}")

    def show(self):
        """Show this module in the parent container."""
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.refresh_all_data()
    
    def hide(self):
        """Hide this module."""
        self.main_container.grid_forget()
