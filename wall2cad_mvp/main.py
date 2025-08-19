#!/usr/bin/env python3
"""
Wall2CAD MVP - Main Application Entry Point
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_main import MainWindow

def main():
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Wall2CAD MVP")
    app.setApplicationVersion("1.0.0")
    
    # Set application properties
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()