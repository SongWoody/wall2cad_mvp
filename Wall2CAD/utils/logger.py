"""
Wall2CAD - 로깅 시스템
애플리케이션 로깅 및 디버깅 지원
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal

class LogHandler(logging.Handler, QObject):
    """Qt 시그널을 지원하는 로그 핸들러"""
    
    log_message = pyqtSignal(str, str)  # level, message
    
    def __init__(self):
        logging.Handler.__init__(self)
        QObject.__init__(self)
        
    def emit(self, record):
        """로그 메시지 발신"""
        try:
            msg = self.format(record)
            level = record.levelname
            self.log_message.emit(level, msg)
        except Exception:
            self.handleError(record)

class Logger:
    """Wall2CAD 로거 클래스"""
    
    def __init__(self, name: str = "Wall2CAD", log_dir: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 로그 디렉토리 설정
        if log_dir is None:
            log_dir = os.path.expanduser('~/.wall2cad/logs')
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 핸들러 설정
        self.setup_handlers()
        
        # Qt 시그널 핸들러
        self.qt_handler = LogHandler()
        self.qt_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.qt_handler.setFormatter(formatter)
        self.logger.addHandler(self.qt_handler)
        
    def setup_handlers(self):
        """로그 핸들러 설정"""
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # 파일 핸들러 (상세 로그)
        log_file = os.path.join(self.log_dir, f'{self.name.lower()}.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 파일 포매터
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # 콘솔 핸들러 (기본 로그)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 콘솔 포매터
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 에러 파일 핸들러 (에러만)
        error_file = os.path.join(self.log_dir, f'{self.name.lower()}_errors.log')
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
    def debug(self, message: str, *args, **kwargs):
        """디버그 로그"""
        self.logger.debug(message, *args, **kwargs)
        
    def info(self, message: str, *args, **kwargs):
        """정보 로그"""
        self.logger.info(message, *args, **kwargs)
        
    def warning(self, message: str, *args, **kwargs):
        """경고 로그"""
        self.logger.warning(message, *args, **kwargs)
        
    def error(self, message: str, *args, **kwargs):
        """에러 로그"""
        self.logger.error(message, *args, **kwargs)
        
    def critical(self, message: str, *args, **kwargs):
        """심각한 에러 로그"""
        self.logger.critical(message, *args, **kwargs)
        
    def exception(self, message: str, *args, **kwargs):
        """예외 로그 (스택 트레이스 포함)"""
        self.logger.exception(message, *args, **kwargs)
        
    def log_system_info(self):
        """시스템 정보 로깅"""
        import platform
        import torch
        
        self.info("=== System Information ===")
        self.info(f"OS: {platform.system()} {platform.release()}")
        self.info(f"Python: {platform.python_version()}")
        self.info(f"PyTorch: {torch.__version__}")
        self.info(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            self.info(f"CUDA Device: {torch.cuda.get_device_name()}")
            self.info(f"CUDA Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
            
    def log_performance(self, operation: str, duration: float, **kwargs):
        """성능 로깅"""
        message = f"Performance - {operation}: {duration:.3f}s"
        
        if kwargs:
            details = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            message += f" ({details})"
            
        self.info(message)
        
    def log_sam_processing(self, image_shape: tuple, mask_count: int, 
                          processing_time: float, params: dict):
        """SAM 처리 로깅"""
        self.info(f"SAM Processing - Image: {image_shape}, "
                 f"Masks: {mask_count}, Time: {processing_time:.3f}s")
        self.debug(f"SAM Parameters: {params}")
        
    def log_dxf_export(self, file_path: str, entity_count: int, 
                      file_size: Optional[int] = None):
        """DXF 내보내기 로깅"""
        message = f"DXF Export - File: {os.path.basename(file_path)}, Entities: {entity_count}"
        
        if file_size is not None:
            message += f", Size: {file_size / 1024:.1f}KB"
            
        self.info(message)
        
    def log_error_with_context(self, error: Exception, context: str = ""):
        """컨텍스트와 함께 에러 로깅"""
        error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
        
        self.error(error_msg)
        self.debug(f"Exception type: {type(error).__name__}")
        self.debug(f"Traceback:\n{traceback.format_exc()}")
        
    def create_session_log(self) -> str:
        """세션 로그 파일 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(self.log_dir, f"session_{timestamp}.log")
        
        # 세션 시작 로그
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"Wall2CAD Session Started: {datetime.now()}\n")
            f.write("=" * 50 + "\n")
            
        self.info(f"Session log created: {session_file}")
        return session_file
        
    def cleanup_old_logs(self, days: int = 30):
        """오래된 로그 파일 정리"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            removed_count = 0
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(self.log_dir, filename)
                    
                    if os.path.getctime(file_path) < cutoff_time:
                        os.remove(file_path)
                        removed_count += 1
                        
            if removed_count > 0:
                self.info(f"Cleaned up {removed_count} old log files")
                
        except Exception as e:
            self.error(f"Error cleaning up log files: {e}")
            
    def set_level(self, level: str):
        """로깅 레벨 설정"""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        
        if level.upper() in level_map:
            self.logger.setLevel(level_map[level.upper()])
            self.info(f"Logging level set to {level.upper()}")
        else:
            self.warning(f"Unknown logging level: {level}")
            
    def get_qt_handler(self) -> LogHandler:
        """Qt 시그널 핸들러 반환"""
        return self.qt_handler
        
    def flush(self):
        """모든 핸들러 플러시"""
        for handler in self.logger.handlers:
            handler.flush()

# 전역 로거 인스턴스
logger = Logger()

# 편의 함수들
def debug(message: str, *args, **kwargs):
    logger.debug(message, *args, **kwargs)

def info(message: str, *args, **kwargs):
    logger.info(message, *args, **kwargs)

def warning(message: str, *args, **kwargs):
    logger.warning(message, *args, **kwargs)

def error(message: str, *args, **kwargs):
    logger.error(message, *args, **kwargs)

def critical(message: str, *args, **kwargs):
    logger.critical(message, *args, **kwargs)

def exception(message: str, *args, **kwargs):
    logger.exception(message, *args, **kwargs)