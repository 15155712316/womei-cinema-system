#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位状态映射
"""

def test_seat_status_mapping():
    """测试座位状态映射"""
    print("=== 测试座位状态映射 ===")
    
    # 模拟沃美座位数据
    test_seat_data = {
        'room_seat': [
            {
                'area_name': '普通区',
                'area_price': 35,
                'seats': {
                    '1': {
                        'row': 1,
                        'detail': [
                            {'seat_no': '1-1', 'row': 1, 'col': 1, 'x': 1, 'y': 1, 'type': 0, 'status': 0},
                            {'seat_no': '1-2', 'row': 1, 'col': 2, 'x': 2, 'y': 1, 'type': 0, 'status': 1},
                            {'seat_no': '1-3', 'row': 1, 'col': 3, 'x': 3, 'y': 1, 'type': 0, 'status': 0}
                        ]
                    }
                }
            }
        ]
    }
    
    # 解析座位状态
    for area in test_seat_data['room_seat']:
        seats_dict = area.get('seats', {})
        for row_key, row_data in seats_dict.items():
            seat_details = row_data.get('detail', [])
            for seat_detail in seat_details:
                seat_status = seat_detail.get('status', 0)
                if seat_status == 0:
                    status = 'available'
                elif seat_status == 1:
                    status = 'sold'
                elif seat_status == 2:
                    status = 'locked'
                else:
                    status = 'available'
                
                seat_no = seat_detail.get('seat_no', '')
                print(f"座位 {seat_no}: 原始状态={seat_status}, 转换状态={status}")
    
    print("\n状态映射规则:")
    print("0 -> available (可选)")
    print("1 -> sold (已售)")
    print("2 -> locked (锁定)")
    
    # 测试座位图组件期望的状态
    print("\n座位图组件支持的状态:")
    print("- available: 可选座位 (绿色)")
    print("- selected: 已选座位 (蓝色)")
    print("- sold: 已售座位 (红色)")
    print("- empty: 空座位 (透明)")
    print("- unavailable: 不可用座位 (灰色)")

if __name__ == "__main__":
    test_seat_status_mapping()
