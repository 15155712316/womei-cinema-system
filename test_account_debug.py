#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号信息流转调试测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from ui.widgets.account_widget import AccountWidget
from ui.widgets.tab_manager_widget import TabManagerWidget
from utils.signals import event_bus

class AccountDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("账号信息流转调试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建账号组件
        print("🚀 创建账号组件...")
        self.account_widget = AccountWidget()
        layout.addWidget(self.account_widget)
        
        # 创建Tab管理器
        print("🚀 创建Tab管理器...")
        self.tab_manager = TabManagerWidget()
        layout.addWidget(self.tab_manager)
        
        # 创建调试按钮
        self.debug_button = QPushButton("检查账号状态")
        self.debug_button.clicked.connect(self.check_account_status)
        layout.addWidget(self.debug_button)
        
        # 连接信号
        self.account_widget.account_selected.connect(self.on_account_selected)
        
        # 延迟检查
        QTimer.singleShot(2000, self.initial_check)
        QTimer.singleShot(5000, self.final_check)
    
    def on_account_selected(self, account_data):
        """账号选择处理"""
        print(f"\n📱 主窗口接收到账号选择信号:")
        print(f"  - 账号: {account_data.get('phone', 'N/A')}")
        print(f"  - Token: {account_data.get('token', '')[:20]}...")
        
        # 发布全局事件
        event_bus.account_changed.emit(account_data)
        print(f"✅ 已发布全局账号变更事件")
    
    def check_account_status(self):
        """检查账号状态"""
        print(f"\n🔍 检查账号状态:")
        
        # 检查账号组件
        if hasattr(self.account_widget, 'current_account'):
            account = self.account_widget.current_account
            print(f"  - 账号组件: {account.get('phone') if account else 'None'}")
        else:
            print(f"  - 账号组件: 无current_account属性")
        
        # 检查Tab管理器
        if hasattr(self.tab_manager, 'current_account'):
            account = self.tab_manager.current_account
            print(f"  - Tab管理器: {account.get('phone') if account else 'None'}")
        else:
            print(f"  - Tab管理器: 无current_account属性")
        
        # 检查UI显示
        if hasattr(self.tab_manager, 'current_account_label'):
            label_text = self.tab_manager.current_account_label.text()
            print(f"  - UI显示: {label_text}")
        else:
            print(f"  - UI显示: 无current_account_label")
    
    def initial_check(self):
        """初始检查"""
        print(f"\n⏰ 初始检查（2秒后）:")
        self.check_account_status()
    
    def final_check(self):
        """最终检查"""
        print(f"\n⏰ 最终检查（5秒后）:")
        self.check_account_status()

def main():
    app = QApplication(sys.argv)
    window = AccountDebugWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
