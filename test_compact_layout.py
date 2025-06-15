#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院座位图UI布局紧凑性优化
验证座位间距移除和空间利用率提升
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

class CompactLayoutTestWindow(QMainWindow):
    """布局紧凑性测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院座位图布局紧凑性测试")
        self.setGeometry(100, 100, 1400, 900)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题和说明
        self.create_header(layout)
        
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
        
        # 创建主要内容区域
        content_layout = QHBoxLayout()
        
        # 左侧：座位图
        self.seat_panel = SeatMapPanelPyQt5()
        self.seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
        
        content_layout.addWidget(self.seat_panel, 3)
        
        # 右侧：测试信息面板
        self.create_info_panel(content_layout, len(seat_matrix), max(len(row) for row in seat_matrix))
        
        layout.addLayout(content_layout)
        
        print(f"✅ 布局紧凑性测试窗口创建完成")
    
    def create_header(self, layout):
        """创建标题区域"""
        header_layout = QVBoxLayout()
        
        title = QLabel("📐 座位图布局紧凑性测试")
        title.setStyleSheet("""
            QLabel {
                font: bold 16px "Microsoft YaHei";
                color: #333;
                padding: 8px;
                text-align: center;
            }
        """)
        
        subtitle = QLabel("验证座位间距移除和空间利用率提升")
        subtitle.setStyleSheet("""
            QLabel {
                font: 12px "Microsoft YaHei";
                color: #666;
                padding: 4px;
                text-align: center;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
    
    def create_info_panel(self, layout, rows, cols):
        """创建信息面板"""
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        
        # 优化效果说明
        info_title = QLabel("🎯 优化效果")
        info_title.setStyleSheet("""
            QLabel {
                font: bold 14px "Microsoft YaHei";
                color: #333;
                padding: 8px 0 4px 0;
            }
        """)
        info_layout.addWidget(info_title)
        
        # 优化详情
        optimization_info = QLabel(f"""
布局优化详情：

📊 座位矩阵规模：
• 总行数：{rows} 行
• 总列数：{cols} 列
• 总座位数：{rows * cols} 个位置

🔧 优化措施：
• 座位间距：2px → 0px
• 网格边距：默认 → 0px
• 主布局边距：5px → 2px
• 主布局间距：8px → 3px
• 区域标签间距：默认 → 2px
• 区域标签内边距：6px → 3px

✅ 预期效果：
• 座位按钮紧密排列
• 无可见间隔
• 空间利用率提升约30%
• 相同视窗显示更多座位
        """)
        optimization_info.setStyleSheet("""
            QLabel {
                font: 10px "Microsoft YaHei";
                color: #555;
                padding: 8px;
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #eee;
                line-height: 1.4;
            }
        """)
        info_layout.addWidget(optimization_info)
        
        # 颜色方案说明
        color_title = QLabel("🎨 区域颜色优化")
        color_title.setStyleSheet("""
            QLabel {
                font: bold 12px "Microsoft YaHei";
                color: #333;
                padding: 8px 0 4px 0;
            }
        """)
        info_layout.addWidget(color_title)
        
        color_info = QLabel("""
区域颜色区分度优化：

• 默认区：#F0F8FF (淡蓝色)
• 前排区域：#FFE4B5 (柔和金色)  
• 按摩区域：#FFE4E1 (淡粉色)
• 中心区域：#E8F5E8 (浅绿色) ✨新

改进：中心区域从浅蓝色改为浅绿色，
与默认区形成明显区分。
        """)
        color_info.setStyleSheet("""
            QLabel {
                font: 9px "Microsoft YaHei";
                color: #555;
                padding: 6px;
                background-color: #f0f8ff;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        info_layout.addWidget(color_info)
        
        # 测试指标
        metrics_title = QLabel("📏 测试指标")
        metrics_title.setStyleSheet("""
            QLabel {
                font: bold 12px "Microsoft YaHei";
                color: #333;
                padding: 8px 0 4px 0;
            }
        """)
        info_layout.addWidget(metrics_title)
        
        metrics_info = QLabel("""
验证标准：
✓ 座位按钮无可见间隔
✓ 整体布局更加紧凑
✓ 相同视窗显示更多座位
✓ 所有交互功能正常
✓ 区域颜色清晰区分
✓ 选择状态正确显示
        """)
        metrics_info.setStyleSheet("""
            QLabel {
                font: 9px "Microsoft YaHei";
                color: #555;
                padding: 6px;
                background-color: #f0fff0;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        info_layout.addWidget(metrics_info)
        
        info_layout.addStretch()
        layout.addWidget(info_widget, 1)

def main():
    """主函数"""
    print("📐 沃美影院座位图布局紧凑性测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = CompactLayoutTestWindow()
    window.show()
    
    print(f"\n🚀 测试窗口已启动")
    print(f"🎯 测试重点:")
    print(f"  1. 座位按钮间距是否完全移除")
    print(f"  2. 整体布局是否更加紧凑")
    print(f"  3. 空间利用率是否提升")
    print(f"  4. 区域颜色区分度是否改善")
    print(f"  5. 所有功能是否正常工作")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
