"""
Wall2CAD - 메인 툴바
CAD 스타일 도구모음
"""

from PyQt6.QtWidgets import QToolBar, QToolButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

class MainToolBar(QToolBar):
    """메인 툴바"""
    
    # 시그널 정의
    open_image = pyqtSignal()
    run_segmentation = pyqtSignal()
    save_dxf = pyqtSignal()
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()
    zoom_fit = pyqtSignal()
    toggle_grid = pyqtSignal(bool)
    toggle_masks = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.init_toolbar()
        
    def init_toolbar(self):
        """툴바 초기화"""
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setMovable(False)
        
        # 파일 작업
        self.add_separator_with_label("파일")
        
        # 이미지 열기
        open_action = QAction("열기", self)
        open_action.setStatusTip("이미지 파일을 엽니다")
        open_action.triggered.connect(self.open_image.emit)
        self.addAction(open_action)
        
        # 세그멘테이션 실행
        self.segment_action = QAction("세그멘테이션 실행", self)
        self.segment_action.setStatusTip("SAM 모델로 이미지 세그멘테이션을 수행합니다")
        self.segment_action.setEnabled(False)  # 기본적으로 비활성화
        self.segment_action.triggered.connect(self.run_segmentation.emit)
        self.addAction(self.segment_action)
        
        # DXF 저장
        self.save_action = QAction("DXF 저장", self)
        self.save_action.setStatusTip("DXF 파일로 저장합니다")
        self.save_action.setEnabled(False)  # 기본적으로 비활성화
        self.save_action.triggered.connect(self.save_dxf.emit)
        self.addAction(self.save_action)
        
        self.addSeparator()
        
        # 보기 작업
        self.add_separator_with_label("보기")
        
        # 확대
        zoom_in_action = QAction("확대", self)
        zoom_in_action.setStatusTip("확대합니다")
        zoom_in_action.triggered.connect(self.zoom_in.emit)
        self.addAction(zoom_in_action)
        
        # 축소
        zoom_out_action = QAction("축소", self)
        zoom_out_action.setStatusTip("축소합니다")
        zoom_out_action.triggered.connect(self.zoom_out.emit)
        self.addAction(zoom_out_action)
        
        # 전체 보기
        zoom_fit_action = QAction("전체보기", self)
        zoom_fit_action.setStatusTip("전체 이미지를 화면에 맞춥니다")
        zoom_fit_action.triggered.connect(self.zoom_fit.emit)
        self.addAction(zoom_fit_action)
        
        self.addSeparator()
        
        # 표시 옵션
        self.add_separator_with_label("표시")
        
        # 그리드 토글
        self.grid_action = QAction("그리드", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.setStatusTip("그리드 표시를 토글합니다")
        self.grid_action.toggled.connect(self.toggle_grid.emit)
        self.addAction(self.grid_action)
        
        # 마스크 토글
        self.mask_action = QAction("마스크", self)
        self.mask_action.setCheckable(True)
        self.mask_action.setChecked(True)
        self.mask_action.setStatusTip("마스크 표시를 토글합니다")
        self.mask_action.setEnabled(False)  # 마스크가 없을 때는 비활성화
        self.mask_action.toggled.connect(self.toggle_masks.emit)
        self.addAction(self.mask_action)
        
    def add_separator_with_label(self, label):
        """라벨이 있는 구분선 추가"""
        # 향후 구현 - 현재는 일반 구분선만 추가
        if self.actions():  # 첫 번째가 아닐 때만
            self.addSeparator()
            
    def set_enabled_state(self, has_image=False, has_masks=False, model_loaded=False):
        """툴바 버튼 활성화 상태 설정"""
        # 세그멘테이션 버튼: 이미지가 있고 모델이 로드된 경우에만 활성화
        self.segment_action.setEnabled(has_image and model_loaded)
        
        # DXF 저장 버튼: 마스크가 있을 때만 활성화
        self.save_action.setEnabled(has_masks)
        
        # 마스크 토글: 마스크가 있을 때만 활성화
        self.mask_action.setEnabled(has_masks)
        
    def set_segmentation_running(self, running: bool):
        """세그멘테이션 실행 상태 설정"""
        if running:
            self.segment_action.setText("처리 중...")
            self.segment_action.setEnabled(False)
        else:
            self.segment_action.setText("세그멘테이션 실행")
            # 이미지와 모델 상태에 따라 활성화 여부 결정 (메인에서 호출)