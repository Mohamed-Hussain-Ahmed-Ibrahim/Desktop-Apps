import sys
import sqlite3
import datetime
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
                            QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QDialog, 
                            QFormLayout, QDialogButtonBox, QCheckBox, QTabWidget, QTextEdit,
                            QFrame, QSplitter, QDateEdit, QHeaderView)
from PyQt5.QtGui import QFont, QIcon, QTextDocument
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction

class DrinkDialog(QDialog):
    """Dialog for adding or editing a drink"""
    def __init__(self, drink_name="", drink_price=0.0, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Drink")
        self.setMinimumWidth(300)
        
        # Layout
        layout = QFormLayout(self)
        
        # Drink name input
        self.name_input = QLineEdit(drink_name)
        layout.addRow("Drink Name:", self.name_input)
        
        # Drink price input
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0, 1000.0)
        self.price_input.setSingleStep(0.5)
        self.price_input.setDecimals(2)
        self.price_input.setValue(drink_price)
        layout.addRow("Price:", self.price_input)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addRow(self.buttons)
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
    
    def get_data(self):
        return {
            "name": self.name_input.text(),
            "price": self.price_input.value()
        }


class OrderItemDialog(QDialog):
    """Dialog for adding an item to the order"""
    def __init__(self, drinks_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Item to Order")
        self.setMinimumWidth(300)
        
        # Store drinks data
        self.drinks_data = drinks_data
        
        # Layout
        layout = QFormLayout(self)
        
        # Drink selector
        self.drink_combo = QComboBox()
        for drink in drinks_data:
            self.drink_combo.addItem(f"{drink['name']} - ${drink['price']:.2f}", drink)
        layout.addRow("Drink:", self.drink_combo)
        
        # Quantity selector
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        self.quantity_spin.setValue(1)
        layout.addRow("Quantity:", self.quantity_spin)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addRow(self.buttons)
        
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
    
    def get_data(self):
        selected_drink = self.drinks_data[self.drink_combo.currentIndex()]
        return {
            "drink_id": selected_drink["id"],
            "name": selected_drink["name"],
            "price": selected_drink["price"],
            "quantity": self.quantity_spin.value(),
            "total": selected_drink["price"] * self.quantity_spin.value()
        }


class OrderDetailsDialog(QDialog):
    """Dialog to display order details"""
    def __init__(self, order_data, items_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Order #{order_data['id']} Details")
        self.setMinimumSize(500, 600)
        
        # Store order data
        self.order_data = order_data
        self.items_data = items_data
        
        # Layout
        main_layout = QVBoxLayout(self)
        
        # Order info section
        info_layout = QFormLayout()
        
        order_id_label = QLabel(f"#{order_data['id']}")
        info_layout.addRow("Order ID:", order_id_label)
        
        table_label = QLabel(f"{order_data['table_number']}")
        info_layout.addRow("Table:", table_label)
        
        timestamp_label = QLabel(order_data['timestamp'])
        info_layout.addRow("Time:", timestamp_label)
        
        tax_status = "Yes" if order_data['tax_included'] else "No"
        tax_label = QLabel(tax_status)
        info_layout.addRow("Tax Included:", tax_label)
        
        total_label = QLabel(f"${order_data['total']:.2f}")
        total_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_layout.addRow("Total:", total_label)
        
        main_layout.addLayout(info_layout)
        
        # Add a divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(divider)
        
        # Items section
        items_label = QLabel("Order Items")
        items_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(items_label)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity", "Total"])
        self.items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate items
        self.items_table.setRowCount(len(items_data))
        for row, item in enumerate(items_data):
            self.items_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.items_table.setItem(row, 1, QTableWidgetItem(f"${item['price']:.2f}"))
            self.items_table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            item_total = item["price"] * item["quantity"]
            self.items_table.setItem(row, 3, QTableWidgetItem(f"${item_total:.2f}"))
        
        self.items_table.resizeColumnsToContents()
        main_layout.addWidget(self.items_table)
        
        # Bill View
        bill_label = QLabel("Bill View")
        bill_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(bill_label)
        
        self.bill_view = QTextEdit()
        self.bill_view.setReadOnly(True)
        self.bill_view.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.bill_view)
        
        # Generate bill HTML
        self.generate_bill_view()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        print_btn = QPushButton("Print")
        print_btn.clicked.connect(self.print_bill)
        buttons_layout.addWidget(print_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        main_layout.addLayout(buttons_layout)
    
    def generate_bill_view(self):
        """Generate the bill view HTML in Egyptian café style with 12-hr format"""
        # Calculate totals
        subtotal = sum(item["price"] * item["quantity"] for item in self.items_data)
        tax_rate = 0.14  # 14% tax
        tax_amount = subtotal * tax_rate if self.order_data["tax_included"] else 0
        
        # Format current time in 12-hour format
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
        
        # Generate random server name (for consistency with the original bill)
        server_names = ["احمد", "محمد", "فاطمة", "عمر", "مريم"]
        random.seed(self.order_data["id"])  # Use order ID as seed for consistent server name
        server_name = random.choice(server_names)
        
        # Build HTML content
        html_content = f"""
        <html>
        <head>
            <style>
               
                body {{  
                    margin: 0; 
                    padding: 20px;
                    background-color: #fff;
                    color: #333;
                    direction: rtl;
                    max-width: 380px;
                    margin: 0 auto;
                }}
                .receipt-header {{ 
                    text-align: center;
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                    margin-bottom: 10px;
                }}
                .logo {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                    color: #4CAF50;
                }}
                .receipt-info {{ 
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    margin: 15px 0;
                }}
                .receipt-info div {{ 
                    text-align: center;
                    flex: 1;
                }}
                .receipt-title {{
                    text-align: center;
                    font-weight: bold;
                    margin: 15px 0;
                    font-size: 16px;
                    border-bottom: 1px solid #000;
                    padding-bottom: 5px;
                }}
                .item-row {{ 
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px dotted #aaa;
                    font-size: 12px;
                    align-items: center;
                }}
                .item-name {{ 
                    flex: 2; 
                    display: flex;
                    align-items: center;
                }}
                .item-image {{
                    width: 30px;
                    height: 30px;
                    object-fit: cover;
                    border-radius: 3px;
                    margin-left: 5px;
                }}
                .item-qty {{ 
                    flex: 0.5; 
                    text-align: center;
                }}
                .item-price {{ 
                    flex: 0.8; 
                    text-align: center;
                }}
                .item-total {{ 
                    flex: 0.8; 
                    text-align: left;
                    font-weight: bold;
                }}
                .header-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #000;
                    font-weight: bold;
                    font-size: 12px;
                }}
                .totals {{ 
                    margin-top: 15px;
                }}
                .total-row {{ 
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                    font-weight: normal;
                    font-size: 13px;
                }}
                .grand-total {{ 
                    font-weight: bold;
                    font-size: 16px;
                    color: #4CAF50;
                    border-top: 1px solid #000;
                    border-bottom: 1px solid #000;
                    padding: 5px 0;
                    margin-top: 5px;
                }}
                .footer {{ 
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    border-top: 1px solid #000;
                    padding-top: 10px;
                }}
                .footer-msg {{ 
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .contact {{ 
                    font-size: 10px;
                    margin-top: 10px;
                }}
                .server {{ 
                    text-align: left; 
                    margin-top: 10px; 
                    font-size: 12px; 
                    color: #888; 
                }}
                .thick-divider {{ 
                    border-top: 2px solid #000; 
                    margin: 15px 0; 
                }}
            </style>
        </head>
        <body>
            <div class="receipt-header">
                <div class="logo">☕ احلى الاوقات</div>
                <div>AHLA EL AWKAT CAFE</div>
            </div>
            
            <div class="receipt-info">
                <div>
                    <strong>التاريخ:</strong><br>
                    {date_str}
                </div>
                <div>
                    <strong>الوقت:</strong><br>
                    {time_str}
                </div>
                <div>
                    <strong>رقم الفاتورة:</strong><br>
                    BILL-{self.order_data['id']}
                </div>
                <div>
                    <strong>طاولة:</strong><br>
                    {self.order_data['table_number']}
                </div>
            </div>
            
            <div class="receipt-title">فاتورة مبيعات</div>
            
            <div class="header-row">
                <div class="item-name">الصنف</div>
                <div class="item-qty">العدد</div>
                <div class="item-price">السعر</div>
                <div class="item-total">الإجمالي</div>
            </div>
        """
        
        # Add items with optional image
        for item in self.items_data:
            item_total = item["price"] * item["quantity"]
            # If the item has an image (you could modify your data to include image URL)
            item_image = f'<img src="{item.get("image_url", "default_image.png")}" class="item-image" />'
            html_content += f"""
            <div class="item-row">
                <div class="item-name">{item_image} {item['name']}</div>
                <div class="item-qty">{item['quantity']}</div>
                <div class="item-price">${item['price']:.2f}</div>
                <div class="item-total">${item_total:.2f}</div>
            </div>
            """
        
        html_content += f"""
            <div class="thick-divider"></div>
            
            <div class="totals">
                <div class="total-row">
                    <span>المجموع الفرعي:</span>
                    <span>${subtotal:.2f}</span>
                </div>
        """
        
        if self.order_data["tax_included"]:
            html_content += f"""
                <div class="total-row">
                    <span>الضريبة (14%):</span>
                    <span>${tax_amount:.2f}</span>
                </div>
            """
        
        html_content += f"""
                <div class="total-row grand-total">
                    <span>الإجمالي:</span>
                    <span>${self.order_data['total']:.2f}</span>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-msg">شكراً لزيارتكم!</div>
                <div>نتمنى لكم تجربة ممتعة</div>
                <div class="contact">
                    ت: 01148633508<br>
                   ahla-elawkat
                </div>
            </div>
            
            <div class="server">
                الخادم: {server_name}
            </div>
            
        </body>
        </html>
        """
        
        self.bill_view.setHtml(html_content)
    
    def print_bill(self):
        """Print the bill"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QDialog.Accepted:
            self.bill_view.print_(printer)
            QMessageBox.information(self, "Print Success", "Bill sent to printer")


class BillPreviewDialog(QDialog):
    """Enhanced Bill Preview Dialog"""
    def __init__(self, order_data, table_number, tax_included, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bill Preview")
        self.setMinimumSize(450, 600)
        
        # Store order data
        self.order_data = order_data
        self.table_number = table_number
        self.tax_included = tax_included
        self.tax_rate = 0.14  # 14% tax
        
        # Generate random bill number and server name
        now = datetime.datetime.now()
        self.bill_number = f"BILL-{now.strftime('%Y%m%d%H%M%S')}"
        
        server_names = ["احلى الاوقات", "احلى الاوقات", "احلى الاوقات"]
        self.server_name = random.choice(server_names)
        
        # Create layout
        main_layout = QVBoxLayout(self)
        
        # Bill content
        self.bill_content = QTextEdit()
        self.bill_content.setReadOnly(True)
        self.bill_content.setStyleSheet("background-color: white;")
        self.bill_content.setFont(QFont("Courier New", 10))
        main_layout.addWidget(self.bill_content)
        
        # Generate bill
        self.generate_bill()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.print_btn = QPushButton("Print Bill")
        self.print_btn.clicked.connect(self.print_bill)
        button_layout.addWidget(self.print_btn)
        
        self.save_btn = QPushButton("Save & Close")
        self.save_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
    
    def generate_bill(self):
        """Generate a professional bill content in Egyptian café-style"""
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%I:%M %p")  # 12-hour format with AM/PM
        
        # Calculate totals
        subtotal = sum(item["quantity"] * item["price"] for item in self.order_data)
        tax_amount = subtotal * self.tax_rate if self.tax_included else 0
        grand_total = subtotal + tax_amount
        
        # Build HTML content for bill
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 20px;
                    background-color: #fff;
                    color: #333;
                    direction: rtl;
                    max-width: 380px;
                    margin: 0 auto;
                }}
                .receipt-header {{ 
                    text-align: center;
                    border-bottom: 2px solid #000;
                    padding-bottom: 10px;
                    margin-bottom: 10px;
                }}
                .logo {{ 
                    font-size: 24px; 
                    font-weight: bold; 
                    margin-bottom: 5px;
                    color: #000;
                }}
                .receipt-info {{ 
                    display: flex;
                    justify-content: space-between;
                    font-size: 12px;
                    margin: 15px 0;
                }}
                .receipt-info div {{ 
                    text-align: center;
                    flex: 1;
                }}
                .receipt-title {{
                    text-align: center;
                    font-weight: bold;
                    margin: 15px 0;
                    font-size: 16px;
                    border-bottom: 1px solid #000;
                    padding-bottom: 5px;
                }}
                .items-table {{ 
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 15px;
                }}
                .items-table th {{ 
                    border-bottom: 1px solid #000;
                    padding: 5px;
                    text-align: right;
                    font-size: 12px;
                }}
                .items-table td {{ 
                    padding: 5px 0;
                    font-size: 12px;
                    border-bottom: 1px dotted #aaa;
                }}
                .price-col {{ 
                    text-align: left;
                }}
                .qty-col {{ 
                    text-align: center;
                }}
                .item-total {{ 
                    text-align: left;
                }}
                .totals {{ 
                    margin-top: 15px;
                }}
                .total-row {{ 
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                    font-weight: normal;
                    font-size: 12px;
                }}
                .grand-total {{ 
                    font-weight: bold;
                    font-size: 14px;
                    border-top: 1px solid #000;
                    border-bottom: 1px solid #000;
                    padding: 5px 0;
                    margin-top: 5px;
                }}
                .footer {{ 
                    text-align: center;
                    margin-top: 20px;
                    font-size: 12px;
                    border-top: 1px solid #000;
                    padding-top: 10px;
                }}
                .footer-msg {{ 
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .contact {{ 
                    font-size: 10px;
                    margin-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="receipt-header">
                <div class="logo">☕ احلى الاوقات</div>
                <div>AHLA EL AWKAT CAFE</div>
            </div>
            
            <div class="receipt-info">
                <div>
                    <strong>التاريخ:</strong><br>
                    {date_str}
                </div>
                <div>
                    <strong>الوقت:</strong><br>
                    {time_str}
                </div>
                <div>
                    <strong>رقم الفاتورة:</strong><br>
                    {self.bill_number}
                </div>
                <div>
                    <strong>طاولة:</strong><br>
                    {self.table_number}
                </div>
            </div>
            
            <div class="receipt-title">فاتورة مبيعات</div>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 50%;">الصنف</th>
                        <th class="qty-col" style="width: 15%;">العدد</th>
                        <th class="price-col" style="width: 15%;">السعر</th>
                        <th class="item-total" style="width: 20%;">الإجمالي</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add items
        for item in self.order_data:
            item_total = item["price"] * item["quantity"]
            html_content += f"""
                    <tr>
                        <td>{item['name']}</td>
                        <td class="qty-col">{item['quantity']}</td>
                        <td class="price-col">${item['price']:.2f}</td>
                        <td class="item-total">${item_total:.2f}</td>
                    </tr>
            """
        
        html_content += f"""
                </tbody>
            </table>
            
            <div class="totals">
                <div class="total-row">
                    <span>المجموع الفرعي:</span>
                    <span>${subtotal:.2f}</span>
                </div>
        """
        
        if self.tax_included:
            html_content += f"""
                <div class="total-row">
                    <span>الضريبة (14%):</span>
                    <span>${tax_amount:.2f}</span>
                </div>
            """
        
        html_content += f"""
                <div class="total-row grand-total">
                    <span>الإجمالي:</span>
                    <span>${grand_total:.2f}</span>
                </div>
            </div>
            
            <div class="footer">
                <div class="footer-msg">شكراً لزيارتكم!</div>
                <div>نتمنى لكم تجربة ممتعة</div>
                <div class="contact">
                    ت: 01148633508<br>
                    ahla-elawkat
                </div>
            </div>
            
        </body>
        </html>
        """
        
        self.bill_content.setHtml(html_content)
    
    def print_bill(self):
        """Print the bill"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QDialog.Accepted:
            self.bill_content.print_(printer)
            QMessageBox.information(self, "Print Success", "Bill sent to printer")


class CafeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("احلى الاوقات")
        self.setMinimumSize(1000, 700)

        # Initialize database
        self.init_database()

        # Setup UI
        self.setup_ui()

        # Add Menu Bar
        self.setup_menu_bar()

        # Load initial data
        self.load_drinks()
        self.load_orders()

        # Initialize order tracking by table
        self.table_orders = {}  # Dictionary to track orders by table number
        self.current_order_items = []
        self.previous_table = None

        # Connect table selection signal
        self.table_input.currentTextChanged.connect(self.table_changed)

    def table_changed(self, table_number):
        """Handle when a different table is selected"""
        if not table_number.strip():
            return
    
        # Save current order items to table_orders before switching if any items exist
        if self.previous_table and self.current_order_items:
            self.table_orders[self.previous_table] = self.current_order_items.copy()
    
        # Clear the current order items when switching to a new table
        self.current_order_items = []
    
        # Load saved items for the newly selected table (if any)
        if table_number in self.table_orders:
            self.current_order_items = self.table_orders[table_number].copy()
    
        # Update the previous table reference
        self.previous_table = table_number
    
        # Refresh the UI to display the correct items for the selected table
        self.update_order_items_table()

    def add_order_item(self):
        """Add item to current order"""
        # Get all drinks
        self.cursor.execute("SELECT id, name, price FROM drinks ORDER BY name")
        drinks = [{"id": row[0], "name": row[1], "price": row[2]} for row in self.cursor.fetchall()]
    
        if not drinks:
            QMessageBox.warning(self, "Error", "No drinks available. Add some drinks first.")
            return
    
        dialog = OrderItemDialog(drinks, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            item_data = dialog.get_data()
    
            # Check if the item already exists, update quantity if needed
            for i, existing_item in enumerate(self.current_order_items):
                if existing_item["drink_id"] == item_data["drink_id"]:
                    self.current_order_items[i]["quantity"] += item_data["quantity"]
                    self.current_order_items[i]["total"] = self.current_order_items[i]["price"] * self.current_order_items[i]["quantity"]
                    break
            else:
                self.current_order_items.append(item_data)
    
            # Save the updated order for the current table in table_orders
            table_number = self.table_input.currentText()
            if table_number.strip():
                self.table_orders[table_number] = self.current_order_items.copy()
    
            self.update_order_items_table()

    def remove_order_item(self, row):
        """Remove item from current order"""
        if 0 <= row < len(self.current_order_items):
            del self.current_order_items[row]
            self.update_order_items_table()
    
            # Update the table_orders dictionary after removing an item
            table_number = self.table_input.currentText()
            if table_number.strip():
                if self.current_order_items:
                    self.table_orders[table_number] = self.current_order_items.copy()
                else:
                    del self.table_orders[table_number]  # Remove the table entry if no items remain

    def save_order(self):
        """Save the current order to database"""
        if not self.current_order_items:
            QMessageBox.warning(self, "Error", "Cannot save empty order")
            return
        
        table_number = self.table_input.currentText()
        if not table_number.strip():
            QMessageBox.warning(self, "Error", "Please specify a table number")
            return
        
        # Calculate total
        subtotal = sum(item["total"] for item in self.current_order_items)
        tax_included = self.tax_checkbox.isChecked()
        tax_rate = 0.14  # 14% tax
        tax_amount = subtotal * tax_rate if tax_included else 0
        total = subtotal + tax_amount
        
        # Show bill preview
        preview_dialog = BillPreviewDialog(self.current_order_items, table_number, tax_included, parent=self)
        if preview_dialog.exec_() != QDialog.Accepted:
            return
        
        # Save order
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.cursor.execute(
            "INSERT INTO orders (table_number, timestamp, total, tax_included) VALUES (?, ?, ?, ?)",
            (table_number, timestamp, total, tax_included)
        )
        order_id = self.cursor.lastrowid
        
        # Save order items
        for item in self.current_order_items:
            self.cursor.execute(
                "INSERT INTO order_items (order_id, drink_id, quantity) VALUES (?, ?, ?)",
                (order_id, item["drink_id"], item["quantity"])
            )
        
        self.conn.commit()
        
        # Clear current order and remove from table tracking
        self.current_order_items = []
        if table_number in self.table_orders:
            del self.table_orders[table_number]
        self.update_order_items_table()
        
        # Refresh orders list
        self.load_orders()

    def clear_current_order(self):
        """Clear all items from current order"""
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear the current order?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            table_number = self.table_input.currentText()
            self.current_order_items = []
            
            # Also remove from table tracking
            if table_number in self.table_orders:
                del self.table_orders[table_number]
                
            self.update_order_items_table()

    def setup_menu_bar(self):
        """Create and configure the menu bar"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_order_action = QAction("New Order", self)
        new_order_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        file_menu.addAction(new_order_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Manage Menu
        manage_menu = menubar.addMenu("&Manage")

        manage_drinks_action = QAction("Manage Drinks", self)
        manage_drinks_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        manage_menu.addAction(manage_drinks_action)

        manage_orders_action = QAction("Order History", self)
        manage_orders_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        manage_menu.addAction(manage_orders_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        """Show the about dialog with additional details and styling."""
        about_text = """
        <h2 style="color: #D35400; text-align: center;">☕ احلى الاوقات</h2>
        <p style="text-align: center;"><strong>Version:</strong> 1.0.0</p>
        
        <h3 style="color: #A04000;">About:</h3>
        <p>A simple yet powerful system designed to manage café orders, billing, and inventory efficiently.</p>
        
        <h3 style="color: #A04000;">Features:</h3>
        <ul>
            <li>✔ Order Management</li>
            <li>✔ Bill Printing & Receipts</li>
            <li>✔ Tax Inclusion Options</li>
            <li>✔ Table Number Assignment</li>
            <li>✔ Sales Reporting & History</li>
            <li>✔ Drink Inventory Management</li>
        </ul>
        
        <p><strong>Support & Contact:</strong></p>
        <p><strong>Email:</strong> support@cafemanager.com</p>
        <p><strong>Website:</strong> <a href="https://cafemanager.com">cafemanager.com</a></p>
        
        <p style="color: #D35400; text-align: center;">© 2025 - Developed by <strong>Mohamed Hussien</strong></p>
        """
        
        QMessageBox.about(self, "About Café Manager", about_text)
    
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect("cafe_manager.db")
        self.cursor = self.conn.cursor()
        
        # Create drinks table if not exists
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS drinks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL
        )
        ''')
        
        # Create orders table if not exists
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total REAL NOT NULL,
            tax_included INTEGER NOT NULL
        )
        ''')
        
        # Create order_items table if not exists
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            drink_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (drink_id) REFERENCES drinks (id)
        )
        ''')
        
        # Add some sample drinks if the table is empty
        self.cursor.execute("SELECT COUNT(*) FROM drinks")
        if self.cursor.fetchone()[0] == 0:
            sample_drinks = [
                ("Espresso", 3.50),
                ("Cappuccino", 4.50),
                ("Latte", 4.75),
                ("Americano", 3.75),
                ("Mocha", 5.00),
                ("Hot Chocolate", 4.25),
                ("Iced Coffee", 4.00),
                ("Tea", 3.00),
                ("Macchiato", 4.25),
                ("Flat White", 4.50)
            ]
            self.cursor.executemany("INSERT INTO drinks (name, price) VALUES (?, ?)", sample_drinks)
            self.conn.commit()
    
    def setup_ui(self):
        """Setup the main UI components"""
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create left and right panels
        left_panel = QWidget()
        right_panel = QWidget()
        
        # Tab widget for right panel
        self.tabs = QTabWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.addWidget(self.tabs)
        
        # Create order management tab
        order_tab = QWidget()
        order_layout = QVBoxLayout(order_tab)
        
        # New order section
        new_order_frame = QFrame()
        new_order_frame.setFrameShape(QFrame.StyledPanel)
        new_order_layout = QVBoxLayout(new_order_frame)
        
        # New order header
        new_order_header = QLabel("New Order")
        new_order_header.setFont(QFont("Arial", 14, QFont.Bold))
        new_order_layout.addWidget(new_order_header)
        
        # Table number input
        table_layout = QHBoxLayout()
        table_label = QLabel("Table Number:")
        self.table_input = QComboBox()
        self.table_input.addItems([f"Table {i}" for i in range(1, 101)])
        self.table_input.setEditable(True)
        self.table_input.setCurrentText("")
        table_layout.addWidget(table_label)
        table_layout.addWidget(self.table_input)
        new_order_layout.addLayout(table_layout)
        
        # Tax included checkbox
        self.tax_checkbox = QCheckBox("Include Tax (14%)")
        self.tax_checkbox.setChecked(True)
        new_order_layout.addWidget(self.tax_checkbox)
        
        # Current order items table
        self.order_items_table = QTableWidget()
        self.order_items_table.setColumnCount(5)
        self.order_items_table.setHorizontalHeaderLabels(["Item", "Price", "Quantity", "Total", "Actions"])
        self.order_items_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        new_order_layout.addWidget(self.order_items_table)
        
        # Order actions
        actions_layout = QHBoxLayout()
        
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.add_order_item)
        actions_layout.addWidget(self.add_item_button)
        
        self.clear_order_button = QPushButton("Clear")
        self.clear_order_button.clicked.connect(self.clear_current_order)
        actions_layout.addWidget(self.clear_order_button)
        
        self.save_order_button = QPushButton("Save Order")
        self.save_order_button.clicked.connect(self.save_order)
        self.save_order_button.setFont(QFont("Arial", 10, QFont.Bold))
        actions_layout.addWidget(self.save_order_button)
        
        new_order_layout.addLayout(actions_layout)
        
        # Order total
        self.order_total_label = QLabel("Total: $0.00")
        self.order_total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.order_total_label.setAlignment(Qt.AlignRight)
        new_order_layout.addWidget(self.order_total_label)
        
        order_layout.addWidget(new_order_frame)
        
        # Create drinks management tab
        drinks_tab = QWidget()
        drinks_layout = QVBoxLayout(drinks_tab)
        
        # Drinks table
        self.drinks_table = QTableWidget()
        self.drinks_table.setColumnCount(3)
        self.drinks_table.setHorizontalHeaderLabels(["Name", "Price", "Actions"])
        self.drinks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.drinks_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        drinks_layout.addWidget(self.drinks_table)
        
        # Drinks actions
        drinks_actions = QHBoxLayout()
        
        self.add_drink_button = QPushButton("Add Drink")
        self.add_drink_button.clicked.connect(self.add_drink)
        drinks_actions.addWidget(self.add_drink_button)
        
        drinks_layout.addLayout(drinks_actions)
        
        # Create orders history tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # Date filter
        date_filter_layout = QHBoxLayout()
        date_filter_layout.addWidget(QLabel("Filter by Date:"))
        
        self.date_filter = QDateEdit()
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDate(QDate.currentDate())
        date_filter_layout.addWidget(self.date_filter)
        
        self.apply_filter_btn = QPushButton("Apply")
        self.apply_filter_btn.clicked.connect(self.filter_orders)
        date_filter_layout.addWidget(self.apply_filter_btn)
        
        self.clear_filter_btn = QPushButton("Clear Filter")
        self.clear_filter_btn.clicked.connect(self.load_orders)
        date_filter_layout.addWidget(self.clear_filter_btn)
        
        date_filter_layout.addStretch()
        history_layout.addLayout(date_filter_layout)
        
        # Orders table
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Table", "Time", "Total", "Actions"])
        self.orders_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.orders_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        history_layout.addWidget(self.orders_table)
        
        # Add tabs
        self.tabs.addTab(order_tab, "New Order")
        self.tabs.addTab(drinks_tab, "Manage Drinks")
        self.tabs.addTab(history_tab, "Order History")
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Create left panel content - statistics and quick actions
        left_layout = QVBoxLayout(left_panel)
        
        # App logo/title
        logo_label = QLabel("☕ احلى الاوقات")
        logo_label.setFont(QFont("Arial", 20, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label)
        
        # Current date display
        today = datetime.datetime.now().strftime("%A, %B %d, %Y")
        date_label = QLabel(today)
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setFont(QFont("Arial", 10))
        left_layout.addWidget(date_label)
        
        # Add divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(divider)
        
        # Quick stats section
        stats_label = QLabel("Today's Stats")
        stats_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(stats_label)
        
        # Stats layout
        stats_layout = QFormLayout()
        
        self.orders_count_label = QLabel("0")
        stats_layout.addRow("Total Orders:", self.orders_count_label)
        
        self.total_sales_label = QLabel("$0.00")
        stats_layout.addRow("Total Sales:", self.total_sales_label)
        
        self.avg_order_label = QLabel("$0.00")
        stats_layout.addRow("Average Order:", self.avg_order_label)
        
        left_layout.addLayout(stats_layout)
        
        # Add another divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.HLine)
        divider2.setFrameShadow(QFrame.Sunken)
        left_layout.addWidget(divider2)
        
        # Quick actions section
        quick_actions_label = QLabel("Quick Actions")
        quick_actions_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(quick_actions_label)
        
        # Quick buttons
        new_order_btn = QPushButton("New Order")
        new_order_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(0))
        left_layout.addWidget(new_order_btn)
        
        view_drinks_btn = QPushButton("Manage Drinks")
        view_drinks_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        left_layout.addWidget(view_drinks_btn)
        
        view_history_btn = QPushButton("Order History")
        view_history_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        left_layout.addWidget(view_history_btn)
        
        # Refresh stats button
        refresh_stats_btn = QPushButton("Refresh Stats")
        refresh_stats_btn.clicked.connect(self.update_statistics)
        left_layout.addWidget(refresh_stats_btn)
        
        left_layout.addStretch()
    
    def load_drinks(self):
        """Load drinks from database into table"""
        self.ensure_connection()  # Ensure the connection is open
        self.cursor.execute("SELECT id, name, price FROM drinks ORDER BY name")
        drinks = self.cursor.fetchall()
        
        self.drinks_table.setRowCount(len(drinks))
        for row, (drink_id, name, price) in enumerate(drinks):
            self.drinks_table.setItem(row, 0, QTableWidgetItem(name))
            self.drinks_table.setItem(row, 1, QTableWidgetItem(f"${price:.2f}"))
            
            # Create actions cell with edit and delete buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(QSize(60, 25))
            edit_btn.clicked.connect(lambda _, d_id=drink_id, d_name=name, d_price=price: self.edit_drink(d_id, d_name, d_price))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(QSize(60, 25))
            delete_btn.clicked.connect(lambda _, d_id=drink_id, d_name=name: self.delete_drink(d_id, d_name))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setSpacing(5)
            
            self.drinks_table.setCellWidget(row, 2, actions_widget)
        
        self.drinks_table.resizeColumnsToContents()
        
    def get_drinks(self):
        """Fetch all drinks safely"""
        with sqlite3.connect("cafe_manager.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price FROM drinks ORDER BY name")
            return cursor.fetchall()

    def load_orders(self):
        """Load orders from database into table"""
        self.cursor.execute("SELECT id, table_number, timestamp, total, tax_included FROM orders ORDER BY id DESC")
        orders = self.cursor.fetchall()
        
        self.orders_table.setRowCount(len(orders))
        for row, (order_id, table, timestamp, total, tax_included) in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.orders_table.setItem(row, 1, QTableWidgetItem(table))
            self.orders_table.setItem(row, 2, QTableWidgetItem(timestamp))
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"${total:.2f}"))
            
            # Create actions cell with view and delete buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("View")
            view_btn.setFixedSize(QSize(60, 25))
            view_btn.clicked.connect(lambda _, o_id=order_id: self.view_order(o_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(QSize(60, 25))
            delete_btn.clicked.connect(lambda _, o_id=order_id: self.delete_order(o_id))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setSpacing(5)
            
            self.orders_table.setCellWidget(row, 4, actions_widget)
        
        self.orders_table.resizeColumnsToContents()
        
        # Update statistics
        self.update_statistics()
    
    def update_statistics(self):
        """Update statistics display"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Get today's orders count
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE timestamp LIKE ?", (f"{today}%",))
        orders_count = self.cursor.fetchone()[0]
        self.orders_count_label.setText(str(orders_count))
        
        # Get today's total sales
        self.cursor.execute("SELECT SUM(total) FROM orders WHERE timestamp LIKE ?", (f"{today}%",))
        total_sales = self.cursor.fetchone()[0] or 0
        self.total_sales_label.setText(f"${total_sales:.2f}")
        
        # Calculate average order value
        avg_order = total_sales / orders_count if orders_count > 0 else 0
        self.avg_order_label.setText(f"${avg_order:.2f}")
    
    def add_drink(self):
        """Add a new drink"""
        dialog = DrinkDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate data
            if not data["name"].strip():
                QMessageBox.warning(self, "Error", "Drink name cannot be empty")
                return
            
            try:
                self.cursor.execute(
                    "INSERT INTO drinks (name, price) VALUES (?, ?)",
                    (data["name"], data["price"])
                )
                self.conn.commit()
                self.load_drinks()
                QMessageBox.information(self, "Success", f"Drink '{data['name']}' added successfully")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", f"Drink with name '{data['name']}' already exists")
    
    def edit_drink(self, drink_id, name, price):
        """Edit an existing drink"""
        dialog = DrinkDialog(drink_name=name, drink_price=price, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate data
            if not data["name"].strip():
                QMessageBox.warning(self, "Error", "Drink name cannot be empty")
                return
            
            try:
                self.cursor.execute(
                    "UPDATE drinks SET name = ?, price = ? WHERE id = ?",
                    (data["name"], data["price"], drink_id)
                )
                self.conn.commit()
                self.load_drinks()
                QMessageBox.information(self, "Success", f"Drink '{data['name']}' updated successfully")
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Error", f"Drink with name '{data['name']}' already exists")
    
    def delete_drink(self, drink_id, name):
        """Delete a drink"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Check if drink is used in any orders
            self.cursor.execute("SELECT COUNT(*) FROM order_items WHERE drink_id = ?", (drink_id,))
            used_count = self.cursor.fetchone()[0]
            
            if used_count > 0:
                reply = QMessageBox.warning(
                    self, "Warning",
                    f"This drink is used in {used_count} orders. Deleting it may cause issues with order history. Continue?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                
                if reply != QMessageBox.Yes:
                    return
            
            self.cursor.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))
            self.conn.commit()
            self.load_drinks()
            QMessageBox.information(self, "Success", f"Drink '{name}' deleted successfully")
    
    def add_order_item(self):
        """Add item to current order"""
        # Get all drinks
        self.cursor.execute("SELECT id, name, price FROM drinks ORDER BY name")
        drinks = [{"id": row[0], "name": row[1], "price": row[2]} for row in self.cursor.fetchall()]
        
        if not drinks:
            QMessageBox.warning(self, "Error", "No drinks available. Add some drinks first.")
            return
        
        dialog = OrderItemDialog(drinks, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            item_data = dialog.get_data()
            
            # Check if drink already in order, if so, update quantity
            for i, existing_item in enumerate(self.current_order_items):
                if existing_item["drink_id"] == item_data["drink_id"]:
                    new_qty = existing_item["quantity"] + item_data["quantity"]
                    self.current_order_items[i]["quantity"] = new_qty
                    self.current_order_items[i]["total"] = existing_item["price"] * new_qty
                    self.update_order_items_table()
                    return
            
            # Otherwise add new item
            self.current_order_items.append(item_data)
            self.update_order_items_table()
    
    def update_order_items_table(self):
        """Update the current order items table"""
        self.order_items_table.setRowCount(len(self.current_order_items))
        
        for row, item in enumerate(self.current_order_items):
            self.order_items_table.setItem(row, 0, QTableWidgetItem(item["name"]))
            self.order_items_table.setItem(row, 1, QTableWidgetItem(f"${item['price']:.2f}"))
            self.order_items_table.setItem(row, 2, QTableWidgetItem(str(item["quantity"])))
            self.order_items_table.setItem(row, 3, QTableWidgetItem(f"${item['total']:.2f}"))
            
            # Create actions cell with remove button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            remove_btn = QPushButton("Remove")
            remove_btn.setFixedSize(QSize(70, 25))
            remove_btn.clicked.connect(lambda _, r=row: self.remove_order_item(r))
            
            actions_layout.addWidget(remove_btn)
            
            self.order_items_table.setCellWidget(row, 4, actions_widget)
        
        self.order_items_table.resizeColumnsToContents()
        
        # Update total
        total = sum(item["total"] for item in self.current_order_items)
        
        # Apply tax if checked
        if self.tax_checkbox.isChecked():
            tax_rate = 0.14  # 14% tax
            tax_amount = total * tax_rate
            total += tax_amount
        
        self.order_total_label.setText(f"Total: ${total:.2f}")
    
    def remove_order_item(self, row):
        """Remove item from current order"""
        if 0 <= row < len(self.current_order_items):
            del self.current_order_items[row]
            self.update_order_items_table()
    
    def view_order(self, order_id):
        """View details of an order"""
        # Get order data
        self.cursor.execute(
            "SELECT id, table_number, timestamp, total, tax_included FROM orders WHERE id = ?", 
            (order_id,)
        )
        order_row = self.cursor.fetchone()
        
        if not order_row:
            QMessageBox.warning(self, "Error", f"Order #{order_id} not found")
            return
        
        order_data = {
            "id": order_row[0],
            "table_number": order_row[1],
            "timestamp": order_row[2],
            "total": order_row[3],
            "tax_included": bool(order_row[4])
        }
        
        # Get order items
        self.cursor.execute("""
            SELECT oi.quantity, d.name, d.price 
            FROM order_items oi
            JOIN drinks d ON oi.drink_id = d.id
            WHERE oi.order_id = ?
        """, (order_id,))
        
        items_data = []
        for quantity, name, price in self.cursor.fetchall():
            items_data.append({
                "name": name,
                "price": price,
                "quantity": quantity
            })
        
        # Show order details dialog
        dialog = OrderDetailsDialog(order_data, items_data, parent=self)
        dialog.exec_()
    
    def delete_order(self, order_id):
        """Delete an order"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete Order #{order_id}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete order items
            self.cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            
            # Delete order
            self.cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            
            self.conn.commit()
            
            # Refresh orders
            self.load_orders()
            QMessageBox.information(self, "Success", f"Order #{order_id} deleted successfully")
    
    def filter_orders(self):
        """Filter orders by date"""
        selected_date = self.date_filter.date().toString("yyyy-MM-dd")
        
        self.cursor.execute(
            "SELECT id, table_number, timestamp, total, tax_included FROM orders WHERE timestamp LIKE ? ORDER BY id DESC", 
            (f"{selected_date}%",)
        )
        orders = self.cursor.fetchall()
        
        self.orders_table.setRowCount(len(orders))
        for row, (order_id, table, timestamp, total, tax_included) in enumerate(orders):
            self.orders_table.setItem(row, 0, QTableWidgetItem(str(order_id)))
            self.orders_table.setItem(row, 1, QTableWidgetItem(table))
            self.orders_table.setItem(row, 2, QTableWidgetItem(timestamp))
            self.orders_table.setItem(row, 3, QTableWidgetItem(f"${total:.2f}"))
            
            # Create actions cell with view and delete buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            
            view_btn = QPushButton("View")
            view_btn.setFixedSize(QSize(60, 25))
            view_btn.clicked.connect(lambda _, o_id=order_id: self.view_order(o_id))
            
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(QSize(60, 25))
            delete_btn.clicked.connect(lambda _, o_id=order_id: self.delete_order(o_id))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setSpacing(5)
            
            self.orders_table.setCellWidget(row, 4, actions_widget)
    
    def closeEvent(self, event):
        """Handle application close event"""
        if hasattr(self, 'conn'):
            self.conn.commit()  # Ensure all changes are saved before closing
            self.conn.close()
        event.accept()

    def ensure_connection(self):
        """Ensure database connection is open"""
        if not hasattr(self, 'conn') or self.conn is None:
            self.conn = sqlite3.connect("cafe_manager.db")
            self.cursor = self.conn.cursor()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = CafeManager()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()