#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 主入口文件
重构版本：使用MVC架构和事件总线
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QFont


def setup_application():
    """设置应用程序"""
    # 高DPI支持
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序信息
    app.setApplicationName("柴犬影院下单系统")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("柴犬影院")

    # 设置默认字体
    default_font = QFont("Microsoft YaHei", 10)
    app.setFont(default_font)

    # 设置应用程序样式
    app.setStyleSheet("""
        QApplication {
            font-family: "Microsoft YaHei";
        }
        QMessageBox {
            font-size: 12px;
        }
        QToolTip {
            background-color: #ffffcc;
            border: 1px solid #999999;
            padding: 5px;
            border-radius: 3px;
            font-size: 11px;
        }
    """)

    return app


def main():
    """主程序入口"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 重构版本 v2.0.0")
    print("=" * 60)
    print("🏗️  架构: MVC + 事件总线")
    print("🎨  界面: PyQt5")
    print("🔧  特性: 模块化、解耦、可扩展")
    print("=" * 60)
    print()

    try:
        # 设置应用程序
        app = setup_application()
        print("✅ 应用程序初始化完成")

        # 导入主窗口
        from views.main_window import MainWindow
        print("✅ 主窗口模块加载完成")

        # 创建主窗口
        MainWindow()  # 主窗口会自动显示
        print("✅ 主窗口创建完成")

        # 启动应用程序
        print("🚀 启动应用程序...")
        sys.exit(app.exec_())

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装:")
        print("  pip install -r requirements.txt")
        print("\n缺少的可能依赖:")
        print("  - PyQt5")
        print("  - requests")
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