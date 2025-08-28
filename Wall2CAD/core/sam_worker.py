"""
Wall2CAD - SAM 워커 스레드
백그라운드에서 SAM 모델 로딩 및 세그멘테이션 수행
"""

import os
import time
import traceback
from typing import Optional, Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal, QMutex
import numpy as np

from core.sam_processor import SAMProcessor


class SAMWorkerThread(QThread):
    """SAM 모델 로딩 및 처리를 위한 워커 스레드"""
    
    # 시그널 정의
    model_load_started = pyqtSignal()
    model_load_progress = pyqtSignal(int, str)  # progress, message
    model_load_finished = pyqtSignal(bool, str)  # success, message
    
    segmentation_started = pyqtSignal()
    segmentation_progress = pyqtSignal(int, str)  # progress, message
    segmentation_finished = pyqtSignal(bool, list, str)  # success, masks, message
    
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.sam_processor = None
        self.mutex = QMutex()
        
        # 작업 상태
        self.current_task = None
        self.should_stop = False
        
        # 모델 로딩 매개변수
        self.model_path = ""
        self.model_type = "vit_h"
        
        # 세그멘테이션 매개변수
        self.input_image = None
        self.sam_params = {}
        
    def load_sam_model(self, model_path: str, model_type: str = "vit_h"):
        """
        SAM 모델 로딩 작업 설정
        
        Args:
            model_path: 모델 파일 경로
            model_type: 모델 타입 (vit_b, vit_l, vit_h)
        """
        self.mutex.lock()
        try:
            self.current_task = "load_model"
            self.model_path = model_path
            self.model_type = model_type
            self.should_stop = False
            
            if not self.isRunning():
                self.start()
        finally:
            self.mutex.unlock()
            
    def run_segmentation(self, image: np.ndarray, params: Dict[str, Any]):
        """
        세그멘테이션 작업 설정
        
        Args:
            image: 입력 이미지
            params: SAM 매개변수
        """
        self.mutex.lock()
        try:
            self.current_task = "segmentation"
            self.input_image = image.copy()
            self.sam_params = params.copy()
            self.should_stop = False
            
            if not self.isRunning():
                self.start()
        finally:
            self.mutex.unlock()
            
    def stop_processing(self):
        """처리 중단"""
        self.mutex.lock()
        try:
            self.should_stop = True
            self.current_task = None
        finally:
            self.mutex.unlock()
            
    def run(self):
        """워커 스레드 메인 실행 함수"""
        try:
            if self.current_task == "load_model":
                self._run_model_loading()
            elif self.current_task == "segmentation":
                self._run_segmentation()
                
        except Exception as e:
            error_msg = f"워커 스레드 오류: {str(e)}"
            print(f"Worker thread error: {e}")
            print(traceback.format_exc())
            self.error_occurred.emit(error_msg)
            
    def _run_model_loading(self):
        """모델 로딩 실행"""
        try:
            self.model_load_started.emit()
            
            if self.should_stop:
                return
                
            # 1. 모델 파일 검증
            self.model_load_progress.emit(10, "모델 파일 검증 중...")
            if not os.path.exists(self.model_path):
                self.model_load_finished.emit(False, f"모델 파일을 찾을 수 없습니다: {self.model_path}")
                return
                
            if self.should_stop:
                return
                
            # 2. SAM 프로세서 초기화
            self.model_load_progress.emit(20, "SAM 프로세서 초기화 중...")
            self.sam_processor = SAMProcessor(self.model_type)
            
            if self.should_stop:
                return
                
            # 3. segment_anything 모듈 확인
            self.model_load_progress.emit(30, "Segment Anything 모듈 확인 중...")
            if not self.sam_processor._check_dependencies():
                self.model_load_finished.emit(False, "Segment Anything 모듈이 설치되지 않았습니다.")
                return
                
            if self.should_stop:
                return
                
            # 4. 모델 로딩 시작
            self.model_load_progress.emit(40, "SAM 모델 로딩 중... (시간이 걸릴 수 있습니다)")
            
            # 실제 모델 로딩 (시간이 오래 걸림)
            success = self.sam_processor.load_model(self.model_path)
            
            if self.should_stop:
                return
                
            if success:
                self.model_load_progress.emit(90, "모델 초기화 완료 중...")
                time.sleep(0.5)  # UI 업데이트를 위한 짧은 대기
                
                self.model_load_progress.emit(100, "모델 로딩 완료!")
                
                # 디바이스 정보 가져오기
                device_info = self.sam_processor.get_device_info()
                device_msg = f"디바이스: {device_info.get('device', 'unknown')}"
                
                self.model_load_finished.emit(True, f"모델 로딩 성공! {device_msg}")
            else:
                self.model_load_finished.emit(False, "모델 로딩에 실패했습니다.")
                
        except Exception as e:
            error_msg = f"모델 로딩 중 오류: {str(e)}"
            print(f"Model loading error: {e}")
            print(traceback.format_exc())
            self.model_load_finished.emit(False, error_msg)
            
    def _run_segmentation(self):
        """세그멘테이션 실행"""
        try:
            self.segmentation_started.emit()
            
            if not self.sam_processor or not self.sam_processor.is_loaded():
                self.segmentation_finished.emit(False, [], "모델이 로드되지 않았습니다.")
                return
                
            if self.should_stop:
                return
                
            # 1. 이미지 전처리
            self.segmentation_progress.emit(10, "이미지 전처리 중...")
            
            # 이미지 크기 확인 및 조정
            h, w = self.input_image.shape[:2]
            if max(h, w) > 1024:
                scale = 1024 / max(h, w)
                new_h, new_w = int(h * scale), int(w * scale)
                import cv2
                resized_image = cv2.resize(self.input_image, (new_w, new_h))
                print(f"이미지 크기 조정: {w}x{h} -> {new_w}x{new_h}")
            else:
                resized_image = self.input_image
                
            if self.should_stop:
                return
                
            # 2. 세그멘테이션 실행
            self.segmentation_progress.emit(30, "SAM 세그멘테이션 실행 중...")
            
            # SAM 매개변수 적용
            masks = self.sam_processor.generate_masks(
                resized_image, 
                **self.sam_params
            )
            
            if self.should_stop:
                return
                
            # 3. 결과 처리
            self.segmentation_progress.emit(90, "결과 처리 중...")
            
            if masks:
                self.segmentation_progress.emit(100, f"세그멘테이션 완료! ({len(masks)}개 마스크 생성)")
                self.segmentation_finished.emit(True, masks, f"{len(masks)}개 마스크가 생성되었습니다.")
            else:
                self.segmentation_finished.emit(False, [], "세그멘테이션 결과가 없습니다.")
                
        except Exception as e:
            error_msg = f"세그멘테이션 중 오류: {str(e)}"
            print(f"Segmentation error: {e}")
            print(traceback.format_exc())
            self.segmentation_finished.emit(False, [], error_msg)
            
    def get_model_info(self) -> Dict[str, Any]:
        """현재 로드된 모델 정보 반환"""
        if self.sam_processor and self.sam_processor.is_loaded():
            return {
                'loaded': True,
                'model_type': self.model_type,
                'model_path': self.model_path,
                'device_info': self.sam_processor.get_device_info()
            }
        return {'loaded': False}
        
    def is_model_loaded(self) -> bool:
        """모델 로드 상태 확인"""
        return self.sam_processor is not None and self.sam_processor.is_loaded()