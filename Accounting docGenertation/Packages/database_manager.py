import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from tkinter.messagebox import showerror
class DatabaseManager:
    """
    Central database manager for the company management system.
    Handles all database operations including CRUD operations for all tables.
    """
    
    def __init__(self, db_path: str = "DB/company_management.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Read and execute the schema SQL
                schema_sql = """
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_name TEXT NOT NULL,
                    brand TEXT NOT NULL,
                    model TEXT NOT NULL,
                    category TEXT NOT NULL,
                    serial_number TEXT UNIQUE NOT NULL,
                    purchase_date DATE NOT NULL,
                    cost REAL NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'available',
                    description TEXT,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    department TEXT,
                    base_salary REAL NOT NULL,
                    phone TEXT,
                    email TEXT,
                    hire_date DATE NOT NULL,
                    emergency_contact TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS payroll (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    base_salary REAL NOT NULL,
                    bonuses REAL DEFAULT 0,
                    deductions REAL DEFAULT 0,
                    total_salary REAL NOT NULL,
                    payment_date DATE,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id),
                    UNIQUE(employee_id, month, year)
                );

                CREATE TABLE IF NOT EXISTS payroll_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payroll_id INTEGER NOT NULL,
                    employee_id INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    bonus REAL DEFAULT 0,
                    deduction REAL DEFAULT 0,
                    notes TEXT NOT NULL,
                    adjusted_by TEXT NOT NULL,
                    adjustment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (payroll_id) REFERENCES payroll (id),
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                );

                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    hours_worked REAL DEFAULT 8.0,
                    overtime_hours REAL DEFAULT 0.0,
                    total_hours REAL GENERATED ALWAYS AS (hours_worked + overtime_hours),
                    status TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id),
                    UNIQUE(employee_id, date)
                );

                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER NOT NULL,
                    sale_price REAL NOT NULL,
                    customer_name TEXT,
                    customer_phone TEXT,
                    sale_date DATE NOT NULL,
                    payment_method TEXT DEFAULT 'cash',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                );

                CREATE TABLE IF NOT EXISTS document_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    description TEXT,
                    quantity INTEGER NOT NULL,
                    unit_cost REAL NOT NULL,
                    total_cost REAL NOT NULL,
                    image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                cursor.executescript(schema_sql)
                
                # Create indexes
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_payroll_employee ON payroll(employee_id);",
                    "CREATE INDEX IF NOT EXISTS idx_payroll_date ON payroll(year, month);",
                    "CREATE INDEX IF NOT EXISTS idx_attendance_employee ON attendance(employee_id);",
                    "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);",
                    "CREATE INDEX IF NOT EXISTS idx_payroll_adjustments_payroll ON payroll_adjustments(payroll_id);",
                    "CREATE INDEX IF NOT EXISTS idx_payroll_adjustments_employee ON payroll_adjustments(employee_id);",
                    "CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);",
                    "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);"
                ]
                
                for index in indexes:
                    cursor.execute(index)
                
                conn.commit()

                
        except sqlite3.Error as e:
            showerror("Error",f"Database initialization error: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = (), fetch: bool = False, fetch_one: bool = False) -> Any:
        """
        Execute a database query with error handling.
        Enhanced to support fetch_one parameter.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Enable dict-like access
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]  # Convert all fetched rows to dicts
                else:
                    conn.commit()
                    return cursor.lastrowid
                    
        except sqlite3.Error as e:
            showerror("Error", f"Database query error: {e}")
            raise
    
    def add_payroll_adjustment(self, adjustment_data: Dict) -> int:
        """Add a payroll adjustment record with full tracking."""
        query = """
        INSERT INTO payroll_adjustments 
        (payroll_id, employee_id, month, year, bonus, deduction, notes, adjusted_by, adjustment_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            adjustment_data.get('payroll_id'),
            adjustment_data['employee_id'],
            adjustment_data['month'],
            adjustment_data['year'],
            adjustment_data.get('bonus', 0),
            adjustment_data.get('deduction', 0),
            adjustment_data['notes'],
            adjustment_data.get('adjusted_by', 'Admin'),
            adjustment_data.get('adjustment_date', datetime.now().isoformat())
        )
        return self.execute_query(query, params)
    
    def get_employee_adjustments(self, employee_id: int, month: int = None, year: int = None) -> List[Dict]:
        """Get all adjustments for a specific employee with optional date filtering."""
        query = """
        SELECT pa.*, e.employee_name, p.base_salary, p.total_salary
        FROM payroll_adjustments pa
        JOIN employees e ON pa.employee_id = e.id
        LEFT JOIN payroll p ON pa.payroll_id = p.id
        WHERE pa.employee_id = ?
        """
        params = [employee_id]
        
        if month is not None:
            query += " AND pa.month = ?"
            params.append(month)
        
        if year is not None:
            query += " AND pa.year = ?"
            params.append(year)
        
        query += " ORDER BY pa.adjustment_date DESC"
        
        return self.execute_query(query, tuple(params), fetch=True)

    def get_all_adjustments_summary(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """Get summary of all payroll adjustments for reporting."""
        query = """
        SELECT 
            pa.id,
            pa.employee_id,
            e.employee_name,
            pa.month,
            pa.year,
            pa.bonus,
            pa.deduction,
            pa.notes,
            pa.adjusted_by,
            pa.adjustment_date,
            p.base_salary,
            p.total_salary
        FROM payroll_adjustments pa
        JOIN employees e ON pa.employee_id = e.id
        LEFT JOIN payroll p ON pa.payroll_id = p.id
        WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(pa.adjustment_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(pa.adjustment_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY pa.adjustment_date DESC"
        
        return self.execute_query(query, tuple(params), fetch=True)

    def update_payroll_with_adjustment(self, payroll_id: int, bonus_amount: float, deduction_amount: float, notes: str) -> bool:
        """Update payroll record with new adjustment amounts."""
        try:
            # Get current payroll record
            current_record = self.execute_query(
                "SELECT bonuses, deductions, base_salary FROM payroll WHERE id = ?",
                (payroll_id,), fetch_one=True
            )
            
            if not current_record:
                raise ValueError(f"Payroll record {payroll_id} not found")
            
            # Calculate new totals
            new_bonuses = (current_record.get('bonuses', 0) or 0) + bonus_amount
            new_deductions = (current_record.get('deductions', 0) or 0) + deduction_amount
            new_total = (current_record.get('base_salary', 0) or 0) + new_bonuses - new_deductions
            
            # Update payroll record
            update_query = """
            UPDATE payroll 
            SET bonuses = ?, deductions = ?, total_salary = ?, 
                notes = COALESCE(notes, '') || ?, updated_at = ?
            WHERE id = ?
            """
            
            adjustment_note = f"\n--- Adjustment on {datetime.now().strftime('%Y-%m-%d %H:%M')} ---\n{notes}\n"
            
            self.execute_query(update_query, (
                new_bonuses, 
                new_deductions, 
                new_total,
                adjustment_note,
                datetime.now().isoformat(),
                payroll_id
            ))
            
            return True
            
        except Exception as e:
            showerror("Error",f"Error updating payroll with adjustment: {e}")
            return False

    # DEVICES METHODS
    def add_device(self, device_data: Dict) -> int:
        """Add a new device to inventory."""
        query = """
        INSERT INTO devices (device_name, brand, model, category, serial_number, 
                           purchase_date, cost, location, description, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            device_data['device_name'], device_data['brand'], device_data['model'],
            device_data['category'], device_data['serial_number'], device_data['purchase_date'],
            device_data['cost'], device_data['location'], device_data.get('description', ''),
            device_data.get('image_path', '')
        )
        return self.execute_query(query, params)
    
    def get_devices(self, status: str = None) -> List[Dict]:
        """Get all devices or filter by status."""
        if status:
            query = "SELECT * FROM devices WHERE status = ? ORDER BY created_at DESC"
            params = (status,)
        else:
            query = "SELECT * FROM devices ORDER BY created_at DESC"
            params = ()
        
        rows = self.execute_query(query, params, fetch=True)
        return [dict(row) for row in rows]
    
    def update_device(self, device_id: int, device_data: Dict) -> None:
        """Update device information."""
        query = """
        UPDATE devices SET device_name=?, brand=?, model=?, category=?, 
                          cost=?, location=?, description=?, image_path=?, updated_at=?
        WHERE id=?
        """
        params = (
            device_data['device_name'], device_data['brand'], device_data['model'],
            device_data['category'], device_data['cost'], device_data['location'],
            device_data.get('description', ''), device_data.get('image_path', ''),
            datetime.now().isoformat(), device_id
        )
        self.execute_query(query, params)
    
    def sell_device(self, device_id: int, sale_data: Dict) -> None:
        """Mark device as sold and record sale."""
        # Update device status
        self.execute_query("UPDATE devices SET status='sold' WHERE id=?", (device_id,))
        
        # Record sale
        query = """
        INSERT INTO sales (device_id, sale_price, customer_name, customer_phone, 
                          sale_date, payment_method, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            device_id, sale_data['sale_price'], sale_data.get('customer_name', ''),
            sale_data.get('customer_phone', ''), sale_data['sale_date'],
            sale_data.get('payment_method', 'cash'), sale_data.get('notes', '')
        )
        self.execute_query(query, params)
    
    def search_devices(self, search_term: str) -> List[Dict]:
        """Search devices by name, brand, model, or description."""
        query = """
        SELECT * FROM devices 
        WHERE device_name LIKE ? OR brand LIKE ? OR model LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
        """
        search_pattern = f"%{search_term}%"
        params = (search_pattern, search_pattern, search_pattern, search_pattern)
        rows = self.execute_query(query, params, fetch=True)
        return [dict(row) for row in rows]
    
    def delete_device(self, device_id: int) -> None:
        """Delete a device from inventory."""
        self.execute_query("DELETE FROM devices WHERE id=?", (device_id,))
    
    # EMPLOYEES METHODS
    def add_employee(self, employee_data: Dict) -> int:
        """Add a new employee."""
        query = """
        INSERT INTO employees (employee_name, position, base_salary, phone, email, hire_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            employee_data['employee_name'], employee_data['position'],
            employee_data['base_salary'], employee_data.get('phone', ''),
            employee_data.get('email', ''), employee_data['hire_date']
        )
        return self.execute_query(query, params)
    
    def get_employees(self, active_only: bool = True) -> List[Dict]:
        """Get all employees."""
        if active_only:
            query = "SELECT * FROM employees WHERE is_active=1 ORDER BY employee_name"
        else:
            query = "SELECT * FROM employees ORDER BY employee_name"
        
        rows = self.execute_query(query, fetch=True)
        return [dict(row) for row in rows]
    
    def update_employee(self, employee_id: int, employee_data: Dict) -> bool:
        """Update employee information with enhanced field handling and validation."""
        from datetime import datetime, date
        
        try:
            # Build the query dynamically based on available fields
            update_fields = []
            params = []
            
            # Define all possible fields and their handling
            field_mappings = {
                'employee_name': 'employee_name',
                'position': 'position', 
                'department': 'department',
                'base_salary': 'base_salary',
                'phone': 'phone',
                'email': 'email',
                'hire_date': 'hire_date',
                'emergency_contact': 'emergency_contact',
                'is_active': 'is_active'
            }
            
            # Add fields that are present in employee_data
            for field_key, db_column in field_mappings.items():
                if field_key in employee_data:
                    value = employee_data[field_key]
                    
                    # Handle None values appropriately
                    if value is None or (isinstance(value, str) and value.strip() == ""):
                        if field_key in ['employee_name', 'position', 'base_salary', 'hire_date']:
                            # Required fields - skip if empty, will cause validation error
                            continue
                        else:
                            # Optional fields - set to NULL
                            update_fields.append(f"{db_column}=?")
                            params.append(None)
                    else:
                        update_fields.append(f"{db_column}=?")
                        params.append(value)
            
            # Always update the timestamp
            update_fields.append("updated_at=?")
            params.append(employee_data.get('updated_at', datetime.now().isoformat()))
            
            # Validate that we have required fields
            required_fields = ['employee_name', 'position', 'base_salary']
            for req_field in required_fields:
                if req_field not in employee_data or not employee_data[req_field]:
                    raise ValueError(f"Required field '{req_field}' is missing or empty")
            
            # Validate salary
            if 'base_salary' in employee_data:
                try:
                    salary = float(employee_data['base_salary'])
                    if salary < 0:
                        raise ValueError("Base salary cannot be negative")
                except (ValueError, TypeError):
                    raise ValueError("Base salary must be a valid number")
            
            # Validate hire_date if provided
            if 'hire_date' in employee_data and employee_data['hire_date']:
                try:
                    hire_date_obj = datetime.strptime(employee_data['hire_date'], "%Y-%m-%d").date()
                    if hire_date_obj > date.today():
                        raise ValueError("Hire date cannot be in the future")
                except ValueError as e:
                    if "time data" in str(e):
                        raise ValueError("Hire date must be in YYYY-MM-DD format")
                    raise
            
            # Build and execute the query
            if not update_fields:
                raise ValueError("No fields to update")
            
            query = f"UPDATE employees SET {', '.join(update_fields)} WHERE id=?"
            params.append(employee_id)
            
            # Execute the update
            cursor = self.execute_query(query, params)
            
            # Check if any rows were affected
            if cursor and hasattr(cursor, 'rowcount'):
                if cursor.rowcount == 0:
                    raise ValueError(f"No employee found with ID {employee_id}")
                elif cursor.rowcount > 1:
                    raise ValueError(f"Multiple employees updated (ID {employee_id}) - database integrity issue")
            
            return True
            
        except Exception as e:
            showerror("Error",f"Database error updating employee {employee_id}: {e}")
            raise e

    def get_employee_by_id(self, employee_id: int) -> Dict:
        """Get a single employee by ID for validation."""
        query = """
        SELECT id, employee_name, position, department, base_salary, phone, email, 
            hire_date, emergency_contact, is_active, created_at, updated_at
        FROM employees WHERE id=?
        """
        result = self.execute_query(query, (employee_id,), fetch_one=True)
        
        if result:
            columns = ['id', 'employee_name', 'position', 'department', 'base_salary', 
                    'phone', 'email', 'hire_date', 'emergency_contact', 'is_active', 
                    'created_at', 'updated_at']
            return dict(zip(columns, result))
        return None

    def validate_employee_data(self, employee_data: Dict, is_update: bool = False) -> Dict:
        """Validate employee data and return cleaned version."""
        from datetime import datetime, date
        
        cleaned_data = {}
        
        # Required fields for new employees
        required_fields = ['employee_name', 'position', 'base_salary', 'hire_date']
        
        # Validate required fields (only for new employees)
        if not is_update:
            for field in required_fields:
                if field not in employee_data or not employee_data[field]:
                    raise ValueError(f"Required field '{field}' is missing")
        
        # Clean and validate each field
        for field, value in employee_data.items():
            if field == 'employee_name':
                if value and len(value.strip()) > 0:
                    cleaned_data[field] = value.strip()
                elif not is_update:
                    raise ValueError("Employee name is required")
                    
            elif field == 'position':
                if value and len(value.strip()) > 0:
                    cleaned_data[field] = value.strip()
                elif not is_update:
                    raise ValueError("Position is required")
                    
            elif field == 'base_salary':
                if value is not None:
                    try:
                        salary = float(value)
                        if salary < 0:
                            raise ValueError("Salary cannot be negative")
                        cleaned_data[field] = salary
                    except (ValueError, TypeError):
                        raise ValueError("Base salary must be a valid number")
                elif not is_update:
                    raise ValueError("Base salary is required")
                    
            elif field == 'hire_date':
                if value:
                    try:
                        hire_date_obj = datetime.strptime(str(value), "%Y-%m-%d").date()
                        if hire_date_obj > date.today():
                            raise ValueError("Hire date cannot be in the future")
                        cleaned_data[field] = value
                    except ValueError as e:
                        if "time data" in str(e):
                            raise ValueError("Hire date must be in YYYY-MM-DD format")
                        raise
                elif not is_update:
                    raise ValueError("Hire date is required")
                    
            elif field in ['phone', 'email', 'department', 'emergency_contact']:
                # Optional fields - clean but allow empty
                cleaned_data[field] = value.strip() if value else None
                
            elif field == 'is_active':
                cleaned_data[field] = bool(value) if value is not None else True
                
            elif field in ['created_at', 'updated_at']:
                cleaned_data[field] = value
        
        return cleaned_data
    
    # PAYROLL METHODS
    def add_payroll_record(self, payroll_data: Dict) -> int:
        """Add a payroll record."""
        query = """
        INSERT INTO payroll (employee_id, month, year, base_salary, bonuses, 
                           deductions, total_salary, payment_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            payroll_data['employee_id'], payroll_data['month'], payroll_data['year'],
            payroll_data['base_salary'], payroll_data.get('bonuses', 0),
            payroll_data.get('deductions', 0), payroll_data['total_salary'],
            payroll_data.get('payment_date'), payroll_data.get('status', 'pending')
        )
        return self.execute_query(query, params)
    
    def get_payroll_records(self, month=None, year=None):
        """Get payroll records with optional month/year filtering."""
        query = """
            SELECT p.*, e.employee_name 
            FROM payroll p
            JOIN employees e ON p.employee_id = e.id
            WHERE 1=1
        """
        params = []
        
        if month is not None:
            query += " AND p.month = ?"
            params.append(month)
        
        if year is not None:
            query += " AND p.year = ?"
            params.append(year)
        
        query += " ORDER BY p.year DESC, p.month DESC, e.employee_name"
        
        records = self.execute_query(query, params, fetch=True)
        return [dict(row) for row in records] if records else []  # Always return a list
    
    # ATTENDANCE METHODS
    def add_attendance(self, attendance_data: Dict) -> int:
        """Add attendance record."""
        query = """
        INSERT OR REPLACE INTO attendance (employee_id, date, hours_worked, overtime_hours, notes)
        VALUES (?, ?, ?, ?, ?)
        """
        params = (
            attendance_data['employee_id'], attendance_data['date'],
            attendance_data.get('hours_worked', 8.0),
            attendance_data.get('overtime_hours', 0.0),
            attendance_data.get('notes', '')
        )
        return self.execute_query(query, params)
    
    def get_attendance_records(self, employee_id: int = None, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get attendance records with optional filters."""
        query = """
        SELECT a.*, e.employee_name 
        FROM attendance a 
        JOIN employees e ON a.employee_id = e.id
        """
        params = []
        conditions = []
        
        if employee_id:
            conditions.append("a.employee_id = ?")
            params.append(employee_id)
        
        if date_from:
            conditions.append("a.date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("a.date <= ?")
            params.append(date_to)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY a.date DESC, e.employee_name"
        
        rows = self.execute_query(query, tuple(params), fetch=True)
        return [dict(row) for row in rows]
    
    # SALES METHODS
    def get_sales_records(self, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Get sales records with optional date filtering."""
        query = """
        SELECT s.*, d.device_name, d.brand, d.model 
        FROM sales s 
        JOIN devices d ON s.device_id = d.id
        """
        params = []
        conditions = []
        
        if date_from:
            conditions.append("s.sale_date >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("s.sale_date <= ?")
            params.append(date_to)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY s.sale_date DESC"
        
        rows = self.execute_query(query, tuple(params), fetch=True)
        return [dict(row) for row in rows]
    
    # DOCUMENT ITEMS METHODS
    def add_document_items(self, document_id: str, items: List[Dict]) -> None:
        """Add items to a document."""
        query = """
        INSERT INTO document_items (document_id, device_name, description, quantity, 
                                  unit_cost, total_cost, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        for item in items:
            params = (
                document_id, item['device_name'], item.get('description', ''),
                item['quantity'], item['unit_cost'], item['total_cost'],
                item.get('image_path', '')
            )
            self.execute_query(query, params)
    
    def get_document_items(self, document_id: str) -> List[Dict]:
        """Get items for a specific document."""
        query = "SELECT * FROM document_items WHERE document_id=? ORDER BY id"
        rows = self.execute_query(query, (document_id,), fetch=True)
        return [dict(row) for row in rows]
    
    def delete_document_items(self, document_id: str) -> None:
        """Delete all items for a document."""
        self.execute_query("DELETE FROM document_items WHERE document_id=?", (document_id,))
    
    # UTILITY METHODS
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database."""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_company_db_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, backup_path)
        return backup_path
    
    # Additional methods needed in DatabaseManager class
    def get_payroll_record_by_id(self, payroll_id: int) -> Optional[Dict]:
        """Get a single payroll record by ID with employee name."""
        query = """
        SELECT p.*, e.employee_name 
        FROM payroll p
        JOIN employees e ON p.employee_id = e.id
        WHERE p.id = ?
        """
        row = self.execute_query(query, (payroll_id,), fetch=True)
        return dict(row[0]) if row else None

    def get_payroll_adjustments(self, payroll_id: int) -> List[Dict]:
        """Get all adjustments for a payroll record."""
        query = """
        SELECT * FROM payroll_adjustments
        WHERE payroll_id = ?
        ORDER BY adjustment_date DESC
        """
        rows = self.execute_query(query, (payroll_id,), fetch=True)
        return [dict(row) for row in rows]

    def get_dashboard_stats(self) -> Dict:
        """Get comprehensive statistics for the dashboard."""
        stats = {}
        
        # Employee stats
        stats['total_employees'] = self.execute_query(
            "SELECT COUNT(*) FROM employees", fetch=True)[0][0]
        stats['active_employees'] = self.execute_query(
            "SELECT COUNT(*) FROM employees WHERE is_active = 1", fetch=True)[0][0]
        stats['inactive_employees'] = stats['total_employees'] - stats['active_employees']
        
        # Department stats
        dept_stats = self.execute_query(
            "SELECT department, COUNT(*) FROM employees GROUP BY department", fetch=True)
        stats['department_stats'] = {dept: count for dept, count in dept_stats}
        
        # Salary stats
        salary_stats = self.execute_query(
            "SELECT AVG(base_salary), MAX(base_salary), MIN(base_salary) FROM employees WHERE is_active = 1", 
            fetch=True)[0]
        stats['avg_salary'] = salary_stats[0] or 0
        stats['max_salary'] = salary_stats[1] or 0
        stats['min_salary'] = salary_stats[2] or 0
        
        # Current month payroll stats
        current_month = datetime.now().month
        current_year = datetime.now().year
        payroll_stats = self.execute_query(
            "SELECT SUM(total_salary), COUNT(*) FROM payroll WHERE month = ? AND year = ?", 
            (current_month, current_year), fetch=True)[0]
        stats['monthly_payroll'] = payroll_stats[0] or 0
        stats['monthly_payroll_count'] = payroll_stats[1] or 0
        
        # Year-to-date payroll
        ytd_stats = self.execute_query(
            "SELECT SUM(total_salary) FROM payroll WHERE year = ?", 
            (current_year,), fetch=True)[0]
        stats['ytd_payroll'] = ytd_stats[0] or 0
        
        # Payroll status counts
        status_stats = self.execute_query(
            "SELECT status, COUNT(*) FROM payroll GROUP BY status", fetch=True)
        stats['pending_payroll'] = sum(count for status, count in status_stats if status.lower() == 'pending')
        stats['paid_payroll'] = sum(count for status, count in status_stats if status.lower() == 'paid')
        
        return stats
