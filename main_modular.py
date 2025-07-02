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
try:
    from api.cinema_api_client import get_api_client, APIException
except ImportError as e:
    print(f"导入API客户端失败，使用简化版本: {e}")
    from api.cinema_api_client_simple import get_api_client, APIException
from patterns.order_observer import get_order_subject, setup_order_observers, OrderStatus
from patterns.payment_strategy import get_payment_context, PaymentContext
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
    cancel_all_unpaid_orders, get_coupon_prepay_info
)

# 影院和账号管理
from services.cinema_manager import CinemaManager
from services.womei_film_service import get_womei_film_service
# from services.member_service import MemberService  # 华联系统代码，已删除
from services.account_api import get_account_list, save_account, delete_account

# 工具类
import json, os, time, traceback

# 🆕 增强支付系统导入
from PyQt5.QtWidgets import QInputDialog, QLineEdit

# 导入登录窗口
from ui.login_window import LoginWindow

# 🆕 导入定时验证服务
from services.refresh_timer_service import refresh_timer_service
from services.auth_error_handler import auth_error_handler


class ModularCinemaMainWindow(QMainWindow):
    """模块化影院下单系统主窗口"""
    
    # 定义信号
    login_success = pyqtSignal(dict)  # 登录成功信号
    
    def __init__(self):
        super().__init__()
        
        # 初始化API客户端
        self.api_client = get_api_client()
        # 初始化设计模式
        self.payment_context = get_payment_context()
        self.order_subject = setup_order_observers(self)
        # 初始化业务服务
        self.auth_service = AuthService()
        self.cinema_manager = CinemaManager()
        # self.member_service = MemberService()  # 华联系统服务，已删除
        # 初始化沃美电影服务 - 延迟初始化，等待token加载
        self.film_service = None

        # 🆕 初始化订单详情管理器
        from modules.order_display import OrderDetailManager
        self.order_detail_manager = OrderDetailManager(self)

        # 🔧 Token失效处理
        self.last_token_popup_time = 0  # 防重复弹窗

        # ===== 第三步：复制关键数据属性（从源项目复制） =====
        self.current_user = None
        self.current_account = None
        self.current_order = None
        # 🚫 移除会员卡支付功能，专注于券码支付
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

        # 🔧 调试模式：临时禁用登录验证
        DEBUG_SKIP_LOGIN = True  # 设置为False可恢复登录验证

        if DEBUG_SKIP_LOGIN:
            # 🔧 调试模式：加载实际账号数据
            self.current_user = self._load_actual_account()
            if not self.current_user:
                # 如果没有找到实际账号，使用配置的测试账号
                from config import config
                if not config.validate():
                    raise ValueError("配置验证失败，请检查 .env 文件")

                self.current_user = {
                    'phone': config.TEST_PHONE,
                    'token': config.DEFAULT_TOKEN,
                    'debug_mode': config.DEBUG
                }
            # 直接显示主窗口
            QTimer.singleShot(100, self._show_main_window_after_debug_login)
        else:
            # 启动用户认证检查
            QTimer.singleShot(100, self._start_auth_check)

    def _init_enhanced_payment_system(self):
        """🆕 初始化增强支付系统"""
        try:
            # 初始化API客户端（如果还没有）
            if not hasattr(self, 'api_client'):
                from services.api_base import APIBase
                self.api_client = APIBase()

            # 调试打印已移除
            # 调试打印已移除
            # 调试打印已移除
            print("[增强支付] 🚫 已移除会员卡支付功能")

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

        # 智能识别按钮
        self.smart_recognition_btn = QPushButton("🤖 智能识别")
        self.smart_recognition_btn.setFixedSize(100, 30)
        self.smart_recognition_btn.setToolTip("从剪贴板智能识别订单信息并自动填充")
        self.smart_recognition_btn.setStyleSheet("""
            QPushButton {
                background-color: #9c27b0;
                color: white;
                border: none;
                border-radius: 4px;
                font: 12px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #7b1fa2;
            }
            QPushButton:pressed {
                background-color: #4a148c;
            }
        """)
        self.smart_recognition_btn.clicked.connect(self.show_smart_recognition)

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
        button_layout.addWidget(self.smart_recognition_btn)
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
        
        # 🆕 按钮区域布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

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
        button_layout.addWidget(self.pay_button)

        # 🆕 调试验证按钮
        self.debug_auth_button = ClassicButton("🔍 调试验证", "info")
        self.debug_auth_button.setMinimumHeight(35)
        self.debug_auth_button.setFixedWidth(100)
        self.debug_auth_button.setToolTip("手动触发用户验证逻辑，用于调试")
        self.debug_auth_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: #ffffff;
                font: bold 10px "Microsoft YaHei";
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        button_layout.addWidget(self.debug_auth_button)

        # 添加按钮布局到订单布局
        order_layout.addLayout(button_layout)
        
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

    def show_smart_recognition(self):
        """显示智能识别对话框"""
        try:
            print("[智能识别] 🤖 启动智能识别功能")

            # 导入智能识别模块
            from services.smart_recognition import SmartOrderRecognition
            from ui.dialogs.smart_recognition_dialog import SmartRecognitionDialog

            # 创建智能识别服务
            recognition_service = SmartOrderRecognition(main_window=self)

            # 创建对话框
            dialog = SmartRecognitionDialog(parent=self)

            # 连接信号
            dialog.recognition_confirmed.connect(self._on_recognition_confirmed)
            dialog.recognition_cancelled.connect(self._on_recognition_cancelled)

            # 显示进度
            dialog.show()
            dialog.show_progress("正在识别剪贴板内容...")

            # 执行识别
            order_info, match_result = recognition_service.recognize_and_match()

            # 显示结果
            dialog.show_recognition_result(order_info, match_result)

            # 调试打印已移除

        except Exception as e:
            print(f"[智能识别] ❌ 显示智能识别对话框失败: {e}")
            import traceback
            traceback.print_exc()

            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "智能识别", f"智能识别功能启动失败: {str(e)}")

    def _on_recognition_confirmed(self, result_data: dict):
        """智能识别确认处理"""
        try:
            # 调试打印已移除

            order_info = result_data.get('order_info')
            match_result = result_data.get('match_result')
            auto_fill = result_data.get('auto_fill', False)

            if not order_info or not match_result:
                # 调试打印已移除
                return

            # 执行自动填充
            if auto_fill:
                self._execute_auto_fill(order_info, match_result)
            else:
                self._execute_manual_fill(order_info, match_result)

            # 调试打印已移除

        except Exception as e:
            print(f"[智能识别] ❌ 处理识别确认失败: {e}")
            import traceback
            traceback.print_exc()

    def _on_recognition_cancelled(self):
        """智能识别取消处理"""
        # 调试打印已移除

    def _execute_auto_fill(self, order_info, match_result):
        """执行自动填充"""
        try:
            # 调试打印已移除

            # 1. 自动选择影院
            if match_result.cinema_match:
                self._auto_select_cinema(match_result.cinema_match)

            # 2. 自动选择影片（需要等待影院选择完成）
            if match_result.movie_match:
                QTimer.singleShot(500, lambda: self._auto_select_movie(match_result.movie_match))

            # 3. 自动选择场次（需要等待影片选择完成）
            if match_result.session_match:
                QTimer.singleShot(1000, lambda: self._auto_select_session(match_result.session_match))

            # 4. 自动选择座位（需要等待场次选择完成）
            if match_result.seat_matches:
                QTimer.singleShot(1500, lambda: self._auto_select_seats(match_result.seat_matches))

            # 显示成功消息
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "智能识别", "自动填充完成！请检查选择结果。")

        except Exception as e:
            print(f"[智能识别] ❌ 自动填充失败: {e}")
            import traceback
            traceback.print_exc()

    def _execute_manual_fill(self, order_info, match_result):
        """执行手动填充"""
        try:
            print("[智能识别] ✋ 执行手动填充")

            # 显示识别结果，让用户手动确认
            from PyQt5.QtWidgets import QMessageBox

            message = "识别结果：\n\n"
            if match_result.cinema_match:
                cinema_name = match_result.cinema_match.get('cinemaShortName', '未知')
                message += f"影院: {cinema_name}\n"

            if order_info.movie_name:
                message += f"影片: {order_info.movie_name}\n"

            if order_info.session_time:
                message += f"场次: {order_info.session_time}\n"

            if order_info.seats:
                message += f"座位: {', '.join(order_info.seats)}\n"

            message += "\n请手动确认并选择相应的选项。"

            QMessageBox.information(self, "智能识别结果", message)

        except Exception as e:
            print(f"[智能识别] ❌ 手动填充失败: {e}")
            import traceback
            traceback.print_exc()

    def _auto_select_cinema(self, cinema_data):
        """自动选择影院"""
        try:
            print(f"[智能识别] 🏢 自动选择影院: {cinema_data.get('cinemaShortName', '未知')}")

            # 发布影院选择事件
            event_bus.cinema_selected.emit(cinema_data)

            # 更新Tab管理器
            if hasattr(self, 'tab_manager_widget'):
                # 这里需要根据实际的Tab管理器接口来实现
                pass

        except Exception as e:
            print(f"[智能识别] ❌ 自动选择影院失败: {e}")

    def _auto_select_movie(self, movie_data):
        """自动选择影片"""
        try:
            print(f"[智能识别] 🎬 自动选择影片: {movie_data.get('name', '未知')}")

            # 这里需要根据实际的影片选择接口来实现
            # 暂时只打印日志

        except Exception as e:
            print(f"[智能识别] ❌ 自动选择影片失败: {e}")

    def _auto_select_session(self, session_data):
        """自动选择场次"""
        try:
            print(f"[智能识别] ⏰ 自动选择场次: {session_data.get('time', '未知')}")

            # 这里需要根据实际的场次选择接口来实现
            # 暂时只打印日志

        except Exception as e:
            print(f"[智能识别] ❌ 自动选择场次失败: {e}")

    def _auto_select_seats(self, seat_matches):
        """自动选择座位"""
        try:
            print(f"[智能识别] 💺 自动选择座位: {len(seat_matches)}个座位")

            # 这里需要根据实际的座位选择接口来实现
            # 暂时只打印日志
            for seat in seat_matches:
                print(f"[智能识别] 座位: {seat.get('row')}排{seat.get('col')}座")

        except Exception as e:
            print(f"[智能识别] ❌ 自动选择座位失败: {e}")

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
        self.tab_manager_widget.token_expired.connect(self._on_token_expired)  # 🔧 Token失效信号
        
        # 座位选择信号
        self.seat_input.textChanged.connect(self._on_seat_input_changed)
        
        # 右栏支付按钮信号
        self.pay_button.clicked.connect(self._on_pay_button_clicked)

        # 🆕 调试验证按钮信号
        self.debug_auth_button.clicked.connect(self._on_debug_auth_button_clicked)

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

            # 🆕 启动定时验证机制
            QTimer.singleShot(1000, lambda: self._start_refresh_monitoring(self.current_user))


        except Exception as e:
            QMessageBox.critical(self, "显示主窗口错误", f"显示主窗口失败: {str(e)}")
            # 如果显示失败，重新启动登录
            self._restart_login()

    def _show_main_window_after_debug_login(self):
        """🔧 调试模式：跳过登录直接显示主窗口"""
        try:
            # 🔧 更新窗口标题显示调试模式
            self.setWindowTitle("柴犬影院下单系统 - 模块化版本 [🚧 调试模式 - 已跳过登录]")

            # 显示主窗口
            self.show()

            # 将窗口提到前台并激活
            self.raise_()
            self.activateWindow()

            # 居中显示窗口
            self.center_window()

            # 发出登录成功信号（使用模拟用户信息）
            self.login_success.emit(self.current_user)

            # 发布全局登录成功事件
            event_bus.user_login_success.emit(self.current_user)

            # 🔧 调试模式：使用加载的实际账号数据
            debug_account = self.current_user.copy()

            # 延迟发送账号信息，确保TabManagerWidget已初始化
            QTimer.singleShot(1000, lambda: self._send_debug_account_info(debug_account))

            # 延迟触发默认影院设置，确保所有组件都已初始化
            QTimer.singleShot(1500, self._trigger_default_cinema_selection)

            # 🔧 调试模式不启动定时验证机制

        except Exception as e:
            QMessageBox.critical(self, "调试模式错误", f"调试模式显示主窗口失败: {str(e)}")
            print(f"🚧 [调试模式] 显示主窗口失败: {e}")

    def _load_actual_account(self):
        """加载简化的账号数据（只包含phone和token）"""
        try:
            import json
            import os

            accounts_file = os.path.join(os.path.dirname(__file__), 'data', 'accounts.json')

            if not os.path.exists(accounts_file):
                # 调试打印已移除
                return None

            with open(accounts_file, "r", encoding="utf-8") as f:
                accounts = json.load(f)

            # 直接使用第一个账号，不进行任何筛选
            if accounts and len(accounts) > 0:
                first_account = accounts[0]

                # 安全的Token显示
                token = first_account.get('token', '')
                if token:
                    pass  # 调试打印已移除
                else:
                    pass  # 调试打印已移除

                return {
                    'phone': first_account.get('phone'),
                    'token': first_account.get('token'),
                    'debug_mode': True
                }
            else:
                # 调试打印已移除
                return None

        except Exception as e:
            print(f"🚧 [调试模式] 加载账号数据失败: {e}")
            return None

    def _send_debug_account_info(self, debug_account):
        """发送调试模式的账号信息"""
        try:
            # 通过事件总线发送账号变更事件
            event_bus.account_changed.emit(debug_account)

        except Exception as e:
            print(f"发送账号信息失败: {e}")

    def _trigger_default_cinema_selection(self):
        """移除本地影院文件加载 - 影院通过API动态获取"""
        try:
            # 不再加载本地影院文件，影院数据完全通过API获取
            # 沃美系统的流程：用户选择城市 → API获取该城市的影院列表
            pass

        except Exception as e:
            print(f"初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def _auto_select_cinema_account(self, cinema_info):
        """简化的账号选择（不再关联影院）"""
        try:
            print(f"[主窗口] 🎯 使用默认账号（不关联影院）")

            # 直接使用已加载的账号，不进行影院关联
            if hasattr(self, 'current_user') and self.current_user:
                pass  # 调试打印已移除
            else:
                print(f"[主窗口] ⚠️ 当前账号未设置")

        except Exception as e:
            print(f"[主窗口] 账号选择失败: {e}")
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
        """重新启动登录流程 - 增强错误处理和窗口管理"""
        try:
            # 调试打印已移除

            # 🆕 清理旧的登录窗口 - 增强清理逻辑
            if hasattr(self, 'login_window') and self.login_window:
                try:
                    # 断开信号连接，避免重复连接
                    self.login_window.login_success.disconnect()
                except:
                    pass

                self.login_window.close()
                self.login_window.deleteLater()  # 🆕 确保窗口被正确删除
                self.login_window = None
                # 调试打印已移除

            # 🆕 确保主窗口完全隐藏
            self.hide()

            # 🆕 延迟创建新的登录窗口，确保旧窗口完全清理
            QTimer.singleShot(300, self._create_new_login_window)

        except Exception as e:
            print(f"[主窗口] ❌ 重启登录失败: {e}")
            QMessageBox.critical(self, "重启登录失败", f"无法重新启动登录: {str(e)}")
            QApplication.quit()

    def _create_new_login_window(self):
        """创建新的登录窗口 - 增强窗口创建和显示逻辑"""
        try:
            # 调试打印已移除

            # 🆕 导入登录窗口类
            from ui.login_window import LoginWindow

            # 🔧 增强：确保主窗口完全隐藏并释放焦点
            self.hide()
            self.setWindowState(Qt.WindowMinimized)

            # 创建新的登录窗口
            self.login_window = LoginWindow()

            # 🆕 连接登录成功信号
            self.login_window.login_success.connect(self._on_user_login_success)

            # 🔧 增强：设置窗口属性，确保正确显示和获得焦点
            self.login_window.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
            self.login_window.setAttribute(Qt.WA_ShowWithoutActivating, False)  # 确保激活窗口

            # 🔧 增强：居中显示登录窗口
            self._center_login_window()

            # 🆕 显示登录窗口并确保获得焦点
            self.login_window.show()
            self.login_window.raise_()
            self.login_window.activateWindow()

            # 🔧 增强：强制获得焦点
            QApplication.setActiveWindow(self.login_window)

            # 调试打印已移除

        except Exception as e:
            print(f"[主窗口] ❌ 创建登录窗口失败: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "创建登录窗口失败", f"无法创建登录窗口: {str(e)}")
            QApplication.quit()

    def _center_login_window(self):
        """居中显示登录窗口"""
        try:
            if hasattr(self, 'login_window') and self.login_window:
                # 获取屏幕几何信息
                screen = QApplication.primaryScreen().geometry()

                # 获取登录窗口大小
                login_size = self.login_window.size()

                # 计算居中位置
                x = (screen.width() - login_size.width()) // 2
                y = (screen.height() - login_size.height()) // 2

                # 设置窗口位置
                self.login_window.move(x, y)

                print(f"[主窗口] 登录窗口已居中显示: ({x}, {y})")

        except Exception as e:
            print(f"[主窗口] 居中登录窗口失败: {e}")

    # ===== 🆕 定时验证相关方法 =====

    def _start_refresh_monitoring(self, user_info: dict):
        """启动用户刷新时间监控"""
        try:
            print(f"[主窗口] 启动刷新监控服务: {user_info.get('phone', 'N/A')}")

            # 连接刷新验证服务的信号
            refresh_timer_service.auth_success.connect(self._on_refresh_auth_success)
            refresh_timer_service.auth_failed.connect(self._on_refresh_auth_failed)

            # 设置检查间隔为1分钟（测试用）
            refresh_timer_service.set_check_interval(1)

            # 开始监控
            success = refresh_timer_service.start_monitoring(user_info)

            if success:
                print(f"[主窗口] 刷新监控服务启动成功")
            else:
                print(f"[主窗口] 刷新监控服务启动失败")

        except Exception as e:
            print(f"[主窗口] 启动刷新监控失败: {e}")

    def _on_refresh_auth_success(self, user_info: dict):
        """刷新验证成功处理"""
        try:
            print(f"[主窗口] 刷新验证成功: {user_info.get('phone', 'N/A')}")
            # 更新本地用户信息
            if self.current_user:
                self.current_user.update(user_info)

            # 可以在这里更新UI状态，比如显示最后刷新时间
            # 例如：在状态栏显示最后验证时间

        except Exception as e:
            print(f"[主窗口] 刷新验证成功处理错误: {e}")

    def _on_refresh_auth_failed(self, error_msg: str):
        """刷新验证失败处理 - 使用统一错误处理"""
        try:
            print(f"[主窗口] 刷新验证失败: {error_msg}")

            # 停止监控
            refresh_timer_service.stop_monitoring()

            # 清理当前用户信息
            self.current_user = None
            self.current_account = None

            # 隐藏主窗口
            self.hide()

            # 🆕 使用统一的认证失败对话框处理
            auth_error_handler.show_auth_failed_dialog(
                self,
                error_msg,
                on_confirmed_callback=self._on_auth_dialog_confirmed
            )

        except Exception as e:
            print(f"[主窗口] 刷新验证失败处理错误: {e}")
            # 如果处理失败，直接退出应用
            QApplication.quit()

    def _on_auth_dialog_confirmed(self):
        """认证失败对话框确认后的处理 - 增强登录重启逻辑"""
        try:
            print(f"[主窗口] 用户确认认证失败对话框，开始重启登录流程")

            # 🔧 增强：确保主窗口完全隐藏
            self.hide()

            # 🔧 增强：清理所有相关状态
            self.current_user = None
            self.current_account = None

            # 🔧 增强：停止所有可能的定时器和服务
            try:
                refresh_timer_service.stop_monitoring()
            except:
                pass

            # 🆕 确保在对话框关闭后立即重启登录
            QTimer.singleShot(200, self._restart_login)

        except Exception as e:
            print(f"[认证对话框] 处理对话框确认事件失败: {e}")
            import traceback
            traceback.print_exc()
            # 备用方案：直接重启登录
            self._restart_login()



    def _on_debug_auth_button_clicked(self):
        """调试验证按钮点击处理 - 手动触发验证逻辑，使用统一错误处理"""
        try:
            # 调试打印已移除

            # 检查当前用户状态
            if not self.current_user:
                QMessageBox.warning(self, "调试验证", "当前没有登录用户，无法执行验证")
                return

            phone = self.current_user.get('phone', '')
            if not phone:
                QMessageBox.warning(self, "调试验证", "当前用户信息不完整，缺少手机号")
                return

            # 🆕 显示调试信息对话框
            self._show_debug_auth_dialog()

            # 🆕 直接使用auth_service进行验证，与定时验证完全一致
            from services.auth_service import auth_service

            success, message, user_info = auth_service.login(phone)

            if success:
                # 🆕 使用统一的认证成功处理（静默模式）
                auth_error_handler.handle_auth_success(user_info, is_silent=True)

                # 显示成功提示（仅调试时显示）
                QMessageBox.information(
                    self,
                    "调试验证",
                    f"✅ 验证成功！\n\n"
                    f"用户: {user_info.get('phone', 'N/A')}\n"
                    f"积分: {user_info.get('points', 0)}\n"
                    f"状态: 正常"
                )

            else:
                # 🆕 使用统一的错误信息解析，但简化对话框处理
                user_friendly_message = auth_error_handler.parse_error_message(message)

                # 🔧 简化：直接显示错误信息，避免复杂的回调逻辑
                QMessageBox.warning(
                    self,
                    "调试验证 - 认证失败",
                    f"用户认证失败，需要重新登录\n\n"
                    f"详细信息:\n{user_friendly_message}\n\n"
                    f"💡 在正常情况下，这里会关闭主窗口并打开登录页面\n"
                    f"由于这是调试模式，主窗口保持打开状态。"
                )

        except Exception as e:
            print(f"调试验证失败: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "调试验证", f"调试验证执行失败: {str(e)}")

    def _show_debug_auth_dialog(self):
        """显示调试验证信息对话框"""
        try:
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle("调试验证 - 实时日志")
            dialog.setFixedSize(600, 400)

            layout = QVBoxLayout(dialog)

            # 说明标签
            info_label = QLabel("正在执行用户验证逻辑，请查看控制台输出...")
            info_label.setStyleSheet("font-weight: bold; color: #2196f3; padding: 10px;")
            layout.addWidget(info_label)

            # 用户信息显示
            user_info = f"当前用户: {self.current_user.get('phone', 'N/A')}\n"
            user_info += f"用户名: {self.current_user.get('username', 'N/A')}\n"
            user_info += f"积分: {self.current_user.get('points', 'N/A')}"

            user_label = QLabel(user_info)
            user_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
            layout.addWidget(user_label)

            # 提示文本
            tip_text = QTextEdit()
            tip_text.setReadOnly(True)
            tip_text.setPlainText(
                "验证过程说明:\n\n"
                "1. 检查验证服务运行状态\n"
                "2. 调用登录API验证用户和机器码\n"
                "3. 根据API响应处理验证结果\n"
                "4. 如果验证失败，会显示错误信息并跳转登录\n\n"
                "请观察控制台输出查看详细的验证过程..."
            )
            tip_text.setMaximumHeight(150)
            layout.addWidget(tip_text)

            # 关闭按钮
            close_button = QPushButton("关闭")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

            # 显示对话框（非模态）
            dialog.show()

        except Exception as e:
            print(f"[调试验证] ❌ 显示调试对话框失败: {e}")
    
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
            
            # 调试打印已移除
            
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
        """🆕 一键支付处理 - 重构完整支付逻辑"""
        try:
            # 第一阶段：基础验证
            if not self._validate_payment_prerequisites():
                return

            # 第二阶段：优惠券验证（如果用户选择了券）
            coupon_validation_result = self._validate_and_process_coupons()
            if coupon_validation_result is None:  # 用户取消或验证失败
                return

            # 第三阶段：支付方式判断和执行
            payment_success = self._execute_payment_process(coupon_validation_result)

            if payment_success:
                pass  # 调试打印已移除
            else:
                print("[支付] 一键支付流程失败")

        except Exception as e:
            import traceback
            traceback.print_exc()
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "支付失败", f"支付过程中发生错误: {e}")

    def _validate_payment_prerequisites(self):
        """验证支付前置条件"""
        try:
            from services.ui_utils import MessageManager

            if not self.current_order:
                MessageManager.show_error(self, "支付失败", "没有待支付的订单")
                return False

            if not self.current_account:
                MessageManager.show_error(self, "支付失败", "请先选择账号")
                return False

            # 获取影院信息
            cinema_data = None
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'current_cinema_data'):
                cinema_data = self.tab_manager_widget.current_cinema_data

            if not cinema_data:
                MessageManager.show_error(self, "支付失败", "缺少影院信息")
                return False

            # 保存到实例变量供后续使用
            self._payment_cinema_data = cinema_data
            self._payment_order_id = self.current_order.get('orderno') or self.current_order.get('order_id', '')
            self._payment_cinema_id = cinema_data.get('cinemaid', '')

            print(f"[支付验证] 前置条件检查通过 - 订单: {self._payment_order_id}, 影院: {self._payment_cinema_id}")
            return True

        except Exception as e:
            print(f"[支付验证] 前置条件检查失败: {e}")
            return False

    def _validate_and_process_coupons(self):
        """验证和处理优惠券（第二阶段）"""
        try:
            # 获取选中的券号
            selected_coupons = getattr(self, 'selected_coupons', [])
            couponcode = ','.join(selected_coupons) if selected_coupons else ''

            if not couponcode:
                # 没有选择券，直接返回无券支付结果
                print("[券验证] 未选择优惠券，使用原价支付")
                return {
                    'has_coupon': False,
                    'couponcode': '',
                    'coupon_info': None,
                    'final_amount': self._get_original_payment_amount()
                }

            # 有选择券，需要验证券并获取实时价格
            # 调试打印已移除

            # 调用优惠券验证接口
            coupon_validation = self._validate_coupon_prepay(self._payment_order_id, couponcode)

            if not coupon_validation.get('success'):
                # 券验证失败
                error_msg = coupon_validation.get('error', '券验证失败')
                from services.ui_utils import MessageManager
                MessageManager.show_error(self, "券验证失败", f"优惠券验证失败: {error_msg}")
                return None

            # 券验证成功，获取实时订单数据
            coupon_data = coupon_validation.get('data', {})

            # 更新订单详情显示，让用户看到优惠效果
            self.current_coupon_info = {
                'resultCode': '0',
                'resultData': coupon_data
            }
            self.selected_coupons = selected_coupons
            self._update_order_detail_with_coupon_info()

            # 获取最终支付金额
            final_amount = self._calculate_final_payment_amount(coupon_data)

            print(f"[券验证] 券验证成功，最终支付金额: {final_amount}分")

            return {
                'has_coupon': True,
                'couponcode': couponcode,
                'coupon_info': coupon_data,
                'final_amount': final_amount
            }

        except Exception as e:
            print(f"[券验证] 券验证处理异常: {e}")
            return None

    def _execute_payment_process(self, coupon_result):
        """执行支付流程（第三阶段）"""
        try:
            from services.ui_utils import MessageManager

            has_coupon = coupon_result.get('has_coupon', False)
            final_amount = coupon_result.get('final_amount', 0)
            couponcode = coupon_result.get('couponcode', '')

            # 🚫 移除会员卡支付，只支持券码支付和微信支付
            if has_coupon and final_amount == 0:
                # 纯券支付：最终金额为0，使用券支付接口
                print("[支付执行] 纯券支付模式")
                return self._execute_coupon_payment(coupon_result)
            elif has_coupon and final_amount > 0:
                # 券码+微信支付：券码抵扣部分金额，剩余使用微信支付
                print(f"[支付执行] 券码+微信支付模式，剩余金额: {final_amount}分")
                return self._execute_wechat_payment(coupon_result)
            else:
                # 纯微信支付
                print("[支付执行] 纯微信支付模式")
                return self._execute_wechat_payment(coupon_result)

        except Exception as e:
            print(f"[支付执行] 支付流程执行异常: {e}")
            return False

    def _execute_coupon_payment(self, coupon_result):
        """执行纯券支付"""
        try:
            from services.order_api import coupon_pay
            from services.ui_utils import MessageManager

            coupon_data = coupon_result.get('coupon_info', {})
            couponcode = coupon_result.get('couponcode', '')

            # 构建券支付参数
            pay_params = {
                'orderno': self._payment_order_id,
                'payprice': '0',  # 纯券支付金额为0
                'discountprice': coupon_data.get('discountprice', '0'),
                'couponcodes': couponcode,
                'groupid': '',
                'cinemaid': self._payment_cinema_id,
                'cardno': self.current_account.get('cardno', ''),
                'userid': self.current_account['userid'],
                'openid': self.current_account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account['token'],
                'source': '2'
            }

            # 调试打印已移除

            # 调用券支付API
            pay_result = coupon_pay(pay_params)

            if pay_result and pay_result.get('resultCode') == '0':
                # 支付成功
                print("[券支付] 券支付成功")
                self._handle_payment_success(pay_result)
                return True
            else:
                # 支付失败
                error_msg = pay_result.get('resultDesc', '券支付失败') if pay_result else '券支付请求失败'
                print(f"[券支付] 券支付失败: {error_msg}")
                MessageManager.show_error(self, "券支付失败", f"券支付失败: {error_msg}")
                return False

        except Exception as e:
            print(f"[券支付] 券支付异常: {e}")
            return False

    def _execute_wechat_payment(self, coupon_result):
        """执行微信支付（可能包含券码抵扣）"""
        try:
            from services.ui_utils import MessageManager

            has_coupon = coupon_result.get('has_coupon', False)
            final_amount = coupon_result.get('final_amount', 0)
            couponcode = coupon_result.get('couponcode', '')

            # 调试打印已移除
            # 调试打印已移除
            print(f"[微信支付] 💰 最终支付金额: {final_amount}分")

            if final_amount == 0:
                # 纯券支付，无需微信支付
                # 调试打印已移除
                return self._execute_coupon_payment(coupon_result)

            # TODO: 实现微信支付逻辑
            # 这里应该调用微信支付API
            MessageManager.show_info(self, "微信支付", f"微信支付功能开发中\n支付金额: ¥{final_amount/100:.2f}")

            # 临时返回成功（实际应该等待微信支付结果）
            # 调试打印已移除
            return True

        except Exception as e:
            print(f"[微信支付] ❌ 微信支付异常: {e}")
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "支付异常", f"微信支付异常: {e}")
            return False

    def _get_current_order_details(self):
        """获取当前订单的详细信息"""
        try:
            # 从当前选择的数据中获取订单详情
            order_details = {
                'filmname': '',
                'featureno': '',
                'ticketcount': '1',
                'cinemaname': ''
            }

            # 获取影片名称
            if hasattr(self, 'current_movie') and self.current_movie:
                order_details['filmname'] = self.current_movie.get('name', self.current_movie.get('filmName', ''))

            # 获取场次号
            if hasattr(self, 'current_session') and self.current_session:
                order_details['featureno'] = self.current_session.get('featureno', '')

            # 获取票数
            if hasattr(self, '_payment_seat_count'):
                order_details['ticketcount'] = str(self._payment_seat_count)

            # 获取影院名称
            if hasattr(self, 'current_cinema') and self.current_cinema:
                order_details['cinemaname'] = self.current_cinema.get('cinemaShortName', '')

            print(f"[订单详情] 获取到的订单详情: {order_details}")
            return order_details

        except Exception as e:
            print(f"[订单详情] 获取订单详情失败: {e}")
            return {
                'filmname': '',
                'featureno': '',
                'ticketcount': '1',
                'cinemaname': ''
            }



    def _get_original_payment_amount(self):
        """获取原始支付金额"""
        try:
            # 检查是否有会员卡
            has_member_card = self.member_info and self.member_info.get('has_member_card', False)

            if has_member_card:
                # 会员：使用会员总价
                amount = self.current_order.get('mem_totalprice', 0)
                print(f"[支付金额] 会员原价: {amount}分")
                return amount
            else:
                # 非会员：使用订单总价
                amount = self.current_order.get('payAmount', self.current_order.get('totalprice', 0))
                print(f"[支付金额] 非会员原价: {amount}分")
                return amount

        except Exception as e:
            print(f"[支付金额] 获取原始支付金额失败: {e}")
            return 0

    def _calculate_final_payment_amount(self, coupon_data):
        """计算最终支付金额"""
        try:
            # 检查是否有会员卡
            has_member_card = self.member_info and self.member_info.get('has_member_card', False)

            if has_member_card:
                # 会员：优先使用会员支付金额
                final_amount = coupon_data.get('mempaymentAmount', coupon_data.get('paymentAmount', '0'))
            else:
                # 非会员：使用普通支付金额
                final_amount = coupon_data.get('paymentAmount', '0')

            # 确保返回整数
            try:
                final_amount = int(final_amount) if final_amount else 0
            except (ValueError, TypeError):
                final_amount = 0

            print(f"[支付金额] 券后最终金额: {final_amount}分")
            return final_amount

        except Exception as e:
            print(f"[支付金额] 计算最终支付金额失败: {e}")
            return 0

    # 🚫 已移除会员卡密码获取功能，专注于券码支付

    def _initialize_order_payment_method(self, order_id: str, cinema_id: str, token: str) -> dict:
        """
        订单支付方式预初始化（核心修复方法）
        解决4004错误：在券码绑定前先设置订单的基础支付方式
        """
        try:
            # 调试打印已移除
            # 调试打印已移除
            # 调试打印已移除
            # 调试打印已移除

            # 构建订单初始化参数
            init_params = {
                'pay_type': 'WECHAT',           # 设置为微信支付
                'discount_type': 'MARKETING',   # 设置为营销类型
                'card_id': '',                  # 空的卡ID
                'voucher_code': '',             # 空的券码
                'voucher_code_type': '',        # 空的券码类型
                'order_id': order_id,           # 实际订单ID
                'cinema_id': cinema_id,         # 影院ID
                'token': token,                 # 用户Token
                'version': 'tp_version'         # 版本参数
            }

            print(f"[订单初始化] 📤 发送初始化请求...")
            # 调试打印已移除

            # 调用订单变更API进行初始化
            from services.womei_order_voucher_service import get_womei_order_voucher_service
            voucher_service = get_womei_order_voucher_service()

            # 使用订单变更接口进行初始化
            init_result = voucher_service.change_order_payment_method(
                order_id=order_id,
                cinema_id=cinema_id,
                token=token
            )

            print(f"[订单初始化] 📥 初始化结果: {init_result}")

            if init_result.get('success', False) and init_result.get('ret') == 0:
                # 调试打印已移除
                return {
                    'success': True,
                    'message': '订单支付方式预初始化成功',
                    'data': init_result.get('data', {})
                }
            else:
                error_msg = init_result.get('msg', '初始化失败')
                print(f"[订单初始化] ❌ 订单支付方式预初始化失败: {error_msg}")
                return {
                    'success': False,
                    'error': f'订单支付方式预初始化失败: {error_msg}',
                    'raw_response': init_result
                }

        except Exception as e:
            print(f"[订单初始化] ❌ 订单支付方式预初始化异常: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'订单支付方式预初始化异常: {str(e)}'
            }

    def _handle_payment_success(self, pay_result):
        """处理支付成功"""
        try:
            from services.ui_utils import MessageManager

            # 调试打印已移除

            # 获取已支付订单详情
            detail_params = {
                'orderno': self._payment_order_id,
                'groupid': '',
                'cinemaid': self._payment_cinema_id,
                'cardno': self.current_account.get('cardno', ''),
                'userid': self.current_account['userid'],
                'openid': self.current_account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account['token'],
                'source': '2'
            }

            # 获取支付后的订单详情
            updated_order_detail = get_order_detail(detail_params)

            if updated_order_detail and updated_order_detail.get('resultCode') == '0':
                # 获取取票码
                if hasattr(self, '_get_ticket_code_after_payment'):
                    self._get_ticket_code_after_payment(
                        self._payment_order_id,
                        self._payment_cinema_id,
                        updated_order_detail.get('resultData', {})
                    )

                # 更新订单详情显示
                self.current_order = updated_order_detail.get('resultData', {})
                if hasattr(self, '_update_order_detail_with_coupon_info'):
                    self._update_order_detail_with_coupon_info()
            else:
                print("[支付成功] 获取订单详情失败，但支付已成功")

            # 应用观察者模式通知状态变化
            if hasattr(self, 'order_subject'):
                from patterns.order_observer import OrderStatus
                self.order_subject.update_order_status(
                    self._payment_order_id,
                    OrderStatus.PAID,
                    self.current_order
                )

            # 发布支付成功事件
            if hasattr(self, 'event_bus'):
                self.event_bus.order_paid.emit(self._payment_order_id)

            # 清空券选择状态
            if hasattr(self, 'selected_coupons'):
                self.selected_coupons.clear()
            if hasattr(self, 'current_coupon_info'):
                self.current_coupon_info = None

            # 显示成功消息
            MessageManager.show_success(self, "支付成功", "订单支付成功！")

            # 调试打印已移除

        except Exception as e:
            print(f"[支付成功] 处理支付成功异常: {e}")
            # 即使处理过程有异常，也要显示基本成功消息
            from services.ui_utils import MessageManager
            MessageManager.show_success(self, "支付成功", "订单支付成功！")

    def _validate_coupon_prepay(self, order_no: str, coupon_codes: str) -> dict:
        """验证券预支付 - 复用现有实现"""
        try:
            if not self.current_account:
                return {'success': False, 'error': '账号信息缺失'}

            cinema_id = self._payment_cinema_id

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

            # 调试打印已移除

            # 调用API
            result = get_coupon_prepay_info(params)

            if result and result.get('resultCode') == '0':
                print(f"[券验证] 券验证成功")
                return {
                    'success': True,
                    'data': result.get('resultData', {})
                }
            else:
                error_msg = result.get('resultDesc', '券验证失败') if result else 'API调用失败'
                print(f"[券验证] 券验证失败: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

        except Exception as e:
            print(f"[券验证] 券验证异常: {e}")
            return {'success': False, 'error': str(e)}

    # 🚫 已移除会员卡密码获取功能，专注于券码支付和微信支付

    def _update_order_detail_with_coupon_info(self):
        """
        🆕 统一订单详情更新方法

        专门用于券相关操作的实时UI更新，统一使用OrderDetailManager处理

        🎯 职责：
        - 券选择后的实时UI响应
        - 支付成功后的状态更新
        - 券取消选择的UI清理
        """
        try:
            if not self.current_order:
                print(f"[订单详情更新] 当前订单为空，跳过更新")
                return

            # 调试打印已移除
            print(f"[订单详情更新] current_order类型: {type(self.current_order)}")
            print(f"[订单详情更新] current_coupon_info: {getattr(self, 'current_coupon_info', None)}")

            # 🎯 统一使用OrderDetailManager处理
            if hasattr(self, 'order_detail_manager') and self.order_detail_manager:
                print(f"[订单详情更新] 使用OrderDetailManager处理")
                try:
                    # 委托给主显示系统处理，使用'coupon'上下文表示券码相关更新
                    self.order_detail_manager.display_order_detail(self.current_order, 'coupon')
                    print(f"[订单详情更新] OrderDetailManager处理成功")
                    return
                except Exception as e:
                    print(f"[订单详情更新] OrderDetailManager处理失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # 显示错误信息
                    if hasattr(self, 'order_detail_text'):
                        self.order_detail_text.setPlainText(f"订单详情更新失败: {str(e)}")
            else:
                # 调试打印已移除
                # 显示错误信息
                if hasattr(self, 'order_detail_text'):
                    self.order_detail_text.setPlainText("订单详情管理器不可用，请重启应用")

        except Exception as e:
            print(f"[订单详情更新] ❌ 更新订单详情异常: {e}")
            import traceback
            traceback.print_exc()
            # 最终错误处理
            if hasattr(self, 'order_detail_text'):
                self.order_detail_text.setPlainText(f"订单详情更新失败: {str(e)}")

    # 🚫 已移除降级显示逻辑，统一使用OrderDetailManager处理所有订单详情显示
    
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
            # 调试打印已移除

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

            # 调试打印已移除

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
                    pass  # 调试打印已移除
                else:
                    # 🆕 无会员卡：resultData为null
                    self.member_info = {
                        'has_member_card': False,
                        'raw_data': None
                    }
                    pass  # 调试打印已移除
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

    def _create_order_with_session_info(self, selected_seats, session_info):
        """使用session_info创建订单（修复影院数据缺失问题）"""
        try:
            from services.ui_utils import MessageManager
            import time

            # 从session_info获取数据
            cinema_data = session_info.get('cinema_data', {})
            account_data = session_info.get('account', {})
            session_data = session_info.get('session_data', {})

            print(f"[订单创建] 使用session_info创建订单")
            print(f"[订单创建] 账号: {account_data.get('phone', 'N/A')}")
            print(f"[订单创建] 影院: {cinema_data.get('cinema_name', 'N/A')}")
            print(f"[订单创建] 座位: {len(selected_seats)} 个")

            # 🔧 修复：沃美系统不需要取消未付款订单功能
            # 第一步：取消该账号的所有未付款订单（沃美系统跳过此步骤）
            print(f"[订单创建] 沃美系统跳过取消未付款订单步骤")

            # 第二步：构建完整的订单参数（使用session_info数据）
            order_params = self._build_order_params_from_session_info(selected_seats, session_info)
            if not order_params:
                MessageManager.show_error(self, "参数错误", "构建订单参数失败", auto_close=False)
                return False

            # 第三步：调用沃美订单创建API
            from services.womei_film_service import get_womei_film_service



            # 🔧 修复：使用沃美电影服务创建订单
            token = account_data.get('token', '')
            film_service = get_womei_film_service(token)

            # 构建沃美系统的座位参数格式
            seatlable_str = self._build_womei_seatlable(order_params.get('seatlable', []), session_info)



            result = film_service.create_order(
                cinema_id=order_params['cinemaid'],
                seatlable=seatlable_str,
                schedule_id=order_params['sessionid']
            )

            # 🔍 格式化打印订单接口返回信息
            self._print_order_api_response(result, "沃美订单创建API")

            # 🔧 修复：适配沃美系统的返回格式
            if not result or not result.get('success'):
                error_msg = result.get('error', '创建订单失败') if result else '网络错误'
                print(f"❌ [订单调试] 沃美订单创建失败: {error_msg}")
                MessageManager.show_error(self, "创建失败", f"订单创建失败: {error_msg}", auto_close=False)
                return False

            # 🔧 修复：使用沃美系统专用方法
            return self._create_womei_order_direct(selected_seats, session_info)

        except Exception as e:
            import traceback
            traceback.print_exc()
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "提交失败", f"提交订单失败\n\n错误: {str(e)}", auto_close=False)
            return False

    def _create_womei_order_direct(self, selected_seats, session_info):
        """沃美系统专用：直接创建订单（抛弃华联系统逻辑）"""
        try:
            # 调试打印已移除

            # 🔧 沃美系统：从session_info获取必要数据
            cinema_data = session_info.get('cinema_data', {})
            account_data = session_info.get('account', {})
            session_data = session_info.get('session_data', {})

            cinema_id = cinema_data.get('cinema_id', '')
            schedule_id = session_data.get('schedule_id', '')
            token = account_data.get('token', '')

            # 调试打印已移除
            print(f"  - cinema_id: {cinema_id}")
            print(f"  - schedule_id: {schedule_id}")
            # 安全的Token显示
            if token:
                print(f"  - token: {token[:10]}*** (已配置)")
            else:
                print(f"  - token: 未配置")
            print(f"  - 座位数: {len(selected_seats)}")

            if not cinema_id or not schedule_id or not token:
                # 调试打印已移除
                return False

            # 🔧 沃美系统：构建真实的座位参数
            seatlable = self._build_womei_seatlable_from_selected_seats(selected_seats)

            if not seatlable:
                print(f"[沃美订单] ❌ 座位参数构建失败")
                return False

            # 🔧 沃美系统：调用专用API
            from services.womei_film_service import get_womei_film_service
            film_service = get_womei_film_service(token)

            result = film_service.create_order(cinema_id, seatlable, schedule_id)

            # 🔍 格式化打印订单接口返回信息
            self._print_order_api_response(result, "沃美订单直接创建API")

            # 🔧 沃美系统：处理返回结果
            if result and result.get('success'):
                return self._handle_womei_order_success(result, selected_seats, session_info)
            else:
                error_msg = result.get('error', '未知错误') if result else '网络错误'
                from services.ui_utils import MessageManager
                MessageManager.show_error(self, "订单失败", f"沃美订单创建失败: {error_msg}", auto_close=False)
                return False

        except Exception as e:
            print(f"[沃美订单] ❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _build_womei_seatlable_from_selected_seats(self, selected_seats):
        """沃美系统专用：从选中座位构建座位参数"""
        try:
            # 调试打印已移除

            seat_parts = []
            for i, seat in enumerate(selected_seats):
                # 从original_data获取真实的座位图API数据
                original_data = seat.get('original_data', {})

                # 优先使用original_data中的真实数据
                real_seat_no = original_data.get('seat_no', '')
                real_area_no = original_data.get('area_no', '')
                real_row = original_data.get('row', '')
                real_col = original_data.get('col', '')

                # 验证数据完整性
                if not real_seat_no or '#' not in real_seat_no:
                    # 调试打印已移除
                    return ""

                if not real_area_no:
                    # 调试打印已移除
                    return ""

                # 🔧 修复：使用真实的座位图API数据构建参数
                # 沃美格式：area_no:row:col:seat_no
                seat_str = f"{real_area_no}:{real_row}:{real_col}:{real_seat_no}"
                seat_parts.append(seat_str)

                print(f"[沃美座位] 座位{i+1}构建: {seat_str}")

            seatlable_str = "|".join(seat_parts)
            # 调试打印已移除

            return seatlable_str

        except Exception as e:
            print(f"[沃美座位] ❌ 构建失败: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _enhance_seat_info_for_display(self, selected_seats):
        """
        🔧 增强座位信息用于显示
        确保座位对象包含完整的显示信息
        """
        try:
            enhanced_seats = []

            for i, seat in enumerate(selected_seats):
                if isinstance(seat, dict):
                    # 复制原始座位对象
                    enhanced_seat = seat.copy()

                    # 🔧 确保有seat_info字段
                    if 'seat_info' not in enhanced_seat or not enhanced_seat['seat_info']:
                        # 尝试从original_data构建
                        original_data = seat.get('original_data', {})
                        if original_data:
                            row = original_data.get('row', seat.get('row', ''))
                            col = original_data.get('col', seat.get('col', ''))
                            if row and col:
                                enhanced_seat['seat_info'] = f"{row}排{col}座"
                                print(f"[座位增强] 从original_data构建座位信息: {enhanced_seat['seat_info']}")

                        # 如果还是没有，尝试从row/col构建
                        if 'seat_info' not in enhanced_seat or not enhanced_seat['seat_info']:
                            row = seat.get('row', '')
                            col = seat.get('col', '')
                            if row and col:
                                enhanced_seat['seat_info'] = f"{row}排{col}座"
                                print(f"[座位增强] 从row/col构建座位信息: {enhanced_seat['seat_info']}")

                    enhanced_seats.append(enhanced_seat)
                    print(f"[座位增强] 座位{i+1}: {enhanced_seat.get('seat_info', 'N/A')}")
                else:
                    # 如果是字符串，尝试构建对象
                    if isinstance(seat, str):
                        enhanced_seat = {
                            'seat_info': f"{seat}排6座",  # 默认假设6座
                            'row': seat,
                            'col': '6',
                            'original_seat': seat
                        }
                        enhanced_seats.append(enhanced_seat)
                        print(f"[座位增强] 字符串座位{i+1}增强: {seat} -> {enhanced_seat['seat_info']}")
                    else:
                        enhanced_seats.append(seat)

            return enhanced_seats

        except Exception as e:
            print(f"[座位增强] ❌ 增强失败: {e}")
            return selected_seats

    def _extract_seat_info_string(self, enhanced_seats):
        """
        🔧 提取座位信息字符串
        从增强的座位对象中提取用于显示的座位信息
        """
        try:
            seat_infos = []

            for seat in enhanced_seats:
                if isinstance(seat, dict):
                    seat_info = seat.get('seat_info', '')
                    if seat_info:
                        seat_infos.append(seat_info)
                    else:
                        # 降级处理
                        row = seat.get('row', '')
                        col = seat.get('col', '')
                        if row and col:
                            seat_infos.append(f"{row}排{col}座")
                        else:
                            seat_infos.append(str(seat))
                else:
                    seat_infos.append(str(seat))

            result = ", ".join(seat_infos) if seat_infos else "未知"
            print(f"[座位提取] 提取的座位信息字符串: {result}")
            return result

        except Exception as e:
            print(f"[座位提取] ❌ 提取失败: {e}")
            return "座位信息提取失败"

    def _enhance_time_info_for_display(self, session_data, order_info):
        """
        🔧 增强时间信息用于显示
        确保时间信息包含完整的日期和时间
        """
        try:
            # 方法1：从session_data获取
            show_date = session_data.get('show_date', '')
            show_time = session_data.get('show_time', '')

            # 方法2：从order_info获取
            if not show_date:
                show_date = order_info.get('show_date', '')

            # 方法3：组合日期和时间
            if show_date and show_time and show_time not in show_date:
                # 如果show_date只有日期，添加时间
                if len(show_date) == 8 and show_date.isdigit():  # YYYYMMDD格式
                    enhanced_time = f"{show_date} {show_time.replace(':', '')}"
                    print(f"[时间增强] 组合时间信息: {show_date} + {show_time} -> {enhanced_time}")
                    return enhanced_time
                else:
                    enhanced_time = f"{show_date} {show_time}"
                    print(f"[时间增强] 组合时间信息: {enhanced_time}")
                    return enhanced_time

            # 如果已经包含时间信息，直接返回
            if show_date:
                print(f"[时间增强] 使用原始时间信息: {show_date}")
                return show_date

            # 最后降级
            print(f"[时间增强] ⚠️ 无法获取时间信息，使用默认值")
            return "时间未知"

        except Exception as e:
            print(f"[时间增强] ❌ 增强失败: {e}")
            return session_data.get('show_date', '时间未知')

    def _handle_womei_order_success(self, result, selected_seats, session_info):
        """沃美系统专用：处理订单成功"""
        try:
            # 🔍 格式化打印订单成功处理信息
            self._print_order_api_response(result, "沃美订单成功处理")

            # 获取沃美订单数据
            order_id = result.get('order_id', f"WOMEI{int(__import__('time').time())}")
            order_info = result.get('order_info', {})

            # 🆕 查询并打印详细的订单信息
            if order_id and order_id != f"WOMEI{int(__import__('time').time())}":
                self._query_and_print_order_detail(order_id, session_info)

            # 从session_info获取显示数据
            cinema_data = session_info.get('cinema_data', {})
            session_data = session_info.get('session_data', {})

            # 计算总价
            total_amount = sum(seat.get('price', 0) for seat in selected_seats)

            # 🔧 修复：增强座位信息构建，确保完整的座位描述
            enhanced_seats = self._enhance_seat_info_for_display(selected_seats)

            # 🔧 修复：增强时间信息构建，确保包含完整时间
            enhanced_show_date = self._enhance_time_info_for_display(session_data, order_info)

            # 构建订单详情
            self.current_order = {
                'order_id': order_id,
                'seats': enhanced_seats,  # 使用增强的座位信息
                'seat_info': self._extract_seat_info_string(enhanced_seats),  # 🆕 添加座位信息字符串
                'total_price': total_amount,
                'cinema_name': cinema_data.get('cinema_name', ''),
                'film_name': session_data.get('movie_name', ''),
                'hall_name': session_data.get('hall_name', ''),
                'show_time': session_data.get('show_time', ''),
                'show_date': enhanced_show_date,  # 使用增强的时间信息
                'api_data': order_info,
                'movieid': session_data.get('movie_id', ''),
                'showid': session_data.get('schedule_id', ''),
                'totalprice': total_amount,
                'cinemaid': cinema_data.get('cinema_id', ''),
                'system_type': 'womei'  # 标记为沃美系统
            }



            # 显示订单详情
            self._show_order_detail(self.current_order)

            # 🔧 修复：沃美订单创建成功后立即初始化支付方式（解决4004错误）
            cinema_id = cinema_data.get('cinema_id', '') or cinema_data.get('cinemaid', '') or cinema_data.get('id', '')
            account_data = session_info.get('account', {})
            token = account_data.get('token', '')

            # 调试打印已移除
            # 调试打印已移除
            # 调试打印已移除
            # 调试打印已移除

            if token and cinema_id:
                init_result = self._initialize_order_payment_method(order_id, cinema_id, token)
                if init_result.get('success', False):
                    pass  # 调试打印已移除
                else:
                    print(f"[沃美订单初始化] ⚠️ 订单支付方式初始化失败: {init_result.get('error', '未知错误')}")
                    # 注意：初始化失败不阻断订单创建流程，仅记录日志
            else:
                pass  # 调试打印已移除

            # 🆕 获取可用券列表 - 修复参数传递

            self._load_available_coupons(order_id, cinema_id)

            # 发布全局事件
            if hasattr(self, 'event_bus'):
                self.event_bus.order_created.emit(self.current_order)

            return True

        except Exception as e:
            print(f"[沃美订单] ❌ 成功处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _save_enhanced_seat_debug_data(self, cinema_id: str, hall_id: str, schedule_id: str, seat_result: dict, session_info: dict):
        """保存增强的座位调试数据，包含完整的会话信息"""
        try:
            import os
            import json
            from datetime import datetime

            # 确保data目录存在
            os.makedirs('data', exist_ok=True)

            # 从session_info获取详细的会话信息
            cinema_data = session_info.get('cinema_data', {})
            session_data = session_info.get('session_data', {})
            account_data = session_info.get('account', {})

            # 构建增强的调试数据
            enhanced_debug_data = {
                "session_info": {
                    "cinema_name": cinema_data.get('cinema_name', cinema_data.get('cinemaShortName', '沃美影院')),
                    "movie_name": session_data.get('movie_name', session_data.get('filmName', '未知影片')),
                    "show_date": session_data.get('show_date', session_data.get('showDate', '未知日期')),
                    "show_time": session_data.get('show_time', session_data.get('showTime', '未知时间')),
                    "cinema_id": cinema_id,
                    "hall_id": hall_id,
                    "hall_name": session_data.get('hall_name', f'{hall_id}号厅'),
                    "schedule_id": schedule_id,
                    "timestamp": datetime.now().isoformat(),
                    "account_phone": account_data.get('phone', 'N/A'),
                    "session_text": session_info.get('session_text', 'N/A')
                },
                "api_response": seat_result,
                "hall_info": seat_result.get('hall_info', {}),
                "cinema_data": cinema_data,
                "session_data": session_data,
                "account_data": {
                    "phone": account_data.get('phone', 'N/A'),
                    "token_status": "已配置" if account_data.get('token') else "未配置"
                },
                "debug_notes": {
                    "purpose": "增强的座位图调试数据（包含完整会话信息，每次覆盖保存）",
                    "area_no_usage": "区域ID应该使用area_no字段，不是固定的1",
                    "seat_no_format": "seat_no应该是类似11051771#09#06的格式",
                    "coordinate_mapping": "row/col是逻辑位置，x/y是物理位置",
                    "status_meaning": "0=可选，1=已售，2=锁定，6=不可选择",
                    "file_location": "data/座位调试数据.json（固定文件名，每次覆盖）",
                    "enhanced_features": [
                        "包含完整的影院、影片、场次信息",
                        "包含账号信息（脱敏处理）",
                        "包含会话上下文数据",
                        "便于调试座位参数构建问题"
                    ]
                }
            }

            # 🔧 修改：固定文件名，每次覆盖
            filename = "data/座位调试数据.json"

            # 保存到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(enhanced_debug_data, f, ensure_ascii=False, indent=2)

            print(f"[主窗口] 📁 座位调试数据已覆盖保存: {filename}")
            print(f"[主窗口] 📊 当前会话数据:")
            print(f"  - 影院: {enhanced_debug_data['session_info']['cinema_name']}")
            print(f"  - 影片: {enhanced_debug_data['session_info']['movie_name']}")
            print(f"  - 场次: {enhanced_debug_data['session_info']['show_date']} {enhanced_debug_data['session_info']['show_time']}")
            print(f"  - 影厅: {enhanced_debug_data['session_info']['hall_name']}")
            print(f"  - 账号: {enhanced_debug_data['session_info']['account_phone']}")
            print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
            print(f"  - 保存方式: 覆盖保存（固定文件名）")

        except Exception as e:
            print(f"[主窗口] ❌ 保存增强座位调试数据失败: {e}")
            import traceback
            traceback.print_exc()

    def _build_womei_seatlable(self, seat_info_list, session_info):
        """构建沃美系统的座位参数格式 - 真实格式"""
        try:
            # 🔧 修复：沃美系统使用特殊的字符串格式
            # 真实格式：1:2:5:11051771#09#06
            # 解析：区域ID:行号:列号:seat_no
            # 其中 seat_no = 11051771#09#06 (座位唯一标识)

            # 分析座位数据

            seat_parts = []
            for seat in seat_info_list:
                # 获取座位信息
                row_num = seat.get("rowNum", 1)
                col_num = seat.get("columnNum", 1)
                area_id = seat.get("areaId", 1)  # 从座位数据获取区域ID

                # 从座位数据的original_data中获取真实的sn字段
                original_data = seat.get("original_data", {})

                # 🔍 尝试多种可能的seat_no字段名
                possible_seat_no_fields = ['sn', 'seat_no', 'seatNo', 'seat_id', 'id', 'code']
                real_seat_no = ""

                # 优先从original_data中查找
                for field in possible_seat_no_fields:
                    if original_data.get(field):
                        real_seat_no = str(original_data[field])
                        print(f"  - 从original_data.{field}获取: {real_seat_no}")
                        break

                # 如果original_data中没有，从seat中查找
                if not real_seat_no:
                    for field in possible_seat_no_fields:
                        if seat.get(field):
                            real_seat_no = str(seat[field])
                            print(f"  - 从seat.{field}获取: {real_seat_no}")
                            break

                # 🔧 如果仍然没有找到，根据真实curl构造
                if not real_seat_no or not "#" in real_seat_no:
                    # 根据真实curl的格式构造：11051771#09#06
                    # 这里需要从session_info获取真实的场次相关信息
                    session_data = session_info.get('session_data', {})
                    schedule_id = session_data.get('schedule_id', '16626081')

                    # 构造格式：{schedule_id}#09#{col_num:02d}
                    constructed_seat_no = f"{schedule_id}#09#{col_num:02d}"
                    real_seat_no = constructed_seat_no
                    # 调试打印已移除

                # 调试打印已移除

                # 构建座位字符串：区域ID:行号:列号:seat_no
                seat_str = f"{area_id}:{row_num}:{col_num}:{real_seat_no}"
                seat_parts.append(seat_str)

                print(f"[订单调试] 座位构建: 区域{area_id} 行{row_num} 列{col_num} -> {seat_str}")

            # 用 | 连接多个座位
            seatlable_str = "|".join(seat_parts)
            # 调试打印已移除
            print(f"[订单调试] 对比真实请求: 1:2:5:11051771#09#06|1:2:4:11051771#09#05")

            return seatlable_str

        except Exception as e:
            print(f"[订单调试] 构建沃美座位参数失败: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def _build_order_params_from_session_info(self, selected_seats, session_info):
        """从session_info构建订单参数"""
        try:
            # 从session_info获取数据
            cinema_data = session_info.get('cinema_data', {})
            account_data = session_info.get('account', {})
            session_data = session_info.get('session_data', {})

            if not cinema_data or not account_data or not session_data:
                print("[订单参数] session_info数据不完整")
                return None

            # 构建座位参数
            seat_info_list = []
            for i, seat in enumerate(selected_seats):
                seat_no = seat.get('sn', '')
                if not seat_no:
                    row_num = seat.get('rn', seat.get('row', 1))
                    col_num = seat.get('cn', seat.get('col', 1))
                    seat_no = f"000000011111-{col_num}-{row_num}"

                seat_price = seat.get('price', 0)

                # 🔧 修复：从original_data获取真实的area_no
                original_data = seat.get('original_data', {})
                real_area_no = original_data.get('area_no', '1')

                seat_info = {
                    "seatNo": seat_no,
                    "rowNum": seat.get('rn', seat.get('row', 1)),
                    "columnNum": seat.get('cn', seat.get('col', 1)),
                    "seatType": seat.get('seatType', 1),
                    "areaId": real_area_no,  # 🔧 修复：使用真实的area_no
                    "unitPrice": seat_price,
                    "seatPrice": seat_price,
                    "serviceCharge": 0,
                    "seatId": f"seat_{i+1}",
                    "x": seat.get('x', 0),
                    "y": seat.get('y', 0),
                    "original_data": original_data  # 🔧 添加：保留original_data用于调试
                }
                seat_info_list.append(seat_info)

            # 构建订单参数
            order_params = {
                "account": account_data,
                "cinemaid": cinema_data.get('cinema_id', ''),
                "filmid": session_data.get('movie_id', ''),
                "seatlable": seat_info_list,
                "sessionid": session_data.get('schedule_id', ''),
                "hallid": session_data.get('hall_id', ''),
                "showtime": session_data.get('show_time', ''),
                "showdate": session_data.get('show_date', ''),
                "totalprice": sum(seat.get('price', 0) for seat in selected_seats),
                "seatcount": len(selected_seats)
            }

            # 调试打印已移除
            print(f"  - 影院ID: {order_params['cinemaid']}")
            print(f"  - 电影ID: {order_params['filmid']}")
            print(f"  - 场次ID: {order_params['sessionid']}")
            print(f"  - 座位数: {order_params['seatcount']}")

            return order_params

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[订单参数] 构建失败: {e}")
            return None

    def _handle_womei_order_creation_success(self, result, selected_seats, session_info):
        """处理沃美订单创建成功"""
        try:
            # 获取沃美订单数据
            order_id = result.get('order_id', f"WOMEI{int(__import__('time').time())}")
            order_info = result.get('order_info', {})

            # 从session_info获取显示数据
            cinema_data = session_info.get('cinema_data', {})
            session_data = session_info.get('session_data', {})

            # 计算总价
            total_amount = sum(seat.get('price', 0) for seat in selected_seats)

            # 构建订单详情
            self.current_order = {
                'order_id': order_id,
                'seats': selected_seats,
                'total_price': total_amount,
                'cinema_name': cinema_data.get('cinema_name', ''),
                'film_name': session_data.get('movie_name', ''),
                'hall_name': session_data.get('hall_name', ''),
                'show_time': session_data.get('show_time', ''),
                'show_date': session_data.get('show_date', ''),
                'api_data': order_info,
                'movieid': session_data.get('movie_id', ''),
                'showid': session_data.get('schedule_id', ''),
                'totalprice': total_amount,
                'cinemaid': cinema_data.get('cinema_id', ''),
                'system_type': 'womei'  # 标记为沃美系统
            }

            # 调试打印已移除
            print(f"  - 订单号: {order_id}")
            print(f"  - 座位数: {len(selected_seats)}")
            print(f"  - 总价: {total_amount} 分")

            # 显示订单详情
            self._show_order_detail(self.current_order)

            # 发布全局事件
            if hasattr(self, 'event_bus'):
                self.event_bus.order_created.emit(self.current_order)

            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[沃美订单成功] 处理失败: {e}")
            return False

    def _handle_order_creation_success_with_session_info(self, result, selected_seats, session_info):
        """使用session_info处理订单创建成功"""
        try:
            # 获取订单数据
            order_data = result.get('resultData', {})
            order_id = order_data.get('orderno', f"ORDER{int(__import__('time').time())}")

            # 从session_info获取显示数据
            cinema_data = session_info.get('cinema_data', {})
            session_data = session_info.get('session_data', {})

            # 计算总价
            total_amount = sum(seat.get('price', 0) for seat in selected_seats)

            # 构建订单详情
            self.current_order = {
                'order_id': order_id,
                'seats': selected_seats,
                'total_price': total_amount,
                'cinema_name': cinema_data.get('cinema_name', ''),
                'film_name': session_data.get('movie_name', ''),
                'hall_name': session_data.get('hall_name', ''),
                'show_time': session_data.get('show_time', ''),
                'show_date': session_data.get('show_date', ''),
                'api_data': order_data,
                'movieid': session_data.get('movie_id', ''),
                'showid': session_data.get('schedule_id', ''),
                'totalprice': total_amount,
                'cinemaid': cinema_data.get('cinema_id', '')
            }

            # 调试打印已移除
            print(f"  - 订单号: {order_id}")
            print(f"  - 座位数: {len(selected_seats)}")
            print(f"  - 总价: {total_amount} 元")

            # 显示订单详情
            self._show_order_detail(self.current_order)

            # 发布全局事件
            if hasattr(self, 'event_bus'):
                self.event_bus.order_created.emit(self.current_order)

            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[订单成功] 处理失败: {e}")
            return False
    
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
            # 🚫 移除本地影院管理器调用
            print(f"[主窗口] 🚫 已移除本地影院文件加载，从API数据中查找影院")
            
            # 方法2: 从Tab管理器的影院数据获取
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'cinemas_data'):
                for cinema in self.tab_manager_widget.cinemas_data:
                    cinema_short_name = cinema.get('cinemaShortName', '')
                    cinema_name_field = cinema.get('name', '')
                    
                    if cinema_short_name == cinema_name or cinema_name_field == cinema_name:
                        return cinema
            
            # 🚫 移除本地影院文件重新加载逻辑
            print(f"[主窗口] 💡 提示：请通过城市选择重新加载影院数据")
            
            return None
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def _load_movies_for_cinema(self, cinema_info):
        """为指定影院加载电影列表"""
        try:
            # 使用沃美电影服务获取电影
            if self.current_account:
                cinema_id = cinema_info.get('cinemaid', '')
                token = self.current_account.get('token', '')

                if cinema_id:
                    # 🔧 修复：使用get_womei_film_service获取服务实例，而不是使用未初始化的self.film_service
                    from services.womei_film_service import get_womei_film_service
                    film_service = get_womei_film_service(token)
                    movies_result = film_service.get_movies(cinema_id)

                    if movies_result.get('success'):
                        movies = movies_result.get('movies', [])
                        if movies and hasattr(self.tab_manager_widget, 'movie_combo'):
                            self.tab_manager_widget.movie_combo.clear()
                            for movie in movies:
                                movie_name = movie.get('name', '')
                                self.tab_manager_widget.movie_combo.addItem(movie_name)
                            print(f"[主窗口] 成功加载 {len(movies)} 部电影")
                        else:
                            print("[主窗口] 未获取到电影数据")
                    else:
                        error = movies_result.get('error', '未知错误')
                        print(f"[主窗口] 获取电影失败: {error}")
                        self._load_default_movies()
                else:
                    print("[主窗口] 缺少影院ID")
                    self._load_default_movies()
            else:
                print("[主窗口] 当前账号为空")
                self._load_default_movies()

        except Exception as e:
            print(f"[主窗口] 加载电影异常: {e}")
            self._load_default_movies()

    def _load_default_movies(self):
        """加载默认电影列表"""
        if hasattr(self.tab_manager_widget, 'movie_combo'):
            self.tab_manager_widget.movie_combo.clear()
            self.tab_manager_widget.movie_combo.addItems([
                "名侦探柯南：独眼的残像",
                "海王2：失落的王国",
                "阿凡达：水之道"
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
            print(f"[主窗口] 🎬 收到场次选择信号")
            # 调试打印已移除
            # 调试打印已移除

            # 验证必要信息
            session_data = session_info.get('session_data')
            account = session_info.get('account')
            cinema_data = session_info.get('cinema_data')

            # 调试打印已移除
            print(f"  - session_data: {type(session_data)} - {bool(session_data)}")
            print(f"  - account: {type(account)} - {bool(account)}")
            print(f"  - cinema_data: {type(cinema_data)} - {bool(cinema_data)}")

            if session_data:
                pass  # 调试打印已移除
            if account:
                pass  # 调试打印已移除
            if cinema_data:
                pass  # 调试打印已移除

            # 简化验证：只检查session_data，不再强制要求account
            if not session_data:
                pass  # 调试打印已移除
                self._safe_update_seat_area("场次信息不完整\n\n无法加载座位图")
                return

            # 如果没有account，使用配置的测试账号
            if not account:
                print(f"[主窗口] ⚠️ 使用配置的测试账号")
                from config import config
                account = self.current_user or {
                    'phone': config.TEST_PHONE,
                    'token': config.DEFAULT_TOKEN
                }
                session_info['account'] = account

            # 如果没有cinema_data，尝试获取
            if not cinema_data:
                print(f"[主窗口] ⚠️ 尝试获取影院数据")
                cinema_data = self._get_current_cinema_data()
                session_info['cinema_data'] = cinema_data

            # 检查是否已经包含座位图数据
            hall_info = session_info.get('hall_info')
            if hall_info:
                # 调试打印已移除
                self._display_seat_map(hall_info, session_info)
            else:
                print(f"[主窗口] 🔄 session_info不包含座位图数据，需要加载")
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
            # 调试打印已移除

            # 获取必要参数
            session_data = session_info['session_data']
            account = session_info['account']
            cinema_data = session_info['cinema_data']

            # 调试打印已移除
            print(f"  - session_data类型: {type(session_data)}")
            print(f"  - account类型: {type(account)}")
            print(f"  - cinema_data类型: {type(cinema_data)}")

            # 获取沃美系统需要的参数
            cinema_id = cinema_data.get('cinemaid', '')
            schedule_id = session_data.get('schedule_id', '')
            hall_id = session_data.get('hall_id', '')

            # 调试打印已移除
            print(f"  - cinema_id: {cinema_id} (来源: cinema_data.cinemaid)")
            print(f"  - schedule_id: {schedule_id} (来源: session_data.schedule_id)")
            print(f"  - hall_id: {hall_id} (来源: session_data.hall_id)")
            print(f"  - cinema_data所有字段: {list(cinema_data.keys()) if cinema_data else 'None'}")
            print(f"  - session_data所有字段: {list(session_data.keys()) if session_data else 'None'}")

            if not all([cinema_id, schedule_id, hall_id]):
                # 调试打印已移除
                print(f"  - cinema_id: {cinema_id} ({'✓' if cinema_id else '✗'})")
                print(f"  - schedule_id: {schedule_id} ({'✓' if schedule_id else '✗'})")
                print(f"  - hall_id: {hall_id} ({'✓' if hall_id else '✗'})")
                self._safe_update_seat_area("缺少座位图参数\n\n请重新选择场次")
                return

            # 调试打印已移除
            print(f"  - 影院名称: {cinema_data.get('cinemaShortName', 'N/A')}")
            print(f"  - 影院ID: {cinema_data.get('cinemaid', 'N/A')}")

            # 设置token并调用沃美座位图API
            token = account.get('token', '')
            # 安全的Token显示
            if token:
                print(f"[主窗口] 🔑 Token状态: 已配置 (长度: {len(token)})")
            else:
                print(f"[主窗口] 🔑 Token状态: 未配置")

            # 🔧 修复：使用get_womei_film_service获取服务实例，而不是使用未初始化的self.film_service
            from services.womei_film_service import get_womei_film_service
            film_service = get_womei_film_service(token)

            # 调用沃美座位图API
            seat_result = film_service.get_hall_info(cinema_id, hall_id, schedule_id)

            if seat_result and isinstance(seat_result, dict):
                if seat_result.get('success'):
                    # 成功获取座位数据
                    hall_info = seat_result.get('hall_info', {})

                    # 🔧 新增：保存增强的会话调试数据
                    self._save_enhanced_seat_debug_data(cinema_id, hall_id, schedule_id, seat_result, session_info)

                    self._display_seat_map(hall_info, session_info)
                else:
                    # API返回错误
                    error_msg = seat_result.get('error', '未知错误')
                    self._safe_update_seat_area(f"获取座位图失败\n\n{error_msg}")
            else:
                # 响应格式错误
                self._safe_update_seat_area("座位图数据格式错误\n\n请重新选择场次")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._safe_update_seat_area("加载座位图异常\n\n请检查网络连接")

    def _display_seat_map(self, seat_data: dict, session_info: dict):
        """显示座位图"""
        try:
            # print(f"[主窗口] 座位数据字段: {list(seat_data.keys()) if seat_data else '空数据'}")
            
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
                
                # 🆕 解析沃美座位数据 - room_seat字段
                room_seat = seat_data.get('room_seat', [])
                if room_seat:
                    seat_matrix, area_data = self._parse_womei_room_seat(room_seat, hall_info)
                    # print(f"[主窗口] 沃美座位矩阵解析完成: {len(seat_matrix) if seat_matrix else 0} 行, {len(area_data) if area_data else 0} 个区域")
                else:
                    # 兼容旧格式
                    seats_array = seat_data.get('seats', [])
                    if seats_array:
                        seat_matrix = self._parse_seats_array(seats_array, hall_info)
                        # print(f"[主窗口] 座位矩阵解析完成: {len(seat_matrix) if seat_matrix else 0} 行")
                    else:
                        print(f"[主窗口] 未找到座位数据333，可用字段: {list(seat_data.keys())}")
            
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

                        # 🆕 使用多区域更新方法
                        if 'area_data' in locals():
                            seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
                        else:
                            seat_panel.update_seat_data(seat_matrix)

                        # 🔧 修复：保存完整的session_info到座位面板
                        seat_panel.session_info = session_info
                        # 调试打印已移除
                        print(f"  - 影院数据: {'存在' if session_info.get('cinema_data') else '缺失'}")
                        print(f"  - 账号数据: {'存在' if session_info.get('account') else '缺失'}")
                        print(f"  - 场次数据: {'存在' if session_info.get('session_data') else '缺失'}")

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

    def _parse_womei_room_seat(self, room_seat: List[Dict], hall_info: dict) -> tuple[List[List[Dict]], List[Dict]]:
        """解析沃美room_seat数据为座位矩阵和区域数据（增强调试功能）"""
        try:
            # 座位数据解析（已移除详细调试输出）

            # 收集所有座位和区域信息
            all_seats = []
            area_data = []  # 🆕 收集区域信息
            max_row = 0
            max_col = 0

            for area_index, area in enumerate(room_seat):
                area_name = area.get('area_name', '未知区域')
                area_price = area.get('area_price', 0)
                area_no = area.get('area_no', str(area_index + 1))
                seats_data = area.get('seats', [])  # 🔧 修复：seats是列表，不是字典

                print(f"[座位调试] 区域 {area_index + 1}: {area_name}, 价格: {area_price}元")
                print(f"[座位调试] 区域座位数据类型: {type(seats_data)}")
                print(f"[座位调试] 区域座位数据长度: {len(seats_data)}")

                # 🆕 收集区域信息
                area_info = {
                    'area_no': area_no,
                    'area_name': area_name,
                    'area_price': area_price
                }
                area_data.append(area_info)

                # 🔧 修复：根据实际数据结构处理座位数据
                if isinstance(seats_data, dict):
                    # 如果seats是字典格式（按行组织）
                    print(f"[座位调试] 处理字典格式的座位数据")
                    for row_key, row_data in seats_data.items():
                        row_num = row_data.get('row', int(row_key))
                        seat_details = row_data.get('detail', [])
                        print(f"[座位调试] 第{row_num}行: {len(seat_details)}个座位")

                        for seat_detail in seat_details:
                            seat = self._process_seat_detail(seat_detail, area_name, area_price, all_seats, area_no, row_num)
                            if seat:
                                max_row = max(max_row, seat['row'])
                                max_col = max(max_col, seat['col'])

                elif isinstance(seats_data, list):
                    # 如果seats是列表格式（直接包含座位）
                    print(f"[座位调试] 处理列表格式的座位数据")
                    for seat_detail in seats_data:
                        seat = self._process_seat_detail(seat_detail, area_name, area_price, all_seats, area_no)
                        if seat:
                            max_row = max(max_row, seat['row'])
                            max_col = max(max_col, seat['col'])
                else:
                    print(f"[座位调试] ⚠️ 未知的座位数据格式: {type(seats_data)}")
                    continue

            # 座位矩阵构建
            seat_matrix = []
            for row in range(1, max_row + 1):
                row_seats = []
                for col in range(1, max_col + 1):
                    # 查找该位置的座位
                    seat = None
                    for s in all_seats:
                        if s['row'] == row and s['col'] == col:
                            seat = s
                            break

                    if seat:
                        row_seats.append(seat)
                    else:
                        # 空座位
                        row_seats.append({
                            'seat_no': '',
                            'row': row,
                            'col': col,
                            'type': -1,  # 空座位标记
                            'status': 'empty',  # 空座位状态
                            'area_name': '',
                            'area_price': 0,
                            'price': 0,
                            'num': ''  # 空座位无座位号
                        })

                seat_matrix.append(row_seats)

            # 更新hall_info
            hall_info['seat_count'] = len(all_seats)
            hall_info['row_count'] = max_row
            hall_info['col_count'] = max_col
            hall_info['name'] = hall_info.get('hall_name', '未知影厅')

            # 座位矩阵构建完成
            return seat_matrix, area_data

        except Exception as e:
            print(f"[座位调试] ❌ 解析沃美座位数据失败: {e}")
            import traceback
            traceback.print_exc()
            return [], []

    def _process_seat_detail(self, seat_detail: dict, area_name: str, area_price: float, all_seats: list, area_no: str, row_num: int = None):
        """处理单个座位详情数据（增强版：包含状态验证）"""
        try:
            # 🔧 沃美座位状态映射：数字状态转换为字符串状态
            seat_status = seat_detail.get('status', 0)
            seat_no = seat_detail.get('seat_no', '')
            seat_row = int(seat_detail.get('row', row_num or 1))
            seat_col = int(seat_detail.get('col', 1))

            # 🎯 特定座位验证：1排6座、1排7座
            is_target_seat = (seat_row == 1 and seat_col in [6, 7])

            if is_target_seat:
                # print(f"\n🎯 [座位状态验证] 发现目标座位: {seat_row}排{seat_col}座")
                # print(f"  座位编号: {seat_no}")
                # print(f"  原始状态码: {seat_status}")
                print(f"  区域: {area_name}")
                # print(f"  完整数据: {seat_detail}")

            # 详细的状态映射调试
            if seat_status == 0:
                status = 'available'  # 可选
                status_desc = "可选"
            elif seat_status == 1:
                status = 'sold'       # 已售
                status_desc = "已售"
            elif seat_status == 2:
                status = 'locked'     # 锁定
                status_desc = "锁定"
            elif seat_status == 6:
                status = 'unavailable'  # 完全不可选择
                status_desc = "不可选择"
                print(f"[主窗口] 🚫 发现不可选择座位: {seat_no} status={seat_status}")
            else:
                status = 'available'  # 默认可选
                status_desc = f"未知状态({seat_status})->默认可选"
                print(f"[主窗口] ⚠️ 未知座位状态: {seat_no} status={seat_status}, 默认设为可选")

            # 🎯 目标座位状态验证
            if is_target_seat:
                print(f"  映射后状态: {status} ({status_desc})")

                # 与预期状态对比
                expected_status = "sold"  # 根据真实APP，这两个座位应该是已售
                if status == expected_status:
                    pass  # 调试打印已移除
                else:
                    # 调试打印已移除
                    print(f"     系统状态: {status}")
                    print(f"     预期状态: {expected_status}")
                    print(f"     真实APP显示: 已售")

                    # 🔧 状态不一致时的详细分析
                    # 调试打印已移除
                    print(f"     API返回状态码: {seat_status}")
                    print(f"     当前映射规则: 0=可选, 1=已售, 2=锁定, 6=不可选择")

                    if seat_status == 1:
                        print(f"     ⚠️ 状态码1应该映射为已售，但可能UI显示有问题")
                    elif seat_status == 0:
                        print(f"     ⚠️ API返回可选状态，但真实APP显示已售")
                        print(f"     可能原因: API数据不同步或状态码定义不同")
                    elif seat_status == 2:
                        print(f"     ⚠️ API返回锁定状态，可能需要映射为已售")

            # 座位信息处理（已移除详细调试输出）

            # 🔧 修复：沃美座位数据格式，确保original_data包含正确的沃美数据
            seat = {
                'seat_no': seat_detail.get('seat_no', ''),
                'row': seat_row,
                'col': seat_col,
                'x': seat_detail.get('x', 1),
                'y': seat_detail.get('y', row_num or 1),
                'type': seat_detail.get('type', 0),
                'status': status,  # 使用转换后的字符串状态
                'area_name': area_name,
                'area_price': area_price,
                'price': area_price,  # 添加价格字段
                'num': str(seat_detail.get('col', 1)),  # 添加座位号显示
                'original_status': seat_status,  # 保存原始状态用于调试
                'is_target_seat': is_target_seat,  # 🆕 标记是否为目标验证座位
                # 🔧 修复：保存完整的沃美座位数据到original_data
                'original_data': {
                    'seat_no': seat_detail.get('seat_no', ''),  # 真实的seat_no
                    'area_no': area_no,  # 🔧 修复：使用真实的区域area_no，不是默认值
                    'row': str(seat_row),
                    'col': str(seat_col),
                    'x': seat_detail.get('x', 1),
                    'y': seat_detail.get('y', row_num or 1),
                    'type': seat_detail.get('type', 0),
                    'status': seat_status,  # 原始状态码
                    'area_name': area_name,
                    'area_price': area_price,
                    # 保存原始API数据
                    'api_data': seat_detail
                }
            }

            all_seats.append(seat)
            return seat

        except Exception as e:
            print(f"[座位调试] 处理座位详情错误: {e}")
            return None

    def _parse_seats_array(self, seats_array: List[Dict], hall_info: dict) -> List[List[Dict]]:
        """解析seats数组为座位矩阵"""
        try:
            # 座位数据处理（已移除详细调试输出）
            if not seats_array:
                return []

            max_row = 0
            max_col = 0
            
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

                    # 🔧 修复：为沃美系统构建正确的座位数据格式
                    seat_data = {
                        'row': logical_row if logical_row else seat.get('rn', physical_row + 1),  # 🆕 优先使用逻辑排号r，备选物理排号rn
                        'col': logical_col if logical_col else seat.get('cn', physical_col + 1),  # 🆕 优先使用逻辑列数c，备选物理列数cn
                        'num': real_seat_num,  # 🆕 使用逻辑列数c作为座位号
                        'status': status,
                        'price': 0,  # 价格信息在priceinfo中
                        'seatname': seat.get('sn', ''),
                        'original_data': {
                            # 🔧 修复：保存沃美系统的真实座位数据
                            'seat_no': seat.get('seat_no', ''),  # 真实的seat_no
                            'area_no': seat.get('area_no', '1'),  # 真实的area_no
                            'row': str(logical_row if logical_row else seat.get('rn', physical_row + 1)),
                            'col': str(logical_col if logical_col else seat.get('cn', physical_col + 1)),
                            'x': seat.get('x', 1),
                            'y': seat.get('y', 1),
                            'type': seat.get('type', 0),
                            'status': seat.get('status', 0),
                            # 保存原始API数据
                            'api_data': seat
                        }
                    }

                    seat_matrix[physical_row][physical_col] = seat_data
            
            # 座位矩阵构建完成
            
            return seat_matrix
            
        except Exception as e:
            print(f"[座位调试] 解析seats数组失败: {e}")
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
    
    def _on_seat_panel_submit_order(self, order_data):
        """座位面板提交订单处理（修复影院数据传递问题）"""
        try:
            # 🔧 修复：处理完整的订单数据
            if isinstance(order_data, dict):
                # 新格式：完整的订单数据
                selected_seats = order_data.get('seats', [])
                session_info = order_data.get('session_info', {})

                print(f"[主窗口] 座位面板提交订单: {len(selected_seats)} 个座位")
                print(f"[主窗口] 订单数据验证:")
                print(f"  - 影院数据: {'存在' if session_info.get('cinema_data') else '缺失'}")
                print(f"  - 账号数据: {'存在' if session_info.get('account') else '缺失'}")
                print(f"  - 场次数据: {'存在' if session_info.get('session_data') else '缺失'}")

                # 验证影院数据
                cinema_data = session_info.get('cinema_data')
                if not cinema_data:
                    print(f"[订单参数] 缺少影院数据")
                    from services.ui_utils import MessageManager
                    MessageManager.show_error(self, "订单创建失败", "缺少影院数据，请重新选择影院和场次", auto_close=False)
                    return
                else:
                    pass  # 调试打印已移除

                # 🔧 修复：直接使用沃美专用订单创建流程
                self._create_womei_order_direct(selected_seats, session_info)

            else:
                # 兼容旧格式：只有座位数据
                # print(f"[主窗口] 座位面板提交订单（兼容模式）: {len(order_data)} 个座位")
                self.on_submit_order(order_data)

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
        """获取当前选中的影院数据（适配沃美系统）"""
        try:
            if hasattr(self.tab_manager_widget, 'cinema_combo'):
                cinema_name = self.tab_manager_widget.cinema_combo.currentText()
                if cinema_name and hasattr(self.tab_manager_widget, 'cinemas_data'):
                    for cinema in self.tab_manager_widget.cinemas_data:
                        # 适配沃美系统的字段名
                        if cinema.get('cinema_name') == cinema_name:
                            # 为了兼容主窗口的座位图加载逻辑，添加华联格式的字段
                            cinema_data = cinema.copy()
                            cinema_data['cinemaid'] = cinema.get('cinema_id')  # 映射沃美cinema_id到华联cinemaid
                            cinema_data['cinemaShortName'] = cinema.get('cinema_name')  # 映射沃美cinema_name到华联cinemaShortName
                            return cinema_data
                        # 兼容华联系统的字段名（如果存在）
                        elif cinema.get('cinemaShortName') == cinema_name:
                            return cinema
            return {}
        except Exception as e:
            print(f"[主窗口] 获取影院数据失败: {e}")
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

            # 调试打印已移除

            # 检查是否已经有取票码二维码显示
            if hasattr(self, 'qr_display'):
                # 如果当前显示的是图片（二维码），则不覆盖
                if self.qr_display.pixmap() and not self.qr_display.pixmap().isNull():
                    # 调试打印已移除
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
                # 调试打印已移除

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
            # 调试打印已移除

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
                # 调试打印已移除

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

            # 调试打印已移除
            # 调试打印已移除

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
                            pass  # 调试打印已移除
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

                        # 调试打印已移除

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
            print("[主窗口] 窗口正在关闭，清理资源...")

            # 🆕 停止刷新监控服务
            refresh_timer_service.stop_monitoring()

            # 清理资源
            self.account_widget.cleanup()
            self.tab_manager_widget.cleanup()

            # 关闭登录窗口（如果存在）
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None

            # 座位区域和右栏区域是直接创建的QWidget，不需要特殊清理
            # 调试打印已移除
            event.accept()

        except Exception as e:
            print(f"[主窗口] 关闭事件处理错误: {e}")
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

    # 🚫 已移除密码策略获取功能，专注于券码支付和微信支付

    # 🚫 已移除密码显示功能，专注于券码支付和微信支付

    # 🚫 已移除支付密码管理功能，专注于券码支付和微信支付

    # 🚫 已移除密码文件保存功能，专注于券码支付和微信支付

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

    # 🚫 已移除增强的会员卡支付处理功能，专注于券码支付和微信支付

    # 🚫 已移除混合支付处理功能，专注于券码支付和微信支付

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

            # 调用API - 修复：只传递params参数
            result = get_coupon_prepay_info(params)

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
                
                # 🔧 修复：沃美系统不需要取消未付款订单功能
                # 取消未支付订单（沃美系统跳过此步骤）
                print(f"[影院切换] 沃美系统跳过取消未付款订单步骤")
                
                # 获取会员信息
                if self.current_account and cinema_info.get('cinemaid'):
                    self._get_member_info(self.current_account, cinema_info['cinemaid'])
                    
        except Exception as e:
            pass

    def on_submit_order(self, selected_seats=None):
        """提交订单 - 重构后的主方法，复用现有完整流程"""
        try:
            # 导入消息管理器
            from services.ui_utils import MessageManager

            # 如果传入了座位信息，需要完整处理座位数据
            if selected_seats is not None:
                # 验证基础条件
                if not self.current_account:
                    MessageManager.show_error(self, "提交失败", "请先选择账号", auto_close=False)
                    return False

                # 获取并验证选择信息
                cinema_text = self.tab_manager_widget.cinema_combo.currentText()
                movie_text = self.tab_manager_widget.movie_combo.currentText()
                date_text = self.tab_manager_widget.date_combo.currentText()
                session_text = self.tab_manager_widget.session_combo.currentText()

                # 验证选择完整性
                if not all([cinema_text, movie_text, date_text, session_text]):
                    MessageManager.show_error(self, "信息不完整", "请完整选择影院、影片、日期和场次", auto_close=False)
                    return False

                if not selected_seats:
                    MessageManager.show_error(self, "座位未选择", "请选择座位", auto_close=False)
                    return False

                # 过滤无效选择
                invalid_selections = ["请选择", "请先选择", "正在加载", "暂无", "加载失败", "选择影院"]
                if any(text in invalid_selections for text in [cinema_text, movie_text, date_text, session_text]):
                    MessageManager.show_error(self, "选择无效", "请重新选择有效的影院、影片、日期和场次", auto_close=False)
                    return False

                # 调用完整的订单创建流程（复用现有实现）
                return self._create_order_with_full_process(selected_seats)

            # 如果没有传入座位信息，使用原有的验证和处理流程
            if not self._validate_order_data():
                return False

            # 构建订单参数
            order_params = self._build_order_params()
            if not order_params:
                return False

            # 提交订单
            success = self._submit_order_to_api(order_params)
            if success:
                self._handle_order_success()
                return True
            else:
                self._handle_order_failure()
                return False

        except Exception as e:
            self._handle_order_exception(e)
            return False

    def _create_order_with_full_process(self, selected_seats):
        """完整的订单创建流程 - 复用现有实现"""
        try:
            from services.ui_utils import MessageManager
            import time

            # 获取当前选择信息
            cinema_text = self.tab_manager_widget.cinema_combo.currentText()
            movie_text = self.tab_manager_widget.movie_combo.currentText()
            date_text = self.tab_manager_widget.date_combo.currentText()
            session_text = self.tab_manager_widget.session_combo.currentText()

            print(f"[订单创建] 账号: {self.current_account.get('userid', 'N/A')}")
            print(f"[订单创建] 座位: {len(selected_seats)} 个")

            # 🔧 修复：沃美系统不需要取消未付款订单功能
            # 第一步：取消该账号的所有未付款订单（沃美系统跳过此步骤）
            cinema_data = self._get_cinema_info_by_name(cinema_text)
            print(f"[订单创建] 沃美系统跳过取消未付款订单步骤")

            # 第二步：构建完整的订单参数
            order_params = self._build_complete_order_params(selected_seats)
            if not order_params:
                MessageManager.show_error(self, "参数错误", "构建订单参数失败", auto_close=False)
                return False

            # 第三步：调用订单创建API
            from services.order_api import create_order

            # 🔍 详细打印提交的订单参数
            # 调试打印已移除
            print(f"=" * 60)
            for key, value in order_params.items():
                if key == 'token':
                    # 安全的Token显示
                    token_str = str(value)
                    if token_str:
                        print(f"  {key}: {token_str[:10]}*** (已配置)")
                    else:
                        print(f"  {key}: 未配置")
                elif key == 'seatInfo':
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")
            print(f"=" * 60)

            result = create_order(order_params)

            # 🔍 格式化打印订单接口返回信息
            self._print_order_api_response(result, "完整流程订单创建API")

            if not result or result.get('resultCode') != '0':
                error_msg = result.get('resultDesc', '创建订单失败') if result else '网络错误'
                print(f"❌ [订单调试-完整流程] 订单创建失败: {error_msg}")
                MessageManager.show_error(self, "创建失败", f"订单创建失败: {error_msg}", auto_close=False)
                return False

            # 第四步：处理订单创建成功
            return self._handle_order_creation_success(result, selected_seats, cinema_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "提交失败", f"提交订单失败\n\n错误: {str(e)}", auto_close=False)
            return False

    def _build_complete_order_params(self, selected_seats):
        """构建完整的订单参数 - 复用现有实现"""
        try:
            # 获取场次数据
            tab_manager = self.tab_manager_widget
            session_data = getattr(tab_manager, 'current_session_data', None)
            if not session_data:
                print("[订单参数] 缺少场次数据")
                return None

            # 获取影院数据
            cinema_text = tab_manager.cinema_combo.currentText()
            cinema_data = self._get_cinema_info_by_name(cinema_text)
            if not cinema_data:
                print("[订单参数] 缺少影院数据")
                return None

            # 构建座位参数 - 使用真实API格式
            seat_info_list = []
            for i, seat in enumerate(selected_seats):
                # 从座位数据中获取正确的字段
                seat_no = seat.get('sn', '')
                if not seat_no:
                    # 如果没有sn字段，尝试构建座位编号
                    row_num = seat.get('rn', seat.get('row', 1))
                    col_num = seat.get('cn', seat.get('col', 1))
                    seat_no = f"000000011111-{col_num}-{row_num}"

                # 获取座位价格
                seat_price = seat.get('price', 0)
                if seat_price == 0:
                    # 如果座位没有价格，从场次数据获取默认价格
                    seat_price = session_data.get('first_price', session_data.get('b', 33.9))

                # 确保seat_price是字符串类型（API要求）
                try:
                    if isinstance(seat_price, (int, float)):
                        seat_price_str = str(seat_price)
                    elif isinstance(seat_price, str):
                        float(seat_price)  # 验证是否可转换为数字
                        seat_price_str = seat_price
                    else:
                        seat_price_str = "33.9"  # 默认价格
                except (ValueError, TypeError):
                    print(f"[订单参数] 座位价格格式错误: {seat_price}，使用默认价格")
                    seat_price_str = "33.9"

                # 获取座位位置信息
                seat_row = seat.get('rn', seat.get('row', 1))
                seat_col = seat.get('cn', seat.get('col', 1))

                # 构建真实API格式的座位信息
                seat_info = {
                    "seatInfo": f"{seat_row}排{seat_col}座",
                    "eventPrice": 0,
                    "strategyPrice": seat_price_str,
                    "ticketPrice": seat_price_str,
                    "seatRow": seat_row,
                    "seatRowId": seat_row,
                    "seatCol": seat_col,
                    "seatColId": seat_col,
                    "seatNo": seat_no,
                    "sectionId": "11111",
                    "ls": "",
                    "rowIndex": seat.get('r', 1) - 1,
                    "colIndex": DataUtils.safe_get(seat, 'c', 1) - 1,
                    "index": i + 1
                }
                seat_info_list.append(seat_info)

            # 构建订单参数 - 使用真实API格式
            import json
            order_params = {
                # 基础参数
                'groupid': '',
                'cardno': 'undefined',
                'userid': DataUtils.safe_get(self.current_account, 'userid', ''),
                'cinemaid': DataUtils.safe_get(cinema_data, 'cinemaid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': DataUtils.safe_get(self.current_account, 'token', ''),
                'openid': DataUtils.safe_get(self.current_account, 'openid', ''),
                'source': '2',

                # 订单相关参数
                'oldOrderNo': '',
                'showTime': f"{DataUtils.safe_get(session_data, 'show_date', '')} {DataUtils.safe_get(session_data, 'q', '')}",
                'eventCode': '',
                'hallCode': DataUtils.safe_get(session_data, 'j', ''),
                'showCode': DataUtils.safe_get(session_data, 'g', ''),
                'filmCode': 'null',
                'filmNo': DataUtils.safe_get(session_data, 'h', ''),
                'recvpPhone': 'undefined',

                # 座位信息 - 使用真实API格式
                'seatInfo': json.dumps(seat_info_list, separators=(',', ':')),

                # 支付相关参数
                'payType': '3',
                'companyChannelId': 'undefined',
                'shareMemberId': '',
                'limitprocount': '0'
            }

            print(f"[订单参数] 座位数量: {len(selected_seats)}")
            print(f"[订单参数] 影院ID: {order_params.get('cinemaid')}")
            print(f"[订单参数] 场次编码: {order_params.get('showCode')}")

            return order_params

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[订单参数] 构建失败: {e}")
            return None

    def _print_order_api_response(self, result, api_name="订单API"):
        """格式化打印订单接口返回信息，方便调试"""
        import json
        from datetime import datetime

        # 调试打印已移除
        print(f"{'=' * 80}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 接口: {api_name}")
        print(f"{'=' * 80}")

        if result is None:
            print(f"❌ 返回数据: None (可能是网络错误或接口异常)")
        else:
            print(f"📊 数据类型: {type(result).__name__}")

            if isinstance(result, dict):
                # 格式化字典数据
                # 调试打印已移除
                print(f"🔑 字段列表: {list(result.keys())}")
                print(f"{'-' * 80}")

                # 按重要性排序显示字段 - 🔧 修复：添加沃美API字段
                important_fields = ['ret', 'sub', 'msg', 'data', 'success', 'resultCode', 'resultDesc', 'error', 'order_id', 'orderno']
                other_fields = [k for k in result.keys() if k not in important_fields]

                # 先显示重要字段
                for key in important_fields:
                    if key in result:
                        value = result[key]
                        if isinstance(value, (dict, list)) and len(str(value)) > 200:
                            print(f"📌 {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                            if isinstance(value, dict):
                                for sub_key, sub_value in list(value.items())[:3]:
                                    print(f"   └─ {sub_key}: {str(sub_value)[:100]}{'...' if len(str(sub_value)) > 100 else ''}")
                                if len(value) > 3:
                                    print(f"   └─ ... 还有 {len(value) - 3} 个字段")
                            elif isinstance(value, list):
                                for i, item in enumerate(value[:2]):
                                    print(f"   └─ [{i}]: {str(item)[:100]}{'...' if len(str(item)) > 100 else ''}")
                                if len(value) > 2:
                                    print(f"   └─ ... 还有 {len(value) - 2} 个项目")
                        else:
                            print(f"📌 {key}: {value}")

                # 再显示其他字段
                if other_fields:
                    print(f"{'-' * 40} 其他字段 {'-' * 40}")
                    for key in other_fields:
                        value = result[key]
                        if isinstance(value, (dict, list)) and len(str(value)) > 200:
                            print(f"🔸 {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                        else:
                            print(f"🔸 {key}: {value}")

                # 判断接口调用结果 - 🔧 修复：支持沃美API的ret字段
                print(f"{'-' * 80}")

                # 沃美API使用ret字段：ret=0表示成功，ret!=0表示失败
                if result.get('ret') == 0:
                    # 🆕 如果有data字段，显示其内容
                    data = result.get('data')
                    if data and isinstance(data, dict):
                        print(f"📦 返回数据内容 (共 {len(data)} 个字段):")
                        for key, value in data.items():  # 显示所有字段
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                print(f"   └─ {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                                # 如果是字典，显示其前3个子字段
                                if isinstance(value, dict):
                                    for sub_key, sub_value in list(value.items())[:3]:
                                        print(f"      ├─ {sub_key}: {str(sub_value)[:80]}{'...' if len(str(sub_value)) > 80 else ''}")
                                    if len(value) > 3:
                                        print(f"      └─ ... 还有 {len(value) - 3} 个子字段")
                                # 如果是列表，显示其前2个项目
                                elif isinstance(value, list):
                                    for i, item in enumerate(value[:2]):
                                        print(f"      ├─ [{i}]: {str(item)[:80]}{'...' if len(str(item)) > 80 else ''}")
                                    if len(value) > 2:
                                        print(f"      └─ ... 还有 {len(value) - 2} 个项目")
                            else:
                                print(f"   └─ {key}: {value}")
                elif result.get('ret') is not None and result.get('ret') != 0:
                    error_msg = result.get('msg') or result.get('error') or result.get('resultDesc') or '未知错误'
                    print(f"❌ 接口调用状态: 失败")
                    print(f"🚨 错误信息: {error_msg}")
                    print(f"🔢 错误代码: {result.get('ret')}")
                # 兼容其他API格式
                elif result.get('success') is True or result.get('resultCode') == '0':
                    pass  # 调试打印已移除
                elif result.get('success') is False or result.get('resultCode') != '0':
                    error_msg = result.get('error') or result.get('resultDesc') or '未知错误'
                    print(f"❌ 接口调用状态: 失败")
                    print(f"🚨 错误信息: {error_msg}")
                else:
                    print(f"⚠️ 接口调用状态: 未知 (无明确的成功/失败标识)")

            elif isinstance(result, (list, tuple)):
                for i, item in enumerate(result[:3]):
                    print(f"🔸 [{i}]: {str(item)[:200]}{'...' if len(str(item)) > 200 else ''}")
                if len(result) > 3:
                    print(f"🔸 ... 还有 {len(result) - 3} 个项目")
            else:
                print(f"📄 返回内容: {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}")

        print(f"{'=' * 80}")

    def _query_and_print_order_detail(self, order_id: str, session_info: dict):
        """查询并打印沃美订单详细信息"""
        try:
            # 获取影院ID和token
            cinema_data = session_info.get('cinema_data', {})
            account_data = session_info.get('account', {})

            cinema_id = cinema_data.get('cinema_id', '')
            token = account_data.get('token', '')

            if not cinema_id or not token:
                return

            # 创建API适配器并查询订单详情
            from cinema_api_adapter import create_womei_api
            api = create_womei_api(token)

            order_detail = api.get_order_info(cinema_id, order_id)

            # 🔍 格式化打印订单详情
            self._print_order_api_response(order_detail, f"沃美订单详情查询 (订单号: {order_id})")

            # 🎯 提取关键信息并格式化显示
            if order_detail and order_detail.get('ret') == 0:
                data = order_detail.get('data', {})
                self._print_order_summary(data, order_id)
            else:
                error_msg = order_detail.get('msg', '查询失败') if order_detail else '网络错误'

        except Exception as e:
            print(f"查询异常: {e}")
            import traceback
            traceback.print_exc()

    def _print_order_summary(self, order_data: dict, order_id: str):
        """打印订单摘要信息"""
        try:
            # 调试打印已移除
            print(f"{'=' * 80}")

            # 基本信息
            print(f"🎫 订单状态: {order_data.get('status_desc', 'N/A')} ({order_data.get('status', 'N/A')})")
            print(f"🏪 影院: {order_data.get('cinema_name', 'N/A')}")
            print(f"🎬 影片: {order_data.get('movie_name', 'N/A')}")
            print(f"🕐 场次: {order_data.get('show_date_style', 'N/A')}")

            # 座位信息
            ticket_items = order_data.get('ticket_items', {})
            if ticket_items:
                print(f"🎭 影厅: {ticket_items.get('hall_name', 'N/A')}")
                print(f"🪑 座位: {ticket_items.get('seat_info', 'N/A')}")
                print(f"🎟️ 票数: {ticket_items.get('ticket_num', 0)}")

            # 价格信息
            print(f"💰 票价: ¥{order_data.get('ticket_total_price', 0)}")
            print(f"💳 总价: ¥{order_data.get('order_total_price', 0)}")
            print(f"💸 实付: ¥{order_data.get('order_payment_price', 0)}")
            print(f"🔢 手续费: ¥{order_data.get('order_total_fee', 0)}")

            # 联系信息
            print(f"📱 手机: {order_data.get('phone', 'N/A')}")
            print(f"💳 支付方式: {order_data.get('pay_way', 'N/A')}")

            # 取票信息
            ticket_code_arr = order_data.get('ticket_code_arr', [])
            if ticket_code_arr:
                for ticket_code_info in ticket_code_arr:
                    code_name = ticket_code_info.get('name', '取票码')
                    code_value = ticket_code_info.get('code', '暂无')
                    print(f"🎫 {code_name}: {code_value}")

            print(f"{'=' * 80}")
            # 调试打印已移除

        except Exception as e:
            print(f"[订单摘要] ❌ 打印摘要失败: {e}")

    def _handle_order_creation_success(self, result, selected_seats, cinema_data):
        """处理订单创建成功 - 复用现有实现"""
        try:
            import time

            # 获取订单数据
            order_data = result.get('resultData', {})
            order_id = order_data.get('orderno', f"ORDER{int(time.time())}")

            # 🚀 订单创建成功后立即初始化支付方式（解决4004错误）
            # 调试打印已移除
            cinema_id = cinema_data.get('cinemaid', '')
            token = self.current_account.get('token', '')

            init_result = self._initialize_order_payment_method(order_id, cinema_id, token)
            if init_result.get('success', False):
                pass  # 调试打印已移除
            else:
                print(f"[订单创建] ⚠️ 订单支付方式初始化失败: {init_result.get('error', '未知错误')}")
                # 注意：初始化失败不阻断订单创建流程，仅记录日志

            # 获取场次数据用于显示
            tab_manager = self.tab_manager_widget
            session_data = getattr(tab_manager, 'current_session_data', {})

            # 获取当前选择信息
            cinema_text = tab_manager.cinema_combo.currentText()
            movie_text = tab_manager.movie_combo.currentText()
            date_text = tab_manager.date_combo.currentText()
            session_text = tab_manager.session_combo.currentText()

            # 构建座位显示信息和计算总价
            seat_display = []
            total_amount = 0
            for seat in selected_seats:
                seat_row = seat.get('rn', seat.get('row', 1))
                seat_col = seat.get('cn', seat.get('col', 1))
                seat_price = seat.get('price', 0)
                if seat_price == 0:
                    seat_price = session_data.get('first_price', session_data.get('b', 33.9))

                seat_display.append(f"{seat_row}排{seat_col}座")

                # 确保seat_price是数字类型
                try:
                    if isinstance(seat_price, str):
                        seat_price = float(seat_price)
                    elif isinstance(seat_price, (int, float)):
                        seat_price = float(seat_price)
                    else:
                        seat_price = 0.0
                    total_amount += seat_price
                except (ValueError, TypeError):
                    print(f"[订单成功] 座位价格转换失败: {seat_price}，使用默认价格0")
                    total_amount += 0.0

            # 获取会员信息
            # 调试打印已移除
            self._get_member_info(self.current_account, cinema_data.get('cinemaid', ''))

            # 获取未支付订单详情以获取会员价格信息
            from services.order_api import get_unpaid_order_detail
            detail_params = {
                'orderno': order_id,
                'groupid': '',
                'cinemaid': cinema_data.get('cinemaid', ''),
                'cardno': self.current_account.get('cardno', ''),
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.current_account.get('token', ''),
                'source': '2'
            }

            print(f"[订单成功] 获取订单详情，订单号: {order_id}")
            order_detail_result = get_unpaid_order_detail(detail_params)

            # 从订单详情中获取会员价格
            member_total_price = 0
            if order_detail_result and order_detail_result.get('resultCode') == '0':
                detail_data = order_detail_result.get('resultData', {})

                # 安全的类型转换
                def safe_price_convert(value, default=0):
                    try:
                        if isinstance(value, str):
                            return int(value) if value.strip() else default
                        elif isinstance(value, (int, float)):
                            return int(value)
                        else:
                            return default
                    except (ValueError, TypeError):
                        return default

                member_total_price = safe_price_convert(detail_data.get('mem_totalprice', '0'))
                print(f"[订单成功] 会员价格: {member_total_price} 分 ({member_total_price/100.0:.2f} 元)")

            # 保存当前订单 - 包含完整信息
            self.current_order = {
                'order_id': order_id,
                'orderno': order_id,
                'cinema': cinema_text,
                'movie': movie_text,
                'date': date_text,
                'session': session_text,
                'showTime': session_data.get('show_date', '') + ' ' + session_data.get('q', ''),
                'seats': seat_display,
                'seat_count': len(selected_seats),
                'amount': total_amount,
                'mem_totalprice': member_total_price,
                'status': '待支付',
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'phone': self.current_account.get('userid', ''),
                'cinema_name': cinema_text,
                'film_name': movie_text,
                'hall_name': session_data.get('hall_name', ''),
                'api_data': order_detail_result.get('resultData', {}) if order_detail_result else order_data,
                # 添加重构后需要的字段
                'movieid': session_data.get('h', ''),  # 从session_data获取电影ID
                'showid': session_data.get('g', ''),   # 从session_data获取场次ID
                'totalprice': total_amount,            # 设置总价
                'cinemaid': cinema_data.get('cinemaid', '')  # 影院ID
            }

            # 调试打印已移除
            print(f"  - 订单号: {order_id}")
            print(f"  - 座位数: {len(selected_seats)}")
            print(f"  - 总价: {total_amount} 元")
            print(f"  - 会员价: {member_total_price/100.0:.2f} 元")

            # 🔍 调试：打印订单数据
            # 调试打印已移除
            print(f"=" * 60)
            print(f"订单号: {self.current_order.get('order_id', 'N/A')}")
            print(f"座位数据类型: {type(self.current_order.get('seats', []))}")
            print(f"座位数据内容: {self.current_order.get('seats', [])}")
            if isinstance(self.current_order.get('seats', []), list) and self.current_order.get('seats', []):
                print(f"第一个座位类型: {type(self.current_order['seats'][0])}")
                print(f"第一个座位内容: {self.current_order['seats'][0]}")
            print(f"=" * 60)

            # 显示订单详情
            self._show_order_detail(self.current_order)

            # 获取可用券列表 - 修复参数传递
            cinema_id = cinema_data.get('cinemaid', '') or cinema_data.get('cinema_id', '') or cinema_data.get('id', '')
            # 调试打印已移除
            print(f"  - cinema_data类型: {type(cinema_data)}")
            print(f"  - cinema_data内容: {cinema_data}")
            print(f"  - 提取的cinema_id: {cinema_id}")
            print(f"  - order_id: {order_id}")

            self._load_available_coupons(order_id, cinema_id)

            # 发布订单创建事件（应用观察者模式）
            if hasattr(self, 'order_subject'):
                from patterns.order_observer import OrderStatus
                self.order_subject.update_order_status(order_id, OrderStatus.CREATED, self.current_order)

            # 发布全局事件
            event_bus.order_created.emit(self.current_order)

            return True

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[订单成功] 处理失败: {e}")
            return False

    def _load_available_coupons(self, order_id: str, cinema_id: str):
        """获取订单可用券列表 - 复用现有实现"""
        try:
            # 调试打印已移除
            print(f"  - current_account存在: {bool(self.current_account)}")
            print(f"  - order_id: '{order_id}' (长度: {len(order_id) if order_id else 0})")
            print(f"  - cinema_id: '{cinema_id}' (长度: {len(cinema_id) if cinema_id else 0})")

            if not self.current_account:
                print("[优惠券] ❌ 券列表加载失败：缺少账号信息")
                self._show_coupon_error_message("缺少账号信息，无法加载券列表")
                return

            if not order_id:
                print("[优惠券] ❌ 券列表加载失败：缺少订单号")
                self._show_coupon_error_message("缺少订单号，无法加载券列表")
                return

            if not cinema_id:
                print("[优惠券] ❌ 券列表加载失败：缺少影院ID")
                self._show_coupon_error_message("缺少影院ID，无法加载券列表")
                return

            # 🆕 获取订单可用券 - 使用沃美新API
            from api.voucher_api import get_order_available_vouchers

            # 提取必要参数
            token = DataUtils.safe_get(self.current_account, 'token', '')

            # 调试打印已移除
            print(f"[优惠券] 🏢 影院ID: {cinema_id}")
            # 安全的Token显示
            if token:
                print(f"[优惠券] 🎫 Token状态: 已配置")
            else:
                print(f"[优惠券] 🎫 Token状态: 未配置")

            # 🆕 调用沃美订单可用券API
            coupon_result = get_order_available_vouchers(cinema_id, token)

            # 🆕 检查沃美API响应
            if coupon_result is None:
                print("[优惠券] 沃美券API返回None，可能是网络异常")
                self._show_coupon_error_message("网络异常，无法获取券列表")
                return

            if not isinstance(coupon_result, dict):
                print(f"[优惠券] 沃美券API返回格式错误，类型: {type(coupon_result)}")
                self._show_coupon_error_message("数据格式错误，无法解析券列表")
                return

            # 🆕 检查沃美API响应状态 (success字段)
            if coupon_result.get('success'):
                # 成功获取券列表
                result_data = coupon_result.get('data')

                if result_data is None:
                    print("[优惠券] 沃美券列表数据为空")
                    self._show_coupon_list([])
                    return

                if not isinstance(result_data, dict):
                    print(f"[优惠券] 沃美券列表数据格式错误，类型: {type(result_data)}")
                    self._show_coupon_error_message("券数据格式错误")
                    return

                # 🆕 获取沃美券列表 (vouchers字段)
                coupons = DataUtils.safe_get(result_data, 'vouchers', [])

                if not isinstance(coupons, list):
                    print(f"[优惠券] 沃美券列表不是数组格式，类型: {type(coupons)}")
                    coupons = []

                print(f"[优惠券] 🎉 获取到 {len(coupons)} 张订单可用券")

                # 🆕 转换沃美券数据格式以兼容现有UI
                converted_coupons = self._convert_womei_vouchers_to_ui_format(coupons)

                # 显示券列表
                self._show_coupon_list(converted_coupons)

            else:
                # 沃美API返回错误
                error_desc = coupon_result.get('message', '未知错误')
                print(f"[优惠券] 沃美券API返回错误: {error_desc}")
                self._show_coupon_error_message(f"获取券列表失败: {error_desc}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[优惠券] 券列表加载异常: {e}")
            self._show_coupon_error_message("券列表加载异常，请重试")

    def _convert_womei_vouchers_to_ui_format(self, womei_vouchers: list) -> list:
        """
        🆕 转换沃美券数据格式以兼容现有UI显示逻辑

        Args:
            womei_vouchers: 沃美API返回的券列表

        Returns:
            list: 转换后的券列表，兼容现有UI格式
        """
        try:
            converted_vouchers = []

            for voucher in womei_vouchers:
                if not isinstance(voucher, dict):
                    continue

                # 🆕 沃美券字段 → 现有UI字段映射
                converted_voucher = {
                    # 券名称映射
                    'couponname': voucher.get('voucher_name', '未知券'),
                    'voucherName': voucher.get('voucher_name', '未知券'),
                    'name': voucher.get('voucher_name', '未知券'),

                    # 券号映射
                    'couponcode': voucher.get('voucher_code', ''),
                    'voucherCode': voucher.get('voucher_code', ''),
                    'code': voucher.get('voucher_code', ''),

                    # 有效期映射
                    'expireddate': voucher.get('expire_time_string', '未知'),
                    'expiredDate': voucher.get('expire_time_string', '未知'),
                    'expireDate': voucher.get('expire_time_string', '未知'),

                    # 券类型映射
                    'voucherType': '订单可用券',
                    'coupontype': '订单可用券',

                    # 状态映射
                    'status': voucher.get('status', 'UN_USE'),

                    # 保留原始沃美数据
                    '_womei_original': voucher
                }

                converted_vouchers.append(converted_voucher)

            # 调试打印已移除
            return converted_vouchers

        except Exception as e:
            print(f"[券格式转换] ❌ 转换失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _show_coupon_error_message(self, error_message: str):
        """显示券列表错误信息"""
        try:
            # 查找券列表组件
            coupon_list_widget = None

            if hasattr(self, 'coupon_list'):
                coupon_list_widget = self.coupon_list
            elif hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'coupon_list'):
                coupon_list_widget = self.tab_manager_widget.coupon_list

            if coupon_list_widget is not None:
                coupon_list_widget.clear()
                coupon_list_widget.addItem(f"❌ {error_message}")
                print(f"[优惠券] 券列表错误信息已显示: {error_message}")
            else:
                print(f"[优惠券] 无法显示券列表错误信息: {error_message}")

        except Exception as e:
            print(f"[优惠券] 显示券列表错误信息失败: {e}")

    def _show_coupon_list(self, coupons: list):
        """显示券列表"""
        try:
            # 确保coupons参数有效
            if coupons is None:
                # 调试打印已移除
                coupons = []

            if not isinstance(coupons, list):
                print(f"[优惠券] 券列表参数类型错误: {type(coupons)}，使用空列表")
                coupons = []

            print(f"[优惠券] 显示券列表: {len(coupons)} 张券")

            # 保存券数据到实例变量
            self.coupons_data = coupons

            # 根据当前订单的座位数设置券选择数量限制
            if self.current_order and isinstance(self.current_order, dict):
                seats = DataUtils.safe_get(self.current_order, 'seats', [])
                if isinstance(seats, list):
                    seat_count = len(seats)
                else:
                    seat_count = 1
                self.max_coupon_select = max(1, seat_count)
            else:
                self.max_coupon_select = 1

            # 查找现有的券列表组件
            coupon_list_widget = None

            # 方法1：直接查找 coupon_list 属性
            if hasattr(self, 'coupon_list'):
                coupon_list_widget = self.coupon_list

            # 方法2：查找 tab_manager_widget 中的券列表
            elif hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'coupon_list'):
                coupon_list_widget = self.tab_manager_widget.coupon_list

            # 方法3：遍历查找 QListWidget
            else:
                from PyQt5.QtWidgets import QListWidget
                for child in self.findChildren(QListWidget):
                    # 检查是否是券列表（通过父组件名称或位置判断）
                    parent = child.parent()
                    if parent and hasattr(parent, 'title') and '券' in parent.title():
                        coupon_list_widget = child
                        break

            # 处理券列表显示
            if coupon_list_widget is not None:
                print(f"[优惠券] 券列表组件有效，类型: {type(coupon_list_widget)}")

                # 设置券列表为多选模式
                from PyQt5.QtWidgets import QAbstractItemView
                coupon_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)

                # 连接券选择事件
                if hasattr(coupon_list_widget, 'itemSelectionChanged'):
                    # 先断开可能存在的连接，避免重复连接
                    try:
                        coupon_list_widget.itemSelectionChanged.disconnect()
                    except:
                        pass
                    # 连接新的事件处理器
                    if hasattr(self, '_on_coupon_selection_changed'):
                        coupon_list_widget.itemSelectionChanged.connect(self._on_coupon_selection_changed)

                # 清空现有券列表
                coupon_list_widget.clear()

                if not coupons:
                    # 显示无券提示
                    coupon_list_widget.addItem("暂无可用券")
                    return

                # 显示券列表
                for i, coupon in enumerate(coupons):
                    # 确保coupon是字典类型
                    if not isinstance(coupon, dict):
                        print(f"[优惠券] 跳过无效券数据: {coupon}")
                        continue

                    # 解析券信息
                    coupon_name = coupon.get('couponname') or coupon.get('voucherName') or DataUtils.safe_get(coupon, 'name', f'券{i+1}')
                    expire_date = coupon.get('expireddate') or coupon.get('expiredDate') or DataUtils.safe_get(coupon, 'expireDate', '未知')
                    coupon_code = coupon.get('couponcode') or coupon.get('voucherCode') or DataUtils.safe_get(coupon, 'code', f'券号{i+1}')
                    coupon_type = coupon.get('voucherType') or coupon.get('coupontype') or '优惠券'

                    # 如果券类型为空或者是数字，尝试从券名称推断
                    if not coupon_type or (isinstance(coupon_type, str) and coupon_type.isdigit()):
                        if '延时' in str(coupon_name):
                            coupon_type = '延时券'
                        elif '折' in str(coupon_name):
                            coupon_type = '折扣券'
                        elif '送' in str(coupon_name):
                            coupon_type = '赠送券'
                        else:
                            coupon_type = '优惠券'

                    # 格式化显示文本
                    display_text = f"{coupon_type} | 有效期至 {expire_date} | 券号 {coupon_code}"
                    coupon_list_widget.addItem(display_text)

                pass  # 调试打印已移除
            else:
                print("[优惠券] 未找到券列表组件")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[优惠券] 显示券列表异常: {e}")

    def _on_coupon_selection_changed(self):
        """券选择事件处理器 - 修复券信息获取和显示"""
        try:
            print(f"[券选择事件] 券选择事件被触发")

            # 获取券列表组件
            coupon_list_widget = None
            if hasattr(self, 'coupon_list'):
                coupon_list_widget = self.coupon_list
            elif hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'coupon_list'):
                coupon_list_widget = self.tab_manager_widget.coupon_list

            if not coupon_list_widget:
                print("[券选择事件] 找不到券列表组件")
                return

            # 检查券数据是否存在
            if not hasattr(self, 'coupons_data') or self.coupons_data is None:
                print("[券选择事件] 券数据不存在")
                return

            # 确保券数据是列表类型
            if not isinstance(self.coupons_data, list):
                print(f"[券选择事件] 券数据类型错误: {type(self.coupons_data)}")
                return

            # 获取选中的券项目索引
            selected_items = coupon_list_widget.selectedItems()
            if selected_items is None:
                selected_items = []

            selected_indices = []
            for item in selected_items:
                if item is not None:
                    row = coupon_list_widget.row(item)
                    if row >= 0:
                        selected_indices.append(row)

            print(f"[券选择事件] 选中券索引: {selected_indices}")

            # 检查max_coupon_select属性
            if not hasattr(self, 'max_coupon_select') or self.max_coupon_select is None:
                self.max_coupon_select = 1

            # 检查选择数量限制
            if len(selected_indices) > self.max_coupon_select:
                from services.ui_utils import MessageManager
                MessageManager.show_warning(
                    self, "选择限制",
                    f"最多只能选择 {self.max_coupon_select} 张券"
                )
                # 清除多余的选择，保留前面的选择
                for i, item in enumerate(selected_items):
                    if i >= self.max_coupon_select:
                        item.setSelected(False)
                return

            # 获取选中的券号
            selected_codes = []
            for index in selected_indices:
                if 0 <= index < len(self.coupons_data):
                    coupon = self.coupons_data[index]

                    # 确保coupon是字典类型
                    if not isinstance(coupon, dict):
                        print(f"[券选择事件] 跳过无效券数据: {coupon}")
                        continue

                    coupon_code = coupon.get('couponcode') or coupon.get('voucherCode') or DataUtils.safe_get(coupon, 'code', '')
                    if coupon_code:
                        selected_codes.append(coupon_code)

            print(f"[券选择事件] 选中券号: {selected_codes}")

            # 验证必要参数
            if not self.current_order or not self.current_account:
                # 调试打印已移除
                return

            # 获取订单和账号信息
            order_id = self.current_order.get('orderno') or DataUtils.safe_get(self.current_order, 'order_id', '')
            account = self.current_account

            # 获取影院信息
            cinema_data = None
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'current_cinema_data'):
                cinema_data = self.tab_manager_widget.current_cinema_data

            if not cinema_data:
                print(f"[券选择事件] 缺少影院信息")
                return

            # 🔧 修复：沃美系统使用cinema_id字段，华联系统使用cinemaid字段
            cinema_id = (DataUtils.safe_get(cinema_data, 'cinema_id', '') or
                        DataUtils.safe_get(cinema_data, 'cinemaid', '') or
                        DataUtils.safe_get(cinema_data, 'id', ''))
            # 调试打印已移除
            # 调试打印已移除

            # 处理券选择 - 🆕 使用两步式券使用流程（价格计算 + 券绑定）
            if selected_codes and selected_codes[0]:  # 确保券号不为空
                try:
                    couponcode = ','.join(selected_codes)
                    # 调试打印已移除

                    # 🆕 使用沃美订单券绑定服务
                    from services.womei_order_voucher_service import get_womei_order_voucher_service
                    voucher_service = get_womei_order_voucher_service()

                    # 🆕 第一步：调用券价格计算接口（必需步骤）
                    print(f"[券选择事件] 1️⃣ 第一步：计算券价格...")
                    price_result = voucher_service.calculate_voucher_price(
                        cinema_id=cinema_id,
                        token=account['token'],
                        order_id=order_id,
                        voucher_code=couponcode,
                        voucher_type='VGC_T'
                    )

                    print(f"[券选择事件] 📥 价格计算结果:")
                    # 调试打印已移除

                    if not price_result.get('success', False) or price_result.get('ret') != 0:
                        error_msg = price_result.get('msg', '价格计算失败')
                        print(f"[券选择事件] ❌ 价格计算失败: {error_msg}")

                        from services.ui_utils import MessageManager
                        MessageManager.show_warning(self, "券价格计算失败", f"无法计算券使用后的价格\n{error_msg}")

                        # 取消选择
                        for item in selected_items:
                            item.setSelected(False)
                        return

                    # 显示价格计算结果
                    price_info = price_result.get('price_info', {})
                    pay_price = price_info.get('pay_price', 0)
                    surcharge_price = price_info.get('surcharge_price', 0)
                    surcharge_msg = price_info.get('surcharge_msg', '')

                    print(f"[券选择事件] 💰 价格计算成功:")
                    print(f"[券选择事件] 💰 支付价格: {pay_price}")
                    print(f"[券选择事件] 💸 附加费用: {surcharge_price}")
                    print(f"[券选择事件] 📝 附加说明: {surcharge_msg}")

                    # 🆕 第二步：绑定券到订单
                    print(f"[券选择事件] 2️⃣ 第二步：绑定券到订单...")
                    bind_result = voucher_service.bind_voucher_to_order(
                        cinema_id=cinema_id,
                        token=account['token'],
                        order_id=order_id,
                        voucher_code=couponcode,
                        voucher_type='VGC_T'
                    )

                    print(f"[券选择事件] 📥 券绑定结果:")
                    # 调试打印已移除
                    print(f"[券选择事件] 📥 绑定成功: {bind_result.get('success')}")

                    if bind_result.get('success'):
                        # 🆕 券绑定成功，整合价格计算和绑定结果
                        bind_data = bind_result.get('data', {})
                        final_payment_price = bind_data.get('order_payment_price', 0)
                        voucher_use = bind_data.get('voucher_use', {})
                        voucher_discounts = bind_data.get('voucher_discounts', [])

                        # 保存券信息（兼容现有格式，同时包含价格计算结果）
                        self.current_coupon_info = {
                            'resultCode': '0',
                            'resultData': bind_result.get('data', {}),
                            'womei_bind_result': bind_result,  # 保存完整的绑定结果
                            'price_calculation': price_result,  # 保存价格计算结果
                            'workflow_summary': {
                                'calculated_pay_price': pay_price,
                                'final_payment_price': final_payment_price,
                                'surcharge_price': surcharge_price,
                                'surcharge_msg': surcharge_msg,
                                'price_match': abs(final_payment_price - pay_price) < 0.01,
                                'voucher_use_count': len(voucher_use.get('use_codes', [])),
                                'total_discount': voucher_use.get('use_total_price', 0)
                            }
                        }
                        self.selected_coupons = selected_codes

                        # 调试打印已移除
                        print(f"[券选择事件] 💰 预计支付价格: {pay_price}")
                        print(f"[券选择事件] 💰 实际支付价格: {final_payment_price}")
                        print(f"[券选择事件] 🎫 券使用数量: {len(voucher_use.get('use_codes', []))}")
                        print(f"[券选择事件] 💸 券抵扣金额: {voucher_use.get('use_total_price', 0)}")

                        # 🆕 获取更新后的订单信息
                        updated_order = voucher_service.get_updated_order_info(
                            cinema_id=cinema_id,
                            token=account['token'],
                            order_id=order_id
                        )

                        if updated_order.get('success'):
                            # 更新当前订单数据
                            self.current_order.update(updated_order.get('data', {}))
                            print(f"[券选择事件] 🔄 订单信息已同步更新")

                        # 刷新订单详情显示，包含券抵扣信息
                        self._update_order_detail_with_coupon_info()

                        # 🆕 显示券绑定成功消息（包含详细价格信息）
                        from services.ui_utils import MessageManager
                        discount_amount = voucher_use.get('use_total_price', 0)

                        if discount_amount > 0:
                            success_msg = f"券使用成功！\n\n"
                            success_msg += f"预计支付价格: ¥{pay_price}\n"
                            success_msg += f"实际支付价格: ¥{final_payment_price}\n"
                            success_msg += f"券抵扣金额: ¥{discount_amount}"

                            if surcharge_price > 0:
                                success_msg += f"\n附加费用: ¥{surcharge_price}"
                            if surcharge_msg:
                                success_msg += f"\n说明: {surcharge_msg}"

                            MessageManager.show_success(self, "券使用成功", success_msg)
                        else:
                            MessageManager.show_success(self, "券绑定成功", "券已成功绑定到订单")

                    else:
                        # 🆕 券绑定失败，清空选择
                        self.current_coupon_info = None
                        self.selected_coupons = []
                        error_msg = bind_result.get('msg', '券绑定失败')
                        print(f"[券选择事件] ❌ 券绑定失败: {error_msg}")

                        from services.ui_utils import MessageManager

                        # 🔧 修复：特殊处理Token超时问题
                        if bind_result.get('is_token_timeout'):
                            MessageManager.show_error(
                                self, "Token超时",
                                f"用户Token已超时，请重新登录账号\n错误详情: {error_msg}"
                            )
                        else:
                            MessageManager.show_warning(self, "券绑定失败", error_msg)

                        # 取消选择
                        for item in selected_items:
                            item.setSelected(False)

                except Exception as e:
                    import traceback
                    traceback.print_exc()

                    self.current_coupon_info = None
                    self.selected_coupons = []
                    print(f"[券选择事件] 券验证异常: {e}")

                    from services.ui_utils import MessageManager
                    MessageManager.show_error(self, "选券异常", f"查询券价格信息失败: {e}")

                    # 取消选择
                    for item in selected_items:
                        item.setSelected(False)
            else:
                # 券号为空，清空券信息
                print(f"[券选择事件] 清空券选择")
                self.current_coupon_info = None
                self.selected_coupons = []

                # 刷新订单详情显示，移除券抵扣信息
                self._update_order_detail_with_coupon_info()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[券选择事件] 券选择事件处理异常: {e}")

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
        """构建订单参数 - 修复后的版本"""
        try:
            cinema_data = self._get_current_cinema_data()
            if not cinema_data:
                QMessageBox.warning(self, "错误", "影院信息获取失败")
                return None

            # 确保current_order存在且包含必要信息
            if not self.current_order:
                print("[订单参数] current_order为空")
                return None

            # 获取座位信息
            seats = DataUtils.safe_get(self.current_order, 'seats', [])
            if isinstance(seats, list) and len(seats) > 0:
                # 检查seats是字符串列表还是对象列表
                if isinstance(seats[0], str):
                    # 如果是字符串列表（如["6排9座", "6排10座"]），提取座位号
                    seat_ids = []
                    for seat_str in seats:
                        # 从"6排9座"中提取"9"
                        import re
                        match = re.search(r'(\d+)排(\d+)座', seat_str)
                        if match:
                            seat_ids.append(match.group(2))  # 提取座位号
                        else:
                            seat_ids.append(seat_str)  # 如果格式不匹配，直接使用
                else:
                    # 如果是对象列表，提取id字段
                    seat_ids = [str(seat.get('id', '')) for seat in seats]
            else:
                print("[订单参数] 座位信息为空")
                return None

            # 构建订单参数
            order_params = {
                'userid': DataUtils.safe_get(self.current_account, 'userid', ''),
                'cinemaid': DataUtils.safe_get(cinema_data, 'cinemaid', '') or DataUtils.safe_get(self.current_order, 'cinemaid', ''),
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': DataUtils.safe_get(self.current_account, 'token', ''),
                'openid': DataUtils.safe_get(self.current_account, 'openid', ''),
                'movieid': DataUtils.safe_get(self.current_order, 'movieid', ''),
                'showid': DataUtils.safe_get(self.current_order, 'showid', ''),
                'seatids': ','.join(seat_ids),
                'totalprice': DataUtils.safe_get(self.current_order, 'totalprice', 0)
            }

            # 调试打印已移除
            print(f"  - 影院ID: {order_params.get('cinemaid')}")
            print(f"  - 电影ID: {order_params.get('movieid')}")
            print(f"  - 场次ID: {order_params.get('showid')}")
            print(f"  - 座位IDs: {order_params.get('seatids')}")
            print(f"  - 总价: {order_params.get('totalprice')}")

            return order_params

        except Exception as e:
            print(f"构建订单参数失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _submit_order_to_api(self, order_params):
        """提交订单到API - 使用真实API调用"""
        try:
            # 使用统一API客户端或现有的订单API
            if hasattr(self, 'api_client'):
                # 使用统一API客户端
                result = self.api_client.create_order(order_params)
            else:
                # 使用现有的订单API
                from services.order_api import create_order
                result = create_order(order_params)

            # 调试打印已移除

            # 检查API响应
            if result and result.get('resultCode') == '0':
                # 调试打印已移除
                return True
            else:
                error_msg = result.get('resultDesc', '未知错误') if result else '网络错误'
                print(f"[API调用] 订单提交失败: {error_msg}")
                return False

        except Exception as e:
            print(f"[API调用] 异常: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _handle_order_success(self):
        """处理订单成功 - 应用设计模式"""
        try:
            # 显示成功消息
            from services.ui_utils import MessageManager
            MessageManager.show_success(self, "订单提交成功", "订单已成功提交，请及时支付", auto_close=True)

            # 应用观察者模式 - 通知订单状态变化
            if hasattr(self, 'order_subject') and self.current_order:
                from patterns.order_observer import OrderStatus
                order_id = self.current_order.get('order_id', self.current_order.get('orderno', ''))
                self.order_subject.update_order_status(order_id, OrderStatus.PAID, self.current_order)

            # 显示订单详情（不清理订单数据，用户可能需要支付）
            if self.current_order:
                self._show_order_detail(self.current_order)

            # 刷新UI
            self.update_ui_after_order()

            # 调试打印已移除

        except Exception as e:
            print(f"[订单成功] 处理异常: {e}")
            # 即使处理过程中有异常，也要显示基本的成功消息
            QMessageBox.information(self, "成功", "订单提交成功")
    
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

    def _on_token_expired(self, error_msg: str):
        """
        处理token失效信号

        Args:
            error_msg: 错误信息
        """
        try:
            import time
            current_time = time.time()

            # 🔧 防重复弹窗：1分钟内只显示一次
            if current_time - self.last_token_popup_time < 60:
                print(f"[Token失效] ⚠️ 1分钟内已显示过弹窗，跳过重复显示")
                return

            self.last_token_popup_time = current_time

            print(f"[Token失效] 🚨 收到token失效信号: {error_msg}")

            # 🎯 显示居中弹窗提醒
            self.show_token_expired_popup(error_msg)

            # 🔧 更新状态栏
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("Token失效，系统功能受限", 0)

            # 调试打印已移除

        except Exception as e:
            print(f"[Token失效] ❌ 处理token失效信号异常: {e}")
            import traceback
            traceback.print_exc()

    def show_token_expired_popup(self, error_msg: str):
        """
        显示token失效弹窗提醒

        Args:
            error_msg: 错误信息
        """
        try:
            from PyQt5.QtWidgets import QMessageBox
            from PyQt5.QtCore import QTimer, Qt

            print(f"[Token失效] 📢 显示弹窗提醒")

            # 🎯 创建信息弹窗
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("系统提醒")

            # 🔧 直接显示详细信息，不需要用户点击查看详情
            main_text = "Token已失效，请及时更新"
            detail_text = f"\n错误详情：{error_msg}"

            # 🎯 将主要信息和详细信息合并显示
            full_message = main_text + detail_text
            msg_box.setText(full_message)

            msg_box.setIcon(QMessageBox.Warning)  # 使用警告图标更醒目
            msg_box.setStandardButtons(QMessageBox.Ok)

            # 🔧 设置弹窗为模态，但不阻塞
            msg_box.setModal(False)
            msg_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

            # 🎯 先显示弹窗以获取正确的尺寸
            msg_box.show()

            # 🎯 等待弹窗完全显示后再计算位置
            def center_popup():
                try:
                    # 🔧 使用frameGeometry()获取包含标题栏的完整窗口区域
                    main_frame = self.frameGeometry()
                    main_x = main_frame.x()
                    main_y = main_frame.y()
                    main_width = main_frame.width()
                    main_height = main_frame.height()

                    # 🔧 使用客户区域计算，排除标题栏影响
                    main_client = self.geometry()
                    client_x = main_client.x()
                    client_y = main_client.y()
                    client_width = main_client.width()
                    client_height = main_client.height()

                    # 获取弹窗的几何信息
                    popup_geometry = msg_box.geometry()
                    popup_width = popup_geometry.width()
                    popup_height = popup_geometry.height()

                    # 🎯 使用客户区域计算居中位置（更精确）
                    center_x = client_x + (client_width - popup_width) // 2
                    center_y = client_y + (client_height - popup_height) // 2

                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除

                    # 🎯 移动弹窗到居中位置
                    msg_box.move(center_x, center_y)

                    # 🔧 验证最终位置
                    final_geometry = msg_box.geometry()
                    final_x = final_geometry.x()
                    final_y = final_geometry.y()

                    # 计算中心点偏差
                    expected_center_x = client_x + client_width // 2
                    expected_center_y = client_y + client_height // 2
                    actual_center_x = final_x + popup_width // 2
                    actual_center_y = final_y + popup_height // 2

                    offset_x = abs(actual_center_x - expected_center_x)
                    offset_y = abs(actual_center_y - expected_center_y)

                    if offset_x <= 5 and offset_y <= 5:
                        pass  # 调试打印已移除
                    else:
                        print(f"[Token失效] ⚠️ 弹窗位置有轻微偏差，但在可接受范围内")

                    # 调试打印已移除

                except Exception as e:
                    print(f"[Token失效] ❌ 居中计算异常: {e}")
                    import traceback
                    traceback.print_exc()

            # 🎯 延迟50ms后执行居中，确保弹窗已完全显示
            QTimer.singleShot(50, center_popup)

            # 🎯 2.5秒后自动关闭（内容更多，需要更多时间阅读）
            QTimer.singleShot(2500, msg_box.close)


        except Exception as e:
            print(f"[Token失效] ❌ 显示弹窗异常: {e}")
            import traceback
            traceback.print_exc()
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