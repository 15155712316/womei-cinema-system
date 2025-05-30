#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试场次显示修复
验证PyQt5版本的场次显示是否正确显示时间、厅名和价格信息
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

from ui.components.cinema_select_panel_pyqt5 import CinemaSelectPanelPyQt5

class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("场次显示测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建影院选择面板
        self.cinema_panel = CinemaSelectPanelPyQt5(self)
        self.cinema_panel.main_window = self  # 设置主窗口引用
        layout.addWidget(self.cinema_panel)
        
        # 使用真实账号数据而不是测试数据
        try:
            import json
            accounts_file = "data/accounts.json"
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
                if accounts:
                    self.current_account = accounts[0]  # 使用第一个真实账号
                    print(f"✅ 使用真实账号: {self.current_account.get('userid', 'N/A')}")
                else:
                    self.current_account = self._create_dummy_account()
            else:
                self.current_account = self._create_dummy_account()
        except Exception as e:
            print(f"⚠️ 加载真实账号失败: {e}")
            self.current_account = self._create_dummy_account()
        
        print("测试窗口已创建")
        print("请按以下步骤测试：")
        print("1. 选择一个影院")
        print("2. 选择一个影片")
        print("3. 选择一个日期")
        print("4. 查看场次下拉框是否显示：时间 厅名 厅信息 票价:价格")
    
    def get_current_account(self):
        """获取当前账号（供影院面板调用）"""
        return self.current_account
    
    def _clear_coupons_impl(self):
        """清空券列表（供影院面板调用）"""
        print("[DEBUG] 清空券列表")

    def _create_dummy_account(self):
        """创建虚拟账号用于测试"""
        print("⚠️ 使用虚拟账号进行测试（可能导致API调用失败）")
        return {
            'phone': '15155712316',
            'openid': 'test_openid',
            'token': 'test_token',
            'userid': 'test_userid'
        }

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置高DPI支持
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 创建测试窗口
    window = TestMainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 