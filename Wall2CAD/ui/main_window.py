"""
Wall2CAD - 메인 윈도우 UI
PyQt6 기반 메인 애플리케이션 윈도우
"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QMenuBar, QStatusBar, QToolBar, QSplitter, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon

from ui.viewport import Viewport
from ui.property_panel import PropertyPanel
from ui.toolbar import MainToolBar
from core.image_loader import ImageLoader

class MainWindow(QMainWindow):
    """메인 애플리케이션 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 이미지 로더 초기화
        self.image_loader = ImageLoader()
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("Wall2CAD - 이미지 세그멘테이션 벡터 변환 도구")
        self.setMinimumSize(QSize(1200, 800))
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QHBoxLayout(central_widget)
        
        # 스플리터로 영역 나누기
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 왼쪽: 뷰포트 (이미지/벡터 표시)
        self.viewport = Viewport()
        splitter.addWidget(self.viewport)
        
        # 오른쪽: 속성 패널
        self.property_panel = PropertyPanel()
        splitter.addWidget(self.property_panel)
        
        # 스플리터 비율 설정 (3:1)
        splitter.setSizes([900, 300])
        
        # 메뉴바, 툴바, 상태바 설정
        self.setup_menubar()
        self.setup_toolbar()
        self.setup_statusbar()
        
    def setup_menubar(self):
        """메뉴바 설정"""
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu('파일(&F)')
        
        # 이미지 열기
        self.open_action = QAction('이미지 열기(&O)', self)
        self.open_action.setShortcut('Ctrl+O')
        self.open_action.setStatusTip('이미지 파일을 열습니다')
        file_menu.addAction(self.open_action)
        
        file_menu.addSeparator()
        
        # DXF 내보내기
        self.export_action = QAction('DXF 내보내기(&E)', self)
        self.export_action.setShortcut('Ctrl+E')
        self.export_action.setStatusTip('DXF 파일로 내보냅니다')
        file_menu.addAction(self.export_action)
        
        file_menu.addSeparator()
        
        # 종료
        exit_action = QAction('종료(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('애플리케이션을 종료합니다')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 편집 메뉴
        edit_menu = menubar.addMenu('편집(&E)')
        
        # 실행 취소/복원
        undo_action = QAction('실행 취소(&U)', self)
        undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('복원(&R)', self)
        redo_action.setShortcut('Ctrl+Y')
        edit_menu.addAction(redo_action)
        
        # 보기 메뉴
        view_menu = menubar.addMenu('보기(&V)')
        
        # 확대/축소
        zoom_in_action = QAction('확대(&I)', self)
        zoom_in_action.setShortcut('Ctrl++')
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('축소(&O)', self)
        zoom_out_action.setShortcut('Ctrl+-')
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction('전체 보기(&F)', self)
        zoom_fit_action.setShortcut('Ctrl+0')
        view_menu.addAction(zoom_fit_action)
        
        # 도구 메뉴
        tools_menu = menubar.addMenu('도구(&T)')
        
        # SAM 처리
        sam_action = QAction('SAM 세그멘테이션(&S)', self)
        sam_action.setShortcut('Ctrl+S')
        sam_action.setStatusTip('SAM 모델로 세그멘테이션을 수행합니다')
        tools_menu.addAction(sam_action)
        
        # 도움말 메뉴
        help_menu = menubar.addMenu('도움말(&H)')
        
        about_action = QAction('정보(&A)', self)
        about_action.setStatusTip('애플리케이션 정보를 표시합니다')
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """툴바 설정"""
        self.main_toolbar = MainToolBar()
        self.addToolBar(self.main_toolbar)
        
    def setup_statusbar(self):
        """상태바 설정"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage('준비됨')
        
    def setup_connections(self):
        """시그널-슬롯 연결"""
        # 파일 메뉴 액션
        self.open_action.triggered.connect(self.open_image)
        self.export_action.triggered.connect(self.export_dxf)
        
        # 이미지 로더 시그널
        self.image_loader.image_loaded.connect(self.on_image_loaded)
        self.image_loader.load_error.connect(self.on_load_error)
        
    def open_image(self):
        """이미지 파일 열기"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "이미지 파일 열기",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.tif);;All Files (*)"
        )
        
        if file_path:
            self.statusbar.showMessage("이미지 로딩 중...")
            success = self.image_loader.load_image(file_path)
            
            if not success:
                self.statusbar.showMessage("이미지 로딩 실패")
                
    def on_image_loaded(self, image, filename):
        """이미지 로드 완료 시 호출"""
        self.statusbar.showMessage(f"이미지 로드 완료: {filename}")
        # 뷰포트에 이미지 표시 (향후 구현)
        print(f"Image loaded: {filename}, Shape: {image.shape}")
        
    def on_load_error(self, error_message):
        """이미지 로드 오류 시 호출"""
        self.statusbar.showMessage("준비됨")
        QMessageBox.warning(self, "오류", f"이미지 로딩 실패:\n{error_message}")
        
    def export_dxf(self):
        """DXF 파일 내보내기"""
        # 향후 구현
        QMessageBox.information(self, "정보", "DXF 내보내기 기능은 아직 구현되지 않았습니다.")