#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 重构版本 v2.1.0 (智能加载优化)
"""

import sys
import os

def main():
    """主程序入口 - 智能加载优化版"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 重构版本 v2.1.0")
    print("=" * 60)
    print("🏗️  架构: MVC + 事件总线")
    print("🎨  界面: PyQt5")
    print("🔧  特性: 模块化、解耦、可扩展")
    print("✨  优化: 智能数据加载 (影院→账号)")
    print("🚀  流程: 登录→主界面→自动选择影院→自动选择账号")
    print("=" * 60)
    print()
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QCoreApplication
        from PyQt5.QtGui import QFont
        
        # 高DPI支持
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("柴犬影院下单系统-智能版")
        app.setApplicationVersion("2.1.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入重构版本主窗口
        from views.main_window import MainWindow
        print("✅ 智能版主窗口模块加载完成")
        
        # 创建主窗口
        MainWindow()
        print("✅ 智能版主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动智能版应用程序...")
        print("💡 登录后将自动选择默认影院和账号")
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装:")
        print("  pip install -r requirements.txt")
        input("\n按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        print("\n错误详情:")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
