#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号管理模块
负责账号登录、列表显示和账号切换功能
"""

import os
import json
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt

# 导入自定义组件
from ui.widgets.classic_components import (
    ClassicGroupBox, ClassicButton, ClassicLineEdit, ClassicTableWidget, ClassicLabel
)
from ui.interfaces.plugin_interface import IWidgetInterface, event_bus


class AccountWidget(QWidget):
    """账号管理组件"""
    
    # 定义信号
    account_selected = pyqtSignal(dict)  # 账号选择信号
    account_login_requested = pyqtSignal(dict)  # 账号登录请求信号
    accounts_refreshed = pyqtSignal(list)  # 账号列表刷新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self.current_account = None
        self.accounts_data = []
        
        # 实现IWidgetInterface接口
        self._widget_interface = IWidgetInterface()
        
        # 初始化界面
        self.initialize()
        
        # 连接全局事件
        self._connect_global_events()
    
    def initialize(self) -> None:
        """初始化组件"""
        self._setup_ui()
        self._connect_signals()
        
        # 自动加载账号数据
        self.refresh_accounts()
    
    def cleanup(self) -> None:
        """清理组件资源"""
        # 断开全局事件连接
        event_bus.user_login_success.disconnect(self._on_user_login_success)
        
        # 清理数据
        self.accounts_data.clear()
        self.current_account = None
    
    def get_widget(self) -> QWidget:
        """获取Qt组件"""
        return self
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 账号登录区
        self.login_group = ClassicGroupBox("影院账号登录")
        self._build_login_area()
        layout.addWidget(self.login_group)
        
        # 账号列表区
        self.account_group = ClassicGroupBox("账号列表")
        self._build_account_list()
        layout.addWidget(self.account_group)
        
        # 设置比例
        layout.setStretchFactor(self.login_group, 2)
        layout.setStretchFactor(self.account_group, 3)
    
    def _build_login_area(self):
        """构建登录区域"""
        layout = QVBoxLayout(self.login_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 手机号输入
        phone_layout = QHBoxLayout()
        phone_label = ClassicLabel("手机号:")
        phone_label.setMinimumWidth(60)
        self.phone_input = ClassicLineEdit("请输入手机号")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # OpenID输入
        openid_layout = QHBoxLayout()
        openid_label = ClassicLabel("OpenID:")
        openid_label.setMinimumWidth(60)
        self.openid_input = ClassicLineEdit("请输入OpenID")
        openid_layout.addWidget(openid_label)
        openid_layout.addWidget(self.openid_input)
        layout.addLayout(openid_layout)
        
        # Token输入
        token_layout = QHBoxLayout()
        token_label = ClassicLabel("Token:")
        token_label.setMinimumWidth(60)
        self.token_input = ClassicLineEdit("请输入Token")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)
        
        # 登录按钮
        button_layout = QHBoxLayout()
        self.login_btn = ClassicButton("登录账号", "primary")
        button_layout.addWidget(self.login_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def _build_account_list(self):
        """构建账号列表"""
        layout = QVBoxLayout(self.account_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.refresh_btn = ClassicButton("刷新", "default")
        self.refresh_btn.setMaximumWidth(50)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 账号表格
        self.account_table = ClassicTableWidget()
        self.account_table.setColumnCount(3)
        self.account_table.setHorizontalHeaderLabels(["账号", "影院", "余额"])
        
        # 设置表格属性
        header = self.account_table.horizontalHeader()
        header.resizeSection(0, 120)  # 账号列
        header.resizeSection(1, 120)  # 影院列
        # 余额列自动拉伸
        
        layout.addWidget(self.account_table)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 按钮事件
        self.login_btn.clicked.connect(self._on_login_clicked)
        self.refresh_btn.clicked.connect(self.refresh_accounts)
        
        # 表格选择事件
        self.account_table.itemSelectionChanged.connect(self._on_account_selection_changed)
        self.account_table.cellDoubleClicked.connect(self._on_account_double_clicked)
    
    def _connect_global_events(self):
        """连接全局事件"""
        # 监听用户登录成功事件
        event_bus.user_login_success.connect(self._on_user_login_success)
    
    def _on_login_clicked(self):
        """登录按钮点击处理"""
        try:
            # 获取输入数据
            phone = self.phone_input.text().strip()
            openid = self.openid_input.text().strip()
            token = self.token_input.text().strip()
            
            # 验证输入
            if not phone:
                QMessageBox.warning(self, "输入错误", "请输入手机号")
                return
            
            if not openid:
                QMessageBox.warning(self, "输入错误", "请输入OpenID")
                return
            
            if not token:
                QMessageBox.warning(self, "输入错误", "请输入Token")
                return
            
            # 构建登录数据
            login_data = {
                "phone": phone,
                "openid": openid,
                "token": token
            }
            
            # 发出登录请求信号
            self.account_login_requested.emit(login_data)
            
        except Exception as e:
            QMessageBox.critical(self, "登录错误", f"处理登录请求失败: {str(e)}")
    
    def _on_account_selection_changed(self):
        """账号选择变化处理"""
        try:
            current_row = self.account_table.currentRow()
            if current_row >= 0:
                # 获取选中账号的完整数据
                account_item = self.account_table.item(current_row, 0)
                if account_item:
                    account_data = account_item.data(Qt.UserRole)
                    if account_data:
                        self.current_account = account_data
                        
                        # 发出账号选择信号
                        self.account_selected.emit(account_data)
                        
                        # 发布全局事件
                        event_bus.account_changed.emit(account_data)
                        
                        print(f"[账号组件] 选择账号: {account_data.get('userid', 'N/A')}")
        
        except Exception as e:
            print(f"[账号组件] 选择处理错误: {e}")
    
    def _on_account_double_clicked(self, row: int, column: int):
        """账号双击处理"""
        try:
            account_item = self.account_table.item(row, 0)
            if account_item:
                account_data = account_item.data(Qt.UserRole)
                if account_data:
                    # 双击直接登录该账号
                    userid = account_data.get("userid", "")
                    QMessageBox.information(
                        self, "快速登录", 
                        f"准备快速登录账号: {userid}\n此功能待实现"
                    )
        
        except Exception as e:
            print(f"[账号组件] 双击处理错误: {e}")
    
    def _on_user_login_success(self, user_info: dict):
        """用户登录成功处理"""
        try:
            # 清空登录表单
            self.phone_input.clear()
            self.openid_input.clear()
            self.token_input.clear()
            
            # 刷新账号列表
            self.refresh_accounts()
            
            print(f"[账号组件] 用户登录成功，已刷新账号列表")
            
        except Exception as e:
            print(f"[账号组件] 登录成功处理错误: {e}")
    
    def refresh_accounts(self):
        """刷新账号列表"""
        try:
            accounts_file = "data/accounts.json"
            
            if not os.path.exists(accounts_file):
                self.account_table.setRowCount(0)
                print(f"[账号组件] 账号文件不存在: {accounts_file}")
                return
            
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            self.accounts_data = accounts
            print(f"[账号组件] 成功加载 {len(accounts)} 个账号")
            
            # 更新表格
            self._update_account_table(accounts)
            
            # 发出刷新信号
            self.accounts_refreshed.emit(accounts)
            
        except Exception as e:
            QMessageBox.warning(self, "数据加载失败", f"刷新账号列表失败: {str(e)}")
            print(f"[账号组件] 刷新错误: {e}")
    
    def _update_account_table(self, accounts: List[Dict]):
        """更新账号表格"""
        try:
            self.account_table.setRowCount(len(accounts))
            
            for i, account in enumerate(accounts):
                userid = account.get("userid", "")
                cinemaid = account.get("cinemaid", "")
                balance = account.get("balance", 0)
                
                # 根据影院ID获取影院名称
                cinema_name = self._get_cinema_name_by_id(cinemaid)
                
                # 设置表格项
                self.account_table.setItem(i, 0, self.account_table.__class__.createItem(userid))
                self.account_table.setItem(i, 1, self.account_table.__class__.createItem(cinema_name))
                self.account_table.setItem(i, 2, self.account_table.__class__.createItem(str(balance)))
                
                # 保存完整账号信息到第一列的数据中
                account_item = self.account_table.item(i, 0)
                account_item.setData(Qt.UserRole, account)
                
        except Exception as e:
            print(f"[账号组件] 更新表格错误: {e}")
    
    def _get_cinema_name_by_id(self, cinema_id: str) -> str:
        """根据影院ID获取影院名称"""
        try:
            # 尝试从全局事件总线获取影院数据
            # 这里可以通过事件总线请求影院数据
            # 暂时返回影院ID
            return f"影院ID:{cinema_id}" if cinema_id else "未设置影院"
            
        except Exception as e:
            print(f"[账号组件] 获取影院名称错误: {e}")
            return f"影院ID:{cinema_id}"
    
    def get_current_account(self) -> Optional[Dict]:
        """获取当前选中的账号"""
        return self.current_account
    
    def get_accounts_data(self) -> List[Dict]:
        """获取所有账号数据"""
        return self.accounts_data.copy()
    
    def set_cinema_name_resolver(self, resolver_func):
        """设置影院名称解析函数"""
        self._cinema_name_resolver = resolver_func
    
    def clear_selection(self):
        """清除选择"""
        self.account_table.clearSelection()
        self.current_account = None
    
    def select_account_by_id(self, userid: str) -> bool:
        """根据用户ID选择账号"""
        try:
            for i in range(self.account_table.rowCount()):
                item = self.account_table.item(i, 0)
                if item and item.text() == userid:
                    self.account_table.selectRow(i)
                    return True
            return False
        except Exception as e:
            print(f"[账号组件] 选择账号错误: {e}")
            return False


# 为了兼容性，创建一个createItem方法
def createItem(text: str):
    """创建表格项目"""
    from PyQt5.QtWidgets import QTableWidgetItem
    return QTableWidgetItem(text)

# 动态添加方法到类
ClassicTableWidget.createItem = staticmethod(createItem) 