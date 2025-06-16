#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示沃美影院座位图系统中逻辑位置和物理位置的区分
简化版本，用于验证核心概念
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLabel, QHBoxLayout, QPushButton, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt
from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

def create_demo_seat_data():
    """创建演示座位数据，展示逻辑位置和物理位置的区别"""
    
    # 模拟一个小型影厅，展示位置映射的概念
    demo_seats = [
        # 第一行：逻辑1排，但物理位置可能不同
        [
            {
                'seat_no': 'A01',
                'row': 1,      # 逻辑行号
                'col': 1,      # 逻辑列号
                'x': 2,        # 物理X坐标（显示位置）
                'y': 1,        # 物理Y坐标（显示位置）
                'status': 'available',
                'area_name': 'VIP区',
                'area_price': 80,
                'price': 80,
                'type': 0,
                'num': '1'
            },
            None,  # 空位，用于展示物理间隔
            {
                'seat_no': 'A02',
                'row': 1,      # 逻辑行号
                'col': 2,      # 逻辑列号
                'x': 4,        # 物理X坐标（跳过了x=3的位置）
                'y': 1,        # 物理Y坐标
                'status': 'available',
                'area_name': 'VIP区',
                'area_price': 80,
                'price': 80,
                'type': 0,
                'num': '2'
            },
            {
                'seat_no': 'A03',
                'row': 1,
                'col': 3,
                'x': 5,
                'y': 1,
                'status': 'sold',
                'area_name': 'VIP区',
                'area_price': 80,
                'price': 80,
                'type': 0,
                'num': '3'
            }
        ],
        # 第二行：逻辑2排
        [
            {
                'seat_no': 'B01',
                'row': 2,      # 逻辑行号
                'col': 1,      # 逻辑列号
                'x': 1,        # 物理X坐标（与逻辑位置不同）
                'y': 2,        # 物理Y坐标
                'status': 'available',
                'area_name': '普通区',
                'area_price': 50,
                'price': 50,
                'type': 0,
                'num': '1'
            },
            {
                'seat_no': 'B02',
                'row': 2,
                'col': 2,
                'x': 2,
                'y': 2,
                'status': 'available',
                'area_name': '普通区',
                'area_price': 50,
                'price': 50,
                'type': 0,
                'num': '2'
            },
            {
                'seat_no': 'B03',
                'row': 2,
                'col': 3,
                'x': 3,
                'y': 2,
                'status': 'available',
                'area_name': '普通区',
                'area_price': 50,
                'price': 50,
                'type': 0,
                'num': '3'
            },
            {
                'seat_no': 'B04',
                'row': 2,
                'col': 4,
                'x': 4,
                'y': 2,
                'status': 'available',
                'area_name': '普通区',
                'area_price': 50,
                'price': 50,
                'type': 0,
                'num': '4'
            },
            {
                'seat_no': 'B05',
                'row': 2,
                'col': 5,
                'x': 5,
                'y': 2,
                'status': 'available',
                'area_name': '普通区',
                'area_price': 50,
                'price': 50,
                'type': 0,
                'num': '5'
            }
        ],
        # 第三行：逻辑3排，展示更复杂的映射
        [
            None,  # 空位
            {
                'seat_no': 'C01',
                'row': 3,      # 逻辑行号
                'col': 1,      # 逻辑列号（注意：这是第1座，但在数组的第2个位置）
                'x': 2,        # 物理X坐标
                'y': 3,        # 物理Y坐标
                'status': 'available',
                'area_name': '经济区',
                'area_price': 30,
                'price': 30,
                'type': 0,
                'num': '1'
            },
            {
                'seat_no': 'C02',
                'row': 3,
                'col': 2,
                'x': 3,
                'y': 3,
                'status': 'available',
                'area_name': '经济区',
                'area_price': 30,
                'price': 30,
                'type': 0,
                'num': '2'
            },
            {
                'seat_no': 'C03',
                'row': 3,
                'col': 3,
                'x': 4,
                'y': 3,
                'status': 'available',
                'area_name': '经济区',
                'area_price': 30,
                'price': 30,
                'type': 0,
                'num': '3'
            },
            None   # 空位
        ]
    ]
    
    # 区域数据
    area_data = [
        {'area_name': 'VIP区', 'area_price': 80},
        {'area_name': '普通区', 'area_price': 50},
        {'area_name': '经济区', 'area_price': 30}
    ]
    
    return demo_seats, area_data

class PositionMappingDemo(QMainWindow):
    """位置映射演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("座位位置映射演示 - 逻辑位置 vs 物理位置")
        self.setGeometry(100, 100, 1400, 800)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加说明
        self.create_explanation(layout)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：座位图
        seat_data, area_data = create_demo_seat_data()
        self.seat_panel = SeatMapPanelPyQt5()
        self.seat_panel.update_seat_data_with_areas(seat_data, area_data)
        self.seat_panel.seat_selected.connect(self.on_seat_selection_changed)
        
        splitter.addWidget(self.seat_panel)
        
        # 右侧：信息面板
        self.create_info_panel(splitter)
        
        layout.addWidget(splitter)
        
        # 初始化信息显示
        self.update_info_display()
        
        print(f"✅ 位置映射演示窗口创建完成")
    
    def create_explanation(self, layout):
        """创建说明区域"""
        explanation = QLabel("""
🗺️ 座位位置映射演示

本演示展示了沃美影院系统中两种不同的座位位置概念：

1. 逻辑位置 (row, col)：用于订单提交的座位标识，如"2排3座"
2. 物理位置 (x, y)：用于座位图显示的实际坐标，确定按钮在网格中的位置

请选择座位观察两种位置的区别。注意有些位置会有空隙，这是通过物理坐标实现的真实影厅布局。
        """)
        explanation.setStyleSheet("""
            QLabel {
                font: 11px "Microsoft YaHei";
                color: #333;
                padding: 10px;
                background-color: #f0f8ff;
                border-radius: 6px;
                margin: 5px;
                border: 1px solid #ddd;
            }
        """)
        layout.addWidget(explanation)
    
    def create_info_panel(self, splitter):
        """创建信息面板"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # 信息标题
        info_title = QLabel("📊 位置信息")
        info_title.setStyleSheet("""
            QLabel {
                font: bold 14px "Microsoft YaHei";
                color: #333;
                padding: 8px 0 4px 0;
            }
        """)
        info_layout.addWidget(info_title)
        
        # 信息显示
        self.info_text = QTextEdit()
        self.info_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Consolas";
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        info_layout.addWidget(self.info_text)
        
        # 控制按钮
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
        
        self.test_order_btn = QPushButton("测试订单数据")
        self.test_order_btn.clicked.connect(self.test_order_data)
        self.test_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font: bold 11px "Microsoft YaHei";
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.test_order_btn)
        info_layout.addLayout(button_layout)
        
        splitter.addWidget(info_widget)
    
    def update_info_display(self):
        """更新信息显示"""
        info_lines = []
        info_lines.append("🗺️ 座位布局分析")
        info_lines.append("=" * 40)
        info_lines.append("")
        
        # 分析座位数据
        seat_data, _ = create_demo_seat_data()
        
        info_lines.append("📍 座位位置映射:")
        for row_idx, row in enumerate(seat_data):
            for col_idx, seat in enumerate(row):
                if seat:
                    logical_pos = f"({seat['row']}, {seat['col']})"
                    physical_pos = f"({seat['y']}, {seat['x']})"
                    mapping_diff = "❗" if (seat['row'] != seat['y'] or seat['col'] != seat['x']) else "✓"
                    
                    info_lines.append(f"  {seat['seat_no']}: 逻辑{logical_pos} → 物理{physical_pos} {mapping_diff}")
        
        info_lines.append("")
        info_lines.append("💡 说明:")
        info_lines.append("  ✓ = 逻辑位置与物理位置一致")
        info_lines.append("  ❗ = 逻辑位置与物理位置不同")
        info_lines.append("")
        info_lines.append("🎯 选择座位查看详细信息...")
        
        self.info_text.clear()
        self.info_text.append("\n".join(info_lines))
    
    def on_seat_selection_changed(self, selected_seats):
        """座位选择变化处理"""
        if selected_seats:
            selection_info = []
            selection_info.append("\n🎯 选中座位详情:")
            selection_info.append("-" * 30)
            
            for seat in selected_seats:
                logical_row = seat.get('logical_row', seat.get('row', '?'))
                logical_col = seat.get('logical_col', seat.get('col', '?'))
                physical_x = seat.get('physical_x', seat.get('x', '?'))
                physical_y = seat.get('physical_y', seat.get('y', '?'))
                area_name = seat.get('area_name', '未知')
                price = seat.get('price', 0)
                
                selection_info.append(f"座位: {seat.get('seat_no', '?')} - {logical_row}排{logical_col}座")
                selection_info.append(f"  逻辑位置: ({logical_row}, {logical_col}) ← 用于订单")
                selection_info.append(f"  物理位置: ({physical_y}, {physical_x}) ← 用于显示")
                selection_info.append(f"  区域: {area_name}, 价格: {price}元")
                selection_info.append("")
            
            self.info_text.append("\n".join(selection_info))
    
    def test_order_data(self):
        """测试订单数据"""
        order_seats = self.seat_panel.get_selected_seats_for_order()
        
        order_info = []
        order_info.append("\n📋 订单数据测试:")
        order_info.append("-" * 30)
        
        if order_seats:
            order_info.append("✅ 订单座位信息（使用逻辑位置）:")
            for seat in order_seats:
                order_info.append(f"  {seat['row']}排{seat['col']}座")
                order_info.append(f"    座位号: {seat['seat_no']}")
                order_info.append(f"    区域: {seat['area_name']}")
                order_info.append(f"    价格: {seat['price']}元")
                order_info.append("")
            
            total_price = sum(seat['price'] for seat in order_seats)
            order_info.append(f"💰 总价: {total_price}元")
        else:
            order_info.append("❌ 请先选择座位")
        
        self.info_text.append("\n".join(order_info))
    
    def clear_selection(self):
        """清空选择"""
        self.seat_panel.clear_selection()
        self.update_info_display()

def main():
    """主函数"""
    print("🗺️ 座位位置映射演示")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # 创建演示窗口
    window = PositionMappingDemo()
    window.show()
    
    print(f"\n🚀 演示窗口已启动")
    print(f"🎯 演示重点:")
    print(f"  1. 逻辑位置 (row, col) - 用于订单提交")
    print(f"  2. 物理位置 (x, y) - 用于座位图显示")
    print(f"  3. 两种位置的自动转换和映射")
    print(f"  4. 真实影厅布局的还原")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
