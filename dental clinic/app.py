import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QStackedWidget, QPushButton, QLabel, QLineEdit, QComboBox, 
                           QTableWidget, QTableWidgetItem, QCalendarWidget, QTimeEdit, 
                           QTextEdit, QFormLayout, QGroupBox, QMessageBox, QDialog, 
                           QFileDialog, QTabWidget, QDateEdit, QSpinBox, QHeaderView, QStyleFactory)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QDate, QTime, QSize, QTimer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# Global Variables
APP_NAME = "Dental Clinic Management System"
DATABASE_NAME = "dental_clinic.db"
THEME = "Light"  # Default theme
ICONS_PATH = "icons/"  # Create a folder called 'icons' in the same directory as the script

# Define Color Schemes
LIGHT_THEME = {
    "primary": "#4a6fa5",
    "secondary": "#789ebf",
    "accent": "#1a365d",
    "background": "#f8f9fa",
    "sidebar": "#e9ecef",
    "text": "#212529",
    "button": "#4a6fa5",
    "button_text": "#ffffff",
    "hover": "#3a5c8c",
    "border": "#ced4da",
    "success": "#28a745",
    "error": "#dc3545",
    "warning": "#ffc107"
}

DARK_THEME = {
    "primary": "#375a7f",
    "secondary": "#5a7b9c",
    "accent": "#1e3c5a",
    "background": "#222",
    "sidebar": "#2d3436",
    "text": "#f8f9fa",
    "button": "#375a7f",
    "button_text": "#ffffff",
    "hover": "#2d4a6c",
    "border": "#495057",
    "success": "#2ecc71",
    "error": "#e74c3c",
    "warning": "#f39c12"
}

# Set active theme
ACTIVE_THEME = LIGHT_THEME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # Create Patients Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact TEXT,
            email TEXT,
            medical_history TEXT,
            registration_date TEXT
        )
        ''')
        
        # Create Appointments Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            appointment_date TEXT,
            appointment_time TEXT,
            doctor TEXT,
            notes TEXT,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
        ''')
        
        # Create Treatments Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS treatments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cost REAL NOT NULL
        )
        ''')
        
        # Create Billing Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            treatment_id INTEGER,
            doctor TEXT,
            cost REAL,
            payment_status TEXT,
            invoice_date TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (treatment_id) REFERENCES treatments (id)
        )
        ''')
        
        # Create Settings Table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clinic_name TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            theme TEXT
        )
        ''')
        
        # Insert default settings if not exist
        self.cursor.execute("SELECT COUNT(*) FROM settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
            INSERT INTO settings (clinic_name, address, phone, email, theme)
            VALUES (?, ?, ?, ?, ?)
            ''', ("Dental Clinic", "123 Main St", "555-1234", "info@dentalclinic.com", "Light"))
        
        # Insert sample treatments
        self.cursor.execute("SELECT COUNT(*) FROM treatments")
        if self.cursor.fetchone()[0] == 0:
            treatments = [
                ("Checkup", 50.00),
                ("Cleaning", 80.00),
                ("Filling", 120.00),
                ("Root Canal", 500.00),
                ("Crown", 800.00),
                ("Extraction", 150.00),
                ("Whitening", 300.00),
                ("Braces", 3000.00)
            ]
            self.cursor.executemany("INSERT INTO treatments (name, cost) VALUES (?, ?)", treatments)
            
        self.conn.commit()
    
    def close(self):
        self.conn.close()


class StyleHelper:
    @staticmethod
    def set_theme(app, theme_name):
        global ACTIVE_THEME
        if theme_name == "Light":
            ACTIVE_THEME = LIGHT_THEME
        else:
            ACTIVE_THEME = DARK_THEME
        
        # Set application stylesheet
        app.setStyle(QStyleFactory.create("Fusion"))
        
        # Set palette
        palette = QPalette()
        if theme_name == "Dark":
            palette.setColor(QPalette.Window, QColor(ACTIVE_THEME["background"]))
            palette.setColor(QPalette.WindowText, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.Base, QColor(ACTIVE_THEME["sidebar"]))
            palette.setColor(QPalette.AlternateBase, QColor(ACTIVE_THEME["primary"]))
            palette.setColor(QPalette.ToolTipBase, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.ToolTipText, QColor(ACTIVE_THEME["background"]))
            palette.setColor(QPalette.Text, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.Button, QColor(ACTIVE_THEME["button"]))
            palette.setColor(QPalette.ButtonText, QColor(ACTIVE_THEME["button_text"]))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(ACTIVE_THEME["accent"]))
            palette.setColor(QPalette.Highlight, QColor(ACTIVE_THEME["secondary"]))
            palette.setColor(QPalette.HighlightedText, QColor(ACTIVE_THEME["text"]))
        else:
            palette.setColor(QPalette.Window, QColor(ACTIVE_THEME["background"]))
            palette.setColor(QPalette.WindowText, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.Base, QColor(ACTIVE_THEME["background"]))
            palette.setColor(QPalette.AlternateBase, QColor(ACTIVE_THEME["sidebar"]))
            palette.setColor(QPalette.ToolTipBase, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.ToolTipText, QColor(ACTIVE_THEME["background"]))
            palette.setColor(QPalette.Text, QColor(ACTIVE_THEME["text"]))
            palette.setColor(QPalette.Button, QColor(ACTIVE_THEME["button"]))
            palette.setColor(QPalette.ButtonText, QColor(ACTIVE_THEME["button_text"]))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(ACTIVE_THEME["accent"]))
            palette.setColor(QPalette.Highlight, QColor(ACTIVE_THEME["primary"]))
            palette.setColor(QPalette.HighlightedText, QColor(ACTIVE_THEME["button_text"]))
            
        app.setPalette(palette)
        
        # Additional stylesheet
        stylesheet = f"""
            QPushButton {{
                background-color: {ACTIVE_THEME["button"]};
                color: {ACTIVE_THEME["button_text"]};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACTIVE_THEME["hover"]};
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_THEME["accent"]};
            }}
            QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit, QSpinBox {{
                border: 1px solid {ACTIVE_THEME["border"]};
                padding: 5px;
                border-radius: 3px;
                background-color: {ACTIVE_THEME["background"]};
                color: {ACTIVE_THEME["text"]};
            }}
            QTableWidget {{
                border: 1px solid {ACTIVE_THEME["border"]};
                gridline-color: {ACTIVE_THEME["border"]};
                selection-background-color: {ACTIVE_THEME["secondary"]};
            }}
            QHeaderView::section {{
                background-color: {ACTIVE_THEME["primary"]};
                color: {ACTIVE_THEME["button_text"]};
                padding: 5px;
                border: 1px solid {ACTIVE_THEME["border"]};
                font-weight: bold;
            }}
            QTabWidget::pane {{
                border: 1px solid {ACTIVE_THEME["border"]};
                background-color: {ACTIVE_THEME["background"]};
            }}
            QTabBar::tab {{
                background-color: {ACTIVE_THEME["sidebar"]};
                color: {ACTIVE_THEME["text"]};
                padding: 8px 16px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {ACTIVE_THEME["primary"]};
                color: {ACTIVE_THEME["button_text"]};
            }}
            QGroupBox {{
                border: 1px solid {ACTIVE_THEME["border"]};
                margin-top: 20px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {ACTIVE_THEME["text"]};
            }}
        """
        app.setStyleSheet(stylesheet)


class CustomButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        
        self.setMinimumHeight(40)
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)


class SideBarButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
        
        self.setMinimumHeight(50)
        self.setMinimumWidth(200)
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.setFont(font)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACTIVE_THEME["sidebar"]};
                color: {ACTIVE_THEME["text"]};
                text-align: left;
                padding-left: 15px;
                border: none;
                border-radius: 0px;
            }}
            QPushButton:hover {{
                background-color: {ACTIVE_THEME["secondary"]};
                color: {ACTIVE_THEME["button_text"]};
            }}
            QPushButton:checked {{
                background-color: {ACTIVE_THEME["primary"]};
                color: {ACTIVE_THEME["button_text"]};
                border-left: 5px solid {ACTIVE_THEME["accent"]};
            }}
        """)
        self.setCheckable(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        
    def init_ui(self):
        # Set window properties
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QHBoxLayout(self.central_widget)
        
        # Create sidebar and content area
        self.create_sidebar()
        self.create_content_area()
        
        # Set up stacked widget connections
        self.setup_connections()
        
        # Apply theme
        self.load_settings()
        
    def create_sidebar(self):
        # Create sidebar widget
        self.sidebar = QWidget()
        self.sidebar.setMinimumWidth(220)
        self.sidebar.setMaximumWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(0)
        
        # Add logo area
        self.logo_area = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_area)
        self.logo_layout.setContentsMargins(15, 15, 15, 15)
        
        self.logo_label = QLabel(APP_NAME)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.logo_label.setFont(font)
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet(f"color: {ACTIVE_THEME['accent']};")
        
        self.logo_layout.addWidget(self.logo_label)
        self.sidebar_layout.addWidget(self.logo_area)
        
        # Add sidebar buttons
        self.dashboard_btn = SideBarButton("Dashboard", None)
        self.patients_btn = SideBarButton("Patients", None)
        self.appointments_btn = SideBarButton("Appointments", None)
        self.billing_btn = SideBarButton("Billing", None)
        self.reports_btn = SideBarButton("Reports", None)
        self.settings_btn = SideBarButton("Settings", None)
        
        # Add buttons to sidebar
        self.sidebar_layout.addWidget(self.dashboard_btn)
        self.sidebar_layout.addWidget(self.patients_btn)
        self.sidebar_layout.addWidget(self.appointments_btn)
        self.sidebar_layout.addWidget(self.billing_btn)
        self.sidebar_layout.addWidget(self.reports_btn)
        self.sidebar_layout.addWidget(self.settings_btn)
        
        # Add stretch at the bottom
        self.sidebar_layout.addStretch()
        
        # Add clinic info at bottom
        self.clinic_info = QLabel("© 2025 Dental Clinic\nAll Rights Reserved")
        self.clinic_info.setAlignment(Qt.AlignCenter)
        self.clinic_info.setStyleSheet(f"color: {ACTIVE_THEME['text']}; padding: 10px;")
        self.sidebar_layout.addWidget(self.clinic_info)
        
        # Add sidebar to main layout
        self.main_layout.addWidget(self.sidebar)
        
    def create_content_area(self):
        # Create content widget
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        
        # Create pages
        self.dashboard_page = DashboardPage(self)
        self.patients_page = PatientsPage(self)
        self.appointments_page = AppointmentsPage(self)
        self.billing_page = BillingPage(self)
        self.reports_page = ReportsPage(self)
        self.settings_page = SettingsPage(self)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.patients_page)
        self.stacked_widget.addWidget(self.appointments_page)
        self.stacked_widget.addWidget(self.billing_page)
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.settings_page)
        
        # Add stacked widget to content layout
        self.content_layout.addWidget(self.stacked_widget)
        
        # Set content area to main layout
        self.main_layout.addWidget(self.content_area)
        
    def setup_connections(self):
        # Connect sidebar buttons to switch pages
        self.dashboard_btn.clicked.connect(lambda: self.change_page(0))
        self.patients_btn.clicked.connect(lambda: self.change_page(1))
        self.appointments_btn.clicked.connect(lambda: self.change_page(2))
        self.billing_btn.clicked.connect(lambda: self.change_page(3))
        self.reports_btn.clicked.connect(lambda: self.change_page(4))
        self.settings_btn.clicked.connect(lambda: self.change_page(5))
        
        # Set dashboard as active on start
        self.dashboard_btn.setChecked(True)
        
    def change_page(self, index):
        # Set all buttons unchecked
        for btn in [self.dashboard_btn, self.patients_btn, self.appointments_btn, 
                   self.billing_btn, self.reports_btn, self.settings_btn]:
            btn.setChecked(False)
        
        # Set the clicked button checked
        [self.dashboard_btn, self.patients_btn, self.appointments_btn, 
         self.billing_btn, self.reports_btn, self.settings_btn][index].setChecked(True)
        
        # Change stacked widget page
        self.stacked_widget.setCurrentIndex(index)
        
    def load_settings(self):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT theme FROM settings")
            theme = cursor.fetchone()[0]
            global THEME
            THEME = theme
            StyleHelper.set_theme(QApplication.instance(), THEME)
        except:
            pass
        
    def update_theme(self, theme_name):
        global THEME
        THEME = theme_name
        StyleHelper.set_theme(QApplication.instance(), THEME)
        
        cursor = self.db.conn.cursor()
        cursor.execute("UPDATE settings SET theme = ?", (theme_name,))
        self.db.conn.commit()
        
    def closeEvent(self, event):
        self.db.close()
        event.accept()


class DashboardPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title
        self.title = QLabel("Dashboard")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        
        # Quick access buttons
        self.quick_access_layout = QHBoxLayout()
        
        # Quick add patient
        self.add_patient_btn = CustomButton("Add Patient")
        self.add_patient_btn.clicked.connect(self.open_add_patient)
        
        # Quick add appointment
        self.add_appointment_btn = CustomButton("Add Appointment")
        self.add_appointment_btn.clicked.connect(self.open_add_appointment)
        
        # Quick create invoice
        self.create_invoice_btn = CustomButton("Create Invoice")
        self.create_invoice_btn.clicked.connect(self.open_create_invoice)
        
        # Add buttons to quick access layout
        self.quick_access_layout.addWidget(self.add_patient_btn)
        self.quick_access_layout.addWidget(self.add_appointment_btn)
        self.quick_access_layout.addWidget(self.create_invoice_btn)
        
        # Summary cards layout
        self.summary_layout = QHBoxLayout()
        
        # Create summary cards
        self.patients_summary = self.create_summary_card("Total Patients", self.get_patients_count())
        self.appointments_summary = self.create_summary_card("Today's Appointments", self.get_today_appointments_count())
        self.pending_summary = self.create_summary_card("Pending Payments", self.get_pending_payments_count())
        
        # Add cards to summary layout
        self.summary_layout.addWidget(self.patients_summary)
        self.summary_layout.addWidget(self.appointments_summary)
        self.summary_layout.addWidget(self.pending_summary)
        
        # Today's appointments section
        self.appointments_group = QGroupBox("Today's Appointments")
        self.appointments_layout = QVBoxLayout(self.appointments_group)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(5)
        self.appointments_table.setHorizontalHeaderLabels(["Time", "Patient", "Doctor", "Notes", "Status"])
        self.appointments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Load today's appointments
        self.load_today_appointments()
        
        # Add table to layout
        self.appointments_layout.addWidget(self.appointments_table)
        
        # Add all components to main layout
        self.layout.addWidget(self.title)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.quick_access_layout)
        self.layout.addSpacing(20)
        self.layout.addLayout(self.summary_layout)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.appointments_group)
        
        # Set up refresh timer for dashboard
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(60000)  # Refresh every minute
        
    def create_summary_card(self, title, value):
        card = QGroupBox()
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        title_label.setFont(font)
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        value_label.setFont(font)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def get_patients_count(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        count = cursor.fetchone()[0]
        return count
    
    def get_today_appointments_count(self):
        cursor = self.db.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE appointment_date = ?", (today,))
        count = cursor.fetchone()[0]
        return count
    
    def get_pending_payments_count(self):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM billing WHERE payment_status = 'Pending'")
        count = cursor.fetchone()[0]
        return count
    
    def load_today_appointments(self):
        cursor = self.db.conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT a.appointment_time, p.name, a.doctor, a.notes, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        """, (today,))
        
        appointments = cursor.fetchall()
        self.appointments_table.setRowCount(len(appointments))
        
        for i, appointment in enumerate(appointments):
            for j, value in enumerate(appointment):
                self.appointments_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def refresh_dashboard(self):
        # Update summary cards
        # Find the value labels (second child in each card)
        self.patients_summary.layout().itemAt(1).widget().setText(str(self.get_patients_count()))
        self.appointments_summary.layout().itemAt(1).widget().setText(str(self.get_today_appointments_count()))
        self.pending_summary.layout().itemAt(1).widget().setText(str(self.get_pending_payments_count()))
        
        # Reload appointments
        self.load_today_appointments()
    
    def open_add_patient(self):
        self.main_window.change_page(1)  # Go to Patients page
        self.main_window.patients_page.clear_patient_form()  # Reset the form
    
    def open_add_appointment(self):
        self.main_window.change_page(2)  # Go to Appointments page
        self.main_window.appointments_page.clear_appointment_form()  # Reset the form
    
    def open_create_invoice(self):
        self.main_window.change_page(3)  # Go to Billing page
        self.main_window.billing_page.clear_billing_form()  # Reset the form


class PatientsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title
        self.title = QLabel("Patient Management")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.patient_list_tab = QWidget()
        self.add_patient_tab = QWidget()
        
        self.tabs.addTab(self.patient_list_tab, "Patient List")
        self.tabs.addTab(self.add_patient_tab, "Add/Edit Patient")
        
        # Setup patient list tab
        self.setup_patient_list_tab()
        
        # Setup add patient tab
        self.setup_add_patient_tab()
        
        # Add components to main layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.tabs)
    
    def setup_patient_list_tab(self):
        # Create layout for patient list tab
        self.patient_list_layout = QVBoxLayout(self.patient_list_tab)
        
        # Search layout
        self.search_layout = QHBoxLayout()
        self.search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter name, email or contact...")
        self.search_input.textChanged.connect(self.search_patients)
        
        # Add search components to search layout
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)
        
        # Patient table
        self.patient_table = QTableWidget()
        self.patient_table.setColumnCount(7)
        self.patient_table.setHorizontalHeaderLabels(["ID", "Name", "Age", "Gender", "Contact", "Email", "Registration Date"])
        self.patient_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.patient_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        self.patient_table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire rows
        self.patient_table.setSelectionMode(QTableWidget.SingleSelection)  # Allow only single selection
        
        # Action buttons layout
        self.action_layout = QHBoxLayout()
        
        # View button
        self.view_btn = CustomButton("View Details")
        self.view_btn.clicked.connect(self.view_patient)
        
        # Edit button
        self.edit_btn = CustomButton("Edit")
        self.edit_btn.clicked.connect(self.edit_patient)
        
        # Delete button
        self.delete_btn = CustomButton("Delete")
        self.delete_btn.clicked.connect(self.delete_patient)
        
        # Add buttons to action layout
        self.action_layout.addWidget(self.view_btn)
        self.action_layout.addWidget(self.edit_btn)
        self.action_layout.addWidget(self.delete_btn)
        
        # Add components to patient list layout
        self.patient_list_layout.addLayout(self.search_layout)
        self.patient_list_layout.addWidget(self.patient_table)
        self.patient_list_layout.addLayout(self.action_layout)
        
        # Load patients
        self.load_patients()
    
    def setup_add_patient_tab(self):
        # Create layout for add patient tab
        self.add_patient_layout = QVBoxLayout(self.add_patient_tab)
        
        # Create form layout
        self.form_layout = QFormLayout()
        
        # Create form fields
        self.patient_id_input = QLineEdit()
        self.patient_id_input.setReadOnly(True)  # ID is read-only
        self.patient_id_input.hide()  # Hide ID field initially
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter patient full name")
        
        self.age_input = QSpinBox()
        self.age_input.setRange(0, 120)
        self.age_input.setValue(30)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        
        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter contact number")
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email address")
        
        self.medical_history_input = QTextEdit()
        self.medical_history_input.setPlaceholderText("Enter medical history and notes...")
        self.medical_history_input.setMinimumHeight(100)
        
        # Add fields to form layout
        self.form_layout.addRow("ID:", self.patient_id_input)
        self.form_layout.addRow("Name *:", self.name_input)
        self.form_layout.addRow("Age:", self.age_input)
        self.form_layout.addRow("Gender:", self.gender_input)
        self.form_layout.addRow("Contact *:", self.contact_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Medical History:", self.medical_history_input)
        
        # Form buttons layout
        self.form_buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_btn = CustomButton("Save Patient")
        self.save_btn.clicked.connect(self.save_patient)
        
        # Clear button
        self.clear_btn = CustomButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_patient_form)
        
        # Add buttons to form buttons layout
        self.form_buttons_layout.addWidget(self.save_btn)
        self.form_buttons_layout.addWidget(self.clear_btn)
        
        # Add form layout and buttons to add patient layout
        self.add_patient_layout.addLayout(self.form_layout)
        self.add_patient_layout.addLayout(self.form_buttons_layout)
        
    def load_patients(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name, age, gender, contact, email, registration_date
            FROM patients
            ORDER BY name
        """)
        
        patients = cursor.fetchall()
        self.patient_table.setRowCount(len(patients))
        
        for i, patient in enumerate(patients):
            for j, value in enumerate(patient):
                self.patient_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def search_patients(self):
        search_text = self.search_input.text().strip().lower()
        
        if not search_text:
            self.load_patients()
            return
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name, age, gender, contact, email, registration_date
            FROM patients
            WHERE LOWER(name) LIKE ? OR LOWER(email) LIKE ? OR LOWER(contact) LIKE ?
            ORDER BY name
        """, (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))
        
        patients = cursor.fetchall()
        self.patient_table.setRowCount(len(patients))
        
        for i, patient in enumerate(patients):
            for j, value in enumerate(patient):
                self.patient_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def view_patient(self):
        selected_rows = self.patient_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to view.")
            return
        
        # Get patient ID from the first column of the selected row
        patient_id = self.patient_table.item(selected_rows[0].row(), 0).text()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM patients WHERE id = ?
        """, (patient_id,))
        
        patient = cursor.fetchone()
        if not patient:
            QMessageBox.warning(self, "Error", "Patient not found.")
            return
        
        # Create message box with patient details
        msg = QMessageBox()
        msg.setWindowTitle("Patient Details")
        msg.setIcon(QMessageBox.Information)
        
        details = f"""
        <b>ID:</b> {patient[0]}
        <b>Name:</b> {patient[1]}
        <b>Age:</b> {patient[2]}
        <b>Gender:</b> {patient[3]}
        <b>Contact:</b> {patient[4]}
        <b>Email:</b> {patient[5]}
        <b>Medical History:</b> {patient[6]}
        <b>Registration Date:</b> {patient[7]}
        """
        
        msg.setText(details)
        msg.exec_()
    
    def edit_patient(self):
        selected_rows = self.patient_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to edit.")
            return
        
        # Get patient ID from the first column of the selected row
        patient_id = self.patient_table.item(selected_rows[0].row(), 0).text()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM patients WHERE id = ?
        """, (patient_id,))
        
        patient = cursor.fetchone()
        if not patient:
            QMessageBox.warning(self, "Error", "Patient not found.")
            return
        
        # Switch to add/edit tab
        self.tabs.setCurrentIndex(1)
        
        # Populate form fields
        self.patient_id_input.show()
        self.patient_id_input.setText(str(patient[0]))
        self.name_input.setText(patient[1])
        self.age_input.setValue(patient[2] if patient[2] else 0)
        
        # Set gender
        gender_index = self.gender_input.findText(patient[3])
        if gender_index >= 0:
            self.gender_input.setCurrentIndex(gender_index)
        
        self.contact_input.setText(patient[4] if patient[4] else "")
        self.email_input.setText(patient[5] if patient[5] else "")
        self.medical_history_input.setText(patient[6] if patient[6] else "")
        
        # Change button text
        self.save_btn.setText("Update Patient")
    
    def delete_patient(self):
        selected_rows = self.patient_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a patient to delete.")
            return
        
        # Get patient ID from the first column of the selected row
        patient_id = self.patient_table.item(selected_rows[0].row(), 0).text()
        patient_name = self.patient_table.item(selected_rows[0].row(), 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete patient {patient_name}?\n\n"
                                    f"This will delete all appointments and billing records for this patient.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db.conn.cursor()
                
                # Check if patient has appointments or billing records
                cursor.execute("SELECT COUNT(*) FROM appointments WHERE patient_id = ?", (patient_id,))
                appointment_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM billing WHERE patient_id = ?", (patient_id,))
                billing_count = cursor.fetchone()[0]
                
                # Start transaction
                self.db.conn.execute("BEGIN TRANSACTION")
                
                # Delete related records
                if appointment_count > 0:
                    cursor.execute("DELETE FROM appointments WHERE patient_id = ?", (patient_id,))
                
                if billing_count > 0:
                    cursor.execute("DELETE FROM billing WHERE patient_id = ?", (patient_id,))
                
                # Delete patient
                cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
                
                # Commit transaction
                self.db.conn.commit()
                
                QMessageBox.information(self, "Success", f"Patient {patient_name} and related records deleted successfully.")
                
                # Refresh patient list
                self.load_patients()
                
            except sqlite3.Error as e:
                # Rollback transaction on error
                self.db.conn.rollback()
                QMessageBox.critical(self, "Error", f"Failed to delete patient: {str(e)}")
    
    def save_patient(self):
        # Validate required fields
        name = self.name_input.text().strip()
        contact = self.contact_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Patient name is required.")
            return
        
        if not contact:
            QMessageBox.warning(self, "Validation Error", "Contact number is required.")
            return
        
        # Get other field values
        patient_id = self.patient_id_input.text().strip()
        age = self.age_input.value()
        gender = self.gender_input.currentText()
        email = self.email_input.text().strip()
        medical_history = self.medical_history_input.toPlainText().strip()
        
        try:
            cursor = self.db.conn.cursor()
            
            # If patient ID exists, update existing patient
            if patient_id:
                cursor.execute("""
                    UPDATE patients 
                    SET name = ?, age = ?, gender = ?, contact = ?, email = ?, medical_history = ?
                    WHERE id = ?
                """, (name, age, gender, contact, email, medical_history, patient_id))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "Patient updated successfully.")
                
            # Otherwise, insert new patient
            else:
                registration_date = datetime.now().strftime("%Y-%m-%d")
                
                cursor.execute("""
                    INSERT INTO patients (name, age, gender, contact, email, medical_history, registration_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, age, gender, contact, email, medical_history, registration_date))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "New patient added successfully.")
            
            # Clear form and refresh list
            self.clear_patient_form()
            self.load_patients()
            
            # Switch to patient list tab
            self.tabs.setCurrentIndex(0)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def clear_patient_form(self):
        # Hide and clear patient ID
        self.patient_id_input.hide()
        self.patient_id_input.clear()
        
        # Clear other fields
        self.name_input.clear()
        self.age_input.setValue(30)
        self.gender_input.setCurrentIndex(0)
        self.contact_input.clear()
        self.email_input.clear()
        self.medical_history_input.clear()
        
        # Reset button text
        self.save_btn.setText("Save Patient")


class AppointmentsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title
        self.title = QLabel("Appointment Management")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.appointment_list_tab = QWidget()
        self.add_appointment_tab = QWidget()
        
        self.tabs.addTab(self.appointment_list_tab, "Appointment List")
        self.tabs.addTab(self.add_appointment_tab, "Schedule Appointment")
        
        # Setup appointment list tab
        self.setup_appointment_list_tab()
        
        # Setup add appointment tab
        self.setup_add_appointment_tab()
        
        # Add components to main layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.tabs)
    
    def setup_appointment_list_tab(self):
        # Create layout for appointment list tab
        self.appointment_list_layout = QVBoxLayout(self.appointment_list_tab)
        
        # Filter layout
        self.filter_layout = QHBoxLayout()
        
        # Date filter
        self.filter_date_label = QLabel("Date:")
        self.filter_date = QDateEdit()
        self.filter_date.setDate(QDate.currentDate())
        self.filter_date.setCalendarPopup(True)
        
        # Doctor filter
        self.filter_doctor_label = QLabel("Doctor:")
        self.filter_doctor = QComboBox()
        self.filter_doctor.addItem("All Doctors")
        
        # Status filter
        self.filter_status_label = QLabel("Status:")
        self.filter_status = QComboBox()
        self.filter_status.addItems(["All", "Scheduled", "Completed", "Cancelled", "No Show"])
        
        # Filter button
        self.filter_btn = CustomButton("Apply Filter")
        self.filter_btn.clicked.connect(self.filter_appointments)
        
        # Add filter components to filter layout
        self.filter_layout.addWidget(self.filter_date_label)
        self.filter_layout.addWidget(self.filter_date)
        self.filter_layout.addWidget(self.filter_doctor_label)
        self.filter_layout.addWidget(self.filter_doctor)
        self.filter_layout.addWidget(self.filter_status_label)
        self.filter_layout.addWidget(self.filter_status)
        self.filter_layout.addWidget(self.filter_btn)
        
        # Appointment table
        self.appointment_table = QTableWidget()
        self.appointment_table.setColumnCount(7)
        self.appointment_table.setHorizontalHeaderLabels(["ID", "Patient", "Date", "Time", "Doctor", "Notes", "Status"])
        self.appointment_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.appointment_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        self.appointment_table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire rows
        self.appointment_table.setSelectionMode(QTableWidget.SingleSelection)  # Allow only single selection
        
        # Action buttons layout
        self.action_layout = QHBoxLayout()
        
        # View button
        self.view_btn = CustomButton("View Details")
        self.view_btn.clicked.connect(self.view_appointment)
        
        # Edit button
        self.edit_btn = CustomButton("Edit")
        self.edit_btn.clicked.connect(self.edit_appointment)
        
        # Update status button
        self.status_btn = CustomButton("Update Status")
        self.status_btn.clicked.connect(self.update_appointment_status)
        
        # Delete button
        self.delete_btn = CustomButton("Delete")
        self.delete_btn.clicked.connect(self.delete_appointment)
        
        # Add buttons to action layout
        self.action_layout.addWidget(self.view_btn)
        self.action_layout.addWidget(self.edit_btn)
        self.action_layout.addWidget(self.status_btn)
        self.action_layout.addWidget(self.delete_btn)
        
        # Add components to appointment list layout
        self.appointment_list_layout.addLayout(self.filter_layout)
        self.appointment_list_layout.addWidget(self.appointment_table)
        self.appointment_list_layout.addLayout(self.action_layout)
        
        # Load appointments
        self.load_appointments()
        
        # Load doctors for filter
        self.load_doctors()
    
    def setup_add_appointment_tab(self):
        # Create layout for add appointment tab
        self.add_appointment_layout = QVBoxLayout(self.add_appointment_tab)
        
        # Create form layout
        self.form_layout = QFormLayout()
        
        # Create form fields
        self.appointment_id_input = QLineEdit()
        self.appointment_id_input.setReadOnly(True)  # ID is read-only
        self.appointment_id_input.hide()  # Hide ID field initially
        
        self.patient_select = QComboBox()
        self.load_patients_for_select()
        
        # Calendar and time widgets
        self.date_widget = QCalendarWidget()
        self.date_widget.setMinimumDate(QDate.currentDate())
        self.date_widget.setGridVisible(True)
        
        self.time_widget = QTimeEdit()
        self.time_widget.setDisplayFormat("HH:mm")
        self.time_widget.setTime(QTime(9, 0))  # Default to 9:00 AM
        
        self.doctor_input = QComboBox()
        self.doctor_input.addItems(["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown"])
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Enter appointment notes...")
        self.notes_input.setMinimumHeight(100)
        
        self.status_input = QComboBox()
        self.status_input.addItems(["Scheduled", "Completed", "Cancelled", "No Show"])
        
        # Add fields to form layout
        self.form_layout.addRow("ID:", self.appointment_id_input)
        self.form_layout.addRow("Patient *:", self.patient_select)
        self.form_layout.addRow("Date *:", self.date_widget)
        self.form_layout.addRow("Time *:", self.time_widget)
        self.form_layout.addRow("Doctor *:", self.doctor_input)
        self.form_layout.addRow("Notes:", self.notes_input)
        self.form_layout.addRow("Status:", self.status_input)
        
        # Form buttons layout
        self.form_buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_btn = CustomButton("Schedule Appointment")
        self.save_btn.clicked.connect(self.save_appointment)
        
        # Clear button
        self.clear_btn = CustomButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_appointment_form)
        
        # Add buttons to form buttons layout
        self.form_buttons_layout.addWidget(self.save_btn)
        self.form_buttons_layout.addWidget(self.clear_btn)
        
        # Add form layout and buttons to add appointment layout
        self.add_appointment_layout.addLayout(self.form_layout)
        self.add_appointment_layout.addLayout(self.form_buttons_layout)
    
    def load_appointments(self):
        cursor = self.db.conn.cursor()
        
        # Get current date from filter
        filter_date = self.filter_date.date().toString("yyyy-MM-dd")
        
        cursor.execute("""
            SELECT a.id, p.name, a.appointment_date, a.appointment_time, 
                   a.doctor, a.notes, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        """, (filter_date,))
        
        appointments = cursor.fetchall()
        self.appointment_table.setRowCount(len(appointments))
        
        for i, appointment in enumerate(appointments):
            for j, value in enumerate(appointment):
                self.appointment_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def load_doctors(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT doctor FROM appointments
            ORDER BY doctor
        """)
        
        doctors = [row[0] for row in cursor.fetchall()]
        
        # Clear and add default option
        self.filter_doctor.clear()
        self.filter_doctor.addItem("All Doctors")
        
        # Add doctors to combo box
        for doctor in doctors:
            self.filter_doctor.addItem(doctor)
    
    def load_patients_for_select(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name FROM patients
            ORDER BY name
        """)
        
        patients = cursor.fetchall()
        
        # Clear and add placeholder
        self.patient_select.clear()
        self.patient_select.addItem("-- Select Patient --", None)
        
        # Add patients to combo box
        for patient in patients:
            self.patient_select.addItem(patient[1], patient[0])  # Display name, store ID as data
    
    def filter_appointments(self):
        cursor = self.db.conn.cursor()
        
        # Get filter values
        filter_date = self.filter_date.date().toString("yyyy-MM-dd")
        filter_doctor = self.filter_doctor.currentText()
        filter_status = self.filter_status.currentText()
        
        # Build query based on filters
        query = """
            SELECT a.id, p.name, a.appointment_date, a.appointment_time, 
                   a.doctor, a.notes, a.status
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.appointment_date = ?
        """
        params = [filter_date]
        
        if filter_doctor != "All Doctors":
            query += " AND a.doctor = ?"
            params.append(filter_doctor)
        
        if filter_status != "All":
            query += " AND a.status = ?"
            params.append(filter_status)
        
        query += " ORDER BY a.appointment_time"
        
        cursor.execute(query, params)
        
        appointments = cursor.fetchall()
        self.appointment_table.setRowCount(len(appointments))
        
        for i, appointment in enumerate(appointments):
            for j, value in enumerate(appointment):
                self.appointment_table.setItem(i, j, QTableWidgetItem(str(value)))
    
    def view_appointment(self):
        selected_rows = self.appointment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to view.")
            return
        
        # Get appointment ID from the first column of the selected row
        appointment_id = self.appointment_table.item(selected_rows[0].row(), 0).text()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as patient_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = ?
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            QMessageBox.warning(self, "Error", "Appointment not found.")
            return
        
        # Create message box with appointment details
        msg = QMessageBox()
        msg.setWindowTitle("Appointment Details")
        msg.setIcon(QMessageBox.Information)
        
        details = f"""
        <b>ID:</b> {appointment[0]}
        <b>Patient:</b> {appointment[9]}
        <b>Date:</b> {appointment[2]}
        <b>Time:</b> {appointment[3]}
        <b>Doctor:</b> {appointment[4]}
        <b>Notes:</b> {appointment[5]}
        <b>Status:</b> {appointment[6]}
        """
        
        msg.setText(details)
        msg.exec_()
    
    def edit_appointment(self):
        selected_rows = self.appointment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to edit.")
            return
        
        # Get appointment ID from the first column of the selected row
        appointment_id = self.appointment_table.item(selected_rows[0].row(), 0).text()
        
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT a.*, p.name as patient_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            WHERE a.id = ?
        """, (appointment_id,))
        
        appointment = cursor.fetchone()
        if not appointment:
            QMessageBox.warning(self, "Error", "Appointment not found.")
            return
        
        # Switch to add/edit tab
        self.tabs.setCurrentIndex(1)
        
        # Show and set appointment ID
        self.appointment_id_input.show()
        self.appointment_id_input.setText(str(appointment[0]))
        
        # Set patient
        patient_index = self.patient_select.findData(appointment[1])
        if patient_index >= 0:
            self.patient_select.setCurrentIndex(patient_index)
        
        # Set date
        appointment_date = QDate.fromString(appointment[2], "yyyy-MM-dd")
        self.date_widget.setSelectedDate(appointment_date)
        
        # Set time
        appointment_time = QTime.fromString(appointment[3], "HH:mm")
        self.time_widget.setTime(appointment_time)
        
        # Set doctor
        doctor_index = self.doctor_input.findText(appointment[4])
        if doctor_index >= 0:
            self.doctor_input.setCurrentIndex(doctor_index)
        
        # Set notes
        self.notes_input.setText(appointment[5] if appointment[5] else "")
        
        # Set status
        status_index = self.status_input.findText(appointment[6])
        if status_index >= 0:
            self.status_input.setCurrentIndex(status_index)
        
        # Change button text
        self.save_btn.setText("Update Appointment")
    
    def update_appointment_status(self):
        selected_rows = self.appointment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to update status.")
            return
        
        # Get appointment ID from the first column of the selected row
        appointment_id = self.appointment_table.item(selected_rows[0].row(), 0).text()
        
        # Create status selection dialog
        status_dialog = QDialog(self)
        status_dialog.setWindowTitle("Update Appointment Status")
        
        dialog_layout = QVBoxLayout()
        
        status_label = QLabel("Select new status:")
        status_combo = QComboBox()
        status_combo.addItems(["Scheduled", "Completed", "Cancelled", "No Show"])
        
        current_status = self.appointment_table.item(selected_rows[0].row(), 6).text()
        status_index = status_combo.findText(current_status)
        if status_index >= 0:
            status_combo.setCurrentIndex(status_index)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        dialog_layout.addWidget(status_label)
        dialog_layout.addWidget(status_combo)
        dialog_layout.addLayout(buttons_layout)
        
        status_dialog.setLayout(dialog_layout)
        
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_status_update(appointment_id, status_combo.currentText(), status_dialog))
        cancel_btn.clicked.connect(status_dialog.reject)
        
        status_dialog.exec_()
    
    def save_status_update(self, appointment_id, new_status, dialog):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                UPDATE appointments
                SET status = ?
                WHERE id = ?
            """, (new_status, appointment_id))
            
            self.db.conn.commit()
            
            # Close dialog
            dialog.accept()
            
            # Show success message
            QMessageBox.information(self, "Success", "Appointment status updated successfully.")
            
            # Refresh appointments
            self.filter_appointments()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to update status: {str(e)}")
    
    def delete_appointment(self):
        selected_rows = self.appointment_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an appointment to delete.")
            return
        
        # Get appointment ID from the first column of the selected row
        appointment_id = self.appointment_table.item(selected_rows[0].row(), 0).text()
        patient_name = self.appointment_table.item(selected_rows[0].row(), 1).text()
        appointment_date = self.appointment_table.item(selected_rows[0].row(), 2).text()
        
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete the appointment for {patient_name} on {appointment_date}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", f"Appointment deleted successfully.")
                
                # Refresh appointments
                self.filter_appointments()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Failed to delete appointment: {str(e)}")
    
    def save_appointment(self):
        # Validate required fields
        patient_id = self.patient_select.currentData()
        if not patient_id:
            QMessageBox.warning(self, "Validation Error", "Please select a patient.")
            return
        
        appointment_date = self.date_widget.selectedDate().toString("yyyy-MM-dd")
        appointment_time = self.time_widget.time().toString("HH:mm")
        doctor = self.doctor_input.currentText()
        
        if not doctor:
            QMessageBox.warning(self, "Validation Error", "Please select a doctor.")
            return
        
        # Get other field values
        appointment_id = self.appointment_id_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        status = self.status_input.currentText()
        
        try:
            cursor = self.db.conn.cursor()
            
            # If appointment ID exists, update existing appointment
            if appointment_id:
                cursor.execute("""
                    UPDATE appointments 
                    SET patient_id = ?, appointment_date = ?, appointment_time = ?, 
                        doctor = ?, notes = ?, status = ?
                    WHERE id = ?
                """, (patient_id, appointment_date, appointment_time, doctor, notes, status, appointment_id))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "Appointment updated successfully.")
                
            # Otherwise, insert new appointment
            else:
                cursor.execute("""
                    INSERT INTO appointments (patient_id, appointment_date, appointment_time, doctor, notes, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, appointment_date, appointment_time, doctor, notes, status))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "New appointment scheduled successfully.")
            
            # Clear form and refresh list
            self.clear_appointment_form()
            self.load_appointments()
            
            # Switch to appointment list tab
            self.tabs.setCurrentIndex(0)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    
    def clear_appointment_form(self):
        # Hide and clear appointment ID
        self.appointment_id_input.hide()
        self.appointment_id_input.clear()
        
        # Reset patient select to first item
        self.patient_select.setCurrentIndex(0)
        
        # Reset date to current date
        self.date_widget.setSelectedDate(QDate.currentDate())
        
        # Reset time to 9:00 AM
        self.time_widget.setTime(QTime(9, 0))
        
        # Reset doctor to first item
        self.doctor_input.setCurrentIndex(0)
        
        # Clear notes
        self.notes_input.clear()
        
        # Reset status to "Scheduled"
        self.status_input.setCurrentIndex(0)
        
        # Reset button text
        self.save_btn.setText("Schedule Appointment")


class BillingPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title
        self.title = QLabel("Billing Management")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.billing_list_tab = QWidget()
        self.create_invoice_tab = QWidget()
        
        self.tabs.addTab(self.billing_list_tab, "Invoice List")
        self.tabs.addTab(self.create_invoice_tab, "Create Invoice")
        
        # Setup billing list tab
        self.setup_billing_list_tab()
        
        # Setup create invoice tab
        self.setup_create_invoice_tab()
        
        # Add components to main layout
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.tabs)
    
    def setup_billing_list_tab(self):
        # Create layout for billing list tab
        self.billing_list_layout = QVBoxLayout(self.billing_list_tab)
        
        # Filter layout
        self.filter_layout = QHBoxLayout()
        
        # Patient filter
        self.filter_patient_label = QLabel("Patient:")
        self.filter_patient = QComboBox()
        self.filter_patient.addItem("All Patients")
        self.load_patients_for_filter()
        
        # Payment status filter
        self.filter_status_label = QLabel("Payment Status:")
        self.filter_status = QComboBox()
        self.filter_status.addItems(["All", "Paid", "Pending", "Cancelled"])
        
        # Date range filter
        self.filter_date_from_label = QLabel("From:")
        self.filter_date_from = QDateEdit()
        self.filter_date_from.setDate(QDate.currentDate().addMonths(-1))
        self.filter_date_from.setCalendarPopup(True)
        
        self.filter_date_to_label = QLabel("To:")
        self.filter_date_to = QDateEdit()
        self.filter_date_to.setDate(QDate.currentDate())
        self.filter_date_to.setCalendarPopup(True)
        
        # Filter button
        self.filter_btn = CustomButton("Apply Filter")
        self.filter_btn.clicked.connect(self.filter_invoices)
        
        # Add filter components to filter layout
        self.filter_layout.addWidget(self.filter_patient_label)
        self.filter_layout.addWidget(self.filter_patient)
        self.filter_layout.addWidget(self.filter_status_label)
        self.filter_layout.addWidget(self.filter_status)
        self.filter_layout.addWidget(self.filter_date_from_label)
        self.filter_layout.addWidget(self.filter_date_from)
        self.filter_layout.addWidget(self.filter_date_to_label)
        self.filter_layout.addWidget(self.filter_date_to)
        self.filter_layout.addWidget(self.filter_btn)
        
        # Invoice table
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(7)
        self.invoice_table.setHorizontalHeaderLabels(["ID", "Patient", "Treatment", "Doctor", "Cost", "Payment Status", "Invoice Date"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make table read-only
        self.invoice_table.setSelectionBehavior(QTableWidget.SelectRows)  # Select entire rows
        self.invoice_table.setSelectionMode(QTableWidget.SingleSelection)  # Allow only single selection
        
        # Action buttons layout
        self.action_layout = QHBoxLayout()
        
        # View button
        self.view_btn = CustomButton("View Invoice")
        self.view_btn.clicked.connect(self.view_invoice)
        
        # Print button
        self.print_btn = CustomButton("Print Invoice")
        self.print_btn.clicked.connect(self.print_invoice)
        
        # Update payment status button
        self.status_btn = CustomButton("Update Payment")
        self.status_btn.clicked.connect(self.update_payment_status)
        
        # Delete button
        self.delete_btn = CustomButton("Delete")
        self.delete_btn.clicked.connect(self.delete_invoice)
        
        # Add buttons to action layout
        self.action_layout.addWidget(self.view_btn)
        self.action_layout.addWidget(self.print_btn)
        self.action_layout.addWidget(self.status_btn)
        self.action_layout.addWidget(self.delete_btn)
        
        # Add components to billing list layout
        self.billing_list_layout.addLayout(self.filter_layout)
        self.billing_list_layout.addWidget(self.invoice_table)
        self.billing_list_layout.addLayout(self.action_layout)
        
        # Load invoices
        self.load_invoices()
    
    def setup_create_invoice_tab(self):
        # Create layout for create invoice tab
        self.create_invoice_layout = QVBoxLayout(self.create_invoice_tab)
        
        # Create form layout
        self.form_layout = QFormLayout()
        
        # Create form fields
        self.invoice_id_input = QLineEdit()
        self.invoice_id_input.setReadOnly(True)  # ID is read-only
        self.invoice_id_input.hide()  # Hide ID field initially
        
        self.patient_select = QComboBox()
        self.load_patients_for_select()
        self.patient_select.currentIndexChanged.connect(self.on_patient_change)
        
        self.treatment_select = QComboBox()
        self.load_treatments()
        self.treatment_select.currentIndexChanged.connect(self.update_cost)
        
        self.doctor_input = QComboBox()
        self.doctor_input.addItems(["Dr. Smith", "Dr. Johnson", "Dr. Williams", "Dr. Brown"])
        
        self.cost_input = QLineEdit()
        self.cost_input.setReadOnly(True)  # Cost is calculated based on treatment
        self.cost_input.setText("$0.00")
        
        self.payment_status = QComboBox()
        self.payment_status.addItems(["Pending", "Paid", "Cancelled"])
        
        self.invoice_date = QDateEdit()
        self.invoice_date.setDate(QDate.currentDate())
        self.invoice_date.setCalendarPopup(True)
        
        # Add fields to form layout
        self.form_layout.addRow("ID:", self.invoice_id_input)
        self.form_layout.addRow("Patient *:", self.patient_select)
        self.form_layout.addRow("Treatment *:", self.treatment_select)
        self.form_layout.addRow("Doctor *:", self.doctor_input)
        self.form_layout.addRow("Cost:", self.cost_input)
        self.form_layout.addRow("Payment Status:", self.payment_status)
        self.form_layout.addRow("Invoice Date:", self.invoice_date)
        
        # Patient recent appointments section
        self.appointments_group = QGroupBox("Recent Appointments")
        self.appointments_layout = QVBoxLayout(self.appointments_group)
        
        # Recent appointments table
        self.recent_appointments = QTableWidget()
        self.recent_appointments.setColumnCount(4)
        self.recent_appointments.setHorizontalHeaderLabels(["Date", "Time", "Doctor", "Status"])
        self.recent_appointments.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.appointments_layout.addWidget(self.recent_appointments)
        
        # Form buttons layout
        self.form_buttons_layout = QHBoxLayout()
        
        # Save button
        self.save_btn = CustomButton("Generate Invoice")
        self.save_btn.clicked.connect(self.save_invoice)
        
        # Clear button
        self.clear_btn = CustomButton("Clear Form")
        self.clear_btn.clicked.connect(self.clear_billing_form)
        
        # Add buttons to form buttons layout
        self.form_buttons_layout.addWidget(self.save_btn)
        self.form_buttons_layout.addWidget(self.clear_btn)
        
        # Add form layout and components to create invoice layout
        self.create_invoice_layout.addLayout(self.form_layout)
        self.create_invoice_layout.addWidget(self.appointments_group)
        self.create_invoice_layout.addLayout(self.form_buttons_layout)
    
    def load_patients_for_filter(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT p.id, p.name 
            FROM patients p
            JOIN billing b ON p.id = b.patient_id
            ORDER BY p.name
        """)
        
        patients = cursor.fetchall()
        
        # Clear and add default option
        self.filter_patient.clear()
        self.filter_patient.addItem("All Patients")
        
        # Add patients to combo box
        for patient in patients:
            self.filter_patient.addItem(patient[1], patient[0])  # Display name, store ID as data
    
    def load_patients_for_select(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name FROM patients
            ORDER BY name
        """)
        
        patients = cursor.fetchall()
        
        # Clear and add placeholder
        self.patient_select.clear()
        self.patient_select.addItem("-- Select Patient --", None)
        
        # Add patients to combo box
        for patient in patients:
            self.patient_select.addItem(patient[1], patient[0])  # Display name, store ID as data
    
    def load_treatments(self):
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT id, name, cost FROM treatments
            ORDER BY name
        """)
        
        treatments = cursor.fetchall()
        
        # Clear and add placeholder
        self.treatment_select.clear()
        self.treatment_select.addItem("-- Select Treatment --", (None, 0.0))
        
        # Add treatments to combo box
        for treatment in treatments:
            self.treatment_select.addItem(f"{treatment[1]} (${treatment[2]:.2f})", (treatment[0], treatment[2]))
    
    def load_invoices(self):
        cursor = self.db.conn.cursor()
        
        # Get date range from filter
        date_from = self.filter_date_from.date().toString("yyyy-MM-dd")
        date_to = self.filter_date_to.date().toString("yyyy-MM-dd")
        
        cursor.execute("""
            SELECT b.id, p.name, t.name, b.doctor, b.cost, b.payment_status, b.invoice_date
            FROM billing b
            JOIN patients p ON b.patient_id = p.id
            JOIN treatments t ON b.treatment_id = t.id
            WHERE b.invoice_date BETWEEN ? AND ?
            ORDER BY b.invoice_date DESC
        """, (date_from, date_to))
        
        invoices = cursor.fetchall()
        self.invoice_table.setRowCount(len(invoices))
        
        for i, invoice in enumerate(invoices):
            for j, value in enumerate(invoice):
                # Format cost as currency
                if j == 4:
                    item = QTableWidgetItem(f"${value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.invoice_table.setItem(i, j, item)
    
    def filter_invoices(self):
        cursor = self.db.conn.cursor()
        
        # Get filter values
        patient_id = self.filter_patient.currentData()
        payment_status = self.filter_status.currentText()
        date_from = self.filter_date_from.date().toString("yyyy-MM-dd")
        date_to = self.filter_date_to.date().toString("yyyy-MM-dd")
        
        # Build query based on filters
        query = """
            SELECT b.id, p.name, t.name, b.doctor, b.cost, b.payment_status, b.invoice_date
            FROM billing b
            JOIN patients p ON b.patient_id = p.id
            JOIN treatments t ON b.treatment_id = t.id
            WHERE b.invoice_date BETWEEN ? AND ?
        """
        params = [date_from, date_to]
        
        if patient_id:
            query += " AND b.patient_id = ?"
            params.append(patient_id)
        
        if payment_status != "All":
            query += " AND b.payment_status = ?"
            params.append(payment_status)
        
        query += " ORDER BY b.invoice_date DESC"
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        self.invoice_table.setRowCount(len(invoices))
        
        for i, invoice in enumerate(invoices):
            for j, value in enumerate(invoice):
                # Format cost as currency
                if j == 4:
                    item = QTableWidgetItem(f"${value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.invoice_table.setItem(i, j, item)
    def update_cost(self):
        treatment_data = self.treatment_select.currentData()
        if treatment_data:
            _, cost = treatment_data  # Extract cost from tuple
            self.cost_input.setText(f"${cost:.2f}")
        else:
            self.cost_input.setText("$0.00")
    def on_patient_change(self):
        patient_id = self.patient_select.currentData()
        if not patient_id:
            self.recent_appointments.setRowCount(0)
            return

        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT appointment_date, appointment_time, doctor, status
            FROM appointments
            WHERE patient_id = ?
            ORDER BY appointment_date DESC
            LIMIT 5
        """, (patient_id,))
        
        appointments = cursor.fetchall()
        self.recent_appointments.setRowCount(len(appointments))

        for i, appointment in enumerate(appointments):
            for j, value in enumerate(appointment):
                self.recent_appointments.setItem(i, j, QTableWidgetItem(str(value)))
    def save_invoice(self):
        patient_id = self.patient_select.currentData()
        treatment_data = self.treatment_select.currentData()
        doctor = self.doctor_input.currentText()
        payment_status = self.payment_status.currentText()
        invoice_date = self.invoice_date.date().toString("yyyy-MM-dd")

        if not patient_id or not treatment_data:
            QMessageBox.warning(self, "Validation Error", "Please select a patient and a treatment.")
            return

        treatment_id, cost = treatment_data
        invoice_id = self.invoice_id_input.text().strip()

        try:
            cursor = self.db.conn.cursor()

            if invoice_id:  # Update existing invoice
                cursor.execute("""
                    UPDATE billing 
                    SET patient_id = ?, treatment_id = ?, doctor = ?, cost = ?, 
                        payment_status = ?, invoice_date = ?
                    WHERE id = ?
                """, (patient_id, treatment_id, doctor, cost, payment_status, invoice_date, invoice_id))
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "Invoice updated successfully.")
            else:  # Insert new invoice
                cursor.execute("""
                    INSERT INTO billing (patient_id, treatment_id, doctor, cost, payment_status, invoice_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (patient_id, treatment_id, doctor, cost, payment_status, invoice_date))
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "Invoice generated successfully.")

            # Clear form and refresh list
            self.clear_billing_form()
            self.load_invoices()
            self.tabs.setCurrentIndex(0)  # Switch to invoice list tab

        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")
    def clear_billing_form(self):
        self.invoice_id_input.hide()
        self.invoice_id_input.clear()
        self.patient_select.setCurrentIndex(0)
        self.treatment_select.setCurrentIndex(0)
        self.doctor_input.setCurrentIndex(0)
        self.cost_input.setText("$0.00")
        self.payment_status.setCurrentIndex(0)
        self.invoice_date.setDate(QDate.currentDate())
        self.recent_appointments.setRowCount(0)
        self.save_btn.setText("Generate Invoice")
    def view_invoice(self):
        selected_rows = self.invoice_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to view.")
            return

        invoice_id = self.invoice_table.item(selected_rows[0].row(), 0).text()
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT b.*, p.name, t.name
            FROM billing b
            JOIN patients p ON b.patient_id = p.id
            JOIN treatments t ON b.treatment_id = t.id
            WHERE b.id = ?
        """, (invoice_id,))

        invoice = cursor.fetchone()
        if not invoice:
            QMessageBox.warning(self, "Error", "Invoice not found.")
            return

        msg = QMessageBox()
        msg.setWindowTitle("Invoice Details")
        msg.setIcon(QMessageBox.Information)

        details = f"""
        <b>Invoice ID:</b> {invoice[0]}
        <b>Patient:</b> {invoice[8]}
        <b>Treatment:</b> {invoice[8]}
        <b>Doctor:</b> {invoice[3]}
        <b>Cost:</b> ${invoice[4]:.2f}
        <b>Payment Status:</b> {invoice[5]}
        <b>Invoice Date:</b> {invoice[6]}
        """

        msg.setText(details)
        msg.exec_()
    def print_invoice(self):
        selected_rows = self.invoice_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to print.")
            return

        invoice_id = self.invoice_table.item(selected_rows[0].row(), 0).text()
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT b.*, p.name, t.name
            FROM billing b
            JOIN patients p ON b.patient_id = p.id
            JOIN treatments t ON b.treatment_id = t.id
            WHERE b.id = ?
        """, (invoice_id,))

        invoice = cursor.fetchone()
        if not invoice:
            QMessageBox.warning(self, "Error", "Invoice not found.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save Invoice", f"Invoice_{invoice_id}.pdf", "PDF Files (*.pdf)")
        if not file_name:
            return

        doc = SimpleDocTemplate(file_name, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"<b>Invoice ID:</b> {invoice[0]}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Patient:</b> {invoice[8]}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Treatment:</b> {invoice[9]}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Doctor:</b> {invoice[3]}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Cost:</b> ${invoice[4]:.2f}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Payment Status:</b> {invoice[5]}", styles["Normal"]))
        elements.append(Paragraph(f"<b>Invoice Date:</b> {invoice[6]}", styles["Normal"]))

        doc.build(elements)
        QMessageBox.information(self, "Success", "Invoice saved successfully!")
    def update_payment_status(self):
        selected_rows = self.invoice_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to update payment status.")
            return
    
        # Get invoice ID
        invoice_id = self.invoice_table.item(selected_rows[0].row(), 0).text()
    
        # Create a status selection dialog
        status_dialog = QDialog(self)
        status_dialog.setWindowTitle("Update Payment Status")
    
        dialog_layout = QVBoxLayout()
    
        status_label = QLabel("Select new payment status:")
        status_combo = QComboBox()
        status_combo.addItems(["Pending", "Paid", "Cancelled"])
    
        # Get current status and set as default
        current_status = self.invoice_table.item(selected_rows[0].row(), 5).text()
        status_index = status_combo.findText(current_status)
        if status_index >= 0:
            status_combo.setCurrentIndex(status_index)
    
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
    
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
    
        dialog_layout.addWidget(status_label)
        dialog_layout.addWidget(status_combo)
        dialog_layout.addLayout(buttons_layout)
    
        status_dialog.setLayout(dialog_layout)
    
        # Connect buttons
        save_btn.clicked.connect(lambda: self.save_payment_status(invoice_id, status_combo.currentText(), status_dialog))
        cancel_btn.clicked.connect(status_dialog.reject)
    
        status_dialog.exec_()
    
    def save_payment_status(self, invoice_id, new_status, dialog):
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("""
                UPDATE billing
                SET payment_status = ?
                WHERE id = ?
            """, (new_status, invoice_id))
    
            self.db.conn.commit()
    
            # Close dialog
            dialog.accept()
    
            # Show success message
            QMessageBox.information(self, "Success", "Payment status updated successfully.")
    
            # Refresh invoice list
            self.load_invoices()
    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Error", f"Failed to update payment status: {str(e)}")
    def delete_invoice(self):
        selected_rows = self.invoice_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select an invoice to delete.")
            return
    
        # Get invoice ID
        invoice_id = self.invoice_table.item(selected_rows[0].row(), 0).text()
        patient_name = self.invoice_table.item(selected_rows[0].row(), 1).text()
        treatment_name = self.invoice_table.item(selected_rows[0].row(), 2).text()
    
        # Confirm deletion
        reply = QMessageBox.question(self, "Confirm Deletion", 
                                    f"Are you sure you want to delete the invoice for {patient_name} - {treatment_name}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            try:
                cursor = self.db.conn.cursor()
                cursor.execute("DELETE FROM billing WHERE id = ?", (invoice_id,))
                
                self.db.conn.commit()
                QMessageBox.information(self, "Success", "Invoice deleted successfully.")
                
                # Refresh invoice list
                self.load_invoices()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Error", f"Failed to delete invoice: {str(e)}")
class ReportsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Title
        self.title = QLabel("Reports & Analytics")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)
        
        # Add message label
        self.info_label = QLabel("Reports and analytics will be available here.")
        self.info_label.setAlignment(Qt.AlignCenter)
        
        # Add widgets to layout
        self.layout.addWidget(self.title)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.info_label)
        self.layout.addStretch()
class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = main_window.db
        self.init_ui()

    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("Settings")
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title.setFont(font)

        # Theme selection
        self.theme_label = QLabel("Select Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light"])
        self.load_settings()

        self.theme_combo.currentTextChanged.connect(self.change_theme)

        # Layout for settings
        self.settings_layout = QFormLayout()
        self.settings_layout.addRow(self.theme_label, self.theme_combo)

        # Add widgets to main layout
        self.layout.addWidget(self.title)
        self.layout.addSpacing(20)
        self.layout.addLayout(self.settings_layout)
        self.layout.addStretch()

    def load_settings(self):
        """Load settings from the database"""
        try:
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT theme FROM settings")
            theme = cursor.fetchone()[0]
            self.theme_combo.setCurrentText(theme)
        except:
            pass

    def change_theme(self, theme_name):
        """Change the theme and update the database"""
        self.main_window.update_theme(theme_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply the selected theme
    StyleHelper.set_theme(app, THEME)

    # Initialize the main window
    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())