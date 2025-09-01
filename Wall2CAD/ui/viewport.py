"""
Wall2CAD - CAD 스타일 뷰포트
PyOpenGL 기반 2D 벡터 렌더링
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QImage, QPainterPath, QPolygonF
import numpy as np
import cv2
from typing import List, Dict, Any

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
        
        # 마스크 시각화 옵션
        self.show_masks = True
        self.show_mask_outlines = True
        self.show_mask_fills = True
        self.mask_colors = self._generate_mask_colors(50)  # 50개 색상 미리 생성
        
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
            
        # 마스크 그리기
        if self.show_masks and self.masks:
            self.draw_masks(painter)
            
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
        
    def display_masks(self, masks: List[Dict[str, Any]]):
        """마스크 표시"""
        self.masks = masks
        print(f"마스크 {len(masks)}개 로드됨")
        self.update()  # 화면 업데이트
        
    def draw_masks(self, painter: QPainter):
        """마스크 그리기"""
        if not self.masks or not self.image_rect:
            return
            
        x, y, width, height = self.image_rect
        
        # 줄 및 패닝 적용
        scaled_width = int(width * self.zoom_factor)
        scaled_height = int(height * self.zoom_factor)
        scaled_x = int(x * self.zoom_factor + self.pan_x)
        scaled_y = int(y * self.zoom_factor + self.pan_y)
        
        # 이미지 크기 비율 계산
        if self.image is not None:
            img_h, img_w = self.image.shape[:2]
            scale_x = scaled_width / img_w
            scale_y = scaled_height / img_h
            
            # 각 마스크 그리기
            for i, mask_data in enumerate(self.masks):
                if i >= len(self.mask_colors):
                    break
                    
                mask = mask_data['segmentation']
                color = self.mask_colors[i]
                
                # 마스크 윤곽선 추출
                contours = self._extract_contours(mask)
                
                for contour in contours:
                    if len(contour) < 3:
                        continue
                        
                    # 좌표 변환 및 스케일링
                    scaled_contour = []
                    for point in contour:
                        px = scaled_x + point[0] * scale_x
                        py = scaled_y + point[1] * scale_y
                        scaled_contour.append((px, py))
                    
                    # QPolygonF 생성
                    polygon = QPolygonF()
                    for px, py in scaled_contour:
                        polygon.append(QPointF(px, py))
                    
                    # 마스크 채우기
                    if self.show_mask_fills:
                        fill_color = QColor(color[0], color[1], color[2], 60)  # 투명도 60
                        brush = QBrush(fill_color)
                        painter.setBrush(brush)
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.drawPolygon(polygon)
                    
                    # 마스크 윤곽선
                    if self.show_mask_outlines:
                        outline_color = QColor(color[0], color[1], color[2], 180)
                        pen = QPen(outline_color, 2)
                        painter.setPen(pen)
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        painter.drawPolygon(polygon)
                        
    def _extract_contours(self, mask: np.ndarray):
        """마스크에서 윤곽선 추출"""
        try:
            # 마스크를 uint8로 변환
            mask_uint8 = (mask.astype(np.uint8)) * 255
            
            # OpenCV로 윤곽선 추출
            contours, _ = cv2.findContours(
                mask_uint8, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 결과 변환
            result_contours = []
            for contour in contours:
                if len(contour) >= 3:
                    # 커브 단순화
                    epsilon = 0.005 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    
                    # 좌표 변환 (n, 1, 2) -> (n, 2)
                    simplified = approx.reshape(-1, 2)
                    result_contours.append(simplified)
                    
            return result_contours
            
        except Exception as e:
            print(f"윤곽선 추출 오류: {e}")
            return []
            
    def _generate_mask_colors(self, count: int):
        """마스크용 색상 생성"""
        colors = []
        
        # HSV 색상 환에서 색상 생성
        for i in range(count):
            hue = (i * 360 / count) % 360
            saturation = 0.7 + (i % 3) * 0.1  # 0.7, 0.8, 0.9 순환
            value = 0.8 + (i % 2) * 0.1       # 0.8, 0.9 순환
            
            # HSV를 RGB로 변환
            import colorsys
            r, g, b = colorsys.hsv_to_rgb(hue/360, saturation, value)
            colors.append((int(r*255), int(g*255), int(b*255)))
            
        return colors
        
    def set_mask_visibility(self, show_masks: bool, show_outlines: bool = True, show_fills: bool = True):
        """마스크 표시 옵션 설정"""
        self.show_masks = show_masks
        self.show_mask_outlines = show_outlines
        self.show_mask_fills = show_fills
        self.update()
        
    def clear_masks(self):
        """마스크 지우기"""
        self.masks = []
        self.update()
        
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