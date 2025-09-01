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
from ui.progress_dialog import ModelLoadingDialog
from core.image_loader import ImageLoader
from core.sam_worker import SAMWorkerThread

class MainWindow(QMainWindow):
    """메인 애플리케이션 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 이미지 로더 초기화
        self.image_loader = ImageLoader()
        
        # SAM 워커 스레드 초기화
        self.sam_worker = SAMWorkerThread()
        
        # 진행률 다이얼로그
        self.progress_dialog = None
        
        # 현재 로드된 모델 정보
        self.current_model_info = {"loaded": False, "path": "", "type": ""}
        
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
        
        # 툴바 연결
        self.connect_toolbar()
        
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
        
        # SAM 워커 시그널
        self.sam_worker.model_load_started.connect(self.on_model_load_started)
        self.sam_worker.model_load_progress.connect(self.on_model_load_progress)
        self.sam_worker.model_load_finished.connect(self.on_model_load_finished)
        self.sam_worker.segmentation_started.connect(self.on_segmentation_started)
        self.sam_worker.segmentation_progress.connect(self.on_segmentation_progress)
        self.sam_worker.segmentation_finished.connect(self.on_segmentation_finished)
        self.sam_worker.error_occurred.connect(self.on_sam_error)
        
        # 속성 패널 시그널
        self.property_panel.sam_params_changed.connect(self.on_sam_params_changed)
        
    def connect_toolbar(self):
        """툴바 시그널 연결"""
        self.main_toolbar.open_image.connect(self.open_image)
        self.main_toolbar.run_segmentation.connect(self.run_segmentation)
        self.main_toolbar.save_dxf.connect(self.export_dxf)
        self.main_toolbar.zoom_in.connect(self.zoom_in)
        self.main_toolbar.zoom_out.connect(self.zoom_out)
        self.main_toolbar.zoom_fit.connect(self.zoom_fit)
        self.main_toolbar.toggle_grid.connect(self.toggle_grid)
        self.main_toolbar.toggle_masks.connect(self.toggle_masks)
        
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
        # 뷰포트에 이미지 표시
        self.viewport.load_image(image)
        # 마스크 지우기 (새 이미지 로드 시)
        self.viewport.clear_masks()
        
        # 툴바 상태 업데이트
        self.update_toolbar_state()
        
        print(f"Image loaded: {filename}, Shape: {image.shape}")
        
    def on_load_error(self, error_message):
        """이미지 로드 오류 시 호출"""
        self.statusbar.showMessage("준비됨")
        QMessageBox.warning(self, "오류", f"이미지 로딩 실패:\n{error_message}")
        
    def export_dxf(self):
        """DXF 파일 내보내기"""
        # 향후 구현
        QMessageBox.information(self, "정보", "DXF 내보내기 기능은 아직 구현되지 않았습니다.")
        
    def zoom_in(self):
        """확대"""
        self.viewport.zoom_factor *= 1.2
        self.viewport.update()
        
    def zoom_out(self):
        """축소"""
        self.viewport.zoom_factor /= 1.2
        self.viewport.update()
        
    def zoom_fit(self):
        """전체 보기"""
        self.viewport.zoom_factor = 1.0
        self.viewport.pan_x = 0
        self.viewport.pan_y = 0
        if self.viewport.image_pixmap:
            self.viewport.fit_image_to_viewport()
        self.viewport.update()
        
    def toggle_grid(self, show):
        """그리드 토글"""
        self.viewport.show_grid = show
        self.viewport.update()
        
    def toggle_masks(self, show):
        """마스크 토글"""
        self.viewport.set_mask_visibility(show)
        
    def run_segmentation(self):
        """세그멘테이션 실행"""
        print("Starting segmentation...")
        current_image = self.image_loader.get_current_image()
        if current_image is None:
            QMessageBox.warning(self, "경고", "먼저 이미지를 로드해주세요.")
            return
            
        if not self.sam_worker.is_model_loaded():
            QMessageBox.warning(self, "경고", "SAM 모델이 로드되지 않았습니다.")
            return
            
        # 세그멘테이션 매개변수 가져오기
        sam_params = self.property_panel.get_sam_parameters()
        
        # 세그멘테이션 시작
        self.sam_worker.run_segmentation(
            current_image,
            sam_params
        )
        
    def update_toolbar_state(self):
        """툴바 상태 업데이트"""
        has_image = self.image_loader.is_loaded()
        has_masks = len(self.viewport.masks) > 0
        model_loaded = self.sam_worker.is_model_loaded()
        
        self.main_toolbar.set_enabled_state(
            has_image=has_image,
            has_masks=has_masks, 
            model_loaded=model_loaded
        )
        
    # SAM 관련 이벤트 핸들러
    def on_sam_params_changed(self, params):
        """SAM 매개변수 변경 시 호출"""
        model_path = params.get('model_path', '')
        
        # 새로운 모델이 선택된 경우 자동 로딩
        if model_path and model_path != self.current_model_info.get('path', ''):
            self.load_sam_model(model_path)
            
    def load_sam_model(self, model_path: str):
        """SAM 모델 로딩 시작"""
        if not model_path:
            return
            
        # 모델 타입 추출
        import os
        filename = os.path.basename(model_path).lower()
        if 'vit_b' in filename:
            model_type = 'vit_b'
        elif 'vit_l' in filename:
            model_type = 'vit_l' 
        elif 'vit_h' in filename:
            model_type = 'vit_h'
        else:
            model_type = 'vit_h'  # 기본값
            
        print(f"Loading SAM model: {model_path} (type: {model_type})")
        
        # 워커 스레드에서 모델 로딩 시작
        self.sam_worker.load_sam_model(model_path, model_type)
        
    def on_model_load_started(self):
        """모델 로딩 시작 시 호출"""
        # 실제 로딩 중인 모델 정보 가져오기
        model_path = self.sam_worker.model_path
        model_type = self.sam_worker.model_type
        
        # 파일명으로부터 간단한 모델명 생성
        import os
        filename = os.path.basename(model_path)
        model_name = f"SAM {model_type.upper()} ({filename})"
        
        self.progress_dialog = ModelLoadingDialog(self)
        
        # 취소 버튼 연결 (시그널이 있는 경우)
        if hasattr(self.progress_dialog, 'cancel_requested'):
            self.progress_dialog.cancel_requested.connect(self.sam_worker.stop_processing)
        
        self.progress_dialog.show()
        self.statusbar.showMessage("SAM 모델 로딩 중...")
        
    def on_model_load_progress(self, progress: int, message: str):
        """모델 로딩 진행률 업데이트"""
        if self.progress_dialog:
            self.progress_dialog.update_progress(progress, message)
            
    def on_model_load_finished(self, success: bool, message: str):
        """모델 로딩 완료 시 호출"""
        if self.progress_dialog:
            self.progress_dialog.set_completed(success, message)
            
        if success:
            # 모델 정보 업데이트
            self.current_model_info = self.sam_worker.get_model_info()
            self.statusbar.showMessage(f"모델 로딩 완료: {message}")
            
            # 세그멘테이션 버튼 활성화
            self.property_panel.process_button.setEnabled(True)
            self.property_panel.process_button.setText("세그멘테이션 실행")
            
            print(f"Model loaded successfully: {self.current_model_info}")
        else:
            self.statusbar.showMessage("모델 로딩 실패")
            self.property_panel.process_button.setEnabled(False)
            
            # 오류 메시지 박스 표시
            QMessageBox.warning(self, "모델 로딩 실패", message)
            
    def on_sam_error(self, error_message: str):
        """SAM 오류 처리"""
        if self.progress_dialog:
            self.progress_dialog.set_error(error_message)
            
        self.statusbar.showMessage("오류 발생")
        print(f"SAM Error: {error_message}")
        
    def on_segmentation_started(self):
        """세그멘테이션 시작"""
        self.statusbar.showMessage("세그멘테이션 실행 중...")
        self.main_toolbar.set_segmentation_running(True)
        
    def on_segmentation_progress(self, progress, message):
        """세그멘테이션 진행률"""
        self.statusbar.showMessage(f"{message} ({progress}%)")
        
    def on_segmentation_finished(self, success, masks, message):
        """세그멘테이션 완료"""
        self.main_toolbar.set_segmentation_running(False)
        
        if success and masks:
            # 마스크 표시
            self.viewport.display_masks(masks)
            self.statusbar.showMessage(f"세그멘테이션 완료 - {len(masks)}개 마스크 생성됨")
            QMessageBox.information(self, "성공", f"{len(masks)}개의 마스크가 생성되었습니다.")
        else:
            self.statusbar.showMessage("세그멘테이션 실패")
            QMessageBox.warning(self, "실패", f"세그멘테이션 실패:\n{message}")
            
        # 툴바 상태 업데이트
        self.update_toolbar_state()
    
    def get_model_status(self) -> str:
        """현재 모델 상태 반환"""
        if self.current_model_info.get('loaded', False):
            model_type = self.current_model_info.get('model_type', 'unknown')
            device = self.current_model_info.get('device_info', {}).get('device', 'unknown')
            return f"모델: {model_type.upper()} ({device})"
        else:
            return "모델: 미로드"