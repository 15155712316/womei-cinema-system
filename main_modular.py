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
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QTimer

# 导入插件系统
from ui.interfaces.plugin_interface import (
    IWidgetInterface, event_bus, plugin_manager
)

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
from utils.machine_code import get_machine_code
import json, os, time, traceback

# 导入登录窗口
from ui.login_window import LoginWindow


class ModularCinemaMainWindow(QMainWindow):
    """模块化影院下单系统主窗口"""
    
    # 定义信号
    login_success = pyqtSignal(dict)  # 登录成功信号
    
    def __init__(self):
        super().__init__()
        
        # 初始化业务服务
        self.auth_service = AuthService()
        self.cinema_manager = CinemaManager()
        self.member_service = MemberService()
        
        # ===== 第三步：复制关键数据属性（从源项目复制） =====
        self.current_user = None
        self.current_account = None
        self.current_order = None
        self.member_info = None
        self.selected_coupons = []
        self.selected_coupons_info = None
        self.current_coupon_info = None
        self.coupons_data = []
        self.max_coupon_select = 1
        self.ui_state = "initial"
        self.show_debug = False
        self.last_priceinfo = {}
        
        # 定时器相关（使用QTimer替代tkinter.after）
        self.auth_check_timer = None
        self.countdown_timer = None
        self.countdown_seconds = 0
        
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
        
        # 启动用户认证检查
        QTimer.singleShot(100, self._start_auth_check)
    
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
        
        print("[主窗口] 模块化UI初始化完成")
    
    def _create_seat_area(self) -> QWidget:
        """创建独立的座位选择区域"""
        from ui.widgets.classic_components import ClassicGroupBox, ClassicLabel, ClassicLineEdit, ClassicButton
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 座位区域组
        seat_group = ClassicGroupBox("座位区域")
        seat_layout = QVBoxLayout(seat_group)
        seat_layout.setContentsMargins(10, 20, 10, 10)
        seat_layout.setSpacing(10)
        
        # 座位选择输入
        seat_input_layout = QHBoxLayout()
        seat_label = ClassicLabel("选择座位:")
        seat_label.setMinimumWidth(80)
        self.seat_input = ClassicLineEdit()
        self.seat_input.setPlaceholderText("请输入座位号，如: A1,A2,B3")
        seat_input_layout.addWidget(seat_label)
        seat_input_layout.addWidget(self.seat_input)
        seat_layout.addLayout(seat_input_layout)
        
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
        seat_layout.addWidget(self.seat_placeholder)
        
        layout.addWidget(seat_group)
        
        return widget
    
    def _create_right_area(self) -> QWidget:
        """创建右栏区域：取票码区 + 订单详情区"""
        from ui.widgets.classic_components import ClassicGroupBox, ClassicLabel, ClassicTextEdit, ClassicButton
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 取票码区 (上部45%)
        qr_group = ClassicGroupBox("取票码区")
        qr_layout = QVBoxLayout(qr_group)
        qr_layout.setContentsMargins(10, 20, 10, 10)
        
        self.qr_display = ClassicLabel("(二维码/取票码展示区)", "default")
        self.qr_display.setAlignment(Qt.AlignCenter)
        self.qr_display.setStyleSheet("""
            QLabel {
                color: #666666;
                font: 12px "Microsoft YaHei";
                background-color: #f0f0f0;
                border: 1px solid #dddddd;
                padding: 20px;
                border-radius: 5px;
            }
        """)
        qr_layout.addWidget(self.qr_display)
        
        layout.addWidget(qr_group, 45)
        
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
        
        # 订单详情文本框
        self.order_detail_text = ClassicTextEdit(read_only=True)
        self.order_detail_text.setPlaceholderText("订单详情将在此显示...")
        self.order_detail_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Microsoft YaHei";
                background-color: #f5f5f5;
                border: 1px solid #cccccc;
                border-radius: 3px;
                padding: 4px;
            }
        """)
        order_layout.addWidget(self.order_detail_text)
        
        # 倒计时标签
        self.countdown_label = ClassicLabel("", "info")
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #0077ff;
                font: bold 10px "Microsoft YaHei";
                padding: 2px 4px;
                background-color: transparent;
            }
        """)
        order_layout.addWidget(self.countdown_label)
        
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
        
        layout.addWidget(order_group, 55)
        
        return widget
    
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
    
    def _start_auth_check(self):
        """启动用户认证检查"""
        try:
            # 创建登录窗口
            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_user_login_success)
            
            # 显示登录窗口
            self.login_window.show()
            
            print("[主窗口] 启动用户认证检查")
            
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
            
            print(f"[主窗口] 用户登录成功: {phone}")
            
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
            
            # 显示成功消息
            phone = self.current_user.get('username', self.current_user.get('phone', ''))
            QTimer.singleShot(300, lambda: QMessageBox.information(
                self, 
                "登录成功", 
                f"登录验证成功，欢迎使用柴犬影院模块化系统\n用户: {phone}"
            ))
            
            print(f"[主窗口] 用户登录成功，主窗口已显示")
            
        except Exception as e:
            QMessageBox.critical(self, "显示主窗口错误", f"显示主窗口失败: {str(e)}")
            # 如果显示失败，重新启动登录
            self._restart_login()
    
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
            print(f"[主窗口] 居中窗口失败: {e}")
    
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
            print(f"[主窗口] 账号选择处理错误: {e}")
    
    def _on_account_login_requested(self, login_data: dict):
        """账号登录请求处理"""
        QMessageBox.information(self, "登录请求", "影院账号登录功能已简化，请直接从账号列表中选择账号")
    
    def _on_cinema_selected(self, cinema_name: str):
        """影院选择处理 - 对接到核心业务方法"""
        try:
            print(f"[主窗口] 影院选择: {cinema_name}")
            
            # 更新座位图占位符
            self.seat_placeholder.setText(
                f"已选择影院: {cinema_name}\n\n"
                f"请继续选择影片、日期和场次\n"
                f"然后在上方输入框中输入座位号"
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
            print(f"[主窗口] 影院选择处理错误: {e}")
    
    def _on_order_submitted(self, order_data: dict):
        """订单提交处理 - 对接到核心业务方法"""
        try:
            order_id = order_data.get("order_id", "")
            cinema = order_data.get("cinema", "")
            movie = order_data.get("movie", "")
            print(f"[主窗口] 接收到订单提交: {order_id}")
            
            # 获取座位信息
            seats_text = self.seat_input.text().strip()
            if seats_text:
                selected_seats = [seat.strip() for seat in seats_text.split(',') if seat.strip()]
                # 调用核心业务方法处理订单提交
                self.on_submit_order(selected_seats)
            else:
                MessageManager.show_warning(self, "座位未选择", "请先选择座位")
            
        except Exception as e:
            print(f"[主窗口] 订单提交处理错误: {e}")
    
    def _on_coupon_bound(self, bind_data: dict):
        """券绑定处理 - 对接到核心业务方法"""
        try:
            # 调用核心绑定券方法
            self.on_bind_coupons()
            
        except Exception as e:
            print(f"[主窗口] 券绑定处理错误: {e}")
    
    def _on_coupon_exchanged(self, exchange_data: dict):
        """券兑换处理"""
        coupon_type = exchange_data.get("type", "")
        quantity = exchange_data.get("quantity", 0)
        print(f"[主窗口] 券兑换完成: {quantity}个{coupon_type}")
    
    def _on_seat_input_changed(self, text: str):
        """座位输入变化处理"""
        try:
            # 解析座位输入
            seats = [seat.strip() for seat in text.split(',') if seat.strip()]
            
            if seats:
                # 更新座位显示
                self._update_seat_selection(seats)
                
                # 发出座位选择信号
                self._on_seat_selected(','.join(seats))
            
        except Exception as e:
            print(f"[主窗口] 座位输入处理错误: {e}")
    
    def _on_pay_button_clicked(self):
        """支付按钮点击处理 - 对接到核心业务方法"""
        try:
            # 调用核心一键支付方法
            self.on_one_click_pay()
            
        except Exception as e:
            print(f"[主窗口] 支付按钮处理错误: {e}")
    
    def _on_seat_selected(self, seats: str):
        """座位选择处理"""
        print(f"[主窗口] 座位选择: {seats}")
    
    def _on_main_login_success(self, user_info: dict):
        """主窗口登录成功处理 - 触发账号列表刷新"""
        try:
            print(f"[主窗口] 处理登录成功事件")
            
            # 刷新账号列表
            self.refresh_account_list()
            
        except Exception as e:
            print(f"[主窗口] 登录成功处理错误: {e}")
    
    # ===== 全局事件处理方法 =====
    
    def _on_global_login_success(self, user_info: dict):
        """全局登录成功处理"""
        print(f"[主窗口] 收到全局登录成功事件")
    
    def _on_global_account_changed(self, account_data: dict):
        """全局账号切换处理"""
        try:
            userid = account_data.get('userid', 'N/A')
            phone = account_data.get('phone', '')
            print(f"[主窗口] 收到全局账号切换事件: {userid}")
            
            # 同步更新右栏显示
            if phone:
                self.phone_display.setText(f"当前账号: {phone}")
            else:
                self.phone_display.setText(f"当前账号: {userid}")
                
        except Exception as e:
            print(f"[主窗口] 全局账号切换处理错误: {e}")
    
    def _on_global_cinema_selected(self, cinema_name: str):
        """全局影院选择处理"""
        print(f"[主窗口] 收到全局影院选择事件: {cinema_name}")
    
    def _on_global_order_created(self, order_data: dict):
        """全局订单创建处理"""
        try:
            order_id = order_data.get('order_id', 'N/A')
            print(f"[主窗口] 收到全局订单创建事件: {order_id}")
            
            # 更新右栏订单详情显示
            self._update_order_details(order_data)
            
            # 更新取票码区域
            self.qr_display.setText(f"订单号: {order_id}\n\n取票码将在支付完成后显示")
            
        except Exception as e:
            print(f"[主窗口] 全局订单创建处理错误: {e}")
    
    def _on_global_order_paid(self, order_id: str):
        """全局订单支付处理"""
        try:
            print(f"[主窗口] 收到全局订单支付事件: {order_id}")
            
            # 更新取票码显示
            self.qr_display.setText(f"支付成功！\n\n订单号: {order_id}\n取票码: TK{order_id[-6:]}")
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
            
            # 更新倒计时显示
            self.countdown_label.setText("支付完成")
            self.countdown_label.setStyleSheet("""
                QLabel {
                    color: #2e7d32;
                    font: bold 10px "Microsoft YaHei";
                    padding: 2px 4px;
                    background-color: transparent;
                }
            """)
            
        except Exception as e:
            print(f"[主窗口] 全局订单支付处理错误: {e}")
    
    def _update_seat_selection(self, seats: list):
        """更新座位选择显示"""
        try:
            if seats:
                seat_info = f"已选择座位: {', '.join(seats)}\n\n"
                seat_info += f"座位数量: {len(seats)} 个\n"
                seat_info += f"预计价格: ¥{len(seats) * 35.0:.2f}"
                
                self.seat_placeholder.setText(seat_info)
                self.seat_placeholder.setStyleSheet("""
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
                self.seat_placeholder.setText("座位图将在此显示\n\n请先选择影院、影片、日期和场次")
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
                
        except Exception as e:
            print(f"[主窗口] 更新座位选择错误: {e}")
    
    def _update_order_details(self, order_data: dict):
        """更新订单详情显示"""
        try:
            # 更新手机号显示
            phone = order_data.get('phone', '')
            if phone:
                self.phone_display.setText(f"手机号: {phone}")
            
            # 更新订单详情
            details = f"订单信息:\n"
            details += f"影院: {order_data.get('cinema', '未选择')}\n"
            details += f"影片: {order_data.get('movie', '未选择')}\n"
            details += f"场次: {order_data.get('session', '未选择')}\n"
            details += f"座位: {order_data.get('seats', '未选择')}\n"
            details += f"金额: ¥{order_data.get('amount', 0):.2f}\n"
            details += f"状态: {order_data.get('status', '待支付')}"
            
            self.order_detail_text.setPlainText(details)
            
            # 更新倒计时（可选）
            if order_data.get('status') == '待支付':
                self.countdown_label.setText("支付倒计时: 15:00")
            else:
                self.countdown_label.setText("")
                
        except Exception as e:
            print(f"[主窗口] 更新订单详情错误: {e}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 清理资源
            self.account_widget.cleanup()
            self.tab_manager_widget.cleanup()
            # 座位区域和右栏区域是直接创建的QWidget，不需要特殊清理
            
            print("[主窗口] 资源清理完成")
            
            event.accept()
            
        except Exception as e:
            print(f"[主窗口] 关闭清理错误: {e}")
            event.accept()

    # ===== 第三步：核心业务方法（从源项目复制） =====
    
    def set_current_account(self, account):
        """设置当前账号"""
        try:
            self.current_account = account
            if account:
                userid = account.get('userid', 'N/A')
                phone = account.get('phone', '')
                print(f"[主窗口] 设置当前账号: {userid}")
                
                # 更新UI显示
                if phone:
                    self.phone_display.setText(f"当前账号: {phone}")
                else:
                    self.phone_display.setText(f"当前账号: {userid}")
                
                # 发布全局账号切换事件
                event_bus.account_changed.emit(account)
                
                # 刷新券列表等
                self._refresh_account_dependent_data()
                
        except Exception as e:
            print(f"[主窗口] 设置账号错误: {e}")
    
    def set_main_account(self, account):
        """设置主账号标记"""
        try:
            if account:
                account['is_main'] = True
                print(f"[主窗口] 设置主账号: {account.get('userid', 'N/A')}")
                
                # 保存到数据文件
                self._save_account_data(account)
                
        except Exception as e:
            print(f"[主窗口] 设置主账号错误: {e}")
    
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
            print(f"[主窗口] 刷新账号列表错误: {e}")
            MessageManager.show_error(self, "刷新失败", f"刷新账号列表失败: {str(e)}")
    
    def on_cinema_changed(self):
        """影院切换事件处理"""
        try:
            cinema_name = self.tab_manager_widget.cinema_combo.currentText()
            if not cinema_name or cinema_name in ["加载中...", "请选择影院"]:
                return
                
            print(f"[主窗口] 影院切换: {cinema_name}")
            
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
            print(f"[主窗口] 影院切换错误: {e}")
    
    def on_submit_order(self, selected_seats):
        """提交订单处理"""
        try:
            if not self.current_account:
                MessageManager.show_error(self, "提交失败", "请先选择账号")
                return
                
            # 获取当前选择的影院和场次信息
            cinema_name = self.tab_manager_widget.cinema_combo.currentText()
            movie_name = self.tab_manager_widget.movie_combo.currentText()
            date = self.tab_manager_widget.date_combo.currentText()
            session = self.tab_manager_widget.session_combo.currentText()
            
            # 验证选择完整性
            if not all([cinema_name, movie_name, date, session]):
                MessageManager.show_error(self, "信息不完整", "请完整选择影院、影片、日期和场次")
                return
                
            if not selected_seats:
                MessageManager.show_error(self, "座位未选择", "请选择座位")
                return
            
            # 获取影院信息
            cinema_info = self._get_cinema_info_by_name(cinema_name)
            if not cinema_info:
                MessageManager.show_error(self, "影院信息错误", "无法获取影院信息")
                return
                
            # 创建订单
            result = self._create_order(self.current_account, cinema_info['cinemaid'], selected_seats)
            if result:
                self.current_order = result
                self._show_order_detail(result)
                MessageManager.show_info(self, "订单创建成功", "订单已创建，请选择优惠券并支付")
                
        except Exception as e:
            print(f"[主窗口] 提交订单错误: {e}")
            MessageManager.show_error(self, "提交失败", f"提交订单失败: {str(e)}")
    
    def update_coupons(self, coupon_result, ticketcount=1):
        """更新券列表"""
        try:
            self.coupons_data = []
            if not coupon_result or coupon_result.get('resultCode') != '0':
                print("[主窗口] 券列表为空或获取失败")
                return
                
            data = coupon_result.get('data', {})
            coupons = data.get('coupons', [])
            
            self.coupons_data = coupons
            
            # 更新UI中的券列表显示
            if hasattr(self.tab_manager_widget, 'coupon_list'):
                self.tab_manager_widget.coupon_list.clear()
                for coupon in coupons:
                    name = coupon.get('couponName', '未知券')
                    valid_date = coupon.get('validEndDate', '')
                    item_text = f"{name} (有效期至{valid_date})"
                    self.tab_manager_widget.coupon_list.addItem(item_text)
                    
            print(f"[主窗口] 券列表已更新，共{len(coupons)}张券")
            
        except Exception as e:
            print(f"[主窗口] 更新券列表错误: {e}")
    
    def on_coupon_select(self, event=None):
        """券选择事件处理"""
        try:
            if not hasattr(self.tab_manager_widget, 'coupon_list'):
                return
                
            selected_items = self.tab_manager_widget.coupon_list.selectedItems()
            if not selected_items:
                return
                
            selected_index = self.tab_manager_widget.coupon_list.row(selected_items[0])
            if 0 <= selected_index < len(self.coupons_data):
                selected_coupon = self.coupons_data[selected_index]
                
                # 处理券选择逻辑
                if selected_coupon not in self.selected_coupons:
                    if len(self.selected_coupons) < self.max_coupon_select:
                        self.selected_coupons.append(selected_coupon)
                        print(f"[主窗口] 选择券: {selected_coupon.get('couponName', '未知券')}")
                    else:
                        MessageManager.show_warning(self, "选择限制", f"最多只能选择{self.max_coupon_select}张券")
                else:
                    self.selected_coupons.remove(selected_coupon)
                    print(f"[主窗口] 取消选择券: {selected_coupon.get('couponName', '未知券')}")
                    
        except Exception as e:
            print(f"[主窗口] 券选择错误: {e}")
    
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
            
            MessageManager.show_info(self, "绑定完成", f"券绑定完成\n成功：{success_count} 个\n失败：{fail_count} 个")
            
        except Exception as e:
            print(f"[主窗口] 绑定券错误: {e}")
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
                
            print(f"[主窗口] 订单列表已刷新")
            
        except Exception as e:
            print(f"[主窗口] 刷新订单列表错误: {e}")
    
    def on_one_click_pay(self):
        """一键支付处理"""
        try:
            if not self.current_order:
                MessageManager.show_error(self, "支付失败", "没有待支付的订单")
                return
                
            # 获取订单详情
            order_detail = get_order_detail({
                'order_id': self.current_order.get('order_id')
            })
            
            if not order_detail or order_detail.get('resultCode') != '0':
                MessageManager.show_error(self, "支付失败", "无法获取订单详情")
                return
            
            # 调用支付API
            pay_result = pay_order({
                'account': self.current_account,
                'order': self.current_order,
                'coupons': self.selected_coupons
            })
            
            if pay_result and pay_result.get('resultCode') == '0':
                # 支付成功
                MessageManager.show_info(self, "支付成功", "订单支付成功！")
                
                # 获取取票码
                qr_result = get_order_qrcode_api({
                    'order_id': self.current_order.get('order_id')
                })
                
                if qr_result and qr_result.get('resultCode') == '0':
                    qr_code = qr_result.get('data', {}).get('qrcode', '')
                    self._show_qr_code(qr_code)
                
                # 发布支付成功事件
                event_bus.order_paid.emit(self.current_order.get('order_id', ''))
                
                # 清空当前订单
                self.current_order = None
                self.selected_coupons.clear()
                
            else:
                error_msg = pay_result.get('resultDesc', '支付失败') if pay_result else '网络错误'
                MessageManager.show_error(self, "支付失败", error_msg)
                
        except Exception as e:
            print(f"[主窗口] 支付错误: {e}")
            MessageManager.show_error(self, "支付失败", f"支付处理失败: {str(e)}")
    
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
                print(f"[主窗口] 已取消未支付订单")
            else:
                print(f"[主窗口] 取消订单失败: {result.get('resultDesc', '未知错误') if result else '网络错误'}")
                
        except Exception as e:
            print(f"[主窗口] 取消订单错误: {e}")
    
    def _get_member_info(self, account, cinemaid):
        """获取会员信息"""
        try:
            member_info = self.member_service.get_member_info(account, cinemaid)
            if member_info:
                self.member_info = member_info
                print(f"[主窗口] 获取会员信息成功")
            else:
                print(f"[主窗口] 获取会员信息失败")
                
        except Exception as e:
            print(f"[主窗口] 获取会员信息错误: {e}")
    
    def _create_order(self, account, cinemaid, selected_seats):
        """创建订单"""
        try:
            # 构建订单参数
            order_params = {
                'account': account,
                'cinemaid': cinemaid,
                'seats': selected_seats,
                'movie': self.tab_manager_widget.movie_combo.currentText(),
                'date': self.tab_manager_widget.date_combo.currentText(),
                'session': self.tab_manager_widget.session_combo.currentText()
            }
            
            # 调用创建订单API
            result = create_order(order_params)
            
            if result and result.get('resultCode') == '0':
                print(f"[主窗口] 订单创建成功")
                return result.get('data')
            else:
                error_msg = result.get('resultDesc', '订单创建失败') if result else '网络错误'
                MessageManager.show_error(self, "创建失败", error_msg)
                return None
                
        except Exception as e:
            print(f"[主窗口] 创建订单错误: {e}")
            MessageManager.show_error(self, "创建失败", f"创建订单失败: {str(e)}")
            return None
    
    def cinema_account_login_api(self, phone, openid, token, cinemaid):
        """影院账号登录API"""
        try:
            # 调用影院登录API
            login_result = self.auth_service.cinema_login(phone, openid, token, cinemaid)
            
            if login_result and login_result.get('resultCode') == '0':
                print(f"[主窗口] 影院账号登录成功")
                return login_result
            else:
                error_msg = login_result.get('resultDesc', '登录失败') if login_result else '网络错误'
                print(f"[主窗口] 影院账号登录失败: {error_msg}")
                return None
                
        except Exception as e:
            print(f"[主窗口] 影院登录错误: {e}")
            return None
    
    # ===== 辅助方法 =====
    
    def _refresh_account_dependent_data(self):
        """刷新依赖账号的数据"""
        try:
            # 刷新券列表
            if self.current_account and self.current_order:
                coupon_result = get_coupons_by_order({
                    'account': self.current_account,
                    'order': self.current_order
                })
                self.update_coupons(coupon_result)
                
        except Exception as e:
            print(f"[主窗口] 刷新账号相关数据错误: {e}")
    
    def _save_account_data(self, account):
        """保存账号数据"""
        try:
            save_account(account)
            print(f"[主窗口] 账号数据已保存")
            
        except Exception as e:
            print(f"[主窗口] 保存账号数据错误: {e}")
    
    def _get_cinema_info_by_name(self, cinema_name):
        """根据名称获取影院信息"""
        try:
            cinemas = self.cinema_manager.get_cinema_list()
            for cinema in cinemas:
                if cinema.get('cinemaShortName') == cinema_name or cinema.get('name') == cinema_name:
                    return cinema
            return None
            
        except Exception as e:
            print(f"[主窗口] 获取影院信息错误: {e}")
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
                        print(f"[主窗口] 没有获取到电影数据")
                else:
                    print(f"[主窗口] 影院信息不完整，无法加载电影")
            else:
                print(f"[主窗口] 没有当前账号，无法加载电影")
                    
        except Exception as e:
            print(f"[主窗口] 加载电影列表错误: {e}")
            # 如果API调用失败，使用默认电影列表
            if hasattr(self.tab_manager_widget, 'movie_combo'):
                self.tab_manager_widget.movie_combo.clear()
                self.tab_manager_widget.movie_combo.addItems([
                    "阿凡达：水之道",
                    "流浪地球2",
                    "满江红"
                ])
    
    def _show_order_detail(self, order_detail):
        """显示订单详情"""
        try:
            if not order_detail:
                return
                
            # 更新右栏订单详情显示
            details = f"订单信息:\n"
            details += f"订单号: {order_detail.get('order_id', 'N/A')}\n"
            details += f"影院: {order_detail.get('cinema', 'N/A')}\n"
            details += f"影片: {order_detail.get('movie', 'N/A')}\n"
            details += f"场次: {order_detail.get('session', 'N/A')}\n"
            details += f"座位: {order_detail.get('seats', 'N/A')}\n"
            details += f"金额: ¥{order_detail.get('amount', 0):.2f}\n"
            details += f"状态: {order_detail.get('status', '未知')}"
            
            self.order_detail_text.setPlainText(details)
            
            # 启动倒计时
            if order_detail.get('status') == '待支付':
                self.start_countdown(900)  # 15分钟倒计时
            else:
                self.stop_countdown()
            
        except Exception as e:
            print(f"[主窗口] 显示订单详情错误: {e}")
    
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
            print(f"[主窗口] 显示取票码错误: {e}")
    
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
            print(f"[主窗口] 更新订单表格错误: {e}")

    # ===== 定时器相关方法（PyQt5替换tkinter.after） =====
    
    def start_countdown(self, seconds=900):
        """启动倒计时（默认15分钟）"""
        try:
            self.countdown_seconds = seconds
            
            if not self.countdown_timer:
                self.countdown_timer = QTimer()
                self.countdown_timer.timeout.connect(self.update_countdown)
            
            self.countdown_timer.start(1000)  # 每秒更新一次
            self.update_countdown()
            
        except Exception as e:
            print(f"[主窗口] 启动倒计时错误: {e}")
    
    def update_countdown(self):
        """更新倒计时显示"""
        try:
            if self.countdown_seconds <= 0:
                # 倒计时结束
                self.countdown_label.setText("时间已到")
                self.countdown_label.setStyleSheet("""
                    QLabel {
                        color: #f44336;
                        font: bold 10px "Microsoft YaHei";
                        padding: 2px 4px;
                        background-color: transparent;
                    }
                """)
                
                if self.countdown_timer:
                    self.countdown_timer.stop()
                
                # 处理超时逻辑
                self._handle_countdown_timeout()
                return
            
            # 计算分钟和秒
            minutes = self.countdown_seconds // 60
            seconds = self.countdown_seconds % 60
            
            # 更新显示
            self.countdown_label.setText(f"支付倒计时: {minutes:02d}:{seconds:02d}")
            
            # 减少1秒
            self.countdown_seconds -= 1
            
        except Exception as e:
            print(f"[主窗口] 更新倒计时错误: {e}")
    
    def stop_countdown(self):
        """停止倒计时"""
        try:
            if self.countdown_timer:
                self.countdown_timer.stop()
            
            self.countdown_label.setText("")
            
        except Exception as e:
            print(f"[主窗口] 停止倒计时错误: {e}")
    
    def _handle_countdown_timeout(self):
        """处理倒计时超时"""
        try:
            if self.current_order:
                # 取消当前订单
                QMessageBox.warning(self, "订单超时", "支付时间已到，订单将被取消")
                
                # 清空当前订单
                self.current_order = None
                self.selected_coupons.clear()
                
                # 清空订单详情
                self.order_detail_text.clear()
                self.qr_display.setText("(二维码/取票码展示区)")
                
        except Exception as e:
            print(f"[主窗口] 处理倒计时超时错误: {e}")


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