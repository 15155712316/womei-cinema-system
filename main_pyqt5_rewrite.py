#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - PyQt5完全重构版
完全摒弃tkinter，使用纯PyQt5实现
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont

# 导入PyQt5版本的主窗口
from ui.main_window_pyqt5 import CinemaOrderSimulatorMainWindow

def setup_application():
    """设置应用程序基本配置"""
    # 设置高DPI支持
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("柴犬影院下单系统")
    app.setApplicationVersion("2.0.0-PyQt5")
    app.setOrganizationName("柴犬影院")
    app.setOrganizationDomain("shibacine.com")
    
    # 设置默认字体
    default_font = QFont("微软雅黑", 10)
    app.setFont(default_font)
    
    return app

def main():
    """主程序入口"""
    try:
        # 设置应用程序
        app = setup_application()
        
        # 创建主窗口
        main_window = CinemaOrderSimulatorMainWindow()
        
        # 启动应用程序
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 