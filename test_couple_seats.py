#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情侣座位显示效果测试
测试不同类型座位的视觉效果
"""

import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class CoupleSeatsTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("情侣座位显示效果测试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title = QLabel("情侣座位显示效果对比")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 创建座位展示区域
        self.create_seat_demo(layout)
        
    def create_seat_demo(self, layout):
        """创建座位展示区域"""
        
        # 普通座位展示
        normal_label = QLabel("普通座位 (type: 0)")
        normal_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(normal_label)
        
        normal_layout = QHBoxLayout()
        for i in range(5):
            btn = self.create_seat_button(f"{i+1}", 0, "available")
            normal_layout.addWidget(btn)
        layout.addLayout(normal_layout)
        
        # 情侣座位展示
        couple_label = QLabel("情侣座位 (type: 1, 2)")
        couple_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(couple_label)
        
        couple_layout = QHBoxLayout()
        # 情侣座位对1
        btn1 = self.create_seat_button("1", 1, "available")
        btn2 = self.create_seat_button("2", 2, "available")
        couple_layout.addWidget(btn1)
        couple_layout.addWidget(btn2)
        
        # 间隔
        couple_layout.addSpacing(20)
        
        # 情侣座位对2
        btn3 = self.create_seat_button("3", 1, "available")
        btn4 = self.create_seat_button("4", 2, "available")
        couple_layout.addWidget(btn3)
        couple_layout.addWidget(btn4)
        
        layout.addLayout(couple_layout)
        
        # 选中状态的情侣座位
        selected_label = QLabel("选中状态的情侣座位")
        selected_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(selected_label)
        
        selected_layout = QHBoxLayout()
        btn5 = self.create_seat_button("5", 1, "selected")
        btn6 = self.create_seat_button("6", 2, "selected")
        selected_layout.addWidget(btn5)
        selected_layout.addWidget(btn6)
        layout.addLayout(selected_layout)
        
        # 已售状态的情侣座位
        sold_label = QLabel("已售状态的情侣座位")
        sold_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        layout.addWidget(sold_label)
        
        sold_layout = QHBoxLayout()
        btn7 = self.create_seat_button("7", 1, "sold")
        btn8 = self.create_seat_button("8", 2, "sold")
        sold_layout.addWidget(btn7)
        sold_layout.addWidget(btn8)
        layout.addLayout(sold_layout)
        
    def create_seat_button(self, text, seat_type, status):
        """创建座位按钮"""
        button = QPushButton(text)
        
        # 根据座位类型设置尺寸
        if seat_type in [1, 2]:
            button.setFixedSize(40, 36)  # 情侣座位更宽
        else:
            button.setFixedSize(36, 36)  # 普通座位
            
        # 应用样式
        self._update_seat_button_style(button, status, "", seat_type)
        
        return button
        
    def _update_seat_button_style(self, button: QPushButton, status: str, area_name: str = '', seat_type: int = 0):
        """更新座位按钮样式 - 支持情侣座位"""
        # 检查是否为情侣座位
        is_couple_seat = seat_type in [1, 2]
        couple_left = seat_type == 1
        couple_right = seat_type == 2
        
        # 情侣座位的特殊边框样式
        if is_couple_seat:
            if couple_left:
                # 情侣座位左座 - 右边圆角较小，与右座连接
                border_radius = "6px 2px 2px 6px"
            else:  # couple_right
                # 情侣座位右座 - 左边圆角较小，与左座连接
                border_radius = "2px 6px 6px 2px"
        else:
            border_radius = "6px"

        if status == "available":
            if is_couple_seat:
                # 情侣座位可选 - 特殊的粉色系
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #fce4ec;
                        border: 2px solid #e91e63;
                        color: #ad1457;
                        font: bold 9px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                    QPushButton:hover {{
                        background-color: #f8bbd9;
                        border: 2px solid #e91e63;
                    }}
                    QPushButton:pressed {{
                        background-color: #f48fb1;
                        border: 2px solid #e91e63;
                    }}
                """)
            else:
                # 普通座位可选 - 清新的蓝色
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e3f2fd;
                        border: 2px solid #2196f3;
                        color: #1976d2;
                        font: bold 10px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                    QPushButton:hover {{
                        background-color: #bbdefb;
                        border: 2px solid #2196f3;
                    }}
                    QPushButton:pressed {{
                        background-color: #90caf9;
                        border: 2px solid #2196f3;
                    }}
                """)
        elif status == "sold":
            # 已售座位 - 明显的红色
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f44336;
                    border: 2px solid #d32f2f;
                    color: #ffffff;
                    font: bold 10px "Microsoft YaHei";
                    border-radius: {border_radius};
                }}
            """)
        elif status == "selected":
            if is_couple_seat:
                # 情侣座位选中 - 特殊的深粉色
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e91e63;
                        border: 2px solid #ad1457;
                        color: #fff;
                        font: bold 9px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                """)
            else:
                # 普通座位选中 - 鲜明的绿色
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #4caf50;
                        border: 2px solid #388e3c;
                        color: #fff;
                        font: bold 10px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoupleSeatsTestWindow()
    window.show()
    sys.exit(app.exec_())
