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
import random

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
        """🔧 设置表格样式 - 移除悬停效果"""
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
        
        # Tab2: 绑券
        tab2 = QWidget()
        self._build_bind_coupon_tab(tab2)
        self.tab_widget.addTab(tab2, "绑券")
        
        # Tab3: 兑换券
        tab3 = QWidget()
        self._build_exchange_coupon_tab(tab3)
        self.tab_widget.addTab(tab3, "兑换券")
        
        # Tab4: 订单
        tab4 = QWidget()
        self._build_order_tab(tab4)
        self.tab_widget.addTab(tab4, "订单")
        
        # Tab5: 影院
        tab5 = QWidget()
        self._build_cinema_tab(tab5)
        self.tab_widget.addTab(tab5, "影院")
    
    def _build_bind_coupon_tab(self, tab_widget):
        """构建绑券Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号信息显示
        self.bind_account_label = QLabel("当前账号: 15155712316 @ 深影国际影城(佐伦虹湾购物中心店)")
        self.bind_account_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font: bold 12px "Microsoft YaHei";
                padding: 8px;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.bind_account_label)
        
        # 主要内容区域 - 左右分栏
        content_layout = QHBoxLayout()
        
        # 左侧输入区
        left_group = ClassicGroupBox("每行一个券号：")
        left_layout = QVBoxLayout(left_group)
        
        # 券号输入文本框
        self.coupon_input = QTextEdit()
        self.coupon_input.setPlaceholderText("请在此输入券号，每行一个券号")
        self.coupon_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font: 11px "Microsoft YaHei";
                padding: 8px;
                line-height: 1.4;
            }
        """)
        left_layout.addWidget(self.coupon_input)
        
        # 绑定按钮
        self.bind_coupon_btn = ClassicButton("绑定当前账号", "success")
        self.bind_coupon_btn.setMinimumHeight(35)
        left_layout.addWidget(self.bind_coupon_btn)
        
        content_layout.addWidget(left_group, 1)
        
        # 右侧日志区
        right_group = ClassicGroupBox("绑定日志：")
        right_layout = QVBoxLayout(right_group)
        
        # 日志文本框
        self.bind_log = QTextEdit()
        self.bind_log.setReadOnly(True)
        self.bind_log.setPlaceholderText("绑定日志将在此显示...")
        self.bind_log.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: #f9f9f9;
                font: 10px "Microsoft YaHei";
                padding: 8px;
            }
        """)
        right_layout.addWidget(self.bind_log)
        
        # 复制日志按钮
        copy_log_layout = QHBoxLayout()
        copy_log_layout.addStretch()
        self.copy_log_btn = ClassicButton("复制日志", "default")
        self.copy_log_btn.setMaximumWidth(80)
        copy_log_layout.addWidget(self.copy_log_btn)
        right_layout.addLayout(copy_log_layout)
        
        content_layout.addWidget(right_group, 1)
        
        layout.addLayout(content_layout)
    
    def _build_exchange_coupon_tab(self, tab_widget):
        """构建兑换券Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号信息显示
        self.exchange_account_label = QLabel("当前账号: 15155712316 @ 深影国际影城(佐伦虹湾购物中心店) (余额:0)")
        self.exchange_account_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font: bold 12px "Microsoft YaHei";
                padding: 8px;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.exchange_account_label)
        
        # 兑换功能区域
        exchange_group = ClassicGroupBox("积分兑换券")
        exchange_layout = QGridLayout(exchange_group)
        
        # 积分信息
        points_label = QLabel("当前积分:")
        self.points_display = QLabel("0")
        self.points_display.setStyleSheet("font: bold 14px 'Microsoft YaHei'; color: #ff6600;")
        
        exchange_layout.addWidget(points_label, 0, 0)
        exchange_layout.addWidget(self.points_display, 0, 1)
        
        # 兑换选项
        exchange_type_label = QLabel("兑换类型:")
        self.exchange_type_combo = ClassicComboBox()
        self.exchange_type_combo.addItems([
            "请选择兑换类型",
            "10元代金券 (需要100积分)",
            "5折优惠券 (需要200积分)",
            "买一送一券 (需要300积分)"
        ])
        
        exchange_layout.addWidget(exchange_type_label, 1, 0)
        exchange_layout.addWidget(self.exchange_type_combo, 1, 1)
        
        # 兑换数量
        quantity_label = QLabel("兑换数量:")
        self.exchange_quantity = ClassicLineEdit("1")
        self.exchange_quantity.setMaximumWidth(100)
        
        exchange_layout.addWidget(quantity_label, 2, 0)
        exchange_layout.addWidget(self.exchange_quantity, 2, 1)
        
        # 兑换按钮
        self.exchange_btn = ClassicButton("立即兑换", "warning")
        self.exchange_btn.setMinimumHeight(35)
        exchange_layout.addWidget(self.exchange_btn, 3, 0, 1, 2)
        
        layout.addWidget(exchange_group)
        
        # 兑换记录
        record_group = ClassicGroupBox("兑换记录")
        record_layout = QVBoxLayout(record_group)
        
        self.exchange_record = QTextEdit()
        self.exchange_record.setReadOnly(True)
        self.exchange_record.setPlaceholderText("兑换记录将在此显示...")
        self.exchange_record.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: #f9f9f9;
                font: 10px "Microsoft YaHei";
                padding: 8px;
            }
        """)
        record_layout.addWidget(self.exchange_record)
        
        layout.addWidget(record_group)
    
    def _build_order_tab(self, tab_widget):
        """构建订单Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.order_refresh_btn = ClassicButton("刷新", "default")
        self.order_refresh_btn.setMaximumWidth(80)
        button_layout.addWidget(self.order_refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 订单表格
        self.order_table = ClassicTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["影片", "影院", "状态", "订单号"])
        
        # 设置表格属性
        self.order_table.setAlternatingRowColors(True)
        self.order_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.order_table.horizontalHeader().setStretchLastSection(True)
        self.order_table.verticalHeader().setVisible(False)
        
        # 设置列宽
        header = self.order_table.horizontalHeader()
        header.resizeSection(0, 150)  # 影片
        header.resizeSection(1, 180)  # 影院  
        header.resizeSection(2, 150)  # 状态
        # 订单号列自动拉伸
        
        # 设置表格样式
        self.order_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                font: 13px "Microsoft YaHei";
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
                text-align: center;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 8px;
                font: bold 13px "Microsoft YaHei";
                color: #333333;
                text-align: center;
            }
        """)
        
        # 设置行高
        self.order_table.verticalHeader().setDefaultSectionSize(36)
        
        layout.addWidget(self.order_table)
        
        # 添加示例数据
        self._load_sample_orders()
    
    def _build_cinema_tab(self, tab_widget):
        """构建影院Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.cinema_refresh_btn = ClassicButton("刷新影院列表", "default")
        self.add_cinema_btn = ClassicButton("添加影院", "success")
        self.delete_cinema_btn = ClassicButton("删除影院", "warning")
        
        button_layout.addWidget(self.cinema_refresh_btn)
        button_layout.addWidget(self.add_cinema_btn)
        button_layout.addWidget(self.delete_cinema_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 影院表格
        self.cinema_table = ClassicTableWidget()
        self.cinema_table.setColumnCount(3)
        self.cinema_table.setHorizontalHeaderLabels(["影院名称", "影院ID", "地址"])
        
        # 设置表格属性
        self.cinema_table.setAlternatingRowColors(True)
        self.cinema_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cinema_table.horizontalHeader().setStretchLastSection(True)
        self.cinema_table.verticalHeader().setVisible(False)
        
        # 设置列宽
        header = self.cinema_table.horizontalHeader()
        header.resizeSection(0, 200)  # 影院名称
        header.resizeSection(1, 150)  # 影院ID
        # 地址列自动拉伸
        
        layout.addWidget(self.cinema_table)
        
        # 加载影院数据
        self._load_cinema_data_to_table()
    
    def _load_sample_orders(self):
        """加载示例订单数据"""
        try:
            # 示例订单数据
            sample_orders = [
                {
                    "movie": "阿凡达：水之道",
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "已完成",
                    "order_id": "ORDER2024122701"
                },
                {
                    "movie": "流浪地球2", 
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "待支付",
                    "order_id": "ORDER2024122702"
                },
                {
                    "movie": "满江红",
                    "cinema": "华夏优加金太都会",
                    "status": "已取消",
                    "order_id": "ORDER2024122703"
                }
            ]
            
            self.order_table.setRowCount(len(sample_orders))
            for i, order in enumerate(sample_orders):
                self.order_table.setItem(i, 0, QTableWidgetItem(order["movie"]))
                self.order_table.setItem(i, 1, QTableWidgetItem(order["cinema"]))
                
                # 设置状态项的颜色
                status_item = QTableWidgetItem(order["status"])
                if order["status"] == "已完成":
                    status_item.setForeground(QColor("#4caf50"))
                elif order["status"] == "待支付":
                    status_item.setForeground(QColor("#ff9800"))
                elif order["status"] == "已取消":
                    status_item.setForeground(QColor("#f44336"))
                
                self.order_table.setItem(i, 2, status_item)
                self.order_table.setItem(i, 3, QTableWidgetItem(order["order_id"]))
                
        except Exception as e:
            print(f"[订单加载] 错误: {e}")
    
    def _load_cinema_data_to_table(self):
        """加载影院数据到表格"""
        try:
            # 从影院管理器获取数据
            cinemas = self.cinema_manager.load_cinema_list()
            
            if not cinemas:
                # 使用示例数据
                cinemas = [
                    {
                        "cinemaShortName": "华夏优加金太都会",
                        "cinemaid": "35fec8259e74",
                        "cinemaAddress": "高新大都会负一层"  # 修复字段名
                    },
                    {
                        "cinemaShortName": "深影国际影城(佐伦虹湾购物中心店)",
                        "cinemaid": "11b7e4bcc265", 
                        "cinemaAddress": "福田区北环大道6098号佐伦虹湾购物中心"  # 修复字段名
                    },
                    {
                        "cinemaShortName": "深圳万友影城BCMall店",
                        "cinemaid": "0f1e21d86ac8",
                        "cinemaAddress": "罗湖区布心路3008号BCMALl4楼"  # 修复字段名
                    }
                ]
            
            self.cinema_table.setRowCount(len(cinemas))
            for i, cinema in enumerate(cinemas):
                name = cinema.get("cinemaShortName", cinema.get("name", ""))
                cinema_id = cinema.get("cinemaid", "")
                # 修复地址字段映射 - 问题1解决
                address = cinema.get("cinemaAddress", cinema.get("address", ""))
                
                self.cinema_table.setItem(i, 0, QTableWidgetItem(name))
                self.cinema_table.setItem(i, 1, QTableWidgetItem(cinema_id))
                self.cinema_table.setItem(i, 2, QTableWidgetItem(address))
                
                # 保存完整数据到第一列
                self.cinema_table.item(i, 0).setData(Qt.UserRole, cinema)
                
        except Exception as e:
            print(f"[影院表格加载] 错误: {e}")
    
    def _show_add_cinema_dialog(self):
        """显示添加影院对话框 - 实现真实API验证"""
        try:
            from PyQt5.QtWidgets import QDialog, QDialogButtonBox
            
            dialog = QDialog(self)
            dialog.setWindowTitle("添加影院")
            dialog.setFixedSize(450, 280)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # 添加说明文字
            info_label = QLabel("请输入影院ID，系统将自动验证并获取影院信息：")
            info_label.setStyleSheet("QLabel { color: #666; font: 12px 'Microsoft YaHei'; }")
            layout.addWidget(info_label)
            
            # 影院ID输入
            id_layout = QHBoxLayout()
            id_label = QLabel("影院ID:")
            id_label.setMinimumWidth(80)
            id_label.setStyleSheet("QLabel { font: bold 12px 'Microsoft YaHei'; }")
            self.cinema_id_input = ClassicLineEdit()
            self.cinema_id_input.setPlaceholderText("请输入12位影院ID，如：35fec8259e74")
            id_layout.addWidget(id_label)
            id_layout.addWidget(self.cinema_id_input)
            layout.addLayout(id_layout)
            
            # 验证状态显示
            self.verify_status_label = QLabel("等待输入影院ID...")
            self.verify_status_label.setStyleSheet("""
                QLabel { 
                    color: #666; 
                    font: 11px 'Microsoft YaHei'; 
                    padding: 8px; 
                    background-color: #f5f5f5; 
                    border: 1px solid #ddd; 
                    border-radius: 3px; 
                }
            """)
            layout.addWidget(self.verify_status_label)
            
            # 验证按钮
            verify_btn = ClassicButton("验证影院ID", "primary")
            verify_btn.clicked.connect(lambda: self._verify_cinema_id_in_dialog())
            layout.addWidget(verify_btn)
            
            # 按钮组
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            
            # 设置按钮文本和样式
            ok_btn = button_box.button(QDialogButtonBox.Ok)
            ok_btn.setText("添加影院")
            ok_btn.setEnabled(False)  # 初始禁用，验证成功后启用
            ok_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    font: bold 11px "Microsoft YaHei";
                    border: none;
                    padding: 10px 20px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #888;
                }
                QPushButton:hover:enabled {
                    background-color: #45a049;
                }
            """)
            
            cancel_btn = button_box.button(QDialogButtonBox.Cancel)
            cancel_btn.setText("取消")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    font: 11px "Microsoft YaHei";
                    border: none;
                    padding: 10px 20px;
                    border-radius: 3px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            # 保存引用到dialog对象上，便于在验证方法中访问
            dialog.ok_btn = ok_btn
            dialog.cinema_id_input = self.cinema_id_input
            dialog.verify_status_label = self.verify_status_label
            dialog.verified_cinema_data = None  # 存储验证成功的影院数据
            
            # 保存对话框引用
            self.add_cinema_dialog = dialog
            
            if dialog.exec_() == QDialog.Accepted:
                if hasattr(dialog, 'verified_cinema_data') and dialog.verified_cinema_data:
                    self._add_verified_cinema_to_system(dialog.verified_cinema_data)
                else:
                    QMessageBox.warning(self, "添加失败", "请先验证影院ID")
            
        except Exception as e:
            QMessageBox.critical(self, "添加影院错误", f"显示添加影院对话框失败: {str(e)}")

    def _verify_cinema_id_in_dialog(self):
        """在对话框中验证影院ID - 问题3解决"""
        try:
            if not hasattr(self, 'add_cinema_dialog'):
                return
                
            dialog = self.add_cinema_dialog
            cinema_id = dialog.cinema_id_input.text().strip()
            
            if not cinema_id:
                dialog.verify_status_label.setText("❌ 请输入影院ID")
                dialog.verify_status_label.setStyleSheet("""
                    QLabel { 
                        color: #f44336; 
                        font: 11px 'Microsoft YaHei'; 
                        padding: 8px; 
                        background-color: #ffebee; 
                        border: 1px solid #f44336; 
                        border-radius: 3px; 
                    }
                """)
                dialog.ok_btn.setEnabled(False)
                return
            
            # 显示验证中状态
            dialog.verify_status_label.setText("🔄 正在验证影院ID...")
            dialog.verify_status_label.setStyleSheet("""
                QLabel { 
                    color: #2196f3; 
                    font: 11px 'Microsoft YaHei'; 
                    padding: 8px; 
                    background-color: #e3f2fd; 
                    border: 1px solid #2196f3; 
                    border-radius: 3px; 
                }
            """)
            QApplication.processEvents()  # 刷新界面
            
            # 调用真实的影院验证API
            from services.cinema_info_api import validate_cinema
            
            print(f"[影院验证] 开始验证影院ID: {cinema_id}")
            is_valid, cinema_info, base_url = validate_cinema(cinema_id)
            
            if is_valid and cinema_info:
                # 验证成功
                cinema_name = cinema_info.get('cinemaShortName', cinema_info.get('cinemaName', '未知影院'))
                cinema_address = cinema_info.get('cinemaAddress', '地址未知')
                
                # 格式化完整的影院数据
                from services.cinema_info_api import format_cinema_data
                complete_cinema_data = format_cinema_data(cinema_info, base_url, cinema_id)
                
                dialog.verify_status_label.setText(
                    f"✅ 验证成功！\n"
                    f"影院名称：{cinema_name}\n"
                    f"影院地址：{cinema_address}\n"
                    f"API域名：{base_url}"
                )
                dialog.verify_status_label.setStyleSheet("""
                    QLabel { 
                        color: #4caf50; 
                        font: 11px 'Microsoft YaHei'; 
                        padding: 8px; 
                        background-color: #e8f5e8; 
                        border: 1px solid #4caf50; 
                        border-radius: 3px; 
                    }
                """)
                
                # 保存验证成功的数据
                dialog.verified_cinema_data = complete_cinema_data
                dialog.ok_btn.setEnabled(True)
                
                print(f"[影院验证] 验证成功 - 影院: {cinema_name}, 地址: {cinema_address}")
                
            else:
                # 验证失败
                dialog.verify_status_label.setText(
                    f"❌ 验证失败！\n"
                    f"影院ID '{cinema_id}' 无效或无法访问\n"
                    f"请检查ID是否正确或联系管理员"
                )
                dialog.verify_status_label.setStyleSheet("""
                    QLabel { 
                        color: #f44336; 
                        font: 11px 'Microsoft YaHei'; 
                        padding: 8px; 
                        background-color: #ffebee; 
                        border: 1px solid #f44336; 
                        border-radius: 3px; 
                    }
                """)
                
                dialog.verified_cinema_data = None
                dialog.ok_btn.setEnabled(False)
                
                print(f"[影院验证] 验证失败 - 影院ID: {cinema_id}")
                
        except Exception as e:
            if hasattr(self, 'add_cinema_dialog'):
                dialog = self.add_cinema_dialog
                dialog.verify_status_label.setText(f"❌ 验证出错：{str(e)}")
                dialog.verify_status_label.setStyleSheet("""
                    QLabel { 
                        color: #f44336; 
                        font: 11px 'Microsoft YaHei'; 
                        padding: 8px; 
                        background-color: #ffebee; 
                        border: 1px solid #f44336; 
                        border-radius: 3px; 
                    }
                """)
                dialog.ok_btn.setEnabled(False)
            
            print(f"[影院验证] 验证异常: {e}")

    def _add_verified_cinema_to_system(self, cinema_data):
        """将验证成功的影院添加到系统中"""
        try:
            # 调用影院管理器的真实添加方法
            success, result = self.cinema_manager.add_cinema_by_id(cinema_data.get('cinemaid'))
            
            if success:
                cinema_name = cinema_data.get('cinemaShortName', '未知影院')
                QMessageBox.information(
                    self, "添加成功", 
                    f"影院添加成功！\n"
                    f"影院名称：{cinema_name}\n"
                    f"影院ID：{cinema_data.get('cinemaid')}\n"
                    f"影院地址：{cinema_data.get('cinemaAddress', '地址未知')}"
                )
                
                # 刷新影院表格和下拉列表
                self._load_cinema_data_to_table()
                self._refresh_cinema_list()
                
                print(f"[影院添加] 成功添加影院: {cinema_name}")
                
            else:
                QMessageBox.warning(self, "添加失败", f"添加影院失败：{result}")
                print(f"[影院添加] 添加失败: {result}")
                
        except Exception as e:
            QMessageBox.critical(self, "添加错误", f"添加影院到系统失败: {str(e)}")
            print(f"[影院添加] 添加异常: {e}")

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
            
            # 3. API验证成功后严格检查机器码匹配
            current_machine_code = self.auth_service.get_machine_code()
            # 兼容不同的机器码字段名
            login_machine_code = user_info.get("machine_code") or user_info.get("machineCode", "")
            
            print(f"[主窗口验证] 当前机器码: {current_machine_code}")
            print(f"[主窗口验证] 登录机器码: {login_machine_code}")
            
            # 严格的机器码匹配检查
            if current_machine_code != login_machine_code:
                print(f"[主窗口验证] 机器码不匹配，拒绝登录")
                QMessageBox.critical(
                    self, "登录失败", 
                    f"设备验证失败，机器码不匹配\n"
                    f"当前设备机器码: {current_machine_code}\n"
                    f"注册设备机器码: {login_machine_code}\n"
                    f"请使用注册设备登录或联系管理员重新绑定设备"
                )
                self._restart_login()
                return
            else:
                print(f"[主窗口验证] 机器码匹配成功")
            
            # 4. 所有验证通过，保存用户信息
            self.current_user = user_info
            
            # 5. 确保登录窗口完全关闭后再显示主窗口
            if hasattr(self, 'login_window'):
                self.login_window.close()
                self.login_window = None  # 清除引用
            
            # 6. 延迟显示主窗口，确保登录窗口已关闭
            QTimer.singleShot(100, self._show_main_window_after_login)
            
        except Exception as e:
            QMessageBox.critical(self, "登录处理错误", f"处理登录结果失败: {str(e)}")
            self._restart_login()
    
    def _show_main_window_after_login(self):
        """登录成功后显示主窗口"""
        try:
            # 显示主窗口
            self.show()
            
            # 加载用户数据
            self._load_user_data()
            
            # 发出登录成功信号
            self.login_success.emit(self.current_user)
            
            # 使用QMessageBox代替MessageManager显示成功消息
            phone = self.current_user.get('username', self.current_user.get('phone', ''))
            QMessageBox.information(
                self, 
                "登录成功", 
                f"登录验证成功，欢迎使用柴犬影院系统\n用户: {phone}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "显示主窗口错误", f"显示主窗口失败: {str(e)}")
    
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
            # 隐藏主窗口
            self.hide()
            
            # 确保旧的登录窗口被清理
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # 延迟创建新的登录窗口，确保旧窗口完全关闭
            QTimer.singleShot(200, self._create_new_login_window)
            
        except Exception as e:
            QMessageBox.critical(self, "重启登录失败", f"无法重新启动登录: {str(e)}")
            QApplication.quit()
    
    def _create_new_login_window(self):
        """创建新的登录窗口"""
        try:
            # 重新创建登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            self.login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "创建登录窗口失败", f"无法创建登录窗口: {str(e)}")
            QApplication.quit()
    
    def _load_user_data(self):
        """加载用户相关数据"""
        try:
            # 刷新账号列表（从本地JSON文件）
            self._refresh_account_list()
            
            # 刷新影院列表（从本地JSON文件）
            self._refresh_cinema_list()
            
        except Exception as e:
            # 使用QMessageBox代替MessageManager
            QMessageBox.warning(self, "数据加载失败", f"加载用户数据失败: {str(e)}")
    
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
            # 使用QMessageBox代替MessageManager
            QMessageBox.warning(self, "账号加载失败", f"刷新账号列表失败: {str(e)}")
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
            # 使用QMessageBox代替MessageManager
            QMessageBox.warning(self, "影院加载失败", f"刷新影院列表失败: {str(e)}")
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

    def _on_delete_cinema(self):
        """删除选中的影院 - 问题2解决"""
        try:
            current_row = self.cinema_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "选择错误", "请选择要删除的影院")
                return
            
            cinema_name = self.cinema_table.item(current_row, 0).text()
            cinema_id = self.cinema_table.item(current_row, 1).text()
            cinema_address = self.cinema_table.item(current_row, 2).text()
            
            reply = QMessageBox.question(
                self, "确认删除",
                f"确认删除影院？\n\n"
                f"影院名称：{cinema_name}\n"
                f"影院ID：{cinema_id}\n"
                f"影院地址：{cinema_address}\n\n"
                f"⚠️ 删除后将无法恢复，请谨慎操作！",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 调用真实的影院管理器删除方法
                success, message = self.cinema_manager.delete_cinema_by_id(cinema_id)
                
                if success:
                    # 从表格中删除行
                    self.cinema_table.removeRow(current_row)
                    
                    # 刷新影院下拉列表
                    self._refresh_cinema_list()
                    
                    QMessageBox.information(
                        self, "删除成功", 
                        f"影院删除成功！\n"
                        f"已从系统中移除：{cinema_name}"
                    )
                    
                    print(f"[影院删除] 成功删除影院: {cinema_name} (ID: {cinema_id})")
                    
                else:
                    QMessageBox.critical(
                        self, "删除失败", 
                        f"删除影院失败：{message}\n\n"
                        f"可能原因：\n"
                        f"1. 影院文件被占用\n"
                        f"2. 没有写入权限\n"
                        f"3. 影院ID不存在"
                    )
                    print(f"[影院删除] 删除失败: {message}")
            
        except Exception as e:
            QMessageBox.critical(self, "删除错误", f"删除影院失败: {str(e)}")
            print(f"[影院删除] 删除异常: {e}")

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
        
        # 绑券Tab按钮
        self.bind_coupon_btn.clicked.connect(self._on_bind_coupon)
        self.copy_log_btn.clicked.connect(self._on_copy_bind_log)
        
        # 兑换券Tab按钮
        self.exchange_btn.clicked.connect(self._on_exchange_coupon)
        
        # 订单Tab按钮
        self.order_refresh_btn.clicked.connect(self._on_refresh_orders)
        
        # 影院Tab按钮
        self.cinema_refresh_btn.clicked.connect(self._on_refresh_cinemas)
        self.add_cinema_btn.clicked.connect(self._show_add_cinema_dialog)
        self.delete_cinema_btn.clicked.connect(self._on_delete_cinema)
    
    # ===== Tab页面事件处理方法 =====
    
    def _on_bind_coupon(self):
        """绑定券处理"""
        try:
            coupon_text = self.coupon_input.toPlainText().strip()
            if not coupon_text:
                QMessageBox.warning(self, "输入错误", "请输入要绑定的券号")
                return
            
            if not self.current_account:
                QMessageBox.warning(self, "账号错误", "请先选择账号")
                return
            
            # 按行分割券号
            coupon_lines = [line.strip() for line in coupon_text.split('\n') if line.strip()]
            
            # 模拟绑定处理
            success_count = 0
            fail_count = 0
            log_text = f"开始绑定 {len(coupon_lines)} 个券号...\n"
            
            for i, coupon_code in enumerate(coupon_lines):
                # 模拟绑定结果
                is_success = random.choice([True, True, False])  # 2/3概率成功
                
                if is_success:
                    success_count += 1
                    log_text += f"✅ 券号 {coupon_code} 绑定成功\n"
                else:
                    fail_count += 1
                    log_text += f"❌ 券号 {coupon_code} 绑定失败：券号无效或已使用\n"
            
            log_text += f"\n绑定完成：成功 {success_count} 个，失败 {fail_count} 个"
            
            # 更新日志
            self.bind_log.setPlainText(log_text)
            
            # 清空输入框
            self.coupon_input.clear()
            
            QMessageBox.information(self, "绑定完成", f"券绑定完成\n成功：{success_count} 个\n失败：{fail_count} 个")
            
        except Exception as e:
            QMessageBox.critical(self, "绑定错误", f"券绑定失败: {str(e)}")
    
    def _on_copy_bind_log(self):
        """复制绑定日志"""
        try:
            log_text = self.bind_log.toPlainText()
            if log_text:
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(log_text)
                QMessageBox.information(self, "复制成功", "绑定日志已复制到剪贴板")
            else:
                QMessageBox.warning(self, "无内容", "没有日志内容可复制")
        except Exception as e:
            QMessageBox.critical(self, "复制错误", f"复制日志失败: {str(e)}")
    
    def _on_exchange_coupon(self):
        """兑换券处理"""
        try:
            exchange_type = self.exchange_type_combo.currentText()
            if exchange_type == "请选择兑换类型":
                QMessageBox.warning(self, "选择错误", "请选择兑换类型")
                return
            
            quantity_text = self.exchange_quantity.text().strip()
            try:
                quantity = int(quantity_text)
                if quantity <= 0:
                    raise ValueError("数量必须大于0")
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的兑换数量")
                return
            
            # 解析所需积分
            required_points = 0
            if "100积分" in exchange_type:
                required_points = 100
            elif "200积分" in exchange_type:
                required_points = 200
            elif "300积分" in exchange_type:
                required_points = 300
            
            total_required = required_points * quantity
            current_points = int(self.points_display.text())
            
            if current_points < total_required:
                QMessageBox.warning(
                    self, "积分不足", 
                    f"积分不足！\n当前积分：{current_points}\n需要积分：{total_required}"
                )
                return
            
            # 确认兑换
            reply = QMessageBox.question(
                self, "确认兑换",
                f"确认兑换 {quantity} 个 {exchange_type.split('(')[0]}？\n"
                f"将消耗 {total_required} 积分",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 模拟兑换成功
                new_points = current_points - total_required
                self.points_display.setText(str(new_points))
                
                # 更新兑换记录
                import time
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                record_text = self.exchange_record.toPlainText()
                new_record = f"[{timestamp}] 兑换 {quantity} 个 {exchange_type.split('(')[0]}，消耗 {total_required} 积分\n"
                self.exchange_record.setPlainText(new_record + record_text)
                
                QMessageBox.information(self, "兑换成功", f"成功兑换 {quantity} 个券！")
            
        except Exception as e:
            QMessageBox.critical(self, "兑换错误", f"券兑换失败: {str(e)}")
    
    def _on_refresh_orders(self):
        """刷新订单列表"""
        try:
            # 重新加载订单数据
            self._load_sample_orders()
            QMessageBox.information(self, "刷新成功", "订单列表已刷新")
        except Exception as e:
            QMessageBox.critical(self, "刷新错误", f"刷新订单失败: {str(e)}")
    
    def _on_refresh_cinemas(self):
        """刷新影院列表"""
        try:
            # 重新加载影院数据
            self._load_cinema_data_to_table()
            QMessageBox.information(self, "刷新成功", "影院列表已刷新")
        except Exception as e:
            QMessageBox.critical(self, "刷新错误", f"刷新影院失败: {str(e)}")

    # ===== 其他必要的界面构建方法 =====
    
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

    # ===== 其他必要的事件处理方法（简化版本） =====
    
    def _on_cinema_account_login(self):
        """影院账号登录处理（简化版）"""
        QMessageBox.information(self, "登录提示", "影院账号登录功能已简化，请直接从账号列表中选择账号")
    
    def _on_refresh_account_list(self):
        """刷新账号列表"""
        try:
            self._refresh_account_list()
            QMessageBox.information(self, "刷新成功", "账号列表刷新成功")
        except Exception as e:
            QMessageBox.critical(self, "刷新失败", f"刷新失败: {str(e)}")
    
    def _on_account_selection_changed(self):
        """账号选择变化处理（简化版）"""
        try:
            current_row = self.account_table.currentRow()
            if current_row >= 0:
                userid = self.account_table.item(current_row, 0).text()
                balance = self.account_table.item(current_row, 2).text()
                self.current_account_label.setText(f"当前账号: {userid} (余额:{balance})")
        except Exception as e:
            print(f"[账号选择] 错误: {e}")
    
    @pyqtSlot(dict)
    def _on_account_changed(self, account_info: dict):
        """账号切换信号处理（简化版）"""
        pass
    
    def _on_cinema_changed(self, cinema_text: str):
        """影院选择变化处理（简化版）"""
        pass
    
    def _on_movie_changed(self, movie_text: str):
        """影片选择变化处理（简化版）"""
        pass
    
    def _on_date_changed(self, date_text: str):
        """日期选择变化处理（简化版）"""
        pass
    
    def _on_session_changed(self, session_text: str):
        """场次选择变化处理（简化版）"""
        pass
    
    def _on_submit_order(self):
        """提交订单处理（简化版）"""
        QMessageBox.information(self, "订单提示", "订单功能正在开发中")
    
    def _on_one_click_pay(self):
        """一键支付处理（简化版）"""
        QMessageBox.information(self, "支付提示", "支付功能正在开发中")

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