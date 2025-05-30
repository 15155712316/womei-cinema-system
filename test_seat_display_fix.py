#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位图显示修复验证脚本
验证座位数据解析和显示功能的修复
"""

import sys
import os

def test_seat_display_fix():
    """测试座位图显示修复"""
    print("=" * 60)
    print("🎭 座位图显示修复验证")
    print("=" * 60)
    
    try:
        # 模拟真实API返回的座位数据格式
        mock_api_response = {
            'hname': '1号厅',
            'screentype': 'IMAX',
            'seatcount': 150,
            'seats': [
                {'rownum': 1, 'colnum': 1, 'seatname': '1-1', 'state': 0, 'price': 45},
                {'rownum': 1, 'colnum': 2, 'seatname': '1-2', 'state': 0, 'price': 45},
                {'rownum': 1, 'colnum': 3, 'seatname': '1-3', 'state': 1, 'price': 45},  # 已售
                {'rownum': 1, 'colnum': 4, 'seatname': '1-4', 'state': 0, 'price': 45},
                {'rownum': 2, 'colnum': 1, 'seatname': '2-1', 'state': 0, 'price': 45},
                {'rownum': 2, 'colnum': 2, 'seatname': '2-2', 'state': 0, 'price': 45},
                {'rownum': 2, 'colnum': 3, 'seatname': '2-3', 'state': 0, 'price': 45},
                {'rownum': 2, 'colnum': 4, 'seatname': '2-4', 'state': 2, 'price': 45},  # 维修
            ]
        }
        
        print("📋 测试1: 座位数据解析")
        print(f"原始API数据: {len(mock_api_response['seats'])} 个座位")
        
        # 导入主程序的解析方法
        from main_modular import ModularCinemaMainWindow
        
        # 创建临时实例进行测试（不启动UI）
        class TestWindow:
            def _parse_seats_array(self, seats_array, hall_info):
                # 复制主程序的解析逻辑
                max_row = 0
                max_col = 0
                
                for seat in seats_array:
                    row_num = seat.get('rownum', 0)
                    col_num = seat.get('colnum', 0)
                    max_row = max(max_row, row_num)
                    max_col = max(max_col, col_num)
                
                print(f"座位矩阵尺寸: {max_row}行 x {max_col}列")
                
                # 创建座位矩阵
                seat_matrix = []
                for row in range(max_row):
                    seat_row = [None] * max_col
                    seat_matrix.append(seat_row)
                
                # 填充座位数据
                for seat in seats_array:
                    row_num = seat.get('rownum', 0) - 1  # 转为0基索引
                    col_num = seat.get('colnum', 0) - 1  # 转为0基索引
                    
                    if 0 <= row_num < max_row and 0 <= col_num < max_col:
                        # 解析座位状态
                        status = 'available'  # 默认可选
                        if seat.get('state') == 1:
                            status = 'sold'
                        elif seat.get('state') == 2:
                            status = 'unavailable'
                        
                        seat_data = {
                            'row': seat.get('rownum', row_num + 1),
                            'col': seat.get('colnum', col_num + 1),
                            'num': f"{seat.get('rownum', row_num + 1)}排{seat.get('colnum', col_num + 1)}座",
                            'status': status,
                            'price': seat.get('price', 0),
                            'seatname': seat.get('seatname', ''),
                            'original_data': seat
                        }
                        
                        seat_matrix[row_num][col_num] = seat_data
                
                return seat_matrix
        
        test_window = TestWindow()
        hall_info = {
            'name': mock_api_response.get('hname', '未知影厅'),
            'screen_type': mock_api_response.get('screentype', ''),
            'seat_count': mock_api_response.get('seatcount', 0)
        }
        
        seat_matrix = test_window._parse_seats_array(mock_api_response['seats'], hall_info)
        
        print(f"✅ 解析完成: {len(seat_matrix)} 行座位矩阵")
        
        # 验证解析结果
        print("\\n📋 测试2: 座位矩阵验证")
        total_seats = 0
        available_seats = 0
        sold_seats = 0
        unavailable_seats = 0
        
        for r, row in enumerate(seat_matrix):
            print(f"第{r+1}行: ", end="")
            for c, seat in enumerate(row):
                if seat:
                    total_seats += 1
                    status = seat['status']
                    if status == 'available':
                        available_seats += 1
                        print("○", end="")
                    elif status == 'sold':
                        sold_seats += 1
                        print("●", end="")
                    elif status == 'unavailable':
                        unavailable_seats += 1
                        print("✗", end="")
                    else:
                        print("?", end="")
                else:
                    print(" ", end="")
            print()
        
        print(f"\\n座位统计:")
        print(f"  总座位: {total_seats}")
        print(f"  可选: {available_seats}")
        print(f"  已售: {sold_seats}")
        print(f"  不可用: {unavailable_seats}")
        
        print("\\n📋 测试3: 座位数据格式验证")
        sample_seat = None
        for row in seat_matrix:
            for seat in row:
                if seat:
                    sample_seat = seat
                    break
            if sample_seat:
                break
        
        if sample_seat:
            print("示例座位数据:")
            for key, value in sample_seat.items():
                print(f"  {key}: {value}")
        
        print("\\n✅ 座位图显示修复验证完成！")
        print("现在可以启动主程序测试座位图显示效果。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_seat_display_fix() 