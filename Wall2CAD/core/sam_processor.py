"""
Wall2CAD - SAM 모델 프로세서
Segment Anything Model 래퍼 클래스
"""

import os
import sys
import torch
import numpy as np
from typing import List, Dict, Any, Optional

# 모델 스캐너 import
from utils.model_scanner import model_scanner

# segment_anything 모듈 import
try:
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
    print("segment_anything module loaded successfully")
except ImportError:
    try:
        # MVP 방식: 상위 디렉토리에서 찾기
        parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.append(parent_dir)
        from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
        print("segment_anything module loaded from parent directory")
    except ImportError:
        try:
            # wall2cad_mvp 디렉토리에서 찾기
            mvp_path = os.path.join(os.path.dirname(__file__), '..', '..', 'wall2cad_mvp')
            if os.path.exists(mvp_path):
                sys.path.insert(0, mvp_path)
                from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
                print("segment_anything module loaded from wall2cad_mvp")
            else:
                raise ImportError("wall2cad_mvp directory not found")
        except ImportError:
            print("Error: segment_anything module not found. Please check installation.")
            print("Tried locations:")
            print("1. System-wide installation")
            print("2. Parent directory")
            print("3. wall2cad_mvp directory")
            sam_model_registry = None
            SamAutomaticMaskGenerator = None
            SamPredictor = None

class SAMProcessor:
    """SAM 모델 처리 클래스"""
    
    def __init__(self, model_type: str = "vit_h"):
        """
        SAM 프로세서 초기화
        
        Args:
            model_type: SAM 모델 타입 (vit_b, vit_l, vit_h)
        """
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam_model = None
        self.mask_generator = None
        self.predictor = None
        
        print(f"SAM Processor initialized with device: {self.device}")
        
    def load_model(self, checkpoint_path: Optional[str] = None) -> bool:
        """
        SAM 모델 로드 (MVP 방식 참고)
        
        Args:
            checkpoint_path: 모델 체크포인트 경로
            
        Returns:
            bool: 로드 성공 여부
        """
        if sam_model_registry is None:
            print("Error: segment_anything module not available")
            return False
            
        try:
            # 체크포인트 경로 자동 탐지
            if checkpoint_path is None:
                checkpoint_path = self._find_checkpoint()
                
            if not os.path.exists(checkpoint_path):
                print(f"Error: Checkpoint not found at {checkpoint_path}")
                return False
                
            print(f"SAM 모델 로딩 시작 ({self.model_type}) on {self.device}...")
            
            # Load SAM model
            print("모델 체크포인트 로딩 중...")
            self.sam_model = sam_model_registry[self.model_type](checkpoint=checkpoint_path)
            
            print(f"모델을 {self.device} 디바이스로 이동 중...")
            self.sam_model.to(device=self.device)
            
            # Initialize automatic mask generator with optimized parameters (MVP 방식)
            print("자동 마스크 생성기 초기화 중...")
            self.mask_generator = SamAutomaticMaskGenerator(
                model=self.sam_model,
                points_per_side=32,  # Good balance of detail vs speed
                pred_iou_thresh=0.88,
                stability_score_thresh=0.95,
                crop_n_layers=0,  # Disable cropping for speed
                crop_nms_thresh=0.7,
                box_nms_thresh=0.7,
                min_mask_region_area=100,  # Filter out very small masks
                output_mode="binary_mask"
            )
            
            # 프레딕터 초기화
            self.predictor = SamPredictor(self.sam_model)
            
            print("SAM 모델 로딩 완료!")
            return True
            
        except Exception as e:
            print(f"Error loading SAM model: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _find_checkpoint(self) -> str:
        """체크포인트 파일 자동 탐지"""
        # 모델 스캐너를 사용하여 모델 찾기
        model_scanner.scan_models()
        models = model_scanner.get_models_by_type(self.model_type)
        
        if models:
            # 첫 번째 모델 사용
            return models[0]['path']
            
        # 모델 스캐너에서 찾지 못한 경우 기존 방식 사용
        possible_paths = [
            # 현재 디렉토리
            f"sam_{self.model_type}_4b8939.pth",
            # MVP 디렉토리
            os.path.join("..", "..", "wall2cad_mvp", f"sam_{self.model_type}_4b8939.pth"),
            # 절대 경로
            os.path.join(os.path.dirname(__file__), "..", "..", "wall2cad_mvp", f"sam_{self.model_type}_4b8939.pth"),
            # resources/models 디렉토리
            os.path.join("..", "resources", "models", f"sam_{self.model_type}_4b8939.pth"),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                return abs_path
                
        # 기본 경로 반환
        return f"sam_{self.model_type}_4b8939.pth"
        
    def generate_masks(self, image: np.ndarray, **kwargs) -> List[Dict[str, Any]]:
        """
        이미지에서 마스크 자동 생성 (MVP 방식 참고)
        
        Args:
            image: 입력 이미지 (RGB)
            **kwargs: 추가 매개변수
            
        Returns:
            List[Dict]: 생성된 마스크 리스트
        """
        if self.mask_generator is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        try:
            print(f"Processing image shape: {image.shape}")
            
            # 매개변수 업데이트
            if kwargs:
                self._update_generator_params(**kwargs)
                
            # Generate masks
            masks = self.mask_generator.generate(image)
            
            print(f"Generated {len(masks)} masks")
            
            # Sort by area (largest first) for better visualization (MVP 방식)
            masks = sorted(masks, key=lambda x: x['area'], reverse=True)
            
            return masks
            
        except Exception as e:
            print(f"Error generating masks: {e}")
            import traceback
            traceback.print_exc()
            return []
            
    def _update_generator_params(self, **kwargs):
        """마스크 생성기 매개변수 업데이트"""
        valid_params = [
            'points_per_side', 'pred_iou_thresh', 'stability_score_thresh',
            'min_mask_region_area', 'crop_n_layers', 'crop_n_points_downscale_factor'
        ]
        
        # 새 매개변수로 생성기 재생성
        generator_kwargs = {}
        for param in valid_params:
            if param in kwargs:
                generator_kwargs[param] = kwargs[param]
                
        if generator_kwargs:
            print(f"Updating generator parameters: {generator_kwargs}")
            self.mask_generator = SamAutomaticMaskGenerator(
                model=self.sam_model,
                **generator_kwargs
            )
            
    def predict_masks(self, image: np.ndarray, point_coords: np.ndarray, 
                     point_labels: np.ndarray) -> Dict[str, Any]:
        """
        포인트 기반 마스크 예측
        
        Args:
            image: 입력 이미지
            point_coords: 점 좌표
            point_labels: 점 라벨
            
        Returns:
            Dict: 예측 결과
        """
        if self.predictor is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
            
        try:
            self.predictor.set_image(image)
            
            masks, scores, logits = self.predictor.predict(
                point_coords=point_coords,
                point_labels=point_labels,
                multimask_output=True
            )
            
            return {
                'masks': masks,
                'scores': scores,
                'logits': logits
            }
            
        except Exception as e:
            print(f"Error predicting masks: {e}")
            return {}
            
    def get_device_info(self) -> Dict[str, str]:
        """디바이스 정보 반환"""
        info = {
            'device': self.device,
            'cuda_available': torch.cuda.is_available()
        }
        
        if torch.cuda.is_available():
            info['cuda_device_name'] = torch.cuda.get_device_name()
            info['cuda_memory'] = f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB"
            
        return info
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information (MVP 호환)"""
        return {
            'model_type': self.model_type,
            'device': self.device,
            'loaded': self.sam_model is not None,
            'device_info': self.get_device_info()
        }
        
    def is_loaded(self) -> bool:
        """모델 로드 상태 확인"""
        return self.sam_model is not None
        
    @staticmethod
    def get_available_models() -> Dict[str, List[Dict[str, str]]]:
        """사용 가능한 SAM 모델 목록 반환"""
        model_scanner.scan_models()
        return model_scanner.discovered_models
        
    @staticmethod
    def add_custom_model(file_path: str) -> bool:
        """커스텀 모델 추가"""
        return model_scanner.add_custom_model(file_path)
        
    @staticmethod
    def validate_model_file(file_path: str) -> bool:
        """모델 파일 유효성 검증"""
        return model_scanner.validate_model_file(file_path)
        
    def _check_dependencies(self) -> bool:
        """필요한 의존성 모듈 확인"""
        return all([
            sam_model_registry is not None,
            SamAutomaticMaskGenerator is not None,
            SamPredictor is not None
        ])