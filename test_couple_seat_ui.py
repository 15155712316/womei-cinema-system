#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情侣座位UI测试脚本
创建一个简单的测试界面来验证情侣座位功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

class CoupleSeatTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("情侣座位功能测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("🎬 沃美电影票务系统 - 情侣座位功能测试")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 添加说明
        info_label = QLabel("💕 测试说明：点击情侣座位时，系统会自动选择相邻的两个座位")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 5px;")
        layout.addWidget(info_label)
        
        # 创建座位面板
        self.seat_panel = SeatMapPanelPyQt5()
        layout.addWidget(self.seat_panel)
        
        # 添加测试按钮
        test_button = QPushButton("加载测试座位数据（包含情侣座位）")
        test_button.clicked.connect(self.load_test_data)
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #e91e63;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #ad1457;
            }
        """)
        layout.addWidget(test_button)
        
        # 连接座位选择信号
        self.seat_panel.seat_selected.connect(self.on_seat_selected)
        
    def load_test_data(self):
        """加载包含情侣座位的测试数据"""
        # 创建测试座位矩阵（5行10列）
        test_seat_matrix = []
        
        for row in range(5):
            seat_row = []
            for col in range(10):
                if row == 2 and col in [3, 4]:  # 第3排第4、5座设为情侣座
                    # 情侣座位
                    seat_type = 1 if col == 3 else 2  # 左座=1，右座=2
                    seat = {
                        'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                        'row': row + 1,
                        'col': col + 1,
                        'x': col + 1,
                        'y': row + 1,
                        'type': seat_type,
                        'status': 'available',
                        'area_name': '情侣座区域',
                        'area_price': 88.0,
                        'price': 88.0,
                        'num': str(col + 1),
                        'original_data': {
                            'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                            'area_no': '10001',
                            'row': str(row + 1),
                            'col': str(col + 1),
                            'type': seat_type,
                            'status': 0
                        }
                    }
                elif row == 2 and col in [6, 7]:  # 第3排第7、8座也设为情侣座
                    # 另一对情侣座位
                    seat_type = 1 if col == 6 else 2  # 左座=1，右座=2
                    seat = {
                        'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                        'row': row + 1,
                        'col': col + 1,
                        'x': col + 1,
                        'y': row + 1,
                        'type': seat_type,
                        'status': 'available',
                        'area_name': '情侣座区域',
                        'area_price': 88.0,
                        'price': 88.0,
                        'num': str(col + 1),
                        'original_data': {
                            'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                            'area_no': '10001',
                            'row': str(row + 1),
                            'col': str(col + 1),
                            'type': seat_type,
                            'status': 0
                        }
                    }
                else:
                    # 普通座位
                    seat = {
                        'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                        'row': row + 1,
                        'col': col + 1,
                        'x': col + 1,
                        'y': row + 1,
                        'type': 0,
                        'status': 'available',
                        'area_name': '普通区域',
                        'area_price': 58.0,
                        'price': 58.0,
                        'num': str(col + 1),
                        'original_data': {
                            'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                            'area_no': '10002',
                            'row': str(row + 1),
                            'col': str(col + 1),
                            'type': 0,
                            'status': 0
                        }
                    }
                
                seat_row.append(seat)
            test_seat_matrix.append(seat_row)
        
        # 创建区域数据
        area_data = [
            {
                'area_no': '10001',
                'area_name': '情侣座区域',
                'area_price': 88.0,
                'color': '#e91e63'
            },
            {
                'area_no': '10002',
                'area_name': '普通区域',
                'area_price': 58.0,
                'color': '#2196f3'
            }
        ]
        
        # 更新座位面板
        self.seat_panel.update_seat_data_with_areas(test_seat_matrix, area_data)
        
        QMessageBox.information(self, "测试数据加载", 
                              "✅ 测试数据已加载！\n\n"
                              "💕 第3排第4、5座：情侣座位\n"
                              "💕 第3排第7、8座：情侣座位\n"
                              "🪑 其他座位：普通座位\n\n"
                              "请点击情侣座位测试自动连选功能！")
    
    def on_seat_selected(self, selected_seats):
        """座位选择回调"""
        if not selected_seats:
            print("🔄 所有座位已取消选择")
            return
        
        print(f"\n📋 当前选中座位: {len(selected_seats)} 个")
        
        couple_seats = []
        normal_seats = []
        
        for seat in selected_seats:
            seat_type = seat.get('type', 0)
            row = seat.get('row', 0)
            col = seat.get('col', 0)
            
            if seat_type in [1, 2]:
                couple_type = "左座" if seat_type == 1 else "右座"
                couple_seats.append(f"{row}排{col}座({couple_type})")
                print(f"  💕 情侣座位: {row}排{col}座 ({couple_type})")
            else:
                normal_seats.append(f"{row}排{col}座")
                print(f"  🪑 普通座位: {row}排{col}座")
        
        # 计算总价
        total_price = sum(seat.get('price', 0) for seat in selected_seats)
        print(f"💰 总价: ¥{total_price}")
        
        # 检查情侣座位是否成对
        if couple_seats:
            if len(couple_seats) % 2 == 0:
                print("✅ 情侣座位配对正确")
            else:
                print("⚠️ 情侣座位配对异常")

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
        }
    """)
    
    window = CoupleSeatTestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
