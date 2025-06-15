#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试沃美影院座位图UI布局紧凑性优化
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLabel, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt
from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

def create_test_seat_data():
    """创建测试座位数据"""
    # 创建一个简单的9x17座位矩阵用于测试
    seat_matrix = []
    area_data = [
        {'area_no': '1', 'area_name': '默认区', 'area_price': 57.9},
        {'area_no': '2', 'area_name': '前排区域', 'area_price': 32.9},
        {'area_no': '3', 'area_name': '按摩区域', 'area_price': 62.9},
        {'area_no': '4', 'area_name': '中心区域', 'area_price': 62.9}
    ]
    
    for row in range(1, 10):  # 9行
        row_seats = []
        for col in range(1, 18):  # 17列
            # 根据位置分配不同区域
            if row <= 2:
                area_name = '前排区域'
                area_price = 32.9
            elif row >= 7:
                area_name = '按摩区域'
                area_price = 62.9
            elif 4 <= col <= 13:
                area_name = '中心区域'
                area_price = 62.9
            else:
                area_name = '默认区'
                area_price = 57.9
            
            # 创建座位数据
            if (row == 3 and col in [1, 2, 16, 17]) or (row == 8 and col in [8, 9, 10]):
                # 一些空位
                row_seats.append(None)
            else:
                # 随机设置一些已售座位
                if (row + col) % 7 == 0:
                    status = 'sold'
                else:
                    status = 'available'
                
                seat = {
                    'seat_no': f'R{row}C{col}',
                    'row': row,
                    'col': col,
                    'x': col,
                    'y': row,
                    'type': 0,
                    'status': status,
                    'area_name': area_name,
                    'area_price': area_price,
                    'price': area_price,
                    'num': str(col)
                }
                row_seats.append(seat)
        
        seat_matrix.append(row_seats)
    
    return seat_matrix, area_data

class QuickCompactTestWindow(QMainWindow):
    """快速紧凑布局测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院座位图紧凑布局快速测试")
        self.setGeometry(100, 100, 1000, 700)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title = QLabel("🔧 座位图紧凑布局测试")
        title.setStyleSheet("""
            QLabel {
                font: bold 16px "Microsoft YaHei";
                color: #333;
                padding: 10px;
                text-align: center;
                background-color: #f0f8ff;
                border-radius: 6px;
                margin: 5px;
            }
        """)
        layout.addWidget(title)
        
        # 优化说明
        info = QLabel("""
🎯 优化措施：
• QGridLayout间距：setSpacing(0)
• 网格边距：setContentsMargins(0,0,0,0)  
• 行列间距：setHorizontalSpacing(0), setVerticalSpacing(0)
• 按钮边距：margin: 0px, padding: 0px
• 区域颜色：中心区域改为浅绿色 #E8F5E8

✅ 预期效果：座位按钮完全紧密排列，无可见间隔
        """)
        info.setStyleSheet("""
            QLabel {
                font: 10px "Microsoft YaHei";
                color: #555;
                padding: 8px;
                background-color: #f9f9f9;
                border-radius: 4px;
                border: 1px solid #ddd;
                margin: 5px;
            }
        """)
        layout.addWidget(info)
        
        # 创建测试座位数据
        seat_matrix, area_data = create_test_seat_data()
        
        # 创建座位图组件
        self.seat_panel = SeatMapPanelPyQt5()
        self.seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
        
        layout.addWidget(self.seat_panel, 1)
        
        # 底部控制按钮
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("清空选择")
        self.clear_btn.clicked.connect(self.clear_selection)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font: bold 11px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        
        self.info_btn = QPushButton("显示信息")
        self.info_btn.clicked.connect(self.show_info)
        self.info_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font: bold 11px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.info_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        print(f"✅ 快速测试窗口创建完成")
        print(f"📊 测试数据: 9行 x 17列 = 153个位置")
        print(f"🎨 区域数量: {len(area_data)}个")
    
    def clear_selection(self):
        """清空选择"""
        self.seat_panel.clear_selection()
        print("🔄 已清空所有选择")
    
    def show_info(self):
        """显示座位信息"""
        info = self.seat_panel.get_seat_count_info()
        selected = self.seat_panel.get_selected_seats()
        
        print(f"\n📊 座位统计信息:")
        print(f"  总座位数: {info['total']}")
        print(f"  可选座位: {info['available']}")
        print(f"  已售座位: {info['sold']}")
        print(f"  已选座位: {info['selected']}")
        if selected:
            print(f"  选中座位: {', '.join(selected)}")

def main():
    """主函数"""
    print("🔧 沃美影院座位图紧凑布局快速测试")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QuickCompactTestWindow()
    window.show()
    
    print(f"\n🚀 测试窗口已启动")
    print(f"🎯 检查要点:")
    print(f"  1. 座位按钮是否紧密排列")
    print(f"  2. 是否还有可见间隔")
    print(f"  3. 区域颜色是否正确显示")
    print(f"  4. 选择功能是否正常")
    print(f"  5. 整体布局是否更紧凑")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
