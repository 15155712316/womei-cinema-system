#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 经典风格主窗口
基于原版界面设计，保持简洁实用的风格
"""

import sys
import os
from typing import Dict, List, Optional, Any
import json
import time

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QTabWidget,
    QGroupBox, QFrame, QTreeWidget, QTreeWidgetItem, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QScrollArea, QSpacerItem, QSizePolicy, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor

# 导入业务服务模块
from services.auth_service import AuthService
from services.cinema_manager import CinemaManager
# from services.film_service import FilmService  # 临时注释掉，因为没有FilmService类
from services.order_api import (
    create_order, get_unpaid_order_detail, get_coupons_by_order, 
    bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api, 
    cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
)
# from services.account_api import AccountAPI  # 临时注释掉
from services.ui_utils import MessageManager, CouponManager, UIConstants

# 导入登录窗口
from ui.login_window import LoginWindow

# 临时服务类定义
class TempFilmService:
    """临时电影服务类"""
    def get_movies_by_cinema(self, cinema_id: str):
        return [
            {"title": "阿凡达：水之道"},
            {"title": "流浪地球2"},
            {"title": "满江红"}
        ]
    
    def get_dates_by_movie(self, cinema_id: str, movie_title: str):
        return ["2024-12-27", "2024-12-28", "2024-12-29"]
    
    def get_sessions_by_date(self, cinema_id: str, movie_title: str, date: str):
        return [
            {"time": "10:30"},
            {"time": "14:20"},
            {"time": "18:45"},
            {"time": "21:30"}
        ]

class TempAccountAPI:
    """临时账号API类"""
    pass

class ClassicGroupBox(QGroupBox):
    """经典风格分组框"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置经典分组框样式"""
        self.setStyleSheet("""
            QGroupBox {
                font: bold 12px "Microsoft YaHei";
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #333333;
                background-color: #f9f9f9;
            }
        """)

class ClassicButton(QPushButton):
    """经典风格按钮"""
    def __init__(self, text="", button_type="default", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
    
    def _setup_style(self):
        """设置按钮样式"""
        if self.button_type == "primary":
            style = """
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #0078d4;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                    border-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                    border-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    border-color: #cccccc;
                    color: #888888;
                }
            """
        elif self.button_type == "success":
            style = """
                QPushButton {
                    background-color: #107c10;
                    color: white;
                    border: 1px solid #107c10;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #0e6e0e;
                    border-color: #0e6e0e;
                }
                QPushButton:pressed {
                    background-color: #0c5c0c;
                    border-color: #0c5c0c;
                }
            """
        elif self.button_type == "warning":
            style = """
                QPushButton {
                    background-color: #ff8c00;
                    color: white;
                    border: 1px solid #ff8c00;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #e67c00;
                    border-color: #e67c00;
                }
                QPushButton:pressed {
                    background-color: #cc6c00;
                    border-color: #cc6c00;
                }
            """
        else:  # default
            style = """
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #999999;
                }
                QPushButton:pressed {
                    background-color: #e6e6e6;
                    border-color: #888888;
                }
            """
        
        self.setStyleSheet(style)

class ClassicLineEdit(QLineEdit):
    """经典风格输入框"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_style()
    
    def _setup_style(self):
        """设置输入框样式"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 3px;
                padding: 6px 8px;
                font: 11px "Microsoft YaHei";
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QLineEdit:hover {
                border-color: #999999;
            }
        """)

class ClassicComboBox(QComboBox):
    """经典风格下拉框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置下拉框样式"""
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid #cccccc;
                border-radius: 3px;
                padding: 6px 8px;
                font: 12px "Microsoft YaHei";
                background-color: #ffffff;
                color: #333333;
                min-width: 140px;
            }
            QComboBox:focus {
                border-color: #0078d4;
            }
            QComboBox:hover {
                border-color: #999999;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666666;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                selection-background-color: #0078d4;
                selection-color: white;
                font: 12px "Microsoft YaHei";
            }
        """)

class ClassicTableWidget(QTableWidget):
    """经典风格表格"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置表格样式"""
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                font: 11px "Microsoft YaHei";
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #e6f3ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 6px;
                font: bold 11px "Microsoft YaHei";
                color: #333333;
            }
        """)

class ClassicTabWidget(QTabWidget):
    """经典风格Tab页"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置Tab样式"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                font: 11px "Microsoft YaHei";
                min-width: 60px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #e6e6e6;
            }
        """)

class CinemaOrderSimulatorClassicWindow(QMainWindow):
    """柴犬影院下单系统经典风格主窗口"""
    
    # 定义信号
    login_success = pyqtSignal(dict)  # 登录成功信号
    account_changed = pyqtSignal(dict)  # 账号切换信号
    
    def __init__(self):
        super().__init__()
        
        # 初始化业务服务
        self.auth_service = AuthService()
        self.cinema_manager = CinemaManager()
        self.film_service = TempFilmService()
        self.account_api = TempAccountAPI()
        self.message_manager = MessageManager()
        self.coupon_manager = CouponManager()
        
        # 初始化状态变量
        self.current_user = None
        self.current_account = None
        self.current_cinema_id = None
        self.current_order = None
        self.selected_coupons = []
        self.coupons_data = []
        self.max_coupon_select = 1
        
        # 计时器
        self.auth_check_timer = QTimer()
        self.countdown_timer = QTimer()
        
        # 设置窗口基本属性 - 放大到1500x900
        self.setWindowTitle("柴犬影院下单系统 - PyQt5完整版")
        self.setFixedSize(1500, 900)
        
        # 设置经典主题
        self._setup_classic_theme()
        
        # 初始化界面
        self._init_ui()
        
        # 连接信号槽
        self._connect_signals()
        
        # 启动用户认证检查
        self._start_auth_check()
    
    def _setup_classic_theme(self):
        """设置经典主题"""
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 计算各栏宽度 - 保持原有区域分布比例
        total_width = 1500
        total_height = 900
        left_w = int(total_width * 0.2)    # 300px (20%)
        center_w = int(total_width * 0.6)  # 900px (60%)
        right_w = total_width - left_w - center_w  # 300px (20%)
        
        # 创建三栏布局
        self._create_left_panel_classic(5, 5, left_w-10, total_height-10)
        self._create_center_panel_classic(left_w+5, 5, center_w-10, total_height-10)
        self._create_right_panel_classic(left_w+center_w+5, 5, right_w-10, total_height-10)
    
    def _create_left_panel_classic(self, x: int, y: int, width: int, height: int):
        """创建经典风格左栏面板"""
        # 主容器
        left_container = QWidget(self.centralWidget())
        left_container.setGeometry(x, y, width, height)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)
        
        # 账号登录区
        login_group = ClassicGroupBox("影院账号登录")
        self._build_login_area_classic(login_group)
        left_layout.addWidget(login_group)
        
        # 账号列表区
        account_group = ClassicGroupBox("账号列表")
        self._build_account_list_classic(account_group)
        left_layout.addWidget(account_group)
        
        # 设置比例
        left_layout.setStretchFactor(login_group, 2)
        left_layout.setStretchFactor(account_group, 3)
    
    def _build_login_area_classic(self, parent_group):
        """构建经典风格登录区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 手机号输入
        phone_layout = QHBoxLayout()
        phone_label = QLabel("手机号:")
        phone_label.setMinimumWidth(60)
        self.phone_input = ClassicLineEdit("请输入手机号")
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)
        
        # OpenID输入
        openid_layout = QHBoxLayout()
        openid_label = QLabel("OpenID:")
        openid_label.setMinimumWidth(60)
        self.openid_input = ClassicLineEdit("请输入OpenID")
        openid_layout.addWidget(openid_label)
        openid_layout.addWidget(self.openid_input)
        layout.addLayout(openid_layout)
        
        # Token输入
        token_layout = QHBoxLayout()
        token_label = QLabel("Token:")
        token_label.setMinimumWidth(60)
        self.token_input = ClassicLineEdit("请输入Token")
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        layout.addLayout(token_layout)
        
        # 登录按钮 - 删除清空按钮
        button_layout = QHBoxLayout()
        self.login_btn = ClassicButton("登录账号", "primary")
        button_layout.addWidget(self.login_btn)
        button_layout.addStretch()  # 填充剩余空间
        layout.addLayout(button_layout)
        
        layout.addStretch()
    
    def _build_account_list_classic(self, parent_group):
        """构建经典风格账号列表"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 操作按钮区 - 只保留刷新按钮
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
        self.account_table.setAlternatingRowColors(True)
        self.account_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.account_table.horizontalHeader().setStretchLastSection(True)
        self.account_table.verticalHeader().setVisible(False)  # 隐藏行号
        
        # 不再添加示例数据，等待从JSON文件加载
        self.account_table.setRowCount(0)
        
        layout.addWidget(self.account_table)
    
    def _create_center_panel_classic(self, x: int, y: int, width: int, height: int):
        """创建经典风格中栏面板"""
        # 主容器
        center_container = QWidget(self.centralWidget())
        center_container.setGeometry(x, y, width, height)
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(5, 5, 5, 5)
        center_layout.setSpacing(10)
        
        # Tab区域
        self.tab_widget = ClassicTabWidget()
        self._create_tab_pages_classic()
        center_layout.addWidget(self.tab_widget, 2)
        
        # 座位区域
        seat_group = ClassicGroupBox("座位选择")
        self._create_seat_area_classic(seat_group)
        center_layout.addWidget(seat_group, 3)
    
    def _create_tab_pages_classic(self):
        """创建经典风格Tab页面"""
        # Tab1: 出票
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.setSpacing(10)
        
        # 左侧：影院选择 - 调整为55%宽度
        cinema_group = ClassicGroupBox("影院选择")
        self._build_cinema_select_classic(cinema_group)
        tab1_layout.addWidget(cinema_group, 55)  # 占55/100
        
        # 右侧：可用券列表 - 调整为45%宽度
        coupon_group = ClassicGroupBox("可用券列表")
        self._build_coupon_list_classic(coupon_group)
        tab1_layout.addWidget(coupon_group, 45)  # 占45/100
        
        self.tab_widget.addTab(tab1, "出票")
        
        # 其他Tab页面
        for name in ["绑券", "兑换券", "订单", "影院"]:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            placeholder = QLabel(f"{name}功能区域")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font: 14px "Microsoft YaHei";
                    background-color: #ffffff;
                    border: 1px dashed #cccccc;
                    padding: 40px;
                }
            """)
            tab_layout.addWidget(placeholder)
            
            self.tab_widget.addTab(tab, name)
    
    def _build_cinema_select_classic(self, parent_group):
        """构建经典风格影院选择"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号显示
        self.current_account_label = QLabel("当前账号: 14700283316 (余额:30)")
        self.current_account_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font: bold 11px "Microsoft YaHei";
                padding: 8px;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.current_account_label)
        
        # 影院选择
        cinema_layout = QHBoxLayout()
        cinema_label = QLabel("影院:")
        cinema_label.setMinimumWidth(40)
        cinema_label.setMaximumWidth(40)
        self.cinema_combo = ClassicComboBox()
        # 不再硬编码影院列表，等待从JSON文件加载
        self.cinema_combo.addItem("加载中...")
        cinema_layout.addWidget(cinema_label)
        cinema_layout.addWidget(self.cinema_combo)
        layout.addLayout(cinema_layout)
        
        # 影片选择
        movie_layout = QHBoxLayout()
        movie_label = QLabel("影片:")
        movie_label.setMinimumWidth(40)
        movie_label.setMaximumWidth(40)
        self.movie_combo = ClassicComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        movie_layout.addWidget(movie_label)
        movie_layout.addWidget(self.movie_combo)
        layout.addLayout(movie_layout)
        
        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("日期:")
        date_label.setMinimumWidth(40)
        date_label.setMaximumWidth(40)
        self.date_combo = ClassicComboBox()
        self.date_combo.addItems(["请先选择影片"])
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_combo)
        layout.addLayout(date_layout)
        
        # 场次选择
        session_layout = QHBoxLayout()
        session_label = QLabel("场次:")
        session_label.setMinimumWidth(40)
        session_label.setMaximumWidth(40)
        self.session_combo = ClassicComboBox()
        self.session_combo.addItems(["请先选择日期"])
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_combo)
        layout.addLayout(session_layout)
        
        layout.addStretch()
    
    def _build_coupon_list_classic(self, parent_group):
        """构建经典风格券列表"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 券列表
        self.coupon_list = QListWidget()
        self.coupon_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font: 11px "Microsoft YaHei";
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f3ff;
            }
        """)
        
        # 添加示例券数据
        self.coupon_list.addItem("10元代金券 (有效期至2024-12-31)")
        self.coupon_list.addItem("5折优惠券 (限周末使用)")
        self.coupon_list.addItem("买一送一券 (限工作日)")
        
        layout.addWidget(self.coupon_list)
    
    def _create_seat_area_classic(self, parent_group):
        """创建经典风格座位区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)
        
        # 座位选择信息
        seat_info_layout = QHBoxLayout()
        seat_info_layout.addWidget(QLabel("加载座位图"))
        
        self.seat_input = ClassicLineEdit()
        self.seat_input.setPlaceholderText("座位选择")
        seat_info_layout.addWidget(self.seat_input)
        
        layout.addLayout(seat_info_layout)
        
        # 座位图区域（占位）
        self.seat_placeholder = QLabel("座位图将在此显示\n\n请先选择影院、影片、日期和场次")
        self.seat_placeholder.setAlignment(Qt.AlignCenter)
        self.seat_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 60px;
            }
        """)
        layout.addWidget(self.seat_placeholder)
        
        # 提交订单按钮
        self.submit_btn = ClassicButton("提交订单", "success")
        self.submit_btn.setMinimumHeight(35)
        layout.addWidget(self.submit_btn)
    
    def _create_right_panel_classic(self, x: int, y: int, width: int, height: int):
        """创建经典风格右栏面板"""
        # 主容器
        right_container = QWidget(self.centralWidget())
        right_container.setGeometry(x, y, width, height)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)
        
        # 取票码区
        qrcode_group = ClassicGroupBox("取票码")
        self._build_qrcode_area_classic(qrcode_group)
        right_layout.addWidget(qrcode_group)
        
        # 订单详情区
        order_group = ClassicGroupBox("订单详情")
        self._build_order_detail_classic(order_group)
        right_layout.addWidget(order_group)
        
        # 设置比例
        right_layout.setStretchFactor(qrcode_group, 2)
        right_layout.setStretchFactor(order_group, 3)
    
    def _build_qrcode_area_classic(self, parent_group):
        """构建经典风格取票码区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        
        qrcode_placeholder = QLabel("取票码/二维码\n将在此显示")
        qrcode_placeholder.setAlignment(Qt.AlignCenter)
        qrcode_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 12px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 40px;
            }
        """)
        layout.addWidget(qrcode_placeholder)
    
    def _build_order_detail_classic(self, parent_group):
        """构建经典风格订单详情"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 用户信息
        self.user_info = QLabel("(二维码/取票码显示区)")
        self.user_info.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font: bold 11px "Microsoft YaHei";
                padding: 8px;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.user_info)
        
        # 订单详情文本
        self.order_detail = QTextEdit()
        self.order_detail.setReadOnly(True)
        self.order_detail.setPlaceholderText("订单详情将在此显示...")
        self.order_detail.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font: 10px "Microsoft YaHei";
                padding: 8px;
            }
        """)
        layout.addWidget(self.order_detail)
        
        # 一键支付按钮
        self.pay_btn = ClassicButton("一键支付", "warning")
        self.pay_btn.setMinimumHeight(35)
        layout.addWidget(self.pay_btn)

    def _start_auth_check(self):
        """启动用户认证检查"""
        try:
            # 隐藏主窗口，等待登录
            self.hide()
            
            # 创建登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            
            # 显示登录窗口
            self.login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "启动错误", f"启动认证检查失败: {str(e)}")
    
    @pyqtSlot(dict)
    def _on_user_login_success(self, user_info):
        """用户登录成功处理 - 加强验证"""
        try:
            # 1. 验证用户信息完整性
            phone = user_info.get("phone", "")
            if not phone:
                QMessageBox.critical(self, "登录失败", "用户信息不完整：缺少手机号")
                self._restart_login()
                return
            
            print(f"[主窗口验证] 开始验证用户: {phone}")
            print(f"[主窗口验证] 登录窗口传入的用户信息: {user_info}")
            
            # 2. 网络API验证（调用真实API验证账号状态）
            if not self._verify_user_with_api(user_info):
                QMessageBox.critical(self, "登录失败", "网络API验证失败，请检查网络连接或联系管理员")
                self._restart_login()
                return
            
            # 3. API验证成功后再检查机器码匹配
            current_machine_code = self.auth_service.get_machine_code()
            # 兼容不同的机器码字段名
            login_machine_code = user_info.get("machine_code") or user_info.get("machineCode", "")
            
            print(f"[主窗口验证] 当前机器码: {current_machine_code}")
            print(f"[主窗口验证] 登录机器码: {login_machine_code}")
            
            # 如果API验证成功，说明机器码是匹配的，这里只做记录不做拦截
            if current_machine_code != login_machine_code:
                print(f"[主窗口验证] 警告：机器码不匹配，但API验证已通过")
                # 更新用户信息中的机器码为当前机器码（统一使用machine_code字段）
                user_info["machine_code"] = current_machine_code
                if "machineCode" in user_info:
                    user_info["machineCode"] = current_machine_code
            else:
                print(f"[主窗口验证] 机器码匹配成功")
            
            # 4. 所有验证通过，保存用户信息
            self.current_user = user_info
            
            # 5. 关闭登录窗口
            if hasattr(self, 'login_window'):
                self.login_window.close()
            
            # 6. 显示主窗口
            self.show()
            
            # 7. 加载用户数据
            self._load_user_data()
            
            # 8. 发出登录成功信号
            self.login_success.emit(user_info)
            
            self.message_manager.show_info(f"登录验证成功，欢迎使用柴犬影院系统，{user_info.get('username', phone)}")
            
        except Exception as e:
            QMessageBox.critical(self, "登录处理错误", f"处理登录结果失败: {str(e)}")
            self._restart_login()
    
    def _verify_user_with_api(self, user_info: dict) -> bool:
        """通过网络API验证用户信息"""
        try:
            phone = user_info.get("phone", "")
            machine_code = user_info.get("machine_code", "")
            
            print(f"[API验证] 开始验证用户: {phone}, 机器码: {machine_code}")
            
            # 调用认证服务进行网络验证
            success, message, validated_user = self.auth_service.login(phone)
            
            print(f"[API验证] 验证结果: success={success}, message={message}")
            if validated_user:
                print(f"[API验证] 用户数据: {validated_user}")
            
            if success and validated_user:
                # API验证成功，更新用户信息
                user_info.update(validated_user)
                print(f"[API验证] 验证成功，用户状态: {validated_user.get('status')}")
                return True
            else:
                print(f"[API验证] 验证失败: {message}")
                return False
                
        except Exception as e:
            print(f"[API验证] 验证异常: {e}")
            return False
    
    def _restart_login(self):
        """重新启动登录流程"""
        try:
            self.hide()
            if hasattr(self, 'login_window'):
                self.login_window.close()
            
            # 重新创建登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            self.login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "重启登录失败", f"无法重新启动登录: {str(e)}")
            QApplication.quit()
    
    def _load_user_data(self):
        """加载用户相关数据"""
        try:
            # 刷新账号列表（从本地JSON文件）
            self._refresh_account_list()
            
            # 刷新影院列表（从本地JSON文件）
            self._refresh_cinema_list()
            
        except Exception as e:
            self.message_manager.show_error(f"加载用户数据失败: {str(e)}")
    
    def _refresh_account_list(self):
        """从本地JSON文件刷新账号列表"""
        try:
            accounts_file = "data/accounts.json"
            if not os.path.exists(accounts_file):
                # 清空表格
                self.account_table.setRowCount(0)
                print(f"[账号加载] 账号文件不存在: {accounts_file}")
                return
            
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            print(f"[账号加载] 成功加载 {len(accounts)} 个账号")
            
            # 更新表格
            self.account_table.setRowCount(len(accounts))
            for i, account in enumerate(accounts):
                userid = account.get("userid", "")
                cinemaid = account.get("cinemaid", "")
                balance = account.get("balance", 0)
                
                # 根据cinemaid获取影院名称
                cinema_name = self._get_cinema_name_by_id(cinemaid)
                
                self.account_table.setItem(i, 0, QTableWidgetItem(userid))
                self.account_table.setItem(i, 1, QTableWidgetItem(cinema_name))
                self.account_table.setItem(i, 2, QTableWidgetItem(str(balance)))
                
                # 保存完整账号信息到表格项的数据中
                self.account_table.item(i, 0).setData(Qt.UserRole, account)
                
        except Exception as e:
            self.message_manager.show_error(f"刷新账号列表失败: {str(e)}")
            print(f"[账号加载] 错误: {e}")
    
    def _refresh_cinema_list(self):
        """从影院管理器加载影院下拉列表（移除备用文件支持）"""
        try:
            # 只从影院管理器加载影院列表
            cinemas = self.cinema_manager.load_cinema_list()
            
            if cinemas:
                print(f"[影院加载] 从影院管理器加载 {len(cinemas)} 个影院")
                cinema_names = [cinema.get("cinemaShortName", cinema.get("name", "未知影院")) for cinema in cinemas]
            else:
                print(f"[影院加载] 影院管理器返回空数据")
                cinema_names = ["暂无影院数据"]
            
            # 更新下拉框
            self.cinema_combo.clear()
            self.cinema_combo.addItems(cinema_names)
            
            # 保存影院数据供后续使用
            self.cinemas_data = cinemas
            
        except Exception as e:
            self.message_manager.show_error(f"刷新影院列表失败: {str(e)}")
            print(f"[影院加载] 错误: {e}")
            # 发生错误时显示错误信息
            self.cinema_combo.clear()
            self.cinema_combo.addItem("加载影院失败")
    
    def _get_cinema_name_by_id(self, cinema_id: str) -> str:
        """根据影院ID获取影院名称（移除备用文件支持）"""
        try:
            # 如果已经加载了影院数据，从中查找
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                for cinema in self.cinemas_data:
                    if cinema.get("cinemaid") == cinema_id:
                        return cinema.get("cinemaShortName", cinema.get("name", "未知影院"))
            
            # 如果没有加载，尝试从影院管理器重新加载
            cinemas = self.cinema_manager.load_cinema_list()
            for cinema in cinemas:
                if cinema.get("cinemaid") == cinema_id:
                    return cinema.get("cinemaShortName", cinema.get("name", "未知影院"))
            
            # 如果都找不到，返回ID本身
            return f"影院ID:{cinema_id}"
            
        except Exception as e:
            print(f"[影院查找] 错误: {e}")
            return f"影院ID:{cinema_id}"
    
    def _get_cinema_id_by_name(self, cinema_name: str) -> Optional[str]:
        """根据影院名称获取影院ID（移除备用文件支持）"""
        try:
            # 从已加载的影院数据中查找
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                for cinema in self.cinemas_data:
                    if cinema.get("cinemaShortName") == cinema_name:
                        return cinema.get("cinemaid")
            
            # 如果没有找到，从影院管理器重新加载
            cinemas = self.cinema_manager.load_cinema_list()
            for cinema in cinemas:
                if cinema.get("cinemaShortName") == cinema_name:
                    return cinema.get("cinemaid")
            
            # 如果都找不到，返回None
            print(f"[影院查找] 未找到影院: {cinema_name}")
            return None
            
        except Exception as e:
            print(f"[影院查找] 错误: {e}")
            return None

    def _connect_signals(self):
        """连接信号槽"""
        # 登录按钮
        self.login_btn.clicked.connect(self._on_cinema_account_login)
        
        # 刷新按钮
        self.refresh_btn.clicked.connect(self._on_refresh_account_list)
        
        # 账号表格选择
        self.account_table.itemSelectionChanged.connect(self._on_account_selection_changed)
        
        # 下拉框变化
        self.cinema_combo.currentTextChanged.connect(self._on_cinema_changed)
        self.movie_combo.currentTextChanged.connect(self._on_movie_changed)
        self.date_combo.currentTextChanged.connect(self._on_date_changed)
        self.session_combo.currentTextChanged.connect(self._on_session_changed)
        
        # 提交订单按钮
        self.submit_btn.clicked.connect(self._on_submit_order)
        
        # 一键支付按钮
        self.pay_btn.clicked.connect(self._on_one_click_pay)
        
        # 账号切换信号
        self.account_changed.connect(self._on_account_changed)
    
    # ===== 事件处理方法 =====
    
    def _on_cinema_account_login(self):
        """影院账号登录处理"""
        try:
            phone = self.phone_input.text().strip()
            openid = self.openid_input.text().strip()
            token = self.token_input.text().strip()
            
            if not phone:
                self.message_manager.show_warning("请输入手机号")
                return
            
            if not openid:
                self.message_manager.show_warning("请输入OpenID")
                return
                
            if not token:
                self.message_manager.show_warning("请输入Token")
                return
            
            # 获取当前选择的影院ID
            current_cinema = self.cinema_combo.currentText()
            if not current_cinema or current_cinema == "请先选择影院":
                self.message_manager.show_warning("请先选择影院")
                return
            
            # 获取影院ID
            cinema_id = self._get_cinema_id_by_name(current_cinema)
            if not cinema_id:
                self.message_manager.show_warning("获取影院ID失败")
                return
            
            # 调用登录API
            self._cinema_account_login_api(phone, openid, token, cinema_id)
            
        except Exception as e:
            self.message_manager.show_error(f"登录处理失败: {str(e)}")
    
    def _cinema_account_login_api(self, phone: str, openid: str, token: str, cinema_id: str):
        """影院账号登录API调用"""
        try:
            # 这里调用账号API进行登录验证
            # 临时实现：创建账号数据并保存
            account_data = {
                "phone": phone,
                "openid": openid,
                "token": token,
                "cinema_id": cinema_id,
                "cinema_name": self.cinema_combo.currentText(),
                "balance": "0",  # 初始余额
                "login_time": time.time()
            }
            
            # 保存账号到本地
            self._save_cinema_account(account_data)
            
            # 刷新账号列表
            self._refresh_account_list()
            
            # 清空输入框
            self.phone_input.clear()
            self.openid_input.clear()
            self.token_input.clear()
            
            self.message_manager.show_success("账号登录成功")
            
        except Exception as e:
            self.message_manager.show_error(f"登录API调用失败: {str(e)}")
    
    def _save_cinema_account(self, account_data: dict):
        """保存影院账号到本地文件 - 使用真实数据格式"""
        try:
            accounts_file = "data/accounts.json"
            accounts = []
            
            # 确保data目录存在
            os.makedirs("data", exist_ok=True)
            
            # 读取现有账号
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
            
            # 构建标准格式的账号数据
            new_account = {
                "userid": account_data.get("phone", ""),
                "openid": account_data.get("openid", ""),
                "token": account_data.get("token", ""),
                "cinemaid": account_data.get("cinema_id", ""),
                "balance": 0,  # 初始余额
                "points": 0,   # 初始积分
                "is_main": False,  # 默认不是主账号
                "cardno": "",  # 会员卡号
                "score": 0     # 评分
            }
            
            # 检查是否已存在相同账号
            account_exists = False
            for i, acc in enumerate(accounts):
                if (acc.get("userid") == new_account["userid"] and 
                    acc.get("cinemaid") == new_account["cinemaid"]):
                    # 更新现有账号
                    accounts[i].update(new_account)
                    account_exists = True
                    break
            
            if not account_exists:
                # 添加新账号
                accounts.append(new_account)
            
            # 保存到文件
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            
            print(f"[账号保存] 成功保存账号: {new_account['userid']} - {new_account['cinemaid']}")
                
        except Exception as e:
            self.message_manager.show_error(f"保存账号失败: {str(e)}")
            print(f"[账号保存] 错误: {e}")
    
    def _on_refresh_account_list(self):
        """刷新账号列表"""
        try:
            self._refresh_account_list()
            self.message_manager.show_success("账号列表刷新成功")
        except Exception as e:
            self.message_manager.show_error(f"刷新失败: {str(e)}")
    
    def _on_account_selection_changed(self):
        """账号选择变化处理"""
        try:
            current_row = self.account_table.currentRow()
            if current_row >= 0:
                # 从表格项的UserRole数据中获取完整账号信息
                account_data_item = self.account_table.item(current_row, 0)
                if account_data_item:
                    complete_account = account_data_item.data(Qt.UserRole)
                    if complete_account:
                        # 使用完整的账号数据
                        self._set_current_account(complete_account)
                        return
                
                # 如果没有完整数据，回退到表格显示的基本信息
                userid = self.account_table.item(current_row, 0).text()
                cinema_name = self.account_table.item(current_row, 1).text()
                balance = self.account_table.item(current_row, 2).text()
                
                # 创建基本账号信息
                account_info = {
                    "userid": userid,
                    "phone": userid,  # 兼容性
                    "cinema_name": cinema_name,
                    "balance": balance
                }
                
                # 设置当前账号
                self._set_current_account(account_info)
                
        except Exception as e:
            self.message_manager.show_error(f"账号选择处理失败: {str(e)}")
    
    def _set_current_account(self, account_info: dict):
        """设置当前账号"""
        try:
            self.current_account = account_info
            
            # 更新当前账号显示
            userid = account_info.get("userid", account_info.get("phone", ""))
            balance = account_info.get("balance", "0")
            current_account_text = f"当前账号: {userid} (余额:{balance})"
            
            # 更新界面显示
            if hasattr(self, 'current_account_label'):
                self.current_account_label.setText(current_account_text)
            
            # 根据账号的cinemaid设置影院选择
            cinemaid = account_info.get("cinemaid", "")
            if cinemaid:
                cinema_name = self._get_cinema_name_by_id(cinemaid)
                # 在下拉框中查找并选择对应影院
                for i in range(self.cinema_combo.count()):
                    if self.cinema_combo.itemText(i) == cinema_name:
                        self.cinema_combo.setCurrentIndex(i)
                        break
            
            # 发出账号切换信号
            self.account_changed.emit(account_info)
            
            print(f"[账号切换] 已切换到账号: {userid}, 影院: {account_info.get('cinema_name', '')}")
            
        except Exception as e:
            self.message_manager.show_error(f"设置当前账号失败: {str(e)}")
    
    @pyqtSlot(dict)
    def _on_account_changed(self, account_info: dict):
        """账号切换信号处理"""
        try:
            # 清空下拉框选择
            self.movie_combo.clear()
            self.movie_combo.addItem("请先选择影院")
            
            self.date_combo.clear() 
            self.date_combo.addItem("请先选择影片")
            
            self.session_combo.clear()
            self.session_combo.addItem("请先选择日期")
            
            # 清空券列表
            self.coupon_list.clear()
            self.coupons_data = []
            self.selected_coupons = []
            
        except Exception as e:
            self.message_manager.show_error(f"账号切换处理失败: {str(e)}")
    
    def _on_cinema_changed(self, cinema_text: str):
        """影院选择变化处理"""
        try:
            if not cinema_text or cinema_text in ["请先选择影院", ""]:
                return
            
            # 清空后续选择
            self.movie_combo.clear()
            self.movie_combo.addItem("正在加载影片...")
            
            # 获取影院ID
            cinema_id = self._get_cinema_id_by_name(cinema_text)
            if cinema_id:
                self.current_cinema_id = cinema_id
                # 加载影片列表
                self._load_movies(cinema_id)
            
        except Exception as e:
            self.message_manager.show_error(f"影院选择处理失败: {str(e)}")
    
    def _load_movies(self, cinema_id: str):
        """加载影片列表"""
        try:
            # 调用电影服务获取影片列表
            movies = self.film_service.get_movies_by_cinema(cinema_id)
            
            # 更新下拉框
            self.movie_combo.clear()
            if movies:
                for movie in movies:
                    self.movie_combo.addItem(movie.get("title", ""))
            else:
                self.movie_combo.addItem("暂无影片")
                
        except Exception as e:
            self.movie_combo.clear()
            self.movie_combo.addItem("加载失败")
            self.message_manager.show_error(f"加载影片失败: {str(e)}")
    
    def _on_movie_changed(self, movie_text: str):
        """影片选择变化处理"""
        try:
            if not movie_text or movie_text in ["请先选择影片", "正在加载影片...", "暂无影片", "加载失败", ""]:
                return
            
            # 清空后续选择
            self.date_combo.clear()
            self.date_combo.addItem("正在加载日期...")
            
            # 加载日期列表
            self._load_dates(self.current_cinema_id, movie_text)
            
        except Exception as e:
            self.message_manager.show_error(f"影片选择处理失败: {str(e)}")
    
    def _load_dates(self, cinema_id: str, movie_title: str):
        """加载日期列表"""
        try:
            # 调用电影服务获取日期列表
            dates = self.film_service.get_dates_by_movie(cinema_id, movie_title)
            
            # 更新下拉框
            self.date_combo.clear()
            if dates:
                for date in dates:
                    self.date_combo.addItem(date)
            else:
                self.date_combo.addItem("暂无排期")
                
        except Exception as e:
            self.date_combo.clear()
            self.date_combo.addItem("加载失败")
            self.message_manager.show_error(f"加载日期失败: {str(e)}")
    
    def _on_date_changed(self, date_text: str):
        """日期选择变化处理"""
        try:
            if not date_text or date_text in ["请先选择日期", "正在加载日期...", "暂无排期", "加载失败", ""]:
                return
            
            # 清空后续选择
            self.session_combo.clear()
            self.session_combo.addItem("正在加载场次...")
            
            # 加载场次列表
            movie_text = self.movie_combo.currentText()
            self._load_sessions(self.current_cinema_id, movie_text, date_text)
            
        except Exception as e:
            self.message_manager.show_error(f"日期选择处理失败: {str(e)}")
    
    def _load_sessions(self, cinema_id: str, movie_title: str, date: str):
        """加载场次列表"""
        try:
            # 调用电影服务获取场次列表
            sessions = self.film_service.get_sessions_by_date(cinema_id, movie_title, date)
            
            # 更新下拉框
            self.session_combo.clear()
            if sessions:
                for session in sessions:
                    self.session_combo.addItem(session.get("time", ""))
            else:
                self.session_combo.addItem("暂无场次")
                
        except Exception as e:
            self.session_combo.clear()
            self.session_combo.addItem("加载失败")
            self.message_manager.show_error(f"加载场次失败: {str(e)}")
    
    def _on_session_changed(self, session_text: str):
        """场次选择变化处理"""
        try:
            if not session_text or session_text in ["请先选择场次", "正在加载场次...", "暂无场次", "加载失败", ""]:
                return
            
            # 加载座位图和券列表
            self._load_seat_map()
            self._load_coupons()
            
        except Exception as e:
            self.message_manager.show_error(f"场次选择处理失败: {str(e)}")
    
    def _load_seat_map(self):
        """加载座位图"""
        try:
            # 这里应该加载实际的座位图
            # 临时显示提示信息
            pass
        except Exception as e:
            self.message_manager.show_error(f"加载座位图失败: {str(e)}")
    
    def _load_coupons(self):
        """加载可用券列表"""
        try:
            if not self.current_account:
                return
            
            # 调用券管理器获取可用券
            coupons = self.coupon_manager.get_available_coupons(
                self.current_account.get("phone", ""),
                self.current_cinema_id
            )
            
            # 更新券列表
            self.coupon_list.clear()
            self.coupons_data = coupons
            
            for coupon in coupons:
                self.coupon_list.addItem(coupon.get("display_text", ""))
                
        except Exception as e:
            self.message_manager.show_error(f"加载券列表失败: {str(e)}")

    def _on_submit_order(self):
        """提交订单处理"""
        try:
            # 检查必要条件
            if not self.current_account:
                self.message_manager.show_warning("请先选择账号")
                return
            
            if not self.current_cinema_id:
                self.message_manager.show_warning("请先选择影院")
                return
            
            cinema_text = self.cinema_combo.currentText()
            movie_text = self.movie_combo.currentText()
            date_text = self.date_combo.currentText()
            session_text = self.session_combo.currentText()
            
            if not all([cinema_text, movie_text, date_text, session_text]) or \
               any(text in ["请先选择", "正在加载", "暂无", "加载失败"] for text in [cinema_text, movie_text, date_text, session_text]):
                self.message_manager.show_warning("请完整选择影院、影片、日期和场次")
                return
            
            # 获取选择的座位
            selected_seats = self.seat_input.text().strip()
            if not selected_seats:
                self.message_manager.show_warning("请输入选择的座位")
                return
            
            # 构建订单数据
            order_data = {
                "account": self.current_account,
                "cinema_id": self.current_cinema_id,
                "cinema_name": cinema_text,
                "movie_title": movie_text,
                "show_date": date_text,
                "show_time": session_text,
                "selected_seats": selected_seats.split(","),  # 假设用逗号分隔多个座位
                "selected_coupons": self.selected_coupons
            }
            
            # 调用创建订单API
            self._create_order_api(order_data)
            
        except Exception as e:
            self.message_manager.show_error(f"提交订单失败: {str(e)}")
    
    def _create_order_api(self, order_data: dict):
        """创建订单API调用"""
        try:
            # 这里调用实际的订单创建API
            # 临时实现：模拟订单创建
            
            # 模拟订单结果
            order_result = {
                "success": True,
                "order_id": f"ORDER_{int(time.time())}",
                "total_price": 58.0,
                "seats": order_data["selected_seats"],
                "movie_title": order_data["movie_title"],
                "show_time": f"{order_data['show_date']} {order_data['show_time']}",
                "cinema_name": order_data["cinema_name"],
                "qr_code": "MOCK_QR_CODE_12345",
                "expire_time": int(time.time()) + 15 * 60  # 15分钟后过期
            }
            
            if order_result.get("success"):
                self.current_order = order_result
                self._show_order_detail(order_result)
                self.message_manager.show_success("订单提交成功！")
            else:
                self.message_manager.show_error(f"订单创建失败: {order_result.get('message', '未知错误')}")
                
        except Exception as e:
            self.message_manager.show_error(f"创建订单API调用失败: {str(e)}")
    
    def _show_order_detail(self, order_detail: dict):
        """显示订单详情"""
        try:
            # 更新用户信息显示
            phone = self.current_account.get("phone", "")
            self.user_info.setText(f"账号: {phone}")
            
            # 构建订单详情文本
            detail_text = f"""订单号: {order_detail.get('order_id', '')}
影片: {order_detail.get('movie_title', '')}
影院: {order_detail.get('cinema_name', '')}
时间: {order_detail.get('show_time', '')}
座位: {', '.join(order_detail.get('seats', []))}
金额: ¥{order_detail.get('total_price', 0)}
取票码: {order_detail.get('qr_code', '')}

订单状态: 待支付
请在15分钟内完成支付"""
            
            # 更新订单详情文本框
            self.order_detail.setPlainText(detail_text)
            
            # 启动倒计时
            self._start_countdown(order_detail.get('expire_time', 0))
            
        except Exception as e:
            self.message_manager.show_error(f"显示订单详情失败: {str(e)}")
    
    def _start_countdown(self, expire_timestamp: int):
        """启动订单倒计时"""
        try:
            # 连接倒计时定时器
            self.countdown_timer.timeout.connect(lambda: self._update_countdown(expire_timestamp))
            self.countdown_timer.start(1000)  # 每秒更新一次
            
        except Exception as e:
            self.message_manager.show_error(f"启动倒计时失败: {str(e)}")
    
    def _update_countdown(self, expire_timestamp: int):
        """更新倒计时显示"""
        try:
            current_time = int(time.time())
            remaining_seconds = expire_timestamp - current_time
            
            if remaining_seconds <= 0:
                # 订单已过期
                self.countdown_timer.stop()
                self.message_manager.show_warning("订单已过期")
                self.order_detail.append("\n\n⚠️ 订单已过期，请重新下单")
                return
            
            # 计算分钟和秒
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            # 更新订单详情中的倒计时信息
            current_text = self.order_detail.toPlainText()
            lines = current_text.split('\n')
            
            # 查找并更新倒计时行
            updated = False
            for i, line in enumerate(lines):
                if '剩余时间:' in line:
                    lines[i] = f"剩余时间: {minutes:02d}:{seconds:02d}"
                    updated = True
                    break
            
            if not updated:
                lines.append(f"剩余时间: {minutes:02d}:{seconds:02d}")
            
            self.order_detail.setPlainText('\n'.join(lines))
            
        except Exception as e:
            self.message_manager.show_error(f"更新倒计时失败: {str(e)}")
    
    def _on_one_click_pay(self):
        """一键支付处理"""
        try:
            if not self.current_order:
                self.message_manager.show_warning("没有待支付的订单")
                return
            
            # 确认支付
            reply = QMessageBox.question(
                self, "确认支付", 
                f"确认支付订单 {self.current_order.get('order_id', '')}？\n"
                f"金额: ¥{self.current_order.get('total_price', 0)}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._process_payment()
                
        except Exception as e:
            self.message_manager.show_error(f"支付处理失败: {str(e)}")
    
    def _process_payment(self):
        """处理支付流程"""
        try:
            # 调用支付API
            payment_data = {
                "order_id": self.current_order.get("order_id"),
                "amount": self.current_order.get("total_price"),
                "account": self.current_account
            }
            
            # 模拟支付成功
            payment_result = {
                "success": True,
                "message": "支付成功",
                "payment_id": f"PAY_{int(time.time())}"
            }
            
            if payment_result.get("success"):
                # 停止倒计时
                self.countdown_timer.stop()
                
                # 更新订单状态
                self.order_detail.append(f"\n\n✅ 支付成功！\n支付单号: {payment_result.get('payment_id')}")
                
                self.message_manager.show_success("支付成功！请凭取票码到影院取票")
                
                # 清空当前订单
                self.current_order = None
                
            else:
                self.message_manager.show_error(f"支付失败: {payment_result.get('message', '未知错误')}")
                
        except Exception as e:
            self.message_manager.show_error(f"支付流程处理失败: {str(e)}")

def main():
    """测试经典风格界面"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    window = CinemaOrderSimulatorClassicWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 