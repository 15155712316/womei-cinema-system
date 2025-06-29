#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券管理UI功能演示脚本
展示新集成的券管理功能
"""

import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer

# 导入券管理组件
from ui.widgets.voucher_widget import VoucherWidget
from ui.widgets.classic_components import ClassicGroupBox, ClassicButton, ClassicLabel

class VoucherDemoWindow(QMainWindow):
    """券管理演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美券管理系统演示")
        self.setGeometry(100, 100, 1000, 700)
        
        # 加载测试账号
        self.test_account = self._load_test_account()
        self.cinema_id = "400028"  # 测试影院ID
        
        self._setup_ui()
        self._setup_demo_data()
    
    def _load_test_account(self):
        """加载测试账号"""
        try:
            with open('data/accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
                if accounts and len(accounts) > 0:
                    return accounts[0]
        except:
            pass
        
        # 默认测试账号
        return {
            "phone": "15155712316",
            "token": "c33d6b500b34c87b71ac8fad4cfb6769"
        }
    
    def _setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        self._create_title_area(layout)
        
        # 账号信息区域
        self._create_account_area(layout)
        
        # 券管理组件
        self._create_voucher_area(layout)
        
        # 操作按钮区域
        self._create_action_area(layout)
    
    def _create_title_area(self, parent_layout):
        """创建标题区域"""
        title_group = ClassicGroupBox("券管理系统演示")
        title_layout = QVBoxLayout(title_group)
        
        title_label = ClassicLabel("沃美券管理系统 - UI集成演示", "info")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                padding: 15px;
            }
        """)
        title_layout.addWidget(title_label)
        
        desc_label = ClassicLabel(
            "本演示展示了新开发的券管理API与现有UI框架的完整集成。\n"
            "功能包括：券列表获取、状态过滤、统计信息显示、实时数据加载等。"
        )
        desc_label.setStyleSheet("color: #666; font-size: 12px; text-align: center; padding: 10px;")
        title_layout.addWidget(desc_label)
        
        parent_layout.addWidget(title_group)
    
    def _create_account_area(self, parent_layout):
        """创建账号信息区域"""
        account_group = ClassicGroupBox("测试账号信息")
        account_layout = QHBoxLayout(account_group)
        
        # 账号信息显示
        phone = self.test_account.get('phone', '未知')
        token_preview = self.test_account.get('token', '')[:20] + "..." if self.test_account.get('token') else '无'
        
        self.account_info_label = ClassicLabel(f"手机号: {phone} | Token: {token_preview} | 影院ID: {self.cinema_id}")
        self.account_info_label.setStyleSheet("color: #333; font-size: 12px; padding: 5px;")
        account_layout.addWidget(self.account_info_label)
        
        # 设置账号按钮
        self.set_account_btn = ClassicButton("设置账号信息", "primary")
        self.set_account_btn.setMaximumWidth(120)
        self.set_account_btn.clicked.connect(self._set_account_info)
        account_layout.addWidget(self.set_account_btn)
        
        account_layout.addStretch()
        parent_layout.addWidget(account_group)
    
    def _create_voucher_area(self, parent_layout):
        """创建券管理区域"""
        # 创建券管理组件
        self.voucher_widget = VoucherWidget()
        
        # 连接信号
        self.voucher_widget.voucher_selected.connect(self._on_voucher_selected)
        
        parent_layout.addWidget(self.voucher_widget)
    
    def _create_action_area(self, parent_layout):
        """创建操作按钮区域"""
        action_group = ClassicGroupBox("演示操作")
        action_layout = QHBoxLayout(action_group)
        
        # 测试API按钮
        self.test_api_btn = ClassicButton("测试券API", "success")
        self.test_api_btn.clicked.connect(self._test_voucher_api)
        action_layout.addWidget(self.test_api_btn)
        
        # 模拟选择券按钮
        self.simulate_select_btn = ClassicButton("模拟选择券", "warning")
        self.simulate_select_btn.clicked.connect(self._simulate_voucher_selection)
        action_layout.addWidget(self.simulate_select_btn)
        
        # 清空数据按钮
        self.clear_data_btn = ClassicButton("清空数据", "danger")
        self.clear_data_btn.clicked.connect(self._clear_voucher_data)
        action_layout.addWidget(self.clear_data_btn)
        
        action_layout.addStretch()
        
        # 状态显示
        self.status_label = ClassicLabel("准备就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
        action_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(action_group)
    
    def _setup_demo_data(self):
        """设置演示数据"""
        # 自动设置账号信息
        QTimer.singleShot(500, self._set_account_info)
    
    def _set_account_info(self):
        """设置账号信息到券组件"""
        try:
            self.voucher_widget.set_account_info(self.test_account, self.cinema_id)
            self.status_label.setText("账号信息已设置")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; margin-left: 20px;")
            
            print(f"[演示] 账号信息已设置: {self.test_account.get('phone')} | 影院: {self.cinema_id}")
            
        except Exception as e:
            self.status_label.setText(f"设置失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; margin-left: 20px;")
            print(f"[演示] 设置账号信息失败: {e}")
    
    def _test_voucher_api(self):
        """测试券API"""
        try:
            self.status_label.setText("正在测试API...")
            self.status_label.setStyleSheet("color: #2196F3; font-size: 11px; margin-left: 20px;")
            
            # 触发券组件刷新
            self.voucher_widget.refresh_vouchers()
            
            print("[演示] 券API测试已启动")
            
        except Exception as e:
            self.status_label.setText(f"API测试失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; margin-left: 20px;")
            print(f"[演示] API测试失败: {e}")
    
    def _simulate_voucher_selection(self):
        """模拟券选择"""
        try:
            selected_voucher = self.voucher_widget.get_selected_voucher()
            
            if selected_voucher:
                voucher_name = selected_voucher.get('voucher_name', '未知券')
                voucher_code = selected_voucher.get('voucher_code_mask', '无券号')
                
                self.status_label.setText(f"已选择: {voucher_name}")
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; margin-left: 20px;")
                
                print(f"[演示] 模拟选择券: {voucher_name} ({voucher_code})")
            else:
                self.status_label.setText("请先选择一张券")
                self.status_label.setStyleSheet("color: #ff8c00; font-size: 11px; margin-left: 20px;")
                print("[演示] 没有选中的券")
                
        except Exception as e:
            self.status_label.setText(f"选择失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; margin-left: 20px;")
            print(f"[演示] 券选择失败: {e}")
    
    def _clear_voucher_data(self):
        """清空券数据"""
        try:
            self.voucher_widget.clear_data()
            self.status_label.setText("数据已清空")
            self.status_label.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
            
            print("[演示] 券数据已清空")
            
        except Exception as e:
            self.status_label.setText(f"清空失败: {str(e)}")
            self.status_label.setStyleSheet("color: #f44336; font-size: 11px; margin-left: 20px;")
            print(f"[演示] 清空数据失败: {e}")
    
    def _on_voucher_selected(self, voucher_data):
        """处理券选择事件"""
        try:
            voucher_name = voucher_data.get('voucher_name', '未知券')
            voucher_code = voucher_data.get('voucher_code_mask', '无券号')
            is_valid = voucher_data.get('is_valid', False)
            
            status_text = "有效" if is_valid else "无效"
            self.status_label.setText(f"选中券: {voucher_name} ({status_text})")
            
            if is_valid:
                self.status_label.setStyleSheet("color: #4CAF50; font-size: 11px; margin-left: 20px;")
            else:
                self.status_label.setStyleSheet("color: #f44336; font-size: 11px; margin-left: 20px;")
            
            print(f"[演示] 券选择事件: {voucher_name} ({voucher_code}) - {status_text}")
            
        except Exception as e:
            print(f"[演示] 处理券选择事件失败: {e}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("沃美券管理系统演示")
    app.setApplicationVersion("1.0.0")
    
    # 创建并显示演示窗口
    demo_window = VoucherDemoWindow()
    demo_window.show()
    
    print("🚀 券管理UI演示启动")
    print("📋 功能说明:")
    print("   1. 自动加载测试账号信息")
    print("   2. 点击'测试券API'按钮获取真实券数据")
    print("   3. 在券列表中选择券查看详情")
    print("   4. 支持有效券过滤和统计显示")
    print("   5. 完整的错误处理和状态提示")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
