import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk
import pandas as pd
import os
from typing import Optional, Dict, Any, List
import numpy as np
from datetime import datetime
import re
import io
import copy
import tempfile
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import scipy.stats as stats

# Set CustomTkinter appearance
ctk.set_appearance_mode("light")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class AdvancedFilter:
    """Class to handle advanced filtering with multiple conditions"""
    def __init__(self):
        self.conditions = []
        self.logic_operators = []  # 'AND', 'OR'
        
    def add_condition(self, column, operator, value, logic_op='AND'):
        """Add a filter condition"""
        self.conditions.append({
            'column': column,
            'operator': operator,
            'value': value
        })
        if len(self.conditions) > 1:
            self.logic_operators.append(logic_op)
    
    def clear_conditions(self):
        """Clear all conditions"""
        self.conditions = []
        self.logic_operators = []
    
    def apply_filters(self, df):
        """Apply all filters to the dataframe"""
        if not self.conditions:
            return df
            
        # Start with all True mask
        final_mask = pd.Series([True] * len(df), index=df.index)
        
        for i, condition in enumerate(self.conditions):
            column = condition['column']
            operator = condition['operator']
            value = condition['value']
            
            # Create mask for this condition
            try:
                mask = self._create_condition_mask(df, column, operator, value)
            except Exception as e:
                print(f"Error in filter mask for {column} {operator}: {e}")
                mask = pd.Series([False] * len(df), index=df.index)
            
            if i == 0:
                final_mask = mask
            else:
                logic_op = self.logic_operators[i-1]
                if logic_op == 'AND':
                    final_mask = final_mask & mask
                else:  # OR
                    final_mask = final_mask | mask
        
        return df[final_mask]
    
    def _create_condition_mask(self, df, column, operator, value):
        """Create a boolean mask for a single condition"""
        col_data = df[column]
        
        try:
            if operator == 'equals':
                return col_data == value
            elif operator == 'not_equals':
                return col_data != value
            elif operator == 'contains':
                return col_data.astype(str).str.contains(str(value), case=False, na=False)
            elif operator == 'not_contains':
                return ~col_data.astype(str).str.contains(str(value), case=False, na=False)
            elif operator == 'starts_with':
                return col_data.astype(str).str.startswith(str(value), na=False)
            elif operator == 'ends_with':
                return col_data.astype(str).str.endswith(str(value), na=False)
            elif operator == 'greater_than':
                return pd.to_numeric(col_data, errors='coerce') > float(value)
            elif operator == 'less_than':
                return pd.to_numeric(col_data, errors='coerce') < float(value)
            elif operator == 'greater_equal':
                return pd.to_numeric(col_data, errors='coerce') >= float(value)
            elif operator == 'less_equal':
                return pd.to_numeric(col_data, errors='coerce') <= float(value)
            elif operator == 'between':
                # value should be a tuple (min, max)
                if isinstance(value, tuple) and len(value) == 2:
                    min_val, max_val = value
                    if float(min_val) > float(max_val):
                        raise ValueError("Min value cannot be greater than max value for 'between' operator.")
                    numeric_col = pd.to_numeric(col_data, errors='coerce')
                    return (numeric_col >= float(min_val)) & (numeric_col <= float(max_val))
            elif operator == 'date_equals':
                return pd.to_datetime(col_data, errors='coerce').dt.date == pd.to_datetime(value).date()
            elif operator == 'date_after':
                return pd.to_datetime(col_data, errors='coerce') > pd.to_datetime(value)
            elif operator == 'date_before':
                return pd.to_datetime(col_data, errors='coerce') < pd.to_datetime(value)
            elif operator == 'date_between':
                # value should be a tuple (start_date, end_date)
                if isinstance(value, tuple) and len(value) == 2:
                    start_date, end_date = value
                    if pd.to_datetime(start_date) > pd.to_datetime(end_date):
                        raise ValueError("Start date cannot be after end date for 'date_between' operator.")
                    date_col = pd.to_datetime(col_data, errors='coerce')
                    return (date_col >= pd.to_datetime(start_date)) & (date_col <= pd.to_datetime(end_date))
            elif operator == 'is_null':
                return col_data.isnull()
            elif operator == 'is_not_null':
                return col_data.notnull()
            elif operator == 'regex':
                return col_data.astype(str).str.contains(str(value), regex=True, case=False, na=False)
        except Exception as e:
            print(f"Error in _create_condition_mask: {e}")
            # If any error occurs, return all False
            return pd.Series([False] * len(df), index=df.index)
        
        return pd.Series([False] * len(df), index=df.index)

class DataAnalysisApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Professional Data Analysis Tool")
        self.root.geometry("1400x900+25+0")
        self.root.minsize(1200, 700)
        
        # Data storage
        self.original_data: Optional[pd.DataFrame] = None
        self.current_data: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.current_file_path: Optional[str] = None
        self.excel_sheets: Dict[str, pd.DataFrame] = {}
        
        # Advanced filtering
        self.advanced_filter = AdvancedFilter()
        
        # Data cleaning report
        self.cleaning_report = DataCleaningReport()
        
        # Chart report
        self.chart_report = ChartReport()
        
        # Outlier operations tracking
        self.outlier_operations = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # File Controls Group
        self.create_file_controls()
        
        # Notebook for tabs
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(20, 0))
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.main_frame, 
            text="Welcome to Professional Data Analysis Tool\n\nClick 'Load File' to get started",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.welcome_label.pack(expand=True)
        
    def create_file_controls(self):
        """Create the file controls section"""
        # File Controls Group Frame
        controls_frame = ctk.CTkFrame(self.main_frame)
        controls_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            controls_frame, 
            text="File Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(15, 10))
        
        # Buttons container
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Load File Button
        self.load_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Load File",
            command=self.load_file,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        )
        self.load_btn.pack(side="left", padx=(0, 10))
        
        # Save Changes Button
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Save Changes",
            command=self.save_changes,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=(0, 10))
        
        # Reset Data Button
        self.reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset Data",
            command=self.reset_data,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            state="disabled"
        )
        self.reset_btn.pack(side="left")
        
        # Sheet selection (initially hidden)
        self.sheet_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        
        self.sheet_label = ctk.CTkLabel(
            self.sheet_frame,
            text="Select Sheet:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.sheet_label.pack(side="left", padx=(0, 10))
        
        self.sheet_dropdown = ctk.CTkOptionMenu(
            self.sheet_frame,
            values=["No sheets available"],
            command=self.on_sheet_change
        )
        self.sheet_dropdown.pack(side="left")
        
    def load_file(self):
        """Load Excel, CSV, or TSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[
                ("All Supported", "*.xlsx;*.xls;*.csv;*.tsv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("TSV files", "*.tsv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            self.current_file_path = file_path
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                self.load_excel_file(file_path)
            elif file_ext == '.csv':
                self.load_csv_file(file_path)
            elif file_ext == '.tsv':
                self.load_tsv_file(file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                return
                
            # Enable buttons
            self.save_btn.configure(state="normal")
            self.reset_btn.configure(state="normal")
            
            # Show welcome message is hidden and show notebook
            self.welcome_label.pack_forget()
            self.notebook.pack(fill="both", expand=True, pady=(20, 0))
            
            # After loading file, update UI
            self.refresh_periodical_breakdown_tab()
            self.refresh_machine_learning_tab()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
            
    def load_excel_file(self, file_path: str):
        """Load Excel file and handle multiple sheets"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            self.excel_sheets = {}
            
            for sheet_name in excel_file.sheet_names:
                self.excel_sheets[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Show sheet selection if multiple sheets
            if len(self.excel_sheets) > 1:
                self.sheet_dropdown.configure(values=list(self.excel_sheets.keys()))
                self.sheet_dropdown.set(list(self.excel_sheets.keys())[0])
                self.sheet_frame.pack(fill="x", padx=20, pady=(0, 15))
            else:
                self.sheet_frame.pack_forget()
            
            # Load first sheet
            first_sheet = list(self.excel_sheets.keys())[0]
            self.load_sheet_data(first_sheet)
            
            # Update dashboard columns
            self.update_dashboard_columns()
            
            # After loading file, update UI
            self.refresh_periodical_breakdown_tab()
            self.refresh_machine_learning_tab()
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
            
    def load_csv_file(self, file_path: str):
        """Load CSV file"""
        try:
            data = pd.read_csv(file_path)
            self.original_data = data.copy()
            self.current_data = data.copy()
            self.sheet_frame.pack_forget()
            self.create_data_view()
            
            # Update dashboard columns
            self.update_dashboard_columns()
            
            # After loading file, update UI
            self.refresh_periodical_breakdown_tab()
            self.refresh_machine_learning_tab()
            
        except Exception as e:
            raise Exception(f"Error reading CSV file: {str(e)}")
            
    def load_tsv_file(self, file_path: str):
        """Load TSV file"""
        try:
            data = pd.read_csv(file_path, sep='\t')
            self.original_data = data.copy()
            self.current_data = data.copy()
            self.sheet_frame.pack_forget()
            self.create_data_view()
            
            # Update dashboard columns
            self.update_dashboard_columns()
            
            # After loading file, update UI
            self.refresh_periodical_breakdown_tab()
            self.refresh_machine_learning_tab()
            
        except Exception as e:
            raise Exception(f"Error reading TSV file: {str(e)}")
            
    def on_sheet_change(self, sheet_name: str):
        """Handle sheet selection change"""
        self.load_sheet_data(sheet_name)
        
    def load_sheet_data(self, sheet_name: str):
        """Load data from specific sheet"""
        if sheet_name in self.excel_sheets:
            self.original_data = self.excel_sheets[sheet_name].copy()
            self.current_data = self.excel_sheets[sheet_name].copy()
            self.create_data_view()  # This recreates all main tabs
            self.update_dashboard_columns()
            # Clear filters and search fields
            if hasattr(self, 'advanced_filter'):
                self.advanced_filter.clear_conditions()
            if hasattr(self, 'quick_search_entry'):
                self.quick_search_entry.delete(0, 'end')
            # Refresh periodical and ML tabs if they exist
            if hasattr(self, 'refresh_periodical_breakdown_tab'):
                self.refresh_periodical_breakdown_tab()
            if hasattr(self, 'refresh_machine_learning_tab'):
                self.refresh_machine_learning_tab()
            # Always select the Data View tab after switching sheets
            if hasattr(self, 'notebook'):
                try:
                    self.notebook.set('Data View')
                except Exception:
                    pass
        
    def create_data_view(self):
        """Create the data view tab and all other main tabs, ensuring no duplicate tabs exist."""
        # Remove existing tabs if they exist
        for tab_name in [
            "Data View", "Data Cleaning", "Dashboard", "Outliers Detection", "Analysis", "Periodical Breakdown", "Machine Learning"
        ]:
            try:
                self.notebook.delete(tab_name)
            except Exception:
                pass
        # Add Data View tab
        self.notebook.add("Data View")
        data_frame = self.notebook.tab("Data View")
        
        # Create main container with grid layout
        main_container = ctk.CTkFrame(data_frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Filter Panel (left side)
        self.create_advanced_filter_panel(main_container)
        
        # Data Table (right side)
        self.create_data_table(main_container)
        
        # Set initial filtered data
        self.filtered_data = self.current_data.copy()
        self.update_table()
        
        # Add Data Cleaning tab
        self.notebook.add("Data Cleaning")
        cleaning_frame = self.notebook.tab("Data Cleaning")
        self.create_data_cleaning_tab(cleaning_frame)
        
        # Add Dashboard tab
        self.notebook.add("Dashboard")
        dashboard_frame = self.notebook.tab("Dashboard")
        self.create_dashboard_tab(dashboard_frame)
        
        # Add Outliers Detection tab
        self.notebook.add("Outliers Detection")
        outlier_frame = self.notebook.tab("Outliers Detection")
        self.create_outliers_detection_tab(outlier_frame)
        
        # Add Analysis tab
        self.notebook.add("Analysis")
        analysis_frame = self.notebook.tab("Analysis")
        self.create_analysis_tab(analysis_frame)
        
        # Add Periodical Breakdown tab only if not already present
        self.periodical_tab = self.notebook.add("Periodical Breakdown")
        self.create_periodical_breakdown_tab(self.periodical_tab)
        # Add Machine Learning tab
        self.ml_tab = self.notebook.add("Machine Learning")
        self.create_machine_learning_tab(self.ml_tab)
        
    def create_advanced_filter_panel(self, parent):
        """Create the advanced filter panel"""
        # Filter frame
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(side="left", fill="y", padx=(0, 10))
        filter_frame.configure(width=400)
        
        # Filter title
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Advanced Filter Panel",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        filter_title.pack(pady=(15, 10))
        
        # Scrollable frame for filter conditions
        self.filter_scroll = ctk.CTkScrollableFrame(filter_frame, height=100)
        self.filter_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Filter conditions container
        self.filter_conditions_frame = ctk.CTkFrame(self.filter_scroll)
        self.filter_conditions_frame.pack(fill="x", pady=(0, 10))
        
        # Active filters label
        self.active_filters_label = ctk.CTkLabel(
            self.filter_conditions_frame,
            text="Active Filters: 0",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.active_filters_label.pack(pady=(10, 5))
        
        # Container for filter condition widgets
        self.filter_widgets_frame = ctk.CTkFrame(self.filter_conditions_frame)
        self.filter_widgets_frame.pack(fill="x", pady=(0, 10))
        
        # Add filter section
        add_filter_frame = ctk.CTkFrame(filter_frame)
        add_filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        add_filter_label = ctk.CTkLabel(
            add_filter_frame,
            text="Add New Filter",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_filter_label.pack(pady=(10, 5))
        
        # Column selection
        column_frame = ctk.CTkFrame(add_filter_frame, fg_color="transparent")
        column_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(column_frame, text="Column:").pack(side="left")
        self.new_filter_column = ctk.CTkOptionMenu(
            column_frame,
            values=list(self.current_data.columns) if self.current_data is not None else [],
            command=self.on_filter_column_change
        )
        self.new_filter_column.pack(side="left", fill="x", expand=True, padx=(10, 0))
        # Type override dropdown
        self.type_override = ctk.CTkOptionMenu(
            column_frame,
            values=["Auto", "Text", "Number", "Date"],
            command=self.on_type_override_change
        )
        self.type_override.set("Auto")
        self.type_override.pack(side="right", padx=(10, 0))
        
        # Operator selection
        operator_frame = ctk.CTkFrame(add_filter_frame, fg_color="transparent")
        operator_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(operator_frame, text="Operator:").pack(side="left")
        self.new_filter_operator = ctk.CTkOptionMenu(
            operator_frame,
            values=["equals", "not_equals", "contains", "not_contains", "starts_with", "ends_with"],
            command=self.on_filter_operator_change
        )
        self.new_filter_operator.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Value input
        value_frame = ctk.CTkFrame(add_filter_frame, fg_color="transparent")
        value_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(value_frame, text="Value:").pack(side="left")
        self.new_filter_value = ctk.CTkEntry(value_frame, placeholder_text="Enter value...")
        self.new_filter_value.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Special inputs for ranges and dates (initially hidden)
        self.create_special_filter_inputs(add_filter_frame)
        
        # Logic operator for multiple conditions
        logic_frame = ctk.CTkFrame(add_filter_frame, fg_color="transparent")
        logic_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(logic_frame, text="Logic:").pack(side="left")
        self.new_filter_logic = ctk.CTkOptionMenu(
            logic_frame,
            values=["AND", "OR"]
        )
        self.new_filter_logic.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Control buttons
        button_frame = ctk.CTkFrame(add_filter_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.add_filter_btn = ctk.CTkButton(
            button_frame,
            text="+ Add Filter",
            command=self.add_filter_condition,
            height=35,
            width=100
        )
        self.add_filter_btn.pack(side="left", padx=(0, 5))
        
        self.apply_filters_btn = ctk.CTkButton(
            button_frame,
            text="Apply Filters",
            command=self.apply_advanced_filters,
            height=35,
            width=100
        )
        self.apply_filters_btn.pack(side="left", padx=(0, 5))
        
        self.clear_all_filters_btn = ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self.clear_all_filters,
            height=35,
            width=100
        )
        self.clear_all_filters_btn.pack(side="left")
        
    def create_special_filter_inputs(self, parent):
        """Create special input widgets for ranges and dates"""
        # Range inputs (for between operator)
        self.range_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        ctk.CTkLabel(self.range_frame, text="Range:").pack(side="left")
        range_inputs = ctk.CTkFrame(self.range_frame, fg_color="transparent")
        range_inputs.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        self.range_min = ctk.CTkEntry(range_inputs, placeholder_text="Min", width=80)
        self.range_min.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(range_inputs, text="to").pack(side="left", padx=(0, 5))
        
        self.range_max = ctk.CTkEntry(range_inputs, placeholder_text="Max", width=80)
        self.range_max.pack(side="left")
        
        # Date inputs
        self.date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        ctk.CTkLabel(self.date_frame, text="Date:").pack(side="left")
        self.date_input = ctk.CTkEntry(self.date_frame, placeholder_text="YYYY-MM-DD")
        self.date_input.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Date range inputs
        self.date_range_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        ctk.CTkLabel(self.date_range_frame, text="Date Range:").pack(side="left")
        date_range_inputs = ctk.CTkFrame(self.date_range_frame, fg_color="transparent")
        date_range_inputs.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        self.date_range_start = ctk.CTkEntry(date_range_inputs, placeholder_text="Start Date", width=100)
        self.date_range_start.pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(date_range_inputs, text="to").pack(side="left", padx=(0, 5))
        
        self.date_range_end = ctk.CTkEntry(date_range_inputs, placeholder_text="End Date", width=100)
        self.date_range_end.pack(side="left")
        
        # Initially hide all special inputs
        self.range_frame.pack_forget()
        self.date_frame.pack_forget()
        self.date_range_frame.pack_forget()
        
    def on_filter_column_change(self, column_name):
        """Handle column selection change for filter"""
        if self.current_data is None or column_name not in self.current_data.columns:
            return
        # Hide all special inputs first
        self.range_frame.pack_forget()
        self.date_frame.pack_forget()
        self.date_range_frame.pack_forget()
        # Determine column type and update operators
        column_data = self.current_data[column_name]
        type_override = self.type_override.get() if hasattr(self, 'type_override') else "Auto"
        is_numeric = pd.api.types.is_numeric_dtype(column_data)
        is_date = pd.api.types.is_datetime64_any_dtype(column_data)
        # Try to detect date columns by parsing a sample
        if not is_date:
            try:
                sample_data = column_data.dropna().head(10)
                parsed_dates = pd.to_datetime(sample_data, errors='coerce')
                if parsed_dates.notna().sum() > len(sample_data) * 0.5:  # If >50% parse as dates
                    is_date = True
            except:
                pass
        # Apply manual override if set
        if type_override == "Number":
            is_numeric = True
            is_date = False
        elif type_override == "Date":
            is_date = True
            is_numeric = False
        elif type_override == "Text":
            is_numeric = False
            is_date = False
        if is_date:
            operators = ["date_equals", "date_after", "date_before", "date_between", "is_null", "is_not_null"]
        elif is_numeric:
            operators = ["equals", "not_equals", "greater_than", "less_than", "greater_equal", "less_equal", "between", "is_null", "is_not_null"]
        else:
            operators = ["equals", "not_equals", "contains", "not_contains", "starts_with", "ends_with", "regex", "is_null", "is_not_null"]
        self.new_filter_operator.configure(values=operators)
        self.new_filter_operator.set(operators[0])
        self.show_appropriate_input(operators[0])
        
    def show_appropriate_input(self, operator):
        """Show appropriate input widget based on operator"""
        # Hide all special inputs first
        self.range_frame.pack_forget()
        self.date_frame.pack_forget()
        self.date_range_frame.pack_forget()
        
        if operator == "between":
            self.range_frame.pack(fill="x", padx=10, pady=(0, 5))
        elif operator in ["date_equals", "date_after", "date_before"]:
            self.date_frame.pack(fill="x", padx=10, pady=(0, 5))
        elif operator == "date_between":
            self.date_range_frame.pack(fill="x", padx=10, pady=(0, 5))
        
    def add_filter_condition(self):
        """Add a new filter condition"""
        column = self.new_filter_column.get()
        operator = self.new_filter_operator.get()
        logic = self.new_filter_logic.get()
        print(f"[DEBUG] Add Filter: column={column}, operator={operator}, logic={logic}")
        # Get the appropriate value based on operator
        value = self.get_filter_value(operator)
        print(f"[DEBUG] Filter value: {value}")
        if not column or column not in self.current_data.columns:
            messagebox.showwarning("Warning", "Please select a valid column")
            print("[DEBUG] Invalid column selected.")
            return
        if operator is None or operator == "":
            messagebox.showwarning("Warning", "Please select a valid operator")
            print("[DEBUG] Invalid operator selected.")
            return
        if value is None and operator not in ["is_null", "is_not_null"]:
            messagebox.showwarning("Warning", "Please enter a valid value")
            print("[DEBUG] Invalid value for filter.")
            return
        # Add condition to advanced filter
        self.advanced_filter.add_condition(column, operator, value, logic)
        print(f"[DEBUG] Filter added: {column} {operator} {value} ({logic})")
        # Update the UI
        self.update_filter_display()
        self.clear_filter_inputs()
        
    def get_filter_value(self, operator):
        """Get the filter value based on operator type"""
        print(f"[DEBUG] get_filter_value called with operator: {operator}")
        if operator == "between":
            min_val = self.range_min.get().strip()
            max_val = self.range_max.get().strip()
            print(f"[DEBUG] between min: {min_val}, max: {max_val}")
            if min_val and max_val:
                try:
                    return (float(min_val), float(max_val))
                except ValueError:
                    print("[DEBUG] Invalid float for between operator")
                    return None
        elif operator in ["date_equals", "date_after", "date_before"]:
            date_val = self.date_input.get().strip()
            print(f"[DEBUG] date input: {date_val}")
            if date_val:
                try:
                    pd.to_datetime(date_val)
                    return date_val
                except:
                    print("[DEBUG] Invalid date input")
                    return None
        elif operator == "date_between":
            start_date = self.date_range_start.get().strip()
            end_date = self.date_range_end.get().strip()
            print(f"[DEBUG] date_between start: {start_date}, end: {end_date}")
            if start_date and end_date:
                try:
                    pd.to_datetime(start_date)
                    pd.to_datetime(end_date)
                    return (start_date, end_date)
                except:
                    print("[DEBUG] Invalid date_between input")
                    return None
        elif operator in ["is_null", "is_not_null"]:
            print("[DEBUG] is_null or is_not_null operator, no value needed")
            return None
        else:
            value = self.new_filter_value.get().strip()
            print(f"[DEBUG] value entry: {value}")
            return value
            
    def clear_filter_inputs(self):
        """Clear all filter input fields"""
        self.new_filter_value.delete(0, 'end')
        self.range_min.delete(0, 'end')
        self.range_max.delete(0, 'end')
        self.date_input.delete(0, 'end')
        self.date_range_start.delete(0, 'end')
        self.date_range_end.delete(0, 'end')
        
    def update_filter_display(self):
        """Update the display of active filters"""
        print(f"[DEBUG] update_filter_display: {len(self.advanced_filter.conditions)} filters")
        # Clear existing filter display widgets
        for widget in self.filter_widgets_frame.winfo_children():
            widget.destroy()
        # Update active filters count
        filter_count = len(self.advanced_filter.conditions)
        self.active_filters_label.configure(text=f"Active Filters: {filter_count}")
        # Display each filter condition
        for i, condition in enumerate(self.advanced_filter.conditions):
            print(f"[DEBUG] Displaying filter {i}: {condition}")
            self.create_filter_display_widget(i, condition)
            
    def create_filter_display_widget(self, index, condition):
        """Create a widget to display a single filter condition"""
        print(f"[DEBUG] create_filter_display_widget: index={index}, condition={condition}")
        filter_widget = ctk.CTkFrame(self.filter_widgets_frame)
        filter_widget.pack(fill="x", pady=(0, 5))
        
        # Logic operator label (except for first condition)
        if index > 0:
            logic_op = self.advanced_filter.logic_operators[index - 1]
            logic_label = ctk.CTkLabel(
                filter_widget,
                text=logic_op,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="blue"
            )
            logic_label.pack(pady=(5, 0))
        
        # Filter description
        value_str = str(condition['value']) if condition['value'] is not None else "NULL"
        if isinstance(condition['value'], tuple):
            value_str = f"{condition['value'][0]} to {condition['value'][1]}"
            
        description = f"{condition['column']} {condition['operator']} {value_str}"
        
        desc_label = ctk.CTkLabel(
            filter_widget,
            text=description,
            font=ctk.CTkFont(size=10),
            wraplength=300
        )
        desc_label.pack(side="left", padx=(10, 0), pady=5)
        
        # Remove button
        remove_btn = ctk.CTkButton(
            filter_widget,
            text="✕",
            command=lambda idx=index: self.remove_filter_condition(idx),
            width=30,
            height=25,
            font=ctk.CTkFont(size=12)
        )
        remove_btn.pack(side="right", padx=(0, 10), pady=5)
        
    def remove_filter_condition(self, index):
        """Remove a filter condition"""
        if 0 <= index < len(self.advanced_filter.conditions):
            # Remove the condition
            self.advanced_filter.conditions.pop(index)
            # Always keep logic_operators in sync: should be len(conditions) - 1
            if len(self.advanced_filter.logic_operators) > 0:
                if index == 0:
                    # Remove the first logic operator if first condition is removed
                    self.advanced_filter.logic_operators.pop(0)
                else:
                    # Remove the logic operator before the removed condition
                    self.advanced_filter.logic_operators.pop(index - 1)
            # Update display
            self.update_filter_display()
            # Auto-apply filters if there are remaining conditions
            if self.advanced_filter.conditions:
                self.apply_advanced_filters()
            else:
                self.clear_all_filters()
                
    def apply_advanced_filters(self):
        """Apply all advanced filters"""
        if self.current_data is None:
            print("[DEBUG] apply_advanced_filters: current_data is None")
            return
        try:
            before_rows = len(self.current_data)
            # Apply filters using the AdvancedFilter class
            self.filtered_data = self.advanced_filter.apply_filters(self.current_data)
            after_rows = len(self.filtered_data)
            print(f"[DEBUG] apply_advanced_filters: rows before={before_rows}, after={after_rows}")
            self.update_table()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {str(e)}")
            
    def clear_all_filters(self):
        """Clear all filters"""
        self.advanced_filter.clear_conditions()
        self.filtered_data = self.current_data.copy()
        self.update_filter_display()
        self.update_table()
        self.clear_filter_inputs()
        
    def create_data_table(self, parent):
        """Create the data table"""
        # Table frame
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(side="right", fill="both", expand=True)
        
        # Table title and controls
        table_header = ctk.CTkFrame(table_frame)
        table_header.pack(fill="x", padx=10, pady=(15, 10))
        
        table_title = ctk.CTkLabel(
            table_header,
            text="Data Table",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        table_title.pack(side="left")
        
        # Table controls
        controls_frame = ctk.CTkFrame(table_header, fg_color="transparent")
        controls_frame.pack(side="right")
        
        # Export filtered data button
        self.export_btn = ctk.CTkButton(
            controls_frame,
            text="📊 Export Filtered",
            command=self.export_filtered_data,
            height=30,
            width=120
        )
        self.export_btn.pack(side="right", padx=(0, 10))
        
        # Quick search
        self.quick_search_entry = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Quick search...",
            width=150
        )
        self.quick_search_entry.pack(side="right", padx=(0, 10))
        self.quick_search_entry.bind('<KeyRelease>', self.on_quick_search)
        
        # Create treeview with scrollbars
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Style for the treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", rowheight=25)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and treeview
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Info label
        self.info_label = ctk.CTkLabel(
            table_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(pady=(0, 10))
        
    def on_quick_search(self, event=None):
        """Handle quick search functionality"""
        search_term = self.quick_search_entry.get().strip()
        # Always start from current_data, apply advanced filters, then quick search
        base_data = self.current_data.copy()
        if self.advanced_filter.conditions:
            try:
                base_data = self.advanced_filter.apply_filters(base_data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to apply advanced filters: {str(e)}")
                base_data = self.current_data.copy()
        if not search_term:
            self.filtered_data = base_data
        else:
            # Apply quick search across all columns
            mask = pd.Series([False] * len(base_data), index=base_data.index)
            for column in base_data.columns:
                try:
                    mask |= base_data[column].astype(str).str.contains(search_term, case=False, na=False)
                except Exception as e:
                    print(f"Quick search error in column {column}: {e}")
            self.filtered_data = base_data[mask]
        self.update_table()
        
    def export_filtered_data(self):
        """Export filtered data to a new file"""
        if self.filtered_data is None or self.filtered_data.empty:
            messagebox.showwarning("Warning", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Filtered Data",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("TSV files", "*.tsv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                self.filtered_data.to_csv(file_path, index=False)
            elif file_ext == '.xlsx':
                self.filtered_data.to_excel(file_path, index=False)
            elif file_ext == '.tsv':
                self.filtered_data.to_csv(file_path, sep='\t', index=False)
            else:
                self.filtered_data.to_csv(file_path, index=False)
                
            messagebox.showinfo("Success", f"Filtered data exported successfully to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
            
    def update_table(self):
        """Update the table with filtered data"""
        if self.filtered_data is None:
            return
            
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Configure columns
        columns = list(self.filtered_data.columns)
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        # Configure column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=80)
            
        # Insert data (limit to first 1000 rows for performance)
        display_data = self.filtered_data.head(1000)
        for index, row in display_data.iterrows():
            values = [str(val) if pd.notna(val) else "" for val in row]
            self.tree.insert("", "end", values=values)
            
        # Update info label
        total_rows = len(self.current_data) if self.current_data is not None else 0
        filtered_rows = len(self.filtered_data)
        displayed_rows = len(display_data)
        
        info_text = f"Showing {displayed_rows} of {filtered_rows} filtered rows (Total: {total_rows})"
        if filtered_rows > 1000:
            info_text += " - Limited to first 1000 rows for performance"
            
        self.info_label.configure(text=info_text)
        
    def save_changes(self):
        """Save changes to the original file"""
        if self.current_data is None or self.current_file_path is None:
            messagebox.showwarning("Warning", "No data to save")
            return
            
        try:
            file_ext = os.path.splitext(self.current_file_path)[1].lower()
            
            if file_ext in ['.xlsx', '.xls']:
                # For Excel files, we need to handle multiple sheets
                if len(self.excel_sheets) > 1:
                    # Update the current sheet data
                    current_sheet = self.sheet_dropdown.get()
                    self.excel_sheets[current_sheet] = self.current_data.copy()
                    
                    # Save all sheets
                    with pd.ExcelWriter(self.current_file_path, engine='openpyxl') as writer:
                        for sheet_name, sheet_data in self.excel_sheets.items():
                            sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    self.current_data.to_excel(self.current_file_path, index=False)
                    
            elif file_ext == '.csv':
                self.current_data.to_csv(self.current_file_path, index=False)
            elif file_ext == '.tsv':
                self.current_data.to_csv(self.current_file_path, sep='\t', index=False)
                
            messagebox.showinfo("Success", "Changes saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")
            
    def reset_data(self):
        """Reset data to original state"""
        if self.original_data is None:
            return
            
        self.current_data = self.original_data.copy()
        self.filtered_data = self.current_data.copy()
        
        # Clear all filters
        self.advanced_filter.clear_conditions()
        self.update_filter_display()
        self.quick_search_entry.delete(0, 'end')
        
        # Update table
        self.update_table()
        
        messagebox.showinfo("Success", "Data reset to original state!")
        
    def on_filter_operator_change(self, operator):
        """Handle operator selection change for filter"""
        print(f"[DEBUG] Operator changed to: {operator}")
        self.show_appropriate_input(operator)
        
    def on_type_override_change(self, type_choice):
        """Handle manual type override for filter column"""
        column = self.new_filter_column.get()
        self.on_filter_column_change(column)
        
    def create_data_cleaning_tab(self, parent):
        """Create the data cleaning tab"""
        # Main container
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="Data Cleaning Tools",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Create scrollable frame for content
        scroll_frame = ctk.CTkScrollableFrame(main_container)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Missing Values Group
        self.create_missing_values_group(scroll_frame)
        
        # Duplicate Rows Group
        self.create_duplicate_rows_group(scroll_frame)
        
        # Report Section
        self.create_report_section(scroll_frame)
        
    def create_missing_values_group(self, parent):
        """Create the missing values group"""
        # Group frame
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", pady=(0, 20))
        
        # Group title
        group_title = ctk.CTkLabel(
            group_frame,
            text="Missing Values",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        group_title.pack(pady=(15, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Detect Missing Values button
        self.detect_missing_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 Detect Missing Values",
            command=self.detect_missing_values,
            height=35,
            width=150
        )
        self.detect_missing_btn.pack(side="left", padx=(0, 10))
        
        # Handle Missing Values button
        self.handle_missing_btn = ctk.CTkButton(
            buttons_frame,
            text="🛠️ Handle Missing Values",
            command=self.show_handle_missing_dialog,
            height=35,
            width=150
        )
        self.handle_missing_btn.pack(side="left")
        
        # Missing values table
        self.create_missing_values_table(group_frame)
        
    def create_missing_values_table(self, parent):
        """Create the missing values table"""
        # Table frame
        table_frame = ctk.CTkFrame(parent)
        table_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Table title
        table_title = ctk.CTkLabel(
            table_frame,
            text="Missing Values Analysis",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        table_title.pack(pady=(10, 5))
        
        # Create treeview for missing values
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Style for the treeview
        try:
            style = ttk.Style()
            style.configure("MissingTreeview", font=("Arial", 10))
            style.configure("MissingTreeview.Heading", font=("Arial", 10, "bold"))
            style.configure("MissingTreeview", rowheight=25)
        except:
            # Fallback to default style if there's an issue
            pass
        
        # Treeview
        try:
            self.missing_tree = ttk.Treeview(tree_frame, style="MissingTreeview")
        except:
            # Fallback to default style
            self.missing_tree = ttk.Treeview(tree_frame)
        
        # Scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.missing_tree.yview)
        self.missing_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # Pack scrollbar and treeview
        v_scrollbar.pack(side="right", fill="y")
        self.missing_tree.pack(side="left", fill="both", expand=True)
        
        # Configure columns
        self.missing_tree["columns"] = ("Column", "Missing Count", "Percentage")
        self.missing_tree["show"] = "headings"
        
        # Configure column headings and widths
        self.missing_tree.heading("Column", text="Column Name")
        self.missing_tree.heading("Missing Count", text="Missing Count")
        self.missing_tree.heading("Percentage", text="Percentage (%)")
        
        self.missing_tree.column("Column", width=200, minwidth=150)
        self.missing_tree.column("Missing Count", width=120, minwidth=100)
        self.missing_tree.column("Percentage", width=120, minwidth=100)
        
    def create_duplicate_rows_group(self, parent):
        """Create the duplicate rows group"""
        # Group frame
        group_frame = ctk.CTkFrame(parent)
        group_frame.pack(fill="x", pady=(0, 20))
        
        # Group title
        group_title = ctk.CTkLabel(
            group_frame,
            text="Duplicate Rows",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        group_title.pack(pady=(15, 10))
        
        # Info label
        self.duplicate_info_label = ctk.CTkLabel(
            group_frame,
            text="Click 'Detect Duplicates' to analyze duplicate rows",
            font=ctk.CTkFont(size=12)
        )
        self.duplicate_info_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(group_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Detect Duplicates button
        self.detect_duplicates_btn = ctk.CTkButton(
            buttons_frame,
            text="🔍 Detect Duplicates",
            command=self.detect_duplicates,
            height=35,
            width=150
        )
        self.detect_duplicates_btn.pack(side="left", padx=(0, 10))
        
        # Remove Duplicates button
        self.remove_duplicates_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Remove Duplicates",
            command=self.remove_duplicates,
            height=35,
            width=150
        )
        self.remove_duplicates_btn.pack(side="left")
        
    def create_report_section(self, parent):
        """Create the report section"""
        # Report frame
        report_frame = ctk.CTkFrame(parent)
        report_frame.pack(fill="x", pady=(0, 20))
        
        # Report title
        report_title = ctk.CTkLabel(
            report_frame,
            text="Cleaning Report",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        report_title.pack(pady=(15, 10))
        
        # Report text area
        self.report_text = ctk.CTkTextbox(report_frame, height=200)
        self.report_text.pack(fill="x", padx=20, pady=(0, 10))
        
        # Buttons frame
        report_buttons_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        report_buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Clear Report button
        self.clear_report_btn = ctk.CTkButton(
            report_buttons_frame,
            text="🗑️ Clear Report",
            command=self.clear_cleaning_report,
            height=35,
            width=120
        )
        self.clear_report_btn.pack(side="left", padx=(0, 10))
        
        # Round Numeric Values button
        self.round_numeric_btn = ctk.CTkButton(
            report_buttons_frame,
            text="🔢 Round Numeric",
            command=self.round_numeric_values,
            height=35,
            width=120
        )
        self.round_numeric_btn.pack(side="left", padx=(0, 10))
        
        # Export Report button
        self.export_report_btn = ctk.CTkButton(
            report_buttons_frame,
            text="📄 Export PDF",
            command=self.export_cleaning_report,
            height=35,
            width=120
        )
        self.export_report_btn.pack(side="left")
        
        # Update report display
        self.update_cleaning_report_display()
        
    def detect_missing_values(self):
        """Detect missing values in the dataset"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        # Check if missing tree exists
        if not hasattr(self, 'missing_tree') or self.missing_tree is None:
            messagebox.showwarning("Warning", "Missing values table not initialized. Please load data first.")
            return
            
        try:
            # Clear existing data
            for item in self.missing_tree.get_children():
                self.missing_tree.delete(item)
                
            # Calculate missing values
            missing_data = []
            total_rows = len(self.current_data)
            
            for column in self.current_data.columns:
                missing_count = self.current_data[column].isnull().sum()
                if missing_count > 0:
                    percentage = (missing_count / total_rows) * 100
                    missing_data.append({
                        'column': column,
                        'count': missing_count,
                        'percentage': percentage
                    })
                    
            # Sort by percentage descending
            missing_data.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Insert data into table
            for item in missing_data:
                self.missing_tree.insert("", "end", values=(
                    item['column'],
                    item['count'],
                    f"{item['percentage']:.2f}%"
                ))
                
            # Record operation
            self.cleaning_report.add_operation(
                "Missing Values Detection",
                {
                    "total_columns_checked": len(self.current_data.columns),
                    "columns_with_missing": len(missing_data),
                    "total_rows": total_rows
                }
            )
            
            # Update report display
            self.update_cleaning_report_display()
            
            if missing_data:
                messagebox.showinfo("Success", f"Found missing values in {len(missing_data)} columns")
            else:
                messagebox.showinfo("Success", "No missing values found in the dataset")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect missing values: {str(e)}")
            
    def show_handle_missing_dialog(self):
        """Show dialog to handle missing values"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        if not hasattr(self, 'cleaning_report') or self.cleaning_report is None:
            messagebox.showwarning("Warning", "Cleaning report not initialized. Please load data first.")
            return
            
        # Create dialog window
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Handle Missing Values")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Handle Missing Values",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Column selection
        column_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        column_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(column_frame, text="Select Column:").pack(side="left")
        column_dropdown = ctk.CTkOptionMenu(
            column_frame,
            values=list(self.current_data.columns)
        )
        column_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Method selection
        method_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        method_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(method_frame, text="Method:").pack(side="left")
        method_dropdown = ctk.CTkOptionMenu(
            method_frame,
            values=["Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode", "Fill with Zero", "KNN Impute", "Forward Fill", "Backward Fill"]
        )
        method_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # KNN parameters (initially hidden)
        knn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        
        ctk.CTkLabel(knn_frame, text="KNN Neighbors:").pack(side="left")
        knn_neighbors = ctk.CTkEntry(knn_frame, placeholder_text="5")
        knn_neighbors.pack(side="right", fill="x", expand=True, padx=(10, 0))
        knn_neighbors.insert(0, "5")
        
        def on_method_change(method):
            if method == "KNN Impute":
                knn_frame.pack(fill="x", pady=(0, 10))
            else:
                knn_frame.pack_forget()
                
        method_dropdown.configure(command=on_method_change)
        
        # Apply button
        def apply_handling():
            column = column_dropdown.get()
            method = method_dropdown.get()
            
            if not column:
                messagebox.showwarning("Warning", "Please select a column")
                return
                
            try:
                self.handle_missing_values(column, method, knn_neighbors.get() if method == "KNN Impute" else None)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to handle missing values: {str(e)}")
                
        apply_btn = ctk.CTkButton(
            main_frame,
            text="Apply",
            command=apply_handling,
            height=35
        )
        apply_btn.pack(pady=20)
        
    def handle_missing_values(self, column: str, method: str, knn_neighbors: str = None):
        """Handle missing values in a specific column"""
        if self.current_data is None or column not in self.current_data.columns:
            return
            
        original_missing = self.current_data[column].isnull().sum()
        
        try:
            if method == "Drop Rows":
                self.current_data = self.current_data.dropna(subset=[column])
                
            elif method == "Fill with Mean":
                if pd.api.types.is_numeric_dtype(self.current_data[column]):
                    mean_value = self.current_data[column].mean()
                    self.current_data[column].fillna(mean_value, inplace=True)
                else:
                    raise ValueError("Cannot calculate mean for non-numeric column")
                    
            elif method == "Fill with Median":
                if pd.api.types.is_numeric_dtype(self.current_data[column]):
                    median_value = self.current_data[column].median()
                    self.current_data[column].fillna(median_value, inplace=True)
                else:
                    raise ValueError("Cannot calculate median for non-numeric column")
                    
            elif method == "Fill with Mode":
                mode_value = self.current_data[column].mode()
                if not mode_value.empty:
                    self.current_data[column].fillna(mode_value.iloc[0], inplace=True)
                else:
                    raise ValueError("No mode found for this column")
                    
            elif method == "Fill with Zero":
                if pd.api.types.is_numeric_dtype(self.current_data[column]):
                    self.current_data[column].fillna(0, inplace=True)
                else:
                    raise ValueError("Cannot fill with zero for non-numeric column")
                    
            elif method == "KNN Impute":
                if not pd.api.types.is_numeric_dtype(self.current_data[column]):
                    raise ValueError("KNN imputation only works with numeric columns")
                    
                # Get numeric columns for KNN
                numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
                if column not in numeric_columns:
                    raise ValueError("Selected column is not numeric")
                    
                # Prepare data for KNN
                knn_data = self.current_data[numeric_columns].copy()
                
                # Scale the data
                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(knn_data)
                
                # Apply KNN imputation
                n_neighbors = int(knn_neighbors) if knn_neighbors else 5
                imputer = KNNImputer(n_neighbors=n_neighbors)
                imputed_data = imputer.fit_transform(scaled_data)
                
                # Inverse transform to get original scale
                imputed_data = scaler.inverse_transform(imputed_data)
                
                # Update the column
                self.current_data[column] = imputed_data[:, numeric_columns.index(column)]
                
            elif method == "Forward Fill":
                self.current_data[column].fillna(method='ffill', inplace=True)
                
            elif method == "Backward Fill":
                self.current_data[column].fillna(method='bfill', inplace=True)
                
            # Update filtered data
            self.filtered_data = self.current_data.copy()
            self.update_table()
            
            # Record operation
            self.cleaning_report.add_operation(
                "Missing Values Handling",
                {
                    "column": column,
                    "method": method,
                    "missing_values_handled": original_missing,
                    "knn_neighbors": knn_neighbors if method == "KNN Impute" else None
                }
            )
            
            # Update report display
            self.update_cleaning_report_display()
            
            messagebox.showinfo("Success", f"Successfully handled missing values in column '{column}' using {method}")
            
        except Exception as e:
            raise Exception(f"Failed to handle missing values: {str(e)}")
            
    def detect_duplicates(self):
        """Detect duplicate rows in the dataset"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        if not hasattr(self, 'duplicate_info_label') or self.duplicate_info_label is None:
            messagebox.showwarning("Warning", "Duplicate info label not initialized. Please load data first.")
            return
            
        try:
            # Find duplicate rows
            duplicates = self.current_data.duplicated()
            duplicate_count = duplicates.sum()
            total_rows = len(self.current_data)
            
            # Update info label
            if duplicate_count > 0:
                percentage = (duplicate_count / total_rows) * 100
                self.duplicate_info_label.configure(
                    text=f"Found {duplicate_count} duplicate rows ({percentage:.2f}% of total data)"
                )
            else:
                self.duplicate_info_label.configure(text="No duplicate rows found")
                
            # Record operation
            self.cleaning_report.add_operation(
                "Duplicate Detection",
                {
                    "total_rows": total_rows,
                    "duplicate_rows": duplicate_count,
                    "duplicate_percentage": f"{(duplicate_count / total_rows) * 100:.2f}%" if duplicate_count > 0 else "0%"
                }
            )
            
            # Update report display
            self.update_cleaning_report_display()
            
            if duplicate_count > 0:
                messagebox.showinfo("Success", f"Found {duplicate_count} duplicate rows")
            else:
                messagebox.showinfo("Success", "No duplicate rows found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect duplicates: {str(e)}")
            
    def remove_duplicates(self):
        """Remove duplicate rows from the dataset"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        if not hasattr(self, 'duplicate_info_label') or self.duplicate_info_label is None:
            messagebox.showwarning("Warning", "Duplicate info label not initialized. Please load data first.")
            return
            
        try:
            # Count duplicates before removal
            duplicates = self.current_data.duplicated()
            duplicate_count = duplicates.sum()
            original_rows = len(self.current_data)
            
            if duplicate_count == 0:
                messagebox.showinfo("Info", "No duplicate rows to remove")
                return
                
            # Remove duplicates
            self.current_data = self.current_data.drop_duplicates()
            new_rows = len(self.current_data)
            removed_rows = original_rows - new_rows
            
            # Update filtered data
            self.filtered_data = self.current_data.copy()
            self.update_table()
            
            # Update duplicate info
            self.duplicate_info_label.configure(text="No duplicate rows found")
            
            # Record operation
            self.cleaning_report.add_operation(
                "Duplicate Removal",
                {
                    "original_rows": original_rows,
                    "duplicate_rows_removed": removed_rows,
                    "remaining_rows": new_rows
                }
            )
            
            # Update report display
            self.update_cleaning_report_display()
            
            messagebox.showinfo("Success", f"Removed {removed_rows} duplicate rows")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove duplicates: {str(e)}")
            
    def update_cleaning_report_display(self):
        """Update the cleaning report display"""
        if hasattr(self, 'report_text') and self.report_text is not None:
            try:
                report_summary = self.cleaning_report.get_report_summary()
                self.report_text.delete("1.0", "end")
                self.report_text.insert("1.0", report_summary)
            except Exception as e:
                print(f"Error updating cleaning report display: {e}")
            
    def clear_cleaning_report(self):
        """Clear the cleaning report"""
        self.cleaning_report.clear_operations()
        self.update_cleaning_report_display()
        messagebox.showinfo("Success", "Cleaning report cleared")
        
    def round_numeric_values(self):
        """Round numeric values to 2 decimal places"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        try:
            # Get numeric columns
            numeric_columns = self.current_data.select_dtypes(include=[np.number]).columns.tolist()
            
            if not numeric_columns:
                messagebox.showinfo("Info", "No numeric columns found in the dataset")
                return
                
            # Count original values for reporting
            original_values_count = 0
            for col in numeric_columns:
                original_values_count += self.current_data[col].notna().sum()
                
            # Round numeric values to 2 decimal places
            for column in numeric_columns:
                self.current_data[column] = self.current_data[column].round(2)
                
            # Update filtered data
            self.filtered_data = self.current_data.copy()
            self.update_table()
            
            # Record operation
            self.cleaning_report.add_operation(
                "Numeric Values Rounding",
                {
                    "numeric_columns_rounded": len(numeric_columns),
                    "columns_affected": numeric_columns,
                    "values_rounded": original_values_count,
                    "decimal_places": 2
                }
            )
            
            # Update report display
            self.update_cleaning_report_display()
            
            messagebox.showinfo("Success", f"Rounded {len(numeric_columns)} numeric columns to 2 decimal places")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to round numeric values: {str(e)}")
            
    def export_cleaning_report(self):
        """Export the cleaning report to a PDF file"""
        if not self.cleaning_report.operations:
            messagebox.showwarning("Warning", "No cleaning operations to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Cleaning Report",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20
            )
            normal_style = styles['Normal']
            
            # Title
            title = Paragraph("Data Cleaning Report", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Summary
            summary_heading = Paragraph("Report Summary", heading_style)
            story.append(summary_heading)
            
            # Create summary table
            summary_data = [
                ["Total Operations", str(len(self.cleaning_report.operations))],
                ["Total Charts", str(len(self.chart_report.charts))],
                ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            if self.current_data is not None:
                summary_data.extend([
                    ["Total Rows", str(len(self.current_data))],
                    ["Total Columns", str(len(self.current_data.columns))]
                ])
                
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Operations details
            operations_heading = Paragraph("Cleaning Operations Details", heading_style)
            story.append(operations_heading)
            
            for i, operation in enumerate(self.cleaning_report.operations, 1):
                # Operation title
                op_title = Paragraph(f"{i}. {operation['operation_type']}", heading_style)
                story.append(op_title)
                
                # Operation details
                details_text = ""
                for key, value in operation['details'].items():
                    if value is not None:
                        details_text += f"• {key}: {value}<br/>"
                
                if details_text:
                    details_para = Paragraph(details_text, normal_style)
                    story.append(details_para)
                    
                story.append(Spacer(1, 12))
                
            # Charts details
            if self.chart_report.charts:
                charts_heading = Paragraph("Dashboard Charts Details", heading_style)
                story.append(charts_heading)
                
                for i, chart in enumerate(self.chart_report.charts, 1):
                    # Chart title
                    chart_title = Paragraph(f"{i}. {chart['chart_type']} Chart", heading_style)
                    story.append(chart_title)
                    
                    # Chart details
                    chart_text = f"• X Column: {chart['x_column']}<br/>"
                    if chart['y_column'] and chart['y_column'] != "No columns available":
                        chart_text += f"• Y Column: {chart['y_column']}<br/>"
                    chart_text += f"• Description: {chart['description']}<br/>"
                    
                    chart_para = Paragraph(chart_text, normal_style)
                    story.append(chart_para)
                    
                    story.append(Spacer(1, 12))
                
            # Build PDF
            doc.build(story)
            
            messagebox.showinfo("Success", f"Cleaning report exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF report: {str(e)}")
        
    def create_dashboard_tab(self, parent):
        """Create the dashboard tab"""
        # Main container
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="Data Visualization Dashboard",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Create main layout with two columns
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Left side - Chart Settings
        self.create_chart_settings_panel(content_frame)
        
        # Right side - Chart Display
        self.create_chart_display_panel(content_frame)
        
    def create_chart_settings_panel(self, parent):
        """Create the chart settings panel"""
        # Settings frame
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.pack(side="left", fill="y", padx=(0, 10))
        settings_frame.configure(width=350)
        
        # Chart Settings Group
        chart_settings_group = ctk.CTkFrame(settings_frame)
        chart_settings_group.pack(fill="x", pady=(0, 20))
        
        # Group title
        group_title = ctk.CTkLabel(
            chart_settings_group,
            text="Chart Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        group_title.pack(pady=(15, 15))
        
        # Chart Type selection
        chart_type_frame = ctk.CTkFrame(chart_settings_group, fg_color="transparent")
        chart_type_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(chart_type_frame, text="Chart Type:").pack(side="left")
        self.chart_type_dropdown = ctk.CTkOptionMenu(
            chart_type_frame,
            values=["Histogram", "Bar", "Line", "Scatter", "Pie", "Box Plot", "Distribution"],
            command=self.on_chart_type_change
        )
        self.chart_type_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # X Column selection
        x_column_frame = ctk.CTkFrame(chart_settings_group, fg_color="transparent")
        x_column_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(x_column_frame, text="X Column:").pack(side="left")
        self.x_column_dropdown = ctk.CTkOptionMenu(
            x_column_frame,
            values=["No columns available"]
        )
        self.x_column_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Y Column selection
        y_column_frame = ctk.CTkFrame(chart_settings_group, fg_color="transparent")
        y_column_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(y_column_frame, text="Y Column:").pack(side="left")
        self.y_column_dropdown = ctk.CTkOptionMenu(
            y_column_frame,
            values=["No columns available"]
        )
        self.y_column_dropdown.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Generate Chart button
        self.generate_chart_btn = ctk.CTkButton(
            chart_settings_group,
            text="📊 Generate Chart",
            command=self.generate_chart,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.generate_chart_btn.pack(pady=(0, 15))
        
        # Save Chart Group
        save_chart_group = ctk.CTkFrame(settings_frame)
        save_chart_group.pack(fill="x")
        
        # Save group title
        save_group_title = ctk.CTkLabel(
            save_chart_group,
            text="Save Chart",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        save_group_title.pack(pady=(15, 10))
        
        # Chart Description
        description_frame = ctk.CTkFrame(save_chart_group, fg_color="transparent")
        description_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(description_frame, text="Chart Description:").pack(anchor="w")
        self.chart_description_entry = ctk.CTkEntry(
            description_frame,
            placeholder_text="Enter chart description..."
        )
        self.chart_description_entry.pack(fill="x", pady=(5, 0))
        
        # Save Chart button
        self.save_chart_btn = ctk.CTkButton(
            save_chart_group,
            text="💾 Save Chart",
            command=self.save_chart,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_chart_btn.pack(pady=(10, 10))
        
        # Export Charts PDF button
        self.export_charts_pdf_btn = ctk.CTkButton(
            save_chart_group,
            text="📄 Export Charts PDF",
            command=self.export_charts_pdf,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.export_charts_pdf_btn.pack(pady=(0, 15))
        
    def create_chart_display_panel(self, parent):
        """Create the chart display panel"""
        # Display frame
        display_frame = ctk.CTkFrame(parent)
        display_frame.pack(side="right", fill="both", expand=True)
        
        # Chart title
        self.chart_title_label = ctk.CTkLabel(
            display_frame,
            text="Chart will appear here",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.chart_title_label.pack(pady=(15, 10))
        
        # Chart canvas frame
        self.chart_canvas_frame = ctk.CTkFrame(display_frame)
        self.chart_canvas_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Initialize chart variables
        self.current_chart_figure = None
        self.current_chart_canvas = None
        
    def update_dashboard_columns(self):
        """Update column dropdowns when data is loaded"""
        if self.current_data is not None:
            # Trigger chart type change to set appropriate columns
            current_chart_type = self.chart_type_dropdown.get()
            self.on_chart_type_change(current_chart_type)
        else:
            self.x_column_dropdown.configure(values=["No columns available"])
            self.y_column_dropdown.configure(values=["No columns available"])
            
    def generate_chart(self):
        """Generate chart based on selected settings"""
        import matplotlib.pyplot as plt
        import seaborn as sns
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
        
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded")
            return
            
        chart_type = self.chart_type_dropdown.get()
        x_column = self.x_column_dropdown.get()
        y_column = self.y_column_dropdown.get()
        
        # Handle placeholder values for Y column
        placeholder_values = ["Not needed for this chart type", "Not needed (count plot)", "No columns available"]
        if y_column in placeholder_values:
            y_column = None
        
        if not x_column or x_column == "No columns available":
            messagebox.showwarning("Warning", "Please select X column")
            return
            
        # Validate chart type and column compatibility
        validation_error = self.validate_chart_columns(chart_type, x_column, y_column)
        if validation_error:
            messagebox.showerror("Chart Validation Error", validation_error)
            return
            
        try:
            # Clear previous chart
            if self.current_chart_canvas:
                self.current_chart_canvas.get_tk_widget().destroy()
                self.current_chart_canvas = None
                
            # Clear any existing widgets in the canvas frame
            for widget in self.chart_canvas_frame.winfo_children():
                widget.destroy()
                
            # Create new figure with interactive backend
            plt.ion()  # Turn on interactive mode
            self.current_chart_figure, ax = plt.subplots(figsize=(10, 6))
            
            # Generate chart based on type
            if chart_type == "Histogram":
                if pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                    ax.hist(self.current_data[x_column].dropna(), bins=20, edgecolor='black')
                    ax.set_xlabel(x_column)
                    ax.set_ylabel('Frequency')
                    ax.set_title(f'Histogram of {x_column}')
                else:
                    raise ValueError("Histogram requires numeric data")
                    
            elif chart_type == "Bar":
                if y_column is not None:
                    if pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                        data = self.current_data.groupby(x_column)[y_column].mean()
                        data.plot(kind='bar', ax=ax)
                        ax.set_xlabel(x_column)
                        ax.set_ylabel(f'Average {y_column}')
                        ax.set_title(f'Bar Chart: {x_column} vs Average {y_column}')
                        plt.xticks(rotation=45)
                    else:
                        raise ValueError("Y column must be numeric for bar chart")
                else:
                    # Count plot
                    value_counts = self.current_data[x_column].value_counts()
                    value_counts.plot(kind='bar', ax=ax)
                    ax.set_xlabel(x_column)
                    ax.set_ylabel('Count')
                    ax.set_title(f'Bar Chart: Count of {x_column}')
                    plt.xticks(rotation=45)
                    
            elif chart_type == "Line":
                if y_column is not None:
                    if pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                        data = self.current_data.groupby(x_column)[y_column].mean()
                        data.plot(kind='line', ax=ax, marker='o')
                        ax.set_xlabel(x_column)
                        ax.set_ylabel(f'Average {y_column}')
                        ax.set_title(f'Line Chart: {x_column} vs Average {y_column}')
                        plt.xticks(rotation=45)
                    else:
                        raise ValueError("Y column must be numeric for line chart")
                else:
                    raise ValueError("Line chart requires Y column")
                    
            elif chart_type == "Scatter":
                if y_column is not None:
                    if (pd.api.types.is_numeric_dtype(self.current_data[x_column]) and 
                        pd.api.types.is_numeric_dtype(self.current_data[y_column])):
                        ax.scatter(self.current_data[x_column], self.current_data[y_column], alpha=0.6)
                        ax.set_xlabel(x_column)
                        ax.set_ylabel(y_column)
                        ax.set_title(f'Scatter Plot: {x_column} vs {y_column}')
                    else:
                        raise ValueError("Both X and Y columns must be numeric for scatter plot")
                else:
                    raise ValueError("Scatter plot requires Y column")
                    
            elif chart_type == "Pie":
                value_counts = self.current_data[x_column].value_counts()
                ax.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
                ax.set_title(f'Pie Chart: Distribution of {x_column}')
                
            elif chart_type == "Box Plot":
                if y_column is not None:
                    if pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                        self.current_data.boxplot(column=y_column, by=x_column, ax=ax)
                        ax.set_xlabel(x_column)
                        ax.set_ylabel(y_column)
                        ax.set_title(f'Box Plot: {y_column} by {x_column}')
                        plt.xticks(rotation=45)
                    else:
                        raise ValueError("Y column must be numeric for box plot")
                else:
                    raise ValueError("Box plot requires Y column")
                    
            elif chart_type == "Distribution":
                if pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                    # Create a more comprehensive distribution plot with KDE
                    sns.histplot(data=self.current_data, x=x_column, kde=True, stat='density', ax=ax, alpha=0.7)
                    ax.set_xlabel(x_column)
                    ax.set_ylabel('Density')
                    ax.set_title(f'Distribution Plot of {x_column} with KDE')
                    
                    # Add additional statistics
                    mean_val = self.current_data[x_column].mean()
                    median_val = self.current_data[x_column].median()
                    std_val = self.current_data[x_column].std()
                    
                    # Add text box with statistics
                    stats_text = f'Mean: {mean_val:.2f}\nMedian: {median_val:.2f}\nStd: {std_val:.2f}'
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                else:
                    raise ValueError("Distribution plot requires numeric data")
                    
            # Adjust layout
            plt.tight_layout()
            
            # Create canvas and display chart
            self.current_chart_canvas = FigureCanvasTkAgg(self.current_chart_figure, self.chart_canvas_frame)
            self.current_chart_canvas.draw()
            self.current_chart_canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Add interactive features
            toolbar = NavigationToolbar2Tk(self.current_chart_canvas, self.chart_canvas_frame)
            toolbar.update()
            toolbar.pack(side="bottom", fill="x")
            
            # Ensure the figure is properly configured for saving
            self.current_chart_figure.tight_layout()
            self.current_chart_figure.canvas.draw()
            
            # Update chart title
            self.chart_title_label.configure(text=f"Chart: {chart_type} - {x_column}" + (f" vs {y_column}" if y_column is not None else ""))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate chart: {str(e)}")
            
    def validate_chart_columns(self, chart_type: str, x_column: str, y_column: str) -> str:
        """Validate chart type and column compatibility"""
        if not x_column or x_column == "No columns available":
            return "Please select a valid X column"
            
        # Check if columns exist in data
        if x_column not in self.current_data.columns:
            return f"Column '{x_column}' not found in dataset"
            
        # Handle placeholder values for Y column
        placeholder_values = ["Not needed for this chart type", "Not needed (count plot)", "No columns available"]
        if y_column and y_column not in placeholder_values and y_column not in self.current_data.columns:
            return f"Column '{y_column}' not found in dataset"
            
        # Chart-specific validations
        if chart_type == "Histogram":
            if not pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                return f"Histogram requires numeric data. Column '{x_column}' is not numeric."
                
        elif chart_type == "Bar":
            # Bar charts can work with both numeric and categorical data
            pass
            
        elif chart_type == "Line":
            if y_column is None:
                return "Line chart requires both X and Y columns"
            if not pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                return f"Line chart Y column must be numeric. Column '{y_column}' is not numeric."
                
        elif chart_type == "Scatter":
            if y_column is None:
                return "Scatter plot requires both X and Y columns"
            if not pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                return f"Scatter plot X column must be numeric. Column '{x_column}' is not numeric."
            if not pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                return f"Scatter plot Y column must be numeric. Column '{y_column}' is not numeric."
                
        elif chart_type == "Pie":
            # Pie charts work best with categorical data
            if pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                # Check if numeric column has too many unique values
                unique_count = self.current_data[x_column].nunique()
                if unique_count > 20:
                    return f"Pie chart works best with categorical data. Column '{x_column}' has {unique_count} unique values (recommended: < 20)."
                    
        elif chart_type == "Box Plot":
            if y_column is None:
                return "Box plot requires both X and Y columns"
            if not pd.api.types.is_numeric_dtype(self.current_data[y_column]):
                return f"Box plot Y column must be numeric. Column '{y_column}' is not numeric."
                
        elif chart_type == "Distribution":
            if not pd.api.types.is_numeric_dtype(self.current_data[x_column]):
                return f"Distribution plot requires numeric data. Column '{x_column}' is not numeric."
                
        return None  # No validation errors
        
    def on_chart_type_change(self, chart_type: str):
        """Handle chart type change to update column suggestions"""
        if self.current_data is None:
            return
            
        # Get all columns
        all_columns = list(self.current_data.columns)
        numeric_columns = list(self.current_data.select_dtypes(include=[np.number]).columns)
        categorical_columns = list(self.current_data.select_dtypes(include=['object', 'category']).columns)
        
        # Update column dropdowns based on chart type
        if chart_type in ["Histogram", "Distribution"]:
            # Only numeric columns for X
            self.x_column_dropdown.configure(values=numeric_columns if numeric_columns else ["No numeric columns available"])
            self.y_column_dropdown.configure(values=["Not needed for this chart type"])
            if numeric_columns:
                self.x_column_dropdown.set(numeric_columns[0])
            self.y_column_dropdown.set("Not needed for this chart type")
            
        elif chart_type == "Pie":
            # Prefer categorical columns for pie charts
            preferred_columns = categorical_columns + numeric_columns
            self.x_column_dropdown.configure(values=preferred_columns if preferred_columns else ["No suitable columns available"])
            self.y_column_dropdown.configure(values=["Not needed for this chart type"])
            if preferred_columns:
                self.x_column_dropdown.set(preferred_columns[0])
            self.y_column_dropdown.set("Not needed for this chart type")
            
        elif chart_type in ["Line", "Scatter", "Box Plot"]:
            # Both X and Y needed, X can be categorical for some charts
            self.x_column_dropdown.configure(values=all_columns)
            self.y_column_dropdown.configure(values=numeric_columns if numeric_columns else ["No numeric columns available"])
            if all_columns:
                self.x_column_dropdown.set(all_columns[0])
            if numeric_columns:
                self.y_column_dropdown.set(numeric_columns[0])
            else:
                self.y_column_dropdown.set("No numeric columns available")
                
        elif chart_type == "Bar":
            # Bar charts are flexible
            self.x_column_dropdown.configure(values=all_columns)
            self.y_column_dropdown.configure(values=["Not needed (count plot)"] + numeric_columns)
            if all_columns:
                self.x_column_dropdown.set(all_columns[0])
            self.y_column_dropdown.set("Not needed (count plot)")
            
    def save_chart(self):
        """Save chart and description to memory for PDF export"""
        if self.current_chart_figure is None:
            messagebox.showwarning("Warning", "No chart to save")
            return
            
        description = self.chart_description_entry.get().strip()
        if not description:
            messagebox.showwarning("Warning", "Please enter a chart description")
            return
            
        chart_type = self.chart_type_dropdown.get()
        x_column = self.x_column_dropdown.get()
        y_column = self.y_column_dropdown.get()
        
        # Handle placeholder values for Y column
        placeholder_values = ["Not needed for this chart type", "Not needed (count plot)", "No columns available"]
        if y_column in placeholder_values:
            y_column = None
        
        try:
            # Create a deep copy of the figure to avoid conflicts
            figure_copy = copy.deepcopy(self.current_chart_figure)
            
            # Record chart in report with figure copy
            self.chart_report.add_chart(chart_type, x_column, y_column, description, figure_copy)
            
            # Clear description
            self.chart_description_entry.delete(0, 'end')
            
            messagebox.showinfo("Success", f"Chart '{chart_type}' saved to report. Use 'Export Charts PDF' to create PDF with all saved charts.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chart: {str(e)}")
            
    def export_charts_pdf(self):
        """Export all saved charts to PDF"""
        if not self.chart_report.charts:
            messagebox.showwarning("Warning", "No charts to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Charts PDF",
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            # Create PDF document
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20
            )
            normal_style = styles['Normal']
            
            # Title
            title = Paragraph("Dashboard Charts Report", title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # Summary
            summary_heading = Paragraph("Report Summary", heading_style)
            story.append(summary_heading)
            
            # Create summary table
            summary_data = [
                ["Total Charts", str(len(self.chart_report.charts))],
                ["Report Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            
            if self.current_data is not None:
                summary_data.extend([
                    ["Dataset Rows", str(len(self.current_data))],
                    ["Dataset Columns", str(len(self.current_data.columns))]
                ])
                
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Charts details and images
            charts_heading = Paragraph("Charts Details", heading_style)
            story.append(charts_heading)
            
            for i, chart in enumerate(self.chart_report.charts, 1):
                # Chart title
                chart_title = Paragraph(f"{i}. {chart['chart_type']} Chart", heading_style)
                story.append(chart_title)
                
                # Chart details
                chart_text = f"• X Column: {chart['x_column']}<br/>"
                if chart['y_column'] is not None:
                    chart_text += f"• Y Column: {chart['y_column']}<br/>"
                chart_text += f"• Description: {chart['description']}<br/>"
                
                chart_para = Paragraph(chart_text, normal_style)
                story.append(chart_para)
                
                # Add chart image if available
                if chart['figure'] is not None:
                    try:
                        # Save figure to buffer
                        buffer = io.BytesIO()
                        chart['figure'].savefig(buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
                        buffer.seek(0)
                        
                        # Add image to PDF
                        img = Image(buffer, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Spacer(1, 12))
                        
                    except Exception as e:
                        print(f"Error adding chart image to PDF: {e}")
                        # Try alternative method
                        try:
                            # Save to temporary file and then add to PDF
                            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                                chart['figure'].savefig(tmp_file.name, format='png', dpi=150, bbox_inches='tight', facecolor='white')
                                img = Image(tmp_file.name, width=6*inch, height=4*inch)
                                story.append(img)
                                story.append(Spacer(1, 12))
                                os.unlink(tmp_file.name)  # Delete temporary file
                        except Exception as e2:
                            print(f"Alternative method also failed: {e2}")
                            story.append(Paragraph("(Chart image could not be included)", normal_style))
                
                story.append(Spacer(1, 20))
                
            # Build PDF
            doc.build(story)
            
            messagebox.showinfo("Success", f"Charts PDF exported to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export charts PDF: {str(e)}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

    def create_outliers_detection_tab(self, parent):
        """Create the Outliers Detection tab UI (full version)"""
        # Main container
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # First group: Outlier Detection
        detection_group = ctk.CTkFrame(main_container)
        detection_group.pack(side="left", fill="y", padx=(0, 20), pady=10)
        ctk.CTkLabel(detection_group, text="Outlier Detection", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 10))

        # Column selection (numerical columns only)
        ctk.CTkLabel(detection_group, text="Column:").pack(anchor="w", padx=10)
        self.outlier_column_option = ctk.CTkOptionMenu(
            detection_group,
            values=self.get_numerical_columns_for_outlier() if self.current_data is not None else []
        )
        self.outlier_column_option.pack(fill="x", padx=10, pady=(0, 10))

        # Method selection
        ctk.CTkLabel(detection_group, text="Method:").pack(anchor="w", padx=10)
        self.outlier_method_option = ctk.CTkOptionMenu(
            detection_group,
            values=["IQR Method", "Z-Score Method", "SVM Method"]
        )
        self.outlier_method_option.pack(fill="x", padx=10, pady=(0, 10))

        # Z-Score threshold
        ctk.CTkLabel(detection_group, text="Z-Score threshold:").pack(anchor="w", padx=10)
        self.zscore_entry = ctk.CTkEntry(detection_group, placeholder_text="Best for data (3)")
        self.zscore_entry.pack(fill="x", padx=10, pady=(0, 10))

        # SVM Contamination (nu)
        ctk.CTkLabel(detection_group, text="SVM Contamination (nu):").pack(anchor="w", padx=10)
        self.svm_nu_entry = ctk.CTkEntry(detection_group, placeholder_text="Best for data (0.1)")
        self.svm_nu_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Detect Outlier button
        self.detect_outlier_btn = ctk.CTkButton(
            detection_group,
            text="Detect Outlier",
            command=self.detect_outliers_stub
        )
        self.detect_outlier_btn.pack(pady=(10, 10))

        # Second group: Outliers Results
        results_group = ctk.CTkFrame(main_container)
        results_group.pack(side="left", fill="both", expand=True, pady=10)
        ctk.CTkLabel(results_group, text="Outliers Results", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 10))

        # Table for results
        self.outlier_tree = ttk.Treeview(results_group)
        self.outlier_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Action selection
        ctk.CTkLabel(results_group, text="Action:").pack(anchor="w", padx=10)
        self.outlier_action_option = ctk.CTkOptionMenu(
            results_group,
            values=["Remove Outliers", "Replace With Mean", "Replace With Median"]
        )
        self.outlier_action_option.pack(fill="x", padx=10, pady=(0, 10))

        # Apply Action button
        self.apply_outlier_action_btn = ctk.CTkButton(
            results_group,
            text="Apply Action",
            command=self.apply_outlier_action_stub
        )
        self.apply_outlier_action_btn.pack(pady=(0, 10))

        # Export PDF button
        self.export_outlier_pdf_btn = ctk.CTkButton(
            results_group,
            text="Export PDF Report",
            command=self.export_outlier_pdf_stub
        )
        self.export_outlier_pdf_btn.pack(pady=(0, 10))

    def get_numerical_columns_for_outlier(self):
        if self.current_data is not None:
            return [col for col in self.current_data.columns if pd.api.types.is_numeric_dtype(self.current_data[col])]
        return []

    def detect_outliers_stub(self):
        """Detect outliers using the selected method"""
        if self.current_data is None:
            messagebox.showwarning("Warning", "No data loaded. Please load a file first.")
            return
            
        column = self.outlier_column_option.get()
        method = self.outlier_method_option.get()
        
        if not column:
            messagebox.showwarning("Warning", "Please select a column.")
            return
            
        try:
            # Get the column data
            col_data = self.current_data[column].dropna()
            
            if len(col_data) == 0:
                messagebox.showwarning("Warning", f"No valid data found in column '{column}'.")
                return
                
            # Detect outliers based on method
            if method == "IQR Method":
                outliers = self.detect_outliers_iqr(col_data)
            elif method == "Z-Score Method":
                threshold = self.get_zscore_threshold()
                outliers = self.detect_outliers_zscore(col_data, threshold)
            elif method == "SVM Method":
                nu = self.get_svm_nu()
                outliers = self.detect_outliers_svm(col_data, nu)
            else:
                messagebox.showerror("Error", f"Unknown method: {method}")
                return
                
            # Store results
            self.outlier_results = {
                'column': column,
                'method': method,
                'outliers': outliers,
                'total_count': len(col_data),
                'outlier_count': len(outliers)
            }
            
            # Track the operation
            operation = {
                'type': 'detection',
                'timestamp': datetime.now(),
                'column': column,
                'method': method,
                'outliers_found': len(outliers),
                'total_values': len(col_data),
                'percentage': (len(outliers)/len(col_data))*100 if len(col_data) > 0 else 0
            }
            self.outlier_operations.append(operation)
            
            # Display results
            self.display_outlier_results()
            
            messagebox.showinfo("Success", f"Found {len(outliers)} outliers using {method}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect outliers: {str(e)}")
            
    def detect_outliers_iqr(self, data):
        """Detect outliers using IQR method"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        return outliers
        
    def detect_outliers_zscore(self, data, threshold=3.0):
        """Detect outliers using Z-Score method"""
        z_scores = np.abs((data - data.mean()) / data.std())
        outliers = data[z_scores > threshold]
        return outliers
        
    def detect_outliers_svm(self, data, nu=0.1):
        """Detect outliers using SVM method"""
        try:
            from sklearn.ensemble import IsolationForest
            # Reshape data for sklearn
            X = data.values.reshape(-1, 1)
            # Use Isolation Forest (more robust than One-Class SVM for outlier detection)
            clf = IsolationForest(contamination=nu, random_state=42)
            predictions = clf.fit_predict(X)
            # -1 for outliers, 1 for inliers
            outlier_mask = predictions == -1
            outliers = data[outlier_mask]
            return outliers
        except ImportError:
            messagebox.showerror("Error", "scikit-learn is required for SVM outlier detection. Please install it.")
            return pd.Series(dtype=float)
            
    def get_zscore_threshold(self):
        """Get Z-Score threshold from entry or use default"""
        threshold_str = self.zscore_entry.get().strip()
        if threshold_str:
            try:
                threshold = float(threshold_str)
                if 1.0 <= threshold <= 5.0:
                    return threshold
                else:
                    messagebox.showwarning("Warning", "Z-Score threshold must be between 1.0 and 5.0. Using default 3.0.")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid Z-Score threshold. Using default 3.0.")
        return 3.0
        
    def get_svm_nu(self):
        """Get SVM contamination (nu) from entry or use default"""
        nu_str = self.svm_nu_entry.get().strip()
        if nu_str:
            try:
                nu = float(nu_str)
                if 0.01 <= nu <= 0.5:
                    return nu
                else:
                    messagebox.showwarning("Warning", "SVM contamination must be between 0.01 and 0.5. Using default 0.1.")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid SVM contamination value. Using default 0.1.")
        return 0.1
        
    def display_outlier_results(self):
        """Display outlier results in the table"""
        if not hasattr(self, 'outlier_results') or not self.outlier_results:
            return
            
        # Clear existing data
        for item in self.outlier_tree.get_children():
            self.outlier_tree.delete(item)
            
        # Configure columns
        self.outlier_tree["columns"] = ["Index", "Value"]
        self.outlier_tree["show"] = "headings"
        
        # Configure column headings
        self.outlier_tree.heading("Index", text="Index")
        self.outlier_tree.heading("Value", text="Value")
        
        # Configure column widths
        self.outlier_tree.column("Index", width=100)
        self.outlier_tree.column("Value", width=150)
        
        # Insert outlier data
        outliers = self.outlier_results['outliers']
        for index, value in outliers.items():
            self.outlier_tree.insert("", "end", values=[index, f"{value:.4f}"])
            
    def apply_outlier_action_stub(self):
        """Apply the selected action to handle outliers"""
        if not hasattr(self, 'outlier_results') or not self.outlier_results:
            messagebox.showwarning("Warning", "No outliers detected. Please detect outliers first.")
            return
            
        action = self.outlier_action_option.get()
        column = self.outlier_results['column']
        
        if not action:
            messagebox.showwarning("Warning", "Please select an action.")
            return
            
        try:
            if action == "Remove Outliers":
                self.remove_outliers(column)
            elif action == "Replace With Mean":
                self.replace_outliers_with_mean(column)
            elif action == "Replace With Median":
                self.replace_outliers_with_median(column)
            else:
                messagebox.showerror("Error", f"Unknown action: {action}")
                return
                
            # Track the action
            operation = {
                'type': 'action',
                'timestamp': datetime.now(),
                'column': column,
                'action': action,
                'outliers_affected': len(self.outlier_results['outliers'])
            }
            self.outlier_operations.append(operation)
                
            # Update the main data table
            self.update_table()
            
            messagebox.showinfo("Success", f"Applied {action} to column '{column}'")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply action: {str(e)}")
            
    def remove_outliers(self, column):
        """Remove outliers from the column"""
        outliers = self.outlier_results['outliers']
        self.current_data = self.current_data.drop(outliers.index)
        
    def replace_outliers_with_mean(self, column):
        """Replace outliers with the mean of non-outlier values"""
        outliers = self.outlier_results['outliers']
        non_outliers = self.current_data[column].drop(outliers.index)
        mean_value = non_outliers.mean()
        self.current_data.loc[outliers.index, column] = mean_value
        
    def replace_outliers_with_median(self, column):
        """Replace outliers with the median of non-outlier values"""
        outliers = self.outlier_results['outliers']
        non_outliers = self.current_data[column].drop(outliers.index)
        median_value = non_outliers.median()
        self.current_data.loc[outliers.index, column] = median_value
        
    def export_outlier_pdf_stub(self):
        """Export outlier detection report as PDF"""
        if not hasattr(self, 'outlier_results') or not self.outlier_results:
            messagebox.showwarning("Warning", "No outlier detection results to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Outlier Detection Report",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            self.create_outlier_pdf_report(file_path)
            messagebox.showinfo("Success", f"Outlier detection report exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
            
    def create_outlier_pdf_report(self, file_path):
        """Create PDF report for outlier detection operations"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=getSampleStyleSheet()['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        elements.append(Paragraph("Outlier Detection Operations Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Report details
        normal_style = getSampleStyleSheet()['Normal']
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=getSampleStyleSheet()['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        # File information
        if hasattr(self, 'current_file_path') and self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            elements.append(Paragraph(f"File: {file_name}", normal_style))
            elements.append(Spacer(1, 10))
            
        # Summary of operations
        if self.outlier_operations:
            elements.append(Paragraph("Operations Summary:", heading_style))
            elements.append(Spacer(1, 10))
            
            for i, operation in enumerate(self.outlier_operations, 1):
                if operation['type'] == 'detection':
                    elements.append(Paragraph(
                        f"Operation {i}: Outlier Detection", 
                        getSampleStyleSheet()['Heading3']
                    ))
                    elements.append(Paragraph(f"• Column: {operation['column']}", normal_style))
                    elements.append(Paragraph(f"• Method: {operation['method']}", normal_style))
                    elements.append(Paragraph(f"• Outliers Found: {operation['outliers_found']}", normal_style))
                    elements.append(Paragraph(f"• Total Values: {operation['total_values']}", normal_style))
                    elements.append(Paragraph(f"• Percentage: {operation['percentage']:.2f}%", normal_style))
                    elements.append(Paragraph(f"• Timestamp: {operation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                    
                elif operation['type'] == 'action':
                    elements.append(Paragraph(
                        f"Operation {i}: Action Applied", 
                        getSampleStyleSheet()['Heading3']
                    ))
                    elements.append(Paragraph(f"• Column: {operation['column']}", normal_style))
                    elements.append(Paragraph(f"• Action: {operation['action']}", normal_style))
                    elements.append(Paragraph(f"• Outliers Affected: {operation['outliers_affected']}", normal_style))
                    elements.append(Paragraph(f"• Timestamp: {operation['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                
                elements.append(Spacer(1, 10))
        else:
            elements.append(Paragraph("No outlier detection operations performed.", normal_style))
            
        # Statistics summary
        if self.outlier_operations:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Statistics Summary:", heading_style))
            elements.append(Spacer(1, 10))
            
            total_detections = len([op for op in self.outlier_operations if op['type'] == 'detection'])
            total_actions = len([op for op in self.outlier_operations if op['type'] == 'action'])
            
            elements.append(Paragraph(f"• Total Detection Operations: {total_detections}", normal_style))
            elements.append(Paragraph(f"• Total Actions Applied: {total_actions}", normal_style))
            
            if total_detections > 0:
                total_outliers = sum([op['outliers_found'] for op in self.outlier_operations if op['type'] == 'detection'])
                elements.append(Paragraph(f"• Total Outliers Detected: {total_outliers}", normal_style))
            
        # Timestamp
        elements.append(Spacer(1, 20))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Report Generated on: {timestamp}", normal_style))
        
        # Build PDF
        doc.build(elements)

    def create_analysis_tab(self, parent):
        """Create the Analysis tab UI (self-contained)"""
        if not hasattr(self, 'analysis_actions'):
            self.analysis_actions = []
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        # First group: Do Analysis (scrollable)
        do_group_scroll = ctk.CTkScrollableFrame(main_container)
        do_group_scroll.grid(row=0, column=0, padx=(0, 20), pady=10, sticky="nsew")
        do_group = do_group_scroll
        ctk.CTkLabel(do_group, text="Do Analysis", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 10))
        # Analysis Type
        ctk.CTkLabel(do_group, text="Analysis Type:").pack(anchor="w", padx=10)
        self.analysis_type_option = ctk.CTkOptionMenu(
            do_group,
            values=["Summary Statistics", "Correlation Matrix", "Group Analysis", "Pivot Table", "Distribution Analysis", "Time Series Analysis", "Statistical Tests", "Hypothesis Testing", "Data Transformation"],
            command=self.on_analysis_type_change
        )
        self.analysis_type_option.pack(fill="x", padx=10, pady=(0, 10))
        # Select Columns
        ctk.CTkLabel(do_group, text="Select Columns:").pack(anchor="w", padx=10)
        self.analysis_columns_listbox = tk.Listbox(do_group, selectmode=tk.MULTIPLE, exportselection=False)
        if self.current_data is not None:
            for col in self.current_data.columns:
                self.analysis_columns_listbox.insert(tk.END, col)
        self.analysis_columns_listbox.pack(fill="x", padx=10, pady=(0, 10))
        # Group By
        ctk.CTkLabel(do_group, text="Group By:").pack(anchor="w", padx=10)
        self.analysis_groupby_option = ctk.CTkOptionMenu(
            do_group,
            values=list(self.current_data.columns) if self.current_data is not None else []
        )
        self.analysis_groupby_option.pack(fill="x", padx=10, pady=(0, 10))
        # --- Time Series Analysis Options ---
        self.ts_frame = ctk.CTkFrame(do_group)
        # Date/Time column
        self.ts_date_label = ctk.CTkLabel(self.ts_frame, text="Date/Time Column:")
        self.ts_date_option = ctk.CTkOptionMenu(self.ts_frame, values=list(self.current_data.columns) if self.current_data is not None else [])
        # Value column
        self.ts_value_label = ctk.CTkLabel(self.ts_frame, text="Value Column:")
        self.ts_value_option = ctk.CTkOptionMenu(self.ts_frame, values=[col for col in self.current_data.columns if pd.api.types.is_numeric_dtype(self.current_data[col])] if self.current_data is not None else [])
        # Method
        self.ts_method_label = ctk.CTkLabel(self.ts_frame, text="Method:")
        self.ts_method_option = ctk.CTkOptionMenu(self.ts_frame, values=["Trend (Rolling Mean)", "Seasonal Decomposition", "Moving Average", "ADF Stationarity Test", "Plot Series"], command=self.on_ts_method_change)
        # Window size (for moving average)
        self.ts_window_label = ctk.CTkLabel(self.ts_frame, text="Window Size:")
        self.ts_window_entry = ctk.CTkEntry(self.ts_frame, placeholder_text="7")
        # Hide initially
        self.ts_frame.pack_forget()
        # Run and Save buttons
        btn_frame = ctk.CTkFrame(do_group)
        btn_frame.pack(fill="x", padx=10, pady=(10, 10))
        self.run_analysis_btn = ctk.CTkButton(
            btn_frame, text="Run Analysis", command=self.run_analysis_action
        )
        self.run_analysis_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.save_analysis_btn = ctk.CTkButton(
            btn_frame, text="Save Analysis", command=self.save_analysis_action
        )
        self.save_analysis_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        # Second group: Result
        result_group = ctk.CTkFrame(main_container)
        result_group.grid(row=0, column=1, pady=10, sticky="nsew")
        ctk.CTkLabel(result_group, text="Result", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 10))
        self.analysis_result_text = tk.Text(result_group, height=30, wrap="word")
        self.analysis_result_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.export_analysis_btn = ctk.CTkButton(
            result_group, text="Export Analysis", command=self.export_analysis_to_excel
        )
        self.export_analysis_btn.pack(pady=(0, 10))
        # For plot display
        self.ts_plot_canvas = None
        self.ts_plot_frame = tk.Frame(result_group)
        self.ts_plot_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.ts_plot_frame.pack_propagate(True)
    def on_analysis_type_change(self, value):
        if value == "Time Series Analysis":
            self.ts_frame.pack(fill="x", padx=10, pady=(10, 10))
            # Show all time series options
            self.ts_date_label.pack(anchor="w", padx=10)
            self.ts_date_option.pack(fill="x", padx=10, pady=(0, 10))
            self.ts_value_label.pack(anchor="w", padx=10)
            self.ts_value_option.pack(fill="x", padx=10, pady=(0, 10))
            self.ts_method_label.pack(anchor="w", padx=10)
            self.ts_method_option.pack(fill="x", padx=10, pady=(0, 10))
            self.ts_window_label.pack_forget()
            self.ts_window_entry.pack_forget()
        else:
            self.ts_frame.pack_forget()
    def on_ts_method_change(self, value):
        if value in ["Moving Average", "Trend (Rolling Mean)"]:
            self.ts_window_label.pack(anchor="w", padx=10)
            self.ts_window_entry.pack(fill="x", padx=10, pady=(0, 10))
        else:
            self.ts_window_label.pack_forget()
            self.ts_window_entry.pack_forget()
    def run_analysis_action(self):
        import matplotlib.pyplot as plt
        
        analysis_type = self.analysis_type_option.get()
        selected_indices = self.analysis_columns_listbox.curselection()
        columns = [self.analysis_columns_listbox.get(i) for i in selected_indices]
        group_by = self.analysis_groupby_option.get()
        result = f"Analysis: {analysis_type}\nColumns: {columns}\nGroup By: {group_by}\n---\n"
        result_df = None
        plot_fig = None
        export_sheet_name = analysis_type  # Default sheet name
        if self.current_data is not None and columns:
            try:
                if analysis_type == "Time Series Analysis":
                    date_col = self.ts_date_option.get()
                    value_col = self.ts_value_option.get()
                    ts_method = self.ts_method_option.get()
                    window = self.ts_window_entry.get()
                    window = int(window) if window.isdigit() else 7
                    export_sheet_name = ts_method if ts_method else analysis_type
                    if not date_col or not value_col or not ts_method:
                        result += "Please select date, value, and method."
                    else:
                        df = self.current_data[[date_col, value_col]].dropna().copy()
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        df = df.dropna(subset=[date_col])
                        df = df.sort_values(date_col)
                        df.set_index(date_col, inplace=True)
                        if ts_method == "Trend (Rolling Mean)":
                            result_df = df[[value_col]].rolling(window=window).mean()
                            result += f"Rolling Mean (window={window}):\n" + str(result_df.tail(10))
                            plot_fig = plt.figure(figsize=(6,3))
                            plt.plot(df.index, df[value_col], label='Original')
                            plt.plot(result_df.index, result_df[value_col], label='Rolling Mean')
                            plt.legend()
                            plt.title('Trend (Rolling Mean)')
                        elif ts_method == "Seasonal Decomposition":
                            from statsmodels.tsa.seasonal import seasonal_decompose
                            decomposition = seasonal_decompose(df[value_col], model='additive', period=window)
                            result += f"Seasonal Decomposition:\nTrend:\n{decomposition.trend.tail(10)}\nSeasonal:\n{decomposition.seasonal.tail(10)}\nResidual:\n{decomposition.resid.tail(10)}"
                            result_df = pd.DataFrame({
                                'trend': decomposition.trend,
                                'seasonal': decomposition.seasonal,
                                'resid': decomposition.resid
                            })
                            plot_fig = decomposition.plot()
                        elif ts_method == "Moving Average":
                            result_df = df[[value_col]].rolling(window=window).mean()
                            result += f"Moving Average (window={window}):\n" + str(result_df.tail(10))
                            plot_fig = plt.figure(figsize=(6,3))
                            plt.plot(df.index, df[value_col], label='Original')
                            plt.plot(result_df.index, result_df[value_col], label='Moving Average')
                            plt.legend()
                            plt.title('Moving Average')
                        elif ts_method == "ADF Stationarity Test":
                            from statsmodels.tsa.stattools import adfuller
                            adf_result = adfuller(df[value_col])
                            result += f"ADF Statistic: {adf_result[0]:.4f}\nP-value: {adf_result[1]:.4g}\n"
                            interpretation = "Series is stationary (p < 0.05)" if adf_result[1] < 0.05 else "Series is not stationary (p >= 0.05)"
                            result += f"Result: {interpretation}\n"
                            result_df = pd.DataFrame({
                                'ADF Statistic': [adf_result[0]],
                                'P-value': [adf_result[1]],
                                'Result': [interpretation]
                            })
                        elif ts_method == "Plot Series":
                            result += "Plotting time series.\n"
                            plot_fig = plt.figure(figsize=(6,3))
                            plt.plot(df.index, df[value_col], label='Series')
                            plt.legend()
                            plt.title('Time Series Plot')
                        else:
                            result += "Unknown time series method."
                else:
                    # Restore logic for all non-time-series analyses
                    df = self.current_data.copy()
                    if analysis_type == "Summary Statistics":
                        stats_dict = {}
                        for col in columns:
                            if pd.api.types.is_numeric_dtype(df[col]):
                                desc = df[col].describe()
                                stats_dict[col] = desc
                            else:
                                value_counts = df[col].value_counts()
                                stats_dict[col] = value_counts
                        result += "Summary Statistics:\n"
                        result_df = pd.concat(stats_dict, axis=1)
                        result += str(result_df)
                    elif analysis_type == "Correlation Matrix":
                        numeric_df = df[columns].select_dtypes(include=[np.number])
                        if len(numeric_df.columns) >= 2:
                            corr = numeric_df.corr()
                            result += "Correlation Matrix:\n" + str(corr)
                            result_df = corr
                        else:
                            result += "Need at least 2 numeric columns for correlation analysis."
                    elif analysis_type == "Group Analysis":
                        if group_by and group_by in df.columns:
                            numeric_cols = df[columns].select_dtypes(include=[np.number]).columns.tolist()
                            if numeric_cols:
                                grouped = df.groupby(group_by)[numeric_cols]
                                agg_stats = grouped.agg(['count', 'mean', 'std', 'min', 'max'])
                                result += f"Group Analysis by '{group_by}':\n" + str(agg_stats)
                                result_df = agg_stats
                            else:
                                count_stats = df.groupby(group_by).size()
                                result += f"Group Counts by '{group_by}':\n" + str(count_stats)
                                result_df = count_stats.to_frame('Count')
                        else:
                            result += "Please select a group by column."
                    elif analysis_type == "Pivot Table":
                        if len(columns) >= 2:
                            value_col = columns[-1]
                            index_cols = columns[:-1]
                            pivot = pd.pivot_table(
                                df,
                                values=value_col,
                                index=index_cols,
                                aggfunc=['count', 'mean', 'median', 'std', 'min', 'max', 'sum']
                            )
                            result += f"Pivot Table: {value_col} by {', '.join(index_cols)}\n" + str(pivot)
                            result_df = pivot
                        else:
                            result += "Please select at least two columns for pivot table."
                    elif analysis_type == "Distribution Analysis":
                        dist_stats_dict = {}
                        for col in columns:
                            numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_data) == 0:
                                continue
                            stats_dict = {
                                'mean': numeric_data.mean(),
                                'median': numeric_data.median(),
                                'std': numeric_data.std(),
                                'skewness': numeric_data.skew(),
                                'kurtosis': numeric_data.kurtosis(),
                                'min': numeric_data.min(),
                                'max': numeric_data.max(),
                                'q1': numeric_data.quantile(0.25),
                                'q3': numeric_data.quantile(0.75)
                            }
                            dist_stats_dict[col] = stats_dict
                        if dist_stats_dict:
                            result_df = pd.DataFrame(dist_stats_dict).T
                            result += "Distribution Analysis:\n" + str(result_df)
                        else:
                            result += "No valid numeric data for distribution analysis."
                    elif analysis_type == "Statistical Tests" or analysis_type == "Hypothesis Testing":
                        if len(columns) >= 2:
                            col1, col2 = columns[:2]
                            data1 = pd.to_numeric(df[col1], errors='coerce').dropna()
                            data2 = pd.to_numeric(df[col2], errors='coerce').dropna()
                            t_stat, p_value = stats.ttest_ind(data1, data2)
                            result += f"T-Test Results ({col1} vs {col2}):\nT-statistic: {t_stat:.4f}\nP-value: {p_value:.4f}\nSignificant difference: {'Yes' if p_value < 0.05 else 'No'}"
                            result_df = pd.DataFrame({
                                'T-statistic': [t_stat],
                                'P-value': [p_value],
                                'Significant': ['Yes' if p_value < 0.05 else 'No']
                            })
                        else:
                            result += "Please select at least two columns for statistical test."
                    elif analysis_type == "Data Transformation":
                        # Example: Log Transform and Z-Score Normalization
                        transform_type = "Log Transform"  # You may want to get this from the UI
                        trans_results = {}
                        for col in columns:
                            numeric_data = pd.to_numeric(df[col], errors='coerce').dropna()
                            if len(numeric_data) == 0:
                                continue
                            if transform_type == "Log Transform":
                                transformed = np.log1p(numeric_data)
                                trans_results[col] = transformed
                            elif transform_type == "Z-Score Normalization":
                                transformed = (numeric_data - numeric_data.mean()) / numeric_data.std()
                                trans_results[col] = transformed
                        if trans_results:
                            result_df = pd.DataFrame(trans_results)
                            result += f"Data Transformation ({transform_type}):\n" + str(result_df.head())
                        else:
                            result += "No valid numeric data for transformation."
                    export_sheet_name = analysis_type
            except Exception as e:
                result += f"Error: {e}"
        else:
            result += "No data or columns selected."
        self.analysis_result_text.delete(1.0, tk.END)
        self.analysis_result_text.insert(tk.END, result)
        # Show plot if any
        if hasattr(self, 'ts_plot_canvas') and self.ts_plot_canvas:
            self.ts_plot_canvas.get_tk_widget().destroy()
            self.ts_plot_canvas = None
        if plot_fig is not None:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.ts_plot_canvas = FigureCanvasTkAgg(plot_fig, master=self.ts_plot_frame)
            self.ts_plot_canvas.draw()
            widget = self.ts_plot_canvas.get_tk_widget()
            widget.pack(fill="both", expand=True)
            widget.update_idletasks()
            widget.minsize(400, 300)
            plt.close(plot_fig)
        # Record the analysis (store both text, DataFrame, and export sheet name)
        self.last_analysis_result = {'text': result, 'df': result_df, 'sheet_name': export_sheet_name}
    def save_analysis_action(self):
        """Save the last analysis result to the actions list"""
        if hasattr(self, 'last_analysis_result'):
            self.analysis_actions.append(self.last_analysis_result)
            messagebox.showinfo("Saved", "Analysis saved.")
        else:
            messagebox.showwarning("Warning", "No analysis to save.")
    def export_analysis_to_excel(self):
        """Export all saved analyses to an Excel file, each in a different sheet as a table, with sheet name as analysis type or method"""
        if not hasattr(self, 'analysis_actions') or not self.analysis_actions:
            messagebox.showwarning("Warning", "No analyses to export.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Analyses",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            sheet_name_counts = {}
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for idx, analysis in enumerate(self.analysis_actions, 1):
                    meta_lines = []
                    text = analysis['text']
                    df = analysis['df']
                    sheet_name = analysis.get('sheet_name', f'Analysis_{idx}')
                    # Extract meta info (before ---)
                    if '\n---\n' in text:
                        meta, _ = text.split('\n---\n', 1)
                        meta_lines = meta.split('\n')
                    else:
                        meta_lines = [text]
                    # Ensure unique sheet name
                    safe_sheet_name = sheet_name[:28]  # Excel sheet name limit is 31 chars
                    count = sheet_name_counts.get(safe_sheet_name, 0)
                    if count:
                        sheet_name_final = f"{safe_sheet_name}_{count+1}"
                    else:
                        sheet_name_final = safe_sheet_name
                    sheet_name_counts[safe_sheet_name] = count + 1
                    # Write meta info as header
                    if df is not None:
                        meta_df = pd.DataFrame({'Info': meta_lines})
                        meta_df.to_excel(writer, sheet_name=sheet_name_final, index=False, header=False, startrow=0)
                        df.to_excel(writer, sheet_name=sheet_name_final, startrow=len(meta_lines)+1)
                    else:
                        pd.DataFrame({'Result': [text]}).to_excel(writer, sheet_name=sheet_name_final, index=False)
            messagebox.showinfo("Success", f"Analyses exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export analyses: {e}")

    def create_periodical_breakdown_tab(self, parent):
        # Main container
        main_container = ctk.CTkFrame(parent)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        # Group 1: Period Settings
        period_group = ctk.CTkFrame(main_container)
        period_group.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(period_group, text="Period Settings", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(period_group, text="Date Column:").pack(anchor="w")
        self.period_date_option = ctk.CTkOptionMenu(period_group, values=self.get_date_columns())
        self.period_date_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(period_group, text="Period Type:").pack(anchor="w")
        self.period_type_option = ctk.CTkOptionMenu(period_group, values=["Day", "Week", "Month", "Quarter", "Year"])
        self.period_type_option.pack(fill="x", pady=(0, 10))
        # Group 2: Columns for Analysis
        columns_group = ctk.CTkFrame(main_container)
        columns_group.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(columns_group, text="Columns for Analysis", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        self.period_columns_listbox = tk.Listbox(columns_group, selectmode="multiple", exportselection=False)
        for col in self.get_all_columns():
            self.period_columns_listbox.insert(tk.END, col)
        self.period_columns_listbox.pack(fill="both", expand=True)
        # Group 3: Results
        results_group = ctk.CTkFrame(main_container)
        results_group.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(results_group, text="Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        self.period_results_text = tk.Text(results_group, height=25, wrap="word")
        self.period_results_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        # Buttons
        btn_frame = ctk.CTkFrame(results_group)
        btn_frame.pack(fill="x", pady=(0, 10))
        self.run_period_analysis_btn = ctk.CTkButton(btn_frame, text="Run Period Analysis", command=self.run_period_analysis)
        self.run_period_analysis_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.save_period_result_btn = ctk.CTkButton(btn_frame, text="Save Results", command=self.save_period_result)
        self.save_period_result_btn.pack(side="left", expand=True, fill="x", padx=(5, 5))
        self.export_period_results_btn = ctk.CTkButton(btn_frame, text="Export Results", command=self.export_period_results)
        self.export_period_results_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        # Storage for saved results
        self.period_saved_results = []
    def get_date_columns(self):
        if self.current_data is not None:
            return list(self.current_data.columns)
        return []
    def get_all_columns(self):
        if self.current_data is not None:
            return list(self.current_data.columns)
        return []
    def run_period_analysis(self):
        if self.current_data is None:
            self.period_results_text.delete(1.0, tk.END)
            self.period_results_text.insert(tk.END, "No data loaded.")
            return
        date_col = self.period_date_option.get()
        period_type = self.period_type_option.get()
        selected_indices = self.period_columns_listbox.curselection()
        columns = [self.period_columns_listbox.get(i) for i in selected_indices]
        if not date_col or not period_type or not columns:
            self.period_results_text.delete(1.0, tk.END)
            self.period_results_text.insert(tk.END, "Please select date column, period type, and columns for analysis.")
            return
        df = self.current_data.copy()
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col])
            freq_map = {"Day": "D", "Week": "W", "Month": "M", "Quarter": "QE", "Year": "YE"}
            freq = freq_map.get(period_type, "M")
            grouped = df.groupby([pd.Grouper(key=date_col, freq=freq)])[columns]
            agg_df = grouped.agg(['count', 'mean', 'sum', 'min', 'max'])
            self.period_last_result = {'df': agg_df, 'meta': {'date_col': date_col, 'period_type': period_type, 'columns': columns}}
            self.period_results_text.delete(1.0, tk.END)
            self.period_results_text.insert(tk.END, str(agg_df.head(30)))
        except Exception as e:
            self.period_results_text.delete(1.0, tk.END)
            self.period_results_text.insert(tk.END, f"Error: {e}")
    def save_period_result(self):
        if hasattr(self, 'period_last_result'):
            self.period_saved_results.append(self.period_last_result)
            messagebox.showinfo("Saved", "Period analysis result saved.")
        else:
            messagebox.showwarning("Warning", "No result to save.")
    def export_period_results(self):
        if not self.period_saved_results:
            messagebox.showwarning("Warning", "No saved results to export.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Period Results",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for idx, result in enumerate(self.period_saved_results, 1):
                    df = result['df']
                    meta = result['meta']
                    import re
                    raw_sheet_name = f"{meta['period_type']}_{'_'.join(meta['columns'])}"
                    safe_sheet_name = re.sub(r'[:\\/?*\[\]]', '_', raw_sheet_name)[:28]
                    df.to_excel(writer, sheet_name=safe_sheet_name)
            messagebox.showinfo("Success", f"Period results exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export period results: {e}")

    def refresh_periodical_breakdown_tab(self):
        # Update date column dropdown
        if hasattr(self, 'period_date_option'):
            self.period_date_option.configure(values=self.get_date_columns())
            if self.get_date_columns():
                self.period_date_option.set(self.get_date_columns()[0])
        # Update columns listbox
        if hasattr(self, 'period_columns_listbox'):
            self.period_columns_listbox.delete(0, tk.END)
            for col in self.get_all_columns():
                self.period_columns_listbox.insert(tk.END, col)
        # Clear results area
        if hasattr(self, 'period_results_text'):
            self.period_results_text.delete(1.0, tk.END)
        # Clear saved results
        if hasattr(self, 'period_saved_results'):
            self.period_saved_results.clear()

    def create_machine_learning_tab(self, parent):
        # Scrollable main container
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        vscroll = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        main_container = ctk.CTkFrame(canvas)
        main_container.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=main_container, anchor="nw")
        main_container.grid_rowconfigure(2, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        # Group 1: ML Settings
        ml_group = ctk.CTkFrame(main_container)
        ml_group.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(ml_group, text="Machine Learning Wizard", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Target Column:").pack(anchor="w")
        self.ml_target_option = ctk.CTkOptionMenu(ml_group, values=self.get_all_columns())
        self.ml_target_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Feature Columns:").pack(anchor="w")
        self.ml_features_listbox = tk.Listbox(ml_group, selectmode="multiple", exportselection=False)
        for col in self.get_all_columns():
            self.ml_features_listbox.insert(tk.END, col)
        self.ml_features_listbox.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Model Type:").pack(anchor="w")
        self.ml_type_option = ctk.CTkOptionMenu(ml_group, values=["Classification", "Regression"], command=self.update_ml_algorithms)
        self.ml_type_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Algorithm:").pack(anchor="w")
        self.ml_algo_option = ctk.CTkOptionMenu(ml_group, values=self.get_ml_algorithms("Classification"))
        self.ml_algo_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Missing Value Strategy:").pack(anchor="w")
        self.ml_missing_option = ctk.CTkOptionMenu(ml_group, values=["Drop Rows", "Fill Mean", "Fill Median", "Fill Mode"])
        self.ml_missing_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Feature Scaling:").pack(anchor="w")
        self.ml_scaling_option = ctk.CTkOptionMenu(ml_group, values=["None", "StandardScaler", "MinMaxScaler", "RobustScaler"])
        self.ml_scaling_option.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Feature Selection:").pack(anchor="w")
        self.ml_featselect_option = ctk.CTkOptionMenu(ml_group, values=["None", "Top N Variance", "Top N Correlation"])
        self.ml_featselect_option.pack(fill="x", pady=(0, 10))
        self.ml_featselect_n_entry = ctk.CTkEntry(ml_group, placeholder_text="N (e.g. 5)")
        self.ml_featselect_n_entry.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(ml_group, text="Train/Test Split (0-1):").pack(anchor="w")
        self.ml_split_entry = ctk.CTkEntry(ml_group, placeholder_text="0.2")
        self.ml_split_entry.pack(fill="x", pady=(0, 10))
        # Group 2: Results
        results_group = ctk.CTkFrame(main_container)
        results_group.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(results_group, text="Results", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        self.ml_results_text = tk.Text(results_group, height=25, wrap="word")
        self.ml_results_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        # For ROC curve/feature importance
        self.ml_plot_canvas = None
        self.ml_plot_frame = tk.Frame(results_group)
        self.ml_plot_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.ml_plot_frame.pack_propagate(True)
        # Buttons
        btn_frame = ctk.CTkFrame(results_group)
        btn_frame.pack(fill="x", pady=(0, 10))
        self.run_ml_btn = ctk.CTkButton(btn_frame, text="Run Model", command=self.run_ml_model)
        self.run_ml_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.export_ml_btn = ctk.CTkButton(btn_frame, text="Export Predictions", command=self.export_ml_predictions)
        self.export_ml_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        # Storage for predictions
        self.ml_last_predictions = None
    def get_ml_algorithms(self, model_type):
        algos = []
        if model_type == "Classification":
            algos = ["Logistic Regression", "Random Forest", "SVM", "KNN", "Naive Bayes"]
        else:
            algos = ["Linear Regression", "Random Forest", "Ridge Regression", "Lasso Regression", "SVR"]
        return algos
    def update_ml_algorithms(self, value):
        self.ml_algo_option.configure(values=self.get_ml_algorithms(value))
        self.ml_algo_option.set(self.get_ml_algorithms(value)[0])
    def run_ml_model(self):
        if self.current_data is None:
            self.ml_results_text.delete(1.0, tk.END)
            self.ml_results_text.insert(tk.END, "No data loaded.")
            return
        target = self.ml_target_option.get()
        selected_indices = self.ml_features_listbox.curselection()
        features = [self.ml_features_listbox.get(i) for i in selected_indices]
        model_type = self.ml_type_option.get()
        algo = self.ml_algo_option.get()
        split = self.ml_split_entry.get()
        missing_strategy = self.ml_missing_option.get()
        scaling_strategy = self.ml_scaling_option.get()
        featselect_strategy = self.ml_featselect_option.get()
        featselect_n = self.ml_featselect_n_entry.get()
        try:
            split = float(split)
            if not (0 < split < 1):
                raise ValueError
        except:
            split = 0.2
        if not target or not features or target in features:
            self.ml_results_text.delete(1.0, tk.END)
            self.ml_results_text.insert(tk.END, "Please select a target and at least one feature (target cannot be a feature).")
            return
        df = self.current_data.copy()
        X = df[features]
        y = df[target]
        # Missing value handling
        if missing_strategy == "Drop Rows":
            X = X.dropna()
            y = y.loc[X.index]
        elif missing_strategy == "Fill Mean":
            X = X.fillna(X.mean(numeric_only=True))
        elif missing_strategy == "Fill Median":
            X = X.fillna(X.median(numeric_only=True))
        elif missing_strategy == "Fill Mode":
            X = X.fillna(X.mode().iloc[0])
        # Simple encoding for X and y
        X = pd.get_dummies(X, drop_first=True)
        if y.dtype == 'O' or y.dtype.name == 'category':
            y = pd.factorize(y)[0]
        # Feature scaling
        if scaling_strategy != "None":
            from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
            scaler = None
            if scaling_strategy == "StandardScaler":
                scaler = StandardScaler()
            elif scaling_strategy == "MinMaxScaler":
                scaler = MinMaxScaler()
            elif scaling_strategy == "RobustScaler":
                scaler = RobustScaler()
            if scaler is not None:
                X = pd.DataFrame(scaler.fit_transform(X), columns=X.columns, index=X.index)
        # Feature selection
        if featselect_strategy != "None":
            try:
                n = int(featselect_n)
            except:
                n = 5
            if featselect_strategy == "Top N Variance":
                variances = X.var().sort_values(ascending=False)
                top_cols = variances.head(n).index.tolist()
                X = X[top_cols]
            elif featselect_strategy == "Top N Correlation":
                if y is not None and len(X) == len(y):
                    corrs = X.apply(lambda col: abs(pd.Series(col).corr(pd.Series(y))), axis=0)
                    top_cols = corrs.sort_values(ascending=False).head(n).index.tolist()
                    X = X[top_cols]
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, random_state=42)
        result = f"Model: {algo}\nTarget: {target}\nFeatures: {list(X.columns)}\nSplit: {split}\n---\n"
        plot_fig = None
        predictions = None
        try:
            if model_type == "Classification":
                if algo == "Logistic Regression":
                    from sklearn.linear_model import LogisticRegression
                    model = LogisticRegression(max_iter=1000)
                elif algo == "Random Forest":
                    from sklearn.ensemble import RandomForestClassifier
                    model = RandomForestClassifier()
                elif algo == "SVM":
                    from sklearn.svm import SVC
                    model = SVC(probability=True)
                elif algo == "KNN":
                    from sklearn.neighbors import KNeighborsClassifier
                    model = KNeighborsClassifier()
                elif algo == "Naive Bayes":
                    from sklearn.naive_bayes import GaussianNB
                    model = GaussianNB()
                elif algo == "XGBoost":
                    import xgboost as xgb
                    model = xgb.XGBClassifier(eval_metric='logloss', use_label_encoder=False)
                else:
                    raise Exception("Unsupported algorithm for classification.")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_curve, auc
                acc = accuracy_score(y_test, y_pred)
                cm = confusion_matrix(y_test, y_pred)
                report = classification_report(y_test, y_pred)
                result += f"Accuracy: {acc:.4f}\n\nConfusion Matrix:\n{cm}\n\nClassification Report:\n{report}\n"
                # ROC curve (only for binary)
                if len(set(y_test)) == 2:
                    y_score = model.predict_proba(X_test)[:,1]
                    fpr, tpr, _ = roc_curve(y_test, y_score)
                    roc_auc = auc(fpr, tpr)
                    import matplotlib.pyplot as plt
                    plot_fig = plt.figure(figsize=(4,3))
                    plt.plot(fpr, tpr, label=f'ROC curve (area = {roc_auc:.2f})')
                    plt.plot([0, 1], [0, 1], 'k--')
                    plt.xlabel('False Positive Rate')
                    plt.ylabel('True Positive Rate')
                    plt.title('ROC Curve')
                    plt.legend(loc='lower right')
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    fi_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances}).sort_values('Importance', ascending=False)
                    result += f"\nFeature Importance:\n{fi_df.to_string(index=False)}\n"
                predictions = pd.DataFrame({"y_true": y_test, "y_pred": y_pred}, index=X_test.index)
            elif model_type == "Regression":
                if algo == "Linear Regression":
                    from sklearn.linear_model import LinearRegression
                    model = LinearRegression()
                elif algo == "Random Forest":
                    from sklearn.ensemble import RandomForestRegressor
                    model = RandomForestRegressor()
                elif algo == "Ridge Regression":
                    from sklearn.linear_model import Ridge
                    model = Ridge()
                elif algo == "Lasso Regression":
                    from sklearn.linear_model import Lasso
                    model = Lasso()
                elif algo == "SVR":
                    from sklearn.svm import SVR
                    model = SVR()
                elif algo == "XGBoost":
                    import xgboost as xgb
                    model = xgb.XGBRegressor()
                else:
                    raise Exception("Unsupported algorithm for regression.")
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
                import numpy as np
                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                result += f"R^2: {r2:.4f}\nMAE: {mae:.4f}\nRMSE: {rmse:.4f}\n"
                # Feature importance
                if hasattr(model, 'feature_importances_'):
                    importances = model.feature_importances_
                    fi_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances}).sort_values('Importance', ascending=False)
                    result += f"\nFeature Importance:\n{fi_df.to_string(index=False)}\n"
                predictions = pd.DataFrame({"y_true": y_test, "y_pred": y_pred}, index=X_test.index)
            else:
                result += "Unknown model type."
        except Exception as e:
            result += f"Error: {e}"
        self.ml_results_text.delete(1.0, tk.END)
        self.ml_results_text.insert(tk.END, result)
        # Show plot if any
        if hasattr(self, 'ml_plot_canvas') and self.ml_plot_canvas:
            self.ml_plot_canvas.get_tk_widget().destroy()
            self.ml_plot_canvas = None
        if plot_fig is not None:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            self.ml_plot_canvas = FigureCanvasTkAgg(plot_fig, master=self.ml_plot_frame)
            self.ml_plot_canvas.draw()
            widget = self.ml_plot_canvas.get_tk_widget()
            widget.pack(fill="both", expand=True)
            widget.update_idletasks()
            widget.minsize(400, 300)
            plt.close(plot_fig)
        self.ml_last_predictions = predictions
    def export_ml_predictions(self):
        if self.ml_last_predictions is None:
            messagebox.showwarning("Warning", "No predictions to export.")
            return
        file_path = filedialog.asksaveasfilename(
            title="Export Predictions",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            self.ml_last_predictions.to_excel(file_path)
            messagebox.showinfo("Success", f"Predictions exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export predictions: {e}")

    def refresh_machine_learning_tab(self):
        # Update target and features dropdowns/listbox
        if hasattr(self, 'ml_target_option'):
            self.ml_target_option.configure(values=self.get_all_columns())
            if self.get_all_columns():
                self.ml_target_option.set(self.get_all_columns()[0])
        if hasattr(self, 'ml_features_listbox'):
            self.ml_features_listbox.delete(0, tk.END)
            for col in self.get_all_columns():
                self.ml_features_listbox.insert(tk.END, col)
        if hasattr(self, 'ml_results_text'):
            self.ml_results_text.delete(1.0, tk.END)
        if hasattr(self, 'ml_last_predictions'):
            self.ml_last_predictions = None
        if hasattr(self, 'ml_algo_option') and hasattr(self, 'ml_type_option'):
            self.ml_algo_option.configure(values=self.get_ml_algorithms(self.ml_type_option.get()))
            self.ml_algo_option.set(self.get_ml_algorithms(self.ml_type_option.get())[0])

class DataCleaningReport:
    """Class to record data cleaning operations for PDF report"""
    def __init__(self):
        self.operations = []
        
    def add_operation(self, operation_type: str, details: Dict[str, Any]):
        """Add a cleaning operation to the report"""
        self.operations.append({
            'operation_type': operation_type,
            'details': details
        })
        
    def get_report_summary(self) -> str:
        """Get a summary of all cleaning operations"""
        if not self.operations:
            return "No data cleaning operations performed."
            
        summary = "Data Cleaning Report Summary:\n\n"
        for op in self.operations:
            summary += f"{op['operation_type']}\n"
            for key, value in op['details'].items():
                summary += f"  - {key}: {value}\n"
            summary += "\n"
        return summary
        
    def clear_operations(self):
        """Clear all recorded operations"""
        self.operations = []

class ChartReport:
    """Class to record chart operations for PDF report"""
    def __init__(self):
        self.charts = []
        
    def add_chart(self, chart_type: str, x_column: str, y_column: str, description: str, figure=None):
        """Add a chart to the report"""
        self.charts.append({
            'chart_type': chart_type,
            'x_column': x_column,
            'y_column': y_column,
            'description': description,
            'figure': figure
        })
        
    def get_report_summary(self) -> str:
        """Get a summary of all charts"""
        if not self.charts:
            return "No charts created."
            
        summary = "Dashboard Charts Summary:\n\n"
        for i, chart in enumerate(self.charts, 1):
            summary += f"Chart {i}:\n"
            summary += f"  - Type: {chart['chart_type']}\n"
            summary += f"  - X Column: {chart['x_column']}\n"
            summary += f"  - Y Column: {chart['y_column']}\n"
            summary += f"  - Description: {chart['description']}\n\n"
        return summary
        
    def clear_charts(self):
        """Clear all recorded charts"""
        self.charts = []

if __name__ == "__main__":
    app = DataAnalysisApp()
    app.run()
