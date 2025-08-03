import sys
import sqlite3
import hashlib
import csv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget,
                             QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
                             QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QDialog, QDialogButtonBox, QFileDialog, QDateEdit,QGroupBox,
                             QDoubleSpinBox, QAction, QStatusBar, QInputDialog, QCompleter)
from PyQt5.QtCore import Qt, QDate, QTimer
class Database:
    def __init__(self, db_file="employee_accounting.db"):
        self.db_file = db_file
        self.create_tables()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table for authentication
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Departments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
        ''')
        
        # Positions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department_id INTEGER,
            description TEXT,
            FOREIGN KEY (department_id) REFERENCES departments (id)
        )
        ''')
        
        # Employees table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            gender TEXT,
            date_of_birth DATE,
            address TEXT,
            phone TEXT,
            email TEXT,
            department_id INTEGER,
            position_id INTEGER,
            hire_date DATE,
            termination_date DATE,
            base_salary REAL NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments (id),
            FOREIGN KEY (position_id) REFERENCES positions (id)
        )
        ''')
        
        # Attendance table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date DATE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
        ''')
        
        # Leave table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            status TEXT DEFAULT 'Pending',
            reason TEXT,
            approved_by INTEGER,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
        ''')
        
        # Payroll table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payrolls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            pay_period_start DATE NOT NULL,
            pay_period_end DATE NOT NULL,
            base_salary REAL NOT NULL,
            total_bonus REAL DEFAULT 0,
            total_deduction REAL DEFAULT 0,
            net_salary REAL NOT NULL,
            payment_date DATE,
            payment_method TEXT,
            payment_status TEXT DEFAULT 'Pending',
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES employees (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Bonuses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bonuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (payroll_id) REFERENCES payrolls (id)
        )
        ''')
        
        # Deductions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS deductions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payroll_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (payroll_id) REFERENCES payrolls (id)
        )
        ''')
        
        # Create admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            admin_password = "admin123"
            password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                          ("admin", password_hash, "Admin"))
        
        # Insert some default departments
        for dept in ["HR", "Finance", "IT", "Marketing", "Operations"]:
            cursor.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (dept,))
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                      (username, password_hash))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def get_departments(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM departments ORDER BY name")
        departments = cursor.fetchall()
        conn.close()
        return departments
    
    def get_positions(self, department_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        if department_id:
            cursor.execute("SELECT * FROM positions WHERE department_id = ? ORDER BY title", (department_id,))
        else:
            cursor.execute("SELECT * FROM positions ORDER BY title")
    
        positions = cursor.fetchall()
        conn.close()
       
        return positions
  
    def add_employee(self, employee_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO employees 
        (employee_id, first_name, last_name, gender, date_of_birth, 
        address, phone, email, department_id, position_id, 
        hire_date, base_salary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            employee_data['employee_id'], 
            employee_data['first_name'], 
            employee_data['last_name'],
            employee_data['gender'],
            employee_data['date_of_birth'],
            employee_data['address'],
            employee_data['phone'],
            employee_data['email'],
            employee_data['department_id'],
            employee_data['position_id'],
            employee_data['hire_date'],
            employee_data['base_salary']
        ))
        
        employee_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return employee_id
    
    def update_employee(self, employee_id, employee_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE employees 
        SET first_name = ?, last_name = ?, gender = ?, date_of_birth = ?,
        address = ?, phone = ?, email = ?, department_id = ?, position_id = ?,
        hire_date = ?, termination_date = ?, base_salary = ?, status = ?,
        updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (
            employee_data['first_name'], 
            employee_data['last_name'],
            employee_data['gender'],
            employee_data['date_of_birth'],
            employee_data['address'],
            employee_data['phone'],
            employee_data['email'],
            employee_data['department_id'],
            employee_data['position_id'],
            employee_data['hire_date'],
            employee_data.get('termination_date'),
            employee_data['base_salary'],
            employee_data['status'],
            employee_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_employee(self, employee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        
        conn.commit()
        conn.close()
    
    def get_employees(self, search_text=None, department_id=None, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        query = '''
        SELECT e.*, d.name as department_name, p.title as position_title
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN positions p ON e.position_id = p.id
        WHERE 1=1
        '''
        params = []
    
        if search_text:
            query += " AND (e.first_name LIKE ? OR e.last_name LIKE ? OR e.employee_id LIKE ?)"
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])
    
        if department_id:
            query += " AND e.department_id = ?"
            params.append(department_id)
    
        if status:
            query += " AND e.status = ?"
            params.append(status)
    
        query += " ORDER BY e.last_name, e.first_name"
    
        cursor.execute(query, params)
        employees = cursor.fetchall()
        conn.close()
        return employees
    
    def get_employee_by_id(self, employee_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT e.*, d.name as department_name, p.title as position_title
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN positions p ON e.position_id = p.id
        WHERE e.id = ?
        ''', (employee_id,))
        
        employee = cursor.fetchone()
        conn.close()
        return employee
    
    def create_payroll(self, payroll_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO payrolls 
        (employee_id, pay_period_start, pay_period_end, base_salary, 
        total_bonus, total_deduction, net_salary, payment_date, 
        payment_method, payment_status, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payroll_data['employee_id'],
            payroll_data['pay_period_start'],
            payroll_data['pay_period_end'],
            payroll_data['base_salary'],
            payroll_data['total_bonus'],
            payroll_data['total_deduction'],
            payroll_data['net_salary'],
            payroll_data['payment_date'],
            payroll_data['payment_method'],
            payroll_data['payment_status'],
            payroll_data['created_by']
        ))
        
        payroll_id = cursor.lastrowid
        
        # Add bonuses
        for bonus in payroll_data.get('bonuses', []):
            cursor.execute('''
            INSERT INTO bonuses (payroll_id, amount, reason)
            VALUES (?, ?, ?)
            ''', (payroll_id, bonus['amount'], bonus['reason']))
        
        # Add deductions
        for deduction in payroll_data.get('deductions', []):
            cursor.execute('''
            INSERT INTO deductions (payroll_id, amount, reason)
            VALUES (?, ?, ?)
            ''', (payroll_id, deduction['amount'], deduction['reason']))
        
        conn.commit()
        conn.close()
        return payroll_id
    
    def get_payroll_history(self, employee_id=None, from_date=None, to_date=None):
        conn = self.get_connection()
        cursor = conn.cursor()
    
        query = '''
        SELECT p.*, e.first_name, e.last_name, e.employee_id as emp_id
        FROM payrolls p
        JOIN employees e ON p.employee_id = e.id
        WHERE 1=1
        '''
        params = []
    
        if employee_id:
            query += " AND p.employee_id = ?"
            params.append(employee_id)
    
        if from_date:
            query += " AND p.pay_period_end >= ?"
            params.append(from_date)
    
        if to_date:
            query += " AND p.pay_period_start <= ?"
            params.append(to_date)
    
        query += " ORDER BY p.pay_period_end DESC, e.last_name, e.first_name"
    
        cursor.execute(query, params)
        payrolls = [dict(row) for row in cursor.fetchall()]  # Convert Row objects to dictionaries
    
        # Get bonuses and deductions for each payroll
        for payroll in payrolls:
            cursor.execute("SELECT * FROM bonuses WHERE payroll_id = ?", (payroll['id'],))
            payroll['bonuses'] = [dict(row) for row in cursor.fetchall()]  # Convert bonuses to dict
    
            cursor.execute("SELECT * FROM deductions WHERE payroll_id = ?", (payroll['id'],))
            payroll['deductions'] = [dict(row) for row in cursor.fetchall()]  # Convert deductions to dict
    
        conn.close()
        return payrolls
    
    def generate_payroll_report(self, from_date, to_date, department_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT 
            d.name as department,
            COUNT(DISTINCT p.id) as payroll_count,
            COUNT(DISTINCT p.employee_id) as employee_count,
            SUM(p.base_salary) as total_base_salary,
            SUM(p.total_bonus) as total_bonuses,
            SUM(p.total_deduction) as total_deductions,
            SUM(p.net_salary) as total_net_salary
        FROM payrolls p
        JOIN employees e ON p.employee_id = e.id
        JOIN departments d ON e.department_id = d.id
        WHERE p.pay_period_start >= ? AND p.pay_period_end <= ?
        '''
        params = [from_date, to_date]
        
        if department_id:
            query += " AND e.department_id = ?"
            params.append(department_id)
        
        query += " GROUP BY d.name ORDER BY d.name"
        
        cursor.execute(query, params)
        report_data = cursor.fetchall()
        conn.close()
        
        return report_data
    
    def add_attendance(self, attendance_data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO attendance (employee_id, date, status, notes)
        VALUES (?, ?, ?, ?)
        ''', (
            attendance_data['employee_id'],
            attendance_data['date'],
            attendance_data['status'],
            attendance_data.get('notes', '')
        ))
        
        conn.commit()
        conn.close()
    
    def get_attendance(self, employee_id=None, from_date=None, to_date=None, record_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT a.*, e.first_name, e.last_name, e.employee_id as emp_id
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        WHERE 1=1
        '''
        params = []
    
        # ✅ If specific record_id is provided, fetch that record only
        if record_id:
            query += " AND a.id = ?"
            params.append(record_id)
        else:
            if employee_id:
                query += " AND a.employee_id = ?"
                params.append(employee_id)
            
            if from_date:
                query += " AND a.date >= ?"
                params.append(from_date)
            
            if to_date:
                query += " AND a.date <= ?"
                params.append(to_date)
    
        query += " ORDER BY a.date DESC, e.last_name, e.first_name"
    
        cursor.execute(query, params)
        attendance = cursor.fetchall()
        conn.close()
        
        return attendance  # Returns a list of attendance records
    
    def get_attendance_statistics(self, from_date, to_date):
        """Fetches employee attendance statistics for the given period."""
        conn = self.get_connection()
        cursor = conn.cursor()
    
        query = '''
        SELECT e.first_name || ' ' || e.last_name AS employee,
               SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS days_present,
               SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS days_absent,
               SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS days_late,
               SUM(CASE WHEN a.status = 'On Leave' THEN 1 ELSE 0 END) AS leave_taken
        FROM employees e
        LEFT JOIN attendance a ON e.id = a.employee_id AND a.date BETWEEN ? AND ?
        GROUP BY e.id
        ORDER BY e.last_name, e.first_name
        '''
    
        cursor.execute(query, (from_date, to_date))
        statistics = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return statistics

    def add_department(self, name, description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO departments (name, description) VALUES (?, ?)", (name, description))
            dept_id = cursor.lastrowid
            conn.commit()
            return dept_id
        except sqlite3.IntegrityError:
            return None  # Prevent duplicate department names
        finally:
            conn.close()

    def get_department_statistics(self):
        """Fetches department-wise employee statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
    
        query = '''
        SELECT d.name AS department,
               COUNT(e.id) AS total_employees,
               COALESCE(AVG(e.base_salary), 0) AS average_salary,
               COALESCE(SUM(e.base_salary), 0) AS total_payroll
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.name
        ORDER BY d.name
        '''
    
        cursor.execute(query)
        statistics = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return statistics

    def add_position(self, title, department_id, description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO positions (title, department_id, description) VALUES (?, ?, ?)",
                           (title, department_id, description))
            pos_id = cursor.lastrowid
            conn.commit()
            return pos_id
        except sqlite3.IntegrityError:
            return None  # Prevent duplicate position names
        finally:
            conn.close()
    
    def update_position(self, position_id, title, department_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE positions SET title = ?, department_id = ? WHERE id = ?", (title, department_id, position_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    
    def add_leave_request(self, leave_data):
        """Inserts a new leave request into the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO leaves (employee_id, leave_type, start_date, end_date, reason, status)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            leave_data['employee_id'],
            leave_data['leave_type'],
            leave_data['start_date'],
            leave_data['end_date'],
            leave_data.get('reason', ''),
            leave_data.get('status', 'Pending')
        ))
        
        leave_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return leave_id
    
    def get_leave_requests(self, employee_id=None, status=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT l.*, e.first_name, e.last_name, e.employee_id as emp_id
        FROM leaves l
        JOIN employees e ON l.employee_id = e.id
        WHERE 1=1
        '''
        params = []
        
        if employee_id:
            query += " AND l.employee_id = ?"
            params.append(employee_id)
        
        if status:
            query += " AND l.status = ?"
            params.append(status)
        
        query += " ORDER BY l.start_date DESC, e.last_name, e.first_name"
        
        cursor.execute(query, params)
        leaves = cursor.fetchall()
        conn.close()
        return leaves
    
    def update_leave_status(self, leave_id, status, approved_by=None):
        """Updates leave request status in the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
    
        if approved_by and status == "Approved":
            cursor.execute('''
            UPDATE leaves
            SET status = ?, approved_by = ?, approved_at = CURRENT_TIMESTAMP
            WHERE id = ?
            ''', (status, approved_by, leave_id))
        else:
            cursor.execute('''
            UPDATE leaves
            SET status = ?
            WHERE id = ?
            ''', (status, leave_id))
    
        conn.commit()
        conn.close()

    
    def backup_database(self, backup_file):
        try:
            # Create a copy of the database file
            with open(self.db_file, 'rb') as src, open(backup_file, 'wb') as dst:
                dst.write(src.read())
            return True
        except Exception as e:
            print(f"Backup error: {e}")
            return False
    
    def export_employees_to_csv(self, csv_file):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT e.*, d.name as department_name, p.title as position_title
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.id
        LEFT JOIN positions p ON e.position_id = p.id
        ORDER BY e.last_name, e.first_name
        ''')
        
        employees = cursor.fetchall()
        
        try:
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Write header
                writer.writerow([
                    'Employee ID', 'First Name', 'Last Name', 'Gender', 
                    'Date of Birth', 'Address', 'Phone', 'Email',
                    'Department', 'Position', 'Hire Date', 
                    'Termination Date', 'Base Salary', 'Status'
                ])
                
                # Write data
                for emp in employees:
                    writer.writerow([
                        emp['employee_id'], emp['first_name'], emp['last_name'],
                        emp['gender'], emp['date_of_birth'], emp['address'],
                        emp['phone'], emp['email'], emp['department_name'],
                        emp['position_title'], emp['hire_date'],
                        emp['termination_date'], emp['base_salary'], emp['status']
                    ])
            
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
        finally:
            conn.close()


class LoginDialog(QDialog):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.user = None
        
        self.setWindowTitle("Employee Accounting System - Login")
        self.setMinimumWidth(300)
        
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept_login)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def accept_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "Please enter username and password")
            return
        
        self.user = self.database.authenticate_user(username, password)
        
        if self.user:
            self.accept()
        else:
            QMessageBox.warning(self, "Login Error", "Invalid username or password")


class EmployeeForm(QDialog):
    def __init__(self, database, parent=None, employee_id=None):
        super().__init__(parent)
        self.database = database
        self.employee_id = employee_id
        self.setWindowTitle("Employee Form")  # Set a title for the dialog
        self.setMinimumWidth(600)  # Optional: Set a minimum width for better UI
        self.init_ui()
        
        if employee_id:
            self.load_employee_data()

    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Personal Information
        personal_group = QGroupBox("Personal Information")
        personal_layout = QGridLayout()
        
        self.employee_id_input = QLineEdit()
        personal_layout.addWidget(QLabel("Employee ID:"), 0, 0)
        personal_layout.addWidget(self.employee_id_input, 0, 1)
        
        self.first_name_input = QLineEdit()
        personal_layout.addWidget(QLabel("First Name:"), 0, 2)
        personal_layout.addWidget(self.first_name_input, 0, 3)
        
        self.last_name_input = QLineEdit()
        personal_layout.addWidget(QLabel("Last Name:"), 1, 0)
        personal_layout.addWidget(self.last_name_input, 1, 1)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female", "Other"])
        personal_layout.addWidget(QLabel("Gender:"), 1, 2)
        personal_layout.addWidget(self.gender_input, 1, 3)
        
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setCalendarPopup(True)
        self.dob_input.setDate(QDate.currentDate().addYears(-30))
        personal_layout.addWidget(QLabel("Date of Birth:"), 2, 0)
        personal_layout.addWidget(self.dob_input, 2, 1)
        
        self.phone_input = QLineEdit()
        personal_layout.addWidget(QLabel("Phone:"), 2, 2)
        personal_layout.addWidget(self.phone_input, 2, 3)
        
        self.email_input = QLineEdit()
        personal_layout.addWidget(QLabel("Email:"), 3, 0)
        personal_layout.addWidget(self.email_input, 3, 1)
        
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(60)
        personal_layout.addWidget(QLabel("Address:"), 4, 0, 1, 1)
        personal_layout.addWidget(self.address_input, 4, 1, 1, 3)
        
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)
        
        # Employment Information
        employment_group = QGroupBox("Employment Information")
        employment_layout = QGridLayout()
        
        self.department_input = QComboBox()
        self.load_departments()
        employment_layout.addWidget(QLabel("Department:"), 0, 0)
        employment_layout.addWidget(self.department_input, 0, 1)
        
        self.position_input = QComboBox()
        employment_layout.addWidget(QLabel("Position:"), 0, 2)
        employment_layout.addWidget(self.position_input, 0, 3)
        # positions = ["Manager","Employee", "Developer", "Designer", "Analyst", "Tester"]
        # self.position_input.addItems(positions)
        # self.position_input.setCurrentText("Developer")  # Set by text value
        
        self.department_input.currentIndexChanged.connect(self.load_positions)
        
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setDisplayFormat("yyyy-MM-dd")
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        employment_layout.addWidget(QLabel("Hire Date:"), 1, 0)
        employment_layout.addWidget(self.hire_date_input, 1, 1)
        
        self.termination_date_input = QDateEdit()
        self.termination_date_input.setDisplayFormat("yyyy-MM-dd")
        self.termination_date_input.setCalendarPopup(True)
        self.termination_date_input.setDate(QDate.currentDate())
        self.termination_date_input.setEnabled(False)
        employment_layout.addWidget(QLabel("Termination Date:"), 1, 2)
        employment_layout.addWidget(self.termination_date_input, 1, 3)
        
        self.status_input = QComboBox()
        self.status_input.addItems(["Active", "On Leave", "Terminated"])
        self.status_input.currentTextChanged.connect(self.on_status_change)
        employment_layout.addWidget(QLabel("Status:"), 2, 0)
        employment_layout.addWidget(self.status_input, 2, 1)
        
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0, 1000000)
        self.salary_input.setPrefix("$")
        self.salary_input.setValue(50000)
        employment_layout.addWidget(QLabel("Base Salary:"), 2, 2)
        employment_layout.addWidget(self.salary_input, 2, 3)
        
        employment_group.setLayout(employment_layout)
        layout.addWidget(employment_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        if self.employee_id:
            self.save_button = QPushButton("Update Employee")
            self.save_button.clicked.connect(self.update_employee)
        else:
            self.save_button = QPushButton("Add Employee")
            self.save_button.clicked.connect(self.add_employee)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_departments(self):
        self.department_input.clear()
        departments = self.database.get_departments()
        
        for dept in departments:
            self.department_input.addItem(dept['name'], dept['id'])
    
    def load_positions(self):
        self.position_input.clear()
        department_id = self.department_input.currentData()
    
        if department_id is None:
            print("DEBUG: No department selected.")  # Debugging
            return
    
        positions = self.database.get_positions(department_id)
    
        if not positions:
            print("DEBUG: No positions found for department:", department_id)  # Debugging
    
        for pos in positions:
            self.position_input.addItem(pos['title'], pos['id'])

    
    def on_status_change(self, status):
        if status == "Terminated":
            self.termination_date_input.setEnabled(True)
        else:
            self.termination_date_input.setEnabled(False)
    
    def load_employee_data(self):
        employee = self.database.get_employee_by_id(self.employee_id)
        
        if not employee:
            QMessageBox.warning(self, "Error", "Employee not found")
        self.employee_id_input.setText(employee["employee_id"])
        self.first_name_input.setText(employee["first_name"])
        self.last_name_input.setText(employee["last_name"])
        self.gender_input.setCurrentText(employee["gender"])
        self.dob_input.setDate(QDate.fromString(employee["date_of_birth"], "yyyy-MM-dd"))
        self.phone_input.setText(employee["phone"])
        self.email_input.setText(employee["email"])
        self.address_input.setPlainText(employee["address"])
        self.hire_date_input.setDate(QDate.fromString(employee["hire_date"], "yyyy-MM-dd"))
        self.termination_date_input.setDate(QDate.fromString(employee["termination_date"], "yyyy-MM-dd") if employee["termination_date"] else QDate.currentDate())
        self.salary_input.setValue(employee["base_salary"])
        self.status_input.setCurrentText(employee["status"])
    
        # Set department and position
        index = self.department_input.findData(employee["department_id"])
        if index != -1:
            self.department_input.setCurrentIndex(index)
            self.load_positions()
        
        index = self.position_input.findData(employee["position_id"])
        if index != -1:
            self.position_input.setCurrentIndex(index)

    def add_employee(self):
        # ✅ Collect Employee Data First
        employee_data = self.collect_employee_data()
    
        # ✅ Validate Employee Data
        if not self.validate_employee_data(employee_data):
            return
    
        # ✅ Check for Duplicate Employee ID
        existing_employee = self.database.get_employee_by_id(employee_data["employee_id"])
        if existing_employee:
            QMessageBox.warning(self, "Error", "Employee ID already exists. Please use a unique Employee ID.")
            return
    
        # ✅ Insert into Database
        employee_id = self.database.add_employee(employee_data)
    
        if employee_id:
            QMessageBox.information(self, "Success", "Employee added successfully!")
    
            # ✅ Refresh Employee List Automatically
            parent = self.parent()
            if isinstance(parent, EmployeeManagementTab):
                parent.load_employees()
    
            self.accept()  # ✅ Properly closes the form
        else:
            QMessageBox.warning(self, "Error", "Failed to add employee. Please try again.")

    
    def update_employee(self):
        employee_data = self.collect_employee_data()
        
        if not self.validate_employee_data(employee_data):
            return
        
        self.database.update_employee(self.employee_id, employee_data)
        QMessageBox.information(self, "Success", "Employee updated successfully")
        self.close()
    
    def collect_employee_data(self):
        return {
            "employee_id": self.employee_id_input.text(),
            "first_name": self.first_name_input.text(),
            "last_name": self.last_name_input.text(),
            "gender": self.gender_input.currentText(),
            "date_of_birth": self.dob_input.date().toString("yyyy-MM-dd"),
            "phone": self.phone_input.text(),
            "email": self.email_input.text(),
            "address": self.address_input.toPlainText(),
            "department_id": self.department_input.currentData(),
            "position_id": self.position_input.currentData(),
            "hire_date": self.hire_date_input.date().toString("yyyy-MM-dd"),
            "termination_date": self.termination_date_input.date().toString("yyyy-MM-dd") if self.status_input.currentText() == "Terminated" else None,
            "base_salary": self.salary_input.value(),
            "status": self.status_input.currentText(),
        }
    
    def validate_employee_data(self, data):
        if not data["employee_id"] or not data["first_name"] or not data["last_name"]:
            QMessageBox.warning(self, "Validation Error", "Employee ID, First Name, and Last Name are required")
            return False
        
        if data["base_salary"] <= 0:
            QMessageBox.warning(self, "Validation Error", "Base salary must be greater than zero")
            return False
        
        return True
# Continue from the previous code...

class EmployeeManagementTab(QWidget):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search and filter controls
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employees...")
        self.search_input.textChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addWidget(QLabel("Department:"))
        
        self.department_filter = QComboBox()
        self.department_filter.addItem("All Departments", None)
        departments = self.database.get_departments()
        for dept in departments:
            self.department_filter.addItem(dept['name'], dept['id'])
        self.department_filter.currentIndexChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.department_filter)
        
        filter_layout.addWidget(QLabel("Status:"))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "On Leave", "Terminated"])
        self.status_filter.currentTextChanged.connect(self.filter_employees)
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Employees table
        self.employees_table = QTableWidget()
        self.employees_table.setColumnCount(8)
        self.employees_table.setHorizontalHeaderLabels([
            "ID", "Name", "Department", "Position", 
            "Hire Date", "Status", "Salary", "Actions"
        ])
        self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.employees_table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Employee")
        self.add_button.clicked.connect(self.add_employee)
        buttons_layout.addWidget(self.add_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_employees)
        buttons_layout.addWidget(self.refresh_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Load employees
        self.load_employees()
    
    def load_employees(self):
        search_text = self.search_input.text() if self.search_input.text() else None
        department_id = self.department_filter.currentData()
        status = self.status_filter.currentText() if self.status_filter.currentText() != "All" else None
        
        employees = self.database.get_employees(search_text, department_id, status)
        
        self.employees_table.setRowCount(0)
        
        for employee in employees:
            row_position = self.employees_table.rowCount()
            self.employees_table.insertRow(row_position)
            
            self.employees_table.setItem(row_position, 0, QTableWidgetItem(employee['employee_id']))
            self.employees_table.setItem(row_position, 1, QTableWidgetItem(f"{employee['first_name']} {employee['last_name']}"))
            self.employees_table.setItem(row_position, 2, QTableWidgetItem(employee['department_name'] or ""))
            self.employees_table.setItem(row_position, 3, QTableWidgetItem(employee['position_title'] or ""))
            self.employees_table.setItem(row_position, 4, QTableWidgetItem(employee['hire_date']))
            self.employees_table.setItem(row_position, 5, QTableWidgetItem(employee['status']))
            
            salary_item = QTableWidgetItem(f"${employee['base_salary']:.2f}")
            salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.employees_table.setItem(row_position, 6, salary_item)
            
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(4, 4, 4, 4)
            
            edit_button = QPushButton("Edit")
            edit_button.setFixedWidth(60)
            edit_button.clicked.connect(lambda checked, id=employee['id']: self.edit_employee(id))
            
            delete_button = QPushButton("Delete")
            delete_button.setFixedWidth(60)
            delete_button.clicked.connect(lambda checked, id=employee['id']: self.delete_employee(id))
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            
            self.employees_table.setCellWidget(row_position, 7, actions_widget)
    
    def filter_employees(self):
        self.load_employees()
    
    def add_employee(self):
        """Opens the employee form and refreshes the payroll list if an employee is added"""
        form = EmployeeForm(self.database, self)
        if form.exec_():  # ✅ Only refresh if an employee was successfully added
            self.load_employees()
    
            # ✅ Refresh Payroll Tab if it exists
            parent = self.parent()
            if isinstance(parent, QTabWidget):  # Ensure we're working within the main window
                for i in range(parent.count()):
                    tab = parent.widget(i)
                    if isinstance(tab, PayrollTab):
                        tab.load_employees()  # ✅ Refresh Payroll Employees
                        break

    
    def edit_employee(self, employee_id):
        form = EmployeeForm(self.database, self, employee_id)
        form.setWindowTitle("Edit Employee")
        form.exec_()
        self.load_employees()
    
    def delete_employee(self, employee_id):
        reply = QMessageBox.question(
            self, "Confirm Deletion", 
            "Are you sure you want to delete this employee?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.database.delete_employee(employee_id)
            self.load_employees()


class PayrollTab(QWidget):
    def __init__(self, database, user, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = user
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        tabs = QTabWidget()
    
        # Create Payroll Tab
        create_payroll_tab = QWidget()
        create_layout = QVBoxLayout()
        form_layout = QFormLayout()
    
        # ✅ Employee Selection (Allow Typing & Choosing)
        self.employee_combo = QComboBox()
        self.employee_combo.setEditable(True)  # ✅ Enable typing
        form_layout.addRow("Employee:", self.employee_combo)
    
        self.load_employees()  # ✅ Load employee list
        create_layout.addLayout(form_layout)
    
        create_payroll_tab.setLayout(create_layout)
        tabs.addTab(create_payroll_tab, "Create Payroll")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
        # ✅ Refresh salary when employee is chosen or typed
        self.employee_combo.currentIndexChanged.connect(self.update_base_salary)
        self.employee_combo.editTextChanged.connect(self.update_base_salary)
    
        QTimer.singleShot(0, self.update_base_salary)  # ✅ Ensure base salary updates
    
        # Employee Selection
        self.employee_combo = QComboBox()
        self.load_employees()
        form_layout.addRow("Employee:", self.employee_combo)
    
        # Pay Period
        period_layout = QHBoxLayout()
        self.period_start = QDateEdit()
        self.period_start.setDisplayFormat("yyyy-MM-dd")
        self.period_start.setCalendarPopup(True)
        self.period_start.setDate(QDate.currentDate().addDays(-14))
        period_layout.addWidget(self.period_start)
    
        period_layout.addWidget(QLabel("to"))
    
        self.period_end = QDateEdit()
        self.period_end.setDisplayFormat("yyyy-MM-dd")
        self.period_end.setCalendarPopup(True)
        self.period_end.setDate(QDate.currentDate())
        period_layout.addWidget(self.period_end)
    
        form_layout.addRow("Pay Period:", period_layout)
    
        # ✅ Base Salary (Defined Before Bonuses/Deductions)
        self.base_salary = QDoubleSpinBox()
        self.base_salary.setRange(0, 100000)
        self.base_salary.setPrefix("$")
        self.base_salary.setDecimals(2)
        self.base_salary.setValue(0.00)
        self.base_salary.setEnabled(False)  # Auto-updated by employee selection
        form_layout.addRow("Base Salary:", self.base_salary)
    
        create_layout.addLayout(form_layout)
    
        # ✅ Bonuses (Define Before Calling `update_base_salary()`)
        bonus_group = QGroupBox("Bonuses")
        bonus_layout = QVBoxLayout()
    
        self.bonuses_table = QTableWidget()  # ✅ Ensure bonuses_table is created
        self.bonuses_table.setColumnCount(2)
        self.bonuses_table.setHorizontalHeaderLabels(["Amount", "Reason"])
        self.bonuses_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        bonus_layout.addWidget(self.bonuses_table)
    
        bonus_button_layout = QHBoxLayout()
        self.add_bonus_button = QPushButton("Add Bonus")
        self.add_bonus_button.clicked.connect(self.add_bonus)
        bonus_button_layout.addWidget(self.add_bonus_button)
    
        self.remove_bonus_button = QPushButton("Remove Bonus")
        self.remove_bonus_button.clicked.connect(self.remove_bonus)
        bonus_button_layout.addWidget(self.remove_bonus_button)
    
        bonus_layout.addLayout(bonus_button_layout)
        bonus_group.setLayout(bonus_layout)
        create_layout.addWidget(bonus_group)
    
        # ✅ Deductions (Define Before Calling `update_base_salary()`)
        deduction_group = QGroupBox("Deductions")
        deduction_layout = QVBoxLayout()
    
        self.deductions_table = QTableWidget()  # ✅ Ensure deductions_table is created
        self.deductions_table.setColumnCount(2)
        self.deductions_table.setHorizontalHeaderLabels(["Amount", "Reason"])
        self.deductions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        deduction_layout.addWidget(self.deductions_table)
    
        deduction_button_layout = QHBoxLayout()
        self.add_deduction_button = QPushButton("Add Deduction")
        self.add_deduction_button.clicked.connect(self.add_deduction)
        deduction_button_layout.addWidget(self.add_deduction_button)
    
        self.remove_deduction_button = QPushButton("Remove Deduction")
        self.remove_deduction_button.clicked.connect(self.remove_deduction)
        deduction_button_layout.addWidget(self.remove_deduction_button)
    
        deduction_layout.addLayout(deduction_button_layout)
        deduction_group.setLayout(deduction_layout)
        create_layout.addWidget(deduction_group)
    
        # ✅ Payment Details
        payment_layout = QHBoxLayout()
        payment_layout.addWidget(QLabel("Payment Date:"))
    
        self.payment_date = QDateEdit()
        self.payment_date.setDisplayFormat("yyyy-MM-dd")
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        payment_layout.addWidget(self.payment_date)
    
        payment_layout.addWidget(QLabel("Payment Method:"))
        self.payment_method = QComboBox()
        self.payment_method.addItems(["Direct Deposit", "Check", "Cash"])
        payment_layout.addWidget(self.payment_method)
    
        payment_layout.addWidget(QLabel("Status:"))
        self.payment_status = QComboBox()
        self.payment_status.addItems(["Pending", "Processed", "Completed"])
        payment_layout.addWidget(self.payment_status)
    
        create_layout.addLayout(payment_layout)
    
        # ✅ Summary
        summary_layout = QHBoxLayout()
        self.total_bonus_label = QLabel("$0.00")
        summary_layout.addWidget(QLabel("Total Bonuses:"))
        summary_layout.addWidget(self.total_bonus_label)
    
        self.total_deduction_label = QLabel("$0.00")
        summary_layout.addWidget(QLabel("Total Deductions:"))
        summary_layout.addWidget(self.total_deduction_label)
    
        self.net_salary_label = QLabel("$0.00")
        summary_layout.addWidget(QLabel("Net Salary:"))
        summary_layout.addWidget(self.net_salary_label)
    
        create_layout.addLayout(summary_layout)
    
        # ✅ Calculate & Create Payroll Buttons
        button_layout = QHBoxLayout()
        self.calculate_button = QPushButton("Calculate")
        self.calculate_button.clicked.connect(self.calculate_payroll)
        button_layout.addWidget(self.calculate_button)
    
        self.create_payroll_button = QPushButton("Create Payroll")
        self.create_payroll_button.clicked.connect(self.create_payroll)
        button_layout.addWidget(self.create_payroll_button)
    
        create_layout.addLayout(button_layout)
        create_payroll_tab.setLayout(create_layout)
        tabs.addTab(create_payroll_tab, "Create Payroll")
    
        # ✅ Payroll History Tab
        history_tab = QWidget()
        history_layout = QVBoxLayout()
    
        # Filter Controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Employee:"))
    
        self.history_employee_combo = QComboBox()
        self.history_employee_combo.addItem("All Employees", None)
        employees = self.database.get_employees()
        for employee in employees:
            self.history_employee_combo.addItem(
                f"{employee['first_name']} {employee['last_name']} ({employee['employee_id']})",
                employee['id']
            )
        self.history_employee_combo.currentIndexChanged.connect(self.load_payroll_history)
        filter_layout.addWidget(self.history_employee_combo)
    
        filter_layout.addWidget(QLabel("From:"))
        self.history_from_date = QDateEdit()
        self.history_from_date.setDisplayFormat("yyyy-MM-dd")
        self.history_from_date.setCalendarPopup(True)
        self.history_from_date.setDate(QDate.currentDate().addMonths(-3))
        self.history_from_date.dateChanged.connect(self.load_payroll_history)
        filter_layout.addWidget(self.history_from_date)
    
        filter_layout.addWidget(QLabel("To:"))
        self.history_to_date = QDateEdit()
        self.history_to_date.setDisplayFormat("yyyy-MM-dd")
        self.history_to_date.setCalendarPopup(True)
        self.history_to_date.setDate(QDate.currentDate())
        self.history_to_date.dateChanged.connect(self.load_payroll_history)
        filter_layout.addWidget(self.history_to_date)
    
        history_layout.addLayout(filter_layout)
    
        # Payroll History Table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Employee", "Period", "Base Salary", "Bonuses", 
            "Deductions", "Net Salary", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        history_layout.addWidget(self.history_table)
    
        history_tab.setLayout(history_layout)
        tabs.addTab(history_tab, "Payroll History")
    
        layout.addWidget(tabs)
    
        # ✅ Set Layout Before Calling Update Methods
        self.setLayout(layout)
    
        # ✅ Ensure Employee Selection Event is Connected ONCE
        self.employee_combo.currentIndexChanged.connect(self.update_base_salary)
    
        # ✅ Call `update_base_salary()` Safely After UI is Initialized
        QTimer.singleShot(0, self.update_base_salary)
        self.load_payroll_history()

    
    def load_employees(self):
        """Load employees into the combo box with autocomplete."""
        self.employee_combo.clear()
        self.employee_data = {}  # ✅ Store employee info in a dictionary
        employees = self.database.get_employees(status="Active")
    
        if not employees:
            self.employee_combo.addItem("No employees found", None)
            return
    
        employee_names = []
        for employee in employees:
            name = f"{employee['first_name']} {employee['last_name']} ({employee['employee_id']})"
            self.employee_combo.addItem(name, (employee['id'], employee['base_salary']))
            self.employee_data[name] = (employee['id'], employee['base_salary'])  # ✅ Store for lookup
            employee_names.append(name)
    
        # ✅ Enable auto-completion when typing employee names
        completer = QCompleter(employee_names, self.employee_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.employee_combo.setCompleter(completer)
    
        # ✅ Refresh base salary if an employee is pre-selected
        if employees:
            self.update_base_salary()
    
    def update_base_salary(self):
        """Update the base salary when an employee is selected or typed."""
        if not hasattr(self, 'base_salary'):
            print("DEBUG: base_salary not initialized yet.")
            return  # Prevent errors if UI element isn't ready
    
        text = self.employee_combo.currentText().strip()
    
        if text in self.employee_data:  # ✅ If typed name exists in dictionary
            employee_id, salary = self.employee_data[text]
            self.base_salary.setValue(salary)  # ✅ Update base salary
            self.calculate_payroll()
        else:
            self.base_salary.setValue(0.00)  # Reset salary if invalid name
    
    def add_bonus(self):
        row_position = self.bonuses_table.rowCount()
        self.bonuses_table.insertRow(row_position)
        
        amount_item = QTableWidgetItem("0.00")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bonuses_table.setItem(row_position, 0, amount_item)
        
        self.bonuses_table.setItem(row_position, 1, QTableWidgetItem(""))
        
        self.calculate_payroll()
    
    def remove_bonus(self):
        selected_rows = self.bonuses_table.selectionModel().selectedRows()
        for row in sorted(selected_rows, reverse=True):
            self.bonuses_table.removeRow(row.row())
        
        self.calculate_payroll()
    
    def add_deduction(self):
        row_position = self.deductions_table.rowCount()
        self.deductions_table.insertRow(row_position)
        
        amount_item = QTableWidgetItem("0.00")
        amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.deductions_table.setItem(row_position, 0, amount_item)
        
        self.deductions_table.setItem(row_position, 1, QTableWidgetItem(""))
        
        self.calculate_payroll()
    
    def remove_deduction(self):
        selected_rows = self.deductions_table.selectionModel().selectedRows()
        for row in sorted(selected_rows, reverse=True):
            self.deductions_table.removeRow(row.row())
        
        self.calculate_payroll()
    
    def calculate_payroll(self):
        """Calculates net salary based on base salary, bonuses, and deductions."""
        base_salary = self.base_salary.value()
    
        # ✅ Calculate total bonuses safely
        total_bonus = 0
        for row in range(self.bonuses_table.rowCount()):
            amount_item = self.bonuses_table.item(row, 0)
            if amount_item and amount_item.text().strip():
                try:
                    total_bonus += float(amount_item.text().replace('$', '').strip())
                except ValueError:
                    QMessageBox.warning(self, "Error", f"Invalid bonus amount at row {row + 1}. Please enter a number.")
                    return
    
        # ✅ Calculate total deductions safely
        total_deduction = 0
        for row in range(self.deductions_table.rowCount()):
            amount_item = self.deductions_table.item(row, 0)
            if amount_item and amount_item.text().strip():
                try:
                    total_deduction += float(amount_item.text().replace('$', '').strip())
                except ValueError:
                    QMessageBox.warning(self, "Error", f"Invalid deduction amount at row {row + 1}. Please enter a number.")
                    return
    
        # ✅ Calculate net salary correctly
        net_salary = base_salary + total_bonus - total_deduction
    
        # ✅ Update UI labels correctly
        self.total_bonus_label.setText(f"${total_bonus:.2f}")
        self.total_deduction_label.setText(f"${total_deduction:.2f}")
        self.net_salary_label.setText(f"${net_salary:.2f}")

    
    def create_payroll(self):
        if not self.employee_combo.currentData():
            QMessageBox.warning(self, "Error", "Please select an employee")
            return
        
        employee_id, _ = self.employee_combo.currentData()
        
        # Validate dates
        if self.period_start.date() > self.period_end.date():
            QMessageBox.warning(self, "Error", "Pay period start date must be before end date")
            return
        
        # Get base salary
        base_salary = self.base_salary.value()
        
        # Get bonuses
        bonuses = []
        for row in range(self.bonuses_table.rowCount()):
            amount_item = self.bonuses_table.item(row, 0)
            reason_item = self.bonuses_table.item(row, 1)
            
            if amount_item and reason_item:
                try:
                    amount = float(amount_item.text().replace('$', '').strip())
                    reason = reason_item.text()
                    
                    bonuses.append({"amount": amount, "reason": reason})
                except ValueError:
                    QMessageBox.warning(self, "Error", f"Invalid bonus amount at row {row + 1}")
                    return
        
        # Get deductions
        deductions = []
        for row in range(self.deductions_table.rowCount()):
            amount_item = self.deductions_table.item(row, 0)
            reason_item = self.deductions_table.item(row, 1)
            
            if amount_item and reason_item:
                try:
                    amount = float(amount_item.text().replace('$', '').strip())
                    reason = reason_item.text()
                    
                    deductions.append({"amount": amount, "reason": reason})
                except ValueError:
                    QMessageBox.warning(self, "Error", f"Invalid deduction amount at row {row + 1}")
                    return
        
        # Calculate totals
        total_bonus = sum(bonus["amount"] for bonus in bonuses)
        total_deduction = sum(deduction["amount"] for deduction in deductions)
        net_salary = base_salary + total_bonus - total_deduction
        
        # Create payroll data
        payroll_data = {
            "employee_id": employee_id,
            "pay_period_start": self.period_start.date().toString("yyyy-MM-dd"),
            "pay_period_end": self.period_end.date().toString("yyyy-MM-dd"),
            "base_salary": base_salary,
            "total_bonus": total_bonus,
            "total_deduction": total_deduction,
            "net_salary": net_salary,
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd"),
            "payment_method": self.payment_method.currentText(),
            "payment_status": self.payment_status.currentText(),
            "created_by": self.user["id"],
            "bonuses": bonuses,
            "deductions": deductions
        }
        
        # Save to database
        payroll_id = self.database.create_payroll(payroll_data)
        
        if payroll_id:
            QMessageBox.information(self, "Success", "Payroll created successfully")
            self.load_payroll_history()
        else:
            QMessageBox.warning(self, "Error", "Failed to create payroll")

    def load_payroll_history(self):
        employee_id = self.history_employee_combo.currentData()
        from_date = self.history_from_date.date().toString("yyyy-MM-dd")
        to_date = self.history_to_date.date().toString("yyyy-MM-dd")
        
        payrolls = self.database.get_payroll_history(employee_id, from_date, to_date)
        
        self.history_table.setRowCount(0)
        
        for payroll in payrolls:
            row_position = self.history_table.rowCount()
            self.history_table.insertRow(row_position)
            
            self.history_table.setItem(row_position, 0, QTableWidgetItem(f"{payroll['first_name']} {payroll['last_name']}"))
            self.history_table.setItem(row_position, 1, QTableWidgetItem(f"{payroll['pay_period_start']} to {payroll['pay_period_end']}"))
            
            base_salary_item = QTableWidgetItem(f"${payroll['base_salary']:.2f}")
            base_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.history_table.setItem(row_position, 2, base_salary_item)
            
            bonus_item = QTableWidgetItem(f"${payroll['total_bonus']:.2f}")
            bonus_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.history_table.setItem(row_position, 3, bonus_item)
            
            deduction_item = QTableWidgetItem(f"${payroll['total_deduction']:.2f}")
            deduction_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.history_table.setItem(row_position, 4, deduction_item)
            
            net_salary_item = QTableWidgetItem(f"${payroll['net_salary']:.2f}")
            net_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.history_table.setItem(row_position, 5, net_salary_item)
            
            self.history_table.setItem(row_position, 6, QTableWidgetItem(payroll['payment_status']))

class ManageDepartmentsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Manage Departments")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Table to display departments
        self.department_table = QTableWidget()
        self.department_table.setColumnCount(3)
        self.department_table.setHorizontalHeaderLabels(["ID", "Department Name", "Actions"])
        self.department_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.department_table)

        # Load existing departments
        self.load_departments()

        # Buttons for actions
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Department")
        self.add_button.clicked.connect(self.add_department)
        button_layout.addWidget(self.add_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_departments(self):
        """Loads departments into the table."""
        self.department_table.setRowCount(0)
        departments = self.database.get_departments()

        for department in departments:
            row_position = self.department_table.rowCount()
            self.department_table.insertRow(row_position)

            self.department_table.setItem(row_position, 0, QTableWidgetItem(str(department["id"])))
            self.department_table.setItem(row_position, 1, QTableWidgetItem(department["name"]))

            # Create Edit & Delete buttons
            actions_layout = QHBoxLayout()
            edit_button = QPushButton("Edit")
            edit_button.setFixedWidth(60)
            edit_button.clicked.connect(lambda _, id=department["id"], name=department["name"]: self.edit_department(id, name))

            delete_button = QPushButton("Delete")
            delete_button.setFixedWidth(60)
            delete_button.clicked.connect(lambda _, id=department["id"]: self.delete_department(id))

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)

            self.department_table.setCellWidget(row_position, 2, actions_widget)

    def add_department(self):
        """Opens a dialog to add a new department."""
        text, ok = QInputDialog.getText(self, "Add Department", "Enter Department Name:")
        if ok and text.strip():
            dept_id = self.database.add_department(text.strip())
            if dept_id:
                QMessageBox.information(self, "Success", "Department added successfully!")
                self.load_departments()
            else:
                QMessageBox.warning(self, "Error", "Failed to add department.")

    def edit_department(self, department_id, old_name):
        """Opens a dialog to edit an existing department."""
        new_name, ok = QInputDialog.getText(self, "Edit Department", "Modify Department Name:", text=old_name)
        if ok and new_name.strip():
            conn = self.database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE departments SET name = ? WHERE id = ?", (new_name.strip(), department_id))
                conn.commit()
                QMessageBox.information(self, "Success", "Department updated successfully!")
                self.load_departments()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Department name already exists!")
            finally:
                conn.close()

    def delete_department(self, department_id):
        """Deletes a department after confirmation."""
        reply = QMessageBox.question(self, "Delete Department",
                                     "Are you sure you want to delete this department?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM departments WHERE id = ?", (department_id,))
                conn.commit()
                QMessageBox.information(self, "Success", "Department deleted successfully!")
                self.load_departments()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Cannot delete department that has positions or employees assigned!")
            finally:
                conn.close()
class PositionFormDialog(QDialog):
    def __init__(self, database, position_id=None, position_title="", department_id=None, parent=None):
        super().__init__(parent)
        self.database = database
        self.position_id = position_id
        self.setWindowTitle("Edit Position" if position_id else "Add Position")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.title_input = QLineEdit(position_title)
        form_layout.addRow("Position Title:", self.title_input)

        self.department_input = QComboBox()
        departments = self.database.get_departments()
        for dept in departments:
            self.department_input.addItem(dept["name"], dept["id"])
        if department_id:
            index = self.department_input.findData(department_id)
            if index != -1:
                self.department_input.setCurrentIndex(index)

        form_layout.addRow("Department:", self.department_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_position)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_position(self):
        title = self.title_input.text().strip()
        department_id = self.department_input.currentData()

        if not title:
            QMessageBox.warning(self, "Error", "Position title cannot be empty!")
            return

        conn = self.database.get_connection()
        cursor = conn.cursor()
        try:
            if self.position_id:
                cursor.execute("UPDATE positions SET title = ?, department_id = ? WHERE id = ?", (title, department_id, self.position_id))
            else:
                cursor.execute("INSERT INTO positions (title, department_id) VALUES (?, ?)", (title, department_id))
            conn.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Position title already exists in this department!")
        finally:
            conn.close()
class ManagePositionsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Manage Positions")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()

        # Table to display positions
        self.position_table = QTableWidget()
        self.position_table.setColumnCount(4)
        self.position_table.setHorizontalHeaderLabels(["ID", "Position Title", "Department", "Actions"])
        self.position_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.position_table)

        # Load existing positions
        self.load_positions()

        # Buttons for actions
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Position")
        self.add_button.clicked.connect(self.add_position)
        button_layout.addWidget(self.add_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_positions(self):
        """Loads positions into the table."""
        self.position_table.setRowCount(0)
        positions = self.database.get_positions()
    
        if not positions:
            print("DEBUG: No positions found in database.")  # Debugging
    
        for position in positions:
            row_position = self.position_table.rowCount()
            self.position_table.insertRow(row_position)
    
            self.position_table.setItem(row_position, 0, QTableWidgetItem(str(position["id"])))
            self.position_table.setItem(row_position, 1, QTableWidgetItem(position["title"]))
    
            # Fetch department name
            department_name = "Unknown"
            departments = self.database.get_departments()
            for dept in departments:
                if dept["id"] == position["department_id"]:
                    department_name = dept["name"]
                    break
            self.position_table.setItem(row_position, 2, QTableWidgetItem(department_name))
    
            # Create Edit & Delete buttons
            actions_layout = QHBoxLayout()
            edit_button = QPushButton("Edit")
            edit_button.setFixedWidth(60)
            edit_button.clicked.connect(lambda _, id=position["id"], title=position["title"], dept_id=position["department_id"]: self.edit_position(id, title, dept_id))
    
            delete_button = QPushButton("Delete")
            delete_button.setFixedWidth(60)
            delete_button.clicked.connect(lambda _, id=position["id"]: self.delete_position(id))
    
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
    
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
    
            self.position_table.setCellWidget(row_position, 3, actions_widget)


    def add_position(self):
        """Opens a dialog to add a new position."""
        dialog = PositionFormDialog(self.database)
        if dialog.exec_():
            self.load_positions()

    def edit_position(self, position_id, old_title, department_id):
        """Opens a dialog to edit an existing position."""
        dialog = PositionFormDialog(self.database, position_id, old_title, department_id)
        if dialog.exec_():
            self.load_positions()

    def delete_position(self, position_id):
        """Deletes a position after confirmation."""
        reply = QMessageBox.question(self, "Delete Position",
                                     "Are you sure you want to delete this position?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM positions WHERE id = ?", (position_id,))
                conn.commit()
                QMessageBox.information(self, "Success", "Position deleted successfully!")
                self.load_positions()
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", "Cannot delete a position that is assigned to employees!")
            finally:
                conn.close()

class PayrollReportDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Payroll Report")
        self.setMinimumWidth(700)
        self.setMinimumHeight(400)

        layout = QVBoxLayout()

        # Date Range Filters
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # Default: Last month
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())  # Default: Today
        filter_layout.addWidget(self.to_date)

        # Department Filter
        filter_layout.addWidget(QLabel("Department:"))
        self.department_input = QComboBox()
        self.department_input.addItem("All Departments", None)
        departments = self.database.get_departments()
        for dept in departments:
            self.department_input.addItem(dept["name"], dept["id"])
        filter_layout.addWidget(self.department_input)

        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.load_report)
        filter_layout.addWidget(self.generate_button)

        layout.addLayout(filter_layout)

        # Table to Show Payroll Report
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "Department", "Payroll Count", "Employees Paid", 
            "Total Salary", "Total Bonuses", "Total Deductions", "Net Salary"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table)

        # Export to CSV Button
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        export_layout.addWidget(self.export_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        export_layout.addWidget(self.close_button)

        layout.addLayout(export_layout)

        self.setLayout(layout)

    def load_report(self):
        """Fetch payroll report and display it in the table."""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        department_id = self.department_input.currentData()

        report_data = self.database.generate_payroll_report(from_date, to_date, department_id)

        self.report_table.setRowCount(0)
        
        if not report_data:
            QMessageBox.information(self, "No Data", "No payroll data found for the selected period.")
            return

        for row_data in report_data:
            row_position = self.report_table.rowCount()
            self.report_table.insertRow(row_position)

            self.report_table.setItem(row_position, 0, QTableWidgetItem(row_data["department"]))
            self.report_table.setItem(row_position, 1, QTableWidgetItem(str(row_data["payroll_count"])))
            self.report_table.setItem(row_position, 2, QTableWidgetItem(str(row_data["employee_count"])))
            self.report_table.setItem(row_position, 3, QTableWidgetItem(f"${row_data['total_base_salary']:.2f}"))
            self.report_table.setItem(row_position, 4, QTableWidgetItem(f"${row_data['total_bonuses']:.2f}"))
            self.report_table.setItem(row_position, 5, QTableWidgetItem(f"${row_data['total_deductions']:.2f}"))
            self.report_table.setItem(row_position, 6, QTableWidgetItem(f"${row_data['total_net_salary']:.2f}"))

    def export_to_csv(self):
        """Export payroll report to a CSV file."""
        csv_file, _ = QFileDialog.getSaveFileName(self, "Export Payroll Report", "", "CSV Files (*.csv)")
        if csv_file:
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Department", "Payroll Count", "Employees Paid", 
                                 "Total Salary", "Total Bonuses", "Total Deductions", "Net Salary"])

                for row in range(self.report_table.rowCount()):
                    row_data = [
                        self.report_table.item(row, col).text() if self.report_table.item(row, col) else ""
                        for col in range(self.report_table.columnCount())
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export Successful", "Payroll report exported successfully!")

class RecordAttendanceDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Record Attendance")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # ✅ Employee Selection (Allow Typing & Choosing)
        self.employee_combo = QComboBox()
        self.employee_combo.setEditable(True)
        form_layout.addRow("Employee:", self.employee_combo)

        # ✅ Load Employees
        self.load_employees()

        # ✅ Attendance Date
        self.attendance_date = QDateEdit()
        self.attendance_date.setDisplayFormat("yyyy-MM-dd")
        self.attendance_date.setCalendarPopup(True)
        self.attendance_date.setDate(QDate.currentDate())  # Default: Today
        form_layout.addRow("Date:", self.attendance_date)

        # ✅ Status Selection
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Present", "Absent", "Sick", "Leave"])
        form_layout.addRow("Status:", self.status_combo)

        # ✅ Notes (Optional)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        form_layout.addRow("Notes (Optional):", self.notes_input)

        layout.addLayout(form_layout)

        # ✅ Save & Cancel Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_attendance)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_employees(self):
        """Loads employees into the combo box with autocomplete."""
        self.employee_combo.clear()
        self.employee_data = {}  # ✅ Store employee info in a dictionary
        employees = self.database.get_employees(status="Active")

        if not employees:
            self.employee_combo.addItem("No employees found", None)
            return

        employee_names = []
        for employee in employees:
            name = f"{employee['first_name']} {employee['last_name']} ({employee['employee_id']})"
            self.employee_combo.addItem(name, employee['id'])  # Store employee ID
            self.employee_data[name] = employee['id']  # ✅ Store for lookup
            employee_names.append(name)

        # ✅ Enable auto-completion when typing employee names
        completer = QCompleter(employee_names, self.employee_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.employee_combo.setCompleter(completer)

    def save_attendance(self):
        """Saves attendance to the database."""
        employee_name = self.employee_combo.currentText().strip()
        attendance_date = self.attendance_date.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()
        notes = self.notes_input.toPlainText()

        if employee_name not in self.employee_data:
            QMessageBox.warning(self, "Error", "Please select a valid employee.")
            return

        employee_id = self.employee_data[employee_name]

        attendance_data = {
            "employee_id": employee_id,
            "date": attendance_date,
            "status": status,
            "notes": notes,
        }

        try:
            self.database.add_attendance(attendance_data)
            QMessageBox.information(self, "Success", "Attendance recorded successfully!")
            self.accept()  # ✅ Close the dialog on success
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to record attendance: {str(e)}")

class ViewAttendanceRecordsDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("View Attendance Records")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # ✅ Filter Section
        filter_layout = QHBoxLayout()

        # 🔹 Employee Filter (Allow Typing)
        filter_layout.addWidget(QLabel("Employee:"))
        self.employee_combo = QComboBox()
        self.employee_combo.setEditable(True)
        self.load_employees()
        filter_layout.addWidget(self.employee_combo)

        # 🔹 Date Range Filters
        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # Default: Last month
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())  # Default: Today
        filter_layout.addWidget(self.to_date)

        # 🔹 Status Filter
        filter_layout.addWidget(QLabel("Status:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("All")
        self.status_combo.addItems(["Present", "Absent", "Sick", "Leave"])
        filter_layout.addWidget(self.status_combo)

        # 🔹 Search Button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.load_attendance_records)
        filter_layout.addWidget(self.search_button)

        layout.addLayout(filter_layout)

        # ✅ Attendance Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels(["Employee", "Date", "Status", "Notes", "Actions"])
        self.attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.attendance_table)

        # ✅ Close Button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

    def load_employees(self):
        """Loads employees into the combo box with autocomplete."""
        self.employee_combo.clear()
        self.employee_combo.addItem("All Employees", None)
        self.employee_data = {}  # ✅ Store employee info in a dictionary
        employees = self.database.get_employees(status="Active")

        if not employees:
            self.employee_combo.addItem("No employees found", None)
            return

        employee_names = []
        for employee in employees:
            name = f"{employee['first_name']} {employee['last_name']} ({employee['employee_id']})"
            self.employee_combo.addItem(name, employee['id'])  # Store employee ID
            self.employee_data[name] = employee['id']  # ✅ Store for lookup
            employee_names.append(name)

        # ✅ Enable auto-completion when typing employee names
        completer = QCompleter(employee_names, self.employee_combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.employee_combo.setCompleter(completer)

    def load_attendance_records(self):
        """Loads attendance records based on filters."""
        employee_name = self.employee_combo.currentText().strip()
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        employee_id = self.employee_data.get(employee_name) if employee_name in self.employee_data else None
        if employee_name == "All Employees":
            employee_id = None

        attendance_records = self.database.get_attendance(employee_id, from_date, to_date)

        self.attendance_table.setRowCount(0)

        for record in attendance_records:
            if status != "All" and record["status"] != status:
                continue  # ✅ Apply status filter

            row_position = self.attendance_table.rowCount()
            self.attendance_table.insertRow(row_position)

            self.attendance_table.setItem(row_position, 0, QTableWidgetItem(f"{record['first_name']} {record['last_name']}"))
            self.attendance_table.setItem(row_position, 1, QTableWidgetItem(record["date"]))
            self.attendance_table.setItem(row_position, 2, QTableWidgetItem(record["status"]))
            self.attendance_table.setItem(row_position, 3, QTableWidgetItem(record["notes"] or ""))

            # ✅ Actions: Edit & Delete Buttons
            actions_layout = QHBoxLayout()
            edit_button = QPushButton("Edit")
            edit_button.setFixedWidth(60)
            edit_button.clicked.connect(lambda _, rid=record["id"]: self.edit_attendance(rid))

            delete_button = QPushButton("Delete")
            delete_button.setFixedWidth(60)
            delete_button.clicked.connect(lambda _, rid=record["id"]: self.delete_attendance(rid))

            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.attendance_table.setCellWidget(row_position, 4, actions_widget)

    def edit_attendance(self, record_id):
        """Allows editing an attendance record."""
        attendance_records = self.database.get_attendance(record_id=record_id)
    
        if not attendance_records:
            QMessageBox.warning(self, "Error", "Attendance record not found!")
            return
    
        attendance = attendance_records[0]  # ✅ Get the first record
    
        dialog = RecordAttendanceDialog(self.database, self)
        dialog.setWindowTitle("Edit Attendance Record")
        dialog.employee_combo.setCurrentText(f"{attendance['first_name']} {attendance['last_name']} ({attendance['emp_id']})")
        dialog.attendance_date.setDate(QDate.fromString(attendance["date"], "yyyy-MM-dd"))
        dialog.status_combo.setCurrentText(attendance["status"])
        dialog.notes_input.setPlainText(attendance["notes"] or "")
    
        if dialog.exec_():  # If user clicks Save
            self.load_attendance_records()  # ✅ Refresh table


    def delete_attendance(self, record_id):
        """Deletes an attendance record after confirmation."""
        reply = QMessageBox.question(self, "Delete Attendance",
                                     "Are you sure you want to delete this attendance record?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = self.database.get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM attendance WHERE id = ?", (record_id,))
                conn.commit()
                QMessageBox.information(self, "Success", "Attendance record deleted successfully!")
                self.load_attendance_records()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete attendance record: {str(e)}")
            finally:
                conn.close()

class RequestLeaveDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Request Leave")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Employee Selection
        self.employee_combo = QComboBox()
        employees = self.database.get_employees(status="Active")
        for emp in employees:
            self.employee_combo.addItem(f"{emp['first_name']} {emp['last_name']} ({emp['employee_id']})", emp['id'])
        form_layout.addRow("Employee:", self.employee_combo)

        # Leave Type Selection
        self.leave_type_combo = QComboBox()
        self.leave_type_combo.addItems(["Vacation", "Sick Leave", "Unpaid Leave", "Maternity Leave", "Other"])
        form_layout.addRow("Leave Type:", self.leave_type_combo)

        # Start Date
        self.start_date = QDateEdit()
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        form_layout.addRow("Start Date:", self.start_date)

        # End Date
        self.end_date = QDateEdit()
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addDays(5))
        form_layout.addRow("End Date:", self.end_date)

        # Leave Reason
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Enter reason for leave (optional)")
        form_layout.addRow("Reason:", self.reason_input)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.submit_button = QPushButton("Submit Request")
        self.submit_button.clicked.connect(self.submit_request)
        button_layout.addWidget(self.submit_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def submit_request(self):
        """Submits the leave request to the database."""
        employee_id = self.employee_combo.currentData()
        leave_type = self.leave_type_combo.currentText()
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        reason = self.reason_input.toPlainText()

        if self.start_date.date() > self.end_date.date():
            QMessageBox.warning(self, "Error", "Start date cannot be after end date.")
            return

        leave_data = {
            "employee_id": employee_id,
            "leave_type": leave_type,
            "start_date": start_date,
            "end_date": end_date,
            "reason": reason,
            "status": "Pending"
        }

        leave_id = self.database.add_leave_request(leave_data)

        if leave_id:
            QMessageBox.information(self, "Success", "Leave request submitted successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to submit leave request.")

class ApproveLeaveDialog(QDialog):
    def __init__(self, database, user, parent=None):
        super().__init__(parent)
        self.database = database
        self.user = user  # Admin user approving the leave
        self.setWindowTitle("Approve Leave Requests")
        self.setMinimumWidth(700)

        layout = QVBoxLayout()

        # Table to display leave requests
        self.leave_table = QTableWidget()
        self.leave_table.setColumnCount(6)
        self.leave_table.setHorizontalHeaderLabels(["Employee", "Type", "Start Date", "End Date", "Status", "Actions"])
        self.leave_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.leave_table)

        self.load_leave_requests()

        # Buttons
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_leave_requests)
        button_layout.addWidget(self.refresh_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_leave_requests(self):
        """Loads leave requests into the table."""
        self.leave_table.setRowCount(0)
        leave_requests = self.database.get_leave_requests(status="Pending")

        if not leave_requests:
            QMessageBox.information(self, "No Requests", "No pending leave requests found.")
            return

        for request in leave_requests:
            row_position = self.leave_table.rowCount()
            self.leave_table.insertRow(row_position)

            self.leave_table.setItem(row_position, 0, QTableWidgetItem(f"{request['first_name']} {request['last_name']}"))
            self.leave_table.setItem(row_position, 1, QTableWidgetItem(request["leave_type"]))
            self.leave_table.setItem(row_position, 2, QTableWidgetItem(request["start_date"]))
            self.leave_table.setItem(row_position, 3, QTableWidgetItem(request["end_date"]))
            self.leave_table.setItem(row_position, 4, QTableWidgetItem(request["status"]))

            # Create Approve & Reject buttons
            actions_layout = QHBoxLayout()
            approve_button = QPushButton("Approve")
            approve_button.setFixedWidth(80)
            approve_button.clicked.connect(lambda _, rid=request["id"]: self.update_leave_status(rid, "Approved"))

            reject_button = QPushButton("Reject")
            reject_button.setFixedWidth(80)
            reject_button.clicked.connect(lambda _, rid=request["id"]: self.update_leave_status(rid, "Rejected"))

            actions_layout.addWidget(approve_button)
            actions_layout.addWidget(reject_button)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)

            self.leave_table.setCellWidget(row_position, 5, actions_widget)

    def update_leave_status(self, leave_id, status):
        """Updates leave request status."""
        self.database.update_leave_status(leave_id, status, approved_by=self.user["id"])
        QMessageBox.information(self, "Success", f"Leave request {status}.")
        self.load_leave_requests()  # Refresh the table

class EmployeeReportDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Employee Report")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # Search and filter controls
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search employees by name or ID...")
        self.search_input.textChanged.connect(self.load_report)
        filter_layout.addWidget(self.search_input)

        filter_layout.addWidget(QLabel("Department:"))
        self.department_filter = QComboBox()
        self.department_filter.addItem("All Departments", None)
        departments = self.database.get_departments()
        for dept in departments:
            self.department_filter.addItem(dept["name"], dept["id"])
        self.department_filter.currentIndexChanged.connect(self.load_report)
        filter_layout.addWidget(self.department_filter)

        filter_layout.addWidget(QLabel("Status:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "On Leave", "Terminated"])
        self.status_filter.currentTextChanged.connect(self.load_report)
        filter_layout.addWidget(self.status_filter)

        layout.addLayout(filter_layout)

        # Table to display employee data
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Department", "Position", "Salary", "Status"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table)

        # Export and Close Buttons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Load employee data initially
        self.load_report()

    def load_report(self):
        """Fetch employee data and display it in the table."""
        search_text = self.search_input.text() if self.search_input.text() else None
        department_id = self.department_filter.currentData()
        status = self.status_filter.currentText() if self.status_filter.currentText() != "All" else None

        employees = self.database.get_employees(search_text, department_id, status)

        self.report_table.setRowCount(0)

        if not employees:
            QMessageBox.information(self, "No Data", "No employees found matching the criteria.")
            return

        for employee in employees:
            row_position = self.report_table.rowCount()
            self.report_table.insertRow(row_position)

            self.report_table.setItem(row_position, 0, QTableWidgetItem(employee["employee_id"]))
            self.report_table.setItem(row_position, 1, QTableWidgetItem(f"{employee['first_name']} {employee['last_name']}"))
            self.report_table.setItem(row_position, 2, QTableWidgetItem(employee["department_name"] or ""))
            self.report_table.setItem(row_position, 3, QTableWidgetItem(employee["position_title"] or ""))
            
            salary_item = QTableWidgetItem(f"${employee['base_salary']:.2f}")
            salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(row_position, 4, salary_item)

            self.report_table.setItem(row_position, 5, QTableWidgetItem(employee["status"]))

    def export_to_csv(self):
        """Exports the employee report to a CSV file."""
        csv_file, _ = QFileDialog.getSaveFileName(self, "Export Employee Report", "", "CSV Files (*.csv)")
        if csv_file:
            with open(csv_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Employee ID", "Name", "Department", "Position", "Salary", "Status"])

                for row in range(self.report_table.rowCount()):
                    row_data = [
                        self.report_table.item(row, col).text() if self.report_table.item(row, col) else ""
                        for col in range(self.report_table.columnCount())
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export Successful", "Employee report exported successfully!")

class DepartmentReportDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Department Report")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # Table to display department statistics
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4)
        self.report_table.setHorizontalHeaderLabels(["Department", "Total Employees", "Avg. Salary", "Total Payroll"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table)

        # Export and Close Buttons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Load department data initially
        self.load_report()

    def load_report(self):
        """Fetch department statistics and display in the table."""
        departments = self.database.get_department_statistics()

        self.report_table.setRowCount(0)

        if not departments:
            QMessageBox.information(self, "No Data", "No department statistics available.")
            return

        for dept in departments:
            row_position = self.report_table.rowCount()
            self.report_table.insertRow(row_position)

            self.report_table.setItem(row_position, 0, QTableWidgetItem(dept["department"]))
            self.report_table.setItem(row_position, 1, QTableWidgetItem(str(dept["total_employees"])))

            avg_salary_item = QTableWidgetItem(f"${dept['average_salary']:.2f}")
            avg_salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(row_position, 2, avg_salary_item)

            total_payroll_item = QTableWidgetItem(f"${dept['total_payroll']:.2f}")
            total_payroll_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.report_table.setItem(row_position, 3, total_payroll_item)

    def export_to_csv(self):
        """Exports the department report to a CSV file."""
        csv_file, _ = QFileDialog.getSaveFileName(self, "Export Department Report", "", "CSV Files (*.csv)")
        if csv_file:
            with open(csv_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Department", "Total Employees", "Avg. Salary", "Total Payroll"])

                for row in range(self.report_table.rowCount()):
                    row_data = [
                        self.report_table.item(row, col).text() if self.report_table.item(row, col) else ""
                        for col in range(self.report_table.columnCount())
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export Successful", "Department report exported successfully!")

class AttendanceReportDialog(QDialog):
    def __init__(self, database, parent=None):
        super().__init__(parent)
        self.database = database
        self.setWindowTitle("Attendance Report")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)

        layout = QVBoxLayout()

        # Date Range Filters
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setDisplayFormat("yyyy-MM-dd")
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))  # Default: Last month
        filter_layout.addWidget(self.from_date)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setDisplayFormat("yyyy-MM-dd")
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())  # Default: Today
        filter_layout.addWidget(self.to_date)

        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.load_report)
        filter_layout.addWidget(self.generate_button)

        layout.addLayout(filter_layout)

        # Table to display attendance statistics
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["Employee", "Days Present", "Days Absent", "Days Late", "Leave Taken"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.report_table)

        # Export and Close Buttons
        button_layout = QHBoxLayout()

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_to_csv)
        button_layout.addWidget(self.export_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_report(self):
        """Fetch attendance statistics and display in the table."""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")

        attendance_data = self.database.get_attendance_statistics(from_date, to_date)

        self.report_table.setRowCount(0)

        if not attendance_data:
            QMessageBox.information(self, "No Data", "No attendance data found for the selected period.")
            return

        for record in attendance_data:
            row_position = self.report_table.rowCount()
            self.report_table.insertRow(row_position)

            self.report_table.setItem(row_position, 0, QTableWidgetItem(record["employee"]))
            self.report_table.setItem(row_position, 1, QTableWidgetItem(str(record["days_present"])))
            self.report_table.setItem(row_position, 2, QTableWidgetItem(str(record["days_absent"])))
            self.report_table.setItem(row_position, 3, QTableWidgetItem(str(record["days_late"])))
            self.report_table.setItem(row_position, 4, QTableWidgetItem(str(record["leave_taken"])))

    def export_to_csv(self):
        """Exports the attendance report to a CSV file."""
        csv_file, _ = QFileDialog.getSaveFileName(self, "Export Attendance Report", "", "CSV Files (*.csv)")
        if csv_file:
            with open(csv_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Employee", "Days Present", "Days Absent", "Days Late", "Leave Taken"])

                for row in range(self.report_table.rowCount()):
                    row_data = [
                        self.report_table.item(row, col).text() if self.report_table.item(row, col) else ""
                        for col in range(self.report_table.columnCount())
                    ]
                    writer.writerow(row_data)

            QMessageBox.information(self, "Export Successful", "Attendance report exported successfully!")

class MainWindow(QMainWindow):
    def __init__(self, database, user):
        super().__init__()
        self.database = database
        self.user = user

        self.setWindowTitle("Employee Accounting System")
        self.setGeometry(100, 100, 1200, 700)

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Logged in as: {self.user['username']} ({self.user['role']})")

        # Create central tab widget
        self.central_tabs = QTabWidget()

        # ✅ Define Employee Management Tab FIRST
        self.employee_tab = EmployeeManagementTab(self.database)
        self.central_tabs.addTab(self.employee_tab, "Employees")
        self.central_tabs.currentChanged.connect(self.on_tab_changed)

        # ✅ Define Payroll Tab
        self.payroll_tab = PayrollTab(self.database, self.user)
        self.central_tabs.addTab(self.payroll_tab, "Payroll")

        # ✅ Set central widget
        self.setCentralWidget(self.central_tabs)

        # ✅ Create menu bar AFTER defining tabs
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        backup_action = QAction("Backup Database", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        export_action = QAction("Export Employees to CSV", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_employees)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Employee menu
        employee_menu = menubar.addMenu("Employees")

        add_employee_action = QAction("Add New Employee", self)
        add_employee_action.triggered.connect(self.employee_tab.add_employee)
        employee_menu.addAction(add_employee_action)

        refresh_employees_action = QAction("Refresh Employee List", self)
        refresh_employees_action.triggered.connect(self.employee_tab.load_employees)
        employee_menu.addAction(refresh_employees_action)

        dept_pos_menu = employee_menu.addMenu("Departments & Positions")

        manage_departments_action = QAction("Manage Departments", self)
        manage_departments_action.triggered.connect(self.open_department_manager)
        dept_pos_menu.addAction(manage_departments_action)

        manage_positions_action = QAction("Manage Positions", self)
        manage_positions_action.triggered.connect(self.open_position_manager)
        dept_pos_menu.addAction(manage_positions_action)

        # Payroll menu
        payroll_menu = menubar.addMenu("Payroll")

        create_payroll_action = QAction("Create New Payroll", self)
        create_payroll_action.triggered.connect(lambda: self.central_tabs.setCurrentWidget(self.payroll_tab))
        payroll_menu.addAction(create_payroll_action)

        payroll_report_action = QAction("Generate Payroll Report", self)
        payroll_report_action.triggered.connect(self.generate_payroll_report)
        payroll_menu.addAction(payroll_report_action)


        # Attendance menu
        attendance_menu = menubar.addMenu("Attendance")

        record_attendance_action = QAction("Record Attendance", self)
        record_attendance_action.triggered.connect(self.open_attendance_recorder)
        attendance_menu.addAction(record_attendance_action)

        view_attendance_action = QAction("View Attendance Records", self)
        view_attendance_action.triggered.connect(self.open_attendance_viewer)
        attendance_menu.addAction(view_attendance_action)

        leaves_menu = attendance_menu.addMenu("Leave Management")

        request_leave_action = QAction("Request Leave", self)
        request_leave_action.triggered.connect(self.open_leave_request)
        leaves_menu.addAction(request_leave_action)

        approve_leave_action = QAction("Approve Leave Requests", self)
        approve_leave_action.triggered.connect(self.open_leave_approval)
        leaves_menu.addAction(approve_leave_action)

        # Reports menu
        reports_menu = menubar.addMenu("Reports")

        employee_report_action = QAction("Employee Report", self)
        employee_report_action.triggered.connect(self.generate_employee_report)
        reports_menu.addAction(employee_report_action)

        department_report_action = QAction("Department Report", self)
        department_report_action.triggered.connect(self.generate_department_report)
        reports_menu.addAction(department_report_action)


        attendance_report_action = QAction("Attendance Report", self)
        attendance_report_action.triggered.connect(self.generate_attendance_report)
        reports_menu.addAction(attendance_report_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def on_tab_changed(self, index):
        """Refresh payroll employee list when switching to Payroll Tab."""
        selected_tab = self.central_tabs.widget(index)
        if isinstance(selected_tab, PayrollTab):
            selected_tab.load_employees()  # ✅ Refresh Payroll Tab when opened


    def show_about_dialog(self):
        """Show the about dialog with additional details and styling."""
        about_text = """
        <h2 style="color: #2E86C1;">Employee Accounting System</h2>
        <p><strong>Version:</strong> 1.0.0</p>
        <p><strong>Description:</strong> A comprehensive system designed for managing employees, payroll, and attendance.</p>
        
        <h3>Features:</h3>
        <ul>
            <li>🔹 Employee Management</li>
            <li>🔹 Payroll Processing</li>
            <li>🔹 Attendance Tracking</li>
            <li>🔹 Leave Requests & Approvals</li>
            <li>🔹 Reporting & Analytics</li>
        </ul>
        
        <p>For any inquiries or support, please contact:</p>
        <p><strong>Email:</strong> support@employeeaccounting.com</p>
        <p><strong>Website:</strong> <a href="https://employeeaccounting.com">employeeaccounting.com</a></p>
        
        <p style="color: #2980B9;">© 2025 - Developed by <strong>Mohamed Hussien</strong></p>
        """
        QMessageBox.about(self, "About Employee Accounting System", about_text)

    def backup_database(self):
        backup_file, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Database (*.db)")
        if backup_file:
            if self.database.backup_database(backup_file):
                QMessageBox.information(self, "Backup Successful", "Database backup completed successfully.")
            else:
                QMessageBox.warning(self, "Backup Failed", "Failed to backup database.")

    def export_employees(self):
        csv_file, _ = QFileDialog.getSaveFileName(self, "Export Employees to CSV", "", "CSV Files (*.csv)")
        if csv_file:
            if self.database.export_employees_to_csv(csv_file):
                QMessageBox.information(self, "Export Successful", "Employees data exported successfully.")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export employees data.")

    def open_department_manager(self):
        """Opens the Manage Departments dialog."""
        dialog = ManageDepartmentsDialog(self.database, self)
        dialog.exec_()

    def open_position_manager(self):
        """Opens the Manage Positions dialog."""
        dialog = ManagePositionsDialog(self.database, self)
        dialog.exec_()

    def generate_payroll_report(self):
        """Opens the Payroll Report Dialog"""
        dialog = PayrollReportDialog(self.database, self)
        dialog.exec_()

    def open_attendance_recorder(self):
        """Opens the attendance recording dialog."""
        dialog = RecordAttendanceDialog(self.database, self)
        dialog.exec_()  # Show the dialog

    def open_attendance_viewer(self):
        """Opens the attendance records viewer dialog."""
        dialog = ViewAttendanceRecordsDialog(self.database, self)
        dialog.exec_()

    def open_leave_request(self):
        """Opens the Request Leave Dialog."""
        dialog = RequestLeaveDialog(self.database, self)
        if dialog.exec_():
            QMessageBox.information(self, "Leave Request", "Your leave request has been submitted.")

    def open_leave_approval(self):
        """Opens the Approve Leave Requests Dialog."""
        dialog = ApproveLeaveDialog(self.database, self.user, self)
        dialog.exec_()

    def generate_employee_report(self):
        """Opens the Employee Report Dialog."""
        dialog = EmployeeReportDialog(self.database, self)
        dialog.exec_()

    def generate_department_report(self):
        """Opens the Department Report Dialog."""
        dialog = DepartmentReportDialog(self.database, self)
        dialog.exec_()

    def generate_attendance_report(self):
        """Opens the Attendance Report Dialog."""
        dialog = AttendanceReportDialog(self.database, self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    database = Database()

    login_dialog = LoginDialog(database)
    if login_dialog.exec_() == QDialog.Accepted:
        user = login_dialog.user
        main_window = MainWindow(database, user)
        main_window.show()
        sys.exit(app.exec_())
