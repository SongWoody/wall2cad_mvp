"""
Wall2CAD - 마스크 후처리기
SAM 마스크의 후처리 및 벡터 변환 준비
"""

import cv2
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy import ndimage
from skimage import measure, morphology
from skimage.segmentation import clear_border

class MaskProcessor:
    """마스크 후처리 클래스"""
    
    def __init__(self):
        self.processed_masks = []
        self.original_masks = []
        
    def process_masks(self, masks: List[Dict[str, Any]], 
                     smoothing: bool = True,
                     noise_removal: bool = True,
                     fill_holes: bool = False,
                     min_area: int = 100,
                     smoothing_strength: float = 1.0) -> List[Dict[str, Any]]:
        """
        마스크 후처리 수행
        
        Args:
            masks: SAM에서 생성된 마스크 리스트
            smoothing: 스무딩 적용 여부
            noise_removal: 노이즈 제거 여부
            fill_holes: 구멍 채우기 여부
            min_area: 최소 영역 크기
            smoothing_strength: 스무딩 강도
            
        Returns:
            List[Dict]: 후처리된 마스크 리스트
        """
        self.original_masks = masks
        self.processed_masks = []
        
        for mask_data in masks:
            try:
                mask = mask_data['segmentation']
                
                # 후처리 적용
                processed_mask = self._process_single_mask(
                    mask, smoothing, noise_removal, fill_holes, 
                    min_area, smoothing_strength
                )
                
                if processed_mask is not None:
                    # 원본 데이터 복사하고 마스크 업데이트
                    processed_data = mask_data.copy()
                    processed_data['segmentation'] = processed_mask
                    
                    # 새로운 통계 계산
                    processed_data['area'] = np.sum(processed_mask)
                    processed_data['bbox'] = self._get_bbox(processed_mask)
                    
                    self.processed_masks.append(processed_data)
                    
            except Exception as e:
                print(f"Error processing mask: {e}")
                continue
                
        print(f"Processed {len(self.processed_masks)} masks from {len(masks)} originals")
        return self.processed_masks
        
    def _process_single_mask(self, mask: np.ndarray,
                           smoothing: bool,
                           noise_removal: bool,
                           fill_holes: bool,
                           min_area: int,
                           smoothing_strength: float) -> Optional[np.ndarray]:
        """단일 마스크 후처리"""
        
        # 타입 변환 (bool -> uint8)
        if mask.dtype == bool:
            mask = mask.astype(np.uint8) * 255
        elif mask.dtype != np.uint8:
            mask = (mask * 255).astype(np.uint8)
            
        # 최소 영역 크기 체크
        if np.sum(mask > 0) < min_area:
            return None
            
        processed = mask.copy()
        
        # 노이즈 제거 (작은 연결 영역 제거)
        if noise_removal:
            processed = self._remove_noise(processed, min_area)
            
        # 구멍 채우기
        if fill_holes:
            processed = self._fill_holes(processed)
            
        # 스무딩
        if smoothing:
            processed = self._smooth_mask(processed, smoothing_strength)
            
        return processed > 0  # bool 타입으로 반환
        
    def _remove_noise(self, mask: np.ndarray, min_area: int) -> np.ndarray:
        """노이즈 제거 (작은 연결 영역 제거)"""
        # 연결 영역 라벨링
        num_labels, labels = cv2.connectedComponents(mask)
        
        # 각 영역의 크기 계산
        clean_mask = np.zeros_like(mask)
        
        for label in range(1, num_labels):
            component = (labels == label)
            if np.sum(component) >= min_area:
                clean_mask[component] = 255
                
        return clean_mask
        
    def _fill_holes(self, mask: np.ndarray) -> np.ndarray:
        """구멍 채우기"""
        # 구멍 채우기 (형태학적 닫힘 연산)
        kernel = np.ones((5, 5), np.uint8)
        filled = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # 또는 ndimage를 사용한 구멍 채우기
        # filled = ndimage.binary_fill_holes(mask > 0).astype(np.uint8) * 255
        
        return filled
        
    def _smooth_mask(self, mask: np.ndarray, strength: float) -> np.ndarray:
        """마스크 스무딩"""
        # 가우시안 블러 적용
        kernel_size = max(3, int(strength * 5))
        if kernel_size % 2 == 0:
            kernel_size += 1
            
        smoothed = cv2.GaussianBlur(mask.astype(np.float32), 
                                  (kernel_size, kernel_size), 
                                  strength)
        
        # 임계값 적용으로 이진화
        _, smoothed = cv2.threshold(smoothed.astype(np.uint8), 
                                  127, 255, cv2.THRESH_BINARY)
        
        return smoothed
        
    def _get_bbox(self, mask: np.ndarray) -> List[int]:
        """마스크의 바운딩 박스 계산"""
        coords = np.argwhere(mask)
        if len(coords) == 0:
            return [0, 0, 0, 0]
            
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        return [int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)]
        
    def extract_contours(self, masks: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        마스크에서 윤곽선 추출
        
        Args:
            masks: 처리할 마스크 리스트 (None인 경우 처리된 마스크 사용)
            
        Returns:
            List[Dict]: 윤곽선 정보가 포함된 딕셔너리 리스트
        """
        if masks is None:
            masks = self.processed_masks
            
        contour_data = []
        
        for i, mask_data in enumerate(masks):
            try:
                mask = mask_data['segmentation']
                
                # uint8로 변환
                if mask.dtype == bool:
                    mask_uint8 = mask.astype(np.uint8) * 255
                else:
                    mask_uint8 = mask.astype(np.uint8)
                    
                # 윤곽선 찾기
                contours, hierarchy = cv2.findContours(
                    mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                
                if contours:
                    # 가장 큰 윤곽선 선택
                    main_contour = max(contours, key=cv2.contourArea)
                    
                    contour_info = {
                        'mask_id': i,
                        'contour': main_contour,
                        'area': cv2.contourArea(main_contour),
                        'perimeter': cv2.arcLength(main_contour, True),
                        'bbox': cv2.boundingRect(main_contour),
                        'original_data': mask_data
                    }
                    
                    contour_data.append(contour_info)
                    
            except Exception as e:
                print(f"Error extracting contour for mask {i}: {e}")
                continue
                
        print(f"Extracted {len(contour_data)} contours")
        return contour_data
        
    def simplify_contours(self, contour_data: List[Dict[str, Any]], 
                         epsilon_factor: float = 0.02) -> List[Dict[str, Any]]:
        """
        윤곽선 단순화 (Douglas-Peucker 알고리즘)
        
        Args:
            contour_data: 윤곽선 데이터 리스트
            epsilon_factor: 단순화 강도 (0.01-0.05)
            
        Returns:
            List[Dict]: 단순화된 윤곽선 데이터
        """
        simplified_data = []
        
        for data in contour_data:
            try:
                contour = data['contour']
                
                # epsilon 계산 (둘레의 일정 비율)
                epsilon = epsilon_factor * cv2.arcLength(contour, True)
                
                # 윤곽선 단순화
                simplified_contour = cv2.approxPolyDP(contour, epsilon, True)
                
                # 데이터 업데이트
                simplified_info = data.copy()
                simplified_info['contour'] = simplified_contour
                simplified_info['simplified'] = True
                simplified_info['epsilon'] = epsilon
                simplified_info['points_original'] = len(contour)
                simplified_info['points_simplified'] = len(simplified_contour)
                
                simplified_data.append(simplified_info)
                
            except Exception as e:
                print(f"Error simplifying contour: {e}")
                # 원본 데이터 유지
                simplified_data.append(data)
                
        return simplified_data
        
    def filter_masks_by_size(self, masks: List[Dict[str, Any]], 
                           min_area: int = 100, 
                           max_area: Optional[int] = None) -> List[Dict[str, Any]]:
        """크기 기준으로 마스크 필터링"""
        filtered = []
        
        for mask_data in masks:
            area = mask_data.get('area', 0)
            
            if area < min_area:
                continue
                
            if max_area is not None and area > max_area:
                continue
                
            filtered.append(mask_data)
            
        return filtered
        
    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계 반환"""
        if not self.processed_masks:
            return {}
            
        areas = [mask['area'] for mask in self.processed_masks]
        
        return {
            'total_masks': len(self.processed_masks),
            'original_count': len(self.original_masks),
            'min_area': min(areas) if areas else 0,
            'max_area': max(areas) if areas else 0,
            'mean_area': np.mean(areas) if areas else 0,
            'total_area': sum(areas) if areas else 0
        }