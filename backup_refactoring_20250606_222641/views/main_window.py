#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - 重构版本
集成所有控制器和组件，建立完整的MVC架构
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMessageBox, QTextEdit, QLabel, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

# 导入事件总线
from utils.signals import event_bus, event_manager, event_handler

# 导入控制器
from controllers.order_controller import OrderController
from controllers.account_controller import AccountController
from controllers.cinema_controller import CinemaController

# 导入UI组件
from views.components.seat_map_panel import SeatMapPanel
from views.components.account_panel import AccountPanel
from views.components.cinema_panel import CinemaPanel

# 导入登录窗口
from ui.login_window import LoginWindow


class MainWindow(QMainWindow):
    """主窗口 - 重构版本"""
    
    # 信号定义
    login_success = pyqtSignal(dict)  # 登录成功
    
    def __init__(self):
        super().__init__()
        
        # 初始化控制器
        self._init_controllers()
        
        # 初始化UI组件
        self._init_ui_components()
        
        # 设置窗口属性
        self._setup_window()
        
        # 初始化UI布局
        self._init_ui()
        
        # 连接信号槽
        self._connect_signals()
        
        # 连接事件总线
        self._connect_events()
        
        # 注册组件到事件管理器
        self._register_components()
        
        # 启动认证流程 - 多重保障
        print("[主窗口] 准备启动认证流程...")

        # 方法1: 立即调用
        try:
            print("[主窗口] 尝试立即启动认证流程...")
            self._start_auth_flow()
        except Exception as e:
            print(f"[主窗口] 立即启动认证失败: {e}")

            # 方法2: 使用QTimer延迟调用
            print("[主窗口] 使用QTimer延迟启动...")
            QTimer.singleShot(100, self._start_auth_flow_safe)

        print("[主窗口] 重构版本初始化完成")
    
    def _init_controllers(self):
        """初始化控制器"""
        self.order_controller = OrderController(self)
        self.account_controller = AccountController(self)
        self.cinema_controller = CinemaController(self)
        
        print("[主窗口] 控制器初始化完成")
    
    def _init_ui_components(self):
        """初始化UI组件"""
        self.seat_map_panel = SeatMapPanel(self)
        self.account_panel = AccountPanel(self)
        self.cinema_panel = CinemaPanel(self)
        
        print("[主窗口] UI组件初始化完成")
    
    def _setup_window(self):
        """设置窗口属性"""
        self.setWindowTitle("柴犬影院下单系统 - 重构版本")
        self.setFixedSize(1500, 900)
        
        # 设置应用程序字体
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(10)
        
        # 创建三栏布局
        self._create_left_panel(main_layout)
        self._create_center_panel(main_layout)
        self._create_right_panel(main_layout)
        
        print("[主窗口] UI布局初始化完成")
    
    def _create_left_panel(self, main_layout: QHBoxLayout):
        """创建左栏面板 - 账号管理"""
        left_widget = QWidget()
        left_widget.setFixedWidth(300)
        left_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.addWidget(self.account_panel)
        
        main_layout.addWidget(left_widget)
    
    def _create_center_panel(self, main_layout: QHBoxLayout):
        """创建中栏面板 - 影院选择和座位图"""
        center_widget = QWidget()
        center_widget.setFixedWidth(900)
        center_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(5, 5, 5, 5)
        center_layout.setSpacing(10)
        
        # 上部：影院选择面板 (40%)
        center_layout.addWidget(self.cinema_panel, 40)
        
        # 下部：座位图面板 (60%)
        center_layout.addWidget(self.seat_map_panel, 60)
        
        main_layout.addWidget(center_widget)
    
    def _create_right_panel(self, main_layout: QHBoxLayout):
        """创建右栏面板 - 订单详情和支付"""
        right_widget = QWidget()
        right_widget.setFixedWidth(300)
        right_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)
        
        # 创建订单详情区域
        self._create_order_detail_area(right_layout)
        
        # 创建支付区域
        self._create_payment_area(right_layout)
        
        main_layout.addWidget(right_widget)
    
    def _create_order_detail_area(self, layout: QVBoxLayout):
        """创建订单详情区域"""
        from PyQt5.QtWidgets import QGroupBox
        
        # 订单详情组
        order_group = QGroupBox("订单详情")
        order_layout = QVBoxLayout(order_group)
        
        # 订单信息显示
        self.order_info_label = QLabel("暂无订单信息")
        self.order_info_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 3px;
                border: 1px solid #eee;
            }
        """)
        order_layout.addWidget(self.order_info_label)
        
        # 订单详情文本
        self.order_detail_text = QTextEdit()
        self.order_detail_text.setReadOnly(True)
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
        
        layout.addWidget(order_group, 70)
    
    def _create_payment_area(self, layout: QVBoxLayout):
        """创建支付区域"""
        from PyQt5.QtWidgets import QGroupBox
        
        # 支付组
        payment_group = QGroupBox("支付操作")
        payment_layout = QVBoxLayout(payment_group)
        
        # 倒计时标签
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("""
            QLabel {
                color: #0077ff;
                font: bold 10px "Microsoft YaHei";
                padding: 2px 4px;
                background-color: transparent;
            }
        """)
        payment_layout.addWidget(self.countdown_label)
        
        # 支付按钮
        self.pay_button = QPushButton("一键支付")
        self.pay_button.setMinimumHeight(40)
        self.pay_button.setEnabled(False)
        self.pay_button.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: #ffffff;
                font: bold 12px "Microsoft YaHei";
                border: none;
                padding: 10px;
                border-radius: 5px;
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
        payment_layout.addWidget(self.pay_button)
        
        # 取票码显示
        self.qr_display = QLabel("(取票码展示区)")
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
        payment_layout.addWidget(self.qr_display)
        
        layout.addWidget(payment_group, 30)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 账号面板信号
        self.account_panel.account_selected.connect(self.account_controller.select_account)
        self.account_panel.account_login_requested.connect(self.account_controller.login_account)
        self.account_panel.account_add_requested.connect(self.account_controller.add_account)
        self.account_panel.account_remove_requested.connect(self.account_controller.remove_account)
        
        # 影院面板信号
        self.cinema_panel.cinema_selected.connect(self.cinema_controller.select_cinema)
        self.cinema_panel.movie_selected.connect(self.cinema_controller.select_movie)
        self.cinema_panel.session_selected.connect(self.cinema_controller.select_session)
        
        # 座位图面板信号
        self.seat_map_panel.order_submitted.connect(self._on_order_submitted)
        
        # 控制器信号
        self.order_controller.order_error.connect(self._show_error_message)
        self.account_controller.account_error.connect(self._show_error_message)
        self.cinema_controller.cinema_error.connect(self._show_error_message)
        
        # 支付按钮
        self.pay_button.clicked.connect(self._on_pay_button_clicked)
        
        print("[主窗口] 信号槽连接完成")
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.user_login_success.connect(self._on_user_login_success)
        event_bus.order_detail_updated.connect(self._on_order_detail_updated)
        event_bus.order_paid.connect(self._on_order_paid)

        # 订阅自定义事件
        event_bus.subscribe('qrcode_received', self._on_qrcode_received)

        print("[主窗口] 事件总线连接完成")
    
    def _register_components(self):
        """注册组件到事件管理器"""
        event_manager.register_component("main_window", self)
        event_manager.register_component("order_controller", self.order_controller)
        event_manager.register_component("account_controller", self.account_controller)
        event_manager.register_component("cinema_controller", self.cinema_controller)
        event_manager.register_component("seat_map_panel", self.seat_map_panel)
        event_manager.register_component("account_panel", self.account_panel)
        event_manager.register_component("cinema_panel", self.cinema_panel)
        
        # 标记主窗口就绪
        event_manager.mark_component_ready("main_window")
        
        print("[主窗口] 组件注册完成")
    
    def _start_auth_flow(self):
        """启动认证流程"""
        print("[主窗口] _start_auth_flow() 被调用")
        try:
            print("[主窗口] 开始创建登录窗口...")

            # 创建登录窗口
            self.login_window = LoginWindow()
            print("[主窗口] 登录窗口创建成功")

            self.login_window.login_success.connect(self._on_login_success)
            print("[主窗口] 登录信号连接成功")

            # 确保登录窗口在主屏幕中央显示
            self._center_login_window()

            # 显示登录窗口
            print("[主窗口] 准备显示登录窗口...")
            self.login_window.show()
            self.login_window.raise_()
            self.login_window.activateWindow()

            # 强制刷新和重绘
            self.login_window.repaint()
            self.login_window.update()

            print(f"[主窗口] 启动用户认证流程完成")
            print(f"[主窗口] 登录窗口位置: {self.login_window.pos()}")
            print(f"[主窗口] 登录窗口可见: {self.login_window.isVisible()}")
            print(f"[主窗口] 登录窗口大小: {self.login_window.size()}")

        except Exception as e:
            print(f"[主窗口] 启动认证流程异常: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "启动错误", f"启动认证流程失败: {str(e)}")

    def _start_auth_flow_safe(self):
        """安全的认证流程启动方法"""
        print("[主窗口] _start_auth_flow_safe() 被调用")
        try:
            # 如果登录窗口已经存在，先关闭
            if hasattr(self, 'login_window') and self.login_window:
                print("[主窗口] 发现已存在的登录窗口，先关闭")
                self.login_window.close()
                self.login_window = None

            # 调用标准认证流程
            self._start_auth_flow()

        except Exception as e:
            print(f"[主窗口] 安全认证流程启动异常: {e}")
            import traceback
            traceback.print_exc()

            # 最后的备用方案：显示错误对话框并提供手动启动选项
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self,
                "认证流程启动失败",
                f"自动启动登录窗口失败: {str(e)}\n\n是否手动启动登录？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )

            if reply == QMessageBox.Yes:
                self._manual_start_login()

    def _manual_start_login(self):
        """手动启动登录窗口"""
        print("[主窗口] 手动启动登录窗口")
        try:
            # 直接创建并显示登录窗口，使用最简单的方式
            from ui.login_window import LoginWindow

            self.login_window = LoginWindow()
            self.login_window.login_success.connect(self._on_login_success)

            # 强制设置窗口位置到屏幕中央
            self.login_window.move(100, 100)  # 安全位置

            # 设置窗口属性确保可见
            self.login_window.setWindowFlags(self.login_window.windowFlags() | Qt.WindowStaysOnTopHint)
            self.login_window.show()
            self.login_window.raise_()
            self.login_window.activateWindow()

            print(f"[主窗口] 手动登录窗口启动完成")
            print(f"[主窗口] 窗口位置: {self.login_window.pos()}")
            print(f"[主窗口] 窗口可见: {self.login_window.isVisible()}")

        except Exception as e:
            print(f"[主窗口] 手动启动登录窗口失败: {e}")
            import traceback
            traceback.print_exc()

            # 最终备用方案：跳过登录直接显示主窗口
            QMessageBox.information(
                self,
                "跳过登录",
                "登录窗口启动失败，将跳过登录直接进入主界面。\n\n您可以在账号面板中手动添加和登录账号。"
            )

            # 模拟登录成功，直接显示主窗口
            fake_user_info = {
                'phone': '未登录',
                'username': '游客用户',
                'points': 0
            }
            self._on_login_success(fake_user_info)

    def _center_login_window(self):
        """确保登录窗口在主屏幕中央"""
        try:
            from PyQt5.QtWidgets import QDesktopWidget

            # 获取主屏幕几何信息
            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry(desktop.primaryScreen())

            # 计算登录窗口的中央位置
            login_size = self.login_window.size()
            x = screen_rect.x() + (screen_rect.width() - login_size.width()) // 2
            y = screen_rect.y() + (screen_rect.height() - login_size.height()) // 2

            # 确保窗口在屏幕范围内
            x = max(screen_rect.x(), min(x, screen_rect.x() + screen_rect.width() - login_size.width()))
            y = max(screen_rect.y(), min(y, screen_rect.y() + screen_rect.height() - login_size.height()))

            self.login_window.move(x, y)
            print(f"[主窗口] 登录窗口已移动到主屏幕中央: ({x}, {y})")

        except Exception as e:
            print(f"[主窗口] 居中登录窗口失败: {e}")
            # 如果居中失败，至少移动到(100, 100)确保可见
            self.login_window.move(100, 100)
    
    @event_handler("login_success")
    def _on_login_success(self, user_info: dict):
        """登录成功处理"""
        try:
            print(f"[主窗口] 用户登录成功: {user_info.get('phone', 'N/A')}")
            
            # 关闭登录窗口
            if hasattr(self, 'login_window') and self.login_window:
                self.login_window.close()
                self.login_window = None
            
            # 显示主窗口
            self.show()
            self.raise_()
            self.activateWindow()
            self._center_window()
            
            # 发布登录成功事件
            self.login_success.emit(user_info)
            event_bus.user_login_success.emit(user_info)
            
            # 启动数据加载
            QTimer.singleShot(500, self._start_data_loading)
            
        except Exception as e:
            QMessageBox.critical(self, "登录处理错误", f"处理登录结果失败: {str(e)}")
    
    def _start_data_loading(self):
        """启动数据加载 - 优化版：先影院后账号"""
        try:
            print("[主窗口] 开始智能数据加载流程...")

            # 第一步：加载影院列表
            print("[主窗口] 步骤1: 加载影院列表")
            cinemas = self.cinema_controller.load_cinema_list()

            if cinemas and len(cinemas) > 0:
                # 第二步：自动选择第一个影院
                first_cinema = cinemas[0]
                cinema_name = first_cinema.get('cinemaShortName', first_cinema.get('name', ''))
                cinema_id = first_cinema.get('cinemaid', '')

                print(f"[主窗口] 步骤2: 自动选择默认影院: {cinema_name} ({cinema_id})")

                # 发布影院选择事件
                from utils.signals import event_bus
                event_bus.cinema_selected.emit(first_cinema)

                # 第三步：延迟加载该影院的关联账号
                QTimer.singleShot(300, lambda: self._load_cinema_accounts(first_cinema))
            else:
                print("[主窗口] 没有可用影院，加载所有账号")
                self.account_controller.load_account_list()

            print("[主窗口] 智能数据加载流程启动完成")

        except Exception as e:
            print(f"[主窗口] 数据加载错误: {e}")

    def _load_cinema_accounts(self, cinema_info: dict):
        """为指定影院加载关联账号"""
        try:
            cinema_name = cinema_info.get('cinemaShortName', cinema_info.get('name', ''))
            cinema_id = cinema_info.get('cinemaid', '')

            print(f"[主窗口] 步骤3: 加载影院 {cinema_name} 的关联账号")

            # 加载账号列表（账号控制器会根据当前影院过滤）
            accounts = self.account_controller.load_account_list()

            if accounts and len(accounts) > 0:
                # 第四步：自动选择第一个账号
                first_account = accounts[0]
                userid = first_account.get('userid', first_account.get('phone', ''))

                print(f"[主窗口] 步骤4: 自动选择默认账号: {userid}")

                # 选择账号
                self.account_controller.select_account(first_account)

                print(f"[主窗口] ✅ 智能加载完成: 影院={cinema_name}, 账号={userid}")
                print(f"[主窗口] 🎬 现在可以开始选择影片和场次了")
            else:
                print(f"[主窗口] ⚠️  影院 {cinema_name} 没有关联账号，请手动添加账号")

        except Exception as e:
            print(f"[主窗口] 加载影院账号错误: {e}")
    
    def _center_window(self):
        """居中显示窗口"""
        try:
            from PyQt5.QtWidgets import QDesktopWidget
            screen = QDesktopWidget().screenGeometry()
            size = self.geometry()
            x = (screen.width() - size.width()) // 2
            y = (screen.height() - size.height()) // 2
            self.move(x, y)
        except Exception as e:
            print(f"[主窗口] 居中窗口失败: {e}")
    
    @event_handler("user_login_success")
    def _on_user_login_success(self, user_info: dict):
        """用户登录成功事件处理"""
        self.order_info_label.setText(f"用户: {user_info.get('phone', 'N/A')}")
        self.order_info_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-weight: bold;
                padding: 10px;
                background-color: #E8F5E9;
                border-radius: 3px;
                border: 1px solid #C8E6C9;
            }
        """)
    
    @event_handler("order_detail_updated")
    def _on_order_detail_updated(self, order_detail: dict):
        """订单详情更新处理"""
        try:
            details = f"订单信息:\n"
            details += f"订单号: {order_detail.get('order_id', 'N/A')}\n"
            details += f"影院: {order_detail.get('cinema', 'N/A')}\n"
            details += f"影片: {order_detail.get('movie', 'N/A')}\n"
            details += f"场次: {order_detail.get('session', 'N/A')}\n"
            details += f"座位: {order_detail.get('seats', 'N/A')}\n"
            details += f"金额: ¥{order_detail.get('amount', 0):.2f}\n"
            details += f"状态: {order_detail.get('status', '未知')}"
            
            self.order_detail_text.setPlainText(details)
            
            # 如果是待支付状态，启用支付按钮
            if order_detail.get('status') == '待支付':
                self.pay_button.setEnabled(True)
                self._start_countdown(900)  # 15分钟倒计时
            
        except Exception as e:
            print(f"[主窗口] 订单详情更新错误: {e}")
    
    def _on_order_submitted(self, order_data: dict):
        """订单提交处理"""
        try:
            # 通过事件总线发送订单提交事件
            event_bus.order_submitted.emit(order_data)
            
        except Exception as e:
            print(f"[主窗口] 订单提交处理错误: {e}")
    
    def _on_pay_button_clicked(self):
        """支付按钮点击处理"""
        try:
            # 获取当前订单ID（这里需要从订单控制器获取）
            current_order = self.order_controller.current_order
            if current_order:
                order_id = current_order.get('order_id', '')
                if order_id:
                    self.order_controller.pay_order(order_id)
            
        except Exception as e:
            print(f"[主窗口] 支付处理错误: {e}")
    
    @event_handler("order_paid")
    def _on_order_paid(self, order_id: str):
        """订单支付成功处理"""
        try:
            print(f"[主窗口] 订单支付成功: {order_id}")
            self.pay_button.setEnabled(False)
            self._stop_countdown()

            # 更新订单详情
            self.order_detail_text.append("\n\n✅ 支付成功！")

        except Exception as e:
            print(f"[主窗口] 支付成功处理错误: {e}")
    
    def _on_qrcode_received(self, qr_data: dict):
        """取票码接收处理"""
        try:
            qr_code = qr_data.get('qrcode', '')
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
            print(f"[主窗口] 取票码处理错误: {e}")
    
    def _start_countdown(self, seconds: int):
        """启动倒计时"""
        # 这里可以实现倒计时逻辑
        self.countdown_label.setText(f"支付倒计时: {seconds//60:02d}:{seconds%60:02d}")
    
    def _stop_countdown(self):
        """停止倒计时"""
        self.countdown_label.setText("")
    
    def _show_error_message(self, title: str, message: str):
        """显示错误消息"""
        QMessageBox.critical(self, title, message)
