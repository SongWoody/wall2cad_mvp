"""
Wall2CAD MVP - Main Window UI
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QStatusBar, QMenuBar, QMenu, 
                            QAction, QFileDialog, QMessageBox, QProgressBar,
                            QFrame, QSplashScreen)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches
import numpy as np
import cv2

from sam_processor import SAMProcessor
from dxf_converter import DXFConverter

class SAMModelLoader(QThread):
    """SAM model loading thread"""
    progress = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished = pyqtSignal(object)  # SAMProcessor instance
    error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        try:
            self.progress.emit(10)
            self.status_update.emit("모델 파일 확인 중...")
            
            self.progress.emit(30)
            self.status_update.emit("SAM 모델 로딩 중... (2-3분 소요)")
            
            sam_processor = SAMProcessor()
            
            self.progress.emit(90)
            self.status_update.emit("모델 초기화 완료")
            
            self.finished.emit(sam_processor)
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(str(e))

class SAMWorkerThread(QThread):
    """SAM processing worker thread to prevent UI blocking"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)  # masks
    error = pyqtSignal(str)
    
    def __init__(self, sam_processor, image_path):
        super().__init__()
        self.sam_processor = sam_processor
        self.image_path = image_path
        
    def run(self):
        try:
            # Load and process image
            self.progress.emit(10)
            image = cv2.imread(self.image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            self.progress.emit(30)
            masks = self.sam_processor.generate_masks(image)
            
            self.progress.emit(90)
            self.finished.emit({'masks': masks, 'image': image, 'path': self.image_path})
            self.progress.emit(100)
            
        except Exception as e:
            self.error.emit(str(e))

class ImageCanvas(FigureCanvas):
    """Custom matplotlib canvas for image display"""
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 8), facecolor='white')
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')
        self.fig.tight_layout()
        
        # Initial empty state
        self.ax.text(0.5, 0.5, 'No image loaded\n\nClick "Load Image" to start', 
                    ha='center', va='center', fontsize=12, color='gray',
                    transform=self.ax.transAxes)
        
        self.current_image = None
        self.current_masks = None
        
    def display_image_only(self, image):
        """Display image without masks"""
        self.ax.clear()
        self.ax.imshow(image)
        self.ax.axis('off')
        self.ax.set_title('Original Image', fontsize=12, pad=10)
        self.current_image = image
        self.draw()
        
    def display_result(self, image, masks):
        """Display image with mask overlays"""
        self.ax.clear()
        self.ax.imshow(image)
        
        # Draw mask contours
        for mask_data in masks:
            mask = mask_data['segmentation']
            mask_uint8 = (mask.astype(np.uint8)) * 255
            
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                cnt = cnt.squeeze()
                if len(cnt.shape) == 2 and cnt.shape[0] >= 3:
                    self.ax.plot(cnt[:, 0], cnt[:, 1], linewidth=1.5, color='red', alpha=0.8)
        
        self.ax.axis('off')
        self.ax.set_title(f'Result: {len(masks)} masks detected', fontsize=12, pad=10)
        self.current_image = image
        self.current_masks = masks
        self.draw()

class LoadingSplash(QSplashScreen):
    """Custom loading splash screen"""
    
    def __init__(self):
        # Create a simple splash screen image
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Add text
        self.showMessage(
            "Wall2CAD MVP\n\nAI 모델 로딩 중...\n잠시만 기다려주세요.",
            Qt.AlignCenter,
            Qt.black
        )
        
    def update_message(self, message, progress=0):
        """Update splash screen message"""
        full_message = f"Wall2CAD MVP\n\n{message}\n\n{progress}% 완료"
        self.showMessage(full_message, Qt.AlignCenter, Qt.black)
        self.repaint()  # Force immediate update

class MainWindow(QMainWindow):
    def __init__(self, splash=None):
        super().__init__()
        self.current_image_path = None
        self.current_result = None
        self.sam_processor = None
        self.dxf_converter = DXFConverter()
        self.splash = splash
        
        self.init_ui()
        self.init_sam_processor()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Wall2CAD MVP v1.0")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Top button bar
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load Image")
        self.load_btn.setMinimumHeight(40)
        self.load_btn.clicked.connect(self.load_image)
        
        self.export_btn = QPushButton("Export DXF")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_dxf)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        
        # Image canvas
        self.canvas = ImageCanvas(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Info label
        self.info_label = QLabel("Ready - Load an image to start")
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        
        # Add to layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.canvas, 1)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.info_label)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Menu bar
        self.create_menu_bar()
        
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Image...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.load_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About...', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def init_sam_processor(self):
        """Initialize SAM processor in background"""
        self.status_bar.showMessage("AI 모델 로딩 중...")
        self.info_label.setText("AI 모델을 로딩 중입니다... 2-3분 정도 소요됩니다.")
        
        # Disable buttons during loading
        self.load_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start model loading in background thread
        self.model_loader = SAMModelLoader()
        self.model_loader.progress.connect(self.on_model_loading_progress)
        self.model_loader.status_update.connect(self.on_model_loading_status)
        self.model_loader.finished.connect(self.on_model_loading_finished)
        self.model_loader.error.connect(self.on_model_loading_error)
        self.model_loader.start()
        
    def on_model_loading_progress(self, progress):
        """Handle model loading progress"""
        self.progress_bar.setValue(progress)
        if self.splash:
            self.splash.update_message("AI 모델 로딩 중...", progress)
            
    def on_model_loading_status(self, status):
        """Handle model loading status update"""
        self.info_label.setText(status)
        self.status_bar.showMessage(status)
        if self.splash:
            self.splash.update_message(status, self.progress_bar.value())
            
    def on_model_loading_finished(self, sam_processor):
        """Handle model loading completion"""
        self.sam_processor = sam_processor
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.info_label.setText("준비 완료 - 이미지를 로드하여 시작하세요")
        self.status_bar.showMessage("준비 완료")
        
        # Close splash screen
        if self.splash:
            self.splash.finish(self)
            
    def on_model_loading_error(self, error_msg):
        """Handle model loading error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "오류", f"AI 모델 로딩 실패:\n{error_msg}")
        self.info_label.setText("AI 모델 로딩 오류 - 애플리케이션을 재시작해주세요")
        self.status_bar.showMessage("오류")
        
        # Close splash screen
        if self.splash:
            self.splash.finish(self)
            
    def load_image(self):
        """Load and process image"""
        if not self.sam_processor:
            QMessageBox.warning(self, "경고", "AI 모델이 아직 로딩 중입니다. 잠시 기다려주세요.")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Image", 
            "", 
            "Image files (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.current_image_path = file_path
            self.process_image(file_path)
            
    def process_image(self, image_path):
        """Process image with SAM"""
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.info_label.setText("이미지 처리 중... 몇 분 정도 소요됩니다.")
        self.status_bar.showMessage("처리 중...")
        
        # Load and display image first
        try:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            self.canvas.display_image_only(image)
        except Exception as e:
            self.show_error(f"Failed to load image: {str(e)}")
            return
            
        # Start SAM processing in background thread
        self.worker_thread = SAMWorkerThread(self.sam_processor, image_path)
        self.worker_thread.progress.connect(self.progress_bar.setValue)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.error.connect(self.on_processing_error)
        self.worker_thread.start()
        
    def on_processing_finished(self, result):
        """Handle SAM processing completion"""
        self.current_result = result
        
        # Display result
        self.canvas.display_result(result['image'], result['masks'])
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        mask_count = len(result['masks'])
        self.info_label.setText(f"처리 완료 - {mask_count}개 마스크 감지됨")
        self.status_bar.showMessage(f"준비 완료 - {mask_count}개 마스크 감지됨")
        
    def on_processing_error(self, error_msg):
        """Handle SAM processing error"""
        self.show_error(f"Processing failed: {error_msg}")
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        
    def export_dxf(self):
        """Export current result to DXF"""
        if not self.current_result:
            QMessageBox.warning(self, "Warning", "No processed image to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save DXF File",
            "",
            "DXF files (*.dxf)"
        )
        
        if file_path:
            try:
                self.dxf_converter.export_masks_to_dxf(
                    self.current_result['masks'],
                    self.current_result['image'].shape,
                    file_path
                )
                
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"DXF file saved successfully:\n{file_path}"
                )
                self.status_bar.showMessage(f"DXF exported: {os.path.basename(file_path)}")
                
            except Exception as e:
                self.show_error(f"Failed to export DXF: {str(e)}")
                
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
        self.info_label.setText("오류 발생 - 자세한 내용은 대화상자를 확인하세요")
        self.status_bar.showMessage("오류")
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Wall2CAD MVP",
            "Wall2CAD MVP v1.0\n\n"
            "AI-powered image segmentation to DXF conversion tool\n"
            "Built with SAM (Segment Anything Model)\n\n"
            "© 2025 Wall2CAD Project"
        )