import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QSlider, QFileDialog, QListWidget, 
                            QMessageBox, QFrame, QSplitter, QProgressBar, QListWidgetItem,
                            QSystemTrayIcon, QMenu, QAction,QDialog,
                            QComboBox,QSpinBox,QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, concatenate_videoclips
import traceback
import subprocess
import json

class VideoThread(QThread):
    """Thread for processing videos without freezing the UI"""
    update_frame = pyqtSignal(np.ndarray)
    update_duration = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, video_path=None):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.paused = False
        self.current_frame_position = 0
        self.cap = None
    
    def run(self):
        try:
            if not self.video_path:
                return
                
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                self.error.emit(f"Error opening video file: {self.video_path}")
                return
                
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps else 0
            self.update_duration.emit(duration)
            
            while self.running:
                if not self.paused:
                    ret, frame = self.cap.read()
                    if not ret:
                        # If reached the end, restart from beginning
                        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        self.current_frame_position = 0
                        continue
                    
                    self.current_frame_position = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
                    self.update_frame.emit(frame)
                
                # Sleep to control playback speed
                self.msleep(33)  # ~30 fps
            
            self.cap.release()
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Error in video thread: {str(e)}")
    
    def stop(self):
        self.running = False
        self.wait()
        if self.cap and self.cap.isOpened():
            self.cap.release()
    
    def toggle_pause(self):
        self.paused = not self.paused
    
    def seek(self, frame_position):
        if self.cap and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            self.current_frame_position = frame_position


class VideoProcessingThread(QThread):
    """Thread for video processing tasks like trimming and merging using MoviePy"""
    progress_update = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, task, params):
        super().__init__()
        self.task = task  # 'trim' or 'merge'
        self.params = params
    
    def run(self):
        try:
            if self.task == 'trim':
                self.trim_video()
            elif self.task == 'merge':
                self.merge_videos()
        except Exception as e:
            self.error.emit(f"Error in video processing: {str(e)}\n{traceback.format_exc()}")
    
    def trim_video(self):
        input_path = self.params['input_path']
        output_path = self.params['output_path']
        start_time = self.params['start_time']
        end_time = self.params['end_time']
        
        try:
            # Initial progress updates
            self.progress_update.emit(5)
            clip = VideoFileClip(input_path)
            self.progress_update.emit(10)
            
            trimmed_clip = clip.subclip(start_time, end_time)
            self.progress_update.emit(20)
            
            # Setup for progress monitoring
            total_frames = int(trimmed_clip.fps * trimmed_clip.duration)
            
            # For progress tracking, we need to monitor the output file's growth
            def our_progress_monitor():
                # Since we can't directly hook into MoviePy's progress,
                # we'll simulate progress based on time
                import time
                start_time = time.time()
                estimated_encoding_time = trimmed_clip.duration * 0.5  # rough estimate
                
                # Loop until the encoding is likely complete
                while time.time() - start_time < estimated_encoding_time * 1.5:
                    elapsed = time.time() - start_time
                    progress_ratio = min(elapsed / (estimated_encoding_time * 1.2), 1.0)
                    scaled_progress = 20 + int(progress_ratio * 70)
                    self.progress_update.emit(scaled_progress)
                    time.sleep(0.3)  # Update roughly 3 times per second
            
            # Start the progress monitor in a separate thread
            import threading
            progress_thread = threading.Thread(target=our_progress_monitor)
            progress_thread.daemon = True
            progress_thread.start()
            
            # Encode the video
            trimmed_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                temp_audiofile="temp-audio.m4a", 
                remove_temp=True,
                preset="medium", 
                threads=4,
                verbose=False, # Disable built-in progress display
                logger=None
            )
            
            # Clean up
            clip.close()
            trimmed_clip.close()
            
            # Ensure we reach 100%
            self.progress_update.emit(100)
            self.finished.emit(output_path)
            
        except Exception as e:
            self.error.emit(f"Error trimming video: {str(e)}\n{traceback.format_exc()}")
    
    def merge_videos(self):
        video_paths = self.params['video_paths']
        output_path = self.params['output_path']
        
        if not video_paths:
            self.error.emit("No videos selected for merging")
            return
        
        try:
            clips = []
            # Load all video clips
            for i, path in enumerate(video_paths):
                progress = int(20 * (i / len(video_paths)))
                self.progress_update.emit(progress)
                clip = VideoFileClip(path)
                clips.append(clip)
            
            # Concatenate clips
            self.progress_update.emit(25)
            final_clip = concatenate_videoclips(clips)
            self.progress_update.emit(30)
            
            # Calculate total duration for progress estimation
            total_duration = sum(clip.duration for clip in clips)
            
            # Setup progress monitoring thread
            def our_progress_monitor():
                import time
                start_time = time.time()
                # Rough estimate based on total video duration
                estimated_encoding_time = total_duration * 0.5
                
                # Loop until the encoding is likely complete
                while time.time() - start_time < estimated_encoding_time * 1.5:
                    elapsed = time.time() - start_time
                    progress_ratio = min(elapsed / (estimated_encoding_time * 1.2), 1.0)
                    # Scale from 30% to 90% for encoding progress
                    scaled_progress = 30 + int(progress_ratio * 60)
                    self.progress_update.emit(scaled_progress)
                    time.sleep(0.3)  # Update roughly 3 times per second
            
            # Start the progress monitor in a separate thread
            import threading
            progress_thread = threading.Thread(target=our_progress_monitor)
            progress_thread.daemon = True
            progress_thread.start()
            
            # Write the output file
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                temp_audiofile="temp-audio.m4a", 
                remove_temp=True, 
                preset="medium", 
                threads=4,
                verbose=False, # Disable built-in progress display
                logger=None
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_clip.close()
            
            # Ensure we reach 100%
            self.progress_update.emit(100)
            self.finished.emit(output_path)
            
        except Exception as e:
            self.error.emit(f"Error merging videos: {str(e)}\n{traceback.format_exc()}")


class VideoPreviewWidget(QWidget):
    """Widget for displaying video preview with controls"""
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.video_path = None
        self.thread = None
        self.duration = 0  # in seconds
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Video display area
        self.video_frame = QLabel()
        self.video_frame.setMinimumSize(320, 240)
        self.video_frame.setAlignment(Qt.AlignCenter)
        self.video_frame.setStyleSheet("background-color: #222; color: #aaa; border-radius: 5px;")
        self.video_frame.setText("No video loaded")
        layout.addWidget(self.video_frame)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.play_button = QPushButton("Play")
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        self.time_label = QLabel("00:00 / 00:00")
        controls_layout.addWidget(self.time_label)
        
        layout.addLayout(controls_layout)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)
        
        self.setLayout(layout)
        
        # Timer for updating slider
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slider_position)
        self.timer.start(1000)  # Update every second
    
    def load_video(self, video_path):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
        
        self.video_path = video_path
        self.thread = VideoThread(video_path)
        self.thread.update_frame.connect(self.update_frame)
        self.thread.update_duration.connect(self.set_duration)
        self.thread.error.connect(self.handle_error)
        self.thread.start()
        
        self.play_button.setEnabled(True)
        self.play_button.setText("Pause")
        self.progress_slider.setEnabled(True)
    
    def update_frame(self, frame):
        # Convert OpenCV BGR to RGB for QImage
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        
        # Create QImage and QPixmap
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        
        # Scale pixmap to fit in video_frame while maintaining aspect ratio
        pixmap = pixmap.scaled(self.video_frame.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.video_frame.setPixmap(pixmap)
    
    def set_duration(self, duration):
        self.duration = duration
        self.progress_slider.setRange(0, int(duration))
        minutes, seconds = divmod(int(duration), 60)
        self.time_label.setText(f"00:00 / {minutes:02d}:{seconds:02d}")
    
    def toggle_playback(self):
        if not self.thread:
            return
            
        self.thread.toggle_pause()
        
        if self.thread.paused:
            self.play_button.setText("Play")
        else:
            self.play_button.setText("Pause")
    
    def set_position(self, position):
        if not self.thread or not self.thread.cap:
            return
            
        # Convert from slider position (seconds) to frame number
        fps = self.thread.cap.get(cv2.CAP_PROP_FPS)
        frame_position = int(position * fps)
        self.thread.seek(frame_position)
        
        # Update time label
        minutes, seconds = divmod(position, 60)
        total_minutes, total_seconds = divmod(int(self.duration), 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
    
    def update_slider_position(self):
        if not self.thread or not self.thread.cap or self.thread.paused:
            return
            
        fps = self.thread.cap.get(cv2.CAP_PROP_FPS)
        if fps > 0:
            current_second = self.thread.current_frame_position / fps
            self.progress_slider.setValue(int(current_second))
            
            # Update time label
            minutes, seconds = divmod(int(current_second), 60)
            total_minutes, total_seconds = divmod(int(self.duration), 60)
            self.time_label.setText(f"{minutes:02d}:{seconds:02d} / {total_minutes:02d}:{total_seconds:02d}")
    
    def handle_error(self, error_msg):
        QMessageBox.critical(self, "Error", error_msg)
    
    def cleanup(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()


class VideoEditor(QMainWindow):
    """Main application window for video editing"""
    def __init__(self):
        super().__init__()
        self.input_video_path = None
        self.output_video_paths = []
        self.recent_files = []
        self.max_recent_files = 5
        self.initUI()
        self.setup_system_tray()
        self.setup_file_associations()
        self.load_settings()
        
        # Check if app was launched with a file argument
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            self.open_file_from_args(sys.argv[1])
    
    def initUI(self):
        self.setWindowTitle("MOHD HABIB Pro Video Editor")
        self.setGeometry(100, 100, 1280, 720)
        
        # Set application icon
        app_icon = self.create_app_icon()
        if app_icon:
            self.setWindowIcon(app_icon)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2D2D30;
                color: #E0E0E0;
            }
            QWidget {
                background-color: #2D2D30;
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1C97EA;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLabel {
                color: #E0E0E0;
            }
            QSlider {
                height: 20px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #3D3D3D;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078D7;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 8px;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #3D3D3D;
            }
            QProgressBar::chunk {
                background-color: #0078D7;
                border-radius: 5px;
            }
            QListWidget {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #444444;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
            }
            QSplitter::handle {
                background-color: #555555;
            }
            QMenuBar {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #333333;
            }
            QMenu {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #555555;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #0078D7;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_title = QLabel("MOHD HABIB Video Editor Pro")
        main_title.setFont(QFont('Arial', 24, QFont.Bold))
        main_title.setAlignment(Qt.AlignCenter)
        main_title.setStyleSheet("color: #0078D7; padding: 20px;")
        main_layout.addWidget(main_title)
        
        # Splitter for preview and editing sections
        main_splitter = QSplitter(Qt.Vertical)
        
        # Preview section
        preview_widget = QWidget()
        preview_layout = QHBoxLayout(preview_widget)
        
        # Input video preview
        self.input_preview = VideoPreviewWidget("Input Video")
        preview_layout.addWidget(self.input_preview)
        
        # Output video preview
        self.output_preview = VideoPreviewWidget("Output Video")
        preview_layout.addWidget(self.output_preview)
        
        main_splitter.addWidget(preview_widget)
        
        # Editing section
        editing_widget = QWidget()
        editing_layout = QVBoxLayout(editing_widget)
        
        # Video operations section (trim and merge)
        operations_layout = QHBoxLayout()
        
        # Trim section
        trim_frame = QFrame()
        trim_frame.setFrameShape(QFrame.StyledPanel)
        trim_layout = QVBoxLayout(trim_frame)
        
        trim_title = QLabel("Trim Video")
        trim_title.setFont(QFont('Arial', 12, QFont.Bold))
        trim_layout.addWidget(trim_title)
        
        load_btn = QPushButton("Load Video")
        load_btn.clicked.connect(self.load_input_video)
        trim_layout.addWidget(load_btn)
        
        # Trim sliders
        sliders_layout = QHBoxLayout()
        
        # Start time slider
        start_layout = QVBoxLayout()
        start_label = QLabel("Start Time (min)")
        start_layout.addWidget(start_label)
        
        self.start_slider = QSlider(Qt.Horizontal)
        self.start_slider.setEnabled(False)
        self.start_slider.valueChanged.connect(self.update_trim_values)
        start_layout.addWidget(self.start_slider)
        
        self.start_time_label = QLabel("00:00")
        self.start_time_label.setAlignment(Qt.AlignCenter)
        start_layout.addWidget(self.start_time_label)
        
        sliders_layout.addLayout(start_layout)
        
        # End time slider
        end_layout = QVBoxLayout()
        end_label = QLabel("End Time (min)")
        end_layout.addWidget(end_label)
        
        self.end_slider = QSlider(Qt.Horizontal)
        self.end_slider.setEnabled(False)
        self.end_slider.valueChanged.connect(self.update_trim_values)
        end_layout.addWidget(self.end_slider)
        
        self.end_time_label = QLabel("00:00")
        self.end_time_label.setAlignment(Qt.AlignCenter)
        end_layout.addWidget(self.end_time_label)
        
        sliders_layout.addLayout(end_layout)
        
        trim_layout.addLayout(sliders_layout)
        
        # Trim button
        self.trim_btn = QPushButton("Trim Video")
        self.trim_btn.clicked.connect(self.trim_video)
        trim_layout.addWidget(self.trim_btn)
        
        operations_layout.addWidget(trim_frame)
        
        # Merge section
        merge_frame = QFrame()
        merge_frame.setFrameShape(QFrame.StyledPanel)
        merge_layout = QVBoxLayout(merge_frame)
        
        merge_title = QLabel("Merge Videos")
        merge_title.setFont(QFont('Arial', 12, QFont.Bold))
        merge_layout.addWidget(merge_title)
        
        # Video list
        self.video_list = QListWidget()
        self.video_list.setAcceptDrops(True)  # Enable drag & drop
        merge_layout.addWidget(self.video_list)
        
        # In the initUI method, right after creating the video_list:
        self.video_list = QListWidget()
        self.video_list.setAcceptDrops(True)  # Enable drag & drop
        self.video_list.installEventFilter(self)  # Install event filter for double-click
        merge_layout.addWidget(self.video_list)
        
        # Buttons for merge operations
        merge_buttons_layout = QHBoxLayout()
        
        self.add_video_btn = QPushButton("Add Video")
        self.add_video_btn.clicked.connect(self.add_video_to_merge)
        merge_buttons_layout.addWidget(self.add_video_btn)
        
        self.remove_video_btn = QPushButton("Remove Video")
        self.remove_video_btn.clicked.connect(self.remove_video_from_merge)
        merge_buttons_layout.addWidget(self.remove_video_btn)
        
        self.move_up_btn = QPushButton("Move Up")
        self.move_up_btn.clicked.connect(self.move_video_up)
        merge_buttons_layout.addWidget(self.move_up_btn)
        
        move_down_btn = QPushButton("Move Down")
        move_down_btn.clicked.connect(self.move_video_down)
        merge_buttons_layout.addWidget(move_down_btn)
        
        merge_layout.addLayout(merge_buttons_layout)
        
        # Merge button
        self.merge_btn = QPushButton("Merge Videos")
        self.merge_btn.clicked.connect(self.merge_videos)
        merge_layout.addWidget(self.merge_btn)
        
        operations_layout.addWidget(merge_frame)
        
        editing_layout.addLayout(operations_layout)
        
        # Progress section
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        progress_layout.addWidget(self.status_label)
        
        editing_layout.addLayout(progress_layout)
        
        main_splitter.addWidget(editing_widget)
        
        # Adjust the sizes of the splitter
        main_splitter.setSizes([400, 300])
        
        main_layout.addWidget(main_splitter)
        
        self.setCentralWidget(central_widget)
        
        # Set up processing thread
        self.processing_thread = None
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        open_action = QAction("&Open Video", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_input_video)
        file_menu.addAction(open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("&Recent Files")
        self.update_recent_files_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        trim_action = QAction("&Trim Video", self)
        trim_action.triggered.connect(self.trim_video)
        tools_menu.addAction(trim_action)
        
        merge_action = QAction("&Merge Videos", self)
        merge_action.triggered.connect(self.merge_videos)
        tools_menu.addAction(merge_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_app_icon(self):
        """Create a basic icon for the application"""
        try:
            # Create a simple icon as a QIcon
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            return QIcon(pixmap)
        except Exception:
            return None
    
    def setup_system_tray(self):
        """Setup system tray icon and menu"""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.windowIcon())
            
            # Create tray menu
            tray_menu = QMenu()
            
            open_action = QAction("Open Video Editor", self)
            open_action.triggered.connect(self.showNormal)
            tray_menu.addAction(open_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
            # Connect double click to show window
            self.tray_icon.activated.connect(self.tray_icon_activated)
        except Exception:
            # System tray might not be available on all platforms
            pass
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showNormal()
    
    def setup_file_associations(self):
        """Setup file associations for common video formats (platform specific)"""
        # This would be implemented differently depending on the OS
        # This is a mock implementation - actual implementation would require
        # platform-specific code (registry for Windows, .desktop files for Linux, etc.)
        pass
    
    def load_settings(self):
        """Load application settings from file"""
        # TODO: Implement loading settings from file
        # For simplicity, we're not implementing this yet, but would include:
        # - Recent files
        # - Window position/size
        # - Default output folder
        # - User preferences
        pass
    
    def save_settings(self):
        """Save application settings to file"""
        # TODO: Implement saving settings to file
        pass
    
    def open_file_from_args(self, file_path):
        """Open a file passed as command line argument"""
        if os.path.isfile(file_path):
            self.input_video_path = file_path
            self.input_preview.load_video(file_path)
            self.status_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.add_to_recent_files(file_path)
            
            # Set up the trim sliders
            try:
                clip = VideoFileClip(file_path)
                duration_seconds = clip.duration
                clip.close()
                
                self.start_slider.setRange(0, int(duration_seconds))
                self.end_slider.setRange(0, int(duration_seconds))
                self.end_slider.setValue(int(duration_seconds))
                
                self.start_slider.setEnabled(True)
                self.end_slider.setEnabled(True)
                
                self.update_trim_values()
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Error getting video duration: {str(e)}")
    
    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        self.recent_files.insert(0, file_path)
        
        # Limit the number of recent files
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
        
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        self.recent_menu.clear()
        
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.setData(file_path)
            action.triggered.connect(self.open_recent_file)
            self.recent_menu.addAction(action)
        
        if not self.recent_files:
            no_recent = QAction("No recent files", self)
            no_recent.setEnabled(False)
            self.recent_menu.addAction(no_recent)
        else:
            self.recent_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_menu.addAction(clear_action)
    
    def open_recent_file(self):
        """Open a file from the recent files menu"""
        action = self.sender()
        if action:
            file_path = action.data()
            if os.path.isfile(file_path):
                self.open_file_from_args(file_path)
            else:
                QMessageBox.warning(self, "Warning", f"File not found: {file_path}")
                self.recent_files.remove(file_path)
                self.update_recent_files_menu()
    
    def clear_recent_files(self):
        """Clear the recent files list"""
        self.recent_files = []
        self.update_recent_files_menu()
    
    def load_input_video(self):
        """Load a video file for editing"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", 
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv);;All Files (*)", 
            options=options
        )
        
        if file_path:
            self.open_file_from_args(file_path)
    
    def update_trim_values(self):
        """Update the display of trim values when sliders change"""
        start_seconds = self.start_slider.value()
        end_seconds = self.end_slider.value()
        
        # Ensure end time is after start time
        if end_seconds <= start_seconds:
            end_seconds = start_seconds + 1
            self.end_slider.setValue(end_seconds)
        
        # Update labels
        start_minutes, start_seconds = divmod(start_seconds, 60)
        self.start_time_label.setText(f"{start_minutes:02d}:{start_seconds:02d}")
        
        end_minutes, end_seconds = divmod(end_seconds, 60)
        self.end_time_label.setText(f"{end_minutes:02d}:{end_seconds:02d}")
    
    # Replace the complex progress monitoring with simplified version:
    def trim_video(self):
        """Trim the loaded video using the selected start and end times"""
        if not self.input_video_path:
            QMessageBox.warning(self, "Warning", "Please load a video first")
            return
        
        start_seconds = self.start_slider.value()
        end_seconds = self.end_slider.value()
        
        # Ensure end time is after start time
        if end_seconds <= start_seconds:
            QMessageBox.warning(self, "Warning", "End time must be after start time")
            return
        
        # Ask for output file
        options = QFileDialog.Options()
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Trimmed Video", "", 
            "MP4 Files (*.mp4);;All Files (*)", 
            options=options
        )
        
        if not output_path:
            return
        
        # Add .mp4 extension if not present
        if not output_path.lower().endswith('.mp4'):
            output_path += '.mp4'
        
        # Show progress
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Trimming video...")
        
        # Process in thread
        params = {
            'input_path': self.input_video_path,
            'output_path': output_path,
            'start_time': start_seconds,
            'end_time': end_seconds
        }
        
        self.processing_thread = VideoProcessingThread('trim', params)
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.finished.connect(self.on_trim_completed)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()
    
    def add_video_to_merge(self):
        """Add a video to the merge list"""
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Videos to Add", "", 
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv);;All Files (*)", 
            options=options
        )
        
        for file_path in files:
            if file_path:
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                self.video_list.addItem(item)
    
    def remove_video_from_merge(self):
        """Remove selected video from the merge list"""
        selected_items = self.video_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            self.video_list.takeItem(self.video_list.row(item))
    
    def move_video_up(self):
        """Move selected video up in the merge list"""
        current_row = self.video_list.currentRow()
        if current_row <= 0:
            return
            
        item = self.video_list.takeItem(current_row)
        self.video_list.insertItem(current_row - 1, item)
        self.video_list.setCurrentItem(item)
    
    def move_video_down(self):
        """Move selected video down in the merge list"""
        current_row = self.video_list.currentRow()
        if current_row < 0 or current_row >= self.video_list.count() - 1:
            return
            
        item = self.video_list.takeItem(current_row)
        self.video_list.insertItem(current_row + 1, item)
        self.video_list.setCurrentItem(item)
    
    def merge_videos(self):
        """Merge the videos in the list while preserving video quality"""
        count = self.video_list.count()
        if count < 2:
            QMessageBox.warning(self, "Warning", "Please add at least two videos to merge")
            return
        
        # Get all video paths
        video_paths = []
        for i in range(count):
            item = self.video_list.item(i)
            path = item.data(Qt.UserRole)
            if not os.path.exists(path):
                QMessageBox.warning(self, "Error", f"File not found: {path}")
                return
            video_paths.append(path)
        
        # Ask for output file
        options = QFileDialog.Options()
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save Merged Video", "", 
            "MP4 Files (*.mp4);;All Files (*)", 
            options=options
        )
        
        if not output_path:
            return
        
        # Add .mp4 extension if not present
        if not output_path.lower().endswith('.mp4'):
            output_path += '.mp4'
        
        # Check if output file already exists
        if os.path.exists(output_path):
            reply = QMessageBox.question(
                self, "File Exists", 
                f"The file {os.path.basename(output_path)} already exists. Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Check if we have write permission for the output directory
        output_dir = os.path.dirname(output_path)
        if not os.access(output_dir, os.W_OK):
            QMessageBox.warning(self, "Error", f"No write permission for directory: {output_dir}")
            return
        
        # Get first video info to determine output settings
        try:
            first_video_info = self.get_video_info(video_paths[0])
            resolution = first_video_info.get('resolution', '1920x1080')
            fps = first_video_info.get('fps', 30)
            codec = first_video_info.get('codec', 'h264')
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to analyze video: {str(e)}")
            return
        
        # Advanced options dialog for merge
        merge_options = self.show_merge_options_dialog(resolution, fps, codec)
        if not merge_options:
            return  # User cancelled
        
        # Show progress
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Preparing to merge {count} videos...")
        
        # Process in thread
        params = {
            'video_paths': video_paths,
            'output_path': output_path,
            'resolution': merge_options['resolution'],
            'fps': merge_options['fps'],
            'codec': merge_options['codec'],
            'bitrate': merge_options['bitrate']
        }
        
        # Disable UI elements during processing
        self.toggle_ui_elements(False)
        
        self.processing_thread = VideoProcessingThread('merge', params)
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.finished.connect(self.on_merge_completed)
        self.processing_thread.error.connect(self.on_processing_error)
        self.processing_thread.start()
    
    def show_merge_options_dialog(self, default_resolution, default_fps, default_codec):
        """Show dialog for advanced merge options"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Merge Options")
        layout = QVBoxLayout()
        
        # Resolution options
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("Resolution:"))
        resolution_combo = QComboBox()
        common_resolutions = ["Original", "3840x2160", "1920x1080", "1280x720", "854x480", "640x360"]
        resolution_combo.addItems(common_resolutions)
        resolution_combo.setCurrentText("Original")
        resolution_layout.addWidget(resolution_combo)
        layout.addLayout(resolution_layout)
        
        # FPS options
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Frame Rate:"))
        fps_combo = QComboBox()
        fps_options = ["Original", "60", "30", "24"]
        fps_combo.addItems(fps_options)
        fps_combo.setCurrentText("Original")
        fps_layout.addWidget(fps_combo)
        layout.addLayout(fps_layout)
        
        # Codec options
        codec_layout = QHBoxLayout()
        codec_layout.addWidget(QLabel("Codec:"))
        codec_combo = QComboBox()
        codec_options = ["h264", "h265", "vp9"]
        codec_combo.addItems(codec_options)
        codec_combo.setCurrentText(default_codec)
        codec_layout.addWidget(codec_combo)
        layout.addLayout(codec_layout)
        
        # Bitrate options
        bitrate_layout = QHBoxLayout()
        bitrate_layout.addWidget(QLabel("Bitrate (Mbps):"))
        bitrate_spinbox = QSpinBox()
        bitrate_spinbox.setRange(1, 50)
        bitrate_spinbox.setValue(8)  # Default 8 Mbps
        bitrate_layout.addWidget(bitrate_spinbox)
        layout.addLayout(bitrate_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            return {
                'resolution': resolution_combo.currentText(),
                'fps': fps_combo.currentText(),
                'codec': codec_combo.currentText(),
                'bitrate': bitrate_spinbox.value()
            }
        return None
    
    def get_video_info(self, video_path):
        """Extract video information using ffprobe"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-select_streams', 'v:0', 
                 '-show_entries', 'stream=width,height,r_frame_rate,codec_name', 
                 '-of', 'json', video_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {'resolution': '1920x1080', 'fps': 30, 'codec': 'h264'}
            
            info = json.loads(result.stdout)
            stream = info.get('streams', [{}])[0]
            
            width = stream.get('width', 1920)
            height = stream.get('height', 1080)
            resolution = f"{width}x{height}"
            
            fps_fraction = stream.get('r_frame_rate', '30/1')
            fps_parts = fps_fraction.split('/')
            fps = round(float(fps_parts[0]) / float(fps_parts[1])) if len(fps_parts) == 2 else 30
            
            codec = stream.get('codec_name', 'h264')
            
            return {'resolution': resolution, 'fps': fps, 'codec': codec}
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return {'resolution': '1920x1080', 'fps': 30, 'codec': 'h264'}
    
    def toggle_ui_elements(self, enabled):
        """Enable or disable UI elements during processing"""
        # Use the correct button names from your VideoEditor class
        self.add_video_btn.setEnabled(enabled)
        self.remove_video_btn.setEnabled(enabled)
        self.merge_btn.setEnabled(enabled)
        self.trim_btn.setEnabled(enabled)
        self.video_list.setEnabled(enabled)
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.setText(message)
    
    def on_merge_completed(self, output_path):
        """Called when merge is completed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Merge completed successfully")
        self.toggle_ui_elements(True)
        
        reply = QMessageBox.question(
            self, "Merge Complete", 
            "Videos merged successfully. Do you want to open the output file?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            self.open_file(output_path)
        
        # Add to recent files
        self.add_to_recent_files(output_path)
    
    def open_file(self, path):
        """Open a file with the default system application"""
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', path])
        else:  # Linux and other Unix-like
            subprocess.call(['xdg-open', path])
    
    def update_progress(self, value):
        """Update the progress bar"""
        self.progress_bar.setValue(value)
    
    def on_trim_completed(self, output_path):
        """Called when trim operation is completed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Trim completed")
        
        # Add to output list
        self.output_video_paths.append(output_path)
        
        # Load the output video in the preview
        self.output_preview.load_video(output_path)
        
        QMessageBox.information(self, "Success", f"Video trimmed successfully:\n{output_path}")
    
    def on_merge_completed(self, output_path):
        """Called when merge operation is completed"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Merge completed")
        
        # Add to output list
        self.output_video_paths.append(output_path)
        
        # Load the output video in the preview
        self.output_preview.load_video(output_path)
        
        QMessageBox.information(self, "Success", f"Videos merged successfully:\n{output_path}")
    
    def on_processing_error(self, error_msg):
        """Called when processing error occurs"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Error occurred")
        
        QMessageBox.critical(self, "Error", error_msg)
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About MOHD HABIB Video Editor",
            "MOHD HABIB Video Editor Pro v1.0\n\n"
            "A simple video editor for trimming and merging videos.\n\n"
            "Developed by Mohamed Hussien(afifi)."
        )
    
    # Implement double-click functionality for video list
    def eventFilter(self, obj, event):
        """Handle events for objects with event filter installed"""
        if obj is self.video_list and event.type() == event.MouseButtonDblClick:
            self.on_video_list_double_click()
            return True
        return super().eventFilter(obj, event)
    
    def on_video_list_double_click(self):
        """Handle double-click on a video in the list"""
        selected_item = self.video_list.currentItem()
        if selected_item:
            video_path = selected_item.data(Qt.UserRole)
            self.preview_merge_video(video_path)
    
    def preview_merge_video(self, video_path):
        """Preview a video from the merge list"""
        if os.path.isfile(video_path):
            self.input_preview.load_video(video_path)
            self.status_label.setText(f"Previewing: {os.path.basename(video_path)}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Clean up threads
        if self.input_preview:
            self.input_preview.cleanup()
        
        if self.output_preview:
            self.output_preview.cleanup()
        
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.terminate()
            self.processing_thread.wait()
        
        # Save settings
        self.save_settings()
        
        # Hide to tray instead of closing completely
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
            event.accept()  # Accept the close event
            QApplication.quit()  # 
        # Perform any cleanup here if needed
        event.accept()  # Accept the close event
        QApplication.quit()  # Explicitly quit the application


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = VideoEditor()
    window.destroyed.connect(lambda: QApplication.quit())
    window.show()
    
    sys.exit(app.exec_())