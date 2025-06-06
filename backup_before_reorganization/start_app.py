#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电影票务系统启动脚本
修复Qt WebEngine初始化问题
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("[启动] 🚀 启动电影票务系统...")

# 🔧 在创建QApplication之前设置Qt属性
print("[启动] 设置Qt属性...")
import PyQt5.QtCore
PyQt5.QtCore.QCoreApplication.setAttribute(PyQt5.QtCore.Qt.AA_ShareOpenGLContexts)
print("[启动] ✅ Qt属性设置成功")

# 现在可以安全地导入其他PyQt5组件
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

def main():
    """主函数"""
    try:
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序属性
        app.setApplicationName("电影票务系统")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("电影Go")
        
        # 设置默认字体
        font = QFont("Microsoft YaHei", 9)
        app.setFont(font)
        
        print("[启动] ✅ 应用程序创建成功")
        
        # 导入并创建主窗口
        from main_modular import ModularCinemaMainWindow

        # 创建主窗口
        main_window = ModularCinemaMainWindow()
        main_window.show()
        
        print("[启动] ✅ 主窗口显示成功")
        print("[启动] 🎉 系统启动完成！")
        
        # 运行应用程序
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"[启动] ❌ 导入错误: {e}")
        print("[启动] 💡 请检查依赖是否正确安装")
        sys.exit(1)
        
    except Exception as e:
        print(f"[启动] ❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
