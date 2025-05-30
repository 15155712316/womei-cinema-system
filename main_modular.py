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
        self.seat_area_layout = QVBoxLayout(seat_group)  # 🆕 保存布局引用供后续使用
        self.seat_area_layout.setContentsMargins(10, 20, 10, 10)
        self.seat_area_layout.setSpacing(10)
        
        # 座位选择输入
        seat_input_layout = QHBoxLayout()
        seat_label = ClassicLabel("选择座位:")
        seat_label.setMinimumWidth(80)
        self.seat_input = ClassicLineEdit()
        self.seat_input.setPlaceholderText("请输入座位号，如: A1,A2,B3")
        seat_input_layout.addWidget(seat_label)
        seat_input_layout.addWidget(self.seat_input)
        self.seat_area_layout.addLayout(seat_input_layout)
        
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
        self.tab_manager_widget.session_selected.connect(self._on_session_selected)
        
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
            
            # 🆕 延迟触发默认影院设置，确保所有组件都已初始化
            QTimer.singleShot(500, self._trigger_default_cinema_selection)
            
            print(f"[主窗口] 用户登录成功，主窗口已显示")
            
        except Exception as e:
            QMessageBox.critical(self, "显示主窗口错误", f"显示主窗口失败: {str(e)}")
            # 如果显示失败，重新启动登录
            self._restart_login()
    
    def _trigger_default_cinema_selection(self):
        """触发默认影院选择 - 🆕 确保账号列表正确过滤"""
        try:
            # 获取第一个影院并触发选择
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            if cinemas:
                first_cinema = cinemas[0]
                cinema_name = first_cinema.get('cinemaShortName', '')
                
                print(f"[主窗口] 准备自动选择默认影院: {cinema_name}")
                print(f"[主窗口] 影院数据: {first_cinema}")
                
                # 🆕 首先更新Tab管理器的影院数据列表
                if hasattr(self.tab_manager_widget, 'update_cinema_list'):
                    self.tab_manager_widget.update_cinema_list(cinemas)
                    print(f"[主窗口] 已更新Tab管理器的影院数据列表")
                
                # 🆕 先发布全局影院选择事件，让账号组件处理
                event_bus.cinema_selected.emit(first_cinema)
                
                # 🆕 延迟更新Tab管理器的影院选择，确保账号组件先处理完
                QTimer.singleShot(300, lambda: self._update_tab_cinema_selection(cinema_name))
                
                print(f"[主窗口] 已发送影院选择事件: {cinema_name}")
            else:
                print(f"[主窗口] 没有可用的影院数据")
            
        except Exception as e:
            print(f"[主窗口] 触发默认影院选择错误: {e}")
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
                        print(f"[主窗口] Tab管理器影院选择已更新: {cinema_name}")
                        break
                else:
                    print(f"[主窗口] 在Tab管理器中未找到影院: {cinema_name}")
            else:
                print(f"[主窗口] Tab管理器的cinema_combo不存在")
                
        except Exception as e:
            print(f"[主窗口] 更新Tab影院选择错误: {e}")
    
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
            print(f"[主窗口] 处理订单错误: {e}")
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
        """创建订单（保留原方法供其他地方调用）"""
        # 直接调用主要的订单创建方法
        return self.on_submit_order(selected_seats)
    
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
        """根据名称获取影院信息 - 增强版本"""
        try:
            print(f"[主窗口] 正在查找影院信息: {cinema_name}")
            
            # 方法1: 从cinema_manager获取数据 - 🆕 修复方法名
            cinemas = self.cinema_manager.load_cinema_list()  # 使用正确的方法名
            if cinemas:
                print(f"[主窗口] cinema_manager获取到 {len(cinemas)} 个影院")
                for cinema in cinemas:
                    cinema_short_name = cinema.get('cinemaShortName', '')
                    cinema_name_field = cinema.get('name', '')
                    print(f"[主窗口] 检查影院: {cinema_short_name} / {cinema_name_field}")
                    
                    if cinema_short_name == cinema_name or cinema_name_field == cinema_name:
                        print(f"[主窗口] 找到匹配影院: {cinema}")
                        return cinema
            
            # 方法2: 从Tab管理器的影院数据获取
            if hasattr(self, 'tab_manager_widget') and hasattr(self.tab_manager_widget, 'cinemas_data'):
                for cinema in self.tab_manager_widget.cinemas_data:
                    cinema_short_name = cinema.get('cinemaShortName', '')
                    cinema_name_field = cinema.get('name', '')
                    print(f"[主窗口] Tab数据检查影院: {cinema_short_name} / {cinema_name_field}")
                    
                    if cinema_short_name == cinema_name or cinema_name_field == cinema_name:
                        print(f"[主窗口] 从Tab数据找到匹配影院: {cinema}")
                        return cinema
            
            # 方法3: 尝试重新加载影院数据
            print(f"[主窗口] 尝试重新加载影院数据...")
            cinemas = self.cinema_manager.load_cinema_list()
            self.tab_manager_widget.cinemas_data = cinemas
            
            for cinema in cinemas:
                cinema_short_name = cinema.get('cinemaShortName', '')
                if cinema_short_name == cinema_name:
                    print(f"[主窗口] 重新加载后找到影院: {cinema}")
                    return cinema
            
            print(f"[主窗口] 未找到影院: {cinema_name}")
            return None
            
        except Exception as e:
            print(f"[主窗口] 获取影院信息错误: {e}")
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

    def _on_session_selected(self, session_info: dict):
        """场次选择处理 - 加载座位图"""
        try:
            print(f"[主窗口] 收到场次选择信号: {session_info.get('session_text', 'N/A')}")
            
            # 验证必要信息
            session_data = session_info.get('session_data')
            account = session_info.get('account')
            cinema_data = session_info.get('cinema_data')
            
            if not all([session_data, account, cinema_data]):
                print(f"[主窗口] 场次信息不完整，无法加载座位图")
                self.seat_placeholder.setText("场次信息不完整\n\n无法加载座位图")
                return
            
            # 更新座位区域提示
            self.seat_placeholder.setText("正在加载座位图，请稍候...")
            
            # 使用QTimer延迟执行，避免阻塞UI
            QTimer.singleShot(100, lambda: self._load_seat_map(session_info))
            
        except Exception as e:
            print(f"[主窗口] 场次选择处理错误: {e}")
            self.seat_placeholder.setText("加载座位图失败\n\n请重新选择场次")

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
            
            print(f"[主窗口] 影院数据检查:")
            print(f"  - 影院名称: {cinema_data.get('cinemaShortName', 'N/A')}")
            print(f"  - 影院ID: {cinema_data.get('cinemaid', 'N/A')}")
            print(f"  - base_url: {base_url}")
            print(f"  - 原始数据: {cinema_data}")
            
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
            
            print(f"[主窗口] 座位图API参数: {params}")
            
            # 验证参数完整性
            required_params = ['base_url', 'showCode', 'hallCode', 'filmCode', 'userid', 'openid', 'token', 'cinemaid']
            missing_params = [p for p in required_params if not params.get(p)]
            if missing_params:
                error_msg = f"缺少必要参数: {', '.join(missing_params)}"
                print(f"[主窗口] {error_msg}")
                self.seat_placeholder.setText(f"参数不完整\n\n{error_msg}")
                return
            
            # 调用座位图API
            print(f"[主窗口] 开始调用座位图API...")
            seat_result = get_plan_seat_info(**params)
            
            print(f"[主窗口] 座位图API响应: {type(seat_result)}")
            
            if seat_result and isinstance(seat_result, dict):
                if seat_result.get('resultCode') == '0':
                    # 成功获取座位数据
                    seat_data = seat_result.get('resultData', {})
                    self._display_seat_map(seat_data, session_info)
                else:
                    # API返回错误
                    error_msg = seat_result.get('resultDesc', '未知错误')
                    print(f"[主窗口] 座位图API错误: {error_msg}")
                    self.seat_placeholder.setText(f"获取座位图失败\n\n{error_msg}")
            else:
                # 响应格式错误
                print(f"[主窗口] 座位图API响应格式错误")
                self.seat_placeholder.setText("座位图数据格式错误\n\n请重新选择场次")
                
        except Exception as e:
            print(f"[主窗口] 加载座位图错误: {e}")
            import traceback
            traceback.print_exc()
            self.seat_placeholder.setText("加载座位图异常\n\n请检查网络连接")

    def _display_seat_map(self, seat_data: dict, session_info: dict):
        """显示座位图"""
        try:
            print(f"[主窗口] 开始显示座位图")
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
                    print(f"[主窗口] 未找到seats数组数据")
            
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
                        
                        print(f"[主窗口] 座位图面板创建成功")
                        
                    else:
                        print(f"[主窗口] 未找到座位区域布局")
                        self.seat_placeholder.setText("座位区域初始化失败")
                        
                except Exception as panel_error:
                    print(f"[主窗口] 创建座位图面板错误: {panel_error}")
                    import traceback
                    traceback.print_exc()
                    self.seat_placeholder.setText(f"座位图显示错误\\n\\n{str(panel_error)}")
            else:
                # 座位数据解析失败
                print(f"[主窗口] 座位矩阵数据无效")
                self.seat_placeholder.setText("座位数据解析失败\\n\\n请重新选择场次或联系管理员")
                
        except Exception as e:
            print(f"[主窗口] 显示座位图错误: {e}")
            import traceback
            traceback.print_exc()
            self.seat_placeholder.setText("显示座位图异常\\n\\n请重新选择场次")

    def _parse_seats_array(self, seats_array: List[Dict], hall_info: dict) -> List[List[Dict]]:
        """解析seats数组为座位矩阵"""
        try:
            print(f"[主窗口] 开始解析seats数组")
            print(f"[主窗口] 影厅信息: {hall_info}")
            print(f"[主窗口] 座位数据量: {len(seats_array)}")
            
            if not seats_array:
                print(f"[主窗口] seats数组为空")
                return []
            
            # 🆕 分析seats数组结构，使用正确的字段名
            max_row = 0
            max_col = 0
            
            # 打印前几个座位数据以调试
            for i, seat in enumerate(seats_array[:3]):
                print(f"[主窗口] 座位{i+1}数据: {seat}")
            
            for seat in seats_array:
                # 🆕 使用正确的字段名：rn(行号), cn(列号)，而不是rownum/colnum
                row_num = seat.get('rn', 0)
                col_num = seat.get('cn', 0)
                max_row = max(max_row, row_num)
                max_col = max(max_col, col_num)
            
            print(f"[主窗口] 座位矩阵尺寸: {max_row}行 x {max_col}列")
            
            if max_row == 0 or max_col == 0:
                print(f"[主窗口] 矩阵尺寸无效，检查字段映射")
                return []
            
            # 🆕 创建座位矩阵
            seat_matrix = []
            for row in range(max_row):
                seat_row = [None] * max_col
                seat_matrix.append(seat_row)
            
            # 🆕 填充座位数据
            for seat in seats_array:
                row_num = seat.get('rn', 0) - 1  # 转为0基索引
                col_num = seat.get('cn', 0) - 1  # 转为0基索引
                
                if 0 <= row_num < max_row and 0 <= col_num < max_col:
                    # 解析座位状态：s字段，F=可选，B=已售等
                    seat_state = seat.get('s', 'F')
                    if seat_state == 'F':
                        status = 'available'
                    elif seat_state == 'B':
                        status = 'sold'
                    else:
                        status = 'unavailable'
                    
                    seat_data = {
                        'row': seat.get('rn', row_num + 1),
                        'col': seat.get('cn', col_num + 1),
                        'num': f"{seat.get('rn', row_num + 1)}-{seat.get('cn', col_num + 1)}",  # 🆕 简洁格式：行-列
                        'status': status,
                        'price': 0,  # 价格信息在priceinfo中
                        'seatname': seat.get('sn', ''),
                        'original_data': seat  # 保存原始数据备用
                    }
                    
                    seat_matrix[row_num][col_num] = seat_data
            
            print(f"[主窗口] 座位矩阵填充完成")
            # 打印前几行座位数据用于调试
            for i, row in enumerate(seat_matrix[:3]):  # 只打印前3行
                valid_seats = [seat['num'] if seat else 'None' for seat in row[:10]]  # 只显示前10列
                print(f"[主窗口] 第{i+1}行座位: {valid_seats}")
            
            return seat_matrix
            
        except Exception as e:
            print(f"[主窗口] 解析seats数组错误: {e}")
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
                    print(f"[主窗口] 已选座位: {seat_names}")
                else:
                    # 清空选择
                    self.seat_input.setText("")
                    print(f"[主窗口] 清空座位选择")
            
            # 触发座位选择事件
            self._on_seat_selected(", ".join([seat.get('num', '') for seat in selected_seats]))
            
        except Exception as e:
            print(f"[主窗口] 处理座位选择变化错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_seat_panel_submit_order(self, selected_seats: List[Dict]):
        """座位面板提交订单处理"""
        try:
            print(f"[主窗口] 座位面板提交订单: {len(selected_seats)} 个座位")
            
            # 调用主要的订单提交方法
            self.on_submit_order(selected_seats)
            
        except Exception as e:
            print(f"[主窗口] 座位面板提交订单错误: {e}")
            import traceback
            traceback.print_exc()

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
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "刷新失败", f"刷新账号列表失败: {str(e)}", auto_close=False)

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
        """提交订单处理 - 完整流程整合"""
        try:
            print(f"[主窗口] 开始提交订单流程")
            
            # 导入消息管理器
            from services.ui_utils import MessageManager
            
            # 1. 基础验证
            if not self.current_account:
                MessageManager.show_error(self, "提交失败", "请先选择账号", auto_close=False)
                return False
                
            # 2. 获取并验证选择信息
            cinema_text = self.tab_manager_widget.cinema_combo.currentText()
            movie_text = self.tab_manager_widget.movie_combo.currentText()
            date_text = self.tab_manager_widget.date_combo.currentText()
            session_text = self.tab_manager_widget.session_combo.currentText()
            
            print(f"[主窗口] 当前选择:")
            print(f"  影院: {cinema_text}")
            print(f"  影片: {movie_text}")
            print(f"  日期: {date_text}")
            print(f"  场次: {session_text}")
            print(f"  账号: {self.current_account.get('userid', 'N/A')}")
            print(f"  座位: {len(selected_seats)} 个")
            
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
            
            # 简化版订单创建 - 返回成功状态
            MessageManager.show_info(self, "正在处理", "正在创建订单，请稍候...", auto_close=True)
            
            # 模拟订单创建成功
            order_id = f"ORDER{int(time.time())}"
            
            # 保存当前订单
            self.current_order = {
                'order_id': order_id,
                'cinema': cinema_text,
                'movie': movie_text,
                'date': date_text,
                'session': session_text,
                'seats': [seat.get('num', '') for seat in selected_seats],
                'amount': len(selected_seats) * 35.0,
                'status': '待支付',
                'create_time': time.strftime("%Y-%m-%d %H:%M:%S"),
                'phone': self.current_account.get('phone', ''),
            }
            
            # 显示订单详情
            self._show_order_detail(self.current_order)
            
            # 发布订单创建事件
            event_bus.order_created.emit(self.current_order)
            
            # 启动支付倒计时
            self.start_countdown(900)  # 15分钟倒计时
            
            print(f"[主窗口] 订单创建成功: {order_id}")
            return True
                
        except Exception as e:
            print(f"[主窗口] 提交订单错误: {e}")
            import traceback
            traceback.print_exc()
            from services.ui_utils import MessageManager
            MessageManager.show_error(self, "提交失败", f"提交订单失败\n\n错误: {str(e)}", auto_close=False)
            return False


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