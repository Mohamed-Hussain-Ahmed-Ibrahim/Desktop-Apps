import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTabWidget, QTableWidget, 
                             QTableWidgetItem, QMessageBox, QFormLayout, QComboBox, 
                             QDateEdit, QDialog, QGroupBox, QHeaderView, QAbstractItemView,
                             QStatusBar)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor

class DatabaseManager:
    """Database management class to handle all database operations"""  
    def __init__(self, db_name="school.db"):
        # Create database file in the current directory
        self.conn = None
        self.cursor = None
        self.db_name = db_name
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Users table for login
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL
                )
            ''')
            
            # Students table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    enrollment_date TEXT,
                    class_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes (id)
                )
            ''')
            
            # Teachers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    address TEXT,
                    hire_date TEXT,
                    subject TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Classes table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL,
                    grade TEXT NOT NULL,
                    room_number TEXT,
                    teacher_id INTEGER,
                    schedule TEXT,
                    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
                )
            ''')
            
            # Insert admin user if not exists
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            if self.cursor.fetchone()[0] == 0:
                self.cursor.execute('''
                    INSERT INTO users (username, password, role)
                    VALUES ('admin', 'admin123', 'admin')
                ''')
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Table creation error: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    def validate_login(self, username, password):
        """Validate user login credentials"""
        try:
            self.cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", 
                             (username, password))
            user = self.cursor.fetchone()
            if user:
                return True, user[0], user[1]  # Success, user_id, role
            return False, None, None
        except sqlite3.Error as e:
            print(f"Login validation error: {e}")
            return False, None, None
    
    # Students CRUD operations
    def add_student(self, student_data):
        """Add a new student to the database"""
        try:
            self.cursor.execute('''
                INSERT INTO students (first_name, last_name, gender, date_of_birth, 
                                    email, phone, address, enrollment_date, class_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', student_data)
            self.conn.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding student: {e}")
            return False, None
    
    def get_all_students(self):
        """Get all students with their class information"""
        try:
            self.cursor.execute('''
                SELECT s.id, s.first_name, s.last_name, s.gender, s.date_of_birth, 
                       s.email, s.phone, s.class_id, c.class_name 
                FROM students s
                LEFT JOIN classes c ON s.class_id = c.id
                ORDER BY s.id
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching students: {e}")
            return []
    
    def get_student(self, student_id):
        """Get a specific student by ID"""
        try:
            self.cursor.execute('''
                SELECT * FROM students WHERE id = ?
            ''', (student_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching student: {e}")
            return None
    
    def update_student(self, student_id, student_data):
        """Update an existing student"""
        try:
            self.cursor.execute('''
                UPDATE students
                SET first_name = ?, last_name = ?, gender = ?, date_of_birth = ?,
                    email = ?, phone = ?, address = ?, enrollment_date = ?, class_id = ?
                WHERE id = ?
            ''', student_data + (student_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating student: {e}")
            return False
    
    def delete_student(self, student_id):
        """Delete a student by ID"""
        try:
            self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting student: {e}")
            return False
    
    # Teachers CRUD operations
    def add_teacher(self, teacher_data, username, password):
        """Add a new teacher with user credentials"""
        try:
            # Begin transaction
            self.conn.execute("BEGIN")
            
            # Add user first
            self.cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, 'teacher')
            ''', (username, password))
            user_id = self.cursor.lastrowid
            
            # Add teacher with user_id
            self.cursor.execute('''
                INSERT INTO teachers (first_name, last_name, gender, date_of_birth, 
                                    email, phone, address, hire_date, subject, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', teacher_data + (user_id,))
            
            self.conn.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error adding teacher: {e}")
            return False, None
    
    def get_all_teachers(self):
        """Get all teachers"""
        try:
            self.cursor.execute('''
                SELECT t.id, t.first_name, t.last_name, t.gender, t.email, 
                       t.phone, t.subject, u.username
                FROM teachers t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.id
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching teachers: {e}")
            return []
    
    def get_teacher(self, teacher_id):
        """Get a specific teacher by ID"""
        try:
            self.cursor.execute('''
                SELECT t.*, u.username 
                FROM teachers t
                JOIN users u ON t.user_id = u.id
                WHERE t.id = ?
            ''', (teacher_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching teacher: {e}")
            return None
    
    def get_teacher_by_user_id(self, user_id):
        """Get teacher information based on user_id"""
        try:
            self.cursor.execute("SELECT * FROM teachers WHERE user_id = ?", (user_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching teacher by user ID: {e}")
            return None
    
    def update_teacher(self, teacher_id, teacher_data, username=None, password=None):
        """Update an existing teacher and optionally their login credentials"""
        try:
            # Begin transaction
            self.conn.execute("BEGIN")
            
            # Update teacher data
            self.cursor.execute('''
                UPDATE teachers
                SET first_name = ?, last_name = ?, gender = ?, date_of_birth = ?,
                    email = ?, phone = ?, address = ?, hire_date = ?, subject = ?
                WHERE id = ?
            ''', teacher_data + (teacher_id,))
            
            # If username or password is provided, update the user record
            if username or password:
                # Get user_id for this teacher
                self.cursor.execute("SELECT user_id FROM teachers WHERE id = ?", (teacher_id,))
                user_id = self.cursor.fetchone()[0]
                
                if username and password:
                    self.cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", 
                                     (username, password, user_id))
                elif username:
                    self.cursor.execute("UPDATE users SET username = ? WHERE id = ?", 
                                     (username, user_id))
                elif password:
                    self.cursor.execute("UPDATE users SET password = ? WHERE id = ?", 
                                     (password, user_id))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error updating teacher: {e}")
            return False
    
    def delete_teacher(self, teacher_id):
        """Delete a teacher and their user account by ID"""
        try:
            # Begin transaction
            self.conn.execute("BEGIN")
            
            # Get user_id for this teacher
            self.cursor.execute("SELECT user_id FROM teachers WHERE id = ?", (teacher_id,))
            result = self.cursor.fetchone()
            if result:
                user_id = result[0]
                
                # Delete teacher
                self.cursor.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
                
                # Delete user
                self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                
                # Update classes that had this teacher
                self.cursor.execute("UPDATE classes SET teacher_id = NULL WHERE teacher_id = ?", 
                                 (teacher_id,))
                
                self.conn.commit()
                return True
            else:
                self.conn.rollback()
                return False
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting teacher: {e}")
            return False
    
    # Classes CRUD operations
    def add_class(self, class_data):
        """Add a new class"""
        try:
            self.cursor.execute('''
                INSERT INTO classes (class_name, grade, room_number, teacher_id, schedule)
                VALUES (?, ?, ?, ?, ?)
            ''', class_data)
            self.conn.commit()
            return True, self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding class: {e}")
            return False, None
    
    def get_all_classes(self):
        """Get all classes with teacher information"""
        try:
            self.cursor.execute('''
                SELECT c.id, c.class_name, c.grade, c.room_number, c.schedule,
                       t.id as teacher_id, t.first_name, t.last_name
                FROM classes c
                LEFT JOIN teachers t ON c.teacher_id = t.id
                ORDER BY c.id
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching classes: {e}")
            return []
    
    def get_class(self, class_id):
        """Get a specific class by ID"""
        try:
            self.cursor.execute("SELECT * FROM classes WHERE id = ?", (class_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error fetching class: {e}")
            return None
    
    def get_classes_by_teacher(self, teacher_id):
        """Get all classes assigned to a specific teacher"""
        try:
            self.cursor.execute('''
                SELECT * FROM classes
                WHERE teacher_id = ?
            ''', (teacher_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching teacher's classes: {e}")
            return []
    
    def update_class(self, class_id, class_data):
        """Update an existing class"""
        try:
            self.cursor.execute('''
                UPDATE classes
                SET class_name = ?, grade = ?, room_number = ?, teacher_id = ?, schedule = ?
                WHERE id = ?
            ''', class_data + (class_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating class: {e}")
            return False
    
    def delete_class(self, class_id):
        """Delete a class by ID"""
        try:
            # Begin transaction
            self.conn.execute("BEGIN")
            
            # Update students that were in this class
            self.cursor.execute("UPDATE students SET class_id = NULL WHERE class_id = ?", (class_id,))
            
            # Delete class
            self.cursor.execute("DELETE FROM classes WHERE id = ?", (class_id,))
            
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error deleting class: {e}")
            return False
    
    def get_class_options(self):
        """Get all classes for dropdown options"""
        try:
            self.cursor.execute("SELECT id, class_name FROM classes ORDER BY class_name")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching class options: {e}")
            return []
    
    def get_teacher_options(self):
        """Get all teachers for dropdown options"""
        try:
            self.cursor.execute('''
                SELECT id, first_name || ' ' || last_name as full_name 
                FROM teachers 
                ORDER BY last_name, first_name
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching teacher options: {e}")
            return []


    def get_students_in_class(self, class_id):
        """Get all students in a specific class"""
        try:
            self.cursor.execute('''
                SELECT id, first_name, last_name, gender, email
                FROM students
                WHERE class_id = ?
                ORDER BY last_name, first_name
            ''', (class_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error fetching students in class: {e}")
            return []


class LoginWindow(QWidget):
    """Login window for the school management system"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.initUI()
    
    def initUI(self):
        """Initialize the login UI"""
        self.setWindowTitle("School Management System - Login")
        self.setFixedSize(450, 300)
        
        main_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("School Management System")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(20)
        
        # Login form
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        main_layout.addLayout(form_layout)
        
        main_layout.addSpacing(20)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        # Version info
        version_label = QLabel("Version 1.0")
        version_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(version_label)
        
        self.setLayout(main_layout)
    
    def login(self):
        """Handle login button click"""
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            self.status_label.setStyleSheet("color: red")
            return
        
        success, user_id, role = self.db_manager.validate_login(username, password)
        
        if success:
            self.status_label.setText("Login successful!")
            self.status_label.setStyleSheet("color: green")
            self.user_id = user_id
            self.role = role
            self.accept()
        else:
            self.status_label.setText("Invalid username or password")
            self.status_label.setStyleSheet("color: red")
    
    def accept(self):
        """Override accept method to emit a custom signal"""
        self.hide()
        # Create and show the main window
        if self.role == 'admin':
            self.main_window = AdminDashboard(self.db_manager)
        else:  # teacher
            teacher_info = self.db_manager.get_teacher_by_user_id(self.user_id)
            self.main_window = TeacherDashboard(self.db_manager, teacher_info)
        
        self.main_window.show()
        self.main_window.show()
        self.close()  # Hide the login window after opening the main window

class AdminDashboard(QMainWindow):
    """Main window for admin users"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.initUI()
        self.closed = False
    
    def initUI(self):
        """Initialize the admin dashboard UI"""
        self.setWindowTitle("School Management System - Admin Dashboard")
        self.setMinimumSize(1000, 600)
    
        # 🌟 Initialize status bar BEFORE calling setup functions
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
    
        # Create header
        header_layout = QHBoxLayout()
        header_label = QLabel("School Management System - Admin Dashboard")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
    
        # Add logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
    
        main_layout.addLayout(header_layout)
    
        # Create tab widget
        self.tab_widget = QTabWidget()
    
        # Create tabs
        self.dashboard_tab = QWidget()
        self.students_tab = QWidget()
        self.teachers_tab = QWidget()
        self.classes_tab = QWidget()
    
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.students_tab, "Students")
        self.tab_widget.addTab(self.teachers_tab, "Teachers")
        self.tab_widget.addTab(self.classes_tab, "Classes")
    
        main_layout.addWidget(self.tab_widget)
    
        # 🌟 Setup UI **after** status bar initialization
        self.setup_dashboard_tab()
        self.setup_students_tab()
        self.setup_teachers_tab()
        self.setup_classes_tab()
    
        # Set central widget
        self.setCentralWidget(central_widget)
    
        # Show initial status bar message
        self.status_bar.showMessage("Ready")
    
    def setup_dashboard_tab(self):
        """Setup the dashboard tab content"""
        layout = QVBoxLayout()
        
        # Stats section
        stats_layout = QHBoxLayout()
        
        # Student stats
        student_stats = QGroupBox("Students")
        student_stats_layout = QVBoxLayout()
        self.student_count_label = QLabel("Total Students: Loading...")
        student_stats_layout.addWidget(self.student_count_label)
        student_stats.setLayout(student_stats_layout)
        stats_layout.addWidget(student_stats)
        
        # Teacher stats
        teacher_stats = QGroupBox("Teachers")
        teacher_stats_layout = QVBoxLayout()
        self.teacher_count_label = QLabel("Total Teachers: Loading...")
        teacher_stats_layout.addWidget(self.teacher_count_label)
        teacher_stats.setLayout(teacher_stats_layout)
        stats_layout.addWidget(teacher_stats)
        
        # Class stats
        class_stats = QGroupBox("Classes")
        class_stats_layout = QVBoxLayout()
        self.class_count_label = QLabel("Total Classes: Loading...")
        class_stats_layout.addWidget(self.class_count_label)
        class_stats.setLayout(class_stats_layout)
        stats_layout.addWidget(class_stats)
        
        layout.addLayout(stats_layout)
        
        # Recent data section
        recent_layout = QHBoxLayout()
        
        # Recent students
        recent_students = QGroupBox("Recent Students")
        recent_students_layout = QVBoxLayout()
        self.recent_students_table = QTableWidget()
        self.recent_students_table.setColumnCount(3)
        self.recent_students_table.setHorizontalHeaderLabels(["ID", "Name", "Class"])
        self.recent_students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_students_layout.addWidget(self.recent_students_table)
        recent_students.setLayout(recent_students_layout)
        recent_layout.addWidget(recent_students)
        
        # Recent classes
        recent_classes = QGroupBox("Recent Classes")
        recent_classes_layout = QVBoxLayout()
        self.recent_classes_table = QTableWidget()
        self.recent_classes_table.setColumnCount(3)
        self.recent_classes_table.setHorizontalHeaderLabels(["ID", "Class Name", "Teacher"])
        self.recent_classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        recent_classes_layout.addWidget(self.recent_classes_table)
        recent_classes.setLayout(recent_classes_layout)
        recent_layout.addWidget(recent_classes)
        
        layout.addLayout(recent_layout)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Dashboard")
        refresh_button.clicked.connect(self.refresh_dashboard)
        layout.addWidget(refresh_button)
        
        self.dashboard_tab.setLayout(layout)
        
        # Load initial data
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Update stats
        students = self.db_manager.get_all_students()
        teachers = self.db_manager.get_all_teachers()
        classes = self.db_manager.get_all_classes()
        
        self.student_count_label.setText(f"Total Students: {len(students)}")
        self.teacher_count_label.setText(f"Total Teachers: {len(teachers)}")
        self.class_count_label.setText(f"Total Classes: {len(classes)}")
        
        # Update recent students table
        self.recent_students_table.setRowCount(min(5, len(students)))
        for i, student in enumerate(students[:5]):
            student_id = QTableWidgetItem(str(student[0]))
            student_name = QTableWidgetItem(f"{student[1]} {student[2]}")
            student_class = QTableWidgetItem(student[8] if student[8] else "Not Assigned")
            
            self.recent_students_table.setItem(i, 0, student_id)
            self.recent_students_table.setItem(i, 1, student_name)
            self.recent_students_table.setItem(i, 2, student_class)
        
        # Update recent classes table
        self.recent_classes_table.setRowCount(min(5, len(classes)))
        for i, cls in enumerate(classes[:5]):
            class_id = QTableWidgetItem(str(cls[0]))
            class_name = QTableWidgetItem(cls[1])
            teacher_name = QTableWidgetItem(f"{cls[6]} {cls[7]}" if cls[6] and cls[7] else "Not Assigned")
            
            self.recent_classes_table.setItem(i, 0, class_id)
            self.recent_classes_table.setItem(i, 1, class_name)
            self.recent_classes_table.setItem(i, 2, teacher_name)
        
        self.statusBar().showMessage("Dashboard refreshed", 3000)
    
    def setup_students_tab(self):
        """Setup the students tab content"""
        layout = QVBoxLayout()
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Gender", "Email", "Phone", "Class"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.students_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.students_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.add_student_button = QPushButton("Add Student")
        self.add_student_button.clicked.connect(self.add_student)
        buttons_layout.addWidget(self.add_student_button)
        
        self.edit_student_button = QPushButton("Edit Student")
        self.edit_student_button.clicked.connect(self.edit_student)
        buttons_layout.addWidget(self.edit_student_button)
        
        self.delete_student_button = QPushButton("Delete Student")
        self.delete_student_button.clicked.connect(self.delete_student)
        buttons_layout.addWidget(self.delete_student_button)
        
        self.refresh_students_button = QPushButton("Refresh")
        self.refresh_students_button.clicked.connect(self.load_students)
        buttons_layout.addWidget(self.refresh_students_button)
        
        layout.addLayout(buttons_layout)
        
        self.students_tab.setLayout(layout)
        
        # Load initial data
        self.load_students()
    
    def load_students(self):
        """Load students data into the table"""
        students = self.db_manager.get_all_students()
        
        self.students_table.setRowCount(len(students))
        for i, student in enumerate(students):
            student_id = QTableWidgetItem(str(student[0]))
            first_name = QTableWidgetItem(student[1])
            last_name = QTableWidgetItem(student[2])
            gender = QTableWidgetItem(student[3])
            email = QTableWidgetItem(student[5])
            phone = QTableWidgetItem(student[6])
            class_name = QTableWidgetItem(student[8] if student[8] else "Not Assigned")
            
            self.students_table.setItem(i, 0, student_id)
            self.students_table.setItem(i, 1, first_name)
            self.students_table.setItem(i, 2, last_name)
            self.students_table.setItem(i, 3, gender)
            self.students_table.setItem(i, 4, email)
            self.students_table.setItem(i, 5, phone)
            self.students_table.setItem(i, 6, class_name)
        
        self.statusBar().showMessage("Students loaded", 3000)
    
    def add_student(self):
        """Open dialog to add a new student"""
        dialog = StudentDialog(self.db_manager)
        if dialog.exec_():
            self.load_students()
            self.refresh_dashboard()
            self.status_bar.showMessage("Student added successfully", 3000)
    
    def edit_student(self):
        """Open dialog to edit selected student"""
        selected_rows = self.students_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a student to edit")
            return
        
        student_id = int(self.students_table.item(selected_rows[0].row(), 0).text())
        
        dialog = StudentDialog(self.db_manager, student_id)
        if dialog.exec_():
            self.load_students()
            self.refresh_dashboard()
            self.status_bar.showMessage("Student updated successfully", 3000)
    
    def delete_student(self):
        """Delete selected student"""
        selected_rows = self.students_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a student to delete")
            return
        
        student_id = int(self.students_table.item(selected_rows[0].row(), 0).text())
        student_name = f"{self.students_table.item(selected_rows[0].row(), 1).text()} {self.students_table.item(selected_rows[0].row(), 2).text()}"
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete student: {student_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_student(student_id):
                self.load_students()
                self.refresh_dashboard()
                self.status_bar.showMessage("Student deleted successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete student")
    
    def setup_teachers_tab(self):
        """Setup the teachers tab content"""
        layout = QVBoxLayout()
        
        # Teachers table
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(7)
        self.teachers_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Gender", "Email", "Phone", "Subject"])
        self.teachers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachers_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.teachers_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.teachers_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.add_teacher_button = QPushButton("Add Teacher")
        self.add_teacher_button.clicked.connect(self.add_teacher)
        buttons_layout.addWidget(self.add_teacher_button)
        
        self.edit_teacher_button = QPushButton("Edit Teacher")
        self.edit_teacher_button.clicked.connect(self.edit_teacher)
        buttons_layout.addWidget(self.edit_teacher_button)
        
        self.delete_teacher_button = QPushButton("Delete Teacher")
        self.delete_teacher_button.clicked.connect(self.delete_teacher)
        buttons_layout.addWidget(self.delete_teacher_button)
        
        self.refresh_teachers_button = QPushButton("Refresh")
        self.refresh_teachers_button.clicked.connect(self.load_teachers)
        buttons_layout.addWidget(self.refresh_teachers_button)
        
        layout.addLayout(buttons_layout)
        
        self.teachers_tab.setLayout(layout)
        
        # Load initial data
        self.load_teachers()
    
    def load_teachers(self):
        """Load teachers data into the table"""
        teachers = self.db_manager.get_all_teachers()
        
        self.teachers_table.setRowCount(len(teachers))
        for i, teacher in enumerate(teachers):
            teacher_id = QTableWidgetItem(str(teacher[0]))
            first_name = QTableWidgetItem(teacher[1])
            last_name = QTableWidgetItem(teacher[2])
            gender = QTableWidgetItem(teacher[3])
            email = QTableWidgetItem(teacher[4])
            phone = QTableWidgetItem(teacher[5])
            subject = QTableWidgetItem(teacher[6])
            
            self.teachers_table.setItem(i, 0, teacher_id)
            self.teachers_table.setItem(i, 1, first_name)
            self.teachers_table.setItem(i, 2, last_name)
            self.teachers_table.setItem(i, 3, gender)
            self.teachers_table.setItem(i, 4, email)
            self.teachers_table.setItem(i, 5, phone)
            self.teachers_table.setItem(i, 6, subject)
        
        self.status_bar.showMessage("Teachers loaded", 3000)
    
    def add_teacher(self):
        """Open dialog to add a new teacher"""
        dialog = TeacherDialog(self.db_manager)
        if dialog.exec_():
            self.load_teachers()
            self.refresh_dashboard()
            self.status_bar.showMessage("Teacher added successfully", 3000)
    
    def edit_teacher(self):
        """Open dialog to edit selected teacher"""
        selected_rows = self.teachers_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a teacher to edit")
            return
        
        teacher_id = int(self.teachers_table.item(selected_rows[0].row(), 0).text())
        
        dialog = TeacherDialog(self.db_manager, teacher_id)
        if dialog.exec_():
            self.load_teachers()
            self.refresh_dashboard()
            self.status_bar.showMessage("Teacher updated successfully", 3000)
    
    def delete_teacher(self):
        """Delete selected teacher"""
        selected_rows = self.teachers_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a teacher to delete")
            return
        
        teacher_id = int(self.teachers_table.item(selected_rows[0].row(), 0).text())
        teacher_name = f"{self.teachers_table.item(selected_rows[0].row(), 1).text()} {self.teachers_table.item(selected_rows[0].row(), 2).text()}"
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete teacher: {teacher_name}? This will also delete their user account.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_teacher(teacher_id):
                self.load_teachers()
                self.refresh_dashboard()
                self.status_bar.showMessage("Teacher deleted successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete teacher")
    
    def setup_classes_tab(self):
        """Setup the classes tab content"""
        layout = QVBoxLayout()
        
        # Classes table
        self.classes_table = QTableWidget()
        self.classes_table.setColumnCount(6)
        self.classes_table.setHorizontalHeaderLabels(["ID", "Class Name", "Grade", "Room", "Teacher", "Schedule"])
        self.classes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.classes_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.classes_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.classes_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        self.add_class_button = QPushButton("Add Class")
        self.add_class_button.clicked.connect(self.add_class)
        buttons_layout.addWidget(self.add_class_button)
        
        self.edit_class_button = QPushButton("Edit Class")
        self.edit_class_button.clicked.connect(self.edit_class)
        buttons_layout.addWidget(self.edit_class_button)
        
        self.delete_class_button = QPushButton("Delete Class")
        self.delete_class_button.clicked.connect(self.delete_class)
        buttons_layout.addWidget(self.delete_class_button)
        
        self.view_students_button = QPushButton("View Students")
        self.view_students_button.clicked.connect(self.view_class_students)
        buttons_layout.addWidget(self.view_students_button)
        
        self.refresh_classes_button = QPushButton("Refresh")
        self.refresh_classes_button.clicked.connect(self.load_classes)
        buttons_layout.addWidget(self.refresh_classes_button)
        
        layout.addLayout(buttons_layout)
        
        self.classes_tab.setLayout(layout)
        
        # Load initial data
        self.load_classes()
    
    def load_classes(self):
        """Load classes data into the table"""
        classes = self.db_manager.get_all_classes()
        
        self.classes_table.setRowCount(len(classes))
        for i, cls in enumerate(classes):
            class_id = QTableWidgetItem(str(cls[0]))
            class_name = QTableWidgetItem(cls[1])
            grade = QTableWidgetItem(cls[2])
            room = QTableWidgetItem(cls[3])
            teacher = QTableWidgetItem(f"{cls[6]} {cls[7]}" if cls[6] and cls[7] else "Not Assigned")
            schedule = QTableWidgetItem(cls[4])
            
            self.classes_table.setItem(i, 0, class_id)
            self.classes_table.setItem(i, 1, class_name)
            self.classes_table.setItem(i, 2, grade)
            self.classes_table.setItem(i, 3, room)
            self.classes_table.setItem(i, 4, teacher)
            self.classes_table.setItem(i, 5, schedule)
        
        self.status_bar.showMessage("Classes loaded", 3000)
    
    def add_class(self):
        """Open dialog to add a new class"""
        dialog = ClassDialog(self.db_manager)
        if dialog.exec_():
            self.load_classes()
            self.refresh_dashboard()
            self.status_bar.showMessage("Class added successfully", 3000)
    
    def edit_class(self):
        """Open dialog to edit selected class"""
        selected_rows = self.classes_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a class to edit")
            return
        
        class_id = int(self.classes_table.item(selected_rows[0].row(), 0).text())
        
        dialog = ClassDialog(self.db_manager, class_id)
        if dialog.exec_():
            self.load_classes()
            self.refresh_dashboard()
            self.status_bar.showMessage("Class updated successfully", 3000)
    
    def delete_class(self):
        """Delete selected class"""
        selected_rows = self.classes_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a class to delete")
            return
        
        class_id = int(self.classes_table.item(selected_rows[0].row(), 0).text())
        class_name = self.classes_table.item(selected_rows[0].row(), 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion",
            f"Are you sure you want to delete class: {class_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_class(class_id):
                self.load_classes()
                self.refresh_dashboard()
                self.status_bar.showMessage("Class deleted successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete class")
    
    def view_class_students(self):
        """View students in the selected class"""
        selected_rows = self.classes_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a class to view students")
            return
        
        class_id = int(self.classes_table.item(selected_rows[0].row(), 0).text())
        class_name = self.classes_table.item(selected_rows[0].row(), 1).text()
        
        dialog = ClassStudentsDialog(self.db_manager, class_id, class_name)
        dialog.exec_()
    
    def logout(self):
        """Handle logout action"""
        reply = QMessageBox.question(
            self, 
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event):
        """Reopen login window when dashboard is closed"""
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.show()
        event.accept()

class TeacherDashboard(QMainWindow):
    """Main window for teacher users"""
    
    def __init__(self, db_manager, teacher_info):
        super().__init__()
        self.db_manager = db_manager
        self.teacher_info = teacher_info
        self.teacher_id = teacher_info[0]
        self.initUI()
        self.closed = False
    
    def initUI(self):
        """Initialize the teacher dashboard UI"""
        self.setWindowTitle("School Management System - Teacher Dashboard")
        self.setMinimumSize(900, 600)
    
        # 🌟 Initialize status bar BEFORE calling setup functions
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
    
        # Create header
        header_layout = QHBoxLayout()
        header_label = QLabel(f"Welcome, {self.teacher_info[1]} {self.teacher_info[2]}")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
    
        # Add logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
    
        main_layout.addLayout(header_layout)
    
        # Create tab widget
        self.tab_widget = QTabWidget()
    
        # Create tabs
        self.dashboard_tab = QWidget()
        self.my_classes_tab = QWidget()
        self.profile_tab = QWidget()
    
        self.tab_widget.addTab(self.dashboard_tab, "Dashboard")
        self.tab_widget.addTab(self.my_classes_tab, "My Classes")
        self.tab_widget.addTab(self.profile_tab, "My Profile")
    
        main_layout.addWidget(self.tab_widget)
    
        # 🌟 Setup UI **after** status bar initialization
        self.setup_dashboard_tab()
        self.setup_my_classes_tab()
        self.setup_profile_tab()
    
        # Set central widget
        self.setCentralWidget(central_widget)
    
        # Show initial status bar message
        self.status_bar.showMessage("Ready")
    
    def setup_dashboard_tab(self):
        """Setup the teacher dashboard tab content"""
        layout = QVBoxLayout()
        
        # Teacher info section
        info_group = QGroupBox("My Information")
        info_layout = QFormLayout()
        
        subject_label = QLabel(f"Subject: {self.teacher_info[9]}")
        email_label = QLabel(f"Email: {self.teacher_info[5]}")
        phone_label = QLabel(f"Phone: {self.teacher_info[6]}")
        
        info_layout.addRow(subject_label)
        info_layout.addRow(email_label)
        info_layout.addRow(phone_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # My classes summary
        classes_group = QGroupBox("My Classes Summary")
        classes_layout = QVBoxLayout()
        
        self.classes_summary_table = QTableWidget()
        self.classes_summary_table.setColumnCount(4)
        self.classes_summary_table.setHorizontalHeaderLabels(["Class Name", "Grade", "Room", "Students"])
        self.classes_summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.classes_summary_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        classes_layout.addWidget(self.classes_summary_table)
        classes_group.setLayout(classes_layout)
        layout.addWidget(classes_group)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Dashboard")
        refresh_button.clicked.connect(self.refresh_dashboard)
        layout.addWidget(refresh_button)
        
        self.dashboard_tab.setLayout(layout)
        
        # Load initial data
        self.refresh_dashboard()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Load teacher's classes
        classes = self.db_manager.get_classes_by_teacher(self.teacher_id)
        
        self.classes_summary_table.setRowCount(len(classes))
        for i, cls in enumerate(classes):
            class_name = QTableWidgetItem(cls[1])
            grade = QTableWidgetItem(cls[2])
            room = QTableWidgetItem(cls[3])
            
            # Count students in this class
            students = self.db_manager.get_students_in_class(cls[0])
            student_count = QTableWidgetItem(str(len(students)))
            
            self.classes_summary_table.setItem(i, 0, class_name)
            self.classes_summary_table.setItem(i, 1, grade)
            self.classes_summary_table.setItem(i, 2, room)
            self.classes_summary_table.setItem(i, 3, student_count)
        
        self.statusBar().showMessage("Dashboard refreshed", 3000)
    
    def setup_my_classes_tab(self):
        """Setup the teacher's classes tab content"""
        layout = QVBoxLayout()
        
        # Classes list
        self.classes_list = QComboBox()
        self.classes_list.currentIndexChanged.connect(self.load_class_students)
        layout.addWidget(QLabel("Select Class:"))
        layout.addWidget(self.classes_list)
        
        # Students in selected class
        students_group = QGroupBox("Students in Class")
        students_layout = QVBoxLayout()
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Gender", "Email"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        students_layout.addWidget(self.students_table)
        students_group.setLayout(students_layout)
        layout.addWidget(students_group)
        
        # Refresh button
        refresh_button = QPushButton("Refresh Classes")
        refresh_button.clicked.connect(self.load_teacher_classes)
        layout.addWidget(refresh_button)
        
        self.my_classes_tab.setLayout(layout)
        
        # Load initial data
        self.load_teacher_classes()
    
    def load_teacher_classes(self):
        """Load teacher's classes into the combo box"""
        self.classes_list.clear()
        
        classes = self.db_manager.get_classes_by_teacher(self.teacher_id)
        self.teacher_classes = classes  # Store classes data
        
        if not classes:
            self.classes_list.addItem("No classes assigned")
            return
        
        for cls in classes:
            self.classes_list.addItem(f"{cls[1]} (Grade {cls[2]})", cls[0])
        
        self.status_bar.showMessage("Classes loaded", 3000)
    
    def load_class_students(self):
        """Load students for the selected class"""
        if self.classes_list.currentText() == "No classes assigned":
            self.students_table.setRowCount(0)
            return
        
        class_id = self.classes_list.currentData()
        if class_id is None:
            return
            
        students = self.db_manager.get_students_in_class(class_id)
        
        self.students_table.setRowCount(len(students))
        for i, student in enumerate(students):
            student_id = QTableWidgetItem(str(student[0]))
            first_name = QTableWidgetItem(student[1])
            last_name = QTableWidgetItem(student[2])
            gender = QTableWidgetItem(student[3])
            email = QTableWidgetItem(student[4])
            
            self.students_table.setItem(i, 0, student_id)
            self.students_table.setItem(i, 1, first_name)
            self.students_table.setItem(i, 2, last_name)
            self.students_table.setItem(i, 3, gender)
            self.students_table.setItem(i, 4, email)
        
        self.status_bar.showMessage(f"Loaded {len(students)} students", 3000)
    
    def setup_profile_tab(self):
        """Setup the teacher profile tab content"""
        layout = QVBoxLayout()
        
        # Teacher profile form
        form_group = QGroupBox("My Profile")
        form_layout = QFormLayout()
        
        # Personal information
        self.first_name_input = QLineEdit(self.teacher_info[1])
        self.last_name_input = QLineEdit(self.teacher_info[2])
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])
        self.gender_input.setCurrentText(self.teacher_info[3])
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.fromString(self.teacher_info[4], "yyyy-MM-dd"))
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Date of Birth:", self.dob_input)
        
        # Contact information
        self.email_input = QLineEdit(self.teacher_info[5])
        self.phone_input = QLineEdit(self.teacher_info[6])
        self.address_input = QLineEdit(self.teacher_info[7])
        
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        
        # Academic information
        self.subject_input = QLineEdit(self.teacher_info[9])
        
        form_layout.addRow("Subject:", self.subject_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Username and password section
        credentials_group = QGroupBox("Login Credentials")
        credentials_layout = QFormLayout()
        
        # Get username from database
        self.cursor = self.db_manager.conn.cursor()
        self.cursor.execute("SELECT username FROM users WHERE id = ?", (self.teacher_info[10],))
        username = self.cursor.fetchone()[0]
        
        self.username_input = QLineEdit(username)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter new password (leave blank to keep current)")
        
        credentials_layout.addRow("Username:", self.username_input)
        credentials_layout.addRow("New Password:", self.password_input)
        
        credentials_group.setLayout(credentials_layout)
        layout.addWidget(credentials_group)
        
        # Save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_profile)
        layout.addWidget(save_button)
        
        self.profile_tab.setLayout(layout)
    
    def save_profile(self):
        """Save teacher profile changes"""
        # Gather form data
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        gender = self.gender_input.currentText()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        subject = self.subject_input.text()
        username = self.username_input.text()
        password = self.password_input.text() if self.password_input.text() else None
        
        # Validate inputs
        if not first_name or not last_name or not email:
            QMessageBox.warning(self, "Warning", "First name, last name, and email are required")
            return
        
        # Teacher data
        teacher_data = (first_name, last_name, gender, dob, email, phone, address, 
                        self.teacher_info[8], subject)
        
        # Update in database
        if self.db_manager.update_teacher(self.teacher_id, teacher_data, username, password):
            # Update teacher info
            self.teacher_info = self.db_manager.get_teacher(self.teacher_id)
            
            # Update header
            self.findChild(QLabel).setText(f"Welcome, {first_name} {last_name}")
            
            QMessageBox.information(self, "Success", "Profile updated successfully")
            self.status_bar.showMessage("Profile updated", 3000)
        else:
            QMessageBox.critical(self, "Error", "Failed to update profile")
    
    def logout(self):
        """Handle logout action"""
        reply = QMessageBox.question(
            self, 
            "Confirm Logout",
            "Are you sure you want to log out?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event):
        """Reopen login window when dashboard is closed"""
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.show()
        event.accept()

class StudentDialog(QDialog):
    """Dialog for adding/editing student information"""
    
    def __init__(self, db_manager, student_id=None):
        super().__init__()
        self.db_manager = db_manager
        self.student_id = student_id
        self.is_edit_mode = student_id is not None
        
        self.initUI()
        
        if self.is_edit_mode:
            self.load_student_data()
    
    def initUI(self):
        """Initialize the dialog UI"""
        if self.is_edit_mode:
            self.setWindowTitle("Edit Student")
        else:
            self.setWindowTitle("Add Student")
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Personal information
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.currentDate().addYears(-15))  # Default age
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Date of Birth:", self.dob_input)
        
        # Contact information
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        
        # Academic information
        self.enrollment_date_input = QDateEdit()
        self.enrollment_date_input.setDisplayFormat("yyyy-MM-dd")
        self.enrollment_date_input.setDate(QDate.currentDate())
        
        self.class_input = QComboBox()
        self.load_class_options()
        
        form_layout.addRow("Enrollment Date:", self.enrollment_date_input)
        form_layout.addRow("Class:", self.class_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        if self.is_edit_mode:
            self.save_button = QPushButton("Update")
        else:
            self.save_button = QPushButton("Add")
        self.save_button.clicked.connect(self.save_student)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.save_button)
        
        layout.addLayout(button_box)
        
        self.setLayout(layout)
    
    def load_class_options(self):
        """Load class options into combobox"""
        self.class_input.addItem("Not Assigned", None)
        
        classes = self.db_manager.get_class_options()
        for cls in classes:
            self.class_input.addItem(cls[1], cls[0])
    
    def load_student_data(self):
        """Load existing student data in edit mode"""
        student = self.db_manager.get_student(self.student_id)
        if not student:
            QMessageBox.critical(self, "Error", "Student not found")
            self.reject()
            return
        
        self.first_name_input.setText(student[1])
        self.last_name_input.setText(student[2])
        self.gender_input.setCurrentText(student[3])
        self.dob_input.setDate(QDate.fromString(student[4], "yyyy-MM-dd"))
        self.email_input.setText(student[5] if student[5] else "")
        self.phone_input.setText(student[6] if student[6] else "")
        self.address_input.setText(student[7] if student[7] else "")
        self.enrollment_date_input.setDate(QDate.fromString(student[8], "yyyy-MM-dd"))
        
        # Set class if assigned
        if student[9]:  # class_id
            index = self.class_input.findData(student[9])
            if index >= 0:
                self.class_input.setCurrentIndex(index)
    
    def save_student(self):
        """Save student data"""
        # Validate inputs
        if not self.first_name_input.text() or not self.last_name_input.text():
            QMessageBox.warning(self, "Warning", "First name and last name are required")
            return
        
        # Gather form data
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        gender = self.gender_input.currentText()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        enrollment_date = self.enrollment_date_input.date().toString("yyyy-MM-dd")
        class_id = self.class_input.currentData()
        
        # Prepare data tuple
        student_data = (first_name, last_name, gender, dob, email, phone, address, enrollment_date, class_id)
        
        if self.is_edit_mode:
            # Update existing student
            if self.db_manager.update_student(self.student_id, student_data):
                QMessageBox.information(self, "Success", "Student updated successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update student")
        else:
            # Add new student
            success, student_id = self.db_manager.add_student(student_data)
            if success:
                QMessageBox.information(self, "Success", "Student added successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add student")


class TeacherDialog(QDialog):
    """Dialog for adding/editing teacher information"""
    
    def __init__(self, db_manager, teacher_id=None):
        super().__init__()
        self.db_manager = db_manager
        self.teacher_id = teacher_id
        self.is_edit_mode = teacher_id is not None
        
        self.initUI()
        
        if self.is_edit_mode:
            self.load_teacher_data()
    
    def initUI(self):
        """Initialize the dialog UI"""
        if self.is_edit_mode:
            self.setWindowTitle("Edit Teacher")
        else:
            self.setWindowTitle("Add Teacher")
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Personal information
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Male", "Female"])
        self.dob_input = QDateEdit()
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.currentDate().addYears(-30))  # Default age
        
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Gender:", self.gender_input)
        form_layout.addRow("Date of Birth:", self.dob_input)
        
        # Contact information
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()
        
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)
        
        # Academic information
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setDisplayFormat("yyyy-MM-dd")
        self.hire_date_input.setDate(QDate.currentDate())
        self.subject_input = QLineEdit()
        
        form_layout.addRow("Hire Date:", self.hire_date_input)
        form_layout.addRow("Subject:", self.subject_input)
        
        # Login credentials
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)
        
        if self.is_edit_mode:
            self.password_input.setPlaceholderText("Leave blank to keep current password")
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        if self.is_edit_mode:
            self.save_button = QPushButton("Update")
        else:
            self.save_button = QPushButton("Add")
        self.save_button.clicked.connect(self.save_teacher)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.save_button)
        
        layout.addLayout(button_box)
        
        self.setLayout(layout)
    
    def load_teacher_data(self):
        """Load existing teacher data in edit mode"""
        teacher = self.db_manager.get_teacher(self.teacher_id)
        if not teacher:
            QMessageBox.critical(self, "Error", "Teacher not found")
            self.reject()
            return
        
        self.first_name_input.setText(teacher[1])
        self.last_name_input.setText(teacher[2])
        self.gender_input.setCurrentText(teacher[3])
        self.dob_input.setDate(QDate.fromString(teacher[4], "yyyy-MM-dd"))
        self.email_input.setText(teacher[5] if teacher[5] else "")
        self.phone_input.setText(teacher[6] if teacher[6] else "")
        self.address_input.setText(teacher[7] if teacher[7] else "")
        self.hire_date_input.setDate(QDate.fromString(teacher[8], "yyyy-MM-dd"))
        self.subject_input.setText(teacher[9] if teacher[9] else "")
        self.username_input.setText(teacher[11] if teacher[11] else "")  # Username
    
    def save_teacher(self):
        """Save teacher data"""
        # Validate inputs
        if not self.first_name_input.text() or not self.last_name_input.text():
            QMessageBox.warning(self, "Warning", "First name and last name are required")
            return
        
        if not self.username_input.text():
            QMessageBox.warning(self, "Warning", "Username is required")
            return
        
        if not self.is_edit_mode and not self.password_input.text():
            QMessageBox.warning(self, "Warning", "Password is required")
            return
        
        # Gather form data
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text()
        gender = self.gender_input.currentText()
        dob = self.dob_input.date().toString("yyyy-MM-dd")
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()
        hire_date = self.hire_date_input.date().toString("yyyy-MM-dd")
        subject = self.subject_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Prepare data tuple
        teacher_data = (first_name, last_name, gender, dob, email, phone, address, hire_date, subject)
        
        if self.is_edit_mode:
            # Update existing teacher
            if self.db_manager.update_teacher(self.teacher_id, teacher_data, username, password if password else None):
                QMessageBox.information(self, "Success", "Teacher updated successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update teacher")
        else:
            # Add new teacher
            success, teacher_id = self.db_manager.add_teacher(teacher_data, username, password)
            if success:
                QMessageBox.information(self, "Success", "Teacher added successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add teacher")


class ClassDialog(QDialog):
    """Dialog for adding/editing class information"""
    
    def __init__(self, db_manager, class_id=None):
        super().__init__()
        self.db_manager = db_manager
        self.class_id = class_id
        self.is_edit_mode = class_id is not None
        
        self.initUI()
        
        if self.is_edit_mode:
            self.load_class_data()
    
    def initUI(self):
        """Initialize the dialog UI"""
        if self.is_edit_mode:
            self.setWindowTitle("Edit Class")
        else:
            self.setWindowTitle("Add Class")
        
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Class information
        self.class_name_input = QLineEdit()
        self.grade_input = QComboBox()
        self.grade_input.addItems(["1-primary", "2-primary", "3-primary", "4-primary", "5-primary", "6-primary", "1-preparatory", "2-preparatory", "3-preparatory", "1-secondary", "2-secondary", "3-secondary"])
        self.room_input = QLineEdit()
        
        form_layout.addRow("Class Name:", self.class_name_input)
        form_layout.addRow("Grade:", self.grade_input)
        form_layout.addRow("Room Number:", self.room_input)
        
        # Teacher selection
        self.teacher_input = QComboBox()
        self.load_teacher_options()
        
        form_layout.addRow("Teacher:", self.teacher_input)
        
        # Schedule
        self.schedule_input = QLineEdit()
        self.schedule_input.setPlaceholderText("e.g., Mon-Wed-Fri 9:00-10:30")
        
        form_layout.addRow("Schedule:", self.schedule_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        if self.is_edit_mode:
            self.save_button = QPushButton("Update")
        else:
            self.save_button = QPushButton("Add")
        self.save_button.clicked.connect(self.save_class)
        
        button_box.addWidget(self.cancel_button)
        button_box.addWidget(self.save_button)
        
        layout.addLayout(button_box)
        
        self.setLayout(layout)
    
    def load_teacher_options(self):
        """Load teacher options into combobox"""
        self.teacher_input.addItem("Not Assigned", None)
        
        # Fix the SQL query in the database manager
        self.db_manager.cursor.execute('''
            SELECT id, first_name || ' ' || last_name as full_name 
            FROM teachers 
            ORDER BY last_name, first_name
        ''')
        teachers = self.db_manager.cursor.fetchall()
        
        for teacher in teachers:
            self.teacher_input.addItem(teacher[1], teacher[0])
    
    def load_class_data(self):
        """Load existing class data in edit mode"""
        class_data = self.db_manager.get_class(self.class_id)
        if not class_data:
            QMessageBox.critical(self, "Error", "Class not found")
            self.reject()
            return
        
        self.class_name_input.setText(class_data[1])
        index = self.grade_input.findText(class_data[2])
        if index >= 0:
            self.grade_input.setCurrentIndex(index)
        self.room_input.setText(class_data[3] if class_data[3] else "")
        
        # Set teacher if assigned
        if class_data[4]:  # teacher_id
            index = self.teacher_input.findData(class_data[4])
            if index >= 0:
                self.teacher_input.setCurrentIndex(index)
        
        self.schedule_input.setText(class_data[5] if class_data[5] else "")
    
    def save_class(self):
        """Save class data"""
        # Validate inputs
        if not self.class_name_input.text():
            QMessageBox.warning(self, "Warning", "Class name is required")
            return
        
        # Gather form data
        class_name = self.class_name_input.text()
        grade = self.grade_input.currentText()
        room = self.room_input.text()
        teacher_id = self.teacher_input.currentData()
        schedule = self.schedule_input.text()
        
        # Prepare data tuple
        class_data = (class_name, grade, room, teacher_id, schedule)
        
        if self.is_edit_mode:
            # Update existing class
            if self.db_manager.update_class(self.class_id, class_data):
                QMessageBox.information(self, "Success", "Class updated successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to update class")
        else:
            # Add new class
            success, class_id = self.db_manager.add_class(class_data)
            if success:
                QMessageBox.information(self, "Success", "Class added successfully")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to add class")


class ClassStudentsDialog(QDialog):
    """Dialog to view students in a class"""
    
    def __init__(self, db_manager, class_id, class_name):
        super().__init__()
        self.db_manager = db_manager
        self.class_id = class_id
        self.class_name = class_name
        
        self.initUI()
        self.load_students()
    
    def initUI(self):
        """Initialize the dialog UI"""
        self.setWindowTitle(f"Students in {self.class_name}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(f"Students in {self.class_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Gender", "Email"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.students_table)

        # Buttons
        button_layout = QHBoxLayout()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def load_students(self):
        """Load students in the selected class"""
        students = self.db_manager.get_students_in_class(self.class_id)

        self.students_table.setRowCount(len(students))
        for i, student in enumerate(students):
            student_id = QTableWidgetItem(str(student[0]))
            first_name = QTableWidgetItem(student[1])
            last_name = QTableWidgetItem(student[2])
            gender = QTableWidgetItem(student[3])
            email = QTableWidgetItem(student[4])

            self.students_table.setItem(i, 0, student_id)
            self.students_table.setItem(i, 1, first_name)
            self.students_table.setItem(i, 2, last_name)
            self.students_table.setItem(i, 3, gender)
            self.students_table.setItem(i, 4, email)
        
        self.status_bar.showMessage(f"Loaded {len(students)} students in {self.class_name}", 3000)


def set_dark_mode(app):
    """Enable dark mode for the PyQt5 application."""
    app.setStyle("Fusion")
    dark_palette = app.palette()
    
    dark_palette.setColor(dark_palette.Window, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Base, QColor(25, 25, 25))
    dark_palette.setColor(dark_palette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Text, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.Highlight, QColor(142, 45, 197))
    dark_palette.setColor(dark_palette.HighlightedText, QColor(255, 255, 255))

    app.setPalette(dark_palette)

# Add this to the main entry point:
if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_mode(app)  # Enable dark mode
    db_manager = DatabaseManager()
    login_window = LoginWindow(db_manager)
    login_window.show()
    sys.exit(app.exec_())
