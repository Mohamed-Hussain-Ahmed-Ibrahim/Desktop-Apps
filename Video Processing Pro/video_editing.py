import sys
import os
from datetime import timedelta

import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QFileDialog, QListWidget, QWidget, QMessageBox, 
    QDialog, QDialogButtonBox, QProgressBar
)
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

from moviepy.editor import VideoFileClip, concatenate_videoclips

class VideoProcessingThread(QThread):
    """Thread to handle video processing to keep UI responsive"""
    progress_updated = pyqtSignal(int)
    processing_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, process_type, *args):
        super().__init__()
        self.process_type = process_type
        self.args = args

    def run(self):
        try:
            if self.process_type == 'split':
                input_video, output_path, start_time, end_time = self.args
                
                # Create subclip
                split_clip = input_video.subclip(start_time, end_time)
                
                # Write video 
                split_clip.write_videofile(
                    output_path, 
                    logger=None,
                    write_logfile=False
                )
                
                input_video.close()
                split_clip.close()
                
                self.processing_complete.emit(output_path)
            
            elif self.process_type == 'merge':
                video_paths, output_path = self.args
                
                # Load video clips
                clips = [VideoFileClip(clip) for clip in video_paths]
                
                # Concatenate clips
                final_clip = concatenate_videoclips(clips)
                
                # Write merged video 
                final_clip.write_videofile(
                    output_path, 
                    logger=None,
                    write_logfile=False
                )
                
                # Clean up
                for clip in clips:
                    clip.close()
                final_clip.close()
                
                self.processing_complete.emit(output_path)
        
        except Exception as e:
            self.error_occurred.emit(str(e))


class VideoSelectionDialog(QDialog):
    def __init__(self, videos, parent=None):
        super().__init__(parent)
        self.setWindowTitle('MOHD HABIB - Select Videos to Merge')
        self.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # Video list for selection
        self.video_list = QListWidget()
        self.video_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Populate list with videos
        for video in videos:
            self.video_list.addItem(os.path.basename(video))
        
        layout.addWidget(QLabel('Select at least 2 videos to merge:'))
        layout.addWidget(self.video_list)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_selected_videos(self, original_videos):
        # Get indices of selected items
        selected_indices = [item.row() for item in self.video_list.selectedIndexes()]
        
        # Return corresponding video paths
        return [original_videos[i] for i in selected_indices]


class VideoEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.current_video = None
        self.loaded_videos = []
        self.video_clips = []
        self.processing_thread = None

    def initUI(self):
        """Initialize the main user interface."""
        self.setWindowTitle('MOHD HABIB - Video Editor Pro')
        self.setGeometry(100, 100, 1100, 750)
        
        # Set a modern, dark color scheme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
                color: #ECF0F1;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QSlider::groove:horizontal {
                background: #34495E;
                height: 10px;
                border-radius: 5px;
            }
            QSlider::handle:horizontal {
                background: #3498DB;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -4px 0;
            }
            QListWidget {
                background-color: #34495E;
                color: #ECF0F1;
                border: none;
            }
            QProgressBar {
                border: 2px solid #34495E;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498DB;
                width: 10px;
                margin: 0.5px;
            }
        """)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title Label
        title_label = QLabel('MOHD HABIB - Video Editor Pro')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ECF0F1;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(title_label)
        
        # Main content layout
        content_layout = QHBoxLayout()
        
        # Left panel for video display and controls
        left_panel = QVBoxLayout()
        
        # Video display area
        self.video_label = QLabel('Load a video to start')
        self.video_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.video_label)
        
        # Time display
        self.time_label = QLabel('00:00:00 / 00:00:00')
        self.time_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.time_label)
        
        # Playback slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderMoved.connect(self.slider_moved)
        left_panel.addWidget(self.slider)
        
        # Control buttons
        button_layout = QHBoxLayout()
        buttons = [
            ('Load Video', self.load_video),
            ('Play/Pause', self.toggle_playback),
            ('Set Start', self.set_start_point),
            ('Set End', self.set_end_point)
        ]
        
        for text, method in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(method)
            button_layout.addWidget(btn)
        
        left_panel.addLayout(button_layout)
        
        # Right panel for video list and processing
        right_panel = QVBoxLayout()
        
        # Video list
        self.video_list = QListWidget()
        right_panel.addWidget(self.video_list)
        
        # Processing buttons
        process_layout = QHBoxLayout()
        process_buttons = [
            ('Split Video', self.split_video),
            ('Merge Videos', self.merge_videos),
            ('Clear List', self.clear_video_list)
        ]
        
        for text, method in process_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(method)
            process_layout.addWidget(btn)
        
        right_panel.addLayout(process_layout)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        right_panel.addWidget(self.progress_bar)
        
        # Combine layouts
        content_layout.addLayout(left_panel, 2)
        content_layout.addLayout(right_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Video playback timer
        self.play_timer = QTimer()
        self.play_timer.timeout.connect(self.update_frame)
        
        # Playback state variables
        self.is_playing = False
        self.start_point = 0
        self.end_point = 0
        self.current_frame = 0
    
    def split_video(self):
        """Split the video based on selected start and end points with user-selected save location."""
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            QMessageBox.warning(self, 'Error', 'No video loaded')
            return
        
        if self.start_point >= self.end_point:
            QMessageBox.warning(self, 'Error', 'Invalid start/end points')
            return
        
        try:
            # Open file dialog to choose save location
            output_path, _ = QFileDialog.getSaveFileName(
                self, 
                'Save Split Video', 
                '', 
                'Video Files (*.mp4);;All Files (*)'
            )
            
            # If user cancels save dialog
            if not output_path:
                return
            
            # Ensure file has .mp4 extension
            if not output_path.lower().endswith('.mp4'):
                output_path += '.mp4'
            
            input_video = VideoFileClip(self.loaded_videos[-1])
            start_time = self.start_point / self.fps
            end_time = self.end_point / self.fps
            
            # Reset and show progress bar
            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)
            
            # Create and start processing thread
            self.processing_thread = VideoProcessingThread(
                'split', 
                input_video, 
                output_path, 
                start_time, 
                end_time
            )
            
            # Connect thread signals
            self.processing_thread.processing_complete.connect(self.on_processing_complete)
            self.processing_thread.error_occurred.connect(self.on_processing_error)
            
            # Start processing
            self.processing_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Could not prepare video splitting: {str(e)}')
    
    def merge_videos(self):
        """Merge selected videos into a single output file."""
        # Check if there are enough videos to merge
        if len(self.loaded_videos) < 2:
            QMessageBox.warning(self, 'Error', 'Load at least 2 videos first')
            return
        
        # Open video selection dialog
        selection_dialog = VideoSelectionDialog(self.loaded_videos, self)
        
        # If dialog is accepted
        if selection_dialog.exec_() == QDialog.Accepted:
            # Get selected video paths
            selected_videos = selection_dialog.get_selected_videos(self.loaded_videos)
            
            # Ensure at least 2 videos are selected
            if len(selected_videos) < 2:
                QMessageBox.warning(self, 'Error', 'Select at least 2 videos to merge')
                return
            
            try:
                # Open file dialog to choose save location
                output_path, _ = QFileDialog.getSaveFileName(
                    self, 
                    'Save Merged Video', 
                    '', 
                    'Video Files (*.mp4);;All Files (*)'
                )
                
                # If user cancels save dialog
                if not output_path:
                    return
                
                # Ensure file has .mp4 extension
                if not output_path.lower().endswith('.mp4'):
                    output_path += '.mp4'
                
                # Reset and show progress bar
                self.progress_bar.setValue(0)
                self.progress_bar.setVisible(True)
                
                # Create and start processing thread
                self.processing_thread = VideoProcessingThread(
                    'merge', 
                    selected_videos, 
                    output_path
                )
                
                # Connect thread signals
                self.processing_thread.processing_complete.connect(self.on_processing_complete)
                self.processing_thread.error_occurred.connect(self.on_processing_error)
                
                # Start processing
                self.processing_thread.start()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not prepare video merging: {str(e)}')
    
    def on_processing_complete(self, output_path):
        """Handle successful video processing"""
        self.progress_bar.setValue(100)
        self.video_clips.append(output_path)
        self.video_list.addItem(f'Processed: {os.path.basename(output_path)}')
        QMessageBox.information(self, 'Success', f'Video processed and saved to:\n{output_path}')
        self.progress_bar.setValue(0)
    
    
    def update_progress_bar(self, value):
        """Update progress bar during video processing."""
        self.progress_bar.setValue(value)

    

    def on_processing_error(self, error_message):
        """Handle processing errors"""
        QMessageBox.critical(self, 'Error', f'Could not process video: {error_message}')
        self.progress_bar.setValue(0)

    def clear_video_list(self):
        """Clear the video list and reset application state."""
        self.video_list.clear()
        self.loaded_videos.clear()
        self.video_clips.clear()

    def format_time(self, seconds):
        """Format time in HH:MM:SS."""
        return str(timedelta(seconds=int(seconds)))

    
    def slider_moved(self, position):
        """Handle slider movement to seek video."""
        self.current_frame = position
        self.update_frame()
        
    def toggle_playback(self):
        """Toggle video play/pause."""
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_timer.start(int(1000 / self.fps))
        else:
            self.play_timer.stop()
            
    def load_video(self):
        """Load a video file and prepare it for playback."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open Video File', 
            '', 
            'Video Files (*.mp4 *.avi *.mov *.mkv)'
        )
        
        if file_path:
            try:
                # Open video using OpenCV
                self.cap = cv2.VideoCapture(file_path)
                
                # Get video properties
                self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.duration = self.total_frames / self.fps
                
                # Configure slider
                self.slider.setRange(0, self.total_frames)
                
                # Update time label
                self.time_label.setText(f'00:00:00 / {self.format_time(self.duration)}')
                
                # Add to video list
                self.video_list.addItem(os.path.basename(file_path))
                self.loaded_videos.append(file_path)
                
                # Display first frame
                self.update_frame()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Could not load video: {str(e)}')

    def set_start_point(self):
        """Set the start point for video splitting."""
        self.start_point = self.current_frame
        QMessageBox.information(self, 'Start Point', f'Start point set at {self.format_time(self.start_point/self.fps)}')

    def set_end_point(self):
        """Set the end point for video splitting."""
        self.end_point = self.current_frame
        QMessageBox.information(self, 'End Point', f'End point set at {self.format_time(self.end_point/self.fps)}')

    def update_frame(self):
        """Update the video frame display."""
        if hasattr(self, 'cap') and self.cap.isOpened():
            # Set video to current frame
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            ret, frame = self.cap.read()
            
            if ret:
                # Convert frame to QImage
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale image to fit label
                pixmap = QPixmap.fromImage(qt_image).scaled(
                    self.video_label.width(), 
                    self.video_label.height(), 
                    Qt.KeepAspectRatio
                )
                self.video_label.setPixmap(pixmap)
                
                # Update time label and slider
                current_time = self.current_frame / self.fps
                self.time_label.setText(
                    f'{self.format_time(current_time)} / {self.format_time(self.duration)}'
                )
                self.slider.setValue(self.current_frame)
                
                # Increment frame if playing
                if self.is_playing:
                    self.current_frame += 1
                    
                    # Stop if reached end or selected end point
                    if (self.current_frame >= self.total_frames or 
                        (self.end_point > 0 and self.current_frame >= self.end_point)):
                        self.toggle_playback()

def main():
    app = QApplication(sys.argv)
    editor = VideoEditorApp()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()