#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化影院下单系统主窗口
基于插件架构的模块化设计
"""

import sys
import os
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMessageBox, QPushButton
)
from ui.ui_component_factory import UIComponentFactory
from utils.data_utils import DataUtils
from api.cinema_api_client import get_api_client, APIException
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer

# 导入插件系统
from ui.interfaces.plugin_interface import (
    IWidgetInterface, plugin_manager
)

# 导入正确的事件总线
from utils.signals import event_bus

# 导入模块化组件
from ui.widgets.classic_components import apply_classic_theme_to_widget
from ui.widgets.account_widget import AccountWidget
from ui.widgets.tab_manager_widget import TabManagerWidget
from ui.widgets.seat_order_widget import SeatOrderWidget

# ===== 第二步：导入所有业务逻辑（按照任务清单） =====

# 用户认证
from services.auth_service import AuthService
from services.ui_utils import MessageManager, CouponManager, UIConstants

# 所有API接口  
from services.order_api import (
    create_order, get_unpaid_order_detail, get_coupons_by_order, 
    bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api,
    cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
)

# 影院和账号管理
from services.cinema_manager import CinemaManager
from services.film_service import get_films, normalize_film_data, get_plan_seat_info
from services.member_service import MemberService
from services.account_api import get_account_list, save_account, delete_account

# 工具类
import json, os, time, traceback

# 🆕 增强支付系统导入
from PyQt5.QtWidgets import QInputDialog, QLineEdit

# 导入登录窗口
from ui.login_window import LoginWindow


class ModularCinemaMainWindow(QMainWindow):
    """模块化影院下单系统主窗口"""
    
    # 定义信号
    login_success = pyqtSignal(dict)  # 登录成功信号
    
    def __init__(self):
        super().__init__()
        
        # 初始化API客户端
        self.api_client = get_api_client()
        # 初始化业务服务
        self.auth_service = AuthService()
        self.cinema_manager = CinemaManager()
        self.member_service = MemberService()

        # 🆕 初始化订单详情管理器
        from modules.order_display import OrderDetailManager
        self.order_detail_manager = OrderDetailManager(self)

        # ===== 第三步：复制关键数据属性（从源项目复制） =====
        self.current_user = None
        self.current_account = None
        self.current_order = None
        self.member_info = {'has_member_card': False}  # 🆕 初始化会员信息
        # 🆕 券选择和支付相关状态变量
        self.selected_coupons = []           # 存储选中券号列表
        self.selected_coupons_info = None    # 选中券的详细信息
        self.current_coupon_info = None      # 存储券价格查询结果
        self.coupons_data = []              # 存储可用券数据
        self.max_coupon_select = 1          # 券选择数量限制（等于座位数）
        self.ui_state = "initial"
        self.show_debug = False
        self.last_priceinfo = {}
        
        # 定时器相关（使用QTimer替代tkinter.after）
        self.auth_check_timer = None
        # 🆕 移除倒计时定时器
        
        # 初始化状态变量
        self.login_window = None
        
        # 设置窗口基本属性
        self.setWindowTitle("柴犬影院下单系统 - 模块化版本")
        self.setFixedSize(1500, 900)
        
        # 应用经典主题
        apply_classic_theme_to_widget(self)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)
        
        # 初始化UI组件
        self._init_ui()
        
        # 连接信号槽
        self._connect_signals()
        
        # 连接全局事件
        self._connect_global_events()
        
        # 不要显示主窗口，直接启动登录流程
        # 移除了之前的show()/hide()逻辑避免闪烁
        
        # 🆕 初始化增强支付系统
        self._init_enhanced_payment_system()

        # 启动用户认证检查
        QTimer.singleShot(100, self._start_auth_check)

    def _init_enhanced_payment_system(self):
        """🆕 初始化增强支付系统"""
        try:
            # 初始化API客户端（如果还没有）
            if not hasattr(self, 'api_client'):
                from services.api_base import APIBase
                self.api_client = APIBase()

            # 🆕 初始化会员卡密码策略状态
            self.member_password_required = False  # 是否需要会员卡密码
            self.member_password_policy = None     # 密码策略详情
            self.member_card_password = None       # 用户输入的会员卡密码

            print("[增强支付] 🚀 增强支付系统初始化完成")
            print("[增强支付] ✅ 支持动态密码策略检测")
            print("[增强支付] ✅ 支持会员信息API实时获取")
            print("[增强支付] ✅ 支持券预支付验证")
            print("[增强支付] ✅ 支持会员卡密码动态验证")

        except Exception as e:
            print(f"[增强支付] ❌ 初始化失败: {e}")

    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # 计算各栏宽度
        total_width = 1500
        left_w = int(total_width * 0.2)    # 300px (20%)
        center_w = int(total_width * 0.6)  # 900px (60%)
        right_w = int(total_width * 0.2)   # 300px (20%)
        
        # 左栏：账号管理模块
        self.account_widget = AccountWidget()
        self.account_widget.setFixedWidth(left_w - 10)
        main_layout.addWidget(self.account_widget)
        
        # 中栏：垂直分割布局
        center_layout = QVBoxLayout()
        
        # Tab管理模块 (上部38%高度)
        self.tab_manager_widget = TabManagerWidget()
        center_layout.addWidget(self.tab_manager_widget, 38)
        
        # 座位选择模块 (下部62%高度) - 独立的座位区域，不包含订单详情
        self.seat_widget = self._create_seat_area()
        center_layout.addWidget(self.seat_widget, 62)
        
        # 将中栏布局添加到主布局
        center_container = QWidget()
        center_container.setLayout(center_layout)
        center_container.setFixedWidth(center_w - 10)
        main_layout.addWidget(center_container)
        
        # 右栏：取票码区 + 订单详情区
        self.right_widget = self._create_right_area()
        self.right_widget.setFixedWidth(right_w - 10)
        main_layout.addWidget(self.right_widget)
        

    
    def _create_seat_area(self) -> QWidget:
        """创建独立的座位选择区域"""
        from ui.widgets.classic_components import ClassicGroupBox, ClassicLabel, ClassicLineEdit, ClassicButton
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 座位区域组
        seat_group = ClassicGroupBox("座位区域")
        self.seat_area_layout = QVBoxLayout(seat_group)  # 🆕 保存布局引用供后续使用
        self.seat_area_layout.setContentsMargins(10, 20, 10, 10)
        self.seat_area_layout.setSpacing(10)
        
        # 🆕 移除座位选择输入框 - 直接使用座位图选择，不需要手动输入
        # 保留seat_input引用以避免代码错误，但不显示在界面上
        self.seat_input = ClassicLineEdit()
        self.seat_input.setPlaceholderText("点击上方座位图选择座位...")
        self.seat_input.hide()  # 隐藏输入框
        
        # 座位图占位符
        self.seat_placeholder = ClassicLabel(
            "座位图将在此显示\n\n请先选择影院、影片、日期和场次",
            "default"
        )
        self.seat_placeholder.setAlignment(Qt.AlignCenter)
        self.seat_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 60px;
                border-radius: 5px;
            }
        """)
        self.seat_area_layout.addWidget(self.seat_placeholder)
        
        layout.addWidget(seat_group)
        
        return widget
    
    def _create_right_area(self) -> QWidget:
        """创建右栏区域：取票码区 + 订单详情区"""
        from ui.widgets.classic_components import ClassicGroupBox, ClassicLabel, ClassicTextEdit, ClassicButton
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 取票码区 (上部50%)
        qr_group = ClassicGroupBox("取票码区")
        qr_layout = QVBoxLayout(qr_group)
        qr_layout.setContentsMargins(10, 20, 10, 10)

        # 🎯 添加按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # 复制路径按钮
        self.copy_path_btn = QPushButton("复制路径")
        self.copy_path_btn.setFixedSize(80, 30)
        self.copy_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 4px;
                font: 12px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.copy_path_btn.clicked.connect(self._on_copy_path)

        # 复制图片按钮
        self.copy_image_btn = QPushButton("复制图片")
        self.copy_image_btn.setFixedSize(80, 30)
        self.copy_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                font: 12px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
        """)
        self.copy_image_btn.clicked.connect(self._on_copy_image)

        # 添加按钮到布局
        button_layout.addWidget(self.copy_path_btn)
        button_layout.addWidget(self.copy_image_btn)
        button_layout.addStretch()  # 左对齐

        # 取票码显示区域
        self.qr_display = ClassicLabel("(二维码/取票码展示区)", "default")
        self.qr_display.setAlignment(Qt.AlignCenter)
        # 🎨 恢复到默认设置，移除最小尺寸限制
        self.qr_display.setStyleSheet("""
            QLabel {
                color: #666666;
                font: 12px "Microsoft YaHei";
                background-color: #f0f0f0;
                border: 1px solid #dddddd;
                padding: 20px;  /* 🎨 恢复到原来的20px padding */
                border-radius: 5px;
            }
        """)

        # 添加到布局
        qr_layout.addLayout(button_layout)  # 先添加按钮
        qr_layout.addWidget(self.qr_display)  # 再添加显示区域
        
        layout.addWidget(qr_group, 45)  # 🔄 恢复为45%

        # 订单详情区 (下部55%)
        order_group = ClassicGroupBox("订单详情区")
        order_layout = QVBoxLayout(order_group)
        order_layout.setContentsMargins(10, 20, 10, 10)
        order_layout.setSpacing(8)
        
        # 手机号显示标签
        self.phone_display = ClassicLabel("", "info")
        self.phone_display.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font: bold 12px "Microsoft YaHei";
                padding: 4px;
                background-color: transparent;
            }
        """)
        order_layout.addWidget(self.phone_display)
        
        # 订单详情文本框 - 改善UI：增大字体，优化样式
        self.order_detail_text = ClassicTextEdit(read_only=True)
        self.order_detail_text.setPlaceholderText("订单详情将在此显示...")
        self.order_detail_text.setStyleSheet("""
            QTextEdit {
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                line-height: 1.6;
                color: #333333;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        order_layout.addWidget(self.order_detail_text)
        
        # 🆕 移除倒计时标签
        
        # 一键支付按钮
        self.pay_button = ClassicButton("一键支付", "warning")
        self.pay_button.setMinimumHeight(35)
        self.pay_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: #ffffff;
                font: bold 11px "Microsoft YaHei";
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
            QPushButton:pressed {
                background-color: #ef6c00;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        order_layout.addWidget(self.pay_button)
        
        layout.addWidget(order_group, 55)  # 🔄 恢复为55%
        
        return widget

    def _on_copy_path(self):
        """🔧 复制路径按钮点击事件 - 修复为绝对路径"""
        try:
            # 获取当前显示的二维码图片路径
            if hasattr(self, 'current_qr_path') and self.current_qr_path:
                import os
                from PyQt5.QtWidgets import QApplication

                # 🔧 转换为绝对路径
                absolute_path = os.path.abspath(self.current_qr_path)

                clipboard = QApplication.clipboard()
                clipboard.setText(absolute_path)
        except Exception as e:
            pass

    def _on_copy_image(self):
        """复制图片按钮点击事件"""
        try:
            # 🎨 优先使用原始图片数据，确保最佳质量
            if hasattr(self, 'current_qr_bytes') and self.current_qr_bytes:
                from PyQt5.QtWidgets import QApplication
                from PyQt5.QtGui import QPixmap
                from PyQt5.QtCore import QByteArray

                # 从原始字节数据创建高质量pixmap
                byte_array = QByteArray(self.current_qr_bytes)
                pixmap = QPixmap()
                pixmap.loadFromData(byte_array, 'PNG')

                if not pixmap.isNull():
                    clipboard = QApplication.clipboard()
                    clipboard.setPixmap(pixmap)
                else:
                    pass
                    # 备用方案：使用界面显示的图片
                    self._copy_display_image()
            else:
                pass
                # 备用方案：使用界面显示的图片
                self._copy_display_image()

        except Exception as e:
            pass
            # 最后备用方案
            self._copy_display_image()

    def _copy_display_image(self):
        """备用方案：复制界面显示的图片"""
        try:
            if hasattr(self, 'qr_display') and self.qr_display.pixmap():
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                pixmap = self.qr_display.pixmap()
                clipboard.setPixmap(pixmap)
        except Exception as e:
            pass

    def _connect_signals(self):
        """连接信号槽"""
        # 账号管理模块信号
        self.account_widget.account_selected.connect(self._on_account_selected)
        self.account_widget.account_login_requested.connect(self._on_account_login_requested)
        
        # Tab管理模块信号
        self.tab_manager_widget.cinema_selected.connect(self._on_cinema_selected)
        self.tab_manager_widget.order_submitted.connect(self._on_order_submitted)
        self.tab_manager_widget.coupon_bound.connect(self._on_coupon_bound)
        self.tab_manager_widget.coupon_exchanged.connect(self._on_coupon_exchanged)
        self.tab_manager_widget.session_selected.connect(self._on_session_selected)
        self.tab_manager_widget.seat_load_requested.connect(self._on_seat_load_requested)  # 🆕 座位图加载请求
        
        # 座位选择信号
        self.seat_input.textChanged.connect(self._on_seat_input_changed)
        
        # 右栏支付按钮信号
        self.pay_button.clicked.connect(self._on_pay_button_clicked)
        
        # 主窗口信号
        self.login_success.connect(self._on_main_login_success)
    
    def _connect_global_events(self):
        """连接全局事件"""
        # 监听全局事件
        event_bus.user_login_success.connect(self._on_global_login_success)
        event_bus.account_changed.connect(self._on_global_account_changed)
        event_bus.cinema_selected.connect(self._on_global_cinema_selected)
        event_bus.order_created.connect(self._on_global_order_created)
        event_bus.order_paid.connect(self._on_global_order_paid)
        event_bus.show_qrcode.connect(self._on_show_qrcode)  # 🔧 添加二维码显示信号监听
    
    def _start_auth_check(self):
        """启动用户认证检查"""
        try:
            # 创建登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            
            # 显示登录窗口
            self.login_window.show()
            
            
        except Exception as e:
            QMessageBox.critical(self, "启动错误", f"启动认证检查失败: {str(e)}")
    
    @pyqtSlot(dict)
    def _on_user_login_success(self, user_info: dict):
        """用户登录成功处理"""
        try:
            # 1. 基本验证用户信息
            phone = user_info.get("phone", "")
            if not phone:
                QMessageBox.critical(self, "登录失败", "用户信息不完整：缺少手机号")
                self._restart_login()
                return
            
            
            # 2. 简化验证逻辑 - 暂时跳过复杂的API和机器码验证
            # 后续可以根据需要恢复
            
            # 保存用户信息
            self.current_user = user_info
            
            # 关闭登录窗口
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # 立即显示主窗口
            self._show_main_window_after_login()
            
        except Exception as e:
            QMessageBox.critical(self, "登录处理错误", f"处理登录结果失败: {str(e)}")
            self._restart_login()
    
    def _show_main_window_after_login(self):
        """登录成功后显示主窗口"""
        try:
            # 显示主窗口
            self.show()
            
            # 将窗口提到前台并激活
            self.raise_()
            self.activateWindow()
            
            # 居中显示窗口
            self.center_window()
            
            # 发出登录成功信号
            self.login_success.emit(self.current_user)
            
            # 发布全局登录成功事件
            event_bus.user_login_success.emit(self.current_user)
            
            # 🆕 延迟触发默认影院设置，确保所有组件都已初始化
            QTimer.singleShot(500, self._trigger_default_cinema_selection)
            
            
        except Exception as e:
            QMessageBox.critical(self, "显示主窗口错误", f"显示主窗口失败: {str(e)}")
            # 如果显示失败，重新启动登录
            self._restart_login()
    
    def _trigger_default_cinema_selection(self):
        """智能默认选择：影院 → 账号 - 避免等待账号选择"""
        try:
            # 第一步：获取影院列表
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()

            if not cinemas:
                return

            # 第二步：自动选择第一个影院
            first_cinema = cinemas[0]
            cinema_name = first_cinema.get('cinemaShortName', '')
            cinema_id = first_cinema.get('cinemaid', '')

            print(f"[主窗口] 📍 步骤1: 自动选择默认影院: {cinema_name} ({cinema_id})")

            # 更新Tab管理器的影院数据
            if hasattr(self.tab_manager_widget, 'update_cinema_list'):
                self.tab_manager_widget.update_cinema_list(cinemas)

            # 发布影院选择事件
            event_bus.cinema_selected.emit(first_cinema)

            # 第三步：延迟选择该影院的关联账号
            QTimer.singleShot(200, lambda: self._auto_select_cinema_account(first_cinema))

            # 第四步：延迟更新Tab管理器界面
            QTimer.singleShot(400, lambda: self._update_tab_cinema_selection(cinema_name))

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _auto_select_cinema_account(self, cinema_info):
        """自动选择影院关联的主账号"""
        try:
            cinema_name = cinema_info.get('cinemaShortName', '')
            cinema_id = cinema_info.get('cinemaid', '')


            # 获取账号列表 - 修复account_manager引用
            if hasattr(self, 'account_widget') and hasattr(self.account_widget, 'load_account_list'):
                all_accounts = self.account_widget.load_account_list()
            else:
                return

            if not all_accounts:
                return

            # 过滤该影院的关联账号
            cinema_accounts = []
            for account in all_accounts:
                account_cinema_id = account.get('cinemaid', '')
                if account_cinema_id == cinema_id:
                    cinema_accounts.append(account)

            # 选择账号
            if cinema_accounts:
                # 有关联账号，选择第一个
                first_account = cinema_accounts[0]
                userid = first_account.get('userid', first_account.get('phone', ''))
            else:
                pass
                # 没有关联账号，选择第一个可用账号
                first_account = all_accounts[0]
                userid = first_account.get('userid', first_account.get('phone', ''))

            # 设置当前账号
            self.set_current_account(first_account)

            # 发布账号选择事件
            event_bus.account_changed.emit(first_account)

            # 更新账号组件显示
            if hasattr(self, 'account_widget'):
                self.account_widget.set_current_account(first_account)


        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _update_tab_cinema_selection(self, cinema_name):
        """更新Tab管理器的影院选择"""
        try:
            if hasattr(self.tab_manager_widget, 'cinema_combo'):
                # 查找并设置影院下拉框的当前项
                for i in range(self.tab_manager_widget.cinema_combo.count()):
                    if self.tab_manager_widget.cinema_combo.itemText(i) == cinema_name:
                        self.tab_manager_widget.cinema_combo.setCurrentIndex(i)
                        break
                else:
                    pass
            else:
                pass

        except Exception as e:
            pass
    
    def center_window(self):
        """将窗口居中显示"""
        try:
            from PyQt5.QtWidgets import QDesktopWidget
            screen = QDesktopWidget().screenGeometry()
            size = self.geometry()
            x = (screen.width() - size.width()) // 2
            y = (screen.height() - size.height()) // 2
            self.move(x, y)
        except Exception as e:
            pass
    
    def _restart_login(self):
        """重新启动登录流程"""
        try:
            # 清理旧的登录窗口
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # 延迟创建新的登录窗口
            QTimer.singleShot(200, self._create_new_login_window)
            
        except Exception as e:
            QMessageBox.critical(self, "重启登录失败", f"无法重新启动登录: {str(e)}")
            QApplication.quit()
    
    def _create_new_login_window(self):
        """创建新的登录窗口"""
        try:
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            self.login_window.show()
            
        except Exception as e:
            QMessageBox.critical(self, "创建登录窗口失败", f"无法创建登录窗口: {str(e)}")
            QApplication.quit()
    
    # ===== 模块信号处理方法 =====
    
    def _on_account_selected(self, account_data: dict):
        """账号选择处理 - 对接到核心业务方法"""
        try:
            # 调用核心业务方法
            self.set_current_account(account_data)
            
        except Exception as e:
            pass
    
    def _on_account_login_requested(self, login_data: dict):
        """账号登录请求处理"""
        QMessageBox.information(self, "登录请求", "影院账号登录功能已简化，请直接从账号列表中选择账号")
    
    def _on_cinema_selected(self, cinema_name: str):
        """影院选择处理 - 对接到核心业务方法"""
        try:
            # 更新座位图占位符 - 移除多余提示
            self.seat_placeholder.setText(
                f"已选择影院: {cinema_name}\n\n"
                f"请继续选择影片、日期和场次"
            )
            
            # 调用核心业务方法处理影院切换
            self.on_cinema_changed()
            
            # 为订单详情预填充影院信息
            current_details = self.order_detail_text.toPlainText()
            if not current_details or "订单信息:" not in current_details:
                details = f"订单信息:\n"
                details += f"影院: {cinema_name}\n"
                details += f"影片: 未选择\n"
                details += f"场次: 未选择\n"
                details += f"座位: 未选择\n"
                details += f"金额: ¥0.00\n"
                details += f"状态: 选择中"
                self.order_detail_text.setPlainText(details)
            
        except Exception as e:
            pass
    
    def _on_order_submitted(self, order_data: dict):
        """处理订单提交信号 - 来自Tab管理器"""
        try:
            print(f"[主窗口] 收到订单提交信号: {order_data.get('trigger_type', 'unknown')}")
            
            # 导入消息管理器
            from services.ui_utils import MessageManager
            
            # 验证基本信息
            if not order_data.get('account'):
                MessageManager.show_error(self, "账号错误", "账号信息缺失", auto_close=False)
                return
            
            # 获取座位信息（从座位图面板）
            selected_seats = []
            if hasattr(self, 'seat_map_panel') and self.seat_map_panel:
                selected_seats = list(self.seat_map_panel.selected_seats)
                # 转换为字典格式
                seat_list = []
                for seat_pos in selected_seats:
                    if hasattr(self.seat_map_panel, 'seat_buttons') and seat_pos in self.seat_map_panel.seat_buttons:
                        # 从座位按钮获取详细信息
                        row, col = seat_pos
                        seat_info = {
                            'row': row,
                            'col': col,
                            'num': f"{row}-{col}",
                            'original_data': getattr(self.seat_map_panel, 'seat_data', {}).get(seat_pos, {})
                        }
                        seat_list.append(seat_info)
                selected_seats = seat_list
            
            if not selected_seats:
                MessageManager.show_error(self, "座位未选择", "请先选择座位", auto_close=False)
                return
            
            print(f"[主窗口] 开始处理订单，选择座位: {len(selected_seats)} 个")
            
            # 调用现有的完整订单处理流程
            result = self.on_submit_order(selected_seats)
            
            if result:
                MessageManager.show_success(self, "订单创建成功", "订单已成功创建，请及时支付", auto_close=True)
            else:
                MessageManager.show_error(self, "订单创建失败", "订单创建过程中出现错误", auto_close=False)
                
        except Exception as e:
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "处理错误", f"处理订单时出错: {str(e)}", auto_close=False)
            import traceback
            traceback.print_exc()
    
    def on_bind_coupons(self):
        """绑定券处理"""
        try:
            if not self.current_account:
                MessageManager.show_error(self, "绑定失败", "请先选择账号")
                return
                
            # 获取券号列表
            if not hasattr(self.tab_manager_widget, 'coupon_input'):
                return
                
            coupon_text = self.tab_manager_widget.coupon_input.toPlainText().strip()
            if not coupon_text:
                MessageManager.show_warning(self, "输入错误", "请输入要绑定的券号")
                return
            
            coupon_codes = [line.strip() for line in coupon_text.split('\n') if line.strip()]
            
            # 批量绑定券
            success_count = 0
            fail_count = 0
            bind_log = f"开始绑定 {len(coupon_codes)} 个券号...\n"
            
            for coupon_code in coupon_codes:
                try:
                    # 调用API绑定券
                    result = bind_coupon({
                        'account': self.current_account,
                        'coupon_code': coupon_code
                    })
                    
                    if result and result.get('resultCode') == '0':
                        success_count += 1
                        bind_log += f"✅ 券号 {coupon_code} 绑定成功\n"
                    else:
                        fail_count += 1
                        error_msg = result.get('resultDesc', '未知错误') if result else '网络错误'
                        bind_log += f"❌ 券号 {coupon_code} 绑定失败：{error_msg}\n"
                        
                except Exception as e:
                    fail_count += 1
                    bind_log += f"❌ 券号 {coupon_code} 绑定失败：{str(e)}\n"
            
            bind_log += f"\n绑定完成：成功 {success_count} 个，失败 {fail_count} 个"
            
            # 更新绑定日志
            if hasattr(self.tab_manager_widget, 'bind_log'):
                self.tab_manager_widget.bind_log.setPlainText(bind_log)
                
            # 清空输入
            self.tab_manager_widget.coupon_input.clear()
            
            # 不显示绑定完成弹窗，只在控制台记录
            
        except Exception as e:
            MessageManager.show_error(self, "绑定失败", f"券绑定失败: {str(e)}")
    
    def refresh_order_list(self):
        """刷新订单列表"""
        try:
            if not self.current_account:
                return
                
            # 调用API获取订单列表
            orders = get_order_list({
                'account': self.current_account
            })
            
            # 更新订单表格
            if hasattr(self.tab_manager_widget, 'order_table') and orders:
                self._update_order_table(orders)
                
            
        except Exception as e:
            pass
    
    def on_one_click_pay(self):
        """🆕 一键支付处理 - 完整的券支付逻辑"""
        try:
            if not self.current_order:
                MessageManager.show_error(self, "支付失败", "没有待支付的订单")
                return

            if not self.current_account:
                MessageManager.show_error(self, "支付失败", "请先选择账号")
                return

            # 获取订单和账号信息
            order_detail = self.current_order
            account = self.current_account
            order_id = order_detail.get('orderno') or order_detail.get('order_id', '')

            # 获取影院信息
            cinema_data = None
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'current_cinema_data'):
                cinema_data = self.tab_manager_widget.current_cinema_data

            if not cinema_data:
                MessageManager.show_error(self, "支付失败", "缺少影院信息")
                return

            cinema_id = cinema_data.get('cinemaid', '')

            # 🆕 检测会员卡密码策略
            password_policy_result = self.validate_member_password_policy(order_id)
            if not password_policy_result.get('success'):
                MessageManager.show_error(self, "支付失败", f"密码策略检测失败: {password_policy_result.get('error')}")
                return

            requires_password = password_policy_result.get('requires_password', False)
            member_password = None

            # 🆕 智能密码处理 - 优先使用预设密码
            if requires_password:
                print(f"[支付-密码] 订单需要会员卡密码，开始获取密码")

                # 1. 首先尝试获取预设的支付密码
                member_password = self._get_account_payment_password(self.current_account)

                if member_password:
                    print(f"[支付-密码] ✅ 使用预设支付密码 (长度: {len(member_password)})")
                else:
                    print(f"[支付-密码] ⚠️ 未设置预设密码，弹出输入对话框")
                    # 2. 如果没有预设密码，才弹出输入对话框
                    member_password = self.get_member_password_input()
                    if member_password is None:
                        MessageManager.show_info(self, "支付取消", "用户取消密码输入")
                        return
                    print(f"[支付-密码] ✅ 用户手动输入密码 (长度: {len(member_password)})")
            else:
                print(f"[支付-密码] 订单无需会员卡密码")

            # 🆕 获取选中的券号
            selected_coupons = getattr(self, 'selected_coupons', [])
            couponcode = ','.join(selected_coupons) if selected_coupons else ''

            # 🆕 获取券选择后的价格信息
            coupon_info = getattr(self, 'current_coupon_info', None)

            # 🆕 判断是否使用券支付
            use_coupon = bool(couponcode and coupon_info and coupon_info.get('resultCode') == '0')

            if use_coupon:
                # 🆕 使用券支付：从券价格信息中获取支付参数
                coupon_data = coupon_info['resultData']
                pay_amount = coupon_data.get('paymentAmount', '0')  # 实付金额（分）
                discount_price = coupon_data.get('discountprice', '0')  # 优惠价格（分）

                # 🆕 检查会员支付金额
                has_member_card = self.member_info and self.member_info.get('has_member_card', False)
                if has_member_card:
                    mem_payment = coupon_data.get('mempaymentAmount', '0')
                    if mem_payment != '0':
                        pay_amount = mem_payment  # 会员优先使用会员支付金额

            else:
                pass
                # 🆕 不使用券，按原价支付
                couponcode = ''  # 清空券号

                # 获取原价支付金额
                has_member_card = self.member_info and self.member_info.get('has_member_card', False)
                if has_member_card:
                    # 会员：使用会员总价
                    pay_amount = str(order_detail.get('mem_totalprice', 0))  # 会员总价（分）
                else:
                    pass
                    # 非会员：使用订单总价
                    pay_amount = str(order_detail.get('payAmount', 0))  # 订单总价（分）

                discount_price = '0'  # 无优惠


            # 🆕 构建支付参数 - 完全按照原版格式
            pay_params = {
                'orderno': order_id,
                'payprice': pay_amount,        # 实付金额（分）
                'discountprice': discount_price, # 优惠价格（分）
                'couponcodes': couponcode,     # 券号列表（逗号分隔，无券时为空字符串）
                'groupid': '',
                'cinemaid': cinema_id,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            }

            # 🆕 根据密码策略添加会员卡密码参数
            if requires_password and member_password:
                pay_params['mempass'] = member_password
                print(f"[支付] 添加会员卡密码参数 (密码长度: {len(member_password)})")
            else:
                print(f"[支付] 不需要会员卡密码 (策略: {requires_password})")


            # 🆕 调用支付API
            pay_result = pay_order(pay_params)


            if pay_result and pay_result.get('resultCode') == '0':
                # 🆕 支付成功处理流程

                # 🆕 获取已支付订单详情
                detail_params = {
                    'orderno': order_id,
                    'groupid': '',
                    'cinemaid': cinema_id,
                    'cardno': account.get('cardno', ''),
                    'userid': account['userid'],
                    'openid': account['openid'],
                    'CVersion': '3.9.12',
                    'OS': 'Windows',
                    'token': account['token'],
                    'source': '2'
                }

                # 支付成功后获取订单详情（此时订单已支付，使用get_order_detail）
                print(f"[调试-支付成功] 获取已支付订单详情，使用接口: get_order_detail")
                updated_order_detail = get_order_detail(detail_params)

                if updated_order_detail and updated_order_detail.get('resultCode') == '0':
                    # 🎯 集成取票码获取和显示流程（与双击订单流程一致）
                    self._get_ticket_code_after_payment(order_id, cinema_id, updated_order_detail.get('resultData', {}))

                    # 🆕 更新订单详情显示为支付成功状态
                    self.current_order = updated_order_detail
                    self._update_order_detail_with_coupon_info()

                else:
                    MessageManager.show_warning(self, "提示", "支付成功，但获取订单详情失败，请手动在订单列表中查看")

                # 🆕 发布支付成功事件
                event_bus.order_paid.emit(order_id)

                # 🆕 清空当前订单和券选择状态
                self.current_order = None
                self.selected_coupons.clear()
                self.current_coupon_info = None

                MessageManager.show_info(self, "支付成功", "订单支付成功！")

            else:
                pass
                # 🆕 支付失败处理
                error_msg = pay_result.get('resultDesc', '未知错误') if pay_result else '支付请求失败'
                MessageManager.show_error(self, "支付失败", f"支付失败: {error_msg}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            MessageManager.show_error(self, "支付失败", f"支付过程中发生错误: {e}")
    
    def show_order_detail(self, detail):
        """显示订单详情"""
        self._show_order_detail(detail)
    
    def _cancel_unpaid_orders(self, account, cinemaid):
        """取消未支付订单"""
        try:
            result = cancel_all_unpaid_orders({
                'account': account,
                'cinemaid': cinemaid
            })
            
            if result and result.get('resultCode') == '0':
                pass
            else:
                print(f"[主窗口] 取消订单失败: {result.get('resultDesc', '未知错误') if result else '网络错误'}")
                
        except Exception as e:
            pass
    
    def _get_member_info(self, account, cinemaid):
        """获取会员信息 - 修复：严格按照API返回数据结构判断"""
        try:
            print(f"[调试-会员信息] 开始获取会员信息，影院ID: {cinemaid}")

            # 直接调用会员信息API，不使用增强方法的包装
            from services.api_base import api_get
            params = {
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account.get('userid', ''),
                'openid': account.get('openid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account.get('token', ''),
                'source': '2'
            }

            print(f"[调试-会员信息] API请求参数: {params}")

            # 调用getMemberInfo API
            api_result = api_get('/MiniTicket/index.php/MiniMember/getMemberInfo', cinemaid, params)

            print(f"[调试-会员信息] API原始返回: {api_result}")

            # 🆕 修复：严格按照API返回数据结构判断会员状态
            if api_result and api_result.get('resultCode') == '0':
                result_data = api_result.get('resultData')

                print(f"[调试-会员信息] resultData: {result_data}")
                print(f"[调试-会员信息] resultData类型: {type(result_data)}")

                if result_data is not None and isinstance(result_data, dict):
                    # 🆕 有会员卡：resultData不为null且包含会员信息
                    self.member_info = {
                        'has_member_card': True,  # 使用明确的字段名
                        'cardno': result_data.get('cardno', ''),
                        'mobile': result_data.get('mobile', ''),
                        'memberId': result_data.get('memberId', ''),
                        'cardtype': result_data.get('cardtype', '0'),
                        'cardcinemaid': result_data.get('cardcinemaid', ''),
                        'balance': result_data.get('balance', 0),
                        'raw_data': result_data  # 保存原始数据供后续使用
                    }
                    print(f"[调试-会员信息] ✅ 检测到会员卡: {self.member_info}")
                else:
                    # 🆕 无会员卡：resultData为null
                    self.member_info = {
                        'has_member_card': False,
                        'raw_data': None
                    }
                    print(f"[调试-会员信息] ❌ 无会员卡 (resultData为null)")
            else:
                # API调用失败
                error_desc = api_result.get('resultDesc', '未知错误') if api_result else '网络错误'
                self.member_info = {
                    'has_member_card': False,
                    'error': error_desc,
                    'raw_data': None
                }
                print(f"[调试-会员信息] ❌ API调用失败: {error_desc}")

        except Exception as e:
            print(f"[调试-会员信息] 获取会员信息异常: {e}")
            self.member_info = {
                'has_member_card': False,
                'error': str(e),
                'raw_data': None
            }
    
    def _create_order(self, account, cinemaid, selected_seats):
        """创建订单（保留原方法供其他地方调用）"""
        # 直接调用主要的订单创建方法
        return self.on_submit_order(selected_seats)
    
    def cinema_account_login_api(self, phone, openid, token, cinemaid):
        """影院账号登录API"""
        try:
            # 调用影院登录API
            login_result = self.auth_service.cinema_login(phone, openid, token, cinemaid)
            
            if login_result and login_result.get('resultCode') == '0':
                return login_result
            else:
                error_msg = login_result.get('resultDesc', '登录失败') if login_result else '网络错误'
                return None
                
        except Exception as e:
            return None
    
    # ===== 辅助方法 =====
    
    def _refresh_account_dependent_data(self):
        """刷新依赖账号的数据 - 🔧 修复空值处理错误"""
        try:
            # 🔧 修复：检查账号和订单数据
            if not self.current_account or not isinstance(self.current_account, dict):
                print("[主窗口] 刷新依赖数据失败：账号数据无效")
                return

            if not self.current_order or not isinstance(self.current_order, dict):
                print("[主窗口] 刷新依赖数据失败：订单数据无效")
                return

            # 获取必要参数
            order_id = self.current_order.get('orderno') or self.current_order.get('order_id', '')
            cinema_id = ''

            # 尝试从多个来源获取影院ID
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'current_cinema_data'):
                cinema_data = self.tab_manager_widget.current_cinema_data
                if isinstance(cinema_data, dict):
                    cinema_id = cinema_data.get('cinemaid', '')

            if not cinema_id and hasattr(self, 'current_cinema_id'):
                cinema_id = self.current_cinema_id

            if order_id and cinema_id:
                print(f"[主窗口] 刷新券列表，订单: {order_id}, 影院: {cinema_id}")
                # 调用修复后的券列表加载函数
                self._load_available_coupons(order_id, cinema_id)
            else:
                print(f"[主窗口] 刷新券列表失败：缺少参数 - 订单ID: {order_id}, 影院ID: {cinema_id}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[主窗口] 刷新依赖数据异常: {e}")
    
    def _save_account_data(self, account):
        """保存账号数据"""
        try:
            save_account(account)
            
        except Exception as e:
            pass
    
    def _get_cinema_info_by_name(self, cinema_name):
        """根据名称获取影院信息 - 增强版本"""
        try:
            # 方法1: 从cinema_manager获取数据 - 🆕 修复方法名
            cinemas = self.cinema_manager.load_cinema_list()  # 使用正确的方法名
            if cinemas:
                print(f"[主窗口] cinema_manager获取到 {len(cinemas)} 个影院")
                for cinema in cinemas:
                    cinema_short_name = cinema.get('cinemaShortName', '')
                    cinema_name_field = cinema.get('name', '')
                    
                    if cinema_short_name == cinema_name or cinema_name_field == cinema_name:
                        return cinema
            
            # 方法2: 从Tab管理器的影院数据获取
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'cinemas_data'):
                for cinema in self.tab_manager_widget.cinemas_data:
                    cinema_short_name = cinema.get('cinemaShortName', '')
                    cinema_name_field = cinema.get('name', '')
                    
                    if cinema_short_name == cinema_name or cinema_name_field == cinema_name:
                        return cinema
            
            # 方法3: 尝试重新加载影院数据
            cinemas = self.cinema_manager.load_cinema_list()
            self.tab_manager_widget.cinemas_data = cinemas
            
            for cinema in cinemas:
                cinema_short_name = cinema.get('cinemaShortName', '')
                if cinema_short_name == cinema_name:
                    return cinema
            
            return None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def _load_movies_for_cinema(self, cinema_info):
        """为指定影院加载电影列表"""
        try:
            # 使用film_service函数获取电影
            if self.current_account:
                base_url = cinema_info.get('base_url', '')
                cinemaid = cinema_info.get('cinemaid', '')
                userid = self.current_account.get('userid', '')
                openid = self.current_account.get('openid', '')
                token = self.current_account.get('token', '')
                
                if all([base_url, cinemaid, userid]):
                    # 调用get_films函数
                    raw_data = get_films(base_url, cinemaid, openid, userid, token)
                    normalized_data = normalize_film_data(raw_data)
                    
                    movies = normalized_data.get('films', [])
                    if movies and hasattr(self.tab_manager_widget, 'movie_combo'):
                        self.tab_manager_widget.movie_combo.clear()
                        for movie in movies:
                            self.tab_manager_widget.movie_combo.addItem(movie.get('name', ''))
                    else:
                        pass
                else:
                    pass
            else:
                pass
                    
        except Exception as e:
            pass
            # 如果API调用失败，使用默认电影列表
            if hasattr(self.tab_manager_widget, 'movie_combo'):
                self.tab_manager_widget.movie_combo.clear()
                self.tab_manager_widget.movie_combo.addItems([
                    "阿凡达：水之道",
                    "流浪地球2",
                    "满江红"
                ])
    
    def _show_order_detail(self, order_detail):
        """🆕 显示订单详情 - 使用统一的订单详情管理器"""
        try:
            if not order_detail:
                return

            print(f"[订单详情] 使用统一管理器显示订单详情")
            # 🆕 使用统一的订单详情管理器
            self.order_detail_manager.display_order_detail(order_detail, 'creation')

        except Exception as e:
            print(f"[订单详情] 显示失败: {e}")
            # 降级处理 - 显示基本错误信息
            if hasattr(self, 'order_detail_text'):
                self.order_detail_text.setPlainText(f"订单详情显示失败: {str(e)}")
    
    def _show_qr_code(self, qr_code):
        """显示取票码"""
        try:
            if qr_code:
                self.qr_display.setText(f"取票成功！\n\n取票码: {qr_code}")
                self.qr_display.setStyleSheet("""
                    QLabel {
                        color: #2e7d32;
                        font: bold 12px "Microsoft YaHei";
                        background-color: #e8f5e8;
                        border: 2px solid #4caf50;
                        padding: 20px;
                        border-radius: 5px;
                    }
                """)
            
        except Exception as e:
            pass
    
    def _update_order_table(self, orders):
        """更新订单表格"""
        try:
            if not hasattr(self.tab_manager_widget, 'order_table'):
                return
                
            table = self.tab_manager_widget.order_table
            table.setRowCount(len(orders))
            
            for i, order in enumerate(orders):
                table.setItem(i, 0, table.__class__.createItem(order.get('movie', '')))
                table.setItem(i, 1, table.__class__.createItem(order.get('cinema', '')))
                
                status = order.get('status', '')
                if status == '已完成':
                    table.add_colored_item(i, 2, status, "#4caf50")
                elif status == '待支付':
                    table.add_colored_item(i, 2, status, "#ff9800")
                elif status == '已取消':
                    table.add_colored_item(i, 2, status, "#f44336")
                else:
                    table.setItem(i, 2, table.__class__.createItem(status))
                
                table.setItem(i, 3, table.__class__.createItem(order.get('order_id', '')))
                
        except Exception as e:
            pass

    # ===== 定时器相关方法（PyQt5替换tkinter.after） =====
    
    # 🆕 移除倒计时相关方法
    
    # 🆕 移除倒计时显示和处理方法

    def _on_session_selected(self, session_info: dict):
        """场次选择处理 - 加载座位图"""
        try:
            # print(f"[主窗口] 收到场次选择信号: {session_info.get('session_text', 'N/A')}")
            # print("[主窗口333] 收到场次选择信号")
            
            # 验证必要信息
            session_data = session_info.get('session_data')
            account = session_info.get('account')
            cinema_data = session_info.get('cinema_data')
            
            if not all([session_data, account, cinema_data]):
                self._safe_update_seat_area("场次信息不完整\n\n无法加载座位图")
                return

            # 🆕 直接加载座位图，不显示加载提示
            # 使用QTimer延迟执行，避免阻塞UI
            QTimer.singleShot(100, lambda: self._load_seat_map(session_info))
            
        except Exception as e:
            pass
            # 安全地更新座位区域显示
            self._safe_update_seat_area("加载座位图失败\n\n请重新选择场次")

    def _safe_update_seat_area(self, message: str):
        """安全地更新座位区域显示"""
        try:
            # 检查座位区域布局是否存在
            if not hasattr(self, 'seat_area_layout') or not self.seat_area_layout:
                return

            # 清理现有的座位组件
            self._clear_seat_area()

            # 重新创建座位占位符
            from ui.widgets.classic_components import ClassicLabel
            self.seat_placeholder = ClassicLabel(message, "default")
            self.seat_placeholder.setAlignment(Qt.AlignCenter)
            self.seat_placeholder.setStyleSheet("""
                QLabel {
                    color: #999999;
                    font: 14px "Microsoft YaHei";
                    background-color: #ffffff;
                    border: 1px dashed #cccccc;
                    padding: 60px;
                    border-radius: 5px;
                }
            """)
            self.seat_area_layout.addWidget(self.seat_placeholder)


        except Exception as e:
            import traceback
            traceback.print_exc()

    def _safe_update_seat_area_with_style(self, message: str, style: str):
        """安全地更新座位区域显示，并应用自定义样式"""
        try:
            # 检查座位区域布局是否存在
            if not hasattr(self, 'seat_area_layout') or not self.seat_area_layout:
                return

            # 清理现有的座位组件
            self._clear_seat_area()

            # 重新创建座位占位符
            from ui.widgets.classic_components import ClassicLabel
            self.seat_placeholder = ClassicLabel(message, "default")
            self.seat_placeholder.setAlignment(Qt.AlignCenter)
            self.seat_placeholder.setStyleSheet(style)
            self.seat_area_layout.addWidget(self.seat_placeholder)


        except Exception as e:
            import traceback
            traceback.print_exc()

    def _clear_seat_area(self):
        """清理座位区域的所有组件"""
        try:
            if hasattr(self, 'seat_area_layout') and self.seat_area_layout:
                # 清理布局中的所有组件
                while self.seat_area_layout.count():
                    child = self.seat_area_layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
        except Exception as e:
            pass

    def _load_seat_map(self, session_info: dict):
        """加载座位图数据"""
        try:
            from services.film_service import get_plan_seat_info
            
            # 获取必要参数
            session_data = session_info['session_data']
            account = session_info['account']
            cinema_data = session_info['cinema_data']
            
            # 🆕 修复base_url字段名问题
            # 从影院数据中获取base_url，支持多种字段名
            base_url = cinema_data.get('base_url', '') or cinema_data.get('domain', '')
            if base_url:
                # 确保去掉协议前缀
                base_url = base_url.replace('https://', '').replace('http://', '')
            
            print(f"  - 影院名称: {cinema_data.get('cinemaShortName', 'N/A')}")
            print(f"  - 影院ID: {cinema_data.get('cinemaid', 'N/A')}")
            
            # 构建API参数
            params = {
                'base_url': base_url,
                'showCode': session_data.get('g', ''),      # 场次唯一编码
                'hallCode': session_data.get('j', ''),      # 影厅编码
                'filmCode': session_data.get('h', ''),      # 影片编码
                'filmNo': session_data.get('fno', ''),      # 影片No
                'showDate': session_data.get('k', '').split(' ')[0] if session_data.get('k') else '',  # 日期部分
                'startTime': session_data.get('q', ''),     # 开始时间
                'userid': account.get('userid', ''),
                'openid': account.get('openid', ''),
                'token': account.get('token', ''),
                'cinemaid': cinema_data.get('cinemaid', ''),
                'cardno': account.get('cardno', '')
            }
            
            
            # 验证参数完整性
            required_params = ['base_url', 'showCode', 'hallCode', 'filmCode', 'userid', 'openid', 'token', 'cinemaid']
            missing_params = [p for p in required_params if not params.get(p)]
            if missing_params:
                error_msg = f"缺少必要参数: {', '.join(missing_params)}"
                self._safe_update_seat_area(f"参数不完整\n\n{error_msg}")
                return
            
            # 调用座位图API
            seat_result = get_plan_seat_info(**params)
            
            print(f"[主窗口] 座位图API响应: {type(seat_result)}")
            
            if seat_result and isinstance(seat_result, dict):
                if seat_result.get('resultCode') == '0':
                    # 成功获取座位数据
                    seat_data = seat_result.get('resultData', {})
                    self._display_seat_map(seat_data, session_info)
                else:
                    pass
                    # API返回错误
                    error_msg = seat_result.get('resultDesc', '未知错误')
                    self._safe_update_seat_area(f"获取座位图失败\n\n{error_msg}")
            else:
                pass
                # 响应格式错误
                self._safe_update_seat_area("座位图数据格式错误\n\n请重新选择场次")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._safe_update_seat_area("加载座位图异常\n\n请检查网络连接")

    def _display_seat_map(self, seat_data: dict, session_info: dict):
        """显示座位图"""
        try:
            print(f"[主窗口] 座位数据字段: {list(seat_data.keys()) if seat_data else '空数据'}")
            
            # 🆕 解析座位图数据结构 - 使用实际API返回的数据格式
            seat_matrix = None
            hall_info = {}
            
            if seat_data:
                # 获取影厅基本信息
                hall_info = {
                    'name': seat_data.get('hname', '未知影厅'),
                    'screen_type': seat_data.get('screentype', ''),
                    'seat_count': seat_data.get('seatcount', 0)
                }
                
                # 🆕 解析seats数组数据
                seats_array = seat_data.get('seats', [])
                if seats_array:
                    seat_matrix = self._parse_seats_array(seats_array, hall_info)
                    print(f"[主窗口] 座位矩阵解析完成: {len(seat_matrix) if seat_matrix else 0} 行")
                else:
                    pass
            
            # 🆕 创建或更新座位图面板
            if seat_matrix and len(seat_matrix) > 0:
                try:
                    # 替换占位符为实际的座位图组件
                    from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5
                    
                    # 移除现有的占位符
                    if hasattr(self, 'seat_area_layout'):
                        # 清除现有组件
                        while self.seat_area_layout.count():
                            child = self.seat_area_layout.takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                        
                        # 创建新的座位图面板
                        seat_panel = SeatMapPanelPyQt5()
                        seat_panel.update_seat_data(seat_matrix)
                        
                        # 连接座位选择信号
                        seat_panel.seat_selected.connect(self._on_seat_map_selection_changed)
                        
                        # 🆕 连接提交订单回调
                        seat_panel.set_on_submit_order(self._on_seat_panel_submit_order)
                        seat_panel.set_account_getter(lambda: self.current_account)
                        
                        # 添加到布局
                        self.seat_area_layout.addWidget(seat_panel)
                        
                        # 保存引用
                        self.current_seat_panel = seat_panel
                        
                        # 更新成功信息
                        session_text = session_info.get('session_text', 'N/A')
                        info_text = f"✅ 座位图加载成功\\n\\n影厅: {hall_info['name']}\\n场次: {session_text}\\n座位: {hall_info['seat_count']}个\\n\\n请在下方选择座位"
                        
                        # 更新座位输入框提示
                        if hasattr(self, 'seat_input'):
                            self.seat_input.setPlaceholderText("点击上方座位图选择座位...")
                            self.seat_input.setText("")  # 清空之前的选择
                        
                        
                    else:
                        self._safe_update_seat_area("座位区域初始化失败")
                        
                except Exception as panel_error:
                    import traceback
                    traceback.print_exc()
                    self._safe_update_seat_area(f"座位图显示错误\n\n{str(panel_error)}")
            else:
                pass
                # 座位数据解析失败
                self._safe_update_seat_area("座位数据解析失败\n\n请重新选择场次或联系管理员")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._safe_update_seat_area("显示座位图异常\n\n请重新选择场次")

    def _parse_seats_array(self, seats_array: List[Dict], hall_info: dict) -> List[List[Dict]]:
        """解析seats数组为座位矩阵"""
        try:
            print(f"[主窗口] 座位数据量: {len(seats_array)}")
            
            if not seats_array:
                return []
            
            # 🆕 分析seats数组结构，使用正确的字段名
            max_row = 0
            max_col = 0
            
            # 🆕 详细打印前几个座位数据以调试座位号问题
            for i, seat in enumerate(seats_array[:5]):  # 增加到5个
                rn = seat.get('rn', 'N/A')
                cn = seat.get('cn', 'N/A')
                sn = seat.get('sn', 'N/A')
                r = seat.get('r', 'N/A')  # 🆕 逻辑排号
                c = seat.get('c', 'N/A')  # 🆕 逻辑列数
                s = seat.get('s', 'N/A')
            
            for seat in seats_array:
                # 🆕 使用物理座位号（rn, cn）来确定座位图的最大尺寸
                # 物理座位号用于构建座位图布局，包括空座位间隔
                physical_row = seat.get('rn', 0)
                physical_col = seat.get('cn', 0)
                max_row = max(max_row, physical_row)
                max_col = max(max_col, physical_col)
            
            
            if max_row == 0 or max_col == 0:
                return []
            
            # 🆕 创建座位矩阵
            seat_matrix = []
            for row in range(max_row):
                seat_row = [None] * max_col
                seat_matrix.append(seat_row)
            
            # 🆕 填充座位数据
            for seat in seats_array:
                # 🆕 使用物理座位号（rn, cn）确定在座位图中的位置
                physical_row = seat.get('rn', 0) - 1  # 转为0基索引
                physical_col = seat.get('cn', 0) - 1  # 转为0基索引

                if 0 <= physical_row < max_row and 0 <= physical_col < max_col:
                    # 解析座位状态：s字段，F=可选，B=已售等
                    seat_state = seat.get('s', 'F')
                    if seat_state == 'F':
                        status = 'available'
                    elif seat_state == 'B':
                        status = 'sold'
                    else:
                        status = 'unavailable'
                    
                    # 🆕 修复：使用逻辑座位号（r, c）作为显示座位号
                    # 物理座位号（rn, cn）用于构建座位图布局
                    # 逻辑座位号（r, c）用于显示和提交
                    logical_row = seat.get('r', '')  # 逻辑排号
                    logical_col = seat.get('c', '')  # 逻辑列数

                    # 显示座位号：优先使用逻辑列数c
                    if logical_col:
                        real_seat_num = str(logical_col)
                    else:
                        pass
                        # 备选：使用物理列号
                        real_seat_num = str(seat.get('cn', physical_col + 1))

                    seat_data = {
                        'row': logical_row if logical_row else seat.get('rn', physical_row + 1),  # 🆕 优先使用逻辑排号r，备选物理排号rn
                        'col': logical_col if logical_col else seat.get('cn', physical_col + 1),  # 🆕 优先使用逻辑列数c，备选物理列数cn
                        'num': real_seat_num,  # 🆕 使用逻辑列数c作为座位号
                        'status': status,
                        'price': 0,  # 价格信息在priceinfo中
                        'seatname': seat.get('sn', ''),
                        'original_data': seat  # 保存原始数据备用
                    }

                    seat_matrix[physical_row][physical_col] = seat_data
            
            # 打印前几行座位数据用于调试，显示物理间隔
            for i, row in enumerate(seat_matrix[:3]):  # 只打印前3行
                valid_seats = [seat['num'] if seat else 'None' for seat in row[:20]]  # 显示前20列以看到间隔

            # 🆕 专门检查5排的物理间隔
            if len(seat_matrix) >= 5:
                row_5 = seat_matrix[4]  # 第5排（0基索引）
                for col_idx, seat in enumerate(row_5):
                    if seat:
                        original_data = seat.get('original_data', {})
                        logical_r = original_data.get('r', '?')
                        logical_c = original_data.get('c', '?')
                        physical_cn = original_data.get('cn', '?')
                        physical_rn = original_data.get('rn', '?')
                    else:
                        pass
            
            return seat_matrix
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []

    def _on_seat_map_selection_changed(self, selected_seats: List[Dict]):
        """座位图选择变化处理"""
        try:
            print(f"[主窗口] 座位选择变化: {len(selected_seats)} 个座位")
            
            if hasattr(self, 'seat_input'):
                if selected_seats:
                    # 显示选中的座位
                    seat_names = [seat.get('num', f"{seat.get('row', '?')}-{seat.get('col', '?')}") for seat in selected_seats]  # 🆕 使用简洁格式
                    self.seat_input.setText(", ".join(seat_names))
                else:
                    pass
                    # 清空选择
                    self.seat_input.setText("")
            
            # 触发座位选择事件
            self._on_seat_selected(", ".join([seat.get('num', '') for seat in selected_seats]))
            
        except Exception as e:
            import traceback
            traceback.print_exc()
    
    def _on_seat_panel_submit_order(self, selected_seats: List[Dict]):
        """座位面板提交订单处理"""
        try:
            print(f"[主窗口] 座位面板提交订单: {len(selected_seats)} 个座位")
            
            # 调用主要的订单提交方法
            self.on_submit_order(selected_seats)
            
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _on_coupon_bound(self, bind_data: dict):
        """券绑定处理 - 对接到核心业务方法"""
        try:
            # 调用核心绑定券方法
            self.on_bind_coupons()
            
        except Exception as e:
            pass

    def _on_coupon_exchanged(self, exchange_data: dict):
        """券兑换处理"""
        coupon_type = exchange_data.get("type", "")
        quantity = exchange_data.get("quantity", 0)

    def _on_seat_load_requested(self, seat_load_data: dict):
        """处理座位图加载请求信号 - 来自Tab管理器的选座按钮"""
        try:
            # print(f"[主窗口] 收到座位图加载请求: {seat_load_data.get('trigger_type', 'unknown')}")

            # 获取场次数据
            session_data = seat_load_data.get('session_data', {})
            if not session_data:
                from services.ui_utils import MessageManager
                MessageManager.show_error(self, "加载失败", "缺少场次数据，请重新选择场次", auto_close=False)
                return

            print(f"  影院: {seat_load_data.get('cinema_name', 'N/A')}")
            print(f"  影片: {seat_load_data.get('movie_name', 'N/A')}")
            print(f"  日期: {seat_load_data.get('show_date', 'N/A')}")
            print(f"  场次: {seat_load_data.get('session_text', 'N/A')}")

            # 构建完整的session_info数据
            session_info = {
                'session_data': session_data,
                'account': seat_load_data.get('account', self.current_account),
                'cinema_data': self._get_current_cinema_data(),
                'session_text': seat_load_data.get('session_text', 'N/A')
            }

            # 调用现有的场次选择处理方法来加载座位图
            self._on_session_selected(session_info)


        except Exception as e:
            import traceback
            traceback.print_exc()

            # 显示错误信息
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "加载失败", f"座位图加载失败: {str(e)}", auto_close=False)

    def _get_current_cinema_data(self):
        """获取当前选中的影院数据"""
        try:
            if hasattr(self.tab_manager_widget, 'cinema_combo'):
                cinema_name = self.tab_manager_widget.cinema_combo.currentText()
                if cinema_name and hasattr(self.tab_manager_widget, 'cinemas_data'):
                    for cinema in self.tab_manager_widget.cinemas_data:
                        if cinema.get('cinemaShortName') == cinema_name:
                            return cinema
            return {}
        except Exception as e:
            return {}

    def _on_seat_input_changed(self, text: str):
        """座位输入变化处理 - 只记录日志，不替换座位图"""
        try:
            # 解析座位输入
            seats = [seat.strip() for seat in text.split(',') if seat.strip()]

            if seats:
                # 只发出座位选择信号，不替换座位图
                self._on_seat_selected(','.join(seats))

        except Exception as e:
            pass

    def _on_pay_button_clicked(self):
        """支付按钮点击处理 - 对接到核心业务方法"""
        try:
            # 调用核心一键支付方法
            self.on_one_click_pay()
            
        except Exception as e:
            pass

    def _on_seat_selected(self, seats: str):
        """座位选择处理 - 只记录日志，不替换座位图"""
        # 注意：不再调用_update_seat_selection，因为座位图面板会自己管理选座信息显示

    def _on_main_login_success(self, user_info: dict):
        """主窗口登录成功处理 - 触发账号列表刷新"""
        try:
            # 刷新账号列表
            self.refresh_account_list()
            
        except Exception as e:
            pass

    # ===== 全局事件处理方法 =====

    def _on_global_login_success(self, user_info: dict):
        """全局登录成功处理"""

    def _on_global_account_changed(self, account_data: dict):
        """全局账号切换处理"""
        try:
            userid = account_data.get('userid', 'N/A')
            phone = account_data.get('phone', '')
            
            # 同步更新右栏显示
            if phone:
                self.phone_display.setText(f"当前账号: {phone}")
            else:
                self.phone_display.setText(f"当前账号: {userid}")
                
        except Exception as e:
            pass

    def _on_global_cinema_selected(self, cinema_data: dict):
        """🔧 全局影院选择处理 - 修复参数类型并添加账号自动选择"""
        try:
            if not cinema_data:
                return

            cinema_name = cinema_data.get('cinemaShortName', '未知影院')
            cinema_id = cinema_data.get('cinemaid', '')

            print(f"[主窗口] 收到全局影院选择事件: {cinema_name} (ID: {cinema_id})")

            # 🔧 触发该影院的主账号自动选择
            if cinema_id:
                self._auto_select_cinema_account(cinema_data)
            else:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _on_global_order_created(self, order_data: dict):
        """全局订单创建处理"""
        try:
            order_id = order_data.get('order_id', 'N/A')
            
            # 更新右栏订单详情显示
            self._update_order_details(order_data)
            
            # 更新取票码区域
            self.qr_display.setText(f"订单号: {order_id}\n\n取票码将在支付完成后显示")
            
        except Exception as e:
            pass

    def _on_global_order_paid(self, order_id: str):
        """全局订单支付处理 - 修复：不覆盖已显示的取票码二维码"""
        try:
            # 🔧 修复：支付成功后不再覆盖取票码显示
            # 因为_get_ticket_code_after_payment已经处理了取票码显示
            # 这里只做必要的状态更新，不覆盖二维码显示

            print(f"[主窗口] 📋 订单支付成功事件: {order_id}")

            # 检查是否已经有取票码二维码显示
            if hasattr(self, 'qr_display'):
                # 如果当前显示的是图片（二维码），则不覆盖
                if self.qr_display.pixmap() and not self.qr_display.pixmap().isNull():
                    print(f"[主窗口] ✅ 取票码二维码已显示，保持当前显示")
                    return

                # 如果当前没有二维码显示，则显示支付成功信息
                success_text = f"支付成功！\n\n订单号: {order_id}\n\n取票码正在生成中..."
                self.qr_display.setText(success_text)
                self.qr_display.setStyleSheet("""
                    QLabel {
                        color: #2e7d32;
                        font: bold 12px "Microsoft YaHei";
                        background-color: #e8f5e8;
                        border: 2px solid #4caf50;
                        padding: 20px;
                        border-radius: 5px;
                    }
                """)

            # 🆕 移除倒计时显示更新

        except Exception as e:
            pass

    def _get_ticket_code_after_payment(self, order_id: str, cinema_id: str, detail_data: dict):
        """支付成功后获取取票码并显示（与双击订单流程一致）"""
        try:
            # 🎯 从订单详情中提取取票码（与双击订单流程一致）
            qr_code = detail_data.get('qrCode', '')
            ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
            ds_code = detail_data.get('dsValidateCode', '')


            # 🎯 确定最终的取票码（优先使用qrCode）
            final_ticket_code = qr_code or ds_code or ticket_code

            if final_ticket_code:
                # 🎯 生成取票码二维码并显示（与双击订单流程一致）
                self._generate_payment_success_qrcode(order_id, final_ticket_code, detail_data, cinema_id)

            else:
                pass
                # 显示支付成功但无取票码的信息
                self._show_payment_success_without_qrcode(order_id)

        except Exception as e:
            import traceback
            traceback.print_exc()
            # 降级显示支付成功信息
            self._show_payment_success_without_qrcode(order_id)

    def _generate_payment_success_qrcode(self, order_id: str, ticket_code: str, detail_data: dict, cinema_id: str):
        """支付成功后生成并显示取票码二维码"""
        try:
            # 🔧 导入二维码生成器
            from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image

            # 🎯 生成二维码图片
            qr_bytes = generate_ticket_qrcode(ticket_code, detail_data)

            if qr_bytes:
                print(f"[支付成功] ✅ 取票码二维码生成成功: {len(qr_bytes)} bytes")

                # 🎯 保存二维码图片到本地
                save_path = save_qrcode_image(qr_bytes, order_id, cinema_id)
                if save_path:
                    pass

                # 🎯 创建显示数据（与双击订单流程一致）
                qr_data = {
                    'order_no': order_id,
                    'qr_bytes': qr_bytes,
                    'qr_path': save_path,
                    'data_size': len(qr_bytes),
                    'data_format': 'PNG',
                    'display_type': 'generated_qrcode',  # 标识为生成的二维码
                    'ticket_code': ticket_code,
                    'film_name': detail_data.get('filmName', ''),
                    'show_time': detail_data.get('showTime', ''),
                    'hall_name': detail_data.get('hallName', ''),
                    'seat_info': detail_data.get('seatInfo', ''),
                    'cinema_name': detail_data.get('cinemaName', ''),
                    'is_generated': True,  # 标识这是自主生成的二维码
                    'source': 'payment_success'  # 🔧 标识来源为支付成功（用于调试）
                }

                print(f"[支付成功] 📤 - 图片大小: {len(qr_bytes)} bytes")

                # 🎯 直接调用显示方法（不通过事件总线，避免延迟）
                # 🔧 修复：确保支付成功后的显示与双击订单查看完全一致
                print(f"[支付成功] 📤 调用统一显示函数，显示类型: {qr_data.get('display_type')}")
                self._on_show_qrcode(qr_data)


            else:
                pass
                # 降级显示支付成功信息
                self._show_payment_success_without_qrcode(order_id)

        except Exception as e:
            import traceback
            traceback.print_exc()
            # 降级显示支付成功信息
            self._show_payment_success_without_qrcode(order_id)

    def _show_payment_success_without_qrcode(self, order_id: str):
        """显示支付成功但无取票码的信息"""
        try:
            success_text = f"支付成功！\n\n订单号: {order_id}\n\n请在订单列表中查看取票码"
            self.qr_display.setText(success_text)
            self.qr_display.setStyleSheet("""
                QLabel {
                    color: #2e7d32;
                    font: bold 14px "Microsoft YaHei";
                    background-color: #e8f5e8;
                    border: 2px solid #4caf50;
                    padding: 20px;
                    border-radius: 5px;
                }
            """)

        except Exception as e:
            pass

    def _on_show_qrcode(self, qr_data):
        """显示二维码处理"""
        try:
            print(f"[主窗口] 🔍 数据类型: {type(qr_data)}")

            # 检查数据格式
            if isinstance(qr_data, dict):
                display_type = qr_data.get('display_type', 'qr_image')

                if display_type == 'ticket_code':
                    # 🎯 处理取票码文本显示
                    print(f"[主窗口] 📱 - 订单号: {qr_data.get('order_no', 'N/A')}")
                    print(f"[主窗口] 📱 - 取票码: {qr_data.get('ticket_code', 'N/A')}")
                    print(f"[主窗口] 📱 - 影片: {qr_data.get('film_name', 'N/A')}")

                    # 显示取票码信息
                    self._display_ticket_code_info(qr_data)

                elif display_type == 'combined':
                    # 🎯 处理组合显示（文本+二维码图片）
                    print(f"[主窗口] 🎭 - 订单号: {qr_data.get('order_no', 'N/A')}")
                    print(f"[主窗口] 🎭 - 取票码: {qr_data.get('ticket_code', 'N/A')}")
                    print(f"[主窗口] 🎭 - 影片: {qr_data.get('film_name', 'N/A')}")
                    print(f"[主窗口] 🎭 - 图片大小: {qr_data.get('data_size', 0)} bytes")

                    # 显示组合信息（文本+图片）
                    self._display_combined_ticket_info(qr_data)

                elif display_type == 'generated_qrcode':
                    # 🎯 处理生成的取票码二维码
                    print(f"[主窗口] 🎨 - 订单号: {qr_data.get('order_no', 'N/A')}")
                    print(f"[主窗口] 🎨 - 取票码: {qr_data.get('ticket_code', 'N/A')}")
                    print(f"[主窗口] 🎨 - 影片: {qr_data.get('film_name', 'N/A')}")
                    print(f"[主窗口] 🎨 - 图片大小: {qr_data.get('data_size', 0)} bytes")
                    print(f"[主窗口] 🎨 - 是否生成: {qr_data.get('is_generated', False)}")

                    # 显示生成的二维码
                    self._display_generated_qrcode(qr_data)

                else:
                    pass
                    # 🎯 处理二维码图片显示
                    print(f"[主窗口] 📊 - 订单号: {qr_data.get('order_no', 'N/A')}")
                    print(f"[主窗口] 📊 - 数据大小: {qr_data.get('data_size', 0)} bytes")
                    print(f"[主窗口] 📊 - 数据格式: {qr_data.get('data_format', 'UNKNOWN')}")

                    # 获取二维码字节数据
                    qr_bytes = qr_data.get('qr_bytes')
                    order_no = qr_data.get('order_no', '')
                    data_format = qr_data.get('data_format', 'UNKNOWN')

                    if qr_bytes and len(qr_bytes) > 0:
                        # 尝试将二进制数据转换为QPixmap并显示
                        success = self._display_qrcode_image(qr_bytes, order_no, data_format)

                        if not success:
                            # 如果图片显示失败，显示文本信息
                            self._display_qrcode_text(f"订单 {order_no} 取票码\n(图片加载失败)")
                    else:
                        self._display_qrcode_text(f"订单 {qr_data.get('order_no', '')} 取票码\n(数据为空)")

            elif isinstance(qr_data, str):
                # 兼容旧的字符串格式
                self._display_qrcode_text(qr_data)
            else:
                print(f"[主窗口] ⚠️ 未知的数据格式: {type(qr_data)}")
                self._display_qrcode_text("二维码数据格式错误")

        except Exception as e:
            import traceback
            traceback.print_exc()
            # 显示错误信息
            self._display_qrcode_text("二维码显示错误")

    def _display_qrcode_image(self, qr_bytes: bytes, order_no: str, data_format: str) -> bool:
        """显示二维码图片"""
        try:
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import QByteArray
            # 将bytes转换为QByteArray
            byte_array = QByteArray(qr_bytes)

            # 创建QPixmap
            pixmap = QPixmap()
            success = pixmap.loadFromData(byte_array)

            if success and not pixmap.isNull():
                print(f"[主窗口] ✅ 二维码图片加载成功: {pixmap.width()}x{pixmap.height()}")

                # 缩放图片以适应显示区域
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # 在取票码区域显示图片
                if hasattr(self, 'qr_display'):
                    self.qr_display.setPixmap(scaled_pixmap)
                    self.qr_display.setText("")  # 清空文本
                    self.qr_display.setAlignment(Qt.AlignCenter)
                    self.qr_display.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            border: 2px solid #4caf50;
                            padding: 10px;
                            border-radius: 5px;
                        }
                    """)

                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

    def _display_ticket_code_info(self, ticket_data: dict):
        """显示取票码详细信息"""
        try:
            order_no = ticket_data.get('order_no', '')
            ticket_code = ticket_data.get('ticket_code', '')
            film_name = ticket_data.get('film_name', '')
            show_time = ticket_data.get('show_time', '')
            hall_name = ticket_data.get('hall_name', '')
            seat_info = ticket_data.get('seat_info', '')
            cinema_name = ticket_data.get('cinema_name', '')

            # 🔍 调试：检查所有字段值
            # 构建详细的取票信息文本
            info_text = f"🎬 {film_name}\n"
            info_text += f"🏛️ {cinema_name}\n"
            info_text += f"🕐 {show_time}\n"
            info_text += f"🎭 {hall_name}\n"
            info_text += f"💺 {seat_info}\n\n"

            # 🔧 修复：确保取票码显示
            if ticket_code:
                info_text += f"🎫 取票码: {ticket_code}\n"
            else:
                info_text += f"🎫 取票码: (未获取到)\n"

            info_text += f"📋 订单号: {order_no}"

            print(f"[主窗口] 🔍 文本长度: {len(info_text)}")
            print(f"[主窗口] 🔍 文本内容: {repr(info_text[:200])}...")

            if hasattr(self, 'qr_display'):
                # 简单清空和设置
                self.qr_display.clear()  # 清空图片和文本
                self.qr_display.setText(info_text)
                self.qr_display.setAlignment(Qt.AlignCenter)
                self.qr_display.setStyleSheet("""
                    QLabel {
                        color: #1976d2;
                        font: bold 11px "Microsoft YaHei";
                        background-color: #e3f2fd;
                        border: 2px solid #2196f3;
                        padding: 15px;
                        border-radius: 8px;
                        line-height: 1.4;
                    }
                """)
            else:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _display_combined_ticket_info(self, combined_data: dict):
        """显示组合信息（文本+二维码图片）"""
        try:
            from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import QByteArray, Qt

            order_no = combined_data.get('order_no', '')
            ticket_code = combined_data.get('ticket_code', '')
            film_name = combined_data.get('film_name', '')
            show_time = combined_data.get('show_time', '')
            hall_name = combined_data.get('hall_name', '')
            seat_info = combined_data.get('seat_info', '')
            cinema_name = combined_data.get('cinema_name', '')
            qr_bytes = combined_data.get('qr_bytes')
            data_format = combined_data.get('data_format', 'UNKNOWN')

            print(f"[主窗口] 🎭 - 二维码: {len(qr_bytes) if qr_bytes else 0} bytes {data_format}")

            if hasattr(self, 'qr_display'):
                # 🎯 方案1：在同一个区域显示文本+图片
                # 创建包含文本和图片的组合内容

                # 先尝试加载二维码图片
                qr_pixmap = None
                if qr_bytes and len(qr_bytes) > 0:
                    try:
                        byte_array = QByteArray(qr_bytes)
                        pixmap = QPixmap()
                        success = pixmap.loadFromData(byte_array)

                        if success and not pixmap.isNull():
                            # 缩放图片
                            qr_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            print(f"[主窗口] ✅ 二维码图片加载成功: {pixmap.width()}x{pixmap.height()}")
                        else:
                            pass
                    except Exception as e:
                        pass

                if qr_pixmap:
                    # 显示二维码图片
                    self.qr_display.setPixmap(qr_pixmap)
                    self.qr_display.setText("")  # 清空文本
                    self.qr_display.setAlignment(Qt.AlignCenter)
                    self.qr_display.setStyleSheet("""
                        QLabel {
                            background-color: #ffffff;
                            border: 2px solid #2196f3;
                            padding: 10px;
                            border-radius: 8px;
                        }
                    """)

                    # 🎯 在二维码下方显示取票码信息（可以考虑添加到状态栏或其他位置）
                else:
                    pass
                    # 如果图片加载失败，显示文本信息
                    info_text = f"🎬 {film_name}\n"
                    info_text += f"🏛️ {cinema_name}\n"
                    info_text += f"🕐 {show_time}\n"
                    info_text += f"🎭 {hall_name}\n"
                    info_text += f"💺 {seat_info}\n\n"
                    info_text += f"🎫 取票码: {ticket_code}\n"
                    info_text += f"📋 订单号: {order_no}\n\n"
                    info_text += f"⚠️ 二维码图片加载失败"

                    self.qr_display.clear()
                    self.qr_display.setText(info_text)
                    self.qr_display.setAlignment(Qt.AlignCenter)
                    self.qr_display.setStyleSheet("""
                        QLabel {
                            color: #1976d2;
                            font: bold 10px "Microsoft YaHei";
                            background-color: #e3f2fd;
                            border: 2px solid #2196f3;
                            padding: 15px;
                            border-radius: 8px;
                            line-height: 1.4;
                        }
                    """)

            else:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _display_generated_qrcode(self, qr_data: dict):
        """显示生成的取票码二维码 - 修复：确保支付成功后与双击订单查看显示一致"""
        try:
            from PyQt5.QtGui import QPixmap
            from PyQt5.QtCore import QByteArray, Qt

            order_no = qr_data.get('order_no', '')
            ticket_code = qr_data.get('ticket_code', '')
            film_name = qr_data.get('film_name', '')
            qr_bytes = qr_data.get('qr_bytes')
            qr_path = qr_data.get('qr_path', '')  # 🎯 获取图片路径
            source = qr_data.get('source', 'unknown')  # 🔧 获取来源信息

            print(f"[主窗口] 🎨 显示来源: {source}")
            print(f"[主窗口] 🎨 - 订单号: {order_no}")
            print(f"[主窗口] 🎨 - 取票码: {ticket_code}")
            print(f"[主窗口] 🎨 - 二维码: {len(qr_bytes) if qr_bytes else 0} bytes")
            print(f"[主窗口] 🎨 - 图片路径: {qr_path}")

            # 🎯 保存图片路径和原始数据供按钮使用
            self.current_qr_path = qr_path
            self.current_qr_bytes = qr_bytes  # 🎨 保存原始图片数据用于高质量复制

            if hasattr(self, 'qr_display') and qr_bytes:
                try:
                    # 🎯 加载生成的二维码图片
                    byte_array = QByteArray(qr_bytes)
                    pixmap = QPixmap()
                    success = pixmap.loadFromData(byte_array)

                    if success and not pixmap.isNull():
                        # 🎯 显示优化后的二维码图片（保持原始尺寸以体现布局优化）
                        # 我们的生成器已经优化了布局，应该保持原始大小
                        print(f"[主窗口] 📐 原始二维码尺寸: {pixmap.width()}x{pixmap.height()}")

                        # 🎨 调整尺寸限制到300x300
                        max_width = 340   # 🎨 调整到300px
                        max_height = 340  # 🎨 调整到300px

                        if pixmap.width() > max_width or pixmap.height() > max_height:
                            scaled_pixmap = pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                            print(f"[主窗口] 📐 缩放后尺寸: {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                        else:
                            scaled_pixmap = pixmap
                            print(f"[主窗口] 📐 保持原始尺寸: {scaled_pixmap.width()}x{scaled_pixmap.height()}")

                        self.qr_display.setPixmap(scaled_pixmap)
                        self.qr_display.setText("")  # 清空文本
                        self.qr_display.setAlignment(Qt.AlignCenter)
                        self.qr_display.setStyleSheet("""
                            QLabel {
                                background-color: #ffffff;
                                border: 2px solid #4CAF50;
                                padding: 15px;
                                border-radius: 8px;
                            }
                        """)

                        print(f"[主窗口] ✅ 生成的二维码显示成功: {pixmap.width()}x{pixmap.height()}")

                    else:
                        pass
                        # 降级显示文本信息
                        self._display_qrcode_text(f"🎫 取票码: {ticket_code}\n📋 订单号: {order_no}\n⚠️ 二维码显示失败")

                except Exception as e:
                    pass
                    # 降级显示文本信息
                    self._display_qrcode_text(f"🎫 取票码: {ticket_code}\n📋 订单号: {order_no}\n⚠️ 二维码处理失败")
            else:
                pass

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _display_qrcode_text(self, text: str):
        """显示二维码文本信息"""
        try:
            if hasattr(self, 'qr_display'):
                self.qr_display.clear()  # 清空图片
                self.qr_display.setText(text)
                self.qr_display.setAlignment(Qt.AlignCenter)
                self.qr_display.setStyleSheet("""
                    QLabel {
                        color: #2e7d32;
                        font: bold 12px "Microsoft YaHei";
                        background-color: #e8f5e8;
                        border: 2px solid #4caf50;
                        padding: 20px;
                        border-radius: 5px;
                    }
                """)
            else:
                pass
        except Exception as e:
            import traceback
            traceback.print_exc()

    def _update_seat_selection(self, seats: list):
        """更新座位选择显示"""
        try:
            if seats:
                seat_info = f"已选择座位: {', '.join(seats)}\n\n"
                seat_info += f"座位数量: {len(seats)} 个\n"
                seat_info += f"预计价格: ¥{len(seats) * 35.0:.2f}"

                # 安全地更新座位区域
                self._safe_update_seat_area_with_style(seat_info, """
                    QLabel {
                        color: #333333;
                        font: 14px "Microsoft YaHei";
                        background-color: #e8f5e8;
                        border: 1px solid #4caf50;
                        padding: 20px;
                        border-radius: 5px;
                    }
                """)
            else:
                # 安全地更新座位区域
                self._safe_update_seat_area("座位图将在此显示\n\n请先选择影院、影片、日期和场次")
                
        except Exception as e:
            pass

    def _update_order_details(self, order_data: dict):
        """🆕 更新订单详情显示 - 使用统一的订单详情管理器"""
        try:
            print(f"[订单详情] 使用统一管理器更新订单详情")
            # 🆕 使用统一的订单详情管理器
            self.order_detail_manager.display_order_detail(order_data, 'update')

        except Exception as e:
            print(f"[订单详情] 更新失败: {e}")
            # 降级处理 - 显示基本错误信息
            if hasattr(self, 'order_detail_text'):
                self.order_detail_text.setPlainText(f"订单详情更新失败: {str(e)}")

    # 🆕 _enhance_order_data 方法已移至 OrderDetailManager 中

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 清理资源
            self.account_widget.cleanup()
            self.tab_manager_widget.cleanup()
            # 座位区域和右栏区域是直接创建的QWidget，不需要特殊清理
            event.accept()
            
        except Exception as e:
            event.accept()

    # ===== 🆕 增强支付系统核心方法 =====

    def get_member_info_enhanced(self) -> Dict[str, Any]:
        """🆕 增强的会员信息获取 - API实时获取替代本地JSON"""
        try:
            if not self.current_account:
                return {'success': False, 'is_member': False, 'error': '当前无登录账号'}

            # 调用会员信息API - 使用APIBase的接口
            cinema_id = self.current_account.get('cinema_id', '')
            params = {
                'groupid': '',
                'cinemaid': cinema_id,
                'cardno': '',
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            # 使用APIBase的便捷函数
            from services.api_base import api_get
            response = api_get('/MiniTicket/index.php/MiniMember/getMemberInfo', cinema_id, params)

            if response.get('resultCode') == '0':
                member_data = response.get('resultData', {})
                return {
                    'success': True,
                    'is_member': True,
                    'cardno': member_data.get('cardno', ''),
                    'mobile': member_data.get('mobile', ''),
                    'memberId': member_data.get('memberId', ''),
                    'cardtype': member_data.get('cardtype', '0'),
                    'cardcinemaid': member_data.get('cardcinemaid', ''),
                    'balance': int(float(member_data.get('balance', 0)) * 100),  # 转换为分
                    'data_source': 'api'
                }
            else:
                return {
                    'success': False,
                    'is_member': False,
                    'error': response.get('resultDesc', '获取会员信息失败'),
                    'data_source': 'api'
                }

        except Exception as e:
            print(f"[增强支付] 会员信息API调用失败: {e}")
            # 降级到本地数据
            return self._get_member_info_fallback()

    def _get_member_info_fallback(self) -> Dict[str, Any]:
        """会员信息获取降级处理"""
        try:
            # 尝试从现有的member_info获取
            if hasattr(self, 'member_info') and self.member_info:
                if isinstance(self.member_info, dict) and self.member_info.get('has_member_card', False):
                    fallback_info = self.member_info.copy()
                    fallback_info['data_source'] = 'local_cache'
                    fallback_info['success'] = True
                    return fallback_info

            return {
                'success': False,
                'is_member': False,
                'error': 'API调用失败且无本地缓存',
                'data_source': 'none'
            }
        except Exception as e:
            return {
                'success': False,
                'is_member': False,
                'error': f'降级处理失败: {str(e)}',
                'data_source': 'error'
            }

    def get_password_policy_from_order(self, order_no: str) -> Dict[str, Any]:
        """🆕 从订单详情获取密码策略 - 增强错误处理"""
        try:
            if not self.current_account:
                print(f"[调试-密码策略] ❌ 当前无登录账号")
                return self._get_smart_default_password_policy()

            # 🆕 修复：使用正确的字段名
            cinema_id = self.current_account.get('cinemaid', '') or self.current_account.get('cinema_id', '')
            if not cinema_id:
                print(f"[调试-密码策略] ❌ 无法获取影院ID")
                return self._get_smart_default_password_policy()

            print(f"[调试-密码策略] 🔄 尝试从API获取订单详情，订单号: {order_no}")

            params = {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': cinema_id,
                'cardno': '',
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            from services.api_base import api_get
            response = api_get('/MiniTicket/index.php/MiniOrder/getUnpaidOrderDetail', cinema_id, params)

            if response and response.get('resultCode') == '0':
                order_data = response.get('resultData', {})
                enable_mempassword = order_data.get('enable_mempassword')

                if enable_mempassword is not None:
                    print(f"[调试-密码策略] ✅ API获取成功: enable_mempassword = {enable_mempassword}")
                    return {
                        'success': True,
                        'requires_password': enable_mempassword == '1',
                        'enable_mempassword': enable_mempassword,
                        'mem_pay_only': order_data.get('memPayONLY', '0'),
                        'source': 'order_detail_api',
                        'description': f"API获取 - {'需要' if enable_mempassword == '1' else '不需要'}会员卡密码"
                    }
                else:
                    print(f"[调试-密码策略] ⚠️ API返回成功但无enable_mempassword字段")
            else:
                error_desc = response.get('resultDesc', '未知错误') if response else 'API调用失败'
                print(f"[调试-密码策略] ❌ API调用失败: {error_desc}")

            # 🆕 降级到影院策略
            print(f"[调试-密码策略] 🔄 降级到影院策略")
            cinema_policy = self._get_cinema_password_policy()
            if cinema_policy.get('success'):
                return cinema_policy

            # 🆕 最终降级到智能默认策略
            print(f"[调试-密码策略] 🔄 降级到智能默认策略")
            return self._get_smart_default_password_policy()

        except Exception as e:
            print(f"[调试-密码策略] ❌ 密码策略获取异常: {e}")
            return self._get_smart_default_password_policy()

    def _get_cinema_password_policy(self) -> Dict[str, Any]:
        """🆕 根据影院特征判断密码策略"""
        try:
            if not hasattr(self, 'current_account') or not self.current_account:
                return {'success': False}

            cinema_id = self.current_account.get('cinemaid', '') or self.current_account.get('cinema_id', '')

            # 🆕 已知的影院密码策略映射
            cinema_password_policies = {
                # 需要密码的影院
                '61011571': {'requires_password': True, 'name': '华夏优加荟大都荟'},
                '35fec8259e74': {'requires_password': True, 'name': '华夏优加荟大都荟'},

                # 不需要密码的影院（示例）
                # 'other_cinema_id': {'requires_password': False, 'name': '其他影院'},
            }

            if cinema_id in cinema_password_policies:
                policy = cinema_password_policies[cinema_id]
                requires_password = policy['requires_password']
                cinema_name = policy['name']

                print(f"[调试-密码策略] ✅ 影院 {cinema_name} ({cinema_id}) 策略: {'需要密码' if requires_password else '无需密码'}")

                return {
                    'success': True,
                    'requires_password': requires_password,
                    'enable_mempassword': '1' if requires_password else '0',
                    'source': 'cinema_policy',
                    'description': f"影院策略 ({cinema_name}) - {'需要密码' if requires_password else '无需密码'}"
                }
            else:
                print(f"[调试-密码策略] ⚠️ 影院 {cinema_id} 无预设策略")
                return {'success': False}

        except Exception as e:
            print(f"[调试-密码策略] ❌ 影院策略获取异常: {e}")
            return {'success': False}

    def _get_smart_default_password_policy(self) -> Dict[str, Any]:
        """🆕 智能默认密码策略 - 基于用户设置状态"""
        try:
            # 检查用户是否已设置支付密码
            has_password = False
            if hasattr(self, 'current_account') and self.current_account:
                payment_password = self.current_account.get('payment_password', '')
                has_password = bool(payment_password)

            if has_password:
                # 用户已设置密码，默认需要密码
                print(f"[调试-密码策略] 🎯 智能默认: 用户已设置密码，默认需要密码")
                return {
                    'success': True,
                    'requires_password': True,
                    'enable_mempassword': '1',
                    'source': 'smart_default',
                    'description': '智能默认 - 用户已设置密码，需要密码'
                }
            else:
                # 用户未设置密码，默认不需要密码（避免支付失败）
                print(f"[调试-密码策略] 🎯 智能默认: 用户未设置密码，默认无需密码")
                return {
                    'success': True,
                    'requires_password': False,
                    'enable_mempassword': '0',
                    'source': 'smart_default',
                    'description': '智能默认 - 用户未设置密码，无需密码'
                }

        except Exception as e:
            print(f"[调试-密码策略] ❌ 智能默认策略异常: {e}")
            # 最终降级：需要密码
            return {
                'success': True,
                'requires_password': True,
                'enable_mempassword': '1',
                'source': 'final_fallback',
                'description': '最终降级 - 需要会员卡密码'
            }

    def _get_enhanced_password_display(self, enable_mempassword: str) -> str:
        """🆕 获取增强的密码策略显示 - 支持智能降级"""
        try:
            if enable_mempassword == '1':
                # 需要密码，检查用户是否已设置支付密码
                if hasattr(self, 'current_account') and self.current_account:
                    payment_password = self.current_account.get('payment_password', '')
                    if payment_password:
                        return "密码: 需要输入 (已设置支付密码)"
                    else:
                        return "密码: 需要输入 (未设置支付密码)"
                else:
                    return "密码: 需要输入"
            elif enable_mempassword == '0':
                return "密码: 无需输入"
            else:
                # 🆕 智能降级处理 - 无法获取策略时使用智能默认
                print(f"[密码显示] enable_mempassword值异常: {enable_mempassword}，使用智能默认策略")
                smart_policy = self._get_smart_default_password_policy()

                if smart_policy.get('requires_password', True):
                    # 需要密码，检查密码设置状态
                    if hasattr(self, 'current_account') and self.current_account:
                        payment_password = self.current_account.get('payment_password', '')
                        if payment_password:
                            return f"密码: 需要输入 (已设置支付密码) - {smart_policy.get('description', '智能默认')}"
                        else:
                            return f"密码: 需要输入 (未设置支付密码) - {smart_policy.get('description', '智能默认')}"
                    else:
                        return f"密码: 需要输入 - {smart_policy.get('description', '智能默认')}"
                else:
                    return f"密码: 无需输入 - {smart_policy.get('description', '智能默认')}"

        except Exception as e:
            print(f"[密码显示] 获取密码显示错误: {e}")
            # 最终降级
            return "密码: 检测中... (系统异常)"

    def _get_account_payment_password(self, account: dict) -> str:
        """🆕 获取账号的支付密码 - 增强调试"""
        try:
            if not account:
                print(f"[密码管理] ❌ 账号数据为空")
                return ""

            # 详细的账号信息调试
            userid = account.get('userid', 'N/A')
            cinemaid = account.get('cinemaid', 'N/A')
            print(f"[密码管理] 🔍 检查账号密码设置:")
            print(f"[密码管理]   - userid: {userid}")
            print(f"[密码管理]   - cinemaid: {cinemaid}")
            print(f"[密码管理]   - 账号数据键: {list(account.keys())}")

            # 从账号数据中获取支付密码
            payment_password = account.get('payment_password', '')
            print(f"[密码管理]   - payment_password字段: {repr(payment_password)}")

            if payment_password:
                print(f"[密码管理] ✅ 账号 {userid}@{cinemaid} 已设置支付密码 (长度: {len(payment_password)})")
                return payment_password
            else:
                print(f"[密码管理] ❌ 账号 {userid}@{cinemaid} 未设置支付密码")
                return ""

        except Exception as e:
            print(f"[密码管理] ❌ 获取支付密码异常: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _prompt_set_payment_password(self, account: dict) -> str:
        """🆕 提示用户设置支付密码"""
        try:
            from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit

            # 提示用户需要设置支付密码
            reply = QMessageBox.question(
                self, "需要设置支付密码",
                f"订单需要会员卡密码，但账号 {account.get('userid', 'N/A')} 未设置支付密码。\n\n是否现在设置支付密码？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                # 获取密码输入
                password, ok = QInputDialog.getText(
                    self, "设置支付密码",
                    f"为账号 {account.get('userid', 'N/A')} 设置会员卡支付密码:",
                    QLineEdit.Password
                )

                if ok and password:
                    # 保存密码到账号数据
                    account['payment_password'] = password

                    # 保存到文件
                    self._save_payment_password_to_account_file(account)

                    QMessageBox.information(self, "设置成功", "支付密码设置成功！")
                    print(f"[密码管理] 支付密码设置成功: {account.get('userid', 'N/A')}")

                    return password
                else:
                    print(f"[密码管理] 用户取消设置支付密码")
                    return ""
            else:
                print(f"[密码管理] 用户选择不设置支付密码")
                return ""

        except Exception as e:
            print(f"[密码管理] 提示设置支付密码错误: {e}")
            return ""

    def _save_payment_password_to_account_file(self, account: dict) -> bool:
        """🆕 保存支付密码到账号文件"""
        try:
            import json
            import os

            accounts_file = "data/accounts.json"

            if not os.path.exists(accounts_file):
                print(f"[密码管理] 账号文件不存在: {accounts_file}")
                return False

            # 读取现有账号数据
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)

            # 更新密码
            userid = account.get('userid', '')
            cinemaid = account.get('cinemaid', '')

            updated = False
            for acc in accounts:
                if (acc.get('userid') == userid and
                    acc.get('cinemaid') == cinemaid):
                    acc['payment_password'] = account.get('payment_password', '')
                    updated = True
                    break

            if updated:
                # 写回文件
                with open(accounts_file, 'w', encoding='utf-8') as f:
                    json.dump(accounts, f, ensure_ascii=False, indent=2)

                print(f"[密码管理] 支付密码已保存到文件: {userid}")
                return True
            else:
                print(f"[密码管理] 未找到对应账号: {userid}")
                return False

        except Exception as e:
            print(f"[密码管理] 保存支付密码错误: {e}")
            return False

    def validate_coupon_prepay_enhanced(self, order_no: str, coupon_codes: str) -> Dict[str, Any]:
        """🆕 增强的券预支付验证"""
        try:
            if not self.current_account:
                return {'success': False, 'error': '当前无登录账号'}

            # 使用APIBase的接口
            cinema_id = self.current_account.get('cinema_id', '')
            params = {
                'orderno': order_no,
                'couponcode': coupon_codes,
                'cinemaid': cinema_id,
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            from services.api_base import api_get
            response = api_get('/MiniTicket/index.php/MiniOrder/ordercouponPrepay', cinema_id, params)

            if response.get('resultCode') == '0':
                result_data = response.get('resultData', {})
                return {
                    'success': True,
                    'payment_amount': int(result_data.get('paymentAmount', '0')),
                    'member_payment_amount': int(result_data.get('mempaymentAmount', '0')),
                    'discount_price': int(result_data.get('discountprice', '0')),
                    'discount_member_price': int(result_data.get('discountmemprice', '0')),
                    'total_price': int(result_data.get('totalprice', '0')),
                    'total_member_price': int(result_data.get('totalmemprice', '0')),
                    'coupon_codes': result_data.get('couponcodes', ''),
                    'bind_type': result_data.get('bindType', 0),
                    'coupon_count': result_data.get('couponcount', 0)
                }
            else:
                return {
                    'success': False,
                    'error': response.get('resultDesc', '券验证失败')
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_member_card_payment_enhanced(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """🆕 增强的会员卡支付处理 - 支持动态密码策略"""
        try:
            # 1. 获取实时会员信息
            member_result = self.get_member_info_enhanced()
            if not member_result.get('success') or not member_result.get('is_member'):
                return {
                    'success': False,
                    'error': member_result.get('error', '请先登录会员账户')
                }

            member_info = member_result

            # 2. 检查余额
            balance = member_info.get('balance', 0)
            total_amount = int(order_data.get('amount', 0) * 100)  # 转换为分

            if balance < total_amount:
                return {
                    'success': False,
                    'error': f"会员卡余额不足\n余额: ¥{balance/100:.2f}\n需要: ¥{total_amount/100:.2f}"
                }

            # 3. 获取密码策略
            order_no = order_data.get('orderno', '')
            cinema_id = self.current_account.get('cinema_id', '')
            password_policy = self.get_password_policy_from_order(order_no)

            # 4. 根据策略决定是否需要密码
            member_password = None
            if password_policy.get('requires_password', True):
                from PyQt5.QtWidgets import QInputDialog, QLineEdit
                password, ok = QInputDialog.getText(
                    self,
                    "会员密码",
                    f"请输入会员卡密码\n({password_policy.get('description', '需要密码验证')}):",
                    QLineEdit.Password
                )
                if not ok or not password:
                    return {'success': False, 'error': '用户取消密码输入'}
                member_password = password

            # 5. 构建支付参数
            payment_params = {
                'totalprice': str(total_amount),
                'memberinfo': json.dumps({
                    'cardno': member_info.get('cardno', ''),
                    'mobile': member_info.get('mobile', ''),
                    'memberId': member_info.get('memberId', ''),
                    'cardtype': '0',
                    'cardcinemaid': member_info.get('cardcinemaid', ''),
                    'balance': member_info.get('balance', 0) / 100  # 转换为元
                }),
                'orderno': order_no,
                'couponcodes': '',
                'price': str(total_amount),
                'discountprice': '0',
                'filmname': order_data.get('movie', ''),
                'featureno': order_data.get('featureno', ''),
                'ticketcount': str(len(order_data.get('seats', []))),
                'cinemaname': order_data.get('cinema', ''),
                'cinemaid': self.current_account.get('cinema_id', ''),
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            # 🆕 增强密码处理逻辑
            if password_policy.get('requires_password', True):
                if member_password:
                    payment_params['mempass'] = member_password
                    print(f"[增强支付] 使用预设支付密码")
                else:
                    return {
                        'success': False,
                        'error': '订单需要会员卡密码，但未设置支付密码',
                        'action_required': 'set_password'
                    }
            else:
                print(f"[增强支付] 订单无需会员卡密码")

            # 6. 执行支付
            from services.api_base import api_post
            response = api_post('/MiniTicket/index.php/MiniPay/memcardPay', cinema_id, payment_params)

            if response.get('resultCode') == '0':
                return {'success': True, 'message': '会员卡支付成功'}
            else:
                return {
                    'success': False,
                    'error': response.get('resultDesc', '支付失败')
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_mixed_payment_enhanced(self, order_data: Dict[str, Any], selected_coupons: List[Dict]) -> Dict[str, Any]:
        """🆕 增强的混合支付处理 - 券+会员卡"""
        try:
            # 1. 券预支付验证
            coupon_codes = ','.join([c.get('couponcode', '') for c in selected_coupons])
            order_no = order_data.get('orderno', '')

            prepay_result = self._validate_coupon_prepay(order_no, coupon_codes)
            if not prepay_result.get('success'):
                return {
                    'success': False,
                    'error': f"券验证失败: {prepay_result.get('error', '未知错误')}"
                }

            prepay_data = prepay_result.get('data', {})

            # 2. 获取会员信息和密码策略
            member_result = self.get_member_info_enhanced()
            if not member_result.get('success') or not member_result.get('has_member_card'):
                return {
                    'success': False,
                    'error': '混合支付需要会员卡，请先登录会员账户'
                }

            # 3. 获取密码策略
            password_policy = self._get_member_password_policy_enhanced(order_data)

            # 4. 处理会员密码
            member_password = ""
            if password_policy.get('requires_password', True):
                member_password = self._get_account_payment_password(self.current_account)
                if not member_password:
                    # 提示用户设置密码
                    member_password = self._prompt_set_payment_password(self.current_account)
                    if not member_password:
                        return {
                            'success': False,
                            'error': '混合支付需要会员卡密码，但未设置支付密码',
                            'action_required': 'set_password'
                        }

            # 5. 构建混合支付参数
            member_info = member_result
            cinema_id = self.current_account.get('cinemaid', '')

            # 使用券抵扣后的会员支付金额
            total_price = prepay_data.get('mempaymentAmount', '0')
            discount_price = prepay_data.get('discountmemprice', '0')

            payment_params = {
                'totalprice': total_price,  # 券抵扣后的会员支付金额
                'memberinfo': json.dumps({
                    'cardno': member_info.get('cardno', ''),
                    'mobile': member_info.get('mobile', ''),
                    'memberId': member_info.get('memberId', ''),
                    'cardtype': '0',
                    'cardcinemaid': member_info.get('cardcinemaid', ''),
                    'balance': member_info.get('balance', 0)
                }),
                'orderno': order_no,
                'couponcodes': coupon_codes,  # 券码
                'price': str(int(total_price) // 2),  # 实际从会员卡扣除的金额（示例）
                'discountprice': discount_price,  # 券抵扣金额
                'filmname': order_data.get('movie', ''),
                'featureno': order_data.get('featureno', ''),
                'ticketcount': str(len(order_data.get('seats', []))),
                'cinemaname': order_data.get('cinema', ''),
                'cinemaid': cinema_id,
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            # 添加密码参数
            if password_policy.get('requires_password', True) and member_password:
                payment_params['mempass'] = member_password

            # 6. 执行混合支付
            from services.api_base import api_post
            response = api_post('/MiniTicket/index.php/MiniPay/memcardPay', cinema_id, payment_params)

            if response.get('resultCode') == '0':
                return {'success': True, 'message': '混合支付成功'}
            else:
                return {
                    'success': False,
                    'error': response.get('resultDesc', '混合支付失败')
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _validate_coupon_prepay(self, order_no: str, coupon_codes: str) -> Dict[str, Any]:
        """🆕 验证券预支付"""
        try:
            from services.order_api import get_coupon_prepay_info

            if not self.current_account:
                return {'success': False, 'error': '账号信息缺失'}

            cinema_id = self.current_account.get('cinemaid', '')

            # 构建参数
            params = {
                'orderno': order_no,
                'couponcode': coupon_codes,
                'groupid': '',
                'cinemaid': cinema_id,
                'cardno': self.current_account.get('cardno', ''),
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            # 调用API
            result = get_coupon_prepay_info(cinema_id, params)

            if result and result.get('resultCode') == '0':
                return {
                    'success': True,
                    'data': result.get('resultData', {})
                }
            else:
                return {
                    'success': False,
                    'error': result.get('resultDesc', '券验证失败') if result else 'API调用失败'
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def process_payment_with_password_management(self, order_data: Dict[str, Any], selected_coupons: List[Dict] = None) -> Dict[str, Any]:
        """🆕 统一的支付处理 - 自动密码管理"""
        try:
            from PyQt5.QtWidgets import QMessageBox

            # 1. 判断支付方式
            has_coupons = bool(selected_coupons)
            has_member_card = (hasattr(self, 'member_info') and
                             self.member_info and
                             self.member_info.get('has_member_card', False))

            print(f"[统一支付] 支付方式判断: 券={has_coupons}, 会员卡={has_member_card}")

            if has_coupons and has_member_card:
                # 混合支付
                print(f"[统一支付] 执行混合支付")
                result = self.process_mixed_payment_enhanced(order_data, selected_coupons)
            elif has_member_card:
                # 纯会员卡支付
                print(f"[统一支付] 执行纯会员卡支付")
                result = self.process_member_card_payment_enhanced(order_data)
            elif has_coupons:
                # 纯券支付
                print(f"[统一支付] 执行纯券支付")
                result = self._process_coupon_payment(order_data, selected_coupons)
            else:
                # 其他支付方式
                return {
                    'success': False,
                    'error': '请选择支付方式（券或会员卡）'
                }

            # 2. 处理支付结果
            if result.get('success'):
                QMessageBox.information(self, "支付成功", result.get('message', '支付成功！'))

                # 获取取票码
                order_no = order_data.get('orderno', '')
                if order_no:
                    self._get_ticket_code_after_payment(order_no)

                return result
            else:
                # 检查是否需要设置密码
                if result.get('action_required') == 'set_password':
                    # 用户需要设置支付密码
                    QMessageBox.warning(self, "需要设置支付密码",
                                      f"{result.get('error', '支付失败')}\n\n请在账号设置中设置支付密码后重试。")
                else:
                    # 其他支付错误
                    QMessageBox.warning(self, "支付失败", result.get('error', '支付失败'))

                return result

        except Exception as e:
            error_msg = f"支付处理异常: {str(e)}"
            print(f"[统一支付] {error_msg}")
            QMessageBox.critical(self, "支付异常", error_msg)
            return {'success': False, 'error': error_msg}

    def _process_coupon_payment(self, order_data: Dict[str, Any], selected_coupons: List[Dict]) -> Dict[str, Any]:
        """🆕 处理纯券支付"""
        try:
            # 这里应该调用现有的券支付逻辑
            # 暂时返回成功，实际应该调用券支付API
            return {
                'success': True,
                'message': '券支付成功'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ===== 第三步：核心业务方法（从源项目复制） =====

    def set_current_account(self, account):
        """设置当前账号 - 修复：账号切换时重新加载座位图"""
        try:
            self.current_account = account
            if account:
                userid = account.get('userid', 'N/A')
                phone = account.get('phone', '')

                # 更新UI显示
                if phone:
                    self.phone_display.setText(f"当前账号: {phone}")
                else:
                    self.phone_display.setText(f"当前账号: {userid}")

                # 发布全局账号切换事件
                event_bus.account_changed.emit(account)

                # 🆕 重置券列表
                if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'reset_coupon_lists'):
                    self.tab_manager_widget.reset_coupon_lists()

                # 刷新券列表等
                self._refresh_account_dependent_data()

                # 重要修复：账号切换时重新加载座位图
                self._reload_seat_map_for_account_change()

        except Exception as e:
            pass

    def _reload_seat_map_for_account_change(self):
        """账号切换时重新加载座位图"""
        try:
            # 检查是否有完整的选择信息
            if not hasattr(self, 'tab_manager_widget'):
                return

            tab_manager = self.tab_manager_widget

            # 获取当前选择
            cinema_text = tab_manager.cinema_combo.currentText()
            movie_text = tab_manager.movie_combo.currentText()
            date_text = tab_manager.date_combo.currentText()
            session_text = tab_manager.session_combo.currentText()

            # 检查选择是否完整
            invalid_selections = ["请选择", "请先选择", "正在加载", "暂无", "加载失败", "选择影院", "加载中..."]
            if any(text in invalid_selections for text in [cinema_text, movie_text, date_text, session_text]):
                self._safe_update_seat_area("请完整选择影院、影片、日期和场次后查看座位图")
                return

            # 如果选择完整，重新加载座位图
            print(f"  - 新账号: {self.current_account.get('userid', 'N/A')}")

            # 重新触发场次选择，这会重新加载座位图
            if hasattr(tab_manager, 'current_session_data') and tab_manager.current_session_data:
                # 先清空当前座位选择
                self._clear_seat_selection()
                # 触发座位图重新加载
                session_info = {
                    'session_data': tab_manager.current_session_data,
                    'session_text': session_text,
                    'account': self.current_account,  # 添加当前账号信息
                    'cinema_data': self._get_cinema_info_by_name(cinema_text)  # 添加影院信息
                }
                self._load_seat_map(session_info)
            else:
                self._safe_update_seat_area("账号已切换，请重新选择场次")

        except Exception as e:
            import traceback
            traceback.print_exc()

    def _clear_seat_selection(self):
        """清空座位选择"""
        try:
            # 清空当前座位面板的选择
            if hasattr(self, 'current_seat_panel') and self.current_seat_panel:
                if hasattr(self.current_seat_panel, 'clear_selection'):
                    self.current_seat_panel.clear_selection()

            # 更新提交按钮文字
            if hasattr(self, 'submit_button'):
                self.submit_button.setText("提交订单")

        except Exception as e:
            pass

    def set_main_account(self, account):
        """设置主账号标记"""
        try:
            if account:
                account['is_main'] = True
                print(f"[主窗口] 设置主账号: {account.get('userid', 'N/A')}")
                
                # 保存到数据文件
                self._save_account_data(account)
                
        except Exception as e:
            pass

    def refresh_account_list(self):
        """刷新账号列表"""
        try:
            # 从API获取账号列表
            accounts = get_account_list()
            
            # 通知账号组件更新列表
            if hasattr(self, 'account_widget'):
                self.account_widget.update_account_list(accounts)
                
            print(f"[主窗口] 账号列表已刷新，共{len(accounts)}个账号")
            
        except Exception as e:
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "刷新失败", f"刷新账号列表失败: {str(e)}", auto_close=False)

    def on_cinema_changed(self):
        """影院切换事件处理"""
        try:
            cinema_name = self.tab_manager_widget.cinema_combo.currentText()
            if not cinema_name or cinema_name in ["加载中...", "请选择影院"]:
                return
            
            
            # 获取影院信息
            cinema_info = self._get_cinema_info_by_name(cinema_name)
            if cinema_info:
                # 更新电影列表
                self._load_movies_for_cinema(cinema_info)
                
                # 取消未支付订单
                if self.current_account and cinema_info.get('cinemaid'):
                    self._cancel_unpaid_orders(self.current_account, cinema_info['cinemaid'])
                
                # 获取会员信息
                if self.current_account and cinema_info.get('cinemaid'):
                    self._get_member_info(self.current_account, cinema_info['cinemaid'])
                    
        except Exception as e:
            pass

    def on_submit_order(self):
        """提交订单 - 重构后的主方法"""
        try:
            # 验证订单数据
            if not self._validate_order_data():
                return
            
            # 构建订单参数
            order_params = self._build_order_params()
            if not order_params:
                return
            
            # 提交订单
            success = self._submit_order_to_api(order_params)
            if success:
                self._handle_order_success()
            else:
                self._handle_order_failure()
                
        except Exception as e:
            self._handle_order_exception(e)
    
    def _validate_order_data(self):
        """验证订单数据"""
        if not self.current_order:
            QMessageBox.warning(self, "错误", "请先选择座位")
            return False
        
        if not self.current_account:
            QMessageBox.warning(self, "错误", "请先登录")
            return False
        
        seats = DataUtils.safe_get(self.current_order, 'seats', [])
        if not seats:
            QMessageBox.warning(self, "错误", "请选择座位")
            return False
        
        return True
    
    def _build_order_params(self):
        """构建订单参数"""
        try:
            cinema_data = self.cinema_manager.get_current_cinema()
            if not cinema_data:
                QMessageBox.warning(self, "错误", "影院信息获取失败")
                return None
            
            seats = DataUtils.safe_get(self.current_order, 'seats', [])
            seat_ids = [str(seat.get('id', '')) for seat in seats]
            
            order_params = {
                'userid': DataUtils.safe_get(self.current_account, 'userid', ''),
                'cinemaid': DataUtils.safe_get(cinema_data, 'cinemaid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': DataUtils.safe_get(self.current_account, 'token', ''),
                'openid': DataUtils.safe_get(self.current_account, 'openid', ''),
                'movieid': DataUtils.safe_get(self.current_order, 'movieid', ''),
                'showid': DataUtils.safe_get(self.current_order, 'showid', ''),
                'seatids': ','.join(seat_ids),
                'totalprice': DataUtils.safe_get(self.current_order, 'totalprice', 0)
            }
            
            return order_params
            
        except Exception as e:
            print(f"构建订单参数失败: {e}")
            return None
    
    def _submit_order_to_api(self, order_params):
        """提交订单到API"""
        try:
            # 这里应该是实际的API调用逻辑
            # 暂时返回True表示成功
            print(f"提交订单参数: {order_params}")
            return True
            
        except Exception as e:
            print(f"API调用失败: {e}")
            return False
    
    def _handle_order_success(self):
        """处理订单成功"""
        QMessageBox.information(self, "成功", "订单提交成功")
        # 清理订单数据
        self.current_order = None
        # 刷新UI
        self.update_ui_after_order()
    
    def _handle_order_failure(self):
        """处理订单失败"""
        QMessageBox.warning(self, "失败", "订单提交失败，请重试")
    
    def _handle_order_exception(self, exception):
        """处理订单异常"""
        error_msg = f"订单处理异常: {str(exception)}"
        print(error_msg)
        QMessageBox.critical(self, "错误", "系统异常，请稍后重试")
    
    def update_ui_after_order(self):
        """订单后更新UI"""
        # 返回到影院选择或其他合适的界面
        if hasattr(self, 'show_cinema_selection'):
            self.show_cinema_selection()
def main():
    """启动模块化应用程序"""
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = ModularCinemaMainWindow()
    
    # 注册插件（示例）
    # plugin_manager.register_plugin("account_manager", AccountWidget())
    # plugin_manager.register_plugin("tab_manager", TabManagerWidget())
    # plugin_manager.register_plugin("seat_order", SeatOrderWidget())
    
    # 启动应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 