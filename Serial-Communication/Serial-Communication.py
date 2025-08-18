import sys
import serial
import serial.tools.list_ports
import threading
import time
import json
import csv
import io
import re
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QComboBox, QTableWidget, 
                            QTableWidgetItem, QLabel, QProgressBar, QMessageBox,
                            QGroupBox, QTextEdit, QSplitter, QMenuBar, QMenu, 
                            QAction, QFileDialog, QDialog, QGridLayout, QCheckBox,
                            QSpinBox, QTabWidget, QLineEdit, QTextBrowser, QFrame,
                            QSizePolicy, QHeaderView, QSlider, QStatusBar, QToolBar,
                            QScrollArea, QSpacerItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QBrush, QPen, QLinearGradient, QPalette


class ModernButton(QPushButton):
    """Custom modern button with enhanced styling."""
    
    def __init__(self, text, button_type="primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setMinimumHeight(35)
        self.setMinimumWidth(100)
        self.update_style()
    
    def update_style(self):
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a6fd8, stop:1 #6a4190);
                    transform: translateY(-1px);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4e5bc6, stop:1 #5e377e);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f093fb, stop:1 #f5576c);
                    border: none;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ee85f7, stop:1 #f14958);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ec77f3, stop:1 #ed3b44);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)
        elif self.button_type == "danger":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff9a9e, stop:1 #fecfef);
                    border: none;
                    border-radius: 8px;
                    color: #333;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff8a8e, stop:1 #febfdf);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff7a7e, stop:1 #feafcf);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #888888;
                }
            """)
        else:  # neutral
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e0e7ff, stop:1 #c7d2fe);
                    border: 1px solid #a5b4fc;
                    border-radius: 8px;
                    color: #3730a3;
                    font-weight: 500;
                    font-size: 11px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #d0d7ff, stop:1 #b7c2fe);
                    border: 1px solid #9ca3f4;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #c0c7ff, stop:1 #a7b2fe);
                }
                QPushButton:disabled {
                    background: #f5f5f5;
                    border: 1px solid #ddd;
                    color: #999;
                }
            """)


class ModernComboBox(QComboBox):
    """Custom modern combo box with enhanced styling."""
    
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(35)
        self.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
                color: #334155;
            }
            QComboBox:hover {
                border: 2px solid #667eea;
            }
            QComboBox:focus {
                border: 2px solid #667eea;
                background: white;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
                margin-right: 12px;
            }
            QComboBox QAbstractItemView {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                selection-background-color: #f1f5f9;
                outline: none;
            }
        """)


class ArduinoDetector(QThread):
    """Enhanced thread for detecting Arduino devices and their baud rates."""
    device_found = pyqtSignal(str, int, str)  # port, baud_rate, device_info
    scan_progress = pyqtSignal(int)
    scan_complete = pyqtSignal()
    scan_error = pyqtSignal(str)
    status_update = pyqtSignal(str)
    
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        self.common_baud_rates = [9600, 19200, 38400, 57600, 74880, 115200, 230400, 250000, 500000, 1000000]
        self.test_commands = [b'I\n', b'INFO\n', b'?\n', b'STATUS\n', b'\n']
    
    def run(self):
        total_tests = len(self.common_baud_rates) * len(self.test_commands)
        current_test = 0
        
        for baud_rate in self.common_baud_rates:
            if not self.running:
                break
            
            self.status_update.emit(f"Testing {self.port} at {baud_rate} baud...")
            
            for command in self.test_commands:
                if not self.running:
                    break
                    
                current_test += 1
                self.scan_progress.emit(int(current_test / total_tests * 100))
                
                try:
                    ser = serial.Serial(self.port, baud_rate, timeout=1)
                    time.sleep(2)  # Allow time for Arduino reset
                    
                    # Clear any existing data
                    ser.flushInput()
                    
                    # Send test command
                    ser.write(command)
                    time.sleep(0.5)
                    
                    # Check for response
                    response = ""
                    attempts = 3
                    for _ in range(attempts):
                        if ser.in_waiting > 0:
                            response += ser.readline().decode('utf-8', errors='ignore').strip()
                        time.sleep(0.2)
                    
                    if response and len(response) > 2:
                        # We got a meaningful response
                        device_info = self.identify_device(response)
                        ser.close()
                        self.device_found.emit(self.port, baud_rate, device_info)
                        self.scan_complete.emit()
                        return
                    
                    ser.close()
                    
                except Exception as e:
                    pass  # Try next combination
        
        self.scan_error.emit(f"Could not detect valid Arduino on {self.port}")
        self.scan_complete.emit()
    
    def identify_device(self, response):
        """Try to identify the Arduino device type from its response."""
        response_lower = response.lower()
        
        if 'uno' in response_lower:
            return "Arduino Uno"
        elif 'nano' in response_lower:
            return "Arduino Nano"
        elif 'mega' in response_lower:
            return "Arduino Mega"
        elif 'esp32' in response_lower:
            return "ESP32"
        elif 'esp8266' in response_lower:
            return "ESP8266"
        elif 'leonardo' in response_lower:
            return "Arduino Leonardo"
        elif 'micro' in response_lower:
            return "Arduino Micro"
        else:
            return "Arduino Compatible"
    
    def stop(self):
        self.running = False


class SerialReader(QThread):
    """Enhanced thread for reading data from Arduino devices."""
    data_received = pyqtSignal(str, object, str)  # port, data, data_type
    connection_error = pyqtSignal(str, str)
    stats_updated = pyqtSignal(str, dict)  # port, stats
    
    def __init__(self, port, baud_rate):
        super().__init__()
        self.port = port
        self.baud_rate = baud_rate
        self.running = True
        self.paused = False
        self.serial = None
        self.stats = {
            "messages_received": 0,
            "bytes_received": 0,
            "errors": 0,
            "start_time": time.time(),
            "last_message_time": None
        }
    
    def run(self):
        try:
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Allow time for Arduino reset
            
            buffer = ""
            
            while self.running:
                try:
                    if not self.paused and self.serial.in_waiting > 0:
                        # Read available data
                        chunk = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                        buffer += chunk
                        self.stats["bytes_received"] += len(chunk)
                        
                        # Process complete lines
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if line:
                                self.stats["messages_received"] += 1
                                self.stats["last_message_time"] = time.time()
                                
                                # Parse and emit the data
                                parsed_data, data_type = self.parse_data(line)
                                self.data_received.emit(self.port, parsed_data, data_type)
                                
                                # Emit stats periodically
                                if self.stats["messages_received"] % 10 == 0:
                                    self.stats_updated.emit(self.port, self.stats.copy())
                        
                except Exception as e:
                    if self.running:
                        self.stats["errors"] += 1
                        self.connection_error.emit(self.port, str(e))
                        break
                
                time.sleep(0.01)
                
        except Exception as e:
            if self.running:
                self.connection_error.emit(self.port, str(e))
        
        finally:
            if self.serial and self.serial.is_open:
                self.serial.close()
    
    def parse_data(self, data_str):
        """Enhanced data parsing with type detection."""
        original_str = data_str
        
        # Try JSON format
        try:
            parsed = json.loads(data_str)
            return parsed, "JSON"
        except json.JSONDecodeError:
            pass
        
        # Try CSV format
        try:
            csv_reader = csv.reader(io.StringIO(data_str))
            for row in csv_reader:
                if row and len(row) > 1:
                    return row, "CSV"
        except:
            pass
        
        # Try key-value pairs (format like "key1:value1,key2:value2" or "key1=value1,key2=value2")
        for separator in [':', '=']:
            if separator in data_str and (',' in data_str or ';' in data_str):
                try:
                    result = {}
                    delimiter = ',' if ',' in data_str else ';'
                    pairs = data_str.split(delimiter)
                    
                    for pair in pairs:
                        if separator in pair:
                            key, value = pair.split(separator, 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Try to convert to appropriate type
                            if value.lower() in ['true', 'false']:
                                result[key] = value.lower() == 'true'
                            else:
                                try:
                                    # Try integer first
                                    if '.' not in value:
                                        result[key] = int(value)
                                    else:
                                        result[key] = float(value)
                                except ValueError:
                                    result[key] = value
                    
                    if result:
                        return result, "Key-Value"
                except:
                    pass
        
        # Try space-separated numeric values
        try:
            values = data_str.split()
            if len(values) > 1 and all(self.is_numeric(v) for v in values):
                numeric_values = []
                for v in values:
                    try:
                        if '.' in v:
                            numeric_values.append(float(v))
                        else:
                            numeric_values.append(int(v))
                    except:
                        numeric_values.append(v)
                return numeric_values, "Numeric Array"
        except:
            pass
        
        # Check if it's a single numeric value
        if self.is_numeric(data_str):
            try:
                if '.' in data_str:
                    return float(data_str), "Float"
                else:
                    return int(data_str), "Integer"
            except:
                pass
        
        # Return as string
        return original_str, "String"
    
    def is_numeric(self, value):
        """Check if a string represents a numeric value."""
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def toggle_pause(self):
        self.paused = not self.paused
        return self.paused
    
    def stop(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()


class DataStatsWidget(QWidget):
    """Widget for displaying data statistics."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QGridLayout()
        
        # Create stat labels with modern styling
        self.stats_labels = {}
        stats = ["Messages", "Bytes", "Errors", "Rate (msg/s)", "Uptime"]
        
        for i, stat in enumerate(stats):
            # Label
            label = QLabel(stat + ":")
            label.setStyleSheet("font-weight: bold; color: #475569;")
            
            # Value
            value_label = QLabel("0")
            value_label.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f8fafc, stop:1 #e2e8f0);
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-family: 'Courier New', monospace;
                    font-weight: bold;
                    color: #1e293b;
                }
            """)
            
            layout.addWidget(label, i // 3, (i % 3) * 2)
            layout.addWidget(value_label, i // 3, (i % 3) * 2 + 1)
            
            self.stats_labels[stat.split()[0].lower()] = value_label
        
        self.setLayout(layout)
    
    def update_stats(self, stats):
        """Update the statistics display."""
        self.stats_labels["messages"].setText(str(stats.get("messages_received", 0)))
        self.stats_labels["bytes"].setText(f"{stats.get('bytes_received', 0):,}")
        self.stats_labels["errors"].setText(str(stats.get("errors", 0)))
        
        # Calculate message rate
        uptime = time.time() - stats.get("start_time", time.time())
        if uptime > 0:
            rate = stats.get("messages_received", 0) / uptime
            self.stats_labels["rate"].setText(f"{rate:.1f}")
            
            # Format uptime
            hours, remainder = divmod(int(uptime), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.stats_labels["uptime"].setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")


class TableSettingsDialog(QDialog):
    """Enhanced dialog for configuring table display settings."""
    
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle("Data Table Settings")
        self.resize(450, 400)
        
        if current_settings is None:
            self.settings = {
                "auto_scroll": True,
                "timestamp": True,
                "row_limit": 1000,
                "columns": [],
                "data_format": "auto",
                "filter_empty": True,
                "highlight_changes": True
            }
        else:
            self.settings = current_settings.copy()
        
        self.init_ui()
        self.apply_modern_style()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tabbed interface
        tabs = QTabWidget()
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout()
        
        # Auto-scroll
        self.auto_scroll_cb = QCheckBox("Auto-scroll to latest data")
        self.auto_scroll_cb.setChecked(self.settings.get("auto_scroll", True))
        general_layout.addWidget(self.auto_scroll_cb)
        
        # Timestamp
        self.timestamp_cb = QCheckBox("Add timestamp to incoming data")
        self.timestamp_cb.setChecked(self.settings.get("timestamp", True))
        general_layout.addWidget(self.timestamp_cb)
        
        # Filter empty
        self.filter_empty_cb = QCheckBox("Filter empty values")
        self.filter_empty_cb.setChecked(self.settings.get("filter_empty", True))
        general_layout.addWidget(self.filter_empty_cb)
        
        # Highlight changes
        self.highlight_changes_cb = QCheckBox("Highlight value changes")
        self.highlight_changes_cb.setChecked(self.settings.get("highlight_changes", True))
        general_layout.addWidget(self.highlight_changes_cb)
        
        # Row limit
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel("Maximum rows to display:"))
        self.row_limit = QSpinBox()
        self.row_limit.setRange(50, 10000)
        self.row_limit.setSingleStep(50)
        self.row_limit.setValue(self.settings.get("row_limit", 1000))
        row_layout.addWidget(self.row_limit)
        general_layout.addLayout(row_layout)
        
        # Data format
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Data format:"))
        self.data_format = QComboBox()
        self.data_format.addItems(["Auto-detect", "JSON", "CSV", "Key-Value", "Raw"])
        current_format = self.settings.get("data_format", "auto")
        format_index = {"auto": 0, "json": 1, "csv": 2, "key-value": 3, "raw": 4}.get(current_format, 0)
        self.data_format.setCurrentIndex(format_index)
        format_layout.addWidget(self.data_format)
        general_layout.addLayout(format_layout)
        
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "General")
        
        # Column settings tab
        if self.settings.get("columns"):
            columns_tab = QWidget()
            columns_layout = QVBoxLayout()
            
            columns_layout.addWidget(QLabel("Select columns to display:"))
            
            scroll = QScrollArea()
            scroll_widget = QWidget()
            scroll_layout = QVBoxLayout()
            
            self.column_checkboxes = {}
            for column in self.settings["columns"]:
                cb = QCheckBox(column["name"])
                cb.setChecked(column.get("visible", True))
                self.column_checkboxes[column["name"]] = cb
                scroll_layout.addWidget(cb)
            
            scroll_widget.setLayout(scroll_layout)
            scroll.setWidget(scroll_widget)
            scroll.setWidgetResizable(True)
            columns_layout.addWidget(scroll)
            
            columns_tab.setLayout(columns_layout)
            tabs.addTab(columns_tab, "Columns")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = ModernButton("Apply", "primary")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = ModernButton("Cancel", "neutral")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def apply_modern_style(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 6px 6px 0 0;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background: #e2e8f0;
            }
            QCheckBox {
                spacing: 8px;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #cbd5e1;
                background: white;
            }
            QCheckBox::indicator:checked {
                background: #667eea;
                border: 2px solid #667eea;
            }
            QSpinBox {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 8px;
                background: white;
            }
            QSpinBox:focus {
                border: 2px solid #667eea;
            }
        """)
    
    def get_settings(self):
        """Get the updated settings from the dialog."""
        self.settings["auto_scroll"] = self.auto_scroll_cb.isChecked()
        self.settings["timestamp"] = self.timestamp_cb.isChecked()
        self.settings["filter_empty"] = self.filter_empty_cb.isChecked()
        self.settings["highlight_changes"] = self.highlight_changes_cb.isChecked()
        self.settings["row_limit"] = self.row_limit.value()
        
        format_map = {0: "auto", 1: "json", 2: "csv", 3: "key-value", 4: "raw"}
        self.settings["data_format"] = format_map[self.data_format.currentIndex()]
        
        # Update column visibility settings
        if hasattr(self, 'column_checkboxes'):
            for column in self.settings["columns"]:
                if column["name"] in self.column_checkboxes:
                    column["visible"] = self.column_checkboxes[column["name"]].isChecked()
        
        return self.settings


class ArduinoSerialMonitor(QMainWindow):
    """Enhanced main application window with modern UI and improved functionality."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Multi-Device Serial Monitor Pro")
        self.resize(1200, 800)
        
        self.serial_detectors = {}
        self.serial_readers = {}
        self.device_data = {}
        self.connected_devices = {}
        self.device_stats = {}
        self.previous_values = {}  # For change highlighting
        
        # Enhanced table settings
        self.table_settings = {
            "auto_scroll": True,
            "timestamp": True,
            "row_limit": 1000,
            "columns": [],
            "data_format": "auto",
            "filter_empty": True,
            "highlight_changes": True
        }
        
        self.apply_modern_theme()
        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()
        self.refresh_ports()
        
        # Enhanced refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_ports)
        self.refresh_timer.start(3000)  # Refresh every 3 seconds
        
        # Animation for status updates
        self.status_animation = QPropertyAnimation(self.statusBar(), b"geometry")
        self.status_animation.setDuration(300)
        self.status_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def apply_modern_theme(self):
        """Apply modern dark/light theme to the application."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
            }
            QWidget {
                background-color: #f8fafc;
                color: #1e293b;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                margin-top: 1em;
                padding-top: 1em;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #334155;
                background: #f8fafc;
                border-radius: 4px;
            }
            QTableWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                selection-background-color: #e0e7ff;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11px;
            }
            QTextEdit, QTextBrowser {
                background: white;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
                selection-background-color: #e0e7ff;
            }
            QProgressBar {
                border: none;
                border-radius: 8px;
                background: #e2e8f0;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 8px;
            }
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #334155);
                color: white;
                font-weight: 500;
                padding: 4px;
            }
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #334155);
                color: white;
                spacing: 3px;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.1);
            }
            QMenu {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background: #f1f5f9;
                color: #667eea;
            }
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border: none;
                padding: 8px;
                spacing: 4px;
            }
            QSplitter::handle {
                background: #cbd5e1;
                border-radius: 2px;
            }
            QSplitter::handle:horizontal {
                width: 4px;
            }
            QSplitter::handle:vertical {
                height: 4px;
            }
        """)
    
    def init_ui(self):
        # Create toolbar
        self.create_toolbar()
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Control panel with modern design
        control_group = QGroupBox("🔌 Device Connection")
        control_layout = QVBoxLayout()
        
        # Port selection with enhanced layout
        port_frame = QFrame()
        port_frame.setFrameStyle(QFrame.Box)
        port_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        port_layout = QHBoxLayout()
        
        port_layout.addWidget(QLabel("📍 Serial Port:"))
        self.port_combo = ModernComboBox()
        port_layout.addWidget(self.port_combo)
        
        self.refresh_btn = ModernButton("🔄 Refresh", "neutral")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        port_layout.addWidget(self.refresh_btn)
        
        port_frame.setLayout(port_layout)
        control_layout.addWidget(port_frame)
        
        # Connection buttons with enhanced layout
        button_frame = QFrame()
        button_frame.setFrameStyle(QFrame.Box)
        button_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        button_layout = QHBoxLayout()
        
        self.connect_btn = ModernButton("🔗 Connect", "primary")
        self.connect_btn.clicked.connect(self.connect_device)
        button_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = ModernButton("❌ Disconnect", "danger")
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        self.disconnect_btn.setEnabled(False)
        button_layout.addWidget(self.disconnect_btn)
        
        self.scan_btn = ModernButton("🔍 Auto-Detect", "secondary")
        self.scan_btn.clicked.connect(self.scan_baud_rate)
        button_layout.addWidget(self.scan_btn)
        
        button_frame.setLayout(button_layout)
        control_layout.addWidget(button_frame)
        
        # Enhanced baud rate and device info display
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e0e7ff, stop:1 #c7d2fe);
                border: 1px solid #a5b4fc;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        info_layout = QHBoxLayout()
        
        info_layout.addWidget(QLabel("📊 Baud Rate:"))
        self.baud_label = QLabel("Not detected")
        self.baud_label.setStyleSheet("""
            QLabel {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                color: #1e293b;
            }
        """)
        info_layout.addWidget(self.baud_label)
        
        info_layout.addWidget(QLabel("🔧 Device:"))
        self.device_label = QLabel("Unknown")
        self.device_label.setStyleSheet("""
            QLabel {
                background: white;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px 8px;
                font-weight: bold;
                color: #1e293b;
            }
        """)
        info_layout.addWidget(self.device_label)
        info_layout.addStretch()
        
        info_frame.setLayout(info_layout)
        control_layout.addWidget(info_frame)
        
        # Enhanced progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 8px;
                background: #f1f5f9;
                text-align: center;
                font-weight: bold;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4ade80, stop:1 #22c55e);
                border-radius: 8px;
            }
        """)
        control_layout.addWidget(self.progress_bar)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Main content splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Devices and Stats
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Connected devices with enhanced styling
        devices_group = QGroupBox("🖥️ Connected Devices")
        devices_layout = QVBoxLayout()
        
        self.devices_table = QTableWidget()
        self.devices_table.setColumnCount(4)
        self.devices_table.setHorizontalHeaderLabels(["Port", "Device", "Baud Rate", "Status"])
        self.devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.devices_table.itemClicked.connect(self.device_selected)
        self.devices_table.setAlternatingRowColors(True)
        
        # Set column widths
        header = self.devices_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        devices_layout.addWidget(self.devices_table)
        devices_group.setLayout(devices_layout)
        left_layout.addWidget(devices_group)
        
        # Statistics widget
        stats_group = QGroupBox("📈 Device Statistics")
        stats_layout = QVBoxLayout()
        self.stats_widget = DataStatsWidget()
        stats_layout.addWidget(self.stats_widget)
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        left_panel.setLayout(left_layout)
        main_splitter.addWidget(left_panel)
        
        # Right panel - Data view with tabs
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        
        # Data view tabs
        self.data_tabs = QTabWidget()
        
        # Table view tab
        table_tab = QWidget()
        table_layout = QVBoxLayout()
        
        # Enhanced display controls
        display_controls = QFrame()
        display_controls.setFrameStyle(QFrame.Box)
        display_controls.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8fafc, stop:1 #f1f5f9);
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        display_layout = QHBoxLayout()
        
        self.toggle_display_btn = ModernButton("⏸️ Pause", "secondary")
        self.toggle_display_btn.clicked.connect(self.toggle_data_display)
        self.toggle_display_btn.setEnabled(False)
        display_layout.addWidget(self.toggle_display_btn)
        
        self.clear_data_btn = ModernButton("🗑️ Clear", "danger")
        self.clear_data_btn.clicked.connect(self.clear_data)
        self.clear_data_btn.setEnabled(False)
        display_layout.addWidget(self.clear_data_btn)
        
        self.table_settings_btn = ModernButton("⚙️ Settings", "neutral")
        self.table_settings_btn.clicked.connect(self.show_table_settings)
        display_layout.addWidget(self.table_settings_btn)
        
        # Data filter
        display_layout.addWidget(QLabel("🔍 Filter:"))
        self.data_filter = QLineEdit()
        self.data_filter.setPlaceholderText("Filter data...")
        self.data_filter.textChanged.connect(self.filter_data)
        self.data_filter.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                padding: 6px 12px;
                background: white;
                font-size: 11px;
            }
            QLineEdit:focus {
                border: 2px solid #667eea;
            }
        """)
        display_layout.addWidget(self.data_filter)
        
        display_layout.addStretch()
        display_controls.setLayout(display_layout)
        table_layout.addWidget(display_controls)
        
        # Enhanced data table
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(3)
        self.data_table.setHorizontalHeaderLabels(["Timestamp", "Key", "Value"])
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        
        # Enhanced table font and styling
        table_font = QFont("Arial", 10)
        self.data_table.setFont(table_font)
        
        # Set up table headers
        data_header = self.data_table.horizontalHeader()
        data_header.setStretchLastSection(True)
        data_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        data_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        
        table_layout.addWidget(self.data_table)
        table_tab.setLayout(table_layout)
        self.data_tabs.addTab(table_tab, "📊 Table View")
        
        # Raw data tab
        raw_tab = QWidget()
        raw_layout = QVBoxLayout()
        
        # Raw data controls
        raw_controls = QHBoxLayout()
        self.raw_auto_scroll = QCheckBox("Auto-scroll")
        self.raw_auto_scroll.setChecked(True)
        raw_controls.addWidget(self.raw_auto_scroll)
        
        self.clear_raw_btn = ModernButton("Clear Raw Data", "neutral")
        self.clear_raw_btn.clicked.connect(self.clear_raw_data)
        raw_controls.addWidget(self.clear_raw_btn)
        raw_controls.addStretch()
        
        raw_layout.addLayout(raw_controls)
        
        self.raw_data = QTextBrowser()
        self.raw_data.setReadOnly(True)
        self.raw_data.setStyleSheet("""
            QTextBrowser {
                background: #1e293b;
                color: #64ffda;
                border: 2px solid #334155;
                border-radius: 8px;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.4;
            }
        """)
        raw_layout.addWidget(self.raw_data)
        
        raw_tab.setLayout(raw_layout)
        self.data_tabs.addTab(raw_tab, "📝 Raw Data")
        
        # Chart view tab (placeholder for future enhancement)
        chart_tab = QWidget()
        chart_layout = QVBoxLayout()
        
        chart_placeholder = QLabel("📈 Chart visualization coming soon...")
        chart_placeholder.setAlignment(Qt.AlignCenter)
        chart_placeholder.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0e7ff, stop:1 #c7d2fe);
                border: 2px dashed #a5b4fc;
                border-radius: 12px;
                padding: 40px;
                font-size: 16px;
                font-weight: bold;
                color: #3730a3;
            }
        """)
        chart_layout.addWidget(chart_placeholder)
        
        chart_tab.setLayout(chart_layout)
        self.data_tabs.addTab(chart_tab, "📈 Charts")
        
        right_layout.addWidget(self.data_tabs)
        right_panel.setLayout(right_layout)
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([350, 850])
        main_layout.addWidget(main_splitter)
        
        # Enhanced status bar
        self.setup_status_bar()
    
    def create_toolbar(self):
        """Create a modern toolbar."""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setMovable(False)
        
        # Quick connect action
        quick_connect = QAction("⚡ Quick Connect", self)
        quick_connect.triggered.connect(self.quick_connect)
        toolbar.addAction(quick_connect)
        
        toolbar.addSeparator()
        
        # Export action
        export_action = QAction("💾 Export Data", self)
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_table_settings)
        toolbar.addAction(settings_action)
        
        toolbar.addSeparator()
        
        # About action
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
        
        self.addToolBar(toolbar)
    
    def setup_status_bar(self):
        """Setup an enhanced status bar."""
        status_bar = QStatusBar()
        
        # Connection status
        self.connection_status = QLabel("🔴 Disconnected")
        self.connection_status.setStyleSheet("""
            QLabel {
                background: #fee2e2;
                border: 1px solid #fecaca;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                color: #dc2626;
            }
        """)
        status_bar.addPermanentWidget(self.connection_status)
        
        # Device count
        self.device_count = QLabel("📱 0 devices")
        self.device_count.setStyleSheet("""
            QLabel {
                background: #e0f2fe;
                border: 1px solid #7dd3fc;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                color: #0369a1;
            }
        """)
        status_bar.addPermanentWidget(self.device_count)
        
        # Message rate
        self.message_rate = QLabel("📡 0 msg/s")
        self.message_rate.setStyleSheet("""
            QLabel {
                background: #f0fdf4;
                border: 1px solid #86efac;
                border-radius: 4px;
                padding: 4px 8px;
                font-weight: bold;
                color: #166534;
            }
        """)
        status_bar.addPermanentWidget(self.message_rate)
        
        status_bar.showMessage("🚀 Arduino Serial Monitor Ready")
        self.setStatusBar(status_bar)
    
    def create_menu_bar(self):
        """Create an enhanced menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("📁 File")
        
        export_action = QAction("💾 Export Data...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        save_settings_action = QAction("💾 Save Settings", self)
        save_settings_action.triggered.connect(self.save_settings)
        file_menu.addAction(save_settings_action)
        
        load_settings_action = QAction("📂 Load Settings", self)
        load_settings_action.triggered.connect(self.load_settings)
        file_menu.addAction(load_settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Device Menu
        device_menu = menubar.addMenu("🔌 Device")
        
        connect_action = QAction("🔗 Connect", self)
        connect_action.setShortcut("Ctrl+C")
        connect_action.triggered.connect(self.connect_device)
        device_menu.addAction(connect_action)
        
        disconnect_action = QAction("❌ Disconnect", self)
        disconnect_action.setShortcut("Ctrl+D")
        disconnect_action.triggered.connect(self.disconnect_device)
        device_menu.addAction(disconnect_action)
        
        device_menu.addSeparator()
        
        scan_action = QAction("🔍 Auto-Detect Baud Rate", self)
        scan_action.setShortcut("Ctrl+S")
        scan_action.triggered.connect(self.scan_baud_rate)
        device_menu.addAction(scan_action)
        
        quick_connect_action = QAction("⚡ Quick Connect All", self)
        quick_connect_action.triggered.connect(self.quick_connect_all)
        device_menu.addAction(quick_connect_action)
        
        # Tools Menu
        tools_menu = menubar.addMenu("🛠️ Tools")
        
        send_command_action = QAction("📤 Send Command", self)
        send_command_action.triggered.connect(self.show_send_command_dialog)
        tools_menu.addAction(send_command_action)
        
        tools_menu.addSeparator()
        
        data_analysis_action = QAction("📊 Data Analysis", self)
        data_analysis_action.triggered.connect(self.show_data_analysis)
        tools_menu.addAction(data_analysis_action)
        
        # View Menu
        view_menu = menubar.addMenu("👁️ View")
        
        table_settings_action = QAction("⚙️ Table Settings...", self)
        table_settings_action.triggered.connect(self.show_table_settings)
        view_menu.addAction(table_settings_action)
        
        self.auto_scroll_action = QAction("📜 Auto-scroll", self)
        self.auto_scroll_action.setCheckable(True)
        self.auto_scroll_action.setChecked(self.table_settings["auto_scroll"])
        self.auto_scroll_action.triggered.connect(self.toggle_auto_scroll)
        view_menu.addAction(self.auto_scroll_action)
        
        view_menu.addSeparator()
        
        toggle_stats_action = QAction("📈 Toggle Statistics", self)
        toggle_stats_action.triggered.connect(self.toggle_stats_visibility)
        view_menu.addAction(toggle_stats_action)
        
        # Help Menu
        help_menu = menubar.addMenu("❓ Help")
        
        about_action = QAction("ℹ️ About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        documentation_action = QAction("📚 Documentation", self)
        documentation_action.triggered.connect(self.show_documentation)
        help_menu.addAction(documentation_action)
    
    def quick_connect(self):
        """Quick connect to the first available port."""
        if self.port_combo.count() == 0:
            self.show_notification("No serial ports available", "warning")
            return
        
        # Set to first port and scan
        self.port_combo.setCurrentIndex(0)
        self.scan_baud_rate()
    
    def quick_connect_all(self):
        """Attempt to connect to all available Arduino ports."""
        ports = [self.port_combo.itemText(i) for i in range(self.port_combo.count())]
        
        if not ports:
            self.show_notification("No serial ports available", "warning")
            return
        
        self.show_notification(f"Scanning {len(ports)} ports...", "info")
        
        for port in ports:
            if port not in self.connected_devices and port not in self.serial_detectors:
                detector = ArduinoDetector(port)
                detector.device_found.connect(self.device_detected)
                detector.scan_progress.connect(self.update_scan_progress)
                detector.scan_complete.connect(lambda p=port: self.scan_completed(p))
                detector.scan_error.connect(self.show_error)
                detector.status_update.connect(self.update_scan_status)
                
                self.serial_detectors[port] = detector
                detector.start()
    
    def show_notification(self, message, msg_type="info"):
        """Show a modern notification message."""
        if msg_type == "success":
            color = "#10b981"
            bg_color = "#d1fae5"
            icon = "✅"
        elif msg_type == "warning":
            color = "#f59e0b"
            bg_color = "#fef3c7"
            icon = "⚠️"
        elif msg_type == "error":
            color = "#ef4444"
            bg_color = "#fee2e2"
            icon = "❌"
        else:  # info
            color = "#3b82f6"
            bg_color = "#dbeafe"
            icon = "ℹ️"
        
        self.statusBar().showMessage(f"{icon} {message}")
        
        # Could add a toast notification widget here for better UX
    
    def refresh_ports(self):
        """Enhanced port refresh with device information."""
        current_port = self.port_combo.currentText()
        self.port_combo.clear()
        
        ports = serial.tools.list_ports.comports()
        arduino_ports = []
        
        for port in ports:
            # Enhanced port detection
            port_info = f"{port.device}"
            if port.description and port.description != "n/a":
                if any(keyword in port.description.lower() for keyword in 
                       ['arduino', 'ch340', 'cp210', 'ftdi', 'usb']):
                    port_info += f" ({port.description})"
                    arduino_ports.append(port_info)
                else:
                    port_info += f" ({port.description})"
            
            self.port_combo.addItem(port_info, port.device)
        
        # Prioritize likely Arduino ports
        for arduino_port in arduino_ports:
            index = self.port_combo.findText(arduino_port)
            if index >= 0:
                item = self.port_combo.itemText(index)
                self.port_combo.removeItem(index)
                self.port_combo.insertItem(0, item, self.port_combo.itemData(index))
        
        # Restore selection
        if current_port:
            for i in range(self.port_combo.count()):
                if self.port_combo.itemData(i) == current_port:
                    self.port_combo.setCurrentIndex(i)
                    break
    
    def scan_baud_rate(self):
        """Enhanced baud rate detection with better UI feedback."""
        port_data = self.port_combo.currentData()
        if not port_data:
            self.show_notification("No serial port selected", "warning")
            return
        
        if port_data in self.connected_devices:
            self.show_notification(f"Already connected to {port_data}", "warning")
            return
        
        if port_data in self.serial_detectors:
            self.show_notification(f"Already scanning {port_data}", "warning")
            return
        
        # Enhanced UI feedback
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.scan_btn.setEnabled(False)
        self.connect_btn.setEnabled(False)
        
        detector = ArduinoDetector(port_data)
        detector.device_found.connect(self.device_detected)
        detector.scan_progress.connect(self.update_scan_progress)
        detector.scan_complete.connect(lambda: self.scan_completed(port_data))
        detector.scan_error.connect(self.show_error)
        detector.status_update.connect(self.update_scan_status)
        
        self.serial_detectors[port_data] = detector
        detector.start()
    
    @pyqtSlot(str, int, str)
    def device_detected(self, port, baud_rate, device_info):
        """Enhanced device detection handler."""
        self.baud_label.setText(str(baud_rate))
        self.device_label.setText(device_info)
        self.show_notification(f"Detected {device_info} on {port} at {baud_rate} baud", "success")
        
        # Automatically connect
        self.connect_to_device(port, baud_rate, device_info)
    
    @pyqtSlot(str)
    def update_scan_status(self, status):
        """Update scan status in the UI."""
        self.statusBar().showMessage(status)
    
    @pyqtSlot(int)
    def update_scan_progress(self, value):
        """Enhanced progress update."""
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_bar.setStyleSheet(self.progress_bar.styleSheet() + """
                QProgressBar::chunk { background: #10b981; }
            """)
    
    def scan_completed(self, port):
        """Enhanced scan completion handler."""
        if port in self.serial_detectors:
            del self.serial_detectors[port]
        
        self.scan_btn.setEnabled(True)
        self.connect_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if port not in self.connected_devices:
            self.show_notification("Scan completed", "info")
    
    def connect_device(self):
        """Enhanced manual device connection."""
        port_data = self.port_combo.currentData()
        if not port_data:
            self.show_notification("No serial port selected", "warning")
            return
        
        if port_data in self.connected_devices:
            self.show_notification(f"Already connected to {port_data}", "warning")
            return
        
        # Default baud rate if not detected
        baud_rate = 9600
        try:
            baud_rate = int(self.baud_label.text())
        except ValueError:
            self.show_notification("Using default baud rate 9600", "warning")
        
        device_info = self.device_label.text()
        if device_info == "Not detected":
            device_info = "Unknown Arduino Device"
        
        self.connect_to_device(port_data, baud_rate, device_info)
    
    def connect_to_device(self, port, baud_rate, device_info):
        """Connect to a specific device with given parameters."""
        try:
            # Create and start the serial reader
            reader = SerialReader(port, baud_rate)
            reader.data_received.connect(self.handle_data)
            reader.connection_error.connect(self.handle_connection_error)
            reader.stats_updated.connect(self.update_device_stats)
            
            self.connected_devices[port] = {
                "reader": reader,
                "baud_rate": baud_rate,
                "device_info": device_info,
                "connected": True
            }
            
            reader.start()
            
            # Update UI
            self.update_devices_table()
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.toggle_display_btn.setEnabled(True)
            self.clear_data_btn.setEnabled(True)
            
            # Update connection status
            self.connection_status.setText("🟢 Connected")
            self.connection_status.setStyleSheet("""
                QLabel {
                    background: #d1fae5;
                    border: 1px solid #a7f3d0;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                    color: #166534;
                }
            """)
            
            self.device_count.setText(f"📱 {len(self.connected_devices)} devices")
            self.show_notification(f"Connected to {device_info} on {port}", "success")
            
        except Exception as e:
            self.show_notification(f"Connection failed: {str(e)}", "error")
    
    def disconnect_device(self):
        """Disconnect from the currently selected device."""
        port_data = self.port_combo.currentData()
        if not port_data or port_data not in self.connected_devices:
            self.show_notification("No device selected or already disconnected", "warning")
            return
        
        try:
            # Stop and remove the reader
            reader = self.connected_devices[port_data]["reader"]
            reader.stop()
            del self.connected_devices[port_data]
            
            # Update UI
            self.update_devices_table()
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            
            # Update connection status
            if not self.connected_devices:
                self.connection_status.setText("🔴 Disconnected")
                self.connection_status.setStyleSheet("""
                    QLabel {
                        background: #fee2e2;
                        border: 1px solid #fecaca;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-weight: bold;
                        color: #dc2626;
                    }
                """)
            
            self.device_count.setText(f"📱 {len(self.connected_devices)} devices")
            self.show_notification(f"Disconnected from {port_data}", "info")
            
        except Exception as e:
            self.show_notification(f"Disconnection failed: {str(e)}", "error")
    
    def update_devices_table(self):
        """Update the connected devices table."""
        self.devices_table.setRowCount(len(self.connected_devices))
        
        for row, (port, device_info) in enumerate(self.connected_devices.items()):
            self.devices_table.setItem(row, 0, QTableWidgetItem(port))
            self.devices_table.setItem(row, 1, QTableWidgetItem(device_info["device_info"]))
            self.devices_table.setItem(row, 2, QTableWidgetItem(str(device_info["baud_rate"])))
            self.devices_table.setItem(row, 3, QTableWidgetItem("Connected" if device_info["connected"] else "Disconnected"))
    
    @pyqtSlot(str, object, str)
    def handle_data(self, port, data, data_type):
        """Handle incoming data from a device."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Add to raw data view
        if self.raw_auto_scroll.isChecked():
            self.raw_data.append(f"[{timestamp}] {port}: {str(data)}")
            scroll_bar = self.raw_data.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())
        else:
            self.raw_data.append(f"[{timestamp}] {port}: {str(data)}")
        
        # Process for table view
        if self.table_settings["timestamp"]:
            timestamp_item = QTableWidgetItem(timestamp)
        else:
            timestamp_item = QTableWidgetItem("")
        
        if data_type == "JSON":
            self.process_json_data(port, data, timestamp_item)
        elif data_type == "CSV":
            self.process_csv_data(port, data, timestamp_item)
        elif data_type == "Key-Value":
            self.process_key_value_data(port, data, timestamp_item)
        elif data_type == "Numeric Array":
            self.process_numeric_array_data(port, data, timestamp_item)
        else:
            self.process_string_data(port, data, timestamp_item)
        
        # Update message rate
        self.update_message_rate()
    
    def process_json_data(self, port, data, timestamp_item):
        """Process JSON formatted data."""
        if not isinstance(data, dict):
            data = {"data": data}
        
        # Add or update columns if needed
        self.update_table_columns(data.keys())
        
        # Add row to table
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, timestamp_item)
        
        for col, (key, value) in enumerate(data.items(), 1):
            value_item = QTableWidgetItem(str(value))
            
            # Highlight changes if enabled
            if self.table_settings["highlight_changes"]:
                prev_key = f"{port}_{key}"
                if prev_key in self.previous_values and self.previous_values[prev_key] != str(value):
                    value_item.setBackground(QColor("#fef3c7"))  # Light yellow
                self.previous_values[prev_key] = str(value)
            
            self.data_table.setItem(row, col, value_item)
        
        # Apply row limit
        if self.data_table.rowCount() > self.table_settings["row_limit"]:
            self.data_table.removeRow(0)
        
        # Auto-scroll if enabled
        if self.table_settings["auto_scroll"]:
            self.data_table.scrollToBottom()
    
    def process_csv_data(self, port, data, timestamp_item):
        """Process CSV formatted data."""
        if not isinstance(data, list):
            data = [data]
        
        # Add row to table
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, timestamp_item)
        
        for col, value in enumerate(data, 1):
            self.data_table.setItem(row, col, QTableWidgetItem(str(value)))
        
        # Apply row limit and auto-scroll
        if self.data_table.rowCount() > self.table_settings["row_limit"]:
            self.data_table.removeRow(0)
        if self.table_settings["auto_scroll"]:
            self.data_table.scrollToBottom()
    
    def process_key_value_data(self, port, data, timestamp_item):
        """Process key-value pair data."""
        self.process_json_data(port, data, timestamp_item)
    
    def process_numeric_array_data(self, port, data, timestamp_item):
        """Process numeric array data."""
        self.process_csv_data(port, data, timestamp_item)
    
    def process_string_data(self, port, data, timestamp_item):
        """Process plain string data."""
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, timestamp_item)
        self.data_table.setItem(row, 1, QTableWidgetItem(str(data)))
        
        # Apply row limit and auto-scroll
        if self.data_table.rowCount() > self.table_settings["row_limit"]:
            self.data_table.removeRow(0)
        if self.table_settings["auto_scroll"]:
            self.data_table.scrollToBottom()
    
    def update_table_columns(self, keys):
        """Update table columns based on incoming data keys."""
        current_columns = [self.data_table.horizontalHeaderItem(i).text() 
                          for i in range(1, self.data_table.columnCount())]
        
        new_columns = [str(key) for key in keys if str(key) not in current_columns]
        
        if new_columns:
            current_column_count = self.data_table.columnCount()
            self.data_table.setColumnCount(current_column_count + len(new_columns))
            
            for i, column in enumerate(new_columns, current_column_count):
                self.data_table.setHorizontalHeaderItem(i, QTableWidgetItem(column))
    
    def update_message_rate(self):
        """Update the message rate display in the status bar."""
        total_messages = sum(stats.get("messages_received", 0) 
                          for stats in self.device_stats.values())
        
        total_uptime = max((time.time() - stats.get("start_time", time.time())) 
                         for stats in self.device_stats.values())
        
        if total_uptime > 0:
            rate = total_messages / total_uptime
            self.message_rate.setText(f"📡 {rate:.1f} msg/s")
    
    @pyqtSlot(str, str)
    def handle_connection_error(self, port, error):
        """Handle connection errors."""
        if port in self.connected_devices:
            del self.connected_devices[port]
            self.update_devices_table()
        
        self.show_notification(f"Connection error on {port}: {error}", "error")
    
    @pyqtSlot(str, dict)
    def update_device_stats(self, port, stats):
        """Update device statistics."""
        self.device_stats[port] = stats
        self.stats_widget.update_stats(stats)
        
        # Update the devices table status if needed
        for row in range(self.devices_table.rowCount()):
            if self.devices_table.item(row, 0).text() == port:
                status = "Connected" if stats.get("errors", 0) < 3 else "Error"
                self.devices_table.setItem(row, 3, QTableWidgetItem(status))
                break
    
    def toggle_data_display(self):
        """Toggle data display pause/resume."""
        port_data = self.port_combo.currentData()
        if port_data and port_data in self.connected_devices:
            reader = self.connected_devices[port_data]["reader"]
            is_paused = reader.toggle_pause()
            
            if is_paused:
                self.toggle_display_btn.setText("▶️ Resume")
                self.show_notification("Data display paused", "info")
            else:
                self.toggle_display_btn.setText("⏸️ Pause")
                self.show_notification("Data display resumed", "info")
    
    def clear_data(self):
        """Clear the data table and raw data view."""
        self.data_table.setRowCount(0)
        self.raw_data.clear()
        self.previous_values = {}
        self.show_notification("Data cleared", "info")
    
    def clear_raw_data(self):
        """Clear only the raw data view."""
        self.raw_data.clear()
        self.show_notification("Raw data cleared", "info")
    
    def filter_data(self):
        """Filter data based on the filter text."""
        filter_text = self.data_filter.text().lower()
        
        for row in range(self.data_table.rowCount()):
            match = False
            for col in range(self.data_table.columnCount()):
                item = self.data_table.item(row, col)
                if item and filter_text in item.text().lower():
                    match = True
                    break
            
            self.data_table.setRowHidden(row, not match)
    
    def show_table_settings(self):
        """Show the table settings dialog."""
        dialog = TableSettingsDialog(self, self.table_settings)
        if dialog.exec_() == QDialog.Accepted:
            self.table_settings = dialog.get_settings()
            self.auto_scroll_action.setChecked(self.table_settings["auto_scroll"])
            self.show_notification("Table settings updated", "success")
    
    def toggle_auto_scroll(self, checked):
        """Toggle auto-scroll setting."""
        self.table_settings["auto_scroll"] = checked
    
    def toggle_stats_visibility(self):
        """Toggle statistics widget visibility."""
        self.stats_widget.setVisible(not self.stats_widget.isVisible())
    
    def device_selected(self, item):
        """Handle device selection from the table."""
        row = item.row()
        port = self.devices_table.item(row, 0).text()
        
        for i in range(self.port_combo.count()):
            if self.port_combo.itemData(i) == port:
                self.port_combo.setCurrentIndex(i)
                break
        
        # Update stats for selected device
        if port in self.device_stats:
            self.stats_widget.update_stats(self.device_stats[port])
    
    def export_data(self):
        """Export data to a file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", 
            "CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt)", 
            options=options)
        
        if not file_name:
            return
        
        try:
            if file_name.endswith('.csv'):
                self.export_to_csv(file_name)
            elif file_name.endswith('.json'):
                self.export_to_json(file_name)
            else:
                self.export_to_text(file_name)
            
            self.show_notification(f"Data exported to {file_name}", "success")
        except Exception as e:
            self.show_notification(f"Export failed: {str(e)}", "error")
    
    def export_to_csv(self, file_name):
        """Export data to CSV format."""
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header
            header = []
            for col in range(self.data_table.columnCount()):
                header.append(self.data_table.horizontalHeaderItem(col).text())
            writer.writerow(header)
            
            # Write data
            for row in range(self.data_table.rowCount()):
                row_data = []
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    row_data.append(item.text() if item else "")
                writer.writerow(row_data)
    
    def export_to_json(self, file_name):
        """Export data to JSON format."""
        data = []
        
        for row in range(self.data_table.rowCount()):
            row_data = {}
            for col in range(self.data_table.columnCount()):
                header = self.data_table.horizontalHeaderItem(col).text()
                item = self.data_table.item(row, col)
                row_data[header] = item.text() if item else ""
            data.append(row_data)
        
        with open(file_name, 'w') as file:
            json.dump(data, file, indent=2)
    
    def export_to_text(self, file_name):
        """Export data to plain text format."""
        with open(file_name, 'w') as file:
            # Write header
            headers = []
            for col in range(self.data_table.columnCount()):
                headers.append(self.data_table.horizontalHeaderItem(col).text())
            file.write("\t".join(headers) + "\n")
            
            # Write data
            for row in range(self.data_table.rowCount()):
                row_data = []
                for col in range(self.data_table.columnCount()):
                    item = self.data_table.item(row, col)
                    row_data.append(item.text() if item else "")
                file.write("\t".join(row_data) + "\n")
    
    def save_settings(self):
        """Save application settings to a file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Settings", "", 
            "JSON Files (*.json)", 
            options=options)
        
        if not file_name:
            return
        
        try:
            settings = {
                "table_settings": self.table_settings,
                "connected_devices": {
                    port: {
                        "baud_rate": info["baud_rate"],
                        "device_info": info["device_info"]
                    }
                    for port, info in self.connected_devices.items()
                }
            }
            
            with open(file_name, 'w') as file:
                json.dump(settings, file, indent=2)
            
            self.show_notification(f"Settings saved to {file_name}", "success")
        except Exception as e:
            self.show_notification(f"Failed to save settings: {str(e)}", "error")
    
    def load_settings(self):
        """Load application settings from a file."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load Settings", "", 
            "JSON Files (*.json)", 
            options=options)
        
        if not file_name:
            return
        
        try:
            with open(file_name, 'r') as file:
                settings = json.load(file)
            
            # Update table settings
            if "table_settings" in settings:
                self.table_settings = settings["table_settings"]
                self.auto_scroll_action.setChecked(self.table_settings["auto_scroll"])
            
            # Reconnect to devices
            if "connected_devices" in settings:
                for port, info in settings["connected_devices"].items():
                    if port not in self.connected_devices:
                        self.connect_to_device(port, info["baud_rate"], info["device_info"])
            
            self.show_notification(f"Settings loaded from {file_name}", "success")
        except Exception as e:
            self.show_notification(f"Failed to load settings: {str(e)}", "error")
    
    def show_send_command_dialog(self):
        """Show dialog for sending commands to devices."""
        if not self.connected_devices:
            self.show_notification("No connected devices", "warning")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Send Command")
        dialog.resize(400, 200)
        
        layout = QVBoxLayout()
        
        # Device selection
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        
        device_combo = QComboBox()
        device_combo.addItems(self.connected_devices.keys())
        device_layout.addWidget(device_combo)
        
        layout.addLayout(device_layout)
        
        # Command input
        command_layout = QVBoxLayout()
        command_layout.addWidget(QLabel("Command:"))
        
        command_edit = QTextEdit()
        command_edit.setPlaceholderText("Enter command to send...")
        command_layout.addWidget(command_edit)
        
        layout.addLayout(command_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        send_button = ModernButton("Send", "primary")
        send_button.clicked.connect(lambda: self.send_command(
            device_combo.currentText(), 
            command_edit.toPlainText()))
        send_button.clicked.connect(dialog.accept)
        
        cancel_button = ModernButton("Cancel", "neutral")
        cancel_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(send_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def send_command(self, port, command):
        """Send a command to a connected device."""
        if port not in self.connected_devices:
            self.show_notification(f"Device {port} not connected", "error")
            return
        
        try:
            reader = self.connected_devices[port]["reader"]
            if reader.serial and reader.serial.is_open:
                reader.serial.write((command + "\n").encode('utf-8'))
                self.show_notification(f"Command sent to {port}", "success")
            else:
                self.show_notification(f"Connection to {port} is closed", "error")
        except Exception as e:
            self.show_notification(f"Failed to send command: {str(e)}", "error")
    
    def show_data_analysis(self):
        """Show data analysis dialog (placeholder for future enhancement)."""
        QMessageBox.information(
            self, "Data Analysis", 
            "Data analysis features will be implemented in a future version.",
            QMessageBox.Ok)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Arduino Multi-Device Serial Monitor Pro</h2>
        <p>Version 1.0.0</p>
        <p>A modern, feature-rich serial monitor for multiple Arduino devices.</p>
        <p>Features:</p>
        <ul>
            <li>Multiple device support</li>
            <li>Automatic baud rate detection</li>
            <li>Data parsing (JSON, CSV, Key-Value)</li>
            <li>Real-time statistics</li>
            <li>Data export</li>
        </ul>
        <p>© 2025 Arduino Serial Monitor Pro</p>
        """
        
        QMessageBox.about(self, "About", about_text)
    
    def show_documentation(self):
        """Show the documentation dialog."""
        doc_text = """
        <head>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                color: #333;
                line-height: 1.6;
                margin: 0;
                padding: 0;
            }
            h1 {
                color: #2c3e50;
                font-size: 22px;
                border-bottom: 1px solid #eaeaea;
                padding-bottom: 10px;
                margin-top: 0;
            }
            h2 {
                color: #3498db;
                font-size: 18px;
                margin-top: 25px;
            }
            p {
                color: #16a085;
                font-size: 24px;
                margin-top: 20px;
            }
            ul, ol {
                margin: 10px 0;
                padding-left: 30px;
            }
            li {
                margin-bottom: 8px;
                font-size: 16px;
            }
            .feature-list {
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 15px;
                margin: 15px 0;
            }
            .code {
                font-family: 'Consolas', monospace;
                background-color: #f0f0f0;
                padding: 2px 5px;
                border-radius: 3px;
                font-size: 14px;
            }
            .note {
                background-color: #e8f4fc;
                border-left: 4px solid #2980b9;
                padding: 10px;
                margin: 15px 0;
            }
            .warning {
                background-color: #fdf2e9;
                border-left: 4px solid #e67e22;
                padding: 10px;
                margin: 15px 0;
            }
        </style>
        </head>
        <body>
        <h2>Arduino Serial Monitor Documentation</h2>
        
        <p>Connecting to Devices:</p>
        <ol>
            <li>Select a serial port from the dropdown</li>
            <li>Choose a baud rate or click "Auto-Detect Baud Rate"</li>
            <li>Click "Connect"</li>
        </ol>
        
        <p>Features:</p>
        <ul>
            <li><b>Auto-Detect Baud Rate:</b> Automatically detects the correct baud rate for your Arduino</li>
            <li><b>Data Display:</b> Shows parsed data in a table format and raw data in the text area</li>
            <li><b>Pause Display:</b> Temporarily pause data display without disconnecting</li>
            <li><b>Export Data:</b> Save collected data to CSV, JSON, or text format</li>
            <li><b>Send Commands:</b> Send custom commands to your Arduino</li>
        </ul>
        
        <p>Supported Data Formats:</p>
        <ul>
            <li><b>JSON:</b> {"sensor": "temp", "value": 23.5}</li>
            <li><b>CSV:</b> temp,23.5,humidity,45</li>
            <li><b>Key-Value:</b> sensor:temp,value:23.5</li>
            <li><b>Raw Text:</b> Any text output</li>
        </ul>
        </body>
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Documentation")
        dialog.resize(600, 500)
        
        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(doc_text)
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Stop all detectors
        for detector in self.serial_detectors.values():
            detector.stop()
            detector.wait()
        
        # Disconnect all devices
        for port in list(self.connected_devices.keys()):
            self.disconnect_device()
        
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set modern font
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = ArduinoSerialMonitor()
    window.show()
    sys.exit(app.exec_())