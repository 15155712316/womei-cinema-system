#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 status: 6 座位处理功能
验证不可选择座位的识别、样式和交互禁用
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

class Status6TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Status 6 座位测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("🎬 沃美电影票务系统 - Status 6 座位测试")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 添加说明
        info_label = QLabel("🚫 测试说明：status: 6 的座位应该显示为深灰色且完全不可点击")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; margin: 5px;")
        layout.addWidget(info_label)
        
        # 创建座位面板
        self.seat_panel = SeatMapPanelPyQt5()
        layout.addWidget(self.seat_panel)
        
        # 添加测试按钮
        test_button = QPushButton("加载测试数据（包含 status: 6 座位）")
        test_button.clicked.connect(self.load_test_data)
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        layout.addWidget(test_button)
        
        # 连接座位选择信号
        self.seat_panel.seat_selected.connect(self.on_seat_selected)
        
    def load_test_data(self):
        """加载包含 status: 6 座位的测试数据"""
        # 创建测试座位矩阵（5行10列）
        test_seat_matrix = []
        
        for row in range(5):
            seat_row = []
            for col in range(10):
                # 设置不同的座位状态进行测试
                if row == 0 and col in [2, 3, 4]:  # 第1排第3、4、5座设为 status: 6
                    seat_status = 'unavailable'
                    status_code = 6
                elif row == 1 and col in [1, 8]:  # 第2排第2、9座设为已售
                    seat_status = 'sold'
                    status_code = 1
                elif row == 2 and col in [0, 9]:  # 第3排第1、10座设为锁定
                    seat_status = 'locked'
                    status_code = 2
                else:
                    seat_status = 'available'
                    status_code = 0
                
                seat = {
                    'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                    'row': row + 1,
                    'col': col + 1,
                    'x': col + 1,
                    'y': row + 1,
                    'type': 0,  # 普通座位
                    'status': seat_status,
                    'area_name': '测试区域',
                    'area_price': 58.0,
                    'price': 58.0,
                    'num': str(col + 1),
                    'original_data': {
                        'seat_no': f'TEST#{row+1:02d}#{col+1:02d}',
                        'area_no': '10001',
                        'row': str(row + 1),
                        'col': str(col + 1),
                        'type': 0,
                        'status': status_code
                    }
                }
                
                seat_row.append(seat)
            test_seat_matrix.append(seat_row)
        
        # 创建区域数据
        area_data = [
            {
                'area_no': '10001',
                'area_name': '测试区域',
                'area_price': 58.0,
                'color': '#2196f3'
            }
        ]
        
        # 更新座位面板
        self.seat_panel.update_seat_data_with_areas(test_seat_matrix, area_data)
        
        # 获取座位统计
        stats = self.seat_panel.get_seat_statistics()
        
        QMessageBox.information(self, "测试数据加载", 
                              f"✅ 测试数据已加载！\n\n"
                              f"📊 座位统计：\n"
                              f"• 总座位数：{stats['total']}\n"
                              f"• 可选座位：{stats['available']}\n"
                              f"• 已售座位：{stats['sold']}\n"
                              f"• 不可选择座位：{stats['unavailable']}\n"
                              f"• 锁定座位：{stats['locked']}\n\n"
                              f"🚫 第1排第3、4、5座：status: 6 (不可选择)\n"
                              f"🔴 第2排第2、9座：status: 1 (已售)\n"
                              f"🔒 第3排第1、10座：status: 2 (锁定)\n"
                              f"🟢 其他座位：status: 0 (可选)\n\n"
                              f"请尝试点击不同状态的座位测试交互！")
    
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
            print(f"  🪑 座位: {row}排{col}座 (状态: {status})")
        
        # 计算总价
        total_price = sum(seat.get('price', 0) for seat in selected_seats)
        print(f"💰 总价: ¥{total_price}")

def test_status_mapping():
    """测试状态映射逻辑"""
    print("🧪 测试状态映射逻辑")
    print("=" * 50)
    
    # 模拟状态映射
    test_statuses = [0, 1, 2, 6, 99]
    
    for status_code in test_statuses:
        if status_code == 0:
            status = 'available'
            desc = "可选"
        elif status_code == 1:
            status = 'sold'
            desc = "已售"
        elif status_code == 2:
            status = 'locked'
            desc = "锁定"
        elif status_code == 6:
            status = 'unavailable'
            desc = "不可选择"
        else:
            status = 'available'
            desc = f"未知状态({status_code})->默认可选"
        
        print(f"状态码 {status_code} -> {status} ({desc})")
    
    print("✅ 状态映射测试完成")

def main():
    # 先运行状态映射测试
    test_status_mapping()
    print()
    
    # 启动UI测试
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
    
    window = Status6TestWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
