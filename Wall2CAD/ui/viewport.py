"""
Wall2CAD - CAD 스타일 뷰포트
PyOpenGL 기반 2D 벡터 렌더링
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QImage
import numpy as np

class Viewport(QWidget):
    """CAD 스타일 2D 뷰포트"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_viewport()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        
        # 임시 플레이스홀더
        self.placeholder = QLabel("뷰포트 영역\n(이미지 및 벡터 표시)")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                color: #666;
                font-size: 14px;
                background-color: #f5f5f5;
            }
        """)
        
        layout.addWidget(self.placeholder)
        
        # 뷰포트 설정
        self.setMinimumSize(400, 300)
        
    def init_viewport(self):
        """뷰포트 초기화"""
        # 뷰포트 상태 변수
        self.zoom_factor = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        
        # 이미지 및 벡터 데이터
        self.image = None
        self.image_pixmap = None
        self.image_rect = None
        self.vectors = []
        self.masks = []
        
        # 그리드 표시 여부
        self.show_grid = True
        
    def paintEvent(self, event):
        """페인트 이벤트 - 향후 OpenGL로 교체 예정"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 배경 그리기
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # 그리드 그리기 (선택적)
        if self.show_grid:
            self.draw_grid(painter)
            
        # 이미지 그리기
        if self.image_pixmap and self.image_rect:
            self.draw_image(painter)
            
    def draw_grid(self, painter):
        """그리드 그리기"""
        pen = QPen(QColor(200, 200, 200), 1)
        painter.setPen(pen)
        
        # 간격 설정
        grid_size = 50
        
        # 수직선
        for x in range(0, self.width(), grid_size):
            painter.drawLine(x, 0, x, self.height())
            
        # 수평선
        for y in range(0, self.height(), grid_size):
            painter.drawLine(0, y, self.width(), y)
            
    def wheelEvent(self, event):
        """마우스 휠 이벤트 - 확대/축소"""
        if not self.image_pixmap:
            return
            
        delta = event.angleDelta().y()
        zoom_in = delta > 0
        
        if zoom_in:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
            
        # 최소/최대 줌 제한
        self.zoom_factor = max(0.1, min(10.0, self.zoom_factor))
        
        self.update()
        
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.MouseButton.MiddleButton:
            self.last_pan_point = event.position()
            
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 - 패닝"""
        if hasattr(self, 'last_pan_point'):
            delta = event.position() - self.last_pan_point
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.last_pan_point = event.position()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """마우스 릴리스 이벤트"""
        if hasattr(self, 'last_pan_point'):
            delattr(self, 'last_pan_point')
            
    def load_image(self, image_array):
        """이미지 로드 및 표시"""
        try:
            self.image = image_array
            
            # NumPy 배열을 QPixmap으로 변환
            height, width, channel = image_array.shape
            bytes_per_line = 3 * width
            
            # RGB 데이터를 QImage로 변환
            q_image = QImage(image_array.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            self.image_pixmap = QPixmap.fromImage(q_image)
            
            # 이미지를 뷰포트 크기에 맞게 조정
            self.fit_image_to_viewport()
            
            # 플레이스홀더 숨기기
            self.placeholder.hide()
            
            # 화면 업데이트
            self.update()
            
        except Exception as e:
            print(f"이미지 로드 오류: {e}")
            
    def fit_image_to_viewport(self):
        """이미지를 뷰포트에 맞게 조정"""
        if not self.image_pixmap:
            return
            
        viewport_size = self.size()
        image_size = self.image_pixmap.size()
        
        # 비율 유지하며 크기 조정
        scale_x = viewport_size.width() / image_size.width()
        scale_y = viewport_size.height() / image_size.height()
        scale = min(scale_x, scale_y) * 0.9  # 여백 추가
        
        new_width = int(image_size.width() * scale)
        new_height = int(image_size.height() * scale)
        
        # 중앙 배치
        x = (viewport_size.width() - new_width) // 2
        y = (viewport_size.height() - new_height) // 2
        
        self.image_rect = (x, y, new_width, new_height)
        
    def draw_image(self, painter):
        """이미지 그리기"""
        if self.image_pixmap and self.image_rect:
            x, y, width, height = self.image_rect
            
            # 줌 및 패닝 적용
            scaled_width = int(width * self.zoom_factor)
            scaled_height = int(height * self.zoom_factor)
            
            scaled_x = int(x * self.zoom_factor + self.pan_x)
            scaled_y = int(y * self.zoom_factor + self.pan_y)
            
            # 스케일된 이미지 그리기
            scaled_pixmap = self.image_pixmap.scaled(
                scaled_width, scaled_height, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            painter.drawPixmap(scaled_x, scaled_y, scaled_pixmap)
        
    def display_masks(self, masks):
        """마스크 표시"""
        # 향후 구현
        pass
        
    def display_vectors(self, vectors):
        """벡터 표시"""
        # 향후 구현
        pass
        
    def resizeEvent(self, event):
        """리사이즈 이벤트"""
        super().resizeEvent(event)
        if self.image_pixmap:
            self.fit_image_to_viewport()
            self.update()