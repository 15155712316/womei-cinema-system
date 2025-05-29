#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化系统演示程序
展示各个模块的基本功能
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt

# 导入模块化组件
from ui.widgets.classic_components import (
    ClassicGroupBox, ClassicButton, ClassicLabel, apply_classic_theme_to_widget
)
from ui.interfaces.plugin_interface import event_bus


class ModularDemoWindow(QMainWindow):
    """模块化系统演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("柴犬影院模块化系统演示")
        self.setFixedSize(1200, 800)
        
        # 应用经典主题
        apply_classic_theme_to_widget(self)
        
        self._init_ui()
        self._connect_events()
    
    def _init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 左栏：模块列表
        self._create_module_list(layout)
        
        # 中栏：功能演示区
        self._create_demo_area(layout)
        
        # 右栏：事件日志
        self._create_event_log(layout)
    
    def _create_module_list(self, parent_layout):
        """创建模块列表"""
        module_group = ClassicGroupBox("模块列表")
        module_layout = QVBoxLayout(module_group)
        
        modules = [
            "🔌 插件接口系统",
            "🎨 经典组件库", 
            "👤 账号管理模块",
            "📱 Tab页面管理模块",
            "🎫 座位订单模块"
        ]
        
        for module in modules:
            label = ClassicLabel(module)
            label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    margin: 2px;
                    background-color: #ffffff;
                }
                QLabel:hover {
                    background-color: #e6f3ff;
                    border-color: #0066cc;
                }
            """)
            module_layout.addWidget(label)
        
        module_layout.addStretch()
        
        module_group.setFixedWidth(250)
        parent_layout.addWidget(module_group)
    
    def _create_demo_area(self, parent_layout):
        """创建演示区域"""
        demo_group = ClassicGroupBox("功能演示")
        demo_layout = QVBoxLayout(demo_group)
        
        # 演示按钮区
        button_layout = QHBoxLayout()
        
        self.demo_btn1 = ClassicButton("账号切换演示", "primary")
        self.demo_btn2 = ClassicButton("影院选择演示", "success")
        self.demo_btn3 = ClassicButton("订单创建演示", "warning")
        
        button_layout.addWidget(self.demo_btn1)
        button_layout.addWidget(self.demo_btn2)
        button_layout.addWidget(self.demo_btn3)
        button_layout.addStretch()
        
        demo_layout.addLayout(button_layout)
        
        # 演示内容区
        self.demo_content = ClassicLabel(
            "欢迎使用柴犬影院模块化系统！\n\n"
            "🎯 系统特性：\n"
            "• 模块化架构设计\n"
            "• 插件式组件加载\n"
            "• 事件总线通信\n"
            "• 经典桌面UI风格\n\n"
            "点击上方按钮体验各模块功能"
        )
        self.demo_content.setAlignment(Qt.AlignTop)
        self.demo_content.setStyleSheet("""
            QLabel {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        
        demo_layout.addWidget(self.demo_content)
        
        parent_layout.addWidget(demo_group)
    
    def _create_event_log(self, parent_layout):
        """创建事件日志"""
        log_group = ClassicGroupBox("事件日志")
        log_layout = QVBoxLayout(log_group)
        
        self.event_log = ClassicLabel("系统启动...\n准备就绪")
        self.event_log.setAlignment(Qt.AlignTop)
        self.event_log.setStyleSheet("""
            QLabel {
                background-color: #000000;
                color: #00ff00;
                border: 1px solid #333;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
        """)
        
        log_layout.addWidget(self.event_log)
        
        log_group.setFixedWidth(300)
        parent_layout.addWidget(log_group)
    
    def _connect_events(self):
        """连接事件"""
        # 连接演示按钮
        self.demo_btn1.clicked.connect(self._demo_account_switch)
        self.demo_btn2.clicked.connect(self._demo_cinema_select)
        self.demo_btn3.clicked.connect(self._demo_order_create)
        
        # 连接全局事件总线
        event_bus.account_changed.connect(self._on_account_changed)
        event_bus.cinema_selected.connect(self._on_cinema_selected)
        event_bus.order_created.connect(self._on_order_created)
    
    def _demo_account_switch(self):
        """演示账号切换"""
        account_data = {
            "userid": "demo_user_001",
            "balance": 158.50,
            "cinemaid": "35fec8259e74"
        }
        
        # 发布账号切换事件
        event_bus.account_changed.emit(account_data)
        
        # 更新演示内容
        self.demo_content.setText(
            "📱 账号切换演示\n\n"
            f"当前账号：{account_data['userid']}\n"
            f"账户余额：¥{account_data['balance']:.2f}\n"
            f"绑定影院：{account_data['cinemaid']}\n\n"
            "✨ 账号切换事件已通过事件总线广播\n"
            "所有模块将同步更新账号状态"
        )
    
    def _demo_cinema_select(self):
        """演示影院选择"""
        cinema_name = "深影国际影城(佐伦虹湾购物中心店)"
        
        # 发布影院选择事件
        event_bus.cinema_selected.emit(cinema_name)
        
        # 更新演示内容
        self.demo_content.setText(
            "🏢 影院选择演示\n\n"
            f"选择影院：{cinema_name}\n"
            f"影院ID：11b7e4bcc265\n"
            f"地址：福田区北环大道6098号\n\n"
            "✨ 影院选择事件已通过事件总线广播\n"
            "座位选择模块将更新可用场次"
        )
    
    def _demo_order_create(self):
        """演示订单创建"""
        import time
        
        order_data = {
            "order_id": f"ORDER{int(time.time())}",
            "cinema": "深影国际影城",
            "movie": "阿凡达：水之道",
            "seats": ["A1", "A2"],
            "amount": 70.0
        }
        
        # 发布订单创建事件
        event_bus.order_created.emit(order_data)
        
        # 更新演示内容
        self.demo_content.setText(
            "🎫 订单创建演示\n\n"
            f"订单号：{order_data['order_id']}\n"
            f"影院：{order_data['cinema']}\n"
            f"影片：{order_data['movie']}\n"
            f"座位：{', '.join(order_data['seats'])}\n"
            f"金额：¥{order_data['amount']:.2f}\n\n"
            "✨ 订单创建事件已通过事件总线广播\n"
            "支付模块将准备处理支付请求"
        )
    
    def _on_account_changed(self, account_data):
        """账号切换事件处理"""
        self._add_log(f"[账号切换] {account_data.get('userid', 'N/A')}")
    
    def _on_cinema_selected(self, cinema_name):
        """影院选择事件处理"""
        self._add_log(f"[影院选择] {cinema_name}")
    
    def _on_order_created(self, order_data):
        """订单创建事件处理"""
        order_id = order_data.get('order_id', 'N/A')
        amount = order_data.get('amount', 0)
        self._add_log(f"[订单创建] {order_id} (¥{amount:.2f})")
    
    def _add_log(self, message):
        """添加日志"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        current_log = self.event_log.text()
        new_log = f"{current_log}\n[{timestamp}] {message}"
        
        # 保持日志在合理长度
        log_lines = new_log.split('\n')
        if len(log_lines) > 15:
            log_lines = log_lines[-15:]
            new_log = '\n'.join(log_lines)
        
        self.event_log.setText(new_log)


def main():
    """启动演示程序"""
    app = QApplication(sys.argv)
    
    # 创建并显示演示窗口
    window = ModularDemoWindow()
    window.show()
    
    # 启动应用
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 