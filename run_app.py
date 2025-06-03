#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电影票务系统启动脚本
彻底解决Qt WebEngine初始化问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    print("[启动] 🚀 启动电影票务系统...")
    
    # 🔧 在导入任何PyQt5之前设置环境变量
    os.environ['QT_WEBENGINE_CHROMIUM_FLAGS'] = '--disable-web-security'
    
    try:
        # 🔧 第一步：导入Qt核心并设置属性
        print("[启动] 设置Qt属性...")
        import PyQt5.QtCore
        PyQt5.QtCore.QCoreApplication.setAttribute(PyQt5.QtCore.Qt.AA_ShareOpenGLContexts)
        print("[启动] ✅ Qt属性设置成功")
        
        # 🔧 第二步：导入PyQt5组件
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtGui import QFont
        
        # 🔧 第三步：创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("电影票务系统")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("电影Go")
        
        # 设置默认字体
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        
        print("[启动] ✅ 应用程序创建成功")
        
        # 🔧 第四步：测试WebEngine是否可用
        print("[启动] 测试WebEngine...")
        try:
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
            print("[启动] ✅ WebEngine可用")
            webengine_available = True
        except Exception as e:
            print(f"[启动] ⚠️ WebEngine不可用: {e}")
            webengine_available = False
        
        # 🔧 第五步：导入并创建主窗口
        from main_modular import ModularCinemaMainWindow
        
        # 创建主窗口
        main_window = ModularCinemaMainWindow()
        
        # 设置WebEngine状态
        if hasattr(main_window, 'webengine_available'):
            main_window.webengine_available = webengine_available
        
        main_window.show()
        
        print("[启动] ✅ 主窗口显示成功")
        
        if webengine_available:
            print("[启动] 🎉 系统启动完成！自动监听功能可用")
        else:
            print("[启动] 🎉 系统启动完成！自动监听功能不可用，请使用手动输入模式")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"[启动] ❌ 导入错误: {e}")
        print("[启动] 💡 请检查依赖是否正确安装")
        print("[启动] 💡 尝试运行: pip install PyQtWebEngine")
        sys.exit(1)
        
    except Exception as e:
        print(f"[启动] ❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
