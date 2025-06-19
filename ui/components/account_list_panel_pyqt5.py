#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号列表面板 - PyQt5版本
完全复刻tkinter版本的功能和布局
"""

import os
import json
from typing import Callable, Optional, Dict, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QHeaderView, QAbstractItemView, QMenu,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor

class AccountListPanelPyQt5(QWidget):
    """账号列表面板 - PyQt5版本"""
    
    def __init__(self, parent=None, on_account_selected=None, on_set_main=None, 
                 on_clear_coupons=None, on_refresh_coupons=None):
        super().__init__(parent)
        
        # 回调函数
        self.on_account_selected = on_account_selected
        self.on_set_main = on_set_main
        self.on_clear_coupons = on_clear_coupons
        self.on_refresh_coupons = on_refresh_coupons
        
        # 数据
        self.accounts_data = []
        self.current_selected_account = None
        
        self._init_ui()
        self._load_accounts()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 账号树形列表
        self.account_tree = QTreeWidget()
        self.account_tree.setHeaderLabels(["手机号", "状态", "主账号"])
        self.account_tree.setFont(QFont("微软雅黑", 10))
        
        # 设置列宽
        header = self.account_tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 手机号列
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # 状态列
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 主账号列
        
        # 设置选择模式
        self.account_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 绑定事件
        self.account_tree.itemClicked.connect(self._on_item_clicked)
        self.account_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.account_tree.customContextMenuRequested.connect(self._show_context_menu)
        
        # 设置样式
        self.account_tree.setStyleSheet("""
            QTreeWidget {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item {
                padding: 3px;
                border-bottom: 1px solid #eee;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QTreeWidget::item:hover {
                background-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.account_tree)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFont(QFont("微软雅黑", 9))
        self.refresh_btn.clicked.connect(self.refresh_account_list)
        self._setup_button_style(self.refresh_btn, "#28a745")
        button_layout.addWidget(self.refresh_btn)
        
        # 清空券按钮
        self.clear_coupons_btn = QPushButton("清空券")
        self.clear_coupons_btn.setFont(QFont("微软雅黑", 9))
        self.clear_coupons_btn.clicked.connect(self._on_clear_coupons)
        self._setup_button_style(self.clear_coupons_btn, "#dc3545")
        button_layout.addWidget(self.clear_coupons_btn)
        
        # 刷新券按钮
        self.refresh_coupons_btn = QPushButton("刷新券")
        self.refresh_coupons_btn.setFont(QFont("微软雅黑", 9))
        self.refresh_coupons_btn.clicked.connect(self._on_refresh_coupons)
        self._setup_button_style(self.refresh_coupons_btn, "#17a2b8")
        button_layout.addWidget(self.refresh_coupons_btn)
        
        button_layout.addStretch()  # 添加弹簧
        layout.addLayout(button_layout)
        
        # 状态标签
        self.status_label = QLabel("请选择账号")
        self.status_label.setFont(QFont("微软雅黑", 9))
        self.status_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.status_label)
    
    def _setup_button_style(self, button: QPushButton, bg_color: str):
        """设置按钮样式"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                font: 9px "Microsoft YaHei";
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 50px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(bg_color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(bg_color, 0.8)};
            }}
        """)
    
    def _darken_color(self, color: str, factor: float = 0.9) -> str:
        """让颜色变暗"""
        # 简化的颜色变暗处理
        color_map = {
            "#28a745": "#1e7e34" if factor == 0.9 else "#155724",
            "#dc3545": "#c82333" if factor == 0.9 else "#a02622",
            "#17a2b8": "#138496" if factor == 0.9 else "#0c6674"
        }
        return color_map.get(color, color)
    
    def _load_accounts(self):
        """加载账号数据"""
        try:
            accounts_file = "data/accounts.json"
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    self.accounts_data = json.load(f)
            else:
                self.accounts_data = []
            
            self._refresh_tree()
            
        except Exception as e:
            print(f"加载账号数据失败: {e}")
            self.accounts_data = []
            self._refresh_tree()
    
    def _refresh_tree(self):
        """刷新树形列表显示"""
        self.account_tree.clear()
        
        for account in self.accounts_data:
            item = QTreeWidgetItem()
            
            # 手机号
            phone = account.get('phone', 'Unknown')
            item.setText(0, phone)
            
            # 状态
            status = "在线" if account.get('token') else "离线"
            item.setText(1, status)
            
            # 主账号标记
            is_main = account.get('is_main', False)
            main_text = "是" if is_main else ""
            item.setText(2, main_text)
            
            # 存储账号数据
            item.setData(0, Qt.UserRole, account)
            
            # 设置样式
            if is_main:
                item.setFont(0, QFont("微软雅黑", 10, QFont.Bold))
                item.setForeground(0, Qt.red)
            
            self.account_tree.addTopLevelItem(item)
        
        # 更新状态
        count = len(self.accounts_data)
        self.status_label.setText(f"共 {count} 个账号")
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """账号项点击事件"""
        try:
            account = item.data(0, Qt.UserRole)
            if account:
                self.current_selected_account = account
                print(f"[账号面板] 选择账号: {account.get('phone', 'Unknown')}")
                
                if self.on_account_selected:
                    self.on_account_selected(account)
                
                # 更新状态
                phone = account.get('phone', 'Unknown')
                self.status_label.setText(f"已选择: {phone}")
        
        except Exception as e:
            print(f"账号选择失败: {e}")
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.account_tree.itemAt(position)
        if not item:
            return
        
        account = item.data(0, Qt.UserRole)
        if not account:
            return
        
        menu = QMenu(self)
        
        # 设置为主账号
        set_main_action = menu.addAction("设置为主账号")
        set_main_action.triggered.connect(lambda: self._set_as_main_account(account))
        
        # 删除账号
        delete_action = menu.addAction("删除账号")
        delete_action.triggered.connect(lambda: self._delete_account(account))
        
        # 复制手机号
        copy_phone_action = menu.addAction("复制手机号")
        copy_phone_action.triggered.connect(lambda: self._copy_phone(account))
        
        menu.exec_(self.account_tree.mapToGlobal(position))
    
    def _set_as_main_account(self, account: Dict):
        """设置为主账号"""
        try:
            if self.on_set_main:
                self.on_set_main(account)
            
            # 刷新显示
            self.refresh_account_list()
            
        except Exception as e:
            print(f"设置主账号失败: {e}")
            QMessageBox.warning(self, "设置失败", f"设置主账号失败: {str(e)}")
    
    def _delete_account(self, account: Dict):
        """删除账号"""
        try:
            phone = account.get('phone', 'Unknown')
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除账号 {phone} 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 从数据中移除
                self.accounts_data = [acc for acc in self.accounts_data 
                                    if acc.get('phone') != phone]
                
                # 保存到文件
                self._save_accounts()
                
                # 刷新显示
                self._refresh_tree()
                
                QMessageBox.information(self, "删除成功", f"账号 {phone} 已删除")
        
        except Exception as e:
            print(f"删除账号失败: {e}")
            QMessageBox.warning(self, "删除失败", f"删除账号失败: {str(e)}")
    
    def _copy_phone(self, account: Dict):
        """复制手机号到剪贴板"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            phone = account.get('phone', '')
            clipboard = QApplication.clipboard()
            clipboard.setText(phone)
            
            self.status_label.setText(f"已复制手机号: {phone}")
            
        except Exception as e:
            print(f"复制手机号失败: {e}")
    
    def _save_accounts(self):
        """保存账号数据到文件"""
        try:
            accounts_file = "data/accounts.json"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(accounts_file), exist_ok=True)
            
            # 保存数据
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            print(f"保存账号数据失败: {e}")
            raise
    
    def _on_clear_coupons(self):
        """清空券按钮点击"""
        if self.on_clear_coupons:
            self.on_clear_coupons()
        self.status_label.setText("券列表已清空")
    
    def _on_refresh_coupons(self):
        """刷新券按钮点击"""
        if self.on_refresh_coupons:
            self.on_refresh_coupons()
        self.status_label.setText("券列表已刷新")
    
    def refresh_account_list(self):
        """刷新账号列表"""
        self._load_accounts()
        self.status_label.setText("账号列表已刷新")
    
    def get_selected_account(self) -> Optional[Dict]:
        """获取当前选中的账号"""
        return self.current_selected_account
    
    def get_main_account(self) -> Optional[Dict]:
        """获取主账号"""
        for account in self.accounts_data:
            if account.get('is_main', False):
                return account
        return None 