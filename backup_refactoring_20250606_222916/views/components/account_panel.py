#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号面板组件 - 重构版本
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QGroupBox, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.signals import event_bus, event_handler


class AccountPanel(QWidget):
    """账号面板"""
    
    # 信号定义
    account_selected = pyqtSignal(dict)  # 账号选择
    account_login_requested = pyqtSignal(dict)  # 账号登录请求
    account_add_requested = pyqtSignal(dict)  # 账号添加请求
    account_remove_requested = pyqtSignal(str)  # 账号删除请求
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self.account_list = []
        self.current_account = None
        self.current_cinema = None
        
        # 初始化UI
        self._init_ui()
        
        # 连接事件总线
        self._connect_events()
        
        print("[账号面板] 初始化完成")
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 账号登录区
        login_group = QGroupBox("账号登录")
        login_layout = QVBoxLayout(login_group)
        
        # 手机号输入
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(QLabel("手机号:"))
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号")
        phone_layout.addWidget(self.phone_input)
        login_layout.addLayout(phone_layout)
        
        # OpenID输入
        openid_layout = QHBoxLayout()
        openid_layout.addWidget(QLabel("OpenID:"))
        self.openid_input = QLineEdit()
        self.openid_input.setPlaceholderText("请输入OpenID")
        openid_layout.addWidget(self.openid_input)
        login_layout.addLayout(openid_layout)
        
        # Token输入
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Token:"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("请输入Token")
        token_layout.addWidget(self.token_input)
        login_layout.addLayout(token_layout)
        
        # 登录按钮
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("登录")
        self.login_button.clicked.connect(self._on_login_clicked)
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self._on_add_clicked)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.add_button)
        login_layout.addLayout(button_layout)
        
        layout.addWidget(login_group)
        
        # 账号列表区
        list_group = QGroupBox("账号列表")
        list_layout = QVBoxLayout(list_group)
        
        # 当前影院显示
        self.cinema_label = QLabel("当前影院: 未选择")
        self.cinema_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-weight: bold;
                padding: 5px;
                background-color: #E3F2FD;
                border-radius: 3px;
            }
        """)
        list_layout.addWidget(self.cinema_label)
        
        # 账号列表
        self.account_list_widget = QListWidget()
        self.account_list_widget.itemClicked.connect(self._on_account_item_clicked)
        self.account_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
            }
        """)
        list_layout.addWidget(self.account_list_widget)
        
        # 账号操作按钮
        account_button_layout = QHBoxLayout()
        self.select_button = QPushButton("选择账号")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.select_button.setEnabled(False)
        
        self.remove_button = QPushButton("删除账号")
        self.remove_button.clicked.connect(self._on_remove_clicked)
        self.remove_button.setEnabled(False)
        
        account_button_layout.addWidget(self.select_button)
        account_button_layout.addWidget(self.remove_button)
        list_layout.addLayout(account_button_layout)
        
        layout.addWidget(list_group)
        
        # 当前账号显示
        current_group = QGroupBox("当前账号")
        current_layout = QVBoxLayout(current_group)
        
        self.current_account_label = QLabel("未选择账号")
        self.current_account_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                padding: 10px;
                background-color: #E8F5E9;
                border-radius: 3px;
                border: 1px solid #C8E6C9;
            }
        """)
        current_layout.addWidget(self.current_account_label)
        
        layout.addWidget(current_group)
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.cinema_selected.connect(self._on_cinema_selected)
        event_bus.account_list_updated.connect(self._on_account_list_updated)
        event_bus.account_selected.connect(self._on_account_selected)
        event_bus.account_login_success.connect(self._on_account_login_success)
        event_bus.account_added.connect(self._on_account_added)
        event_bus.account_removed.connect(self._on_account_removed)
    
    @event_handler("cinema_selected")
    def _on_cinema_selected(self, cinema_data: dict):
        """影院选择处理"""
        self.current_cinema = cinema_data
        cinema_name = cinema_data.get('cinemaShortName', '未知影院')
        self.cinema_label.setText(f"当前影院: {cinema_name}")
        
        print(f"[账号面板] 影院已选择: {cinema_name}")
    
    @event_handler("account_list_updated")
    def _on_account_list_updated(self, account_list: List[dict]):
        """账号列表更新处理"""
        self.account_list = account_list
        self._update_account_list_display()
        
        print(f"[账号面板] 账号列表已更新: {len(account_list)} 个账号")
    
    @event_handler("account_selected")
    def _on_account_selected(self, account_data: dict):
        """账号选择处理"""
        self.current_account = account_data
        self._update_current_account_display()
    
    @event_handler("account_login_success")
    def _on_account_login_success(self, account_data: dict):
        """账号登录成功处理"""
        QMessageBox.information(self, "登录成功", f"账号 {account_data.get('phone', 'N/A')} 登录成功")
        self._clear_input_fields()
    
    @event_handler("account_added")
    def _on_account_added(self, account_data: dict):
        """账号添加处理"""
        QMessageBox.information(self, "添加成功", f"账号 {account_data.get('phone', 'N/A')} 添加成功")
        self._clear_input_fields()
    
    @event_handler("account_removed")
    def _on_account_removed(self, phone: str):
        """账号删除处理"""
        QMessageBox.information(self, "删除成功", f"账号 {phone} 删除成功")
        
        # 如果删除的是当前账号，清空显示
        if self.current_account and self.current_account.get('phone') == phone:
            self.current_account = None
            self._update_current_account_display()
    
    def _update_account_list_display(self):
        """更新账号列表显示"""
        try:
            self.account_list_widget.clear()
            
            if not self.account_list:
                item = QListWidgetItem("暂无账号数据")
                item.setFlags(Qt.NoItemFlags)  # 不可选择
                self.account_list_widget.addItem(item)
                return
            
            for account in self.account_list:
                phone = account.get('phone', 'N/A')
                cinema_name = account.get('cinema_name', '未知影院')
                
                # 创建显示文本
                display_text = f"{phone}\n影院: {cinema_name}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, account)  # 存储账号数据
                
                # 设置字体
                font = QFont()
                font.setPointSize(9)
                item.setFont(font)
                
                self.account_list_widget.addItem(item)
            
        except Exception as e:
            print(f"[账号面板] 更新账号列表显示错误: {e}")
    
    def _update_current_account_display(self):
        """更新当前账号显示"""
        if self.current_account:
            phone = self.current_account.get('phone', 'N/A')
            cinema_name = self.current_account.get('cinema_name', '未知影院')
            self.current_account_label.setText(f"当前账号: {phone}\n影院: {cinema_name}")
        else:
            self.current_account_label.setText("未选择账号")
    
    def _on_account_item_clicked(self, item: QListWidgetItem):
        """账号列表项点击处理"""
        account_data = item.data(Qt.UserRole)
        if account_data:
            self.select_button.setEnabled(True)
            self.remove_button.setEnabled(True)
        else:
            self.select_button.setEnabled(False)
            self.remove_button.setEnabled(False)
    
    def _on_login_clicked(self):
        """登录按钮点击处理"""
        try:
            phone = self.phone_input.text().strip()
            openid = self.openid_input.text().strip()
            token = self.token_input.text().strip()
            
            if not all([phone, openid, token]):
                QMessageBox.warning(self, "输入错误", "请填写完整的账号信息")
                return
            
            # 构建账号数据
            account_data = {
                'phone': phone,
                'openid': openid,
                'token': token
            }
            
            # 如果有当前影院，添加影院信息
            if self.current_cinema:
                account_data['cinemaid'] = self.current_cinema.get('cinemaid', '')
                account_data['cinema_name'] = self.current_cinema.get('cinemaShortName', '')
            
            # 发送登录请求信号
            self.account_login_requested.emit(account_data)
            
        except Exception as e:
            print(f"[账号面板] 登录处理错误: {e}")
            QMessageBox.critical(self, "登录错误", f"登录处理失败: {str(e)}")
    
    def _on_add_clicked(self):
        """添加按钮点击处理"""
        try:
            phone = self.phone_input.text().strip()
            openid = self.openid_input.text().strip()
            token = self.token_input.text().strip()
            
            if not all([phone, openid, token]):
                QMessageBox.warning(self, "输入错误", "请填写完整的账号信息")
                return
            
            # 检查是否已存在
            for account in self.account_list:
                if account.get('phone') == phone:
                    QMessageBox.warning(self, "添加失败", "该手机号已存在")
                    return
            
            # 构建账号数据
            account_data = {
                'phone': phone,
                'openid': openid,
                'token': token
            }
            
            # 如果有当前影院，添加影院信息
            if self.current_cinema:
                account_data['cinemaid'] = self.current_cinema.get('cinemaid', '')
                account_data['cinema_name'] = self.current_cinema.get('cinemaShortName', '')
            
            # 发送添加请求信号
            self.account_add_requested.emit(account_data)
            
        except Exception as e:
            print(f"[账号面板] 添加处理错误: {e}")
            QMessageBox.critical(self, "添加错误", f"添加处理失败: {str(e)}")
    
    def _on_select_clicked(self):
        """选择按钮点击处理"""
        try:
            current_item = self.account_list_widget.currentItem()
            if not current_item:
                return
            
            account_data = current_item.data(Qt.UserRole)
            if account_data:
                # 发送账号选择信号
                self.account_selected.emit(account_data)
                
        except Exception as e:
            print(f"[账号面板] 选择处理错误: {e}")
            QMessageBox.critical(self, "选择错误", f"选择处理失败: {str(e)}")
    
    def _on_remove_clicked(self):
        """删除按钮点击处理"""
        try:
            current_item = self.account_list_widget.currentItem()
            if not current_item:
                return
            
            account_data = current_item.data(Qt.UserRole)
            if not account_data:
                return
            
            phone = account_data.get('phone', '')
            if not phone:
                return
            
            # 确认删除
            reply = QMessageBox.question(
                self, "确认删除", 
                f"确定要删除账号 {phone} 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 发送删除请求信号
                self.account_remove_requested.emit(phone)
                
        except Exception as e:
            print(f"[账号面板] 删除处理错误: {e}")
            QMessageBox.critical(self, "删除错误", f"删除处理失败: {str(e)}")
    
    def _clear_input_fields(self):
        """清空输入字段"""
        self.phone_input.clear()
        self.openid_input.clear()
        self.token_input.clear()
    
    def get_current_account(self) -> Optional[dict]:
        """获取当前账号"""
        return self.current_account
    
    def set_enabled(self, enabled: bool):
        """设置面板启用状态"""
        self.login_button.setEnabled(enabled)
        self.add_button.setEnabled(enabled)
        self.select_button.setEnabled(enabled and self.account_list_widget.currentItem() is not None)
        self.remove_button.setEnabled(enabled and self.account_list_widget.currentItem() is not None)
        self.account_list_widget.setEnabled(enabled)
