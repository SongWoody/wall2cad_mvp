#!/usr/bin/env python3
"""
Wall2CAD - 애플리케이션 진입점
SAM 기반 이미지 세그멘테이션 및 벡터 변환 도구
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    """애플리케이션 메인 함수"""
    # QApplication 생성
    app = QApplication(sys.argv)
    
    # 애플리케이션 속성 설정
    app.setApplicationName("Wall2CAD")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Wall2CAD Team")
    
    # 고해상도 DPI 지원 (PyQt6에서는 기본적으로 활성화됨)
    # PyQt6에서는 AA_EnableHighDpiScaling이 더 이상 필요하지 않음
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()
    
    # 애플리케이션 실행
    sys.exit(app.exec())

if __name__ == "__main__":
    main()