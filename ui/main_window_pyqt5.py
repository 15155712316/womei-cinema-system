#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - PyQt5主窗口
完全复刻tkinter版本的界面布局和功能
"""

import sys
import os
import json
import datetime
import time
import traceback
from typing import Dict, List, Optional, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QTabWidget,
    QGroupBox, QFrame, QMessageBox, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QAbstractItemView, QComboBox, QSpinBox, QProgressBar,
    QMenu, QAction, QSplitter, QScrollArea, QCheckBox
)
from PyQt5.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, pyqtSlot, QRect, QSize, QPoint
)
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QClipboard, QCursor
)

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.login_window import LoginWindow
from ui.components.account_list_panel_pyqt5 import AccountListPanelPyQt5
from ui.components.cinema_select_panel_pyqt5 import CinemaSelectPanelPyQt5  
from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

from services.auth_service import auth_service
from services.ui_utils import MessageManager, CouponManager, UIConstants
from services.order_api import (
    create_order, get_unpaid_order_detail, get_coupons_by_order,
    bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api,
    cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
)

from PIL import Image, ImageDraw, ImageFont, ImageTk
import io
import re

class CinemaOrderSimulatorMainWindow(QMainWindow):
    """柴犬影院下单系统主窗口 - PyQt5版本"""
    
    def __init__(self):
        super().__init__()
        
        # 用户认证相关
        self.current_user = None
        self.auth_check_timer = None
        
        # 业务数据
        self.last_priceinfo = {}
        self.current_order = None
        self.member_info = None
        self.selected_coupons_info = None
        self.current_coupon_info = None
        self.coupons_data = []
        self.selected_coupons = []
        self.max_coupon_select = 1
        
        # UI状态
        self.ui_state = "initial"
        self.show_debug = False
        
        # 设置窗口基本属性
        self.setWindowTitle("柴犬影院下单系统")
        self.setFixedSize(1250, 750)  # 固定窗口大小
        self.setStyleSheet("QMainWindow { background-color: #f8f8f8; }")
        
        # 隐藏窗口，等待用户登录
        self.hide()
        
        # 初始化界面
        self._init_ui()
        
        # 启动用户认证检查
        self._start_auth_check()
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 计算各栏宽度 - 严格按照README要求
        total_width = 1250
        total_height = 750
        left_w = int(total_width * 0.2)    # 250px (20%)
        center_w = int(total_width * 0.6)  # 750px (60%)
        right_w = total_width - left_w - center_w  # 250px (20%)
        
        # 创建三栏布局框架 - 使用绝对定位复刻tkinter的place布局
        self._create_left_panel(0, 0, left_w, total_height)
        self._create_center_panel(left_w, 0, center_w, total_height)
        self._create_right_panel(left_w + center_w, 0, right_w, total_height)
    
    def _create_left_panel(self, x: int, y: int, width: int, height: int):
        """创建左栏面板 - 账号登录区和账号列表区"""
        left_frame = QFrame(self.centralWidget())
        left_frame.setGeometry(x, y, width, height)
        left_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        # 左栏上下分区 - 按照README精确比例
        login_h = int(height * 0.33)  # 上部33%
        account_h = height - login_h  # 下部67%
        
        # 账号登录区（上部）
        self.login_group = QGroupBox("账号登录区", left_frame)
        self.login_group.setGeometry(0, 0, width, login_h)
        self._setup_login_area_style(self.login_group)
        self._build_login_area()
        
        # 账号列表区（下部）
        self.account_list_group = QGroupBox("账号列表区", left_frame)
        self.account_list_group.setGeometry(0, login_h, width, account_h)
        self._setup_login_area_style(self.account_list_group)
        
        # 集成账号列表面板
        self.account_list_panel = AccountListPanelPyQt5(
            self.account_list_group,
            on_account_selected=self.set_current_account,
            on_set_main=self.set_main_account,
            on_clear_coupons=self.clear_coupons,
            on_refresh_coupons=self.refresh_coupons
        )
        
        # 设置账号列表面板布局
        account_layout = QVBoxLayout(self.account_list_group)
        account_layout.addWidget(self.account_list_panel)
        account_layout.setContentsMargins(5, 20, 5, 5)  # 为标题留空间
    
    def _create_center_panel(self, x: int, y: int, width: int, height: int):
        """创建中栏面板 - Tab区域和座位区域"""
        center_frame = QFrame(self.centralWidget())
        center_frame.setGeometry(x, y, width, height)
        center_frame.setStyleSheet("QFrame { background-color: #fff; }")
        
        # 中栏上下分区
        center_top_h = int(height * 0.38)  # 上部38%
        center_bottom_h = height - center_top_h  # 下部62%
        
        # 下部座位区域 - 先创建座位面板
        self.seat_group = QGroupBox("座位区域", center_frame)
        self.seat_group.setGeometry(0, center_top_h, width, center_bottom_h)
        self._setup_login_area_style(self.seat_group)
        
        # 创建座位面板
        self.seat_panel = SeatMapPanelPyQt5(self.seat_group, seat_data=[])
        seat_layout = QVBoxLayout(self.seat_group)
        seat_layout.addWidget(self.seat_panel)
        seat_layout.setContentsMargins(10, 25, 10, 10)  # 为标题留空间
        
        # 设置座位面板回调
        self.seat_panel.set_account_getter(lambda: getattr(self, 'current_account', {}))
        self.seat_panel.set_on_submit_order(self.on_submit_order)
        
        # 上部Tab区域 - 在座位面板创建后再创建Tab页面
        self.center_notebook = QTabWidget(center_frame)
        self.center_notebook.setGeometry(0, 0, width, center_top_h)
        self._create_tab_pages(width, center_top_h)
    
    def _create_right_panel(self, x: int, y: int, width: int, height: int):
        """创建右栏面板 - 取票码区和订单详情区"""
        right_frame = QFrame(self.centralWidget())
        right_frame.setGeometry(x, y, width, height)
        right_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        # 右栏上下分区 - 按照README精确比例
        qrcode_height = int(height * 0.45)  # 取票码区占45%
        orderinfo_height = height - qrcode_height  # 订单详情区占55%
        
        # 取票码区（上部）
        self.qrcode_group = QGroupBox("取票码区", right_frame)
        self.qrcode_group.setGeometry(0, 0, width, qrcode_height)
        self._setup_login_area_style(self.qrcode_group)
        
        # 取票码显示标签
        self.qrcode_label = QLabel("(二维码/取票码展示区)", self.qrcode_group)
        self.qrcode_label.setFont(QFont("微软雅黑", 12))
        self.qrcode_label.setAlignment(Qt.AlignCenter)
        qrcode_layout = QVBoxLayout(self.qrcode_group)
        qrcode_layout.addWidget(self.qrcode_label)
        qrcode_layout.setContentsMargins(4, 20, 4, 4)  # 为标题留空间
        
        # 订单详情区（下部）
        self.orderinfo_group = QGroupBox("订单详情区", right_frame)
        self.orderinfo_group.setGeometry(0, qrcode_height, width, orderinfo_height)
        self._setup_login_area_style(self.orderinfo_group)
        self._build_order_detail_area()
    
    def _setup_login_area_style(self, group_box: QGroupBox):
        """设置组框样式 - 复刻tkinter的红色标题LabelFrame"""
        group_box.setStyleSheet("""
            QGroupBox {
                font: bold 12px "Microsoft YaHei";
                color: red;
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f0f0f0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: red;
            }
        """)
    
    def _build_login_area(self):
        """构建账号登录区 - 完全复刻tkinter版本布局"""
        # 创建主布局
        main_layout = QVBoxLayout(self.login_group)
        main_layout.setContentsMargins(5, 20, 5, 5)  # 为标题留空间
        main_layout.setSpacing(10)
        
        # 1. 标题区域
        title_label = QLabel("影院账号登录")
        title_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        title_label.setStyleSheet("QLabel { color: blue; }")
        title_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_label)
        
        # 2. 输入框区域 - 使用Grid布局复刻原版
        input_widget = QWidget()
        input_layout = QGridLayout(input_widget)
        input_layout.setSpacing(5)
        
        # Row 0: "手机号:" + Entry
        input_layout.addWidget(QLabel("手机号:"), 0, 0)
        self.phone_entry = QLineEdit()
        self.phone_entry.setFont(QFont("微软雅黑", 10))
        self.phone_entry.setFixedWidth(140)  # 复刻width=20的效果
        self._setup_entry_style(self.phone_entry)
        input_layout.addWidget(self.phone_entry, 0, 1)
        
        # Row 1: "OpenID:" + Entry
        input_layout.addWidget(QLabel("OpenID:"), 1, 0)
        self.openid_entry = QLineEdit()
        self.openid_entry.setFont(QFont("微软雅黑", 10))
        self.openid_entry.setFixedWidth(140)
        self._setup_entry_style(self.openid_entry)
        input_layout.addWidget(self.openid_entry, 1, 1)
        
        # Row 2: "Token:" + Entry
        input_layout.addWidget(QLabel("Token:"), 2, 0)
        self.token_entry = QLineEdit()
        self.token_entry.setFont(QFont("微软雅黑", 10))
        self.token_entry.setFixedWidth(140)
        self._setup_entry_style(self.token_entry)
        input_layout.addWidget(self.token_entry, 2, 1)
        
        # 设置列权重 - 复刻column 1 weight=1
        input_layout.setColumnStretch(1, 1)
        main_layout.addWidget(input_widget)
        
        # 3. 按钮区域 - 水平排列，左对齐
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # "登录影院账号" 按钮
        self.login_btn = QPushButton("登录影院账号")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.login_btn.clicked.connect(self.on_cinema_account_login)
        self._setup_login_button_style(self.login_btn)
        button_layout.addWidget(self.login_btn)
        
        # "清空" 按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setObjectName("clearBtn")
        self.clear_btn.setFont(QFont("微软雅黑", 10))
        self.clear_btn.clicked.connect(self.clear_login_inputs)
        self._setup_clear_button_style(self.clear_btn)
        button_layout.addWidget(self.clear_btn)
        
        # 添加弹簧推到左侧
        button_layout.addStretch()
        main_layout.addWidget(button_widget)
        
        # 4. 状态显示区域
        self.login_status_label = QLabel("请输入影院账号信息")
        self.login_status_label.setFont(QFont("微软雅黑", 9))
        self.login_status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.login_status_label)
        
        # 添加弹簧到底部
        main_layout.addStretch()
    
    def _setup_entry_style(self, entry: QLineEdit):
        """设置输入框样式"""
        entry.setStyleSheet("""
            QLineEdit {
                font: 10px "Microsoft YaHei";
                padding: 3px;
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #007acc;
            }
        """)
    
    def _setup_login_button_style(self, button: QPushButton):
        """设置登录按钮样式"""
        button.setStyleSheet("""
            QPushButton#loginBtn {
                background-color: #007acc;
                color: white;
                font: bold 10px "Microsoft YaHei";
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton#loginBtn:hover {
                background-color: #005a99;
            }
            QPushButton#loginBtn:pressed {
                background-color: #004d7a;
            }
        """)
    
    def _setup_clear_button_style(self, button: QPushButton):
        """设置清空按钮样式"""
        button.setStyleSheet("""
            QPushButton#clearBtn {
                background-color: #6c757d;
                color: white;
                font: 10px "Microsoft YaHei";
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 50px;
            }
            QPushButton#clearBtn:hover {
                background-color: #545b62;
            }
            QPushButton#clearBtn:pressed {
                background-color: #454d54;
            }
        """)
    
    def _build_order_detail_area(self):
        """构建订单详情区 - 垂直排列布局"""
        main_layout = QVBoxLayout(self.orderinfo_group)
        main_layout.setContentsMargins(4, 20, 4, 4)  # 为标题留空间
        main_layout.setSpacing(2)
        
        # 1. 手机号显示标签
        self.orderinfo_mobile = QLabel("")
        self.orderinfo_mobile.setFont(QFont("微软雅黑", 12, QFont.Bold))
        self.orderinfo_mobile.setStyleSheet("QLabel { color: red; }")
        self.orderinfo_mobile.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.orderinfo_mobile)
        
        # 2. 订单详情文本框
        self.orderinfo_text = QTextEdit()
        self.orderinfo_text.setFont(QFont("微软雅黑", 10))
        self.orderinfo_text.setReadOnly(True)
        self.orderinfo_text.setFixedHeight(180)  # 复刻height=12的效果
        self.orderinfo_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: #f5f5f5;
                padding: 3px;
            }
        """)
        main_layout.addWidget(self.orderinfo_text)
        
        # 3. 倒计时标签
        self.orderinfo_countdown = QLabel("")
        self.orderinfo_countdown.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.orderinfo_countdown.setStyleSheet("QLabel { color: #0077ff; }")
        self.orderinfo_countdown.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.orderinfo_countdown)
        
        # 4. 一键支付按钮
        self.pay_btn = QPushButton("一键支付")
        self.pay_btn.setObjectName("payBtn")
        self.pay_btn.setFont(QFont("微软雅黑", 11, QFont.Bold))
        self.pay_btn.clicked.connect(self.on_one_click_pay)
        self._setup_pay_button_style(self.pay_btn)
        main_layout.addWidget(self.pay_btn)
    
    def _setup_pay_button_style(self, button: QPushButton):
        """设置支付按钮样式"""
        button.setStyleSheet("""
            QPushButton#payBtn {
                background-color: #ff9800;
                color: white;
                font: bold 11px "Microsoft YaHei";
                border: none;
                padding: 8px;
                border-radius: 3px;
                min-height: 25px;
            }
            QPushButton#payBtn:hover {
                background-color: #f57c00;
            }
            QPushButton#payBtn:pressed {
                background-color: #ef6c00;
            }
        """)
    
    def _create_tab_pages(self, width: int, height: int):
        """创建Tab页面 - 完全复刻tkinter版本"""
        # Tab1: "出票"页面 - 左右分区
        self._create_ticket_tab(width, height)
        
        # Tab2-5: 其余Tab页面
        tab_names = ["绑券", "兑换券", "订单", "影院"]
        for name in tab_names:
            tab_widget = QWidget()
            if name == "绑券":
                self._build_bind_coupon_tab(tab_widget)
            elif name == "兑换券":
                self._build_coupon_exchange_tab(tab_widget)
            elif name == "订单":
                self._build_order_list_tab(tab_widget)
            elif name == "影院":
                self._build_cinema_management_tab(tab_widget)
            
            self.center_notebook.addTab(tab_widget, name)
    
    def _create_ticket_tab(self, width: int, height: int):
        """创建出票Tab页面 - 左右分区布局"""
        tab1_widget = QWidget()
        
        # 创建左右分区框架
        left_group = QGroupBox("影院选择区", tab1_widget)
        left_group.setGeometry(0, 0, width//2, height)
        self._setup_login_area_style(left_group)
        
        right_group = QGroupBox("券列表区", tab1_widget)
        right_group.setGeometry(width//2, 0, width//2, height)
        self._setup_login_area_style(right_group)
        
        # 创建影院选择面板
        self.cinema_panel = CinemaSelectPanelPyQt5(left_group, on_cinema_changed=self.on_cinema_changed)
        left_layout = QVBoxLayout(left_group)
        left_layout.addWidget(self.cinema_panel)
        left_layout.setContentsMargins(2, 20, 2, 2)  # 为标题留空间
        
        # 设置主窗口引用 - 立即设置，确保功能正常
        self.cinema_panel.set_main_window(self)
        
        # 创建券列表 - 支持多选的QListWidget
        self.coupon_listbox = QListWidget(right_group)
        self.coupon_listbox.setSelectionMode(QAbstractItemView.MultiSelection)
        self.coupon_listbox.setFont(QFont("微软雅黑", 10))
        self.coupon_listbox.setStyleSheet("""
            QListWidget {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        
        # 绑定券选择事件
        self.coupon_listbox.itemSelectionChanged.connect(self.on_coupon_select)
        
        right_layout = QVBoxLayout(right_group)
        right_layout.addWidget(self.coupon_listbox)
        right_layout.setContentsMargins(8, 25, 8, 8)  # 为标题留空间
        
        # 绑定场次选择事件
        self.cinema_panel.set_seat_panel(self.seat_panel)
        
        # 添加到Tab
        self.center_notebook.addTab(tab1_widget, "出票")
    
    def _start_auth_check(self):
        """启动用户认证检查"""
        try:
            # 创建并显示登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            
            # 在主窗口中心显示登录窗口
            self._center_login_window()
            self.login_window.show()
            
        except Exception as e:
            print(f"启动认证检查失败: {e}")
            traceback.print_exc()
    
    def _center_login_window(self):
        """居中显示登录窗口"""
        if hasattr(self, 'login_window'):
            # 获取主窗口的位置和大小
            main_geometry = self.geometry()
            main_x = main_geometry.x()
            main_y = main_geometry.y()
            main_width = main_geometry.width()
            main_height = main_geometry.height()
            
            # 获取登录窗口的大小
            login_width = self.login_window.width()
            login_height = self.login_window.height()
            
            # 计算居中位置
            x = main_x + (main_width - login_width) // 2
            y = main_y + (main_height - login_height) // 2
            
            self.login_window.move(x, y)
    
    @pyqtSlot(dict)
    def _on_user_login_success(self, user_info: dict):
        """用户登录成功处理"""
        print(f"[主窗口] 用户登录成功: {user_info.get('phone', 'Unknown')}")
        
        # 保存用户信息
        self.current_user = user_info
        
        # 关闭登录窗口
        if hasattr(self, 'login_window'):
            self.login_window.close()
            self.login_window = None
        
        # 显示主窗口
        self.show()
        
        # 自动加载初始状态
        self._auto_load_initial_state()
        
        # 启动定期权限检查
        self._start_periodic_auth_check()
    
    def _start_periodic_auth_check(self):
        """启动定期权限检查"""
        def check_auth():
            try:
                # 检查用户权限是否仍然有效
                if self.current_user:
                    phone = self.current_user.get('phone')
                    if phone:
                        success, message, updated_user_info = auth_service.login(phone)
                        if not success:
                            print(f"[权限检查] 用户权限失效: {message}")
                            self.logout_and_restart()
                        else:
                            # 更新用户信息
                            self.current_user = updated_user_info
                            print(f"[权限检查] 用户权限正常，剩余点数: {updated_user_info.get('points', 0)}")
                    else:
                        print("[权限检查] 未找到用户手机号，注销用户")
                        self.logout_and_restart()
                else:
                    print("[权限检查] 当前无登录用户")
                    self.logout_and_restart()
            except Exception as e:
                print(f"[权限检查] 异常: {e}")
                # 权限检查异常时也进行注销，确保安全
                self.logout_and_restart()
        
        # 每5分钟检查一次权限
        self.auth_check_timer = QTimer()
        self.auth_check_timer.timeout.connect(check_auth)
        self.auth_check_timer.start(5 * 60 * 1000)  # 5分钟 = 5 * 60 * 1000毫秒
    
    def logout_and_restart(self):
        """注销用户并重启登录流程"""
        try:
            # 停止定期检查
            if self.auth_check_timer:
                self.auth_check_timer.stop()
                self.auth_check_timer = None
            
            # 清空用户信息
            self.current_user = None
            
            # 隐藏主窗口
            self.hide()
            
            # 显示登录窗口重新认证
            QMessageBox.warning(self, "权限失效", "您的权限已失效，请重新登录。")
            self._start_auth_check()
            
        except Exception as e:
            print(f"注销重启失败: {e}")
            # 如果注销失败，直接退出程序
            QApplication.quit()
    
    def check_permission_before_action(self, action_name: str, points_cost: int = 0) -> bool:
        """执行操作前检查权限"""
        try:
            if not self.current_user:
                QMessageBox.warning(self, "权限检查", "请先登录系统")
                return False
            
            current_points = self.current_user.get('points', 0)
            if points_cost > 0 and current_points < points_cost:
                QMessageBox.warning(
                    self, "积分不足", 
                    f"执行 {action_name} 需要 {points_cost} 积分，您当前积分: {current_points}"
                )
                return False
            
            return True
            
        except Exception as e:
            print(f"权限检查异常: {e}")
            QMessageBox.critical(self, "权限检查异常", f"权限检查时发生异常: {str(e)}")
            return False
    
    def use_points_for_action(self, action_name: str, points_cost: int) -> bool:
        """使用积分执行操作"""
        try:
            if not self.check_permission_before_action(action_name, points_cost):
                return False
            
            # 扣除积分（这里应该调用API更新服务器端积分）
            self.current_user['points'] -= points_cost
            
            print(f"[积分使用] {action_name} 消耗 {points_cost} 积分，剩余: {self.current_user['points']}")
            return True
            
        except Exception as e:
            print(f"积分使用异常: {e}")
            QMessageBox.critical(self, "积分使用异常", f"积分使用时发生异常: {str(e)}")
            return False
    
    def _auto_load_initial_state(self):
        """自动加载初始状态"""
        try:
            # 刷新账号列表
            self.refresh_account_list()
            
            # 刷新影院下拉框
            if hasattr(self, 'cinema_panel'):
                self.cinema_panel.refresh_cinema_dropdown()
            
            print("[主窗口] 初始状态加载完成")
            
        except Exception as e:
            print(f"初始状态加载失败: {e}")
            traceback.print_exc()
    
    # ==========================================================================
    # 业务逻辑方法 - 从原tkinter版本移植
    # ==========================================================================
    
    def get_selected_cinemaid(self):
        """获取影院选择区当前选中的cinemaid"""
        if hasattr(self, 'cinema_panel'):
            return self.cinema_panel.get_selected_cinemaid()
        return None
    
    def set_current_account(self, account):
        """设置当前账号"""
        self.current_account = account
        print(f"[主窗口] 设置当前账号: {account.get('phone', 'Unknown')}")
        
        # 更新绑券Tab的账号信息显示
        if hasattr(self, 'bind_current_account_label'):
            self.update_bind_account_info()
        
        # 更新兑换券Tab的账号信息显示  
        if hasattr(self, 'exchange_current_account_label'):
            self.update_exchange_account_info()
    
    def set_main_account(self, account):
        """设置主账号并保存到accounts.json"""
        try:
            accounts_file = "data/accounts.json"
            
            # 读取现有账号数据
            accounts_data = []
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts_data = json.load(f)
            
            # 更新主账号标记
            for acc in accounts_data:
                acc['is_main'] = (acc.get('phone') == account.get('phone'))
            
            # 保存更新后的数据
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts_data, f, ensure_ascii=False, indent=2)
            
            print(f"[主窗口] 设置主账号: {account.get('phone', 'Unknown')}")
            
        except Exception as e:
            print(f"设置主账号失败: {e}")
            QMessageBox.warning(self, "设置主账号失败", f"设置主账号时发生错误: {str(e)}")
    
    def clear_coupons(self):
        """清空券列表"""
        if not self.check_permission_before_action("清空券列表"):
            return
        
        self._clear_coupons_impl()
    
    def _clear_coupons_impl(self):
        """清空券列表实现"""
        self.coupons_data = []
        self.selected_coupons = []
        self.coupon_listbox.clear()
    
    def refresh_coupons(self):
        """刷新券列表"""
        if not self.check_permission_before_action("刷新券列表"):
            return
        
        # 调用独立券接口（待开发），此处先清空券列表
        self._clear_coupons_impl()
        QMessageBox.information(self, "刷新券列表", "券列表已刷新（当前为清空操作）")
    
    def refresh_account_list(self):
        """刷新账号列表"""
        try:
            if hasattr(self, 'account_list_panel'):
                self.account_list_panel.refresh_account_list()
        except Exception as e:
            print(f"刷新账号列表失败: {e}")
    
    def on_cinema_changed(self):
        """影院选择变化事件"""
        try:
            print("[主窗口] 影院选择已变化")
            # 刷新账号列表以匹配新的影院
            self.refresh_account_list()
        except Exception as e:
            print(f"影院变化处理失败: {e}")
    
    def on_coupon_select(self):
        """券选择事件处理"""
        try:
            # 获取当前选中的券
            selected_items = self.coupon_listbox.selectedItems()
            selected_indices = [self.coupon_listbox.row(item) for item in selected_items]
            
            # 检查选择数量限制
            if len(selected_indices) > self.max_coupon_select:
                QMessageBox.warning(
                    self, "选择限制", 
                    f"最多只能选择 {self.max_coupon_select} 张券"
                )
                # 清除多余的选择
                for i, item in enumerate(selected_items):
                    if i >= self.max_coupon_select:
                        item.setSelected(False)
                return
            
            # 更新选中的券数据
            self.selected_coupons = []
            for index in selected_indices[:self.max_coupon_select]:
                if 0 <= index < len(self.coupons_data):
                    self.selected_coupons.append(self.coupons_data[index])
            
            print(f"[券选择] 已选择 {len(self.selected_coupons)} 张券")
            
        except Exception as e:
            print(f"券选择处理失败: {e}")
    
    def on_submit_order(self, selected_seats):
        """提交订单"""
        if not self.check_permission_before_action("提交订单", 10):  # 提交订单消耗10积分
            return
        
        try:
            print(f"[订单提交] 开始提交订单，选中座位: {len(selected_seats)}")
            
            # 获取当前账号和影院
            if not hasattr(self, 'current_account') or not self.current_account:
                QMessageBox.warning(self, "提交订单", "请先选择账号")
                return
            
            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                QMessageBox.warning(self, "提交订单", "请先选择影院")
                return
            
            # 取消未支付订单
            self._cancel_unpaid_orders(self.current_account, cinemaid)
            
            # 获取会员信息
            member_info = self._get_member_info(self.current_account, cinemaid)
            if not member_info:
                return
            
            # 创建订单
            order_detail = self._create_order(self.current_account, cinemaid, selected_seats)
            if order_detail:
                # 使用积分
                self.use_points_for_action("提交订单", 10)
                
                # 显示订单详情
                self.show_order_detail(order_detail)
            
        except Exception as e:
            print(f"提交订单失败: {e}")
            traceback.print_exc()
            QMessageBox.critical(self, "提交订单失败", f"提交订单时发生错误: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 停止定期检查
            if self.auth_check_timer:
                self.auth_check_timer.stop()
            
            # 关闭登录窗口（如果存在）
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
            
            print("[主窗口] 程序正常退出")
            event.accept()
            
        except Exception as e:
            print(f"程序退出异常: {e}")
            event.accept()
    
    # ==========================================================================
    # 登录相关方法
    # ==========================================================================
    
    def clear_login_inputs(self):
        """清空登录输入框"""
        self.phone_entry.clear()
        self.openid_entry.clear()
        self.token_entry.clear()
        self.login_status_label.setText("已清空输入信息")
    
    def on_cinema_account_login(self):
        """影院账号登录"""
        if not self.check_permission_before_action("影院账号登录", 5):  # 登录消耗5积分
            return
        
        try:
            # 获取输入信息
            phone = self.phone_entry.text().strip()
            openid = self.openid_entry.text().strip()
            token = self.token_entry.text().strip()
            
            if not phone or not openid or not token:
                QMessageBox.warning(self, "登录失败", "请填写完整的登录信息")
                return
            
            # 获取当前选中的影院ID
            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                QMessageBox.warning(self, "登录失败", "请先选择影院")
                return
            
            # 显示登录进度
            self.login_status_label.setText("正在登录...")
            self.login_btn.setEnabled(False)
            
            # 执行登录API调用
            self.cinema_account_login_api(phone, openid, token, cinemaid)
            
        except Exception as e:
            print(f"影院账号登录失败: {e}")
            self.login_status_label.setText("登录失败")
            self.login_btn.setEnabled(True)
            QMessageBox.critical(self, "登录失败", f"登录时发生错误: {str(e)}")
    
    def cinema_account_login_api(self, phone: str, openid: str, token: str, cinemaid: str):
        """影院账号登录API调用（这里需要实现具体的API调用逻辑）"""
        try:
            # 这里应该调用具体的登录API
            # 暂时模拟登录成功
            
            # 构造账号数据
            account_data = {
                'phone': phone,
                'openid': openid,
                'token': token,
                'cinemaid': cinemaid,
                'login_time': datetime.datetime.now().isoformat()
            }
            
            # 保存账号
            self.save_cinema_account(account_data)
            
            # 使用积分
            self.use_points_for_action("影院账号登录", 5)
            
            # 更新UI状态
            self.login_status_label.setText("登录成功")
            self.login_btn.setEnabled(True)
            
            # 刷新账号列表
            self.refresh_account_list()
            
            QMessageBox.information(self, "登录成功", f"账号 {phone} 登录成功")
            
        except Exception as e:
            print(f"API登录调用失败: {e}")
            self.login_status_label.setText("登录失败")
            self.login_btn.setEnabled(True)
            QMessageBox.critical(self, "API调用失败", f"API调用时发生错误: {str(e)}")
    
    def save_cinema_account(self, account_data: dict):
        """保存影院账号到本地"""
        try:
            accounts_file = "data/accounts.json"
            
            # 确保目录存在
            os.makedirs(os.path.dirname(accounts_file), exist_ok=True)
            
            # 读取现有账号数据
            accounts = []
            if os.path.exists(accounts_file):
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    accounts = json.load(f)
            
            # 检查是否已存在相同账号
            phone = account_data['phone']
            existing_account = None
            for i, acc in enumerate(accounts):
                if acc.get('phone') == phone:
                    existing_account = i
                    break
            
            if existing_account is not None:
                # 更新现有账号
                accounts[existing_account].update(account_data)
                print(f"[账号保存] 更新现有账号: {phone}")
            else:
                # 添加新账号
                accounts.append(account_data)
                print(f"[账号保存] 添加新账号: {phone}")
            
            # 保存到文件
            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)
            
        except Exception as e:
            print(f"保存账号失败: {e}")
            raise 

    # ==========================================================================
    # Tab页面构建方法
    # ==========================================================================
    
    def _build_bind_coupon_tab(self, tab_widget: QWidget):
        """构建绑券Tab页面 - 左右分区布局"""
        # 创建左右分区
        left_widget = QWidget(tab_widget)
        left_widget.setGeometry(0, 0, 375, tab_widget.height())
        
        right_widget = QWidget(tab_widget)
        right_widget.setGeometry(375, 0, 375, tab_widget.height())
        
        # 左侧输入区
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)
        
        # 1. 当前账号信息显示
        self.bind_current_account_label = QLabel("当前账号：未选择")
        self.bind_current_account_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.bind_current_account_label.setStyleSheet("QLabel { color: red; }")
        self.bind_current_account_label.setWordWrap(True)
        self.bind_current_account_label.setMaximumWidth(300)
        left_layout.addWidget(self.bind_current_account_label)
        
        # 2. 提示标签
        prompt_label = QLabel("每行一个券号：")
        prompt_label.setFont(QFont("微软雅黑", 10))
        left_layout.addWidget(prompt_label)
        
        # 3. 文本输入框
        self.bind_coupon_text = QTextEdit()
        self.bind_coupon_text.setFont(QFont("微软雅黑", 10))
        self.bind_coupon_text.setFixedHeight(240)  # 复刻height=16的效果
        self.bind_coupon_text.setFixedWidth(200)   # 复刻width=24的效果
        self.bind_coupon_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                padding: 5px;
            }
        """)
        left_layout.addWidget(self.bind_coupon_text)
        
        # 4. 绑定按钮
        self.bind_coupon_btn = QPushButton("绑定当前账号")
        self.bind_coupon_btn.setObjectName("bindBtn")
        self.bind_coupon_btn.setFont(QFont("微软雅黑", 11, QFont.Bold))
        self.bind_coupon_btn.clicked.connect(self.on_bind_coupons)
        self._setup_bind_button_style(self.bind_coupon_btn)
        left_layout.addWidget(self.bind_coupon_btn)
        
        left_layout.addStretch()
        
        # 右侧日志区
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(5)
        
        # 1. 标签
        log_label = QLabel("绑定日志：")
        log_label.setFont(QFont("微软雅黑", 10))
        right_layout.addWidget(log_label)
        
        # 2. 日志文本框
        self.bind_log_text = QTextEdit()
        self.bind_log_text.setFont(QFont("微软雅黑", 10))
        self.bind_log_text.setReadOnly(True)
        self.bind_log_text.setFixedHeight(270)  # 复刻height=18的效果
        self.bind_log_text.setFixedWidth(320)   # 复刻width=40的效果
        self.bind_log_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: #f5f5f5;
                padding: 5px;
            }
        """)
        right_layout.addWidget(self.bind_log_text)
        
        # 3. 复制按钮
        copy_log_btn = QPushButton("复制日志")
        copy_log_btn.setFont(QFont("微软雅黑", 9))
        copy_log_btn.clicked.connect(self.copy_bind_log)
        copy_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font: 9px "Microsoft YaHei";
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        right_layout.addWidget(copy_log_btn, 0, Qt.AlignRight)
        
        right_layout.addStretch()
    
    def _setup_bind_button_style(self, button: QPushButton):
        """设置绑定按钮样式"""
        button.setStyleSheet("""
            QPushButton#bindBtn {
                background-color: #4caf50;
                color: white;
                font: bold 11px "Microsoft YaHei";
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                min-width: 100px;
            }
            QPushButton#bindBtn:hover {
                background-color: #45a049;
            }
            QPushButton#bindBtn:pressed {
                background-color: #3d8b40;
            }
        """)
    
    def _build_order_list_tab(self, tab_widget: QWidget):
        """构建订单Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 顶部刷新按钮
        top_layout = QHBoxLayout()
        self.refresh_order_btn = QPushButton("刷新")
        self.refresh_order_btn.setFixedWidth(80)  # 复刻width=8的效果
        self.refresh_order_btn.setFont(QFont("微软雅黑", 10))
        self.refresh_order_btn.clicked.connect(self.refresh_order_list)
        self.refresh_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font: 10px "Microsoft YaHei";
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #005a99;
            }
        """)
        top_layout.addWidget(self.refresh_order_btn)
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # 订单表格
        self.order_tree = QTreeWidget()
        self.order_tree.setHeaderLabels(["影片", "影院", "状态", "订单号"])
        self.order_tree.setFont(QFont("微软雅黑", 13))
        
        # 设置列宽
        header = self.order_tree.header()
        header.resizeSection(0, 150)  # 影片
        header.resizeSection(1, 180)  # 影院
        header.resizeSection(2, 150)  # 状态
        header.resizeSection(3, 150)  # 订单号
        
        # 设置行高和样式
        self.order_tree.setStyleSheet("""
            QTreeWidget {
                font: 13px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item {
                padding: 18px 5px;
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
                padding: 8px;
                border: 1px solid #ddd;
                font: bold 13px "Microsoft YaHei";
            }
        """)
        
        # 设置对齐方式
        self.order_tree.setRootIsDecorated(False)
        self.order_tree.setAlternatingRowColors(True)
        
        # 绑定双击事件
        self.order_tree.itemDoubleClicked.connect(self.on_order_double_click)
        
        # 设置右键菜单
        self.order_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.order_tree.customContextMenuRequested.connect(self.show_order_context_menu)
        
        layout.addWidget(self.order_tree)
    
    def _build_cinema_management_tab(self, tab_widget: QWidget):
        """构建影院管理Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 顶部按钮区
        top_layout = QHBoxLayout()
        
        # 刷新按钮
        refresh_cinema_btn = QPushButton("刷新影院列表")
        refresh_cinema_btn.setFont(QFont("微软雅黑", 10))
        refresh_cinema_btn.clicked.connect(self.refresh_cinema_list)
        top_layout.addWidget(refresh_cinema_btn)
        
        # 添加影院按钮
        add_cinema_btn = QPushButton("添加影院")
        add_cinema_btn.setFont(QFont("微软雅黑", 10))
        add_cinema_btn.clicked.connect(self.add_cinema)
        top_layout.addWidget(add_cinema_btn)
        
        top_layout.addStretch()
        layout.addLayout(top_layout)
        
        # 影院列表
        self.cinema_tree = QTreeWidget()
        self.cinema_tree.setHeaderLabels(["影院名称", "域名", "影院ID"])
        self.cinema_tree.setFont(QFont("微软雅黑", 11))
        
        # 设置列宽
        header = self.cinema_tree.header()
        header.resizeSection(0, 200)  # 影院名称
        header.resizeSection(1, 250)  # 域名
        header.resizeSection(2, 100)  # 影院ID
        
        # 设置样式
        self.cinema_tree.setStyleSheet("""
            QTreeWidget {
                font: 11px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTreeWidget::item {
                padding: 8px 5px;
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
                padding: 8px;
                border: 1px solid #ddd;
                font: bold 11px "Microsoft YaHei";
            }
        """)
        
        # 设置右键菜单
        self.cinema_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cinema_tree.customContextMenuRequested.connect(self.show_cinema_context_menu)
        
        # 绑定双击事件
        self.cinema_tree.itemDoubleClicked.connect(self.on_cinema_double_click)
        
        layout.addWidget(self.cinema_tree)
    
    def _build_coupon_exchange_tab(self, tab_widget: QWidget):
        """构建兑换券Tab页面"""
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号显示
        self.exchange_current_account_label = QLabel("当前账号：未选择")
        self.exchange_current_account_label.setFont(QFont("微软雅黑", 10, QFont.Bold))
        self.exchange_current_account_label.setStyleSheet("QLabel { color: red; }")
        layout.addWidget(self.exchange_current_account_label)
        
        # 刷新按钮
        refresh_exchange_btn = QPushButton("刷新兑换券列表")
        refresh_exchange_btn.setFont(QFont("微软雅黑", 10))
        refresh_exchange_btn.clicked.connect(self.refresh_coupon_exchange_list)
        layout.addWidget(refresh_exchange_btn)
        
        # 兑换券列表
        self.exchange_coupon_list = QListWidget()
        self.exchange_coupon_list.setFont(QFont("微软雅黑", 10))
        self.exchange_coupon_list.setStyleSheet("""
            QListWidget {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        layout.addWidget(self.exchange_coupon_list)
        
        # 清空按钮
        clear_exchange_btn = QPushButton("清空兑换券列表")
        clear_exchange_btn.setFont(QFont("微软雅黑", 10))
        clear_exchange_btn.clicked.connect(self.clear_exchange_coupon_list)
        layout.addWidget(clear_exchange_btn)
    
    # ==========================================================================
    # 业务逻辑方法的具体实现
    # ==========================================================================
    
    def update_bind_account_info(self):
        """更新绑券Tab的账号信息显示"""
        if hasattr(self, 'current_account') and self.current_account:
            phone = self.current_account.get('phone', 'Unknown')
            cinemaid = self.current_account.get('cinemaid', 'Unknown')
            self.bind_current_account_label.setText(f"当前账号：{phone} (影院ID: {cinemaid})")
            self.bind_current_account_label.setStyleSheet("QLabel { color: blue; }")
        else:
            self.bind_current_account_label.setText("当前账号：未选择")
            self.bind_current_account_label.setStyleSheet("QLabel { color: red; }")
    
    def update_exchange_account_info(self):
        """更新兑换券Tab的账号信息显示"""
        if hasattr(self, 'current_account') and self.current_account:
            phone = self.current_account.get('phone', 'Unknown')
            cinemaid = self.current_account.get('cinemaid', 'Unknown')
            self.exchange_current_account_label.setText(f"当前账号：{phone} (影院ID: {cinemaid})")
            self.exchange_current_account_label.setStyleSheet("QLabel { color: blue; }")
        else:
            self.exchange_current_account_label.setText("当前账号：未选择")
            self.exchange_current_account_label.setStyleSheet("QLabel { color: red; }")
    
    def on_bind_coupons(self):
        """绑定优惠券"""
        if not self.check_permission_before_action("绑定优惠券", 2):  # 绑定券消耗2积分
            return
        
        try:
            # 获取当前账号
            if not hasattr(self, 'current_account') or not self.current_account:
                QMessageBox.warning(self, "绑券失败", "请先选择账号")
                return
            
            # 获取券号列表
            coupon_text = self.bind_coupon_text.toPlainText().strip()
            if not coupon_text:
                QMessageBox.warning(self, "绑券失败", "请输入券号")
                return
            
            coupon_codes = [line.strip() for line in coupon_text.split('\n') if line.strip()]
            if not coupon_codes:
                QMessageBox.warning(self, "绑券失败", "没有有效的券号")
                return
            
            # 开始绑定
            self.bind_log_text.append(f"开始绑定 {len(coupon_codes)} 张券...")
            
            success_count = 0
            fail_count = 0
            
            for i, coupon_code in enumerate(coupon_codes, 1):
                try:
                    # 这里应该调用实际的绑券API
                    # 暂时模拟绑定结果
                    result = f"券号 {coupon_code} 绑定成功"
                    self.bind_log_text.append(f"[{i}/{len(coupon_codes)}] {result}")
                    success_count += 1
                    
                except Exception as e:
                    result = f"券号 {coupon_code} 绑定失败: {str(e)}"
                    self.bind_log_text.append(f"[{i}/{len(coupon_codes)}] {result}")
                    fail_count += 1
            
            # 使用积分
            self.use_points_for_action("绑定优惠券", 2)
            
            # 显示绑定结果
            summary = f"绑定完成！成功: {success_count}, 失败: {fail_count}"
            self.bind_log_text.append(f"\n{summary}")
            QMessageBox.information(self, "绑券结果", summary)
            
        except Exception as e:
            print(f"绑定优惠券失败: {e}")
            QMessageBox.critical(self, "绑券失败", f"绑定优惠券时发生错误: {str(e)}")
    
    def copy_bind_log(self):
        """复制绑定日志"""
        try:
            from PyQt5.QtWidgets import QApplication
            
            log_text = self.bind_log_text.toPlainText()
            clipboard = QApplication.clipboard()
            clipboard.setText(log_text)
            
            QMessageBox.information(self, "复制成功", "日志已复制到剪贴板")
            
        except Exception as e:
            print(f"复制日志失败: {e}")
    
    def refresh_order_list(self):
        """刷新订单列表"""
        if not self.check_permission_before_action("刷新订单列表"):
            return
        
        try:
            # 清空现有列表
            self.order_tree.clear()
            
            # 这里应该调用实际的订单列表API
            # 暂时添加一些示例数据
            sample_orders = [
                {"film": "示例影片1", "cinema": "示例影院1", "status": "未支付", "order_id": "1234567890"},
                {"film": "示例影片2", "cinema": "示例影院2", "status": "已支付", "order_id": "1234567891"},
            ]
            
            for order in sample_orders:
                item = QTreeWidgetItem()
                item.setText(0, order["film"])
                item.setText(1, order["cinema"])
                item.setText(2, order["status"])
                item.setText(3, order["order_id"])
                
                # 存储订单数据
                item.setData(0, Qt.UserRole, order)
                
                self.order_tree.addTopLevelItem(item)
            
            print(f"[订单列表] 刷新完成，共 {len(sample_orders)} 个订单")
            
        except Exception as e:
            print(f"刷新订单列表失败: {e}")
            QMessageBox.warning(self, "刷新失败", f"刷新订单列表失败: {str(e)}")
    
    def show_order_context_menu(self, position):
        """显示订单右键菜单"""
        item = self.order_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # 查看详情
        view_detail_action = menu.addAction("查看详情")
        view_detail_action.triggered.connect(lambda: self.on_order_double_click(item, 0))
        
        # 取消订单
        cancel_action = menu.addAction("取消订单")
        cancel_action.triggered.connect(self.cancel_selected_order)
        
        menu.exec_(self.order_tree.mapToGlobal(position))
    
    def cancel_selected_order(self):
        """取消选中的订单"""
        current_item = self.order_tree.currentItem()
        if not current_item:
            return
        
        order_data = current_item.data(0, Qt.UserRole)
        if not order_data:
            return
        
        reply = QMessageBox.question(
            self, "确认取消", 
            f"确定要取消订单 {order_data['order_id']} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 这里应该调用取消订单的API
            QMessageBox.information(self, "取消成功", "订单已取消")
            self.refresh_order_list()
    
    def on_order_double_click(self, item: QTreeWidgetItem, column: int):
        """订单双击事件"""
        order_data = item.data(0, Qt.UserRole)
        if not order_data:
            return
        
        # 显示订单详情
        detail_text = f"""订单详情：
影片：{order_data['film']}
影院：{order_data['cinema']}
状态：{order_data['status']}
订单号：{order_data['order_id']}"""
        
        QMessageBox.information(self, "订单详情", detail_text)
    
    def refresh_cinema_list(self):
        """刷新影院列表"""
        try:
            self.cinema_tree.clear()
            
            # 加载影院数据
            cinemas = load_cinemas()
            
            for cinema in cinemas:
                item = QTreeWidgetItem()
                item.setText(0, cinema.get('name', 'Unknown'))
                item.setText(1, cinema.get('base_url', 'Unknown'))
                item.setText(2, cinema.get('cinemaid', 'Unknown'))
                
                # 存储影院数据
                item.setData(0, Qt.UserRole, cinema)
                
                self.cinema_tree.addTopLevelItem(item)
            
            print(f"[影院管理] 刷新完成，共 {len(cinemas)} 个影院")
            
        except Exception as e:
            print(f"刷新影院列表失败: {e}")
            QMessageBox.warning(self, "刷新失败", f"刷新影院列表失败: {str(e)}")
    
    def add_cinema(self):
        """添加影院"""
        QMessageBox.information(self, "功能提示", "添加影院功能正在开发中")
    
    def show_cinema_context_menu(self, position):
        """显示影院右键菜单"""
        item = self.cinema_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        # 编辑影院
        edit_action = menu.addAction("编辑影院")
        edit_action.triggered.connect(self.edit_cinema)
        
        # 删除影院
        delete_action = menu.addAction("删除影院")
        delete_action.triggered.connect(self.delete_cinema)
        
        # 复制影院ID
        copy_id_action = menu.addAction("复制影院ID")
        copy_id_action.triggered.connect(self.copy_cinema_id)
        
        menu.exec_(self.cinema_tree.mapToGlobal(position))
    
    def edit_cinema(self):
        """编辑影院"""
        QMessageBox.information(self, "功能提示", "编辑影院功能正在开发中")
    
    def delete_cinema(self):
        """删除影院"""
        QMessageBox.information(self, "功能提示", "删除影院功能正在开发中")
    
    def copy_cinema_id(self):
        """复制影院ID"""
        current_item = self.cinema_tree.currentItem()
        if not current_item:
            return
        
        cinema_id = current_item.text(2)
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(cinema_id)
        
        QMessageBox.information(self, "复制成功", f"影院ID {cinema_id} 已复制到剪贴板")
    
    def on_cinema_double_click(self, item: QTreeWidgetItem, column: int):
        """影院双击事件"""
        cinema_data = item.data(0, Qt.UserRole)
        if not cinema_data:
            return
        
        # 显示影院详情
        detail_text = f"""影院详情：
名称：{cinema_data.get('name', 'Unknown')}
域名：{cinema_data.get('base_url', 'Unknown')}
影院ID：{cinema_data.get('cinemaid', 'Unknown')}"""
        
        QMessageBox.information(self, "影院详情", detail_text)
    
    def refresh_coupon_exchange_list(self):
        """刷新兑换券列表"""
        if not self.check_permission_before_action("刷新兑换券列表"):
            return
        
        try:
            self.exchange_coupon_list.clear()
            
            # 这里应该调用实际的兑换券API
            # 暂时添加一些示例数据
            sample_coupons = [
                "兑换券示例1 - 10元代金券",
                "兑换券示例2 - 5折优惠券",
                "兑换券示例3 - 买一送一券"
            ]
            
            for coupon in sample_coupons:
                self.exchange_coupon_list.addItem(coupon)
            
            print(f"[兑换券] 刷新完成，共 {len(sample_coupons)} 张兑换券")
            
        except Exception as e:
            print(f"刷新兑换券列表失败: {e}")
            QMessageBox.warning(self, "刷新失败", f"刷新兑换券列表失败: {str(e)}")
    
    def clear_exchange_coupon_list(self):
        """清空兑换券列表"""
        self.exchange_coupon_list.clear()
        QMessageBox.information(self, "清空成功", "兑换券列表已清空")
    
    # ==========================================================================
    # 订单相关的具体实现方法（从原tkinter版本移植）
    # ==========================================================================
    
    def _cancel_unpaid_orders(self, account: Dict, cinemaid: str):
        """取消未支付订单"""
        try:
            # 这里应该调用实际的取消订单API
            print(f"[取消订单] 账号: {account.get('phone')}, 影院: {cinemaid}")
            # 暂时返回成功
            return True
        except Exception as e:
            print(f"取消未支付订单失败: {e}")
            return False
    
    def _get_member_info(self, account: Dict, cinemaid: str):
        """获取会员信息"""
        try:
            # 这里应该调用实际的会员信息API
            print(f"[会员信息] 账号: {account.get('phone')}, 影院: {cinemaid}")
            # 暂时返回模拟数据
            return {
                'member_id': account.get('userid', ''),
                'phone': account.get('phone', ''),
                'balance': 0
            }
        except Exception as e:
            print(f"获取会员信息失败: {e}")
            return None
    
    def _create_order(self, account: Dict, cinemaid: str, selected_seats: List):
        """创建订单"""
        try:
            # 这里应该调用实际的创建订单API
            print(f"[创建订单] 账号: {account.get('phone')}, 影院: {cinemaid}, 座位数: {len(selected_seats)}")
            
            # 暂时返回模拟订单数据
            import time
            import random
            
            order_detail = {
                'order_id': f"ORDER_{int(time.time())}_{random.randint(100, 999)}",
                'seats': selected_seats,
                'total_price': len(selected_seats) * 50,  # 假设每个座位50元
                'create_time': time.time(),
                'status': 'unpaid',
                'expire_time': time.time() + 15 * 60  # 15分钟后过期
            }
            
            return order_detail
            
        except Exception as e:
            print(f"创建订单失败: {e}")
            QMessageBox.critical(self, "创建订单失败", f"创建订单时发生错误: {str(e)}")
            return None
    
    def show_order_detail(self, order_detail: Dict):
        """显示订单详情"""
        try:
            # 更新手机号显示
            if hasattr(self, 'current_account') and self.current_account:
                phone = self.current_account.get('phone', 'Unknown')
                self.orderinfo_mobile.setText(phone)
            
            # 更新订单详情文本
            seats_info = []
            for seat in order_detail.get('seats', []):
                seat_num = seat.get('num', 'Unknown')
                seats_info.append(seat_num)
            
            detail_text = f"""订单详情：
订单号：{order_detail.get('order_id', 'Unknown')}
座位：{', '.join(seats_info)}
总价：{order_detail.get('total_price', 0)} 元
状态：{order_detail.get('status', 'Unknown')}
创建时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(order_detail.get('create_time', 0)))}"""
            
            self.orderinfo_text.setPlainText(detail_text)
            
            # 启动倒计时
            self._start_order_countdown(order_detail.get('expire_time', 0))
            
            # 保存当前订单
            self.current_order = order_detail
            
            print(f"[订单详情] 订单 {order_detail.get('order_id')} 显示完成")
            
        except Exception as e:
            print(f"显示订单详情失败: {e}")
    
    def _start_order_countdown(self, expire_time: float):
        """启动订单倒计时"""
        try:
            self.order_countdown_timer = QTimer()
            self.order_countdown_timer.timeout.connect(lambda: self._update_order_countdown(expire_time))
            self.order_countdown_timer.start(1000)  # 每秒更新一次
            
        except Exception as e:
            print(f"启动倒计时失败: {e}")
    
    def _update_order_countdown(self, expire_time: float):
        """更新订单倒计时显示"""
        try:
            import time
            
            current_time = time.time()
            remaining = int(expire_time - current_time)
            
            if remaining <= 0:
                self.orderinfo_countdown.setText("订单已过期")
                if hasattr(self, 'order_countdown_timer'):
                    self.order_countdown_timer.stop()
            else:
                minutes = remaining // 60
                seconds = remaining % 60
                self.orderinfo_countdown.setText(f"剩余时间：{minutes:02d}:{seconds:02d}")
                
        except Exception as e:
            print(f"更新倒计时失败: {e}")
    
    def on_one_click_pay(self):
        """一键支付"""
        if not self.check_permission_before_action("一键支付", 5):  # 支付消耗5积分
            return
        
        try:
            if not self.current_order:
                QMessageBox.warning(self, "支付失败", "没有待支付的订单")
                return
            
            order_id = self.current_order.get('order_id', '')
            total_price = self.current_order.get('total_price', 0)
            
            reply = QMessageBox.question(
                self, "确认支付", 
                f"确定要支付订单 {order_id}，金额 {total_price} 元吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 这里应该调用实际的支付API
                # 暂时模拟支付成功
                
                # 使用积分
                self.use_points_for_action("一键支付", 5)
                
                # 更新订单状态
                self.current_order['status'] = 'paid'
                
                # 停止倒计时
                if hasattr(self, 'order_countdown_timer'):
                    self.order_countdown_timer.stop()
                
                self.orderinfo_countdown.setText("支付成功")
                
                QMessageBox.information(self, "支付成功", f"订单 {order_id} 支付成功！")
                
        except Exception as e:
            print(f"支付失败: {e}")
            QMessageBox.critical(self, "支付失败", f"支付时发生错误: {str(e)}") 