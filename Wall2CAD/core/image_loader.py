"""
Wall2CAD - 이미지 로더
이미지 파일 로딩 및 전처리
"""

import os
import cv2
import numpy as np
from typing import Optional, Tuple, List
from PyQt6.QtCore import QObject, pyqtSignal

class ImageLoader(QObject):
    """이미지 로더 클래스"""
    
    # 시그널 정의
    image_loaded = pyqtSignal(np.ndarray, str)  # 이미지, 파일명
    load_error = pyqtSignal(str)  # 오류 메시지
    
    # 지원하는 이미지 포맷
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    
    def __init__(self):
        super().__init__()
        self.current_image = None
        self.current_path = None
        self.original_image = None
        
    def load_image(self, file_path: str) -> bool:
        """
        이미지 파일 로드
        
        Args:
            file_path: 이미지 파일 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        try:
            # 파일 존재 확인
            if not os.path.exists(file_path):
                self.load_error.emit(f"파일을 찾을 수 없습니다: {file_path}")
                return False
                
            # 파일 확장자 확인
            ext = os.path.splitext(file_path.lower())[1]
            if ext not in self.SUPPORTED_FORMATS:
                self.load_error.emit(f"지원하지 않는 파일 형식입니다: {ext}")
                return False
                
            # 이미지 로드
            image = cv2.imread(file_path)
            if image is None:
                self.load_error.emit(f"이미지를 로드할 수 없습니다: {file_path}")
                return False
                
            # BGR -> RGB 변환
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 이미지 정보 저장
            self.current_image = image
            self.original_image = image.copy()
            self.current_path = file_path
            
            # 시그널 발신
            filename = os.path.basename(file_path)
            self.image_loaded.emit(image, filename)
            
            print(f"Image loaded: {filename} ({image.shape[1]}x{image.shape[0]})")
            return True
            
        except Exception as e:
            error_msg = f"이미지 로드 중 오류 발생: {str(e)}"
            self.load_error.emit(error_msg)
            print(error_msg)
            return False
            
    def preprocess_image(self, brightness: float = 0, contrast: float = 1.0, 
                        rotation: float = 0, target_size: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        이미지 전처리
        
        Args:
            brightness: 밝기 조정 (-100 ~ 100)
            contrast: 대비 조정 (0.5 ~ 3.0)
            rotation: 회전 각도 (도)
            target_size: 목표 크기 (width, height)
            
        Returns:
            np.ndarray: 전처리된 이미지
        """
        if self.original_image is None:
            return None
            
        image = self.original_image.copy()
        
        # 밝기/대비 조정
        if brightness != 0 or contrast != 1.0:
            image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
            
        # 회전
        if rotation != 0:
            height, width = image.shape[:2]
            center = (width // 2, height // 2)
            matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
            image = cv2.warpAffine(image, matrix, (width, height))
            
        # 크기 조정
        if target_size is not None:
            image = cv2.resize(image, target_size)
            
        self.current_image = image
        return image
        
    def get_image_info(self) -> dict:
        """현재 이미지 정보 반환"""
        if self.current_image is None:
            return {}
            
        height, width = self.current_image.shape[:2]
        channels = self.current_image.shape[2] if len(self.current_image.shape) > 2 else 1
        
        return {
            'path': self.current_path,
            'filename': os.path.basename(self.current_path) if self.current_path else '',
            'width': width,
            'height': height,
            'channels': channels,
            'size_mb': self.current_image.nbytes / (1024 * 1024),
            'dtype': str(self.current_image.dtype)
        }
        
    def resize_for_display(self, max_size: int = 1024) -> np.ndarray:
        """
        디스플레이용 이미지 크기 조정
        
        Args:
            max_size: 최대 크기 (긴 변 기준)
            
        Returns:
            np.ndarray: 크기 조정된 이미지
        """
        if self.current_image is None:
            return None
            
        height, width = self.current_image.shape[:2]
        
        # 크기 조정이 필요한지 확인
        if max(height, width) <= max_size:
            return self.current_image
            
        # 비율 계산
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
            
        return cv2.resize(self.current_image, (new_width, new_height))
        
    def get_pixel_value(self, x: int, y: int) -> Optional[Tuple[int, int, int]]:
        """
        특정 위치의 픽셀 값 반환
        
        Args:
            x, y: 픽셀 좌표
            
        Returns:
            Tuple[int, int, int]: RGB 값
        """
        if self.current_image is None:
            return None
            
        height, width = self.current_image.shape[:2]
        if 0 <= x < width and 0 <= y < height:
            return tuple(self.current_image[y, x])
        
        return None
        
    def reset_to_original(self):
        """원본 이미지로 리셋"""
        if self.original_image is not None:
            self.current_image = self.original_image.copy()
            
    def is_loaded(self) -> bool:
        """이미지 로드 상태 확인"""
        return self.current_image is not None
        
    def get_current_image(self) -> Optional[np.ndarray]:
        """현재 이미지 반환"""
        return self.current_image
        
    def get_original_image(self) -> Optional[np.ndarray]:
        """원본 이미지 반환"""
        return self.original_image