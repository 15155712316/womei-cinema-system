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
    QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMessageBox, QMenu, QAction
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
        self.current_cinema_id = None  # 🆕 当前选择的影院ID
        self.all_accounts_data = []    # 🆕 所有账号数据缓存
        
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
        """构建账号列表区域"""
        layout = QVBoxLayout(self.account_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 刷新按钮
        self.refresh_btn = ClassicButton("刷新账号", "default")
        self.refresh_btn.setMaximumWidth(100)
        layout.addWidget(self.refresh_btn)
        
        # 账号表格 - 🆕 修改为三列：账号、余额、积分
        self.account_table = ClassicTableWidget()
        self.account_table.setColumnCount(3)
        self.account_table.setHorizontalHeaderLabels(["账号", "余额", "积分"])
        
        # 🆕 移除悬停效果，设置选择行为
        self.account_table.setSelectionBehavior(self.account_table.SelectRows)
        self.account_table.setSelectionMode(self.account_table.SingleSelection)
        self.account_table.setAlternatingRowColors(False)  # 移除交替行颜色
        
        # 🆕 移除悬停样式
        self.account_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性 - 优化列宽避免滚动条
        header = self.account_table.horizontalHeader()

        # 先设置固定模式，再设置宽度
        header.setSectionResizeMode(0, header.Fixed)  # 账号列固定宽度
        header.setSectionResizeMode(1, header.Fixed)  # 余额列固定宽度
        header.setSectionResizeMode(2, header.Fixed)  # 积分列固定宽度

        # 然后设置具体宽度
        header.resizeSection(0, 110)  # 账号列 - 缩小10px
        header.resizeSection(1, 60)   # 余额列 - 缩小20px
        header.resizeSection(2, 50)   # 积分列 - 缩小30px

        # 设置表格固定宽度，避免出现滚动条
        self.account_table.setFixedWidth(240)  # 110+60+50+20(边距) = 240
        self.account_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 🆕 移除右键菜单设置，因为不再需要主账号设置选项
        # self.account_table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.account_table.customContextMenuRequested.connect(self._show_context_menu)

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
        
        # 🆕 监听影院选择事件
        event_bus.cinema_selected.connect(self._on_cinema_selected)
    
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

    def _show_context_menu(self, position):
        """显示右键菜单 - 🆕 移除主账号设置选项"""
        try:
            # 获取点击位置的项目
            item = self.account_table.itemAt(position)
            if not item:
                return

            # 获取行号
            row = item.row()
            account_item = self.account_table.item(row, 0)
            if not account_item:
                return

            # 获取账号数据
            account_data = account_item.data(Qt.UserRole)
            if not account_data:
                return

            # 🆕 暂时不显示右键菜单，因为主账号设置已移除
            # 如果将来需要添加其他右键菜单选项，可以在这里添加
            return

        except Exception as e:
            print(f"[账号组件] 显示右键菜单错误: {e}")

    def _set_as_main_account(self, account_data: dict):
        """设置为主账号 - 🆕 无确认，直接设置"""
        try:
            userid = account_data.get('userid', '')
            cinemaid = account_data.get('cinemaid', '')

            if not userid or not cinemaid:
                print(f"[账号组件] 设置主账号失败: 账号信息不完整")
                return

            # 🆕 直接执行设置，无确认对话框
            success = self._update_main_account_in_file(cinemaid, userid)

            if success:
                # 🆕 静默刷新账号列表，无提示信息
                self.refresh_accounts()
                print(f"[账号组件] 主账号设置成功: {userid} (影院: {cinemaid})")
            else:
                print(f"[账号组件] 主账号设置失败: 更新账号文件失败")

        except Exception as e:
            print(f"[账号组件] 设置主账号错误: {e}")

    def _update_main_account_in_file(self, cinemaid: str, userid: str) -> bool:
        """更新账号文件中的主账号设置"""
        try:
            accounts_file = "data/accounts.json"

            if not os.path.exists(accounts_file):
                print(f"[账号组件] 账号文件不存在: {accounts_file}")
                return False

            # 读取现有账号数据
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)

            # 更新主账号设置
            updated = False
            for account in accounts:
                if account.get('cinemaid') == cinemaid:
                    # 如果是目标账号，设置为主账号
                    if account.get('userid') == userid:
                        account['is_main'] = True
                        updated = True
                        print(f"[账号组件] 设置主账号: {userid} (影院: {cinemaid})")
                    else:
                        # 其他同影院账号取消主账号状态
                        if account.get('is_main', False):
                            account['is_main'] = False
                            print(f"[账号组件] 取消主账号: {account.get('userid')} (影院: {cinemaid})")

            if not updated:
                print(f"[账号组件] 未找到目标账号: {userid} (影院: {cinemaid})")
                return False

            # 写回文件
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)

            # 更新缓存
            self.all_accounts_data = accounts

            print(f"[账号组件] 主账号设置已保存到文件")
            return True

        except Exception as e:
            print(f"[账号组件] 更新账号文件错误: {e}")
            return False
    
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
    
    def _on_cinema_selected(self, cinema_data: dict):
        """影院选择处理 - 🆕 根据影院过滤账号"""
        try:
            # 🆕 直接处理dict类型的影院数据
            if isinstance(cinema_data, dict):
                cinema_id = cinema_data.get('cinemaid', '')
                cinema_name = cinema_data.get('cinemaShortName', '')
            else:
                print(f"[账号组件] 收到非dict类型的影院数据: {type(cinema_data)}")
                return
            
            if cinema_id:
                self.current_cinema_id = cinema_id
                self._filter_accounts_by_cinema(cinema_id)
                print(f"[账号组件] 影院切换: {cinema_name} ({cinema_id})，已过滤账号列表")
                
                # 🆕 如果过滤后有账号，优先选择主账号
                if self.accounts_data:
                    selected_account = self._find_main_account_for_cinema(cinema_id)

                    if not selected_account:
                        # 如果没有主账号，选择第一个账号
                        selected_account = self.accounts_data[0]
                        print(f"[账号组件] 影院 {cinema_name} 没有主账号，选择第一个账号")
                    else:
                        print(f"[账号组件] 影院 {cinema_name} 自动选择主账号")

                    self.current_account = selected_account

                    # 找到该账号在表格中的行号并选择
                    selected_row = self._find_account_row(selected_account.get('userid', ''))
                    if selected_row >= 0:
                        self.account_table.selectRow(selected_row)

                    # 发出账号选择信号
                    self.account_selected.emit(selected_account)
                    event_bus.account_changed.emit(selected_account)

                    print(f"[账号组件] 自动选择账号: {selected_account.get('userid', 'N/A')}")
                else:
                    print(f"[账号组件] 影院 {cinema_name} 没有关联账号")
            
        except Exception as e:
            print(f"[账号组件] 影院选择处理错误: {e}")

    def _find_main_account_for_cinema(self, cinema_id: str) -> Optional[dict]:
        """查找指定影院的主账号"""
        try:
            for account in self.accounts_data:
                if (account.get('cinemaid') == cinema_id and
                    account.get('is_main', False)):
                    return account
            return None
        except Exception as e:
            print(f"[账号组件] 查找主账号错误: {e}")
            return None

    def _find_account_row(self, userid: str) -> int:
        """查找账号在表格中的行号"""
        try:
            for row in range(self.account_table.rowCount()):
                item = self.account_table.item(row, 0)
                if item:
                    # 获取存储的账号数据来比较
                    account_data = item.data(Qt.UserRole)
                    if account_data and account_data.get('userid') == userid:
                        return row
            return -1
        except Exception as e:
            print(f"[账号组件] 查找账号行号错误: {e}")
            return -1

    def _get_cinema_id_by_name(self, cinema_name: str) -> str:
        """根据影院名称获取影院ID"""
        try:
            # 从影院管理器获取影院数据
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            for cinema in cinemas:
                if cinema.get('cinemaShortName') == cinema_name:
                    return cinema.get('cinemaid', '')
            
            return ''
            
        except Exception as e:
            print(f"[账号组件] 获取影院ID错误: {e}")
            return ''
    
    def _filter_accounts_by_cinema(self, cinema_id: str):
        """根据影院ID过滤账号列表"""
        try:
            if not self.all_accounts_data:
                return
            
            # 过滤出属于指定影院的账号
            filtered_accounts = [
                account for account in self.all_accounts_data 
                if account.get('cinemaid') == cinema_id
            ]
            
            # 更新显示的账号数据
            self.accounts_data = filtered_accounts
            self._update_account_table(filtered_accounts)
            
            print(f"[账号组件] 影院 {cinema_id} 关联账号: {len(filtered_accounts)} 个")
            
        except Exception as e:
            print(f"[账号组件] 过滤账号错误: {e}")
    
    def _set_default_cinema(self):
        """设置默认影院 - 🆕 程序启动时自动选择第一个影院"""
        try:
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            if cinemas:
                first_cinema = cinemas[0]
                cinema_id = first_cinema.get('cinemaid', '')
                
                if cinema_id:
                    self.current_cinema_id = cinema_id
                    self._filter_accounts_by_cinema(cinema_id)
                    print(f"[账号组件] 默认选择影院: {first_cinema.get('cinemaShortName', 'N/A')} ({cinema_id})")
                    
        except Exception as e:
            print(f"[账号组件] 设置默认影院错误: {e}")
    
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
            
            # 🆕 保存所有账号数据到缓存
            self.all_accounts_data = accounts
            print(f"[账号组件] 成功加载 {len(accounts)} 个账号")
            
            # 🆕 如果没有设置当前影院，则设置默认影院
            if not self.current_cinema_id:
                self._set_default_cinema()
            else:
                # 根据当前影院过滤账号
                self._filter_accounts_by_cinema(self.current_cinema_id)
            
            # 发出刷新信号
            self.accounts_refreshed.emit(self.accounts_data)
            
        except Exception as e:
            QMessageBox.warning(self, "数据加载失败", f"刷新账号列表失败: {str(e)}")
            print(f"[账号组件] 刷新错误: {e}")
    
    def _update_account_table(self, accounts: List[Dict]):
        """更新账号表格"""
        try:
            self.account_table.setRowCount(len(accounts))
            
            for i, account in enumerate(accounts):
                userid = account.get("userid", "")
                balance = account.get("balance", 0)
                points = account.get("points", account.get("score", 0))  # 兼容points和score字段

                # 🆕 不改变样式，保持原有显示
                display_userid = userid

                # 🆕 只设置三列：账号、余额、积分
                self.account_table.setItem(i, 0, self.account_table.__class__.createItem(display_userid))
                self.account_table.setItem(i, 1, self.account_table.__class__.createItem(str(balance)))
                self.account_table.setItem(i, 2, self.account_table.__class__.createItem(str(points)))

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
        """获取账号数据"""
        return self.accounts_data
    
    def update_account_list(self, accounts: List[Dict]):
        """更新账号列表"""
        try:
            self.accounts_data = accounts
            self._update_account_table(accounts)
            print(f"[账号组件] 更新账号列表完成，共{len(accounts)}个账号")
        except Exception as e:
            print(f"[账号组件] 更新账号列表错误: {e}")
    
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