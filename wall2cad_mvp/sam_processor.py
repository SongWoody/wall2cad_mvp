"""
Wall2CAD MVP - SAM Model Processor
"""

import torch
import numpy as np
import sys
import os

# Add parent directory to path to import segment_anything
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
except ImportError:
    print("Error: segment_anything module not found. Please check installation.")
    sys.exit(1)

class SAMProcessor:
    """SAM model processor for automatic mask generation"""
    
    def __init__(self, model_type="vit_h", checkpoint_path=None):
        """
        Initialize SAM processor
        
        Args:
            model_type: SAM model type (vit_h, vit_l, vit_b)
            checkpoint_path: Path to model checkpoint file
        """
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Default checkpoint path
        if checkpoint_path is None:
            checkpoint_path = self._find_checkpoint()
            
        self.checkpoint_path = checkpoint_path
        self.sam_model = None
        self.mask_generator = None
        
        self._load_model()
        
    def _find_checkpoint(self):
        """Find SAM checkpoint file"""
        possible_paths = [
            f"sam_{self.model_type}_4b8939.pth",  # Current directory
            f"../notebooks/sam_{self.model_type}_4b8939.pth",  # Notebooks directory
            f"models/sam_{self.model_type}_4b8939.pth"  # Models directory
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        raise FileNotFoundError(
            f"SAM checkpoint file not found. Please ensure sam_{self.model_type}_4b8939.pth "
            f"is available in one of these locations: {possible_paths}"
        )
        
    def _load_model(self):
        """Load SAM model and initialize mask generator"""
        print(f"SAM 모델 로딩 시작 ({self.model_type}) on {self.device}...")
        
        # Load SAM model
        print("모델 체크포인트 로딩 중...")
        self.sam_model = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
        
        print(f"모델을 {self.device} 디바이스로 이동 중...")
        self.sam_model.to(device=self.device)
        
        # Initialize automatic mask generator with optimized parameters
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
        
        print("SAM 모델 로딩 완료!")
        
    def generate_masks(self, image):
        """
        Generate masks for input image
        
        Args:
            image: RGB image as numpy array
            
        Returns:
            List of mask dictionaries
        """
        if self.mask_generator is None:
            raise RuntimeError("SAM model not initialized")
            
        print(f"Processing image shape: {image.shape}")
        
        # Generate masks
        masks = self.mask_generator.generate(image)
        
        print(f"Generated {len(masks)} masks")
        
        # Sort by area (largest first) for better visualization
        masks = sorted(masks, key=lambda x: x['area'], reverse=True)
        
        return masks
        
    def get_model_info(self):
        """Get model information"""
        return {
            'model_type': self.model_type,
            'device': self.device,
            'checkpoint_path': self.checkpoint_path,
            'loaded': self.sam_model is not None
        }