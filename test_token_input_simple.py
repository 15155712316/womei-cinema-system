#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试Token输入框问题
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_token_input():
    """测试Token输入框"""
    print("🔍 简单Token输入框测试")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("Token输入框测试")
    window.setGeometry(300, 200, 400, 300)
    
    # 创建中央部件
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # 添加说明
    layout.addWidget(QLabel("请尝试在Token输入框中输入文字"))
    
    # 导入并创建账号组件
    try:
        from ui.widgets.account_widget import AccountWidget
        account_widget = AccountWidget()
        layout.addWidget(account_widget)
        
        # 添加测试按钮
        test_btn = QPushButton("检查Token输入框内容")
        def check_content():
            token_text = account_widget.token_input.text()
            print(f"[测试] Token输入框内容: '{token_text}' ({len(token_text)}字符)")
            
        test_btn.clicked.connect(check_content)
        layout.addWidget(test_btn)
        
        print(f"✅ 账号组件加载成功")
        
    except Exception as e:
        error_label = QLabel(f"❌ 加载失败: {e}")
        layout.addWidget(error_label)
        print(f"❌ 加载失败: {e}")
    
    window.show()
    
    print(f"📋 请在Token输入框中尝试输入文字")
    print(f"📋 观察控制台是否有调试信息输出")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_token_input()
