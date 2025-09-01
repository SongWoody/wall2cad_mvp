"""
Wall2CAD MVP - Main Window UI
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QStatusBar, QMenuBar, QMenu, 
                            QAction, QFileDialog, QMessageBox, QProgressBar,
                            QFrame, QSplashScreen, QTextEdit, QSplitter,
                            QGroupBox, QCheckBox, QSpinBox, QSlider)
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
        """Display image with mask overlays with improved visualization"""
        self.ax.clear()
        self.ax.imshow(image)
        
        # Generate distinct colors for each mask
        colors = plt.cm.tab20(np.linspace(0, 1, min(len(masks), 20)))
        if len(masks) > 20:
            # Use rainbow colors for more masks
            colors = plt.cm.rainbow(np.linspace(0, 1, len(masks)))
        
        # Draw mask overlays and contours
        for i, mask_data in enumerate(masks):
            mask = mask_data['segmentation']
            area = mask_data.get('area', 0)
            stability_score = mask_data.get('stability_score', 0)
            
            # Color intensity based on mask quality
            alpha = max(0.3, min(0.8, stability_score))
            color = colors[i % len(colors)]
            
            # Create colored mask overlay
            colored_mask = np.zeros((*mask.shape, 4))
            colored_mask[mask] = [color[0], color[1], color[2], alpha * 0.4]
            self.ax.imshow(colored_mask)
            
            # Draw contours
            mask_uint8 = (mask.astype(np.uint8)) * 255
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for cnt in contours:
                cnt = cnt.squeeze()
                if len(cnt.shape) == 2 and cnt.shape[0] >= 3:
                    # Line width based on mask size
                    linewidth = max(0.8, min(2.5, area / 10000))
                    self.ax.plot(cnt[:, 0], cnt[:, 1], 
                               linewidth=linewidth, color=color[:3], alpha=0.9)
        
        self.ax.axis('off')
        
        # Enhanced title with statistics
        total_area = sum(mask['area'] for mask in masks)
        avg_score = sum(mask.get('stability_score', 0) for mask in masks) / len(masks) if masks else 0
        title = f'Result: {len(masks)} masks detected\nTotal area: {total_area:,} pixels, Avg quality: {avg_score:.2f}'
        self.ax.set_title(title, fontsize=11, pad=10)
        
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
        
        self.segment_btn = QPushButton("세그멘테이션 실행")
        self.segment_btn.setMinimumHeight(40)
        self.segment_btn.setEnabled(False)
        self.segment_btn.clicked.connect(self.run_segmentation)
        self.segment_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        
        self.export_btn = QPushButton("Export DXF")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.export_dxf)
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.segment_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.export_btn)
        
        # Image canvas
        self.canvas = ImageCanvas(self)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Info panel
        info_group = QGroupBox("마스크 정보")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel("Ready - Load an image to start")
        self.info_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        
        # Detailed info text area
        self.detail_info = QTextEdit()
        self.detail_info.setMaximumHeight(100)
        self.detail_info.setReadOnly(True)
        self.detail_info.setVisible(False)
        
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.detail_info)
        
        # Add to layout
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.canvas, 1)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(info_group)
        
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
        self.segment_btn.setEnabled(False)
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
        self.status_bar.showMessage("준비 완룼")
        
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
        """Load image only (without processing)"""
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
            try:
                # Load and display image
                image = cv2.imread(file_path)
                if image is None:
                    raise Exception("이미지를 로드할 수 없습니다")
                    
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.canvas.display_image_only(image)
                
                # Update state
                self.current_image_path = file_path
                self.current_result = None
                
                # Enable segmentation button
                self.segment_btn.setEnabled(True)
                self.export_btn.setEnabled(False)
                
                # Update info
                filename = os.path.basename(file_path)
                image_shape = image.shape
                self.info_label.setText(
                    f"이미지 로드 완료: {filename} ({image_shape[1]}x{image_shape[0]}px) - "
                    f"세그멘테이션 실행 버튼을 눌러주세요"
                )
                self.status_bar.showMessage(f"이미지 로드 완료: {filename}")
                
                # Hide detailed info
                self.detail_info.setVisible(False)
                
            except Exception as e:
                self.show_error(f"이미지 로드 실패: {str(e)}")
                
    def run_segmentation(self):
        """Run segmentation on loaded image"""
        if not self.current_image_path:
            QMessageBox.warning(self, "경고", "먼저 이미지를 로드해주세요.")
            return
            
        if not self.sam_processor:
            QMessageBox.warning(self, "경고", "AI 모델이 아직 로딩 중입니다.")
            return
            
        self.process_image(self.current_image_path)
            
    def process_image(self, image_path):
        """Process image with SAM"""
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.load_btn.setEnabled(False)
        self.segment_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.info_label.setText("세그멘테이션 처리 중... 몇 분 정도 소요됩니다.")
        self.status_bar.showMessage("세그멘테이션 처리 중...")
        
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
        
        # Update detailed information
        self.update_detailed_info(result['masks'])
        
        # Update UI
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.segment_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        masks = result['masks']
        mask_count = len(masks)
        
        # Calculate statistics
        if masks:
            total_area = sum(mask['area'] for mask in masks)
            avg_score = sum(mask.get('stability_score', 0) for mask in masks) / len(masks)
            
            # Quality distribution
            quality_counts = {}
            for mask in masks:
                category = mask.get('quality_category', 'unknown')
                quality_counts[category] = quality_counts.get(category, 0) + 1
                
            # Create detailed status message
            quality_summary = ', '.join([f"{count} {quality}" for quality, count in quality_counts.items()])
            
            self.info_label.setText(
                f"처리 완료 - {mask_count}개 마스크 감지됨 | "
                f"총 면적: {total_area:,}px | "
                f"평균 품질: {avg_score:.3f} | "
                f"품질 분포: {quality_summary}"
            )
            
            self.status_bar.showMessage(f"준비 완료 - {mask_count}개 마스크 (평균 품질: {avg_score:.3f})")
        else:
            self.info_label.setText("처리 완료 - 마스크를 감지하지 못했습니다")
            self.status_bar.showMessage("준비 완료 - 마스크 없음")
        
    def on_processing_error(self, error_msg):
        """Handle SAM processing error"""
        self.show_error(f"세그멘테이션 실패: {error_msg}")
        self.progress_bar.setVisible(False)
        self.load_btn.setEnabled(True)
        self.segment_btn.setEnabled(True)
        
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
        
    def update_detailed_info(self, masks):
        """Update detailed mask information display"""
        if not masks:
            self.detail_info.setText("마스크 정보가 없습니다.")
            return
            
        # Show detailed info panel
        self.detail_info.setVisible(True)
        
        # Generate detailed statistics
        info_lines = []
        info_lines.append(f"=== 마스크 상세 정보 ===")
        info_lines.append(f"총 마스크 수: {len(masks)}")
        info_lines.append("")
        
        # Top 10 masks by area
        info_lines.append("주요 마스크 (Top 10):")
        for i, mask in enumerate(masks[:10]):
            area = mask['area']
            stability = mask.get('stability_score', 0)
            category = mask.get('quality_category', 'unknown')
            info_lines.append(
                f"{i+1:2d}. 면적: {area:6,}px | 품질: {stability:.3f} | 등급: {category}"
            )
            
        # Quality distribution
        quality_dist = {}
        for mask in masks:
            category = mask.get('quality_category', 'unknown')
            quality_dist[category] = quality_dist.get(category, 0) + 1
            
        info_lines.append("")
        info_lines.append("품질 분포:")
        for quality, count in sorted(quality_dist.items()):
            percentage = (count / len(masks)) * 100
            info_lines.append(f"  {quality}: {count}개 ({percentage:.1f}%)")
            
        self.detail_info.setText("\n".join(info_lines))
        
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