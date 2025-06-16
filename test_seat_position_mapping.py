#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院座位图系统中逻辑位置和物理位置的区分
验证座位显示位置和订单位置的正确映射
"""

import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLabel, QHBoxLayout, QPushButton, QTextEdit, QSplitter
)
from PyQt5.QtCore import Qt
from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5

def load_test_data():
    """加载测试数据"""
    try:
        with open('real_seat_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        hall_data = data['data']
        room_seat = hall_data['room_seat']
        
        print(f"✅ 加载测试数据成功")
        print(f"影厅: {hall_data['hall_name']}")
        print(f"区域数量: {len(room_seat)}")
        
        return room_seat
    except Exception as e:
        print(f"❌ 加载测试数据失败: {e}")
        return None

def parse_test_seat_data(room_seat):
    """解析测试座位数据，分析逻辑位置和物理位置的映射"""
    try:
        print(f"\n🔍 解析座位数据:")
        
        # 收集所有座位和区域信息
        all_seats = []
        area_data = []
        position_analysis = []
        
        for area_index, area in enumerate(room_seat):
            area_name = area.get('area_name', '未知区域')
            area_price = area.get('area_price', 0)
            area_no = area.get('area_no', str(area_index + 1))
            seats_data = area.get('seats', {})
            
            print(f"  区域 {area_index + 1}: {area_name}, 价格: {area_price}元")
            
            # 收集区域信息
            area_info = {
                'area_no': area_no,
                'area_name': area_name,
                'area_price': area_price
            }
            area_data.append(area_info)
            
            # 处理座位数据，分析位置映射
            if isinstance(seats_data, dict):
                for row_key, row_data in seats_data.items():
                    seat_details = row_data.get('detail', [])
                    row_num = row_data.get('row', int(row_key))
                    
                    for seat_detail in seat_details:
                        # 分析位置映射
                        logical_row = seat_detail.get('row', row_num)
                        logical_col = seat_detail.get('col', 1)
                        physical_x = seat_detail.get('x', logical_col)
                        physical_y = seat_detail.get('y', logical_row)
                        
                        position_info = {
                            'seat_no': seat_detail.get('seat_no', ''),
                            'logical_row': logical_row,
                            'logical_col': logical_col,
                            'physical_x': physical_x,
                            'physical_y': physical_y,
                            'area_name': area_name,
                            'mapping_diff': (logical_row != physical_y) or (logical_col != physical_x)
                        }
                        position_analysis.append(position_info)
                        
                        seat = process_seat_detail(seat_detail, area_name, area_price, row_num)
                        if seat:
                            all_seats.append(seat)
        
        # 构建座位矩阵（基于数组索引）
        max_row = max(len(room_seat[0]['seats']) if room_seat else 0, 10)
        max_col = max(len(list(room_seat[0]['seats'].values())[0]['detail']) if room_seat else 0, 17)
        
        seat_matrix = []
        seat_index = 0
        for row in range(max_row):
            row_seats = []
            for col in range(max_col):
                if seat_index < len(all_seats):
                    row_seats.append(all_seats[seat_index])
                    seat_index += 1
                else:
                    row_seats.append(None)
            seat_matrix.append(row_seats)
        
        print(f"✅ 座位数据解析完成:")
        print(f"  总座位数: {len(all_seats)}")
        print(f"  矩阵尺寸: {len(seat_matrix)} 行 x {max_col} 列")
        print(f"  区域数量: {len(area_data)}")
        
        # 分析位置映射差异
        mapping_diff_count = sum(1 for p in position_analysis if p['mapping_diff'])
        print(f"  位置映射差异: {mapping_diff_count}/{len(position_analysis)} 个座位")
        
        return seat_matrix, area_data, position_analysis
        
    except Exception as e:
        print(f"❌ 解析座位数据失败: {e}")
        import traceback
        traceback.print_exc()
        return [], [], []

def process_seat_detail(seat_detail, area_name, area_price, row_num=None):
    """处理单个座位详情"""
    try:
        seat_status = seat_detail.get('status', 0)
        seat_no = seat_detail.get('seat_no', '')
        seat_row = int(seat_detail.get('row', row_num or 1))
        seat_col = int(seat_detail.get('col', 1))
        
        # 状态映射
        if seat_status == 0:
            status = 'available'
        elif seat_status == 1:
            status = 'sold'
        elif seat_status == 2:
            status = 'locked'
        else:
            status = 'available'
        
        seat = {
            'seat_no': seat_no,
            'row': seat_row,
            'col': seat_col,
            'x': seat_detail.get('x', 1),
            'y': seat_detail.get('y', row_num or 1),
            'type': seat_detail.get('type', 0),
            'status': status,
            'area_name': area_name,
            'area_price': area_price,
            'price': area_price,
            'num': str(seat_detail.get('col', 1))
        }
        
        return seat
        
    except Exception as e:
        print(f"处理座位详情错误: {e}")
        return None

class SeatPositionTestWindow(QMainWindow):
    """座位位置映射测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院座位位置映射测试")
        self.setGeometry(100, 100, 1600, 900)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        self.create_header(layout)
        
        # 加载测试数据
        room_seat = load_test_data()
        if not room_seat:
            print("❌ 无法加载测试数据")
            return
        
        # 解析座位数据
        seat_matrix, area_data, position_analysis = parse_test_seat_data(room_seat)
        if not seat_matrix:
            print("❌ 无法解析座位数据")
            return
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：座位图
        self.seat_panel = SeatMapPanelPyQt5()
        self.seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
        self.seat_panel.seat_selected.connect(self.on_seat_selection_changed)
        
        splitter.addWidget(self.seat_panel)
        
        # 右侧：分析面板
        self.create_analysis_panel(splitter, position_analysis)
        
        layout.addWidget(splitter)
        
        self.position_analysis = position_analysis
        
        print(f"✅ 座位位置映射测试窗口创建完成")
    
    def create_header(self, layout):
        """创建标题区域"""
        title = QLabel("🗺️ 座位位置映射测试 - 逻辑位置 vs 物理位置")
        title.setStyleSheet("""
            QLabel {
                font: bold 16px "Microsoft YaHei";
                color: #333;
                padding: 10px;
                background-color: #f0f8ff;
                border-radius: 6px;
                margin: 5px;
            }
        """)
        layout.addWidget(title)
    
    def create_analysis_panel(self, splitter, position_analysis):
        """创建分析面板"""
        analysis_widget = QWidget()
        analysis_layout = QVBoxLayout(analysis_widget)
        
        # 分析标题
        analysis_title = QLabel("📊 位置映射分析")
        analysis_title.setStyleSheet("""
            QLabel {
                font: bold 14px "Microsoft YaHei";
                color: #333;
                padding: 8px 0 4px 0;
            }
        """)
        analysis_layout.addWidget(analysis_title)
        
        # 分析结果显示
        self.analysis_text = QTextEdit()
        self.analysis_text.setStyleSheet("""
            QTextEdit {
                font: 9px "Consolas";
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        analysis_layout.addWidget(self.analysis_text)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("分析位置映射")
        self.analyze_btn.clicked.connect(self.analyze_position_mapping)
        self.analyze_btn.setStyleSheet("""
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
        
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.clear_btn)
        analysis_layout.addLayout(button_layout)
        
        splitter.addWidget(analysis_widget)
        
        # 初始分析
        self.analyze_position_mapping()
    
    def analyze_position_mapping(self):
        """分析位置映射"""
        analysis_info = []
        analysis_info.append("🗺️ 座位位置映射分析报告")
        analysis_info.append("=" * 50)
        
        # 统计信息
        total_seats = len(self.position_analysis)
        mapping_diff_seats = [p for p in self.position_analysis if p['mapping_diff']]
        
        analysis_info.append(f"📊 统计信息:")
        analysis_info.append(f"  总座位数: {total_seats}")
        analysis_info.append(f"  位置映射差异: {len(mapping_diff_seats)} 个")
        analysis_info.append(f"  映射一致性: {((total_seats - len(mapping_diff_seats)) / total_seats * 100):.1f}%")
        analysis_info.append("")
        
        # 位置映射差异详情
        if mapping_diff_seats:
            analysis_info.append("🔍 位置映射差异详情:")
            for seat in mapping_diff_seats[:10]:  # 只显示前10个
                analysis_info.append(f"  座位 {seat['seat_no']}:")
                analysis_info.append(f"    逻辑位置: ({seat['logical_row']}, {seat['logical_col']})")
                analysis_info.append(f"    物理位置: ({seat['physical_y']}, {seat['physical_x']})")
                analysis_info.append(f"    区域: {seat['area_name']}")
                analysis_info.append("")
            
            if len(mapping_diff_seats) > 10:
                analysis_info.append(f"  ... 还有 {len(mapping_diff_seats) - 10} 个座位存在映射差异")
        
        analysis_info.append("")
        analysis_info.append("💡 说明:")
        analysis_info.append("  - 逻辑位置: 用于订单提交的座位标识")
        analysis_info.append("  - 物理位置: 用于座位图显示的坐标")
        analysis_info.append("  - 系统会自动处理两种位置的转换")
        
        # 更新显示
        self.analysis_text.clear()
        self.analysis_text.append("\n".join(analysis_info))
    
    def on_seat_selection_changed(self, selected_seats):
        """座位选择变化处理"""
        if selected_seats:
            selection_info = []
            selection_info.append("\n" + "🎯 选中座位详情:")
            selection_info.append("-" * 30)
            
            for seat in selected_seats:
                logical_row = seat.get('logical_row', seat.get('row', '?'))
                logical_col = seat.get('logical_col', seat.get('col', '?'))
                physical_x = seat.get('physical_x', seat.get('x', '?'))
                physical_y = seat.get('physical_y', seat.get('y', '?'))
                area_name = seat.get('area_name', '未知')
                
                selection_info.append(f"座位: {logical_row}排{logical_col}座")
                selection_info.append(f"  逻辑位置: ({logical_row}, {logical_col})")
                selection_info.append(f"  物理位置: ({physical_y}, {physical_x})")
                selection_info.append(f"  区域: {area_name}")
                selection_info.append("")
            
            # 获取订单座位信息
            order_seats = self.seat_panel.get_selected_seats_for_order()
            if order_seats:
                selection_info.append("📋 订单座位信息:")
                for order_seat in order_seats:
                    selection_info.append(f"  {order_seat['row']}排{order_seat['col']}座 - {order_seat['area_name']} {order_seat['price']}元")
            
            self.analysis_text.append("\n".join(selection_info))
    
    def clear_selection(self):
        """清空选择"""
        self.seat_panel.clear_selection()
        self.analyze_position_mapping()

def main():
    """主函数"""
    print("🗺️ 沃美影院座位位置映射测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = SeatPositionTestWindow()
    window.show()
    
    print(f"\n🚀 测试窗口已启动")
    print(f"🎯 测试重点:")
    print(f"  1. 验证逻辑位置和物理位置的正确区分")
    print(f"  2. 检查座位显示位置是否使用物理坐标")
    print(f"  3. 确认订单信息是否使用逻辑位置")
    print(f"  4. 分析位置映射的一致性")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
