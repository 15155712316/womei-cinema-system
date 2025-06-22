#!/usr/bin/env python3
"""
PySide6 测试示例
验证 PySide6 安装是否成功并展示基本功能
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 测试窗口")
        self.setGeometry(100, 100, 400, 300)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题标签
        title_label = QLabel("PySide6 安装验证成功！")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # 添加信息标签
        info_label = QLabel(f"PySide6 版本: 6.9.1\n系统: macOS\nPython: {sys.version}")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 添加按钮
        test_button = QPushButton("点击测试")
        test_button.clicked.connect(self.on_button_clicked)
        layout.addWidget(test_button)
        
        # 添加文本区域
        self.text_area = QTextEdit()
        self.text_area.setPlainText("PySide6 功能测试:\n- GUI 窗口 ✓\n- 布局管理 ✓\n- 事件处理 ✓\n- 中文显示 ✓")
        layout.addWidget(self.text_area)
        
        # 设置定时器测试
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每秒更新
        
        self.click_count = 0
    
    def on_button_clicked(self):
        self.click_count += 1
        self.text_area.append(f"按钮被点击了 {self.click_count} 次")
    
    def update_time(self):
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.setWindowTitle(f"PySide6 测试窗口 - {current_time}")

def main():
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = TestWindow()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
