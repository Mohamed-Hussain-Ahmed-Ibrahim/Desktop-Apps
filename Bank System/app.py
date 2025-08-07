import sys
import sqlite3
import hashlib
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon
import os
import datetime

class Database:
    def __init__(self):
        # Create or connect to SQLite database
        self.conn = sqlite3.connect('bank_system.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # Create users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0
            )
        ''')
        
        # Create accounts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                email TEXT,
                balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                account_id INTEGER,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        ''')
        
        # Check if default admin exists, if not create one
        self.cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not self.cursor.fetchone():
            # Create default admin (username: admin, password: admin123)
            hashed_password = hashlib.sha256("admin123".encode()).hexdigest()
            self.cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                               ("admin", hashed_password, 1))
        
        self.conn.commit()
    
    def authenticate_user(self, username, password):
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                           (username, hashed_password))
        return self.cursor.fetchone()
    
    def create_account(self, name, account_number, email, initial_balance=0.0):
        try:
            self.cursor.execute(
                "INSERT INTO accounts (name, account_number, email, balance) VALUES (?, ?, ?, ?)",
                (name, account_number, email, initial_balance)
            )
            self.conn.commit()
            
            # Get the ID of the newly created account
            account_id = self.cursor.lastrowid
            
            # Record the initial deposit as a transaction if balance > 0
            if initial_balance > 0:
                self.add_transaction(account_id, "deposit", initial_balance)
                
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_accounts(self):
        self.cursor.execute("SELECT * FROM accounts ORDER BY name")
        return self.cursor.fetchall()
    
    def get_account_by_id(self, account_id):
        self.cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
        return self.cursor.fetchone()
    
    def get_account_by_number(self, account_number):
        self.cursor.execute("SELECT * FROM accounts WHERE account_number = ?", (account_number,))
        return self.cursor.fetchone()
    
    def search_accounts(self, search_term):
        self.cursor.execute(
            "SELECT * FROM accounts WHERE name LIKE ? OR account_number LIKE ?", 
            (f"%{search_term}%", f"%{search_term}%")
        )
        return self.cursor.fetchall()
    
    def update_account(self, account_id, name, email, account_number):
        try:
            self.cursor.execute(
                "UPDATE accounts SET name = ?, email = ?, account_number = ? WHERE id = ?",
                (name, email, account_number, account_id)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def delete_account(self, account_id):
        try:
            # Delete all transactions for this account
            self.cursor.execute("DELETE FROM transactions WHERE account_id = ?", (account_id,))
            # Delete the account
            self.cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting account: {e}")
            return False
    
    def deposit(self, account_id, amount):
        try:
            # First, update the account balance
            self.cursor.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (amount, account_id)
            )
            # Then, record the transaction
            self.add_transaction(account_id, "deposit", amount)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error during deposit: {e}")
            return False
    
    def withdraw(self, account_id, amount):
        try:
            # Check if there's enough balance
            self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            current_balance = self.cursor.fetchone()[0]
            
            if current_balance < amount:
                return False
            
            # Update the account balance
            self.cursor.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, account_id)
            )
            # Record the transaction
            self.add_transaction(account_id, "withdrawal", amount)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error during withdrawal: {e}")
            return False
    
    def add_transaction(self, account_id, transaction_type, amount):
        self.cursor.execute(
            "INSERT INTO transactions (account_id, transaction_type, amount) VALUES (?, ?, ?)",
            (account_id, transaction_type, amount)
        )
        self.conn.commit()
    
    def get_account_transactions(self, account_id):
        self.cursor.execute(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY timestamp DESC",
            (account_id,)
        )
        return self.cursor.fetchall()

    def get_account_balance(self, account_id):
        self.cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return 0
    
    def close(self):
        self.conn.close()


class LoginWindow(QWidget):
    loginSuccessful = pyqtSignal()
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Bank Management System - Login")
        self.setGeometry(300, 300, 400, 200)
        
        main_layout = QVBoxLayout()
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_edit)
        
        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_edit)
        
        # Create login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        
        # Add layouts to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.login_button)
        
        # Set main layout to the widget
        self.setLayout(main_layout)
        
    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Warning", "Please enter both username and password.")
            return
        
        user = self.db.authenticate_user(username, password)
        
        if user:
            self.loginSuccessful.emit()
        else:
            QMessageBox.critical(self, "Error", "Invalid username or password.")


class AccountsTable(QTableWidget):
    accountSelected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["ID", "Name", "Account Number", "Email", "Balance"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.itemSelectionChanged.connect(self.on_selection_changed)
        
    def populate_accounts(self, accounts):
        self.setRowCount(0)
        
        for account in accounts:
            row_position = self.rowCount()
            self.insertRow(row_position)
            
            self.setItem(row_position, 0, QTableWidgetItem(str(account[0])))
            self.setItem(row_position, 1, QTableWidgetItem(account[1]))
            self.setItem(row_position, 2, QTableWidgetItem(account[2]))
            self.setItem(row_position, 3, QTableWidgetItem(account[3] if account[3] else ""))
            self.setItem(row_position, 4, QTableWidgetItem(f"${account[4]:.2f}"))
            
    def on_selection_changed(self):
        selected_items = self.selectedItems()
        if selected_items:
            account_id = int(selected_items[0].text())
            self.accountSelected.emit(account_id)


class TransactionsTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["ID", "Type", "Amount", "Date"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
    def populate_transactions(self, transactions):
        self.setRowCount(0)
        
        for transaction in transactions:
            row_position = self.rowCount()
            self.insertRow(row_position)
            
            self.setItem(row_position, 0, QTableWidgetItem(str(transaction[0])))
            self.setItem(row_position, 1, QTableWidgetItem(transaction[2].capitalize()))
            
            # Format amount with currency and color
            amount_item = QTableWidgetItem(f"${transaction[3]:.2f}")
            if transaction[2].lower() == "deposit":
                amount_item.setForeground(Qt.darkGreen)
            else:
                amount_item.setForeground(Qt.darkRed)
            self.setItem(row_position, 2, amount_item)
            
            # Format date
            date_str = transaction[4]
            self.setItem(row_position, 3, QTableWidgetItem(date_str))


class BankApp(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_account_id = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Bank Management System")
        self.setGeometry(100, 100, 1000, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_accounts_tab()
        self.create_transactions_tab()
        self.create_search_tab()
        
    def create_accounts_tab(self):
        accounts_tab = QWidget()
        layout = QVBoxLayout()
        
        # Create layout for account creation form
        form_group = QGroupBox("Create New Account")
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)
        
        # Account number field
        self.account_number_edit = QLineEdit()
        form_layout.addRow("Account Number:", self.account_number_edit)
        
        # Email field
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        # Initial balance field
        self.initial_balance_edit = QDoubleSpinBox()
        self.initial_balance_edit.setRange(0, 1000000)
        self.initial_balance_edit.setDecimals(2)
        self.initial_balance_edit.setSingleStep(100)
        form_layout.addRow("Initial Balance:", self.initial_balance_edit)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Create account button
        create_button = QPushButton("Create Account")
        create_button.clicked.connect(self.create_account)
        button_layout.addWidget(create_button)
        
        # Edit account button
        self.edit_button = QPushButton("Update Account")
        self.edit_button.clicked.connect(self.update_account)
        self.edit_button.setEnabled(False)
        button_layout.addWidget(self.edit_button)
        
        # Delete account button
        self.delete_button = QPushButton("Delete Account")
        self.delete_button.clicked.connect(self.delete_account)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        # Clear form button
        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_account_form)
        button_layout.addWidget(clear_button)
        
        # Add layouts to form group
        form_group.setLayout(form_layout)
        
        # Add form and buttons to layout
        layout.addWidget(form_group)
        layout.addLayout(button_layout)
        
        # Create accounts table
        self.accounts_table = AccountsTable()
        self.accounts_table.accountSelected.connect(self.on_account_selected)
        layout.addWidget(self.accounts_table)
        
        # Set layout to tab
        accounts_tab.setLayout(layout)
        
        # Add tab to tab widget
        self.tab_widget.addTab(accounts_tab, "Accounts")
        
        # Load accounts
        self.load_accounts()
        
    def create_transactions_tab(self):
        transactions_tab = QWidget()
        layout = QVBoxLayout()
        
        # Create a splitter for the left and right panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel for account selection and transaction actions
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Account info group
        account_group = QGroupBox("Account Information")
        account_layout = QFormLayout()
        
        self.selected_account_label = QLabel("No account selected")
        account_layout.addRow("Selected Account:", self.selected_account_label)
        
        self.balance_label = QLabel("$0.00")
        self.balance_label.setFont(QFont("Arial", 12, QFont.Bold))
        account_layout.addRow("Current Balance:", self.balance_label)
        
        account_group.setLayout(account_layout)
        left_layout.addWidget(account_group)
        
        # Transaction group
        transaction_group = QGroupBox("Make Transaction")
        transaction_layout = QFormLayout()
        
        # Transaction type
        self.transaction_type = QComboBox()
        self.transaction_type.addItems(["Deposit", "Withdrawal"])
        transaction_layout.addRow("Type:", self.transaction_type)
        
        # Amount field
        self.amount_edit = QDoubleSpinBox()
        self.amount_edit.setRange(0, 1000000)
        self.amount_edit.setDecimals(2)
        self.amount_edit.setSingleStep(100)
        transaction_layout.addRow("Amount:", self.amount_edit)
        
        # Submit button
        self.submit_transaction_button = QPushButton("Submit Transaction")
        self.submit_transaction_button.clicked.connect(self.submit_transaction)
        self.submit_transaction_button.setEnabled(False)
        
        transaction_group.setLayout(transaction_layout)
        left_layout.addWidget(transaction_group)
        left_layout.addWidget(self.submit_transaction_button)
        left_layout.addStretch()
        
        # Right panel for transaction history
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Transaction history label
        history_label = QLabel("Transaction History")
        history_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(history_label)
        
        # Transactions table
        self.transactions_table = TransactionsTable()
        right_layout.addWidget(self.transactions_table)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        
        # Set splitter sizes
        splitter.setSizes([300, 700])
        
        # Add splitter to layout
        layout.addWidget(splitter)
        
        # Set layout to tab
        transactions_tab.setLayout(layout)
        
        # Add tab to tab widget
        self.tab_widget.addTab(transactions_tab, "Transactions")
    
    def create_search_tab(self):
        search_tab = QWidget()
        layout = QVBoxLayout()
        
        # Search form
        search_layout = QHBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or account number")
        search_layout.addWidget(self.search_edit)
        
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_accounts)
        search_layout.addWidget(search_button)
        
        layout.addLayout(search_layout)
        
        # Search results table
        self.search_results_table = AccountsTable()
        self.search_results_table.accountSelected.connect(self.on_account_selected)
        layout.addWidget(self.search_results_table)
        
        # Set layout to tab
        search_tab.setLayout(layout)
        
        # Add tab to tab widget
        self.tab_widget.addTab(search_tab, "Search")
    
    def load_accounts(self):
        accounts = self.db.get_all_accounts()
        self.accounts_table.populate_accounts(accounts)
    
    def create_account(self):
        name = self.name_edit.text()
        account_number = self.account_number_edit.text()
        email = self.email_edit.text()
        initial_balance = self.initial_balance_edit.value()
        
        if not name or not account_number:
            QMessageBox.warning(self, "Warning", "Please enter name and account number.")
            return
        
        success = self.db.create_account(name, account_number, email, initial_balance)
        
        if success:
            QMessageBox.information(self, "Success", "Account created successfully.")
            self.clear_account_form()
            self.load_accounts()
        else:
            QMessageBox.critical(self, "Error", "Account number already exists. Please use a different one.")
    
    def update_account(self):
        if not self.selected_account_id:
            return
        
        name = self.name_edit.text()
        account_number = self.account_number_edit.text()
        email = self.email_edit.text()
        
        if not name or not account_number:
            QMessageBox.warning(self, "Warning", "Please enter name and account number.")
            return
        
        success = self.db.update_account(self.selected_account_id, name, email, account_number)
        
        if success:
            QMessageBox.information(self, "Success", "Account updated successfully.")
            self.clear_account_form()
            self.load_accounts()
            self.selected_account_id = None
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            QMessageBox.critical(self, "Error", "Account number already exists. Please use a different one.")
    
    def delete_account(self):
        if not self.selected_account_id:
            return
        
        reply = QMessageBox.question(self, "Confirmation", 
                                    "Are you sure you want to delete this account? This action cannot be undone.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success = self.db.delete_account(self.selected_account_id)
            
            if success:
                QMessageBox.information(self, "Success", "Account deleted successfully.")
                self.clear_account_form()
                self.load_accounts()
                self.selected_account_id = None
                self.edit_button.setEnabled(False)
                self.delete_button.setEnabled(False)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete account.")
    
    def clear_account_form(self):
        self.name_edit.clear()
        self.account_number_edit.clear()
        self.email_edit.clear()
        self.initial_balance_edit.setValue(0)
        self.selected_account_id = None
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
    
    def on_account_selected(self, account_id):
        self.selected_account_id = account_id
        account = self.db.get_account_by_id(account_id)
        
        if account:
            # Update account form
            self.name_edit.setText(account[1])
            self.account_number_edit.setText(account[2])
            self.email_edit.setText(account[3] if account[3] else "")
            
            # Enable edit and delete buttons
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            
            # Update transaction tab
            self.selected_account_label.setText(f"{account[1]} ({account[2]})")
            self.balance_label.setText(f"${account[4]:.2f}")
            self.submit_transaction_button.setEnabled(True)
            
            # Load transactions
            transactions = self.db.get_account_transactions(account_id)
            self.transactions_table.populate_transactions(transactions)
            
            # Switch to transactions tab if not in search tab
            if self.tab_widget.currentIndex() != 2:  # Not search tab
                self.tab_widget.setCurrentIndex(1)  # Switch to transactions tab
    
    def submit_transaction(self):
        if not self.selected_account_id:
            return
        
        transaction_type = self.transaction_type.currentText().lower()
        amount = self.amount_edit.value()
        
        if amount <= 0:
            QMessageBox.warning(self, "Warning", "Amount must be greater than zero.")
            return
        
        success = False
        
        if transaction_type == "deposit":
            success = self.db.deposit(self.selected_account_id, amount)
        elif transaction_type == "withdrawal":
            success = self.db.withdraw(self.selected_account_id, amount)
        
        if success:
            QMessageBox.information(self, "Success", f"{transaction_type.capitalize()} successful.")
            
            # Update balance
            new_balance = self.db.get_account_balance(self.selected_account_id)
            self.balance_label.setText(f"${new_balance:.2f}")
            
            # Reset amount field
            self.amount_edit.setValue(0)
            
            # Refresh transactions
            transactions = self.db.get_account_transactions(self.selected_account_id)
            self.transactions_table.populate_transactions(transactions)
        else:
            if transaction_type == "withdrawal":
                QMessageBox.critical(self, "Error", "Insufficient funds.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to process {transaction_type}.")
    
    def search_accounts(self):
        search_term = self.search_edit.text()
        
        if not search_term:
            QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return
        
        accounts = self.db.search_accounts(search_term)
        self.search_results_table.populate_accounts(accounts)


def main():
    app = QApplication(sys.argv)
    
    # Create database connection
    db = Database()
    
    # Create login window
    login_window = LoginWindow(db)
    
    # Create main application window
    main_window = BankApp(db)
    
    # Connect login signal
    login_window.loginSuccessful.connect(lambda: (login_window.hide(), main_window.show()))
    
    # Show login window
    login_window.show()
    
    # Execute application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
