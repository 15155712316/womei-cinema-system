#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的沃美影院多区域座位颜色方案
"""

import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout
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

class ImprovedColorTestWindow(QMainWindow):
    """改进颜色方案测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院改进颜色方案测试 - 柔和用户友好版")
        self.setGeometry(100, 100, 1200, 900)
        
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
        
        # 创建座位图组件
        self.seat_panel = SeatMapPanelPyQt5()
        
        # 使用多区域更新方法
        self.seat_panel.update_seat_data_with_areas(seat_matrix, area_data)
        
        # 添加到布局
        layout.addWidget(self.seat_panel)
        
        # 添加颜色说明
        self.create_color_legend(layout, area_data)
        
        print(f"✅ 改进颜色方案测试窗口创建完成")
    
    def create_header(self, layout):
        """创建标题区域"""
        header_layout = QVBoxLayout()
        
        title = QLabel("🎨 沃美影院改进颜色方案测试")
        title.setStyleSheet("""
            QLabel {
                font: bold 16px "Microsoft YaHei";
                color: #333;
                padding: 10px;
                text-align: center;
            }
        """)
        
        subtitle = QLabel("柔和、协调、用户友好的多区域座位显示")
        subtitle.setStyleSheet("""
            QLabel {
                font: 12px "Microsoft YaHei";
                color: #666;
                padding: 5px;
                text-align: center;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addLayout(header_layout)
    
    def create_color_legend(self, layout, area_data):
        """创建颜色说明"""
        legend_layout = QVBoxLayout()
        
        legend_title = QLabel("🎯 颜色方案对比")
        legend_title.setStyleSheet("""
            QLabel {
                font: bold 14px "Microsoft YaHei";
                color: #333;
                padding: 10px 0 5px 0;
            }
        """)
        legend_layout.addWidget(legend_title)
        
        # 颜色对比表
        comparison_layout = QHBoxLayout()
        
        # 旧颜色方案
        old_colors = {
            '默认区': '#FFFFFF',
            '前排区域': '#FFFF00',
            '按摩区域': '#FF0000',
            '中心区域': '#0000FF'
        }
        
        # 新颜色方案
        new_colors = {
            '默认区': '#F0F8FF',
            '前排区域': '#FFE4B5',
            '按摩区域': '#FFE4E1',
            '中心区域': '#E6F3FF'
        }
        
        # 创建对比表
        for area in area_data:
            area_name = area['area_name']
            area_price = area['area_price']
            
            area_layout = QVBoxLayout()
            
            # 区域名称
            name_label = QLabel(f"{area_name} ({area_price}元)")
            name_label.setStyleSheet("""
                QLabel {
                    font: bold 11px "Microsoft YaHei";
                    color: #333;
                    padding: 2px;
                }
            """)
            area_layout.addWidget(name_label)
            
            # 旧颜色
            old_color = old_colors.get(area_name, '#CCCCCC')
            old_label = QLabel("旧方案")
            old_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {old_color};
                    border: 2px solid #999;
                    padding: 8px;
                    border-radius: 4px;
                    font: 10px "Microsoft YaHei";
                    color: #333;
                }}
            """)
            area_layout.addWidget(old_label)
            
            # 新颜色
            new_color = new_colors.get(area_name, '#CCCCCC')
            new_label = QLabel("新方案")
            new_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {new_color};
                    border: 1px solid #ddd;
                    padding: 8px;
                    border-radius: 6px;
                    font: 10px "Microsoft YaHei";
                    color: #555;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }}
            """)
            area_layout.addWidget(new_label)
            
            comparison_layout.addLayout(area_layout)
        
        legend_layout.addLayout(comparison_layout)
        
        # 改进说明
        improvements = QLabel("""
✨ 改进要点：
• 降低颜色饱和度，避免刺眼效果
• 使用柔和的色调，提升视觉舒适度
• 边框宽度从3px调整为2px，更加精致
• 添加微妙的阴影效果，增强层次感
• 保持区域间的可识别性
        """)
        improvements.setStyleSheet("""
            QLabel {
                font: 10px "Microsoft YaHei";
                color: #666;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #eee;
            }
        """)
        legend_layout.addWidget(improvements)
        
        layout.addLayout(legend_layout)

def main():
    """主函数"""
    print("🎨 沃美影院改进颜色方案测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = ImprovedColorTestWindow()
    window.show()
    
    print(f"\n🚀 改进颜色方案测试窗口已启动")
    print(f"🎯 新颜色方案特点:")
    print(f"  - 默认区: 淡蓝色 (#F0F8FF) - 柔和清新")
    print(f"  - 前排区域: 柔和金色 (#FFE4B5) - 温暖舒适")
    print(f"  - 按摩区域: 淡粉色 (#FFE4E1) - 温和优雅")
    print(f"  - 中心区域: 浅蓝色 (#E6F3FF) - 宁静专业")
    print(f"  - 边框宽度: 2px（更精致）")
    print(f"  - 添加微妙阴影效果")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
