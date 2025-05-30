#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tab管理器测试脚本
验证TabManagerWidget是否能正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from ui.widgets.tab_manager_widget import TabManagerWidget


class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tab管理器测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建Tab管理器
        try:
            self.tab_manager = TabManagerWidget()
            layout.addWidget(self.tab_manager)
            print("✅ TabManagerWidget 创建成功！")
        except Exception as e:
            print(f"❌ TabManagerWidget 创建失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("Tab管理器测试")
    app.setApplicationVersion("1.0.0")
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print("🚀 测试程序启动成功！")
    print("📋 Tab管理器包含以下页面:")
    print("   - 出票")
    print("   - 绑券") 
    print("   - 兑换券")
    print("   - 订单")
    print("   - 影院")
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 