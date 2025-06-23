#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位状态视觉效果测试
验证所有座位状态的视觉设计和交互效果
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

class SeatStatusVisualTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("座位状态视觉效果测试")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("🎬 沃美电影票务系统 - 座位状态视觉效果测试")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 添加状态说明
        status_layout = QHBoxLayout()
        
        status_info = [
            ("🟢 可选座位", "status: 0 - 蓝色主题，可点击"),
            ("🔴 已售座位", "status: 1 - 红色，不可点击"),
            ("🔒 锁定座位", "status: 2 - 橙色，不可点击"),
            ("🚫 不可选择", "status: 6 - 浅灰色，禁止光标")
        ]
        
        for status_text, desc in status_info:
            status_label = QLabel(f"{status_text}\n{desc}")
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    padding: 8px;
                    margin: 5px;
                    font-size: 12px;
                }
            """)
            status_layout.addWidget(status_label)
        
        layout.addLayout(status_layout)
        
        # 创建座位面板
        self.seat_panel = SeatMapPanelPyQt5()
        layout.addWidget(self.seat_panel)
        
        # 添加控制按钮
        button_layout = QHBoxLayout()
        
        load_button = QPushButton("加载测试数据")
        load_button.clicked.connect(self.load_test_data)
        load_button.setStyleSheet(self.get_button_style("#2196f3"))
        button_layout.addWidget(load_button)
        
        stats_button = QPushButton("显示座位统计")
        stats_button.clicked.connect(self.show_statistics)
        stats_button.setStyleSheet(self.get_button_style("#4caf50"))
        button_layout.addWidget(stats_button)
        
        reset_button = QPushButton("重置选择")
        reset_button.clicked.connect(self.reset_selection)
        reset_button.setStyleSheet(self.get_button_style("#ff9800"))
        button_layout.addWidget(reset_button)
        
        layout.addLayout(button_layout)
        
        # 连接座位选择信号
        self.seat_panel.seat_selected.connect(self.on_seat_selected)
        
    def get_button_style(self, color):
        """获取按钮样式"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin: 5px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """
        
    def load_test_data(self):
        """加载包含所有状态的测试数据"""
        # 创建测试座位矩阵（6行12列）
        test_seat_matrix = []
        
        # 状态分布设计
        status_patterns = [
            # 第1排：展示所有状态
            [6, 6, 0, 0, 1, 1, 2, 2, 0, 0, 6, 6],
            # 第2排：主要可选，少量其他状态
            [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            # 第3排：情侣座位 + 不可选择
            [0, 1, 1, 0, 0, 6, 6, 0, 0, 2, 2, 0],
            # 第4排：混合状态
            [6, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 6],
            # 第5排：主要可选
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            # 第6排：边缘不可选择
            [6, 6, 0, 0, 0, 0, 0, 0, 0, 0, 6, 6]
        ]
        
        for row in range(6):
            seat_row = []
            for col in range(12):
                status_code = status_patterns[row][col]
                
                # 状态映射
                if status_code == 0:
                    seat_status = 'available'
                elif status_code == 1:
                    seat_status = 'sold'
                elif status_code == 2:
                    seat_status = 'locked'
                elif status_code == 6:
                    seat_status = 'unavailable'
                else:
                    seat_status = 'available'
                
                # 设置情侣座位（第3排第4、5座）
                seat_type = 0
                if row == 2 and col == 3:  # 情侣座左座
                    seat_type = 1
                elif row == 2 and col == 4:  # 情侣座右座
                    seat_type = 2
                
                seat = {
                    'seat_no': f'VISUAL#{row+1:02d}#{col+1:02d}',
                    'row': row + 1,
                    'col': col + 1,
                    'x': col + 1,
                    'y': row + 1,
                    'type': seat_type,
                    'status': seat_status,
                    'area_name': '视觉测试区域',
                    'area_price': 68.0,
                    'price': 68.0,
                    'num': str(col + 1),
                    'original_data': {
                        'seat_no': f'VISUAL#{row+1:02d}#{col+1:02d}',
                        'area_no': '10001',
                        'row': str(row + 1),
                        'col': str(col + 1),
                        'type': seat_type,
                        'status': status_code
                    }
                }
                
                seat_row.append(seat)
            test_seat_matrix.append(seat_row)
        
        # 创建区域数据
        area_data = [
            {
                'area_no': '10001',
                'area_name': '视觉测试区域',
                'area_price': 68.0,
                'color': '#2196f3'
            }
        ]
        
        # 更新座位面板
        self.seat_panel.update_seat_data_with_areas(test_seat_matrix, area_data)
        
        QMessageBox.information(self, "测试数据加载", 
                              "✅ 视觉测试数据已加载！\n\n"
                              "📋 测试内容：\n"
                              "• 第1排：展示所有状态类型\n"
                              "• 第3排：包含情侣座位\n"
                              "• 各种状态混合分布\n\n"
                              "🎯 测试重点：\n"
                              "• 🚫 不可选择座位的视觉效果\n"
                              "• 各状态间的视觉区分度\n"
                              "• 点击交互的正确性\n\n"
                              "请尝试点击不同状态的座位！")
    
    def show_statistics(self):
        """显示座位统计信息"""
        stats = self.seat_panel.get_seat_statistics()
        
        QMessageBox.information(self, "座位统计", 
                              f"📊 当前座位统计：\n\n"
                              f"🎫 总座位数：{stats['total']}\n"
                              f"🟢 可选座位：{stats['available']}\n"
                              f"🔴 已售座位：{stats['sold']}\n"
                              f"🔒 锁定座位：{stats['locked']}\n"
                              f"🚫 不可选择：{stats['unavailable']}\n"
                              f"✅ 已选座位：{stats['selected']}\n\n"
                              f"💡 可选率：{stats['available']/(stats['total']-stats['unavailable'])*100:.1f}%")
    
    def reset_selection(self):
        """重置座位选择"""
        self.seat_panel.reset_seat_selection()
        QMessageBox.information(self, "重置完成", "✅ 座位选择已重置！")
    
    def on_seat_selected(self, selected_seats):
        """座位选择回调"""
        if not selected_seats:
            print("🔄 所有座位已取消选择")
            return
        
        print(f"\n📋 当前选中座位: {len(selected_seats)} 个")
        
        for seat in selected_seats:
            row = seat.get('row', 0)
            col = seat.get('col', 0)
            status = seat.get('status', 'unknown')
            seat_type = seat.get('type', 0)
            type_desc = "情侣座" if seat_type in [1, 2] else "普通座"
            print(f"  🪑 {row}排{col}座 ({type_desc}, 状态: {status})")
        
        # 计算总价
        total_price = sum(seat.get('price', 0) for seat in selected_seats)
        print(f"💰 总价: ¥{total_price}")

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
    
    window = SeatStatusVisualTestWindow()
    window.show()
    
    print("🎬 座位状态视觉效果测试程序启动")
    print("=" * 50)
    print("📋 测试项目：")
    print("1. status: 0 (可选) - 蓝色主题")
    print("2. status: 1 (已售) - 红色主题")
    print("3. status: 2 (锁定) - 橙色主题")
    print("4. status: 6 (不可选择) - 浅灰色 + 🚫符号")
    print("5. 情侣座位 - 粉色主题 + 💕符号")
    print("=" * 50)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
