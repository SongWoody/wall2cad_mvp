"""
Wall2CAD - 설정 관리
애플리케이션 설정 및 구성 관리
"""

import os
import json
from typing import Dict, Any, Optional
from PyQt6.QtCore import QSettings

class ConfigManager:
    """설정 관리자 클래스"""
    
    def __init__(self, app_name: str = "Wall2CAD", org_name: str = "Wall2CAD Team"):
        self.app_name = app_name
        self.org_name = org_name
        self.settings = QSettings(org_name, app_name)
        
        # 기본 설정값
        self.defaults = {
            # SAM 모델 설정
            'sam_model_type': 'vit_h',
            'sam_points_per_side': 32,
            'sam_pred_iou_thresh': 0.88,
            'sam_stability_score_thresh': 0.95,
            'sam_min_mask_region_area': 100,
            
            # 벡터 후처리 설정
            'vector_smoothing': True,
            'vector_smoothing_strength': 1.0,
            'vector_noise_removal': True,
            'vector_fill_holes': False,
            'vector_epsilon_factor': 0.02,
            
            # DXF 내보내기 설정
            'dxf_version': 'R2018',
            'dxf_units': 'mm',
            'dxf_scale_factor': 1.0,
            'dxf_add_image_reference': False,
            
            # UI 설정
            'window_width': 1200,
            'window_height': 800,
            'window_maximized': False,
            'splitter_sizes': [900, 300],
            'show_grid': True,
            'grid_size': 50,
            
            # 파일 경로
            'last_image_directory': '',
            'last_export_directory': '',
            'model_cache_directory': '',
            
            # 성능 설정
            'use_cuda': True,
            'max_image_size': 1024,
            'enable_multiprocessing': True,
            'worker_thread_count': 4,
            
            # 기타
            'auto_save_settings': True,
            'show_splash_screen': True,
            'enable_debug_logging': False
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값 가져오기
        
        Args:
            key: 설정 키
            default: 기본값 (None인 경우 defaults에서 가져옴)
            
        Returns:
            설정값
        """
        if default is None and key in self.defaults:
            default = self.defaults[key]
            
        return self.settings.value(key, default)
        
    def set(self, key: str, value: Any):
        """
        설정값 저장
        
        Args:
            key: 설정 키
            value: 설정값
        """
        self.settings.setValue(key, value)
        
        # 자동 저장이 활성화된 경우
        if self.get('auto_save_settings', True):
            self.settings.sync()
            
    def get_sam_params(self) -> Dict[str, Any]:
        """SAM 매개변수 반환"""
        return {
            'model_type': self.get('sam_model_type'),
            'points_per_side': int(self.get('sam_points_per_side')),
            'pred_iou_thresh': float(self.get('sam_pred_iou_thresh')),
            'stability_score_thresh': float(self.get('sam_stability_score_thresh')),
            'min_mask_region_area': int(self.get('sam_min_mask_region_area'))
        }
        
    def set_sam_params(self, params: Dict[str, Any]):
        """SAM 매개변수 저장"""
        mapping = {
            'model_type': 'sam_model_type',
            'points_per_side': 'sam_points_per_side',
            'pred_iou_thresh': 'sam_pred_iou_thresh',
            'stability_score_thresh': 'sam_stability_score_thresh',
            'min_mask_region_area': 'sam_min_mask_region_area'
        }
        
        for key, setting_key in mapping.items():
            if key in params:
                self.set(setting_key, params[key])
                
    def get_vector_params(self) -> Dict[str, Any]:
        """벡터 후처리 매개변수 반환"""
        return {
            'smoothing': self.get('vector_smoothing'),
            'smoothing_strength': float(self.get('vector_smoothing_strength')),
            'noise_removal': self.get('vector_noise_removal'),
            'fill_holes': self.get('vector_fill_holes'),
            'epsilon_factor': float(self.get('vector_epsilon_factor'))
        }
        
    def get_dxf_params(self) -> Dict[str, Any]:
        """DXF 내보내기 매개변수 반환"""
        return {
            'version': self.get('dxf_version'),
            'units': self.get('dxf_units'),
            'scale_factor': float(self.get('dxf_scale_factor')),
            'add_image_reference': self.get('dxf_add_image_reference')
        }
        
    def get_window_geometry(self) -> Dict[str, Any]:
        """윈도우 지오메트리 반환"""
        return {
            'width': int(self.get('window_width')),
            'height': int(self.get('window_height')),
            'maximized': self.get('window_maximized'),
            'splitter_sizes': self.get('splitter_sizes')
        }
        
    def set_window_geometry(self, width: int, height: int, 
                           maximized: bool = False, 
                           splitter_sizes: Optional[list] = None):
        """윈도우 지오메트리 저장"""
        self.set('window_width', width)
        self.set('window_height', height)
        self.set('window_maximized', maximized)
        
        if splitter_sizes:
            self.set('splitter_sizes', splitter_sizes)
            
    def restore_defaults(self):
        """기본값으로 복원"""
        self.settings.clear()
        
        # 기본값 설정
        for key, value in self.defaults.items():
            self.set(key, value)
            
    def export_settings(self, file_path: str) -> bool:
        """
        설정을 파일로 내보내기
        
        Args:
            file_path: 내보낼 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            settings_dict = {}
            
            # 모든 설정값 수집
            for key in self.defaults.keys():
                settings_dict[key] = self.get(key)
                
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
            
    def import_settings(self, file_path: str) -> bool:
        """
        파일에서 설정 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            
        Returns:
            bool: 성공 여부
        """
        try:
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                settings_dict = json.load(f)
                
            # 설정값 적용
            for key, value in settings_dict.items():
                if key in self.defaults:  # 유효한 키만 적용
                    self.set(key, value)
                    
            return True
            
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
            
    def get_model_cache_path(self) -> str:
        """모델 캐시 디렉토리 경로 반환"""
        cache_dir = self.get('model_cache_directory')
        
        if not cache_dir:
            # 기본 캐시 디렉토리 설정
            cache_dir = os.path.expanduser('~/.wall2cad/models')
            self.set('model_cache_directory', cache_dir)
            
        # 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        return cache_dir
        
    def get_temp_directory(self) -> str:
        """임시 디렉토리 경로 반환"""
        temp_dir = os.path.expanduser('~/.wall2cad/temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
        
    def cleanup_temp_files(self):
        """임시 파일 정리"""
        try:
            temp_dir = self.get_temp_directory()
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
            
    def sync(self):
        """설정 동기화 (디스크에 저장)"""
        self.settings.sync()


# 전역 설정 인스턴스
config = ConfigManager()