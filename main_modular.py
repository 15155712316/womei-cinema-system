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

# 导入业务服务
from services.auth_service import AuthService
from services.cinema_manager import CinemaManager

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
        
        # 初始化状态变量
        self.current_user = None
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
        """账号选择处理"""
        try:
            userid = account_data.get('userid', 'N/A')
            phone = account_data.get('phone', '')
            print(f"[主窗口] 账号选择: {userid}")
            
            # 更新右栏的手机号显示
            if phone:
                self.phone_display.setText(f"当前账号: {phone}")
            else:
                self.phone_display.setText(f"当前账号: {userid}")
                
        except Exception as e:
            print(f"[主窗口] 账号选择处理错误: {e}")
    
    def _on_account_login_requested(self, login_data: dict):
        """账号登录请求处理"""
        QMessageBox.information(self, "登录请求", "影院账号登录功能已简化，请直接从账号列表中选择账号")
    
    def _on_cinema_selected(self, cinema_name: str):
        """影院选择处理"""
        try:
            print(f"[主窗口] 影院选择: {cinema_name}")
            
            # 更新座位图占位符
            self.seat_placeholder.setText(
                f"已选择影院: {cinema_name}\n\n"
                f"请继续选择影片、日期和场次\n"
                f"然后在上方输入框中输入座位号"
            )
            
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
        """订单提交处理"""
        try:
            order_id = order_data.get("order_id", "")
            cinema = order_data.get("cinema", "")
            movie = order_data.get("movie", "")
            print(f"[主窗口] 接收到订单提交: {order_id}")
            
            # 直接更新右栏订单详情显示
            self._update_order_details(order_data)
            
            # 更新取票码区域显示订单等待状态
            self.qr_display.setText(f"订单创建中...\n\n订单号: {order_id}\n请选择座位后支付")
            
        except Exception as e:
            print(f"[主窗口] 订单提交处理错误: {e}")
    
    def _on_coupon_bound(self, bind_data: dict):
        """券绑定处理"""
        success_count = bind_data.get("success_count", 0)
        fail_count = bind_data.get("fail_count", 0)
        print(f"[主窗口] 券绑定完成: 成功{success_count}个, 失败{fail_count}个")
    
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
        """支付按钮点击处理"""
        try:
            QMessageBox.information(self, "支付功能", "一键支付功能待实现\n当前为演示版本")
            print("[主窗口] 支付按钮点击")
            
        except Exception as e:
            print(f"[主窗口] 支付按钮处理错误: {e}")
    
    def _on_seat_selected(self, seats: str):
        """座位选择处理"""
        print(f"[主窗口] 座位选择: {seats}")
    
    def _on_main_login_success(self, user_info: dict):
        """主窗口登录成功处理"""
        print(f"[主窗口] 处理登录成功事件")
    
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