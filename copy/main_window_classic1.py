#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 经典风格主窗口
基于原版界面设计，保持简洁实用的风格
"""

import sys
import os
from typing import Dict, List, Optional, Any

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QListWidget, QTabWidget,
    QGroupBox, QFrame, QTreeWidget, QTreeWidgetItem, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QScrollArea, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

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
                font: 11px "Microsoft YaHei";
                background-color: #ffffff;
                color: #333333;
                min-width: 120px;
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
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口基本属性
        self.setWindowTitle("柴犬影院下单系统 - PyQt5完整版")
        self.setFixedSize(1250, 750)
        
        # 设置经典主题
        self._setup_classic_theme()
        
        # 初始化界面
        self._init_ui()
    
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
        
        # 计算各栏宽度 - 保持原有区域分布
        total_width = 1250
        total_height = 750
        left_w = int(total_width * 0.2)    # 250px (20%)
        center_w = int(total_width * 0.6)  # 750px (60%)
        right_w = total_width - left_w - center_w  # 250px (20%)
        
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
        
        # 按钮区域
        button_layout = QHBoxLayout()
        self.login_btn = ClassicButton("登录账号", "primary")
        self.clear_btn = ClassicButton("清空", "default")
        
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)
        
        # 状态显示
        self.login_status = QLabel("请输入账号信息登录")
        self.login_status.setStyleSheet("""
            QLabel {
                color: #666666;
                font: 10px "Microsoft YaHei";
                padding: 5px;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.login_status)
        
        layout.addStretch()
    
    def _build_account_list_classic(self, parent_group):
        """构建经典风格账号列表"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        refresh_btn = ClassicButton("刷新", "default")
        refresh_btn.setMaximumWidth(50)
        clear_coupon_btn = ClassicButton("清空券", "warning")
        clear_coupon_btn.setMaximumWidth(60)
        refresh_coupon_btn = ClassicButton("刷新券", "success")
        refresh_coupon_btn.setMaximumWidth(60)
        
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(clear_coupon_btn)
        button_layout.addWidget(refresh_coupon_btn)
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
        
        # 添加示例数据
        self.account_table.setRowCount(3)
        self.account_table.setItem(0, 0, QTableWidgetItem("15155712316"))
        self.account_table.setItem(0, 1, QTableWidgetItem("华夏优加荟"))
        self.account_table.setItem(0, 2, QTableWidgetItem("400.0"))
        
        self.account_table.setItem(1, 0, QTableWidgetItem("14700283316"))
        self.account_table.setItem(1, 1, QTableWidgetItem("万达影城"))
        self.account_table.setItem(1, 2, QTableWidgetItem("0"))
        
        self.account_table.setItem(2, 0, QTableWidgetItem("15155712316"))
        self.account_table.setItem(2, 1, QTableWidgetItem("CGV影城"))
        self.account_table.setItem(2, 2, QTableWidgetItem("262.8"))
        
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
        
        # 左侧：影院选择
        cinema_group = ClassicGroupBox("影院选择")
        self._build_cinema_select_classic(cinema_group)
        tab1_layout.addWidget(cinema_group)
        
        # 右侧：可用券列表
        coupon_group = ClassicGroupBox("可用券列表")
        self._build_coupon_list_classic(coupon_group)
        tab1_layout.addWidget(coupon_group)
        
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
        current_account = QLabel("当前账号: 14700283316 (余额:30)")
        current_account.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font: bold 11px "Microsoft YaHei";
                padding: 8px;
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 3px;
            }
        """)
        layout.addWidget(current_account)
        
        # 影院选择
        cinema_layout = QHBoxLayout()
        cinema_label = QLabel("影院:")
        cinema_label.setMinimumWidth(50)
        self.cinema_combo = ClassicComboBox()
        self.cinema_combo.addItems(["华夏优加荟大都荟", "万达影城", "CGV影城"])
        cinema_layout.addWidget(cinema_label)
        cinema_layout.addWidget(self.cinema_combo)
        layout.addLayout(cinema_layout)
        
        # 影片选择
        movie_layout = QHBoxLayout()
        movie_label = QLabel("影片:")
        movie_label.setMinimumWidth(50)
        self.movie_combo = ClassicComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        movie_layout.addWidget(movie_label)
        movie_layout.addWidget(self.movie_combo)
        layout.addLayout(movie_layout)
        
        # 日期选择
        date_layout = QHBoxLayout()
        date_label = QLabel("日期:")
        date_label.setMinimumWidth(50)
        self.date_combo = ClassicComboBox()
        self.date_combo.addItems(["请先选择影片"])
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_combo)
        layout.addLayout(date_layout)
        
        # 场次选择
        session_layout = QHBoxLayout()
        session_label = QLabel("场次:")
        session_label.setMinimumWidth(50)
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
        
        seat_input = ClassicLineEdit()
        seat_input.setPlaceholderText("座位选择")
        seat_info_layout.addWidget(seat_input)
        
        layout.addLayout(seat_info_layout)
        
        # 座位图区域（占位）
        seat_placeholder = QLabel("座位图将在此显示\n\n请先选择影院、影片、日期和场次")
        seat_placeholder.setAlignment(Qt.AlignCenter)
        seat_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 60px;
            }
        """)
        layout.addWidget(seat_placeholder)
        
        # 提交订单按钮
        submit_btn = ClassicButton("提交订单", "success")
        submit_btn.setMinimumHeight(35)
        layout.addWidget(submit_btn)
    
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
        pay_btn = ClassicButton("一键支付", "warning")
        pay_btn.setMinimumHeight(35)
        layout.addWidget(pay_btn)


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