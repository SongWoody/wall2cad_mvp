"""
Wall2CAD - 진행률 표시 다이얼로그
모델 로딩 및 세그멘테이션 진행 상황 표시
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QProgressBar, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ProgressDialog(QDialog):
    """진행률 표시 다이얼로그"""
    
    # 시그널 정의
    cancel_requested = pyqtSignal()
    
    def __init__(self, title: str = "작업 진행중", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.cancelled = False
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 제목 라벨
        self.title_label = QLabel("작업을 준비하는 중...")
        title_font = QFont()
        title_font.setPointSize(10)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 상태 메시지
        self.status_label = QLabel("대기 중...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; padding: 8px;")
        layout.addWidget(self.status_label)
        
        # 세부 로그 (접을 수 있음)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setVisible(False)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        
        # 로그 토글 버튼
        self.log_toggle_btn = QPushButton("로그 표시")
        self.log_toggle_btn.setCheckable(True)
        self.log_toggle_btn.clicked.connect(self.toggle_log_visibility)
        button_layout.addWidget(self.log_toggle_btn)
        
        button_layout.addStretch()
        
        # 취소 버튼
        self.cancel_btn = QPushButton("취소")
        self.cancel_btn.clicked.connect(self.request_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def set_title(self, title: str):
        """제목 설정"""
        self.title_label.setText(title)
        
    def update_progress(self, value: int, message: str = ""):
        """진행률 업데이트"""
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
            self.add_log_message(f"[{value}%] {message}")
            
    def add_log_message(self, message: str):
        """로그 메시지 추가"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"{timestamp} - {message}"
        self.log_text.append(log_entry)
        
        # 자동 스크롤
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def toggle_log_visibility(self):
        """로그 표시/숨김 토글"""
        if self.log_text.isVisible():
            self.log_text.setVisible(False)
            self.log_toggle_btn.setText("로그 표시")
            self.resize(self.width(), self.minimumHeight())
        else:
            self.log_text.setVisible(True)
            self.log_toggle_btn.setText("로그 숨김")
            
    def request_cancel(self):
        """취소 요청"""
        if not self.cancelled:
            self.cancelled = True
            self.cancel_btn.setText("취소 중...")
            self.cancel_btn.setEnabled(False)
            self.add_log_message("사용자가 작업 취소를 요청했습니다.")
            self.cancel_requested.emit()
            
    def set_completed(self, success: bool, message: str):
        """작업 완료 처리"""
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("✅ " + message)
            self.status_label.setStyleSheet("color: green; padding: 8px;")
            self.cancel_btn.setText("확인")
        else:
            self.status_label.setText("❌ " + message)
            self.status_label.setStyleSheet("color: red; padding: 8px;")
            self.cancel_btn.setText("닫기")
            
        self.add_log_message(f"작업 완료: {message}")
        self.cancel_btn.setEnabled(True)
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.accept)
        
    def set_error(self, error_message: str):
        """오류 상태 설정"""
        self.set_completed(False, f"오류: {error_message}")
        
    def closeEvent(self, event):
        """다이얼로그 닫기 이벤트"""
        if not self.cancelled and self.progress_bar.value() < 100:
            # 작업 진행 중일 때는 취소 확인
            self.request_cancel()
            event.ignore()
        else:
            super().closeEvent(event)


class ModelLoadingDialog(ProgressDialog):
    """SAM 모델 로딩 전용 다이얼로그"""
    
    def __init__(self, model_name: str, parent=None):
        super().__init__("SAM 모델 로딩", parent)
        self.model_name = model_name
        self.set_title(f"SAM 모델 로딩 중: {model_name}")
        self.add_log_message(f"모델 로딩 시작: {model_name}")
        
        # 모델 로딩 관련 스타일 적용
        self.setStyleSheet("""
            QLabel {
                font-size: 10pt;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 3px;
            }
        """)


class SegmentationDialog(ProgressDialog):
    """세그멘테이션 전용 다이얼로그"""
    
    def __init__(self, image_name: str, parent=None):
        super().__init__("이미지 세그멘테이션", parent)
        self.image_name = image_name
        self.set_title(f"이미지 세그멘테이션: {image_name}")
        self.add_log_message(f"세그멘테이션 시작: {image_name}")
        
        # 세그멘테이션 관련 스타일 적용
        self.setStyleSheet("""
            QLabel {
                font-size: 10pt;
            }
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #28a745;
                border-radius: 3px;
            }
        """)