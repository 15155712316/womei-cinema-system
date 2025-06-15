#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院多区域座位显示功能
"""

import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
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
    """解析测试座位数据"""
    try:
        print(f"\n🔍 解析座位数据:")
        
        # 收集所有座位和区域信息
        all_seats = []
        area_data = []
        max_row = 0
        max_col = 0
        
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
            
            # 处理座位数据
            if isinstance(seats_data, dict):
                for row_key, row_data in seats_data.items():
                    seat_details = row_data.get('detail', [])
                    row_num = row_data.get('row', int(row_key))
                    
                    for seat_detail in seat_details:
                        seat = process_seat_detail(seat_detail, area_name, area_price, row_num)
                        if seat:
                            all_seats.append(seat)
                            max_row = max(max_row, seat['row'])
                            max_col = max(max_col, seat['col'])
        
        # 构建座位矩阵
        seat_matrix = []
        for row in range(1, max_row + 1):
            row_seats = []
            for col in range(1, max_col + 1):
                # 查找该位置的座位
                seat = None
                for s in all_seats:
                    if s['row'] == row and s['col'] == col:
                        seat = s
                        break
                
                if seat:
                    row_seats.append(seat)
                else:
                    # 空座位
                    row_seats.append(None)
            
            seat_matrix.append(row_seats)
        
        print(f"✅ 座位数据解析完成:")
        print(f"  总座位数: {len(all_seats)}")
        print(f"  矩阵尺寸: {max_row} 行 x {max_col} 列")
        print(f"  区域数量: {len(area_data)}")
        
        return seat_matrix, area_data
        
    except Exception as e:
        print(f"❌ 解析座位数据失败: {e}")
        import traceback
        traceback.print_exc()
        return [], []

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

class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院多区域座位显示测试")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 加载测试数据
        room_seat = load_test_data()
        if not room_seat:
            print("❌ 无法加载测试数据")
            return
        
        # 解析座位数据
        seat_matrix, area_data = parse_test_seat_data(room_seat)
        if not seat_matrix:
            print("❌ 无法解析座位数据")
            return
        
        # 创建座位图组件
        self.seat_panel = SeatMapPanelPyQt5()
        
        # 使用多区域更新方法
        self.seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
        
        # 添加到布局
        layout.addWidget(self.seat_panel)
        
        print(f"✅ 测试窗口创建完成")
        print(f"🎯 测试要点:")
        print(f"  1. 检查不同区域的座位是否有不同颜色的边框")
        print(f"  2. 检查区域价格信息是否正确显示")
        print(f"  3. 检查座位选择功能是否正常")
        print(f"  4. 检查区域颜色映射:")
        for area in area_data:
            area_name = area['area_name']
            area_price = area['area_price']
            print(f"     - {area_name}: {area_price}元")

def main():
    """主函数"""
    print("🎬 沃美影院多区域座位显示功能测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestWindow()
    window.show()
    
    print(f"\n🚀 测试窗口已启动")
    print(f"💡 预期效果:")
    print(f"  - 默认区: 白色边框")
    print(f"  - 前排区域: 黄色边框")
    print(f"  - 按摩区域: 红色边框")
    print(f"  - 中心区域: 蓝色边框")
    print(f"  - 顶部显示各区域价格信息")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
