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
    save_dxf = pyqtSignal()
    zoom_in = pyqtSignal()
    zoom_out = pyqtSignal()
    zoom_fit = pyqtSignal()
    toggle_grid = pyqtSignal(bool)
    
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
        
        # DXF 저장
        save_action = QAction("저장", self)
        save_action.setStatusTip("DXF 파일로 저장합니다")
        save_action.triggered.connect(self.save_dxf.emit)
        self.addAction(save_action)
        
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
        
    def add_separator_with_label(self, label):
        """라벨이 있는 구분선 추가"""
        # 향후 구현 - 현재는 일반 구분선만 추가
        if self.actions():  # 첫 번째가 아닐 때만
            self.addSeparator()
            
    def set_enabled_state(self, has_image=False, has_vectors=False):
        """툴바 버튼 활성화 상태 설정"""
        # 향후 구현
        pass