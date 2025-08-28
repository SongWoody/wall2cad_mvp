"""
Wall2CAD - 모델 파일 스캐너
SAM 모델 파일을 자동 탐지하고 관리하는 유틸리티
"""

import os
import glob
from typing import List, Dict, Optional
from pathlib import Path

class ModelScanner:
    """SAM 모델 파일 스캐너"""
    
    # SAM 모델 파일명 패턴
    SAM_MODEL_PATTERNS = [
        "sam_vit_b_*.pth",
        "sam_vit_l_*.pth", 
        "sam_vit_h_*.pth"
    ]
    
    # 모델 타입 매핑
    MODEL_TYPE_MAPPING = {
        'vit_b': 'SAM ViT-B (Base)',
        'vit_l': 'SAM ViT-L (Large)',
        'vit_h': 'SAM ViT-H (Huge)'
    }
    
    def __init__(self, search_paths: Optional[List[str]] = None):
        """
        모델 스캐너 초기화
        
        Args:
            search_paths: 검색할 경로 목록 (None이면 기본 경로 사용)
        """
        self.search_paths = search_paths or self._get_default_search_paths()
        self.discovered_models = {}
        
    def _get_default_search_paths(self) -> List[str]:
        """기본 검색 경로 목록 반환"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 프로젝트 루트 찾기
        project_root = current_dir
        while project_root and not os.path.exists(os.path.join(project_root, 'main.py')):
            parent = os.path.dirname(project_root)
            if parent == project_root:  # 루트 디렉토리에 도달
                break
            project_root = parent
            
        search_paths = [
            # 현재 Wall2CAD 디렉토리
            current_dir,
            os.path.join(current_dir, '..'),
            # 프로젝트 루트
            project_root,
            # 프로젝트 루트의 상위 디렉토리
            os.path.dirname(project_root) if project_root else '',
            # 일반적인 모델 디렉토리
            os.path.join(project_root, 'models') if project_root else '',
            os.path.join(project_root, 'resources', 'models') if project_root else '',
        ]
        
        # 빈 경로 제거 및 절대 경로 변환
        return [os.path.abspath(path) for path in search_paths if path and os.path.exists(path)]
        
    def scan_models(self) -> Dict[str, List[Dict[str, str]]]:
        """
        SAM 모델 파일 스캔
        
        Returns:
            Dict: {모델_타입: [{'path': 경로, 'name': 표시명, 'size': 크기}]}
        """
        models = {'vit_b': [], 'vit_l': [], 'vit_h': []}
        
        for search_path in self.search_paths:
            try:
                # 각 패턴에 대해 검색
                for pattern in self.SAM_MODEL_PATTERNS:
                    file_pattern = os.path.join(search_path, pattern)
                    found_files = glob.glob(file_pattern)
                    
                    for file_path in found_files:
                        if os.path.isfile(file_path):
                            model_info = self._analyze_model_file(file_path)
                            if model_info:
                                model_type = model_info['type']
                                if model_type in models:
                                    # 중복 검사
                                    if not any(m['path'] == file_path for m in models[model_type]):
                                        models[model_type].append(model_info)
                                        
                # symlink 검사
                self._scan_symlinks(search_path, models)
                
            except Exception as e:
                print(f"Error scanning directory {search_path}: {e}")
                
        self.discovered_models = models
        return models
        
    def _scan_symlinks(self, search_path: str, models: Dict[str, List[Dict[str, str]]]):
        """심볼릭 링크 파일들도 검사"""
        try:
            for pattern in self.SAM_MODEL_PATTERNS:
                # 심볼릭 링크 검사를 위해 os.listdir 사용
                if not os.path.exists(search_path):
                    continue
                    
                for filename in os.listdir(search_path):
                    file_path = os.path.join(search_path, filename)
                    
                    # 심볼릭 링크이거나 일반 파일인 경우
                    if os.path.islink(file_path) or os.path.isfile(file_path):
                        # 패턴과 매치하는지 확인
                        import fnmatch
                        if fnmatch.fnmatch(filename, pattern.split('/')[-1]):
                            # 실제 파일이 존재하는지 확인
                            real_path = os.path.realpath(file_path)
                            if os.path.exists(real_path):
                                model_info = self._analyze_model_file(file_path)
                                if model_info:
                                    model_type = model_info['type']
                                    if model_type in models:
                                        # 중복 검사
                                        if not any(m['path'] == file_path for m in models[model_type]):
                                            models[model_type].append(model_info)
                                            
        except Exception as e:
            print(f"Error scanning symlinks in {search_path}: {e}")
        
    def _analyze_model_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """
        모델 파일 분석
        
        Args:
            file_path: 모델 파일 경로
            
        Returns:
            모델 정보 딕셔너리 또는 None
        """
        try:
            filename = os.path.basename(file_path)
            
            # 모델 타입 추출
            model_type = None
            for pattern in self.SAM_MODEL_PATTERNS:
                if 'vit_b' in pattern and 'vit_b' in filename.lower():
                    model_type = 'vit_b'
                    break
                elif 'vit_l' in pattern and 'vit_l' in filename.lower():
                    model_type = 'vit_l'
                    break
                elif 'vit_h' in pattern and 'vit_h' in filename.lower():
                    model_type = 'vit_h'
                    break
                    
            if not model_type:
                return None
                
            # 파일 크기 계산
            file_size = os.path.getsize(file_path)
            size_str = self._format_file_size(file_size)
            
            # 표시명 생성
            display_name = f"{self.MODEL_TYPE_MAPPING.get(model_type, model_type.upper())} ({size_str})"
            
            # 심볼릭 링크인지 확인
            if os.path.islink(file_path):
                real_path = os.path.realpath(file_path)
                display_name += f" → {os.path.basename(real_path)}"
                
            return {
                'path': file_path,
                'name': display_name,
                'type': model_type,
                'size': file_size,
                'size_str': size_str,
                'is_symlink': os.path.islink(file_path)
            }
            
        except Exception as e:
            print(f"Error analyzing model file {file_path}: {e}")
            return None
            
    def _format_file_size(self, size_bytes: int) -> str:
        """파일 크기를 읽기 쉬운 형태로 포맷"""
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
        
    def get_models_by_type(self, model_type: str) -> List[Dict[str, str]]:
        """특정 타입의 모델 목록 반환"""
        return self.discovered_models.get(model_type, [])
        
    def get_all_models(self) -> List[Dict[str, str]]:
        """모든 모델을 리스트로 반환"""
        all_models = []
        for model_list in self.discovered_models.values():
            all_models.extend(model_list)
        return all_models
        
    def get_model_info(self, file_path: str) -> Optional[Dict[str, str]]:
        """특정 파일 경로의 모델 정보 반환"""
        for model_list in self.discovered_models.values():
            for model_info in model_list:
                if model_info['path'] == file_path:
                    return model_info
        return None
        
    def validate_model_file(self, file_path: str) -> bool:
        """모델 파일 유효성 검증"""
        if not os.path.exists(file_path):
            return False
            
        try:
            # 파일 크기 검사 (SAM 모델은 최소 몇 MB 이상)
            file_size = os.path.getsize(file_path)
            if file_size < 1024 * 1024:  # 1MB 미만이면 의심스러움
                return False
                
            # 파일 확장자 검사
            if not file_path.lower().endswith('.pth'):
                return False
                
            # 파일명 패턴 검사
            filename = os.path.basename(file_path).lower()
            if not any(pattern.replace('*', '').replace('.pth', '') in filename 
                      for pattern in ['sam_vit_b', 'sam_vit_l', 'sam_vit_h']):
                return False
                
            return True
            
        except Exception as e:
            print(f"Error validating model file {file_path}: {e}")
            return False
            
    def add_custom_model(self, file_path: str) -> bool:
        """커스텀 모델 경로 추가"""
        if not self.validate_model_file(file_path):
            return False
            
        model_info = self._analyze_model_file(file_path)
        if not model_info:
            return False
            
        model_type = model_info['type']
        if model_type in self.discovered_models:
            # 중복 검사
            if not any(m['path'] == file_path for m in self.discovered_models[model_type]):
                self.discovered_models[model_type].append(model_info)
                return True
                
        return False
        
    def get_default_model_path(self, model_type: str = 'vit_h') -> Optional[str]:
        """기본 모델 경로 반환"""
        if model_type in self.discovered_models and self.discovered_models[model_type]:
            # 첫 번째 모델 사용
            return self.discovered_models[model_type][0]['path']
        return None


# 전역 스캐너 인스턴스
model_scanner = ModelScanner()