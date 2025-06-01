#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 主入口优化版 (智能默认选择)
"""

import sys
import os

def main():
    """主程序入口 - 智能默认选择优化版"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 主入口优化版")
    print("=" * 60)
    print("🏗️  架构: 单体架构 + Tab管理器")
    print("🎨  界面: 传统PyQt5界面")
    print("🔧  特性: 完整功能 + 智能默认选择")
    print("✨  优化: 登录后自动选择影院和账号")
    print("🚀  流程: 登录→主界面→自动选择影院→自动选择账号→加载影片")
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
        app.setApplicationName("柴犬影院下单系统-优化版")
        app.setApplicationVersion("1.6.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入主窗口
        from main_modular import ModularCinemaMainWindow
        print("✅ 优化版主窗口模块加载完成")
        
        # 创建主窗口
        window = ModularCinemaMainWindow()
        print("✅ 优化版主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动优化版应用程序...")
        print("💡 登录后将自动选择默认影院和关联账号")
        print("🎯 不再出现'等待账号选择'问题")
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
