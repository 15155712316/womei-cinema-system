#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 现代化UI启动程序
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window_modern import CinemaOrderSimulatorModernWindow


def main():
    """主程序入口"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("柴犬影院下单系统")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("柴犬影院")
    
    # 设置高DPI支持
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei", 10)
    app.setFont(default_font)
    
    # 设置现代化样式
    app.setStyle('Fusion')
    
    try:
        # 创建主窗口
        window = CinemaOrderSimulatorModernWindow()
        window.show()
        
        # 启动应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 