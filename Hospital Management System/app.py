import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QFormLayout, QComboBox, QDateEdit, QTimeEdit,
                             QMessageBox, QDialog, QTextEdit, QGroupBox, QSpinBox, QGridLayout,
                             QHeaderView, QFrame, QStackedWidget, QCheckBox)
from PyQt5.QtCore import Qt, QDate, QTime, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator

class HospitalManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize menu bar
        self.create_menu_bar()
        
        # Initialize database
        self.init_database()
        
        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create header
        self.create_header()
        
        # Create main stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Create and add dashboard widget
        self.dashboard_widget = self.create_dashboard()
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # Create and add patient management widget
        self.patient_widget = self.create_patient_management()
        self.stacked_widget.addWidget(self.patient_widget)
        
        # Create and add doctor management widget
        self.doctor_widget = self.create_doctor_management()
        self.stacked_widget.addWidget(self.doctor_widget)
        
        # Create and add appointment widget
        self.appointment_widget = self.create_appointment_management()
        self.stacked_widget.addWidget(self.appointment_widget)
        
        # Create and add billing widget
        self.billing_widget = self.create_billing_management()
        self.stacked_widget.addWidget(self.billing_widget)
        
        # Set default screen to dashboard
        self.stacked_widget.setCurrentIndex(0)
    def create_menu_bar(self):
        """Create menu bar with navigation and options."""
        menu_bar = self.menuBar()
    
        # 🔹 File Menu
        file_menu = menu_bar.addMenu("File")
    
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
    
        # 🔹 Navigation Menu
        nav_menu = menu_bar.addMenu("Navigate")
    
        dashboard_action = nav_menu.addAction("Dashboard")
        dashboard_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(0))
    
        patient_action = nav_menu.addAction("Patients")
        patient_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(1))
    
        doctor_action = nav_menu.addAction("Doctors")
        doctor_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(2))
    
        appointment_action = nav_menu.addAction("Appointments")
        appointment_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(3))
    
        billing_action = nav_menu.addAction("Billing")
        billing_action.triggered.connect(lambda: self.stacked_widget.setCurrentIndex(4))
    
        # 🔹 Help Menu
        help_menu = menu_bar.addMenu("Help")
    
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about_dialog)
    
    def show_about_dialog(self):
        """Show the about dialog with additional details and styling."""
        about_text = """
        <h2 style="color: #2E86C1;">Hospital Management System</h2>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Description:</strong> A comprehensive system designed for managing hospital operations, patient records, and billing.</p>
        
        <h3>Features:</h3>
        <ul>
            <li>🏥 Patient Management</li>
            <li>👨‍⚕️ Doctor Management</li>
            <li>📅 Appointment Scheduling</li>
            <li>💰 Billing & Payments</li>
            <li>📊 Reporting & Analytics</li>
        </ul>
        
        <p>For any inquiries or support, please contact:</p>
        <p><strong>Email:</strong> support@hospitalmanagement.com</p>
        <p><strong>Website:</strong> <a href="https://hospitalmanagement.com">hospitalmanagement.com</a></p>
        
        <p style="color: #2980B9;">© 2025 - Developed by <strong>Mohamed Hussien</strong></p>
        """
        
        QMessageBox.about(self, "About Hospital Management System", about_text)


  
    def create_header(self):
        """Create header with navigation buttons"""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Hospital Management System")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Navigation buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.patient_btn = QPushButton("Patients")
        self.doctor_btn = QPushButton("Doctors")
        self.appointment_btn = QPushButton("Appointments")
        self.billing_btn = QPushButton("Billing")
        
        # Connect buttons to navigation
        self.dashboard_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.patient_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.doctor_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.appointment_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.billing_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.dashboard_btn)
        button_layout.addWidget(self.patient_btn)
        button_layout.addWidget(self.doctor_btn)
        button_layout.addWidget(self.appointment_btn)
        button_layout.addWidget(self.billing_btn)
        
        # Add title and buttons to header
        header_layout.addWidget(title_label)
        
        # Add the button layout to main layout
        self.main_layout.addLayout(header_layout)
        self.main_layout.addLayout(button_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separator)
        
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        try:
            # Connect to database (creates if not exists)
            self.conn = sqlite3.connect('hospital.db')
            self.cursor = self.conn.cursor()
            
            # Create patients table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    gender TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    address TEXT,
                    blood_group TEXT,
                    diagnosis TEXT,
                    admission_date TEXT,
                    discharge_date TEXT
                )
            ''')
            
            # Create doctors table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    email TEXT,
                    availability TEXT,
                    qualification TEXT
                )
            ''')
            
            # Create appointments table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    purpose TEXT,
                    status TEXT DEFAULT 'Scheduled',
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (doctor_id) REFERENCES doctors (id)
                )
            ''')
            
            # Create billing table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS billing (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    bill_date TEXT NOT NULL,
                    services TEXT,
                    medicines TEXT,
                    consultation_fee REAL,
                    medicine_charges REAL,
                    room_charges REAL,
                    misc_charges REAL,
                    total_amount REAL,
                    payment_status TEXT DEFAULT 'Pending',
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Commit changes
            self.conn.commit()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {e}")
    
    def create_dashboard(self):
        """Create dashboard widget with summary information"""
        dashboard = QWidget()
        layout = QVBoxLayout(dashboard)
        
        # Dashboard title
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Statistics section
        stats_layout = QGridLayout()
        
        # Patient stats
        patient_group = QGroupBox("Patients")
        patient_layout = QVBoxLayout()
        self.total_patients_label = QLabel("Total Patients: Loading...")
        patient_layout.addWidget(self.total_patients_label)
        patient_group.setLayout(patient_layout)
        
        # Doctor stats
        doctor_group = QGroupBox("Doctors")
        doctor_layout = QVBoxLayout()
        self.total_doctors_label = QLabel("Total Doctors: Loading...")
        doctor_layout.addWidget(self.total_doctors_label)
        doctor_group.setLayout(doctor_layout)
        
        # Appointment stats
        appointment_group = QGroupBox("Appointments")
        appointment_layout = QVBoxLayout()
        self.today_appointments_label = QLabel("Today's Appointments: Loading...")
        self.pending_appointments_label = QLabel("Pending Appointments: Loading...")
        appointment_layout.addWidget(self.today_appointments_label)
        appointment_layout.addWidget(self.pending_appointments_label)
        appointment_group.setLayout(appointment_layout)
        
        # Billing stats
        billing_group = QGroupBox("Billing")
        billing_layout = QVBoxLayout()
        self.pending_bills_label = QLabel("Pending Bills: Loading...")
        self.total_revenue_label = QLabel("Total Revenue: Loading...")
        billing_layout.addWidget(self.pending_bills_label)
        billing_layout.addWidget(self.total_revenue_label)
        billing_group.setLayout(billing_layout)
        
        # Add groups to layout
        stats_layout.addWidget(patient_group, 0, 0)
        stats_layout.addWidget(doctor_group, 0, 1)
        stats_layout.addWidget(appointment_group, 1, 0)
        stats_layout.addWidget(billing_group, 1, 1)
        
        layout.addLayout(stats_layout)
        
        # Quick actions section
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        add_patient_btn = QPushButton("Add New Patient")
        add_patient_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        add_doctor_btn = QPushButton("Add New Doctor")
        add_doctor_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        
        add_appointment_btn = QPushButton("Schedule Appointment")
        add_appointment_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        
        create_bill_btn = QPushButton("Create New Bill")
        create_bill_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        actions_layout.addWidget(add_patient_btn)
        actions_layout.addWidget(add_doctor_btn)
        actions_layout.addWidget(add_appointment_btn)
        actions_layout.addWidget(create_bill_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # Connect dashboard update function
        dashboard.showEvent = lambda event: self.update_dashboard_stats()
        
        return dashboard
    
    def update_dashboard_stats(self):
        """Update the statistics displayed on the dashboard"""
        try:
            # Get patient count
            self.cursor.execute("SELECT COUNT(*) FROM patients")
            patient_count = self.cursor.fetchone()[0]
            self.total_patients_label.setText(f"Total Patients: {patient_count}")
            
            # Get doctor count
            self.cursor.execute("SELECT COUNT(*) FROM doctors")
            doctor_count = self.cursor.fetchone()[0]
            self.total_doctors_label.setText(f"Total Doctors: {doctor_count}")
            
            # Get today's appointments
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", (today,))
            today_appointments = self.cursor.fetchone()[0]
            self.today_appointments_label.setText(f"Today's Appointments: {today_appointments}")
            
            # Get pending appointments
            self.cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'Scheduled'")
            pending_appointments = self.cursor.fetchone()[0]
            self.pending_appointments_label.setText(f"Pending Appointments: {pending_appointments}")
            
            # Get pending bills
            self.cursor.execute("SELECT COUNT(*) FROM billing WHERE payment_status = 'Pending'")
            pending_bills = self.cursor.fetchone()[0]
            self.pending_bills_label.setText(f"Pending Bills: {pending_bills}")
            
            # Get total revenue
            self.cursor.execute("SELECT SUM(total_amount) FROM billing WHERE payment_status = 'Paid'")
            total_revenue = self.cursor.fetchone()[0]
            if total_revenue is None:
                total_revenue = 0
            self.total_revenue_label.setText(f"Total Revenue: ${total_revenue:.2f}")
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to update dashboard: {e}")
    
    def create_patient_management(self):
        """Create patient management widget"""
        patient_widget = QWidget()
        layout = QVBoxLayout(patient_widget)
        
        # Patient Management title
        title = QLabel("Patient Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget for different patient operations
        patient_tabs = QTabWidget()
        
        # Add patient tab
        add_patient_tab = QWidget()
        self.create_add_patient_tab(add_patient_tab)
        patient_tabs.addTab(add_patient_tab, "Add Patient")
        
        # View patients tab
        view_patients_tab = QWidget()
        self.create_view_patients_tab(view_patients_tab)
        patient_tabs.addTab(view_patients_tab, "View Patients")
        
        layout.addWidget(patient_tabs)
        
        # Connect update function when tab is shown
        patient_tabs.currentChanged.connect(self.refresh_patient_data)
        
        return patient_widget
    
    def create_add_patient_tab(self, tab):
        """Create the add patient tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for patient details
        form_layout = QFormLayout()
        
        # Patient form fields
        self.patient_name = QLineEdit()
        self.patient_age = QSpinBox()
        self.patient_age.setRange(0, 120)
        
        self.patient_gender = QComboBox()
        self.patient_gender.addItems(["Male", "Female", "Other"])
        
        self.patient_contact = QLineEdit()
        # Validate phone number
        regex = QRegExp("^[0-9+()-]{10,15}$")
        validator = QRegExpValidator(regex)
        self.patient_contact.setValidator(validator)
        
        self.patient_address = QTextEdit()
        self.patient_address.setMaximumHeight(60)
        
        self.patient_blood_group = QComboBox()
        self.patient_blood_group.addItems(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
        
        self.patient_diagnosis = QLineEdit()
        
        self.patient_admission_date = QDateEdit()
        self.patient_admission_date.setCalendarPopup(True)
        self.patient_admission_date.setDate(QDate.currentDate())
        
        self.patient_discharge_date = QDateEdit()
        self.patient_discharge_date.setCalendarPopup(True)
        self.patient_discharge_date.setDate(QDate.currentDate())
        self.patient_discharge_date.setEnabled(False)
        
        self.is_admitted = QCheckBox("Patient is being admitted")
        self.is_admitted.stateChanged.connect(self.toggle_discharge_date)
        # Add fields to form
        form_layout.addRow("Name:", self.patient_name)
        form_layout.addRow("Age:", self.patient_age)
        form_layout.addRow("Gender:", self.patient_gender)
        form_layout.addRow("Contact:", self.patient_contact)
        form_layout.addRow("Address:", self.patient_address)
        form_layout.addRow("Blood Group:", self.patient_blood_group)
        form_layout.addRow("Diagnosis:", self.patient_diagnosis)
        form_layout.addRow("Admission Date:", self.patient_admission_date)
        form_layout.addRow("", self.is_admitted)
        form_layout.addRow("Discharge Date:", self.patient_discharge_date)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add save button
        save_button = QPushButton("Save Patient")
        save_button.clicked.connect(self.save_patient)
        layout.addWidget(save_button)
        
        # Add some stretching space
        layout.addStretch()
    
    def toggle_discharge_date(self, state):
        """Toggle discharge date field based on admission status"""
        if state == Qt.Checked:
            self.patient_discharge_date.setEnabled(False)
        else:
            self.patient_discharge_date.setEnabled(True)
    
    def clear_patient_form(self):
        """Clear all fields in the patient form"""
        self.patient_name.clear()
        self.patient_age.setValue(0)
        self.patient_gender.setCurrentIndex(0)
        self.patient_contact.clear()
        self.patient_address.clear()
        self.patient_blood_group.setCurrentIndex(8)  # Unknown
        self.patient_diagnosis.clear()
        self.patient_admission_date.setDate(QDate.currentDate())
        self.patient_discharge_date.setDate(QDate.currentDate())
        self.is_admitted.setChecked(False)
    
    def create_view_patients_tab(self, tab):
        """Create the view patients tab"""
        layout = QVBoxLayout(tab)
        
        # Search fields
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.patient_search = QLineEdit()
        self.patient_search.setPlaceholderText("Search by name, contact, or diagnosis...")
        self.patient_search.textChanged.connect(self.filter_patients)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.patient_search)
        
        layout.addLayout(search_layout)
        
        # Create table for patients
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(10)
        self.patients_table.setHorizontalHeaderLabels([
            "ID", "Name", "Age", "Gender", "Contact", "Address", 
            "Blood Group", "Diagnosis", "Admission Date", "Discharge Date"
        ])
        
        # Set table properties
        self.patients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patients_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.patients_table)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_patient)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_patient)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_patient_data)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
    
    def refresh_patient_data(self):
        """Refresh the patients table with data from database"""
        try:
            # Clear existing data
            self.patients_table.setRowCount(0)
            
            # Get data from database
            self.cursor.execute("SELECT * FROM patients ORDER BY name")
            patients = self.cursor.fetchall()
            
            # Populate table
            for row_num, patient in enumerate(patients):
                self.patients_table.insertRow(row_num)
                for col_num, data in enumerate(patient):
                    item = QTableWidgetItem(str(data))
                    # Make ID column non-editable
                    if col_num == 0:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.patients_table.setItem(row_num, col_num, item)
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load patient data: {e}")
    
    def filter_patients(self):
        """Filter patient records based on search text"""
        search_text = self.patient_search.text().lower()
        
        for row in range(self.patients_table.rowCount()):
            match_found = False
            
            # Check name, contact and diagnosis columns (1, 4, 7)
            for col in [1, 4, 7]:
                cell_text = self.patients_table.item(row, col).text().lower()
                if search_text in cell_text:
                    match_found = True
                    break
            
            # Show/hide row based on match
            self.patients_table.setRowHidden(row, not match_found)
    
    def edit_patient(self):
        """Open dialog to edit selected patient"""
        selected_rows = self.patients_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to edit.")
            return
        
        # Get patient ID from the first column
        patient_id = self.patients_table.item(selected_rows[0].row(), 0).text()
        
        # Create edit dialog
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Patient")
        edit_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(edit_dialog)
        form_layout = QFormLayout()
        
        # Get patient data
        self.cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient_data = self.cursor.fetchone()
        
        if not patient_data:
            QMessageBox.warning(self, "Error", "Patient data not found.")
            return
        
        # Create form fields with current data
        name_edit = QLineEdit(patient_data[1])
        age_edit = QSpinBox()
        age_edit.setRange(0, 120)
        age_edit.setValue(patient_data[2])
        
        gender_edit = QComboBox()
        gender_edit.addItems(["Male", "Female", "Other"])
        gender_edit.setCurrentText(patient_data[3])
        
        contact_edit = QLineEdit(patient_data[4])
        
        address_edit = QTextEdit()
        address_edit.setPlainText(patient_data[5])
        address_edit.setMaximumHeight(60)
        
        blood_group_edit = QComboBox()
        blood_group_edit.addItems(["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown"])
        blood_group_edit.setCurrentText(patient_data[6] if patient_data[6] else "Unknown")
        
        diagnosis_edit = QLineEdit(patient_data[7] if patient_data[7] else "")
        
        admission_date_edit = QDateEdit()
        admission_date_edit.setCalendarPopup(True)
        if patient_data[8]:
            admission_date_edit.setDate(QDate.fromString(patient_data[8], "yyyy-MM-dd"))
        else:
            admission_date_edit.setDate(QDate.currentDate())
        
        discharge_date_edit = QDateEdit()
        discharge_date_edit.setCalendarPopup(True)
        is_admitted = QCheckBox("Patient is still admitted")
        
        if patient_data[9]:
            discharge_date_edit.setDate(QDate.fromString(patient_data[9], "yyyy-MM-dd"))
            discharge_date_edit.setEnabled(True)
            is_admitted.setChecked(False)
        else:
            discharge_date_edit.setDate(QDate.currentDate())
            discharge_date_edit.setEnabled(False)
            is_admitted.setChecked(True)
        
        # Connect checkbox to discharge date
        is_admitted.stateChanged.connect(
            lambda state: discharge_date_edit.setEnabled(not state == Qt.Checked)
        )
        
        # Add fields to form
        form_layout.addRow("Name:", name_edit)
        form_layout.addRow("Age:", age_edit)
        form_layout.addRow("Gender:", gender_edit)
        form_layout.addRow("Contact:", contact_edit)
        form_layout.addRow("Address:", address_edit)
        form_layout.addRow("Blood Group:", blood_group_edit)
        form_layout.addRow("Diagnosis:", diagnosis_edit)
        form_layout.addRow("Admission Date:", admission_date_edit)
        form_layout.addRow("", is_admitted)
        form_layout.addRow("Discharge Date:", discharge_date_edit)
        
        dialog_layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        dialog_layout.addLayout(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(edit_dialog.reject)
        save_btn.clicked.connect(lambda: self.save_edited_patient(
            edit_dialog,
            patient_id,
            name_edit.text(),
            age_edit.value(),
            gender_edit.currentText(),
            contact_edit.text(),
            address_edit.toPlainText(),
            blood_group_edit.currentText(),
            diagnosis_edit.text(),
            admission_date_edit.date().toString("yyyy-MM-dd"),
            "" if is_admitted.isChecked() else discharge_date_edit.date().toString("yyyy-MM-dd")
        ))
        
        # Show dialog
        edit_dialog.exec_()
    
    def save_edited_patient(self, dialog, patient_id, name, age, gender, contact, address, 
                           blood_group, diagnosis, admission_date, discharge_date):
        """Save edited patient data to database"""
        try:
            # Validate required fields
            if not name or not contact:
                QMessageBox.warning(self, "Validation Error", "Name and Contact are required fields.")
                return
            
            # Update database
            self.cursor.execute('''
                UPDATE patients
                SET name = ?, age = ?, gender = ?, contact = ?, address = ?,
                    blood_group = ?, diagnosis = ?, admission_date = ?, discharge_date = ?
                WHERE id = ?
            ''', (name, age, gender, contact, address, blood_group, diagnosis, 
                 admission_date, discharge_date, patient_id))
            
            self.conn.commit()
            
            # Close dialog and refresh
            dialog.accept()
            self.refresh_patient_data()
            
            QMessageBox.information(self, "Success", "Patient record updated successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update patient record: {e}")
    
    def delete_patient(self):
        """Delete selected patient"""
        selected_rows = self.patients_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to delete.")
            return
        
        # Get patient ID from the first column
        patient_id = self.patients_table.item(selected_rows[0].row(), 0).text()
        patient_name = self.patients_table.item(selected_rows[0].row(), 1).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete patient '{patient_name}'?\n\n"
            "This will also delete all appointments and bills for this patient.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Begin transaction
                self.conn.execute("BEGIN TRANSACTION")
                
                # Delete related appointments
                self.cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
                
                # Delete related bills
                self.cursor.execute("DELETE FROM billing WHERE patient_id = ?", (patient_id,))
                
                # Delete patient
                self.cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                
                # Commit transaction
                self.conn.commit()
                
                # Refresh table
                self.refresh_patient_data()
                
                QMessageBox.information(self, "Success", "Patient and related records deleted successfully!")
                
            except sqlite3.Error as e:
                # Rollback in case of error
                self.conn.rollback()
                QMessageBox.critical(self, "Database Error", f"Failed to delete patient: {e}")
    
    def create_doctor_management(self):
        """Create doctor management widget"""
        doctor_widget = QWidget()
        layout = QVBoxLayout(doctor_widget)
        
        # Doctor Management title
        title = QLabel("Doctor Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget for different doctor operations
        doctor_tabs = QTabWidget()
        
        # Add doctor tab
        add_doctor_tab = QWidget()
        self.create_add_doctor_tab(add_doctor_tab)
        doctor_tabs.addTab(add_doctor_tab, "Add Doctor")
        
        # View doctors tab
        view_doctors_tab = QWidget()
        self.create_view_doctors_tab(view_doctors_tab)
        doctor_tabs.addTab(view_doctors_tab, "View Doctors")
        
        layout.addWidget(doctor_tabs)
        
        # Connect update function when tab is shown
        doctor_tabs.currentChanged.connect(self.refresh_doctor_data)
        
        return doctor_widget
    
    def create_add_doctor_tab(self, tab):
        """Create the add doctor tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for doctor details
        form_layout = QFormLayout()
        
        # Doctor form fields
        self.doctor_name = QLineEdit()
        
        self.doctor_specialization = QComboBox()
        self.doctor_specialization.addItems([
            "General Medicine", "Cardiology", "Neurology", "Orthopedics", 
            "Pediatrics", "Gynecology", "Dermatology", "Ophthalmology",
            "ENT", "Psychiatry", "Radiology", "Surgery", "Other"
        ])
        
        self.doctor_contact = QLineEdit()
        # Validate phone number
        regex = QRegExp("^[0-9+()-]{10,15}$")
        validator = QRegExpValidator(regex)
        self.doctor_contact.setValidator(validator)
        
        self.doctor_email = QLineEdit()
        
        self.doctor_qualification = QLineEdit()
        
        self.doctor_availability = QTextEdit()
        self.doctor_availability.setMaximumHeight(60)
        self.doctor_availability.setPlaceholderText("Mon-Fri: 9AM-5PM, Sat: 10AM-2PM")
        
        # Add fields to form
        form_layout.addRow("Name:", self.doctor_name)
        form_layout.addRow("Specialization:", self.doctor_specialization)
        form_layout.addRow("Contact:", self.doctor_contact)
        form_layout.addRow("Email:", self.doctor_email)
        form_layout.addRow("Qualification:", self.doctor_qualification)
        form_layout.addRow("Availability:", self.doctor_availability)
        
        # Add form to layout
        layout.addLayout(form_layout)
        
        # Add save button
        save_button = QPushButton("Save Doctor")
        save_button.clicked.connect(self.save_doctor)
        layout.addWidget(save_button)
        
        # Add some stretching space
        layout.addStretch()
    
    def save_doctor(self):
        """Save doctor data to database and refresh dropdown."""
        try:
            if not self.doctor_name.text() or not self.doctor_contact.text():
                QMessageBox.warning(self, "Validation Error", "Name and Contact are required fields.")
                return
    
            name = self.doctor_name.text()
            specialization = self.doctor_specialization.currentText()
            contact = self.doctor_contact.text()
            email = self.doctor_email.text()
            qualification = self.doctor_qualification.text()
            availability = self.doctor_availability.toPlainText()
    
            self.cursor.execute('''
                INSERT INTO doctors (name, specialization, contact, email, qualification, availability)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, specialization, contact, email, qualification, availability))
    
            self.conn.commit()
    
            self.clear_doctor_form()
            self.refresh_doctor_data()
            self.refresh_doctor_dropdown()  # **🔹 Fix: Refresh dropdown after adding a doctor**
            QMessageBox.information(self, "Success", "Doctor record saved successfully!")
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save doctor record: {e}")

    def clear_doctor_form(self):
        """Clear all fields in the doctor form"""
        self.doctor_name.clear()
        self.doctor_specialization.setCurrentIndex(0)
        self.doctor_contact.clear()
        self.doctor_email.clear()
        self.doctor_qualification.clear()
        self.doctor_availability.clear()
    
    def create_view_doctors_tab(self, tab):
        """Create the view doctors tab"""
        layout = QVBoxLayout(tab)
        
        # Search fields
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.doctor_search = QLineEdit()
        self.doctor_search.setPlaceholderText("Search by name, specialization, or contact...")
        self.doctor_search.textChanged.connect(self.filter_doctors)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.doctor_search)
        
        layout.addLayout(search_layout)
        
        # Create table for doctors
        self.doctors_table = QTableWidget()
        self.doctors_table.setColumnCount(7)
        self.doctors_table.setHorizontalHeaderLabels([
            "ID", "Name", "Specialization", "Contact", "Email", "Qualification", "Availability"
        ])
        
        # Set table properties
        self.doctors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.doctors_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.doctors_table)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_doctor)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_doctor)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_doctor_data)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
    
    def refresh_doctor_data(self):
        """Refresh the doctors table with data from database"""
        try:
            # Clear existing data
            self.doctors_table.setRowCount(0)
            
            # Get data from database
            self.cursor.execute("SELECT * FROM doctors ORDER BY name")
            doctors = self.cursor.fetchall()
            
            # Populate table
            for row_num, doctor in enumerate(doctors):
                self.doctors_table.insertRow(row_num)
                for col_num, data in enumerate(doctor):
                    item = QTableWidgetItem(str(data))
                    # Make ID column non-editable
                    if col_num == 0:
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.doctors_table.setItem(row_num, col_num, item)
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load doctor data: {e}")
    
    def filter_doctors(self):
        """Filter doctor records based on search text"""
        search_text = self.doctor_search.text().lower()
        
        for row in range(self.doctors_table.rowCount()):
            match_found = False
            
            # Check name, specialization and contact columns (1, 2, 3)
            for col in [1, 2, 3]:
                cell_text = self.doctors_table.item(row, col).text().lower()
                if search_text in cell_text:
                    match_found = True
                    break
            
            # Show/hide row based on match
            self.doctors_table.setRowHidden(row, not match_found)
    
    def edit_doctor(self):
        """Open dialog to edit selected doctor"""
        selected_rows = self.doctors_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to edit.")
            return
        
        # Get doctor ID from the first column
        doctor_id = self.doctors_table.item(selected_rows[0].row(), 0).text()
        
        # Create edit dialog
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Doctor")
        edit_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(edit_dialog)
        form_layout = QFormLayout()
        
        # Get doctor data
        self.cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        doctor_data = self.cursor.fetchone()
        
        if not doctor_data:
            QMessageBox.warning(self, "Error", "Doctor data not found.")
            return
        
        # Create form fields with current data
        name_edit = QLineEdit(doctor_data[1])
        
        specialization_edit = QComboBox()
        specialization_edit.addItems([
            "General Medicine", "Cardiology", "Neurology", "Orthopedics", 
            "Pediatrics", "Gynecology", "Dermatology", "Ophthalmology",
            "ENT", "Psychiatry", "Radiology", "Surgery", "Other"
        ])
        specialization_edit.setCurrentText(doctor_data[2])
        
        contact_edit = QLineEdit(doctor_data[3])
        email_edit = QLineEdit(doctor_data[4] if doctor_data[4] else "")
        qualification_edit = QLineEdit(doctor_data[5] if doctor_data[5] else "")
        
        availability_edit = QTextEdit()
        availability_edit.setPlainText(doctor_data[6] if doctor_data[6] else "")
        availability_edit.setMaximumHeight(60)
        
        # Add fields to form
        form_layout.addRow("Name:", name_edit)
        form_layout.addRow("Specialization:", specialization_edit)
        form_layout.addRow("Contact:", contact_edit)
        form_layout.addRow("Email:", email_edit)
        form_layout.addRow("Qualification:", qualification_edit)
        form_layout.addRow("Availability:", availability_edit)
        
        dialog_layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        dialog_layout.addLayout(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(edit_dialog.reject)
        save_btn.clicked.connect(lambda: self.save_edited_doctor(
            edit_dialog,
            doctor_id,
            name_edit.text(),
            specialization_edit.currentText(),
            contact_edit.text(),
            email_edit.text(),
            qualification_edit.text(),
            availability_edit.toPlainText()
        ))
        
        # Show dialog
        edit_dialog.exec_()
    
    def save_edited_doctor(self, dialog, doctor_id, name, specialization, contact, 
                          email, qualification, availability):
        """Save edited doctor data to database"""
        try:
            # Validate required fields
            if not name or not contact:
                QMessageBox.warning(self, "Validation Error", "Name and Contact are required fields.")
                return
            
            # Update database
            self.cursor.execute('''
                UPDATE doctors
                SET name = ?, specialization = ?, contact = ?, email = ?, 
                    qualification = ?, availability = ?
                WHERE id = ?
            ''', (name, specialization, contact, email, qualification, availability, doctor_id))
            
            self.conn.commit()
            
            # Close dialog and refresh
            dialog.accept()
            self.refresh_doctor_data()
            
            QMessageBox.information(self, "Success", "Doctor record updated successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update doctor record: {e}")
    
    def delete_doctor(self):
        """Delete selected doctor"""
        selected_rows = self.doctors_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a doctor to delete.")
            return
        
        # Get doctor ID from the first column
        doctor_id = self.doctors_table.item(selected_rows[0].row(), 0).text()
        doctor_name = self.doctors_table.item(selected_rows[0].row(), 1).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete doctor '{doctor_name}'?\n\n"
            "This will also delete all appointments for this doctor.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Begin transaction
                self.conn.execute("BEGIN TRANSACTION")
                
                # Delete related appointments
                self.cursor.execute("DELETE FROM appointments WHERE doctor_id = ?", (doctor_id,))
                
                # Delete doctor
                self.cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
                
                # Commit transaction
                self.conn.commit()
                
                # Refresh table
                self.refresh_doctor_data()
                
                QMessageBox.information(self, "Success", "Doctor and related records deleted successfully!")
                
            except sqlite3.Error as e:
                # Rollback in case of error
                self.conn.rollback()
                QMessageBox.critical(self, "Database Error", f"Failed to delete doctor: {e}")
    
    def create_appointment_management(self):
        """Create appointment management widget."""
        appointment_widget = QWidget()
        layout = QVBoxLayout(appointment_widget)
    
        # Title
        title = QLabel("Appointment Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
    
        # Create tab widget for different appointment operations
        appointment_tabs = QTabWidget()
    
        # Schedule appointment tab
        schedule_tab = QWidget()
        self.create_schedule_appointment_tab(schedule_tab)
        appointment_tabs.addTab(schedule_tab, "Schedule Appointment")
    
        # View appointments tab
        view_tab = QWidget()
        self.create_view_appointments_tab(view_tab)
        appointment_tabs.addTab(view_tab, "View Appointments")
    
        layout.addWidget(appointment_tabs)
    
        # **🔹 Fix: Refresh dropdowns when the tab is opened**
        appointment_tabs.currentChanged.connect(lambda: self.refresh_dropdowns())
    
        return appointment_widget
    def refresh_dropdowns(self):
        """Refresh both patient and doctor dropdowns dynamically."""
        self.refresh_patient_dropdown()
        self.refresh_doctor_dropdown()
    
    def save_appointment(self):
        """Save appointment data to database and refresh appointment list."""
        try:
            # Ensure patient and doctor are selected
            if self.appointment_patient.count() == 0 or self.appointment_doctor.count() == 0:
                QMessageBox.warning(self, "Error", "Please select both a patient and a doctor.")
                return
            
            # Get values from form
            patient_id = self.appointment_patient.currentData()
            doctor_id = self.appointment_doctor.currentData()
            appointment_date = self.appointment_date.date().toString("yyyy-MM-dd")
            appointment_time = self.appointment_time.time().toString("hh:mm AP")
            purpose = self.appointment_purpose.text()
            status = self.appointment_status.currentText()
    
            # Insert into database
            self.cursor.execute('''
                INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, purpose, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (patient_id, doctor_id, appointment_date, appointment_time, purpose, status))
    
            self.conn.commit()
    
            # Clear form fields after successful save
            self.appointment_purpose.clear()
            self.appointment_date.setDate(QDate.currentDate())
            self.appointment_time.setTime(QTime.currentTime())
            self.appointment_status.setCurrentIndex(0)
    
            QMessageBox.information(self, "Success", "Appointment scheduled successfully!")
    
            # Refresh appointment table
            self.refresh_appointment_data()
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to schedule appointment: {e}")

    def create_schedule_appointment_tab(self, tab):
        """Create the schedule appointment tab"""
        layout = QVBoxLayout(tab)
        
        form_layout = QFormLayout()
        
        # Patient selection
        self.appointment_patient = QComboBox()
        self.refresh_patient_dropdown()
        
        # Doctor selection
        self.appointment_doctor = QComboBox()
        self.refresh_doctor_dropdown()
        
        # Date and time
        self.appointment_date = QDateEdit()
        self.appointment_date.setCalendarPopup(True)
        self.appointment_date.setDate(QDate.currentDate())
        
        self.appointment_time = QTimeEdit()
        self.appointment_time.setTime(QTime.currentTime())
        self.appointment_time.setDisplayFormat("hh:mm AP")
        
        # Purpose
        self.appointment_purpose = QLineEdit()
        
        # Status
        self.appointment_status = QComboBox()
        self.appointment_status.addItems(["Scheduled", "Completed", "Cancelled", "No-show"])
        
        # Add to form
        form_layout.addRow("Patient:", self.appointment_patient)
        form_layout.addRow("Doctor:", self.appointment_doctor)
        form_layout.addRow("Date:", self.appointment_date)
        form_layout.addRow("Time:", self.appointment_time)
        form_layout.addRow("Purpose:", self.appointment_purpose)
        form_layout.addRow("Status:", self.appointment_status)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save Appointment")
        save_button.clicked.connect(self.save_appointment)  # 🔹 Connect to save_appointment
        
        refresh_button = QPushButton("Refresh Lists")
        refresh_button.clicked.connect(self.refresh_dropdowns)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def refresh_patient_dropdown(self):
        """Refresh the patient dropdown list"""
        try:
            self.appointment_patient.clear()
            
            # Get patients from database
            self.cursor.execute("SELECT id, name FROM patients ORDER BY name")
            patients = self.cursor.fetchall()
            
            # Add to dropdown
            for patient in patients:
                self.appointment_patient.addItem(f"{patient[1]} (ID: {patient[0]})", patient[0])
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load patients: {e}")
    
    def refresh_doctor_dropdown(self):
        """Refresh the doctor dropdown list"""
        try:
            self.appointment_doctor.clear()
            
            # Get doctors from database
            self.cursor.execute("SELECT id, name, specialization FROM doctors ORDER BY name")
            doctors = self.cursor.fetchall()
            
            # Add to dropdown
            for doctor in doctors:
                self.appointment_doctor.addItem(f"{doctor[1]} - {doctor[2]} (ID: {doctor[0]})", doctor[0])
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load doctors: {e}")
    
    def refresh_dropdowns(self):
        """Refresh both patient and doctor dropdowns"""
        self.refresh_patient_dropdown()
        self.refresh_doctor_dropdown()
    
    def save_patient(self):
        """Save patient data to database and refresh dropdown."""
        try:
            if not self.patient_name.text() or not self.patient_contact.text():
                QMessageBox.warning(self, "Validation Error", "Name and Contact are required fields.")
                return
    
            name = self.patient_name.text()
            age = self.patient_age.value()
            gender = self.patient_gender.currentText()
            contact = self.patient_contact.text()
            address = self.patient_address.toPlainText()
            blood_group = self.patient_blood_group.currentText()
            diagnosis = self.patient_diagnosis.text()
            admission_date = self.patient_admission_date.date().toString("yyyy-MM-dd")
            discharge_date = "" if self.is_admitted.isChecked() else self.patient_discharge_date.date().toString("yyyy-MM-dd")
    
            self.cursor.execute('''
                INSERT INTO patients (name, age, gender, contact, address, blood_group, diagnosis, admission_date, discharge_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, contact, address, blood_group, diagnosis, admission_date, discharge_date))
    
            self.conn.commit()
    
            self.clear_patient_form()
            self.refresh_patient_data()
            self.refresh_patient_dropdown()  # **🔹 Fix: Refresh dropdown after adding a patient**
            QMessageBox.information(self, "Success", "Patient record saved successfully!")
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to save patient record: {e}")

    def create_view_appointments_tab(self, tab):
        """Create the view appointments tab"""
        layout = QVBoxLayout(tab)
        
        # Date filter
        filter_layout = QHBoxLayout()
        date_label = QLabel("Filter by date:")
        self.appointment_date_filter = QDateEdit()
        self.appointment_date_filter.setCalendarPopup(True)
        self.appointment_date_filter.setDate(QDate.currentDate())
        
        apply_filter_btn = QPushButton("Apply Filter")
        apply_filter_btn.clicked.connect(self.filter_appointments_by_date)
        
        clear_filter_btn = QPushButton("Show All")
        clear_filter_btn.clicked.connect(self.show_all_appointments)
        
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.appointment_date_filter)
        filter_layout.addWidget(apply_filter_btn)
        filter_layout.addWidget(clear_filter_btn)
        
        layout.addLayout(filter_layout)
        
        # Search field
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.appointment_search = QLineEdit()
        self.appointment_search.setPlaceholderText("Search by patient or doctor name...")
        self.appointment_search.textChanged.connect(self.filter_appointments)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.appointment_search)
        
        layout.addLayout(search_layout)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(8)
        self.appointments_table.setHorizontalHeaderLabels([
            "ID", "Patient", "Doctor", "Date", "Time", "Purpose", "Status", "Actions"
        ])
        
        # Set table properties
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.appointments_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.appointments_table)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_appointment)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_appointment)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_appointment_data)
        
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
    
    def refresh_appointment_data(self):
        """Refresh the appointments table with data from database"""
        try:
            # Clear existing data
            self.appointments_table.setRowCount(0)
            
            # Get data from database with patient and doctor names
            self.cursor.execute('''
                SELECT a.id, p.name, d.name, a.appointment_date, a.appointment_time, 
                       a.purpose, a.status, a.patient_id, a.doctor_id
                FROM appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN doctors d ON a.doctor_id = d.id
                ORDER BY a.appointment_date DESC, a.appointment_time ASC
            ''')
            
            appointments = self.cursor.fetchall()
            
            # Populate table
            for row_num, appt in enumerate(appointments):
                self.appointments_table.insertRow(row_num)
                
                # Add appointment details
                for col_num in range(7):
                    item = QTableWidgetItem(str(appt[col_num]))
                    if col_num == 0:  # Make ID column non-editable
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.appointments_table.setItem(row_num, col_num, item)
                
                # Add status change button
                status_cell = QWidget()
                status_layout = QHBoxLayout(status_cell)
                status_layout.setContentsMargins(2, 2, 2, 2)
                
                if appt[6] == "Scheduled":
                    complete_btn = QPushButton("Complete")
                    complete_btn.clicked.connect(lambda checked, row=row_num, id=appt[0]: 
                                              self.update_appointment_status(id, "Completed"))
                    status_layout.addWidget(complete_btn)
                
                self.appointments_table.setCellWidget(row_num, 7, status_cell)
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load appointments: {e}")
    
    def update_appointment_status(self, appointment_id, new_status):
        """Update the status of an appointment"""
        try:
            self.cursor.execute('''
                UPDATE appointments
                SET status = ?
                WHERE id = ?
            ''', (new_status, appointment_id))
            
            self.conn.commit()
            self.refresh_appointment_data()
            
            QMessageBox.information(self, "Success", f"Appointment marked as {new_status}.")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update appointment: {e}")
    
    def filter_appointments_by_date(self):
        """Filter appointments by the selected date"""
        selected_date = self.appointment_date_filter.date().toString("yyyy-MM-dd")
        
        for row in range(self.appointments_table.rowCount()):
            date_cell = self.appointments_table.item(row, 3).text()
            self.appointments_table.setRowHidden(row, date_cell != selected_date)
    
    def show_all_appointments(self):
        """Show all appointments (clear date filter)"""
        for row in range(self.appointments_table.rowCount()):
            self.appointments_table.setRowHidden(row, False)
    
    def filter_appointments(self):
        """Filter appointments based on search text"""
        search_text = self.appointment_search.text().lower()
        
        for row in range(self.appointments_table.rowCount()):
            match_found = False
            
            # Check patient and doctor name columns (1, 2)
            for col in [1, 2]:
                cell_text = self.appointments_table.item(row, col).text().lower()
                if search_text in cell_text:
                    match_found = True
                    break
            
            # Show/hide row based on match
            self.appointments_table.setRowHidden(row, not match_found)
    
    def edit_appointment(self):
        """Open dialog to edit selected appointment"""
        selected_rows = self.appointments_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to edit.")
            return
        
        # Get appointment ID from the first column
        row = selected_rows[0].row()
        appointment_id = self.appointments_table.item(row, 0).text()
        
        # Create edit dialog
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Appointment")
        edit_dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(edit_dialog)
        form_layout = QFormLayout()
        
        # Get appointment data
        self.cursor.execute('''
            SELECT * FROM appointments WHERE id = ?
        ''', (appointment_id,))
        appointment_data = self.cursor.fetchone()
        
        if not appointment_data:
            QMessageBox.warning(self, "Error", "Appointment data not found.")
            return
        
        # Get patient and doctor lists
        patient_combo = QComboBox()
        doctor_combo = QComboBox()
        
        # Get patients
        self.cursor.execute("SELECT id, name FROM patients ORDER BY name")
        patients = self.cursor.fetchall()
        for patient in patients:
            patient_combo.addItem(f"{patient[1]} (ID: {patient[0]})", patient[0])
            if patient[0] == appointment_data[1]:
                patient_combo.setCurrentIndex(patient_combo.count() - 1)
        
        # Get doctors
        self.cursor.execute("SELECT id, name, specialization FROM doctors ORDER BY name")
        doctors = self.cursor.fetchall()
        for doctor in doctors:
            doctor_combo.addItem(f"{doctor[1]} - {doctor[2]} (ID: {doctor[0]})", doctor[0])
            if doctor[0] == appointment_data[2]:
                doctor_combo.setCurrentIndex(doctor_combo.count() - 1)
        
        # Date and time
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.fromString(appointment_data[3], "yyyy-MM-dd"))
        
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("hh:mm AP")
        time_parts = appointment_data[4].split()
        time_string = time_parts[0]
        if len(time_parts) > 1:
            am_pm = time_parts[1]
            if am_pm.upper() == "PM":
                hour, minute = map(int, time_string.split(':'))
                if hour < 12:
                    hour += 12
                time_string = f"{hour}:{minute}"
        time_edit.setTime(QTime.fromString(time_string, "hh:mm"))
        
        # Purpose
        purpose_edit = QLineEdit(appointment_data[5] if appointment_data[5] else "")
        
        # Status
        status_combo = QComboBox()
        status_combo.addItems(["Scheduled", "Completed", "Cancelled", "No-show"])
        status_combo.setCurrentText(appointment_data[6])
        
        # Add fields to form
        form_layout.addRow("Patient:", patient_combo)
        form_layout.addRow("Doctor:", doctor_combo)
        form_layout.addRow("Date:", date_edit)
        form_layout.addRow("Time:", time_edit)
        form_layout.addRow("Purpose:", purpose_edit)
        form_layout.addRow("Status:", status_combo)
        
        dialog_layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        
        button_box.addWidget(save_btn)
        button_box.addWidget(cancel_btn)
        dialog_layout.addLayout(button_box)
        
        # Connect buttons
        cancel_btn.clicked.connect(edit_dialog.reject)
        save_btn.clicked.connect(lambda: self.save_edited_appointment(
            edit_dialog,
            appointment_id,
            patient_combo.currentData(),
            doctor_combo.currentData(),
            date_edit.date().toString("yyyy-MM-dd"),
            time_edit.time().toString("hh:mm AP"),
            purpose_edit.text(),
            status_combo.currentText()
        ))
        
        # Show dialog
        edit_dialog.exec_()
    
    def save_edited_appointment(self, dialog, appointment_id, patient_id, doctor_id, 
                               appointment_date, appointment_time, purpose, status):
        """Save edited appointment data to database"""
        try:
            # Update database
            self.cursor.execute('''
                UPDATE appointments
                SET patient_id = ?, doctor_id = ?, appointment_date = ?, 
                    appointment_time = ?, purpose = ?, status = ?
                WHERE id = ?
            ''', (patient_id, doctor_id, appointment_date, appointment_time, 
                 purpose, status, appointment_id))
            
            self.conn.commit()
            
            # Close dialog and refresh
            dialog.accept()
            self.refresh_appointment_data()
            
            QMessageBox.information(self, "Success", "Appointment updated successfully!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update appointment: {e}")
    
    def delete_appointment(self):
        """Delete selected appointment"""
        selected_rows = self.appointments_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to delete.")
            return
        
        # Get appointment ID from the first column
        row = selected_rows[0].row()
        appointment_id = self.appointments_table.item(row, 0).text()
        
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete this appointment?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Delete appointment
                self.cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                self.conn.commit()
                
                # Refresh table
                self.refresh_appointment_data()
                
                QMessageBox.information(self, "Success", "Appointment deleted successfully!")
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete appointment: {e}")
    
    def create_billing_management(self):
        """Create billing management widget"""
        billing_widget = QWidget()
        layout = QVBoxLayout(billing_widget)
        
        # Billing Management title
        title = QLabel("Billing Management")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create tab widget for different billing operations
        billing_tabs = QTabWidget()
        
        # Create bill tab
        create_bill_tab = QWidget()
        self.create_new_bill_tab(create_bill_tab)
        billing_tabs.addTab(create_bill_tab, "Create Bill")
        
        # View bills tab
        view_bills_tab = QWidget()
        self.create_view_bills_tab(view_bills_tab)
        billing_tabs.addTab(view_bills_tab, "View Bills")
        
        layout.addWidget(billing_tabs)
        
        # Connect update function when tab is shown
        billing_tabs.currentChanged.connect(self.refresh_billing_data)
        
        return billing_widget
    
    def create_new_bill_tab(self, tab):
        """Create the new bill tab"""
        layout = QVBoxLayout(tab)
        
        # Form layout for bill details
        form_layout = QFormLayout()
        
        # Patient selection
        self.bill_patient = QComboBox()
        self.refresh_bill_patient_dropdown()
        
        # Bill date
        self.bill_date = QDateEdit()
        self.bill_date.setCalendarPopup(True)
        self.bill_date.setDate(QDate.currentDate())
        
        # Services
        self.bill_services = QTextEdit()
        self.bill_services.setMaximumHeight(80)
        self.bill_services.setPlaceholderText("Enter services separated by commas...")
        
        # Medicines
        self.bill_medicines = QTextEdit()
        self.bill_medicines.setMaximumHeight(80)
        self.bill_medicines.setPlaceholderText("Enter medicines separated by commas...")
        
        # Charges
        self.consultation_fee = QLineEdit("0.00")
        self.medicine_charges = QLineEdit("0.00")
        self.room_charges = QLineEdit("0.00")
        self.misc_charges = QLineEdit("0.00")
        
        # Payment status
        self.payment_status = QComboBox()
        self.payment_status.addItems(["Pending", "Paid", "Partially Paid"])
        
        # Add fields to form
        form_layout.addRow("Patient:", self.bill_patient)
        form_layout.addRow("Bill Date:", self.bill_date)
        form_layout.addRow("Services:", self.bill_services)
        form_layout.addRow("Medicines:", self.bill_medicines)
        form_layout.addRow("Consultation Fee ($):", self.consultation_fee)
        form_layout.addRow("Medicine Charges ($):", self.medicine_charges)
        form_layout.addRow("Room Charges ($):", self.room_charges)
        form_layout.addRow("Miscellaneous Charges ($):", self.misc_charges)
        form_layout.addRow("Payment Status:", self.payment_status)
        
        # Total amount (calculated)
        self.total_amount_label = QLabel("Total Amount: $0.00")
        self.total_amount_label.setFont(QFont("Arial", 10, QFont.Bold))
        form_layout.addRow("", self.total_amount_label)
        
        # Connect charge fields to calculate total
        self.consultation_fee.textChanged.connect(self.calculate_total)
        self.medicine_charges.textChanged.connect(self.calculate_total)
        self.room_charges.textChanged.connect(self.calculate_total)
        self.misc_charges.textChanged.connect(self.calculate_total)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Generate Bill")
        save_button.clicked.connect(self.save_bill)
        
        refresh_button = QPushButton("Refresh Patients")
        refresh_button.clicked.connect(self.refresh_bill_patient_dropdown)
        
        calculate_button = QPushButton("Calculate Total")
        calculate_button.clicked.connect(self.calculate_total)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(calculate_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def refresh_bill_patient_dropdown(self):
        """Refresh the patient dropdown in billing tab"""
        try:
            self.bill_patient.clear()
            
            # Get patients from database
            self.cursor.execute("SELECT id, name FROM patients ORDER BY name")
            patients = self.cursor.fetchall()
            
            # Add to dropdown
            for patient in patients:
                self.bill_patient.addItem(f"{patient[1]} (ID: {patient[0]})", patient[0])
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load patients: {e}")
    
    def calculate_total(self):
        """Calculate the total bill amount"""
        try:
            # Get values from form fields
            consultation = float(self.consultation_fee.text() or 0)
            medicines = float(self.medicine_charges.text() or 0)
            room = float(self.room_charges.text() or 0)
            misc = float(self.misc_charges.text() or 0)
            
            # Calculate total
            total = consultation + medicines + room + misc
            
            # Update label
            self.total_amount_label.setText(f"Total Amount: ${total:.2f}")
            
        except ValueError:
            self.total_amount_label.setText("Total Amount: Invalid input")
    
    def save_bill(self):
        """Save bill data to database"""
        try:
            # Check if patient is selected
            if self.bill_patient.count() == 0:
                QMessageBox.warning(self, "Error", "Please select a patient.")
                return
            
            # Calculate total amount
            try:
                consultation = float(self.consultation_fee.text() or 0)
                medicines = float(self.medicine_charges.text() or 0)
                room = float(self.room_charges.text() or 0)
                misc = float(self.misc_charges.text() or 0)
                total = consultation + medicines + room + misc
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter valid numeric values for charges.")
                return
            
            # Get values
            patient_id = self.bill_patient.currentData()
            bill_date = self.bill_date.date().toString("yyyy-MM-dd")
            services = self.bill_services.toPlainText()
            medicines_text = self.bill_medicines.toPlainText()
            payment_status = self.payment_status.currentText()
            
            # Insert into database
            self.cursor.execute('''
                INSERT INTO billing (
                    patient_id, bill_date, services, medicines, 
                    consultation_fee, medicine_charges, room_charges, misc_charges,
                    total_amount, payment_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id, bill_date, services, medicines_text,
                consultation, medicines, room, misc,
                total, payment_status
            ))
            
            self.conn.commit()
            
            # Clear form
            self.bill_services.clear()
            self.bill_medicines.clear()
            self.consultation_fee.setText("0.00")
            self.medicine_charges.setText("0.00")
            self.room_charges.setText("0.00")
            self.misc_charges.setText("0.00")
            self.payment_status.setCurrentIndex(0)
            
            QMessageBox.information(self, "Success", "Bill generated successfully!")
            
            # Refresh billing table
            self.refresh_billing_data()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to generate bill: {e}")
    
    def create_view_bills_tab(self, tab):
        """Create the view bills tab"""
        layout = QVBoxLayout(tab)
        
        # Search field
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.bill_search = QLineEdit()
        self.bill_search.setPlaceholderText("Search by patient name...")
        self.bill_search.textChanged.connect(self.filter_bills)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.bill_search)
        
        layout.addLayout(search_layout)
        
        # Filter by payment status
        status_layout = QHBoxLayout()
        status_label = QLabel("Filter by status:")
        self.bill_status_filter = QComboBox()
        self.bill_status_filter.addItems(["All", "Pending", "Paid", "Partially Paid"])
        self.bill_status_filter.currentTextChanged.connect(self.filter_bills_by_status)
        
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.bill_status_filter)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        # Bills table
        self.bills_table = QTableWidget()
        self.bills_table.setColumnCount(9)
        self.bills_table.setHorizontalHeaderLabels([
            "ID", "Patient", "Date", "Services", "Medicines", 
            "Total Amount", "Payment Status", "Actions", "Print"
        ])
        
        # Set table properties
        self.bills_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bills_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.bills_table)
        
        # Buttons for actions
        button_layout = QHBoxLayout()
        
        view_details_button = QPushButton("View Details")
        view_details_button.clicked.connect(self.view_bill_details)
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_bill)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_bill)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_billing_data)
        
        button_layout.addWidget(view_details_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
    
    def refresh_billing_data(self):
        """Refresh the bills table with data from database"""
        try:
            # Clear existing data
            self.bills_table.setRowCount(0)
            
            # Get data from database with patient names
            self.cursor.execute('''
                SELECT b.id, p.name, b.bill_date, b.services, b.medicines, 
                       b.total_amount, b.payment_status, b.patient_id
                FROM billing b
                JOIN patients p ON b.patient_id = p.id
                ORDER BY b.bill_date DESC
            ''')
            
            bills = self.cursor.fetchall()
            
            # Populate table
            for row_num, bill in enumerate(bills):
                self.bills_table.insertRow(row_num)
                
                # Add bill details
                for col_num in range(7):
                    text = bill[col_num]
                    if col_num == 5:  # Format total amount
                        text = f"${bill[col_num]:.2f}"
                    item = QTableWidgetItem(str(text))
                    if col_num == 0:  # Make ID column non-editable
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.bills_table.setItem(row_num, col_num, item)
                
                # Add status update button
                status_cell = QWidget()
                status_layout = QHBoxLayout(status_cell)
                status_layout.setContentsMargins(2, 2, 2, 2)
                
                if bill[6] != "Paid":
                    mark_paid_btn = QPushButton("Mark Paid")
                    mark_paid_btn.clicked.connect(lambda checked, row=row_num, id=bill[0]: 
                                             self.update_bill_status(id, "Paid"))
                    status_layout.addWidget(mark_paid_btn)
                
                self.bills_table.setCellWidget(row_num, 7, status_cell)
                
                # Add print button
                print_cell = QWidget()
                print_layout = QHBoxLayout(print_cell)
                print_layout.setContentsMargins(2, 2, 2, 2)
                
                print_btn = QPushButton("Print")
                print_btn.clicked.connect(lambda checked, bill_id=bill[0], patient_id=bill[7]: 
                                     self.print_bill(bill_id, patient_id))
                print_layout.addWidget(print_btn)
                
                self.bills_table.setCellWidget(row_num, 8, print_cell)
                
            # Resize columns to content
            self.bills_table.resizeColumnsToContents()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to refresh billing data: {str(e)}")
    
    def filter_bills(self):
        """Filter bills based on search text"""
        search_text = self.bill_search.text().strip().lower()
    
        for row in range(self.bills_table.rowCount()):
            match_found = False
            
            # Check if the patient name cell exists before accessing text
            item = self.bills_table.item(row, 1)
            patient_name = item.text().strip().lower() if item else ""
    
            if search_text in patient_name:
                match_found = True
            
            # Show/hide rows based on match
            self.bills_table.setRowHidden(row, not match_found)

    def filter_bills_by_status(self):
        """Filter bills based on payment status"""
        selected_status = self.bill_status_filter.currentText()
    
        for row in range(self.bills_table.rowCount()):
            item = self.bills_table.item(row, 6)  # Payment Status column
            if item:
                payment_status = item.text().strip()
    
                # Show all if "All" is selected, otherwise match the status
                should_hide = selected_status != "All" and payment_status != selected_status
                self.bills_table.setRowHidden(row, should_hide)
    
    def view_bill_details(self):
        """Show details of the selected bill."""
        selected_rows = self.bills_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a bill to view details.")
            return
    
        # Get bill ID from the first column
        bill_id = self.bills_table.item(selected_rows[0].row(), 0).text()
    
        try:
            # Fetch bill details from database
            self.cursor.execute('''
                SELECT b.id, p.name, b.bill_date, b.services, b.medicines, 
                       b.consultation_fee, b.medicine_charges, b.room_charges, 
                       b.misc_charges, b.total_amount, b.payment_status
                FROM billing b
                JOIN patients p ON b.patient_id = p.id
                WHERE b.id = ?
            ''', (bill_id,))
            
            bill = self.cursor.fetchone()
            if not bill:
                QMessageBox.warning(self, "Error", "Bill details not found.")
                return
    
            # Create dialog to show details
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle("Bill Details")
            details_dialog.setMinimumWidth(400)
            
            dialog_layout = QVBoxLayout(details_dialog)
            form_layout = QFormLayout()
            
            # Populate fields
            form_layout.addRow("Bill ID:", QLabel(str(bill[0])))
            form_layout.addRow("Patient Name:", QLabel(bill[1]))
            form_layout.addRow("Bill Date:", QLabel(bill[2]))
            form_layout.addRow("Services:", QLabel(bill[3] or "N/A"))
            form_layout.addRow("Medicines:", QLabel(bill[4] or "N/A"))
            form_layout.addRow("Consultation Fee:", QLabel(f"${bill[5]:.2f}"))
            form_layout.addRow("Medicine Charges:", QLabel(f"${bill[6]:.2f}"))
            form_layout.addRow("Room Charges:", QLabel(f"${bill[7]:.2f}"))
            form_layout.addRow("Misc Charges:", QLabel(f"${bill[8]:.2f}"))
            form_layout.addRow("Total Amount:", QLabel(f"${bill[9]:.2f}"))
            form_layout.addRow("Payment Status:", QLabel(bill[10]))
            
            dialog_layout.addLayout(form_layout)
    
            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(details_dialog.accept)
            dialog_layout.addWidget(close_btn)
    
            # Show dialog
            details_dialog.exec_()
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve bill details: {e}")
    def edit_bill(self):
        """Open dialog to edit selected bill."""
        selected_rows = self.bills_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a bill to edit.")
            return
    
        # Get bill ID from the first column
        bill_id = self.bills_table.item(selected_rows[0].row(), 0).text()
    
        try:
            # Fetch bill details from database
            self.cursor.execute('''
                SELECT b.id, b.patient_id, b.bill_date, b.services, b.medicines, 
                       b.consultation_fee, b.medicine_charges, b.room_charges, 
                       b.misc_charges, b.total_amount, b.payment_status
                FROM billing b
                WHERE b.id = ?
            ''', (bill_id,))
            
            bill = self.cursor.fetchone()
            if not bill:
                QMessageBox.warning(self, "Error", "Bill details not found.")
                return
    
            # Create edit dialog
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("Edit Bill")
            edit_dialog.setMinimumWidth(400)
    
            dialog_layout = QVBoxLayout(edit_dialog)
            form_layout = QFormLayout()
    
            # Patient (Display Only)
            self.cursor.execute("SELECT name FROM patients WHERE id = ?", (bill[1],))
            patient_name = self.cursor.fetchone()[0]
            patient_label = QLabel(patient_name)
    
            # Bill Date
            bill_date_edit = QDateEdit()
            bill_date_edit.setCalendarPopup(True)
            bill_date_edit.setDate(QDate.fromString(bill[2], "yyyy-MM-dd"))
    
            # Services & Medicines
            services_edit = QTextEdit()
            services_edit.setPlainText(bill[3] if bill[3] else "")
    
            medicines_edit = QTextEdit()
            medicines_edit.setPlainText(bill[4] if bill[4] else "")
    
            # Charges
            consultation_fee_edit = QLineEdit(str(bill[5]))
            medicine_charges_edit = QLineEdit(str(bill[6]))
            room_charges_edit = QLineEdit(str(bill[7]))
            misc_charges_edit = QLineEdit(str(bill[8]))
    
            # Payment Status
            payment_status_edit = QComboBox()
            payment_status_edit.addItems(["Pending", "Paid", "Partially Paid"])
            payment_status_edit.setCurrentText(bill[10])
    
            # Total Amount Label (Updated Automatically)
            total_amount_label = QLabel(f"Total Amount: ${bill[9]:.2f}")
    
            def calculate_total():
                """Recalculate the total amount dynamically."""
                try:
                    consultation = float(consultation_fee_edit.text() or 0)
                    medicines = float(medicine_charges_edit.text() or 0)
                    room = float(room_charges_edit.text() or 0)
                    misc = float(misc_charges_edit.text() or 0)
                    total = consultation + medicines + room + misc
                    total_amount_label.setText(f"Total Amount: ${total:.2f}")
                except ValueError:
                    total_amount_label.setText("Total Amount: Invalid input")
    
            # Connect changes to recalculate total
            consultation_fee_edit.textChanged.connect(calculate_total)
            medicine_charges_edit.textChanged.connect(calculate_total)
            room_charges_edit.textChanged.connect(calculate_total)
            misc_charges_edit.textChanged.connect(calculate_total)
    
            # Add fields to form
            form_layout.addRow("Patient:", patient_label)
            form_layout.addRow("Bill Date:", bill_date_edit)
            form_layout.addRow("Services:", services_edit)
            form_layout.addRow("Medicines:", medicines_edit)
            form_layout.addRow("Consultation Fee ($):", consultation_fee_edit)
            form_layout.addRow("Medicine Charges ($):", medicine_charges_edit)
            form_layout.addRow("Room Charges ($):", room_charges_edit)
            form_layout.addRow("Misc Charges ($):", misc_charges_edit)
            form_layout.addRow("Payment Status:", payment_status_edit)
            form_layout.addRow("", total_amount_label)
    
            dialog_layout.addLayout(form_layout)
    
            # Buttons
            button_box = QHBoxLayout()
            save_btn = QPushButton("Save Changes")
            cancel_btn = QPushButton("Cancel")
    
            button_box.addWidget(save_btn)
            button_box.addWidget(cancel_btn)
            dialog_layout.addLayout(button_box)
    
            # Connect buttons
            cancel_btn.clicked.connect(edit_dialog.reject)
            save_btn.clicked.connect(lambda: self.save_edited_bill(
                edit_dialog, bill_id, bill_date_edit.date().toString("yyyy-MM-dd"),
                services_edit.toPlainText(), medicines_edit.toPlainText(),
                consultation_fee_edit.text(), medicine_charges_edit.text(),
                room_charges_edit.text(), misc_charges_edit.text(),
                payment_status_edit.currentText()
            ))
    
            # Show dialog
            edit_dialog.exec_()
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to retrieve bill details: {e}")
    
   
    #This method updates the bill in the database.

    def save_edited_bill(self, dialog, bill_id, bill_date, services, medicines, 
                         consultation_fee, medicine_charges, room_charges, misc_charges, 
                         payment_status):
        """Save edited bill data to database."""
        try:
            # Validate inputs
            try:
                consultation_fee = float(consultation_fee or 0)
                medicine_charges = float(medicine_charges or 0)
                room_charges = float(room_charges or 0)
                misc_charges = float(misc_charges or 0)
                total_amount = consultation_fee + medicine_charges + room_charges + misc_charges
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter valid numeric values for charges.")
                return
    
            # Update database
            self.cursor.execute('''
                UPDATE billing
                SET bill_date = ?, services = ?, medicines = ?, 
                    consultation_fee = ?, medicine_charges = ?, room_charges = ?, 
                    misc_charges = ?, total_amount = ?, payment_status = ?
                WHERE id = ?
            ''', (bill_date, services, medicines, consultation_fee, medicine_charges,
                  room_charges, misc_charges, total_amount, payment_status, bill_id))
    
            self.conn.commit()
    
            # Close dialog and refresh data
            dialog.accept()
            self.refresh_billing_data()
    
            QMessageBox.information(self, "Success", "Bill updated successfully!")
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update bill: {e}")
    def delete_bill(self):
        """Delete selected bill from the database."""
        selected_rows = self.bills_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a bill to delete.")
            return
    
        # Get bill ID and patient name
        row = selected_rows[0].row()
        bill_id = self.bills_table.item(row, 0).text()
        patient_name = self.bills_table.item(row, 1).text()
    
        # Confirm deletion
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete this bill for {patient_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
    
        if confirm == QMessageBox.Yes:
            try:
                # Delete bill from database
                self.cursor.execute("DELETE FROM billing WHERE id = ?", (bill_id,))
                self.conn.commit()
    
                # Refresh table
                self.refresh_billing_data()
    
                QMessageBox.information(self, "Success", "Bill deleted successfully!")
    
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete bill: {e}")
    def print_bill(self, bill_id, patient_id):
        """Generate a printable bill summary."""
        try:
            # Fetch bill details from the database
            self.cursor.execute('''
                SELECT b.id, p.name, b.bill_date, b.services, b.medicines, 
                       b.consultation_fee, b.medicine_charges, b.room_charges, b.misc_charges, 
                       b.total_amount, b.payment_status
                FROM billing b
                JOIN patients p ON b.patient_id = p.id
                WHERE b.id = ? AND p.id = ?
            ''', (bill_id, patient_id))
    
            bill = self.cursor.fetchone()
    
            if not bill:
                QMessageBox.warning(self, "Error", "Bill details not found.")
                return
    
            # Formatting bill details
            bill_text = f"""
            <h2 style="color: #2E86C1;">Hospital Bill Receipt</h2>
            <p><strong>Bill ID:</strong> {bill[0]}</p>
            <p><strong>Patient Name:</strong> {bill[1]}</p>
            <p><strong>Date:</strong> {bill[2]}</p>
            
            <h3>Services:</h3>
            <p>{bill[3] if bill[3] else "N/A"}</p>
            
            <h3>Medicines:</h3>
            <p>{bill[4] if bill[4] else "N/A"}</p>
    
            <h3>Charges Breakdown:</h3>
            <ul>
                <li><strong>Consultation Fee:</strong> ${bill[5]:.2f}</li>
                <li><strong>Medicine Charges:</strong> ${bill[6]:.2f}</li>
                <li><strong>Room Charges:</strong> ${bill[7]:.2f}</li>
                <li><strong>Miscellaneous Charges:</strong> ${bill[8]:.2f}</li>
            </ul>
    
            <h3 style="color: #C0392B;">Total Amount: <strong>${bill[9]:.2f}</strong></h3>
            <p><strong>Payment Status:</strong> <span style="color: {'green' if bill[10] == 'Paid' else 'red'};">{bill[10]}</span></p>
    
            <p style="color: #2980B9;">© 2025 - Hospital Management System</p>
            """
    
            # Display bill details
            QMessageBox.about(self, "Bill Summary", bill_text)
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to fetch bill details: {e}")

    def closeEvent(self, event):
        """Handle application exit to close database connection."""
        self.conn.close()
        event.accept()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HospitalManagementSystem()
    window.show()
    sys.exit(app.exec_())
