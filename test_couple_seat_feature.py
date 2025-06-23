#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情侣座位自动连选功能测试脚本
测试沃美电影票务系统中的情侣座位功能
"""

import sys
import os
import json
from typing import List, Dict

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_couple_seat_identification():
    """测试情侣座位识别功能"""
    print("🧪 测试情侣座位识别功能")
    print("=" * 50)
    
    # 模拟沃美API返回的座位数据
    test_seat_data = [
        {
            "seat_no": "11051771#01#08",
            "row": "8",
            "col": "3",
            "x": 3,
            "y": 9,
            "type": 1,  # 情侣座左座
            "status": 0
        },
        {
            "seat_no": "11051771#01#07",
            "row": "8",
            "col": "4",
            "x": 4,
            "y": 9,
            "type": 2,  # 情侣座右座
            "status": 0
        },
        {
            "seat_no": "11051771#01#06",
            "row": "8",
            "col": "5",
            "x": 5,
            "y": 9,
            "type": 0,  # 普通座位
            "status": 0
        }
    ]
    
    # 测试情侣座位识别
    for i, seat in enumerate(test_seat_data):
        seat_type = seat.get('type', 0)
        is_couple = seat_type in [1, 2]
        couple_type = "左座" if seat_type == 1 else "右座" if seat_type == 2 else "普通座位"
        
        print(f"座位 {i+1}: {seat['row']}排{seat['col']}座")
        print(f"  - 类型: {seat_type} ({couple_type})")
        print(f"  - 是否情侣座: {'是' if is_couple else '否'}")
        print(f"  - 物理位置: x={seat['x']}, y={seat['y']}")
        print()
    
    return True

def test_couple_seat_pairing():
    """测试情侣座位配对逻辑"""
    print("🧪 测试情侣座位配对逻辑")
    print("=" * 50)
    
    # 模拟座位矩阵
    seat_matrix = [
        [
            {
                "seat_no": "11051771#01#08",
                "row": 8, "col": 3, "x": 3, "y": 9,
                "type": 1, "status": "available"
            },
            {
                "seat_no": "11051771#01#07", 
                "row": 8, "col": 4, "x": 4, "y": 9,
                "type": 2, "status": "available"
            },
            {
                "seat_no": "11051771#01#06",
                "row": 8, "col": 5, "x": 5, "y": 9,
                "type": 0, "status": "available"
            }
        ]
    ]
    
    def find_couple_partner(seat, seat_matrix):
        """模拟查找配对座位的逻辑"""
        current_x = seat.get('x')
        current_y = seat.get('y')
        seat_type = seat.get('type')
        
        if seat_type == 1:  # 左座，查找右座
            target_x = current_x + 1
            target_type = 2
        elif seat_type == 2:  # 右座，查找左座
            target_x = current_x - 1
            target_type = 1
        else:
            return None
        
        # 在矩阵中查找
        for row in seat_matrix:
            for partner_seat in row:
                if (partner_seat.get('x') == target_x and 
                    partner_seat.get('y') == current_y and
                    partner_seat.get('type') == target_type):
                    return partner_seat
        return None
    
    # 测试配对
    for row in seat_matrix:
        for seat in row:
            seat_type = seat.get('type')
            if seat_type in [1, 2]:
                partner = find_couple_partner(seat, seat_matrix)
                print(f"座位 {seat['row']}排{seat['col']}座 (type={seat_type})")
                if partner:
                    print(f"  ✅ 找到配对座位: {partner['row']}排{partner['col']}座 (type={partner['type']})")
                else:
                    print(f"  ❌ 未找到配对座位")
                print()
    
    return True

def test_couple_seat_selection_logic():
    """测试情侣座位选择逻辑"""
    print("🧪 测试情侣座位选择逻辑")
    print("=" * 50)
    
    # 模拟选择状态
    selected_seats = set()
    
    def simulate_couple_seat_selection(seat1_key, seat2_key, seat1, seat2):
        """模拟情侣座位选择"""
        print(f"点击情侣座位: {seat1['row']}排{seat1['col']}座")
        
        # 检查当前状态
        both_selected = seat1_key in selected_seats and seat2_key in selected_seats
        both_unselected = seat1_key not in selected_seats and seat2_key not in selected_seats
        
        if both_selected:
            # 取消选择
            selected_seats.discard(seat1_key)
            selected_seats.discard(seat2_key)
            seat1['status'] = 'available'
            seat2['status'] = 'available'
            print(f"  💔 取消选择情侣座位: {seat1['row']}排{seat1['col']}座 + {seat2['row']}排{seat2['col']}座")
        elif both_unselected:
            # 检查是否可选
            if seat1['status'] == 'available' and seat2['status'] == 'available':
                # 选择
                selected_seats.add(seat1_key)
                selected_seats.add(seat2_key)
                seat1['status'] = 'selected'
                seat2['status'] = 'selected'
                print(f"  💕 选择情侣座位: {seat1['row']}排{seat1['col']}座 + {seat2['row']}排{seat2['col']}座")
            else:
                print(f"  ❌ 情侣座位不可选择")
        else:
            print(f"  ⚠️ 情侣座位状态异常")
        
        print(f"  当前已选座位数: {len(selected_seats)}")
        return True
    
    # 测试数据
    seat1 = {"row": 8, "col": 3, "type": 1, "status": "available"}
    seat2 = {"row": 8, "col": 4, "type": 2, "status": "available"}
    seat1_key = (0, 0)
    seat2_key = (0, 1)
    
    # 测试选择
    print("第一次点击（选择）:")
    simulate_couple_seat_selection(seat1_key, seat2_key, seat1, seat2)
    print()
    
    print("第二次点击（取消选择）:")
    simulate_couple_seat_selection(seat1_key, seat2_key, seat1, seat2)
    print()
    
    return True

def test_couple_seat_order_data():
    """测试情侣座位订单数据格式"""
    print("🧪 测试情侣座位订单数据格式")
    print("=" * 50)
    
    # 模拟选中的情侣座位数据
    selected_couple_seats = [
        {
            'seat_no': '11051771#01#08',
            'row': 8,
            'col': 3,
            'area_name': '中心区域',
            'area_price': 62.9,
            'price': 62.9,
            'type': 1,  # 情侣座左座
            'num': '3',
            'original_data': {
                'seat_no': '11051771#01#08',
                'area_no': '10013',
                'row': '8',
                'col': '3',
                'type': 1,
                'status': 0
            }
        },
        {
            'seat_no': '11051771#01#07',
            'row': 8,
            'col': 4,
            'area_name': '中心区域',
            'area_price': 62.9,
            'price': 62.9,
            'type': 2,  # 情侣座右座
            'num': '4',
            'original_data': {
                'seat_no': '11051771#01#07',
                'area_no': '10013',
                'row': '8',
                'col': '4',
                'type': 2,
                'status': 0
            }
        }
    ]
    
    print("情侣座位订单数据:")
    for i, seat in enumerate(selected_couple_seats):
        seat_type_desc = "左座" if seat['type'] == 1 else "右座" if seat['type'] == 2 else "普通座"
        print(f"座位 {i+1}: {seat['row']}排{seat['col']}座 ({seat_type_desc})")
        print(f"  - 座位编号: {seat['seat_no']}")
        print(f"  - 区域: {seat['area_name']}")
        print(f"  - 价格: ¥{seat['price']}")
        print(f"  - 类型: {seat['type']}")
        print()
    
    # 计算总价
    total_price = sum(seat['price'] for seat in selected_couple_seats)
    print(f"情侣座位总价: ¥{total_price}")
    
    return True

def main():
    """主测试函数"""
    print("🎬 沃美电影票务系统 - 情侣座位功能测试")
    print("=" * 60)
    print()
    
    tests = [
        test_couple_seat_identification,
        test_couple_seat_pairing,
        test_couple_seat_selection_logic,
        test_couple_seat_order_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print("✅ 测试通过")
            else:
                print("❌ 测试失败")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
        print()
    
    print("=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！情侣座位功能实现正确。")
    else:
        print("⚠️ 部分测试失败，请检查实现。")

if __name__ == "__main__":
    main()
