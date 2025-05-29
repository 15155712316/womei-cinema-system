#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 现代化UI主窗口
保持区域分布一致，但采用现代化设计风格
"""

import sys
import os
from typing import Dict, List, Optional, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QTabWidget,
    QGroupBox, QFrame, QTreeWidget, QTreeWidgetItem, QComboBox,
    QProgressBar, QScrollArea, QSplitter, QGraphicsView, QGraphicsScene
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QLinearGradient, QPainter,
    QBrush, QPen, QFontMetrics
)

class ModernCard(QFrame):
    """现代化卡片组件"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.title = title
        self._setup_style()
        self._setup_layout()
    
    def _setup_style(self):
        """设置现代化卡片样式"""
        self.setStyleSheet("""
            ModernCard {
                background-color: #ffffff;
                border: none;
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
        """)
    
    def _setup_layout(self):
        """设置布局"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 15, 20, 15)
        self.main_layout.setSpacing(12)
        
        if self.title:
            # 标题
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
            title_label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    background: transparent;
                    border: none;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #3498db;
                }
            """)
            self.main_layout.addWidget(title_label)
    
    def add_widget(self, widget):
        """添加组件到卡片"""
        self.main_layout.addWidget(widget)

class ModernButton(QPushButton):
    """现代化按钮组件"""
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
    
    def _setup_style(self):
        """设置按钮样式"""
        base_style = """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font: 600 11px "Microsoft YaHei";
                min-height: 16px;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                transform: translateY(0px);
            }
        """
        
        if self.button_type == "primary":
            style = base_style + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4facfe, stop:1 #00f2fe);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #43a6fc, stop:1 #00e8fc);
                }
            """
        elif self.button_type == "success":
            style = base_style + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #56ab2f, stop:1 #a8e6cf);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4e9f28, stop:1 #98d9bd);
                }
            """
        elif self.button_type == "warning":
            style = base_style + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff9500, stop:1 #ffb347);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e6850e, stop:1 #ffa033);
                }
            """
        elif self.button_type == "secondary":
            style = base_style + """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
                    color: white;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5a6fd8, stop:1 #693f8f);
                }
            """
        else:  # default
            style = base_style + """
                QPushButton {
                    background: #f8f9fa;
                    color: #495057;
                    border: 1px solid #dee2e6;
                }
                QPushButton:hover {
                    background: #e9ecef;
                    border-color: #adb5bd;
                }
            """
        
        self.setStyleSheet(style)

class ModernInput(QLineEdit):
    """现代化输入框组件"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_style()
    
    def _setup_style(self):
        """设置输入框样式"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font: 11px "Microsoft YaHei";
                background-color: #ffffff;
                color: #495057;
            }
            QLineEdit:focus {
                border-color: #4facfe;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #adb5bd;
            }
        """)

class ModernComboBox(QComboBox):
    """现代化下拉框组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置下拉框样式"""
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 12px 16px;
                font: 11px "Microsoft YaHei";
                background-color: #ffffff;
                color: #495057;
                min-width: 120px;
            }
            QComboBox:focus {
                border-color: #4facfe;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #6c757d;
                margin-right: 10px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dee2e6;
                border-radius: 8px;
                background-color: #ffffff;
                selection-background-color: #4facfe;
                selection-color: white;
                padding: 8px;
            }
        """)

class ModernListWidget(QListWidget):
    """现代化列表组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置列表样式"""
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                alternate-background-color: #f8f9fa;
                font: 11px "Microsoft YaHei";
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #f1f3f4;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
                border-radius: 6px;
            }
        """)

class ModernTabWidget(QTabWidget):
    """现代化Tab组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置Tab样式"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #f8f9fa;
                color: #6c757d;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font: 600 11px "Microsoft YaHei";
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4facfe, stop:1 #00f2fe);
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background: #e9ecef;
                color: #495057;
            }
        """)

class CinemaOrderSimulatorModernWindow(QMainWindow):
    """柴犬影院下单系统现代化主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("🎬 柴犬影院下单系统 - 现代版")
        self.setFixedSize(1250, 750)
        
        # 设置现代化主题
        self._setup_modern_theme()
        
        # 初始化界面
        self._init_ui()
    
    def _setup_modern_theme(self):
        """设置现代化主题"""
        # 设置主窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
        """)
    
    def _init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 计算各栏宽度 - 保持原有区域分布
        total_width = 1250
        total_height = 750
        left_w = int(total_width * 0.2)    # 250px (20%)
        center_w = int(total_width * 0.6)  # 750px (60%)
        right_w = total_width - left_w - center_w  # 250px (20%)
        
        # 创建三栏布局 - 使用现代化间距
        self._create_left_panel_modern(5, 5, left_w-10, total_height-10)
        self._create_center_panel_modern(left_w+5, 5, center_w-10, total_height-10)
        self._create_right_panel_modern(left_w+center_w+5, 5, right_w-10, total_height-10)
    
    def _create_left_panel_modern(self, x: int, y: int, width: int, height: int):
        """创建现代化左栏面板"""
        # 主容器
        left_container = QWidget(self.centralWidget())
        left_container.setGeometry(x, y, width, height)
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 账号登录卡片
        login_card = ModernCard("🔐 账号登录")
        self._build_login_area_modern(login_card)
        left_layout.addWidget(login_card)
        
        # 账号列表卡片
        account_card = ModernCard("👥 账号管理")
        self._build_account_list_modern(account_card)
        left_layout.addWidget(account_card)
        
        # 设置比例
        left_layout.setStretchFactor(login_card, 2)
        left_layout.setStretchFactor(account_card, 3)
    
    def _build_login_area_modern(self, parent_card):
        """构建现代化登录区域"""
        # 输入区域
        input_layout = QVBoxLayout()
        input_layout.setSpacing(12)
        
        # 手机号输入
        self.phone_input = ModernInput("请输入手机号")
        input_layout.addWidget(self.phone_input)
        
        # OpenID输入
        self.openid_input = ModernInput("请输入OpenID")
        input_layout.addWidget(self.openid_input)
        
        # Token输入
        self.token_input = ModernInput("请输入Token")
        input_layout.addWidget(self.token_input)
        
        parent_card.add_widget(QWidget())  # 占位
        parent_card.main_layout.addLayout(input_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_btn = ModernButton("登录账号", "primary")
        self.clear_btn = ModernButton("清空", "default")
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        parent_card.main_layout.addLayout(button_layout)
        
        # 状态显示
        self.login_status = QLabel("请输入账号信息")
        self.login_status.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font: 10px "Microsoft YaHei";
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #e9ecef;
            }
        """)
        parent_card.add_widget(self.login_status)
        
        parent_card.main_layout.addStretch()
    
    def _build_account_list_modern(self, parent_card):
        """构建现代化账号列表"""
        # 操作按钮区
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        refresh_btn = ModernButton("刷新", "secondary")
        refresh_btn.setMaximumWidth(60)
        clear_coupon_btn = ModernButton("清空券", "warning")
        clear_coupon_btn.setMaximumWidth(70)
        refresh_coupon_btn = ModernButton("刷新券", "success")
        refresh_coupon_btn.setMaximumWidth(70)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_coupon_btn)
        button_layout.addWidget(refresh_coupon_btn)
        button_layout.addStretch()
        
        parent_card.main_layout.addLayout(button_layout)
        
        # 账号列表
        self.account_list = ModernListWidget()
        # 添加示例数据
        self.account_list.addItem("📱 138****1234 (主账号)")
        self.account_list.addItem("📱 159****5678")
        self.account_list.addItem("📱 186****9012")
        
        parent_card.add_widget(self.account_list)
    
    def _create_center_panel_modern(self, x: int, y: int, width: int, height: int):
        """创建现代化中栏面板"""
        # 主容器
        center_container = QWidget(self.centralWidget())
        center_container.setGeometry(x, y, width, height)
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(15)
        
        # Tab区域卡片
        tab_card = ModernCard()
        self._create_tab_area_modern(tab_card)
        center_layout.addWidget(tab_card)
        
        # 座位区域卡片
        seat_card = ModernCard("🎭 座位选择")
        self._create_seat_area_modern(seat_card)
        center_layout.addWidget(seat_card)
        
        # 设置比例
        center_layout.setStretchFactor(tab_card, 2)
        center_layout.setStretchFactor(seat_card, 3)
    
    def _create_tab_area_modern(self, parent_card):
        """创建现代化Tab区域"""
        self.tab_widget = ModernTabWidget()
        
        # Tab1: 出票
        tab1 = QWidget()
        tab1_layout = QHBoxLayout(tab1)
        tab1_layout.setSpacing(15)
        
        # 左侧：影院选择
        cinema_card = ModernCard("🏢 影院选择")
        self._build_cinema_select_modern(cinema_card)
        tab1_layout.addWidget(cinema_card)
        
        # 右侧：券列表
        coupon_card = ModernCard("🎫 优惠券")
        self._build_coupon_list_modern(coupon_card)
        tab1_layout.addWidget(coupon_card)
        
        self.tab_widget.addTab(tab1, "🎟️ 出票")
        
        # 其他Tab页面
        for i, (icon, name) in enumerate([
            ("🎫", "绑券"), ("💰", "兑换券"), ("📋", "订单"), ("🏢", "影院")
        ], 2):
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            placeholder = QLabel(f"{icon} {name}功能区域")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    font: 16px "Microsoft YaHei";
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 12px;
                    padding: 40px;
                }
            """)
            tab_layout.addWidget(placeholder)
            
            self.tab_widget.addTab(tab, f"{icon} {name}")
        
        parent_card.add_widget(self.tab_widget)
    
    def _build_cinema_select_modern(self, parent_card):
        """构建现代化影院选择"""
        # 当前账号显示
        current_account = QLabel("当前账号: 未选择")
        current_account.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font: bold 11px "Microsoft YaHei";
                padding: 8px 12px;
                background-color: #fff5f5;
                border: 1px solid #fed7d7;
                border-radius: 6px;
            }
        """)
        parent_card.add_widget(current_account)
        
        # 下拉框区域
        combo_layout = QVBoxLayout()
        combo_layout.setSpacing(12)
        
        # 影院选择
        cinema_label = QLabel("🏢 选择影院:")
        cinema_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        combo_layout.addWidget(cinema_label)
        
        self.cinema_combo = ModernComboBox()
        self.cinema_combo.addItems(["华夏优加荟大都荟", "万达影城", "CGV影城"])
        combo_layout.addWidget(self.cinema_combo)
        
        # 影片选择
        movie_label = QLabel("🎬 选择影片:")
        movie_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        combo_layout.addWidget(movie_label)
        
        self.movie_combo = ModernComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        combo_layout.addWidget(self.movie_combo)
        
        # 日期选择
        date_label = QLabel("📅 选择日期:")
        date_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        combo_layout.addWidget(date_label)
        
        self.date_combo = ModernComboBox()
        self.date_combo.addItems(["请先选择影片"])
        combo_layout.addWidget(self.date_combo)
        
        # 场次选择
        session_label = QLabel("⏰ 选择场次:")
        session_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        combo_layout.addWidget(session_label)
        
        self.session_combo = ModernComboBox()
        self.session_combo.addItems(["请先选择日期"])
        combo_layout.addWidget(self.session_combo)
        
        parent_card.main_layout.addLayout(combo_layout)
        
        # 操作按钮
        open_seat_btn = ModernButton("🎭 打开选座", "success")
        parent_card.add_widget(open_seat_btn)
        
        parent_card.main_layout.addStretch()
    
    def _build_coupon_list_modern(self, parent_card):
        """构建现代化券列表"""
        self.coupon_list = ModernListWidget()
        # 添加示例券数据
        self.coupon_list.addItem("🎫 10元代金券 (有效期至2024-12-31)")
        self.coupon_list.addItem("🎫 5折优惠券 (限周末使用)")
        self.coupon_list.addItem("🎫 买一送一券 (限工作日)")
        
        parent_card.add_widget(self.coupon_list)
    
    def _create_seat_area_modern(self, parent_card):
        """创建现代化座位区域"""
        # 座位图容器
        seat_container = QWidget()
        seat_layout = QVBoxLayout(seat_container)
        
        # 屏幕标识
        screen_label = QLabel("🎬 银 幕")
        screen_label.setAlignment(Qt.AlignCenter)
        screen_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font: bold 14px "Microsoft YaHei";
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
        """)
        seat_layout.addWidget(screen_label)
        
        # 座位图区域（占位）
        seat_placeholder = QLabel("🪑 座位图将在此显示\n\n点击选座按钮加载座位信息")
        seat_placeholder.setAlignment(Qt.AlignCenter)
        seat_placeholder.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font: 14px "Microsoft YaHei";
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 12px;
                padding: 60px;
            }
        """)
        seat_layout.addWidget(seat_placeholder)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        submit_btn = ModernButton("🛒 提交订单", "primary")
        clear_btn = ModernButton("🗑️ 清空选择", "default")
        
        button_layout.addWidget(submit_btn)
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        
        seat_layout.addLayout(button_layout)
        
        parent_card.add_widget(seat_container)
    
    def _create_right_panel_modern(self, x: int, y: int, width: int, height: int):
        """创建现代化右栏面板"""
        # 主容器
        right_container = QWidget(self.centralWidget())
        right_container.setGeometry(x, y, width, height)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 取票码卡片
        qrcode_card = ModernCard("📱 取票码")
        self._build_qrcode_area_modern(qrcode_card)
        right_layout.addWidget(qrcode_card)
        
        # 订单详情卡片
        order_card = ModernCard("📋 订单详情")
        self._build_order_detail_modern(order_card)
        right_layout.addWidget(order_card)
        
        # 设置比例
        right_layout.setStretchFactor(qrcode_card, 2)
        right_layout.setStretchFactor(order_card, 3)
    
    def _build_qrcode_area_modern(self, parent_card):
        """构建现代化取票码区域"""
        qrcode_placeholder = QLabel("📱\n\n取票码/二维码\n将在此显示")
        qrcode_placeholder.setAlignment(Qt.AlignCenter)
        qrcode_placeholder.setStyleSheet("""
            QLabel {
                color: #6c757d;
                font: 12px "Microsoft YaHei";
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 12px;
                padding: 40px;
                line-height: 1.6;
            }
        """)
        parent_card.add_widget(qrcode_placeholder)
    
    def _build_order_detail_modern(self, parent_card):
        """构建现代化订单详情"""
        # 用户信息
        self.user_info = QLabel("")
        self.user_info.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                font: bold 12px "Microsoft YaHei";
                padding: 8px 12px;
                background-color: #fff5f5;
                border: 1px solid #fed7d7;
                border-radius: 6px;
            }
        """)
        parent_card.add_widget(self.user_info)
        
        # 订单详情文本
        self.order_detail = QTextEdit()
        self.order_detail.setReadOnly(True)
        self.order_detail.setPlaceholderText("订单详情将在此显示...")
        self.order_detail.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: #ffffff;
                font: 10px "Microsoft YaHei";
                padding: 12px;
                line-height: 1.5;
            }
        """)
        parent_card.add_widget(self.order_detail)
        
        # 倒计时
        self.countdown = QLabel("")
        self.countdown.setStyleSheet("""
            QLabel {
                color: #4facfe;
                font: bold 11px "Microsoft YaHei";
                padding: 8px 12px;
                background-color: #f0f9ff;
                border: 1px solid #cce7ff;
                border-radius: 6px;
            }
        """)
        parent_card.add_widget(self.countdown)
        
        # 支付按钮
        pay_btn = ModernButton("💳 一键支付", "warning")
        parent_card.add_widget(pay_btn)


def main():
    """测试现代化界面"""
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle('Fusion')
    
    window = CinemaOrderSimulatorModernWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 