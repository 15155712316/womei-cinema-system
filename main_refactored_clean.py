#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 重构版本 (干净启动)
确保只运行重构版本，避免Tab管理器干扰
"""

import sys
import os

def clean_imports():
    """清理可能冲突的导入"""
    # 移除可能导致冲突的模块
    modules_to_remove = []
    for module_name in sys.modules.keys():
        if any(keyword in module_name.lower() for keyword in ['tab_manager', 'main_modular']):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        print(f"清理模块: {module_name}")
        del sys.modules[module_name]

def main():
    """主程序入口 - 重构版本专用"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 重构版本 v2.0.0 (干净启动)")
    print("=" * 60)
    print("🏗️  架构: MVC + 事件总线")
    print("🎨  界面: PyQt5")
    print("🔧  特性: 模块化、解耦、可扩展")
    print("🧹  模式: 干净启动，避免Tab管理器干扰")
    print("=" * 60)
    print()
    
    try:
        # 清理可能冲突的导入
        clean_imports()
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QCoreApplication
        from PyQt5.QtGui import QFont
        
        # 高DPI支持
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("柴犬影院下单系统-重构版")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入重构版本主窗口
        from views.main_window import MainWindow
        print("✅ 重构版本主窗口模块加载完成")
        
        # 创建主窗口
        MainWindow()
        print("✅ 重构版本主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动重构版本应用程序...")
        print("💡 如果看到\"等待账号选择\"日志，说明有其他进程在运行")
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
