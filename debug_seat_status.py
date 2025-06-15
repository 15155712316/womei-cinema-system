#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位状态调试工具 - 专门验证特定座位的状态映射
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.womei_film_service import get_womei_film_service

def debug_specific_seats():
    """调试特定座位状态"""
    print("🎯 调试特定座位状态映射")
    print("=" * 50)
    
    # 目标座位信息
    target_seats = [
        {"row": 1, "col": 6, "expected": "已售"},
        {"row": 1, "col": 7, "expected": "已售"}
    ]
    
    print("🎬 目标场次信息:")
    print("  影院: 北京龙湖店")
    print("  电影: 新驯龙高手")
    print("  时间: 2025年6月15日 20:20")
    print("  影厅: 1厅")
    
    print("\n🎯 目标座位:")
    for seat in target_seats:
        print(f"  {seat['row']}排{seat['col']}座 - 预期状态: {seat['expected']}")
    
    # 这里需要实际的场次ID和影厅ID
    # 您需要从实际的六级联动中获取这些ID
    print("\n⚠️ 使用说明:")
    print("1. 请先在主程序中完成六级联动选择")
    print("2. 找到对应的cinema_id, hall_id, schedule_id")
    print("3. 更新下面的参数后运行调试")
    
    # 示例参数（需要替换为实际值）
    cinema_id = "请替换为实际的cinema_id"
    hall_id = "请替换为实际的hall_id" 
    schedule_id = "请替换为实际的schedule_id"
    token = "47794858a832916d8eda012e7cabd269"  # 使用实际token
    
    print(f"\n📋 当前参数:")
    print(f"  cinema_id: {cinema_id}")
    print(f"  hall_id: {hall_id}")
    print(f"  schedule_id: {schedule_id}")
    print(f"  token: {token[:20]}...")
    
    if cinema_id == "请替换为实际的cinema_id":
        print("\n❌ 请先更新实际的场次参数！")
        return False
    
    try:
        # 调用沃美座位图API
        film_service = get_womei_film_service(token)
        result = film_service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        if not result or not result.get('success'):
            print(f"\n❌ 获取座位图失败: {result.get('error', '未知错误')}")
            return False
        
        hall_info = result.get('hall_info', {})
        room_seat = hall_info.get('room_seat', [])
        
        print(f"\n✅ 成功获取座位图数据")
        print(f"区域数量: {len(room_seat)}")
        
        # 分析目标座位状态
        analyze_target_seats(room_seat, target_seats)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_target_seats(room_seat, target_seats):
    """分析目标座位的状态"""
    print("\n🔍 分析目标座位状态:")
    print("=" * 40)
    
    found_seats = []
    
    for area_index, area in enumerate(room_seat):
        area_name = area.get('area_name', '未知区域')
        seats_data = area.get('seats', [])
        
        print(f"\n区域 {area_index + 1}: {area_name}")
        print(f"座位数据类型: {type(seats_data)}")
        print(f"座位数量: {len(seats_data)}")
        
        if isinstance(seats_data, list):
            # 列表格式：直接遍历座位
            for seat_detail in seats_data:
                check_seat_detail(seat_detail, target_seats, found_seats, area_name)
                
        elif isinstance(seats_data, dict):
            # 字典格式：按行遍历
            for row_key, row_data in seats_data.items():
                seat_details = row_data.get('detail', [])
                for seat_detail in seat_details:
                    check_seat_detail(seat_detail, target_seats, found_seats, area_name)
    
    # 总结分析结果
    print("\n📊 目标座位状态分析结果:")
    print("=" * 40)
    
    for target in target_seats:
        target_key = f"{target['row']}-{target['col']}"
        found = False
        
        for found_seat in found_seats:
            if found_seat['row'] == target['row'] and found_seat['col'] == target['col']:
                found = True
                print(f"\n🎯 {target['row']}排{target['col']}座:")
                print(f"  原始状态码: {found_seat['original_status']}")
                print(f"  映射后状态: {found_seat['mapped_status']}")
                print(f"  预期状态: {target['expected']}")
                
                # 状态一致性检查
                if found_seat['mapped_status'] == 'sold' and target['expected'] == '已售':
                    print(f"  ✅ 状态映射正确")
                else:
                    print(f"  ❌ 状态映射不一致！")
                    print(f"     系统显示: {found_seat['mapped_status']}")
                    print(f"     应该显示: sold (已售)")
                break
        
        if not found:
            print(f"\n❌ 未找到 {target['row']}排{target['col']}座")

def check_seat_detail(seat_detail, target_seats, found_seats, area_name):
    """检查单个座位详情"""
    try:
        seat_row = seat_detail.get('row', 0)
        seat_col = seat_detail.get('col', 0)
        seat_status = seat_detail.get('status', 0)
        seat_no = seat_detail.get('seat_no', '')
        
        # 状态映射
        if seat_status == 0:
            mapped_status = 'available'
        elif seat_status == 1:
            mapped_status = 'sold'
        elif seat_status == 2:
            mapped_status = 'locked'
        else:
            mapped_status = 'available'
        
        # 检查是否是目标座位
        for target in target_seats:
            if seat_row == target['row'] and seat_col == target['col']:
                found_seats.append({
                    'row': seat_row,
                    'col': seat_col,
                    'seat_no': seat_no,
                    'original_status': seat_status,
                    'mapped_status': mapped_status,
                    'area_name': area_name,
                    'raw_data': seat_detail
                })
                
                print(f"\n🎯 找到目标座位: {seat_row}排{seat_col}座 ({seat_no})")
                print(f"  区域: {area_name}")
                print(f"  原始状态: {seat_status}")
                print(f"  映射状态: {mapped_status}")
                break
                
    except Exception as e:
        print(f"检查座位详情错误: {e}")

if __name__ == "__main__":
    debug_specific_seats()
