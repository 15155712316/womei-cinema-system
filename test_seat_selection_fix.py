#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院座位选择状态管理修复
验证座位选择/取消选择的样式一致性
"""

import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QLabel, QHBoxLayout, QPushButton, QTextEdit
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

class SeatSelectionTestWindow(QMainWindow):
    """座位选择状态管理测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("沃美影院座位选择状态管理测试")
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
        
        # 连接座位选择信号
        self.seat_panel.seat_selected.connect(self.on_seat_selection_changed)
        
        content_layout.addWidget(self.seat_panel, 2)
        
        # 右侧：测试控制面板
        self.create_test_panel(content_layout)
        
        layout.addLayout(content_layout)
        
        print(f"✅ 座位选择状态管理测试窗口创建完成")
    
    def create_header(self, layout):
        """创建标题区域"""
        header_layout = QVBoxLayout()
        
        title = QLabel("🔧 座位选择状态管理测试")
        title.setStyleSheet("""
            QLabel {
                font: bold 16px "Microsoft YaHei";
                color: #333;
                padding: 10px;
                text-align: center;
            }
        """)
        
        subtitle = QLabel("验证座位选择/取消选择的样式一致性")
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
    
    def create_test_panel(self, layout):
        """创建测试控制面板"""
        test_widget = QWidget()
        test_layout = QVBoxLayout(test_widget)
        
        # 测试说明
        test_title = QLabel("🎯 测试要点")
        test_title.setStyleSheet("""
            QLabel {
                font: bold 14px "Microsoft YaHei";
                color: #333;
                padding: 10px 0 5px 0;
            }
        """)
        test_layout.addWidget(test_title)
        
        # 测试步骤
        test_steps = QLabel("""
测试步骤：
1. 点击任意可选座位（变为绿色）
2. 再次点击该座位（应恢复为初始状态）
3. 检查样式是否与从未选择过的座位一致
4. 重复多次选择/取消操作
5. 测试不同区域的座位

预期结果：
✅ 取消选择后样式完全恢复
✅ 区域边框颜色正确保持
✅ 背景色、文字色、hover效果一致
        """)
        test_steps.setStyleSheet("""
            QLabel {
                font: 10px "Microsoft YaHei";
                color: #555;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 6px;
                border: 1px solid #eee;
            }
        """)
        test_layout.addWidget(test_steps)
        
        # 测试按钮
        btn_layout = QVBoxLayout()
        
        self.clear_btn = QPushButton("清空所有选择")
        self.clear_btn.clicked.connect(self.clear_all_selections)
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
        btn_layout.addWidget(self.clear_btn)
        
        test_layout.addLayout(btn_layout)
        
        # 选择状态显示
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet("""
            QTextEdit {
                font: 10px "Consolas";
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        test_layout.addWidget(QLabel("选择状态日志:"))
        test_layout.addWidget(self.status_text)
        
        layout.addWidget(test_widget, 1)
    
    def on_seat_selection_changed(self, selected_seats):
        """座位选择变化处理"""
        try:
            selection_info = f"[{len(selected_seats)}个座位] "
            if selected_seats:
                seat_info = []
                for seat in selected_seats:
                    area_name = seat.get('area_name', '未知')
                    row = seat.get('row', '?')
                    col = seat.get('col', '?')
                    seat_info.append(f"{row}排{col}座({area_name})")
                selection_info += ", ".join(seat_info)
            else:
                selection_info += "无选择"
            
            # 添加到日志
            self.status_text.append(f"[{self.get_current_time()}] {selection_info}")
            
            # 自动滚动到底部
            cursor = self.status_text.textCursor()
            cursor.movePosition(cursor.End)
            self.status_text.setTextCursor(cursor)
            
        except Exception as e:
            print(f"处理座位选择变化错误: {e}")
    
    def clear_all_selections(self):
        """清空所有选择"""
        self.seat_panel.clear_selection()
        self.status_text.append(f"[{self.get_current_time()}] 🔄 清空所有选择")
    
    def get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")

def main():
    """主函数"""
    print("🔧 沃美影院座位选择状态管理测试")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = SeatSelectionTestWindow()
    window.show()
    
    print(f"\n🚀 测试窗口已启动")
    print(f"🎯 测试重点:")
    print(f"  1. 选择座位 → 取消选择 → 检查样式一致性")
    print(f"  2. 区域边框颜色是否正确保持")
    print(f"  3. 多次选择/取消操作的稳定性")
    print(f"  4. 不同区域座位的样式管理")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
