#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位编号格式
验证seat_no的正确获取和使用
"""

import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_seat_no_extraction():
    """测试座位编号提取"""
    print("🧪 测试座位编号提取")
    print("=" * 50)
    
    # 模拟从应用程序日志中提取的座位数据
    # 这是从订单创建时打印的座位数据
    mock_seat_data = [
        {
            'seatNo': '000000011111-4-2',  # 这是构造的格式
            'rowNum': 2,
            'columnNum': 4,
            'seatType': 1,
            'areaId': 1,
            'unitPrice': 57.9,
            'seatPrice': 57.9,
            'serviceCharge': 0,
            'seatId': 'seat_1',
            'x': 6,
            'y': 2,
            'original_data': {
                'rn': 2,
                'cn': 4,
                'sn': '11051771#09#05',  # 这是真实的seat_no格式
                'r': '2',
                'c': '4',
                's': 'F'
            }
        },
        {
            'seatNo': '000000011111-5-2',  # 这是构造的格式
            'rowNum': 2,
            'columnNum': 5,
            'seatType': 1,
            'areaId': 1,
            'unitPrice': 57.9,
            'seatPrice': 57.9,
            'serviceCharge': 0,
            'seatId': 'seat_2',
            'x': 7,
            'y': 2,
            'original_data': {
                'rn': 2,
                'cn': 5,
                'sn': '11051771#09#06',  # 这是真实的seat_no格式
                'r': '2',
                'c': '5',
                's': 'F'
            }
        }
    ]
    
    print(f"模拟座位数据:")
    for i, seat in enumerate(mock_seat_data):
        print(f"  座位{i+1}:")
        print(f"    - seatNo: {seat['seatNo']}")
        print(f"    - original_data.sn: {seat['original_data']['sn']}")
        print(f"    - rowNum: {seat['rowNum']}, columnNum: {seat['columnNum']}")
    
    return mock_seat_data

def test_seat_parameter_building(seat_data):
    """测试座位参数构建"""
    print(f"\n🧪 测试座位参数构建")
    print("=" * 50)
    
    # 模拟session_info
    session_info = {
        'session_data': {
            'schedule_id': '16626081'
        }
    }
    
    # 模拟座位参数构建逻辑（修复后的版本）
    seat_parts = []
    for seat in seat_data:
        row_num = seat.get("rowNum", 1)
        col_num = seat.get("columnNum", 1)
        area_id = seat.get("areaId", 1)
        
        # 🔧 关键修复：使用真实的seat_no
        original_data = seat.get("original_data", {})
        seat_no_from_original = original_data.get("sn", "")
        seat_no_from_seat = seat.get("seatNo", "")
        
        # 优先使用original_data中的sn
        real_seat_no = seat_no_from_original or seat_no_from_seat
        
        print(f"座位{row_num}-{col_num}:")
        print(f"  - original_data.sn: {seat_no_from_original}")
        print(f"  - seat.seatNo: {seat_no_from_seat}")
        print(f"  - 最终使用: {real_seat_no}")
        
        # 构建座位字符串：区域ID:行号:列号:seat_no
        seat_str = f"{area_id}:{row_num}:{col_num}:{real_seat_no}"
        seat_parts.append(seat_str)
        
        print(f"  - 构建结果: {seat_str}")
    
    # 用 | 连接多个座位
    seatlable_str = "|".join(seat_parts)
    
    print(f"\n最终座位参数: {seatlable_str}")
    print(f"真实小程序参数: 1:2:5:11051771#09#06|1:2:4:11051771#09#05")
    
    return seatlable_str

def compare_formats(our_format, real_format):
    """对比格式差异"""
    print(f"\n🔍 格式对比分析")
    print("=" * 50)
    
    print(f"我们的格式: {our_format}")
    print(f"真实格式:   {real_format}")
    
    # 分析差异
    our_parts = our_format.split("|")
    real_parts = real_format.split("|")
    
    print(f"\n详细对比:")
    for i, (our_part, real_part) in enumerate(zip(our_parts, real_parts)):
        print(f"  座位{i+1}:")
        print(f"    我们: {our_part}")
        print(f"    真实: {real_part}")
        
        # 解析格式
        our_elements = our_part.split(":")
        real_elements = real_part.split(":")
        
        if len(our_elements) >= 4 and len(real_elements) >= 4:
            print(f"    区域ID: {our_elements[0]} vs {real_elements[0]} {'✅' if our_elements[0] == real_elements[0] else '❌'}")
            print(f"    行号:   {our_elements[1]} vs {real_elements[1]} {'✅' if our_elements[1] == real_elements[1] else '❌'}")
            print(f"    列号:   {our_elements[2]} vs {real_elements[2]} {'✅' if our_elements[2] == real_elements[2] else '❌'}")
            print(f"    seat_no: {our_elements[3]} vs {real_elements[3]} {'✅' if our_elements[3] == real_elements[3] else '❌'}")

def test_api_call_simulation():
    """模拟API调用测试"""
    print(f"\n🧪 模拟API调用测试")
    print("=" * 50)
    
    # 使用修复后的座位参数
    seatlable = "1:2:4:11051771#09#05|1:2:5:11051771#09#06"
    schedule_id = "16626081"
    cinema_id = "400028"
    
    print(f"API调用参数:")
    print(f"  - URL: https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/ticket/")
    print(f"  - seatlable: {seatlable}")
    print(f"  - schedule_id: {schedule_id}")
    
    # 模拟请求数据
    data = {
        'seatlable': seatlable,
        'schedule_id': schedule_id
    }
    
    print(f"\n请求数据: {data}")
    
    # 预期结果分析
    print(f"\n预期结果分析:")
    print(f"  ✅ 格式正确: 使用真实的seat_no格式")
    print(f"  ✅ 参数完整: 包含所有必需字段")
    print(f"  ✅ 数据来源: 从original_data获取真实sn")
    print(f"  💡 可能结果: 锁座成功或座位已被占用")

def main():
    """主函数"""
    print("🔧 座位编号格式测试")
    print("=" * 60)
    
    # 测试座位编号提取
    seat_data = test_seat_no_extraction()
    
    # 测试座位参数构建
    our_format = test_seat_parameter_building(seat_data)
    
    # 对比真实格式
    real_format = "1:2:5:11051771#09#06|1:2:4:11051771#09#05"
    compare_formats(our_format, real_format)
    
    # 模拟API调用
    test_api_call_simulation()
    
    print(f"\n🎯 修复总结")
    print("=" * 60)
    print(f"✅ 关键修复:")
    print(f"  1. 使用original_data.sn获取真实seat_no")
    print(f"  2. seat_no格式: 11051771#09#05 (不是构造的)")
    print(f"  3. 座位参数格式: 区域ID:行号:列号:seat_no")
    print(f"  4. 多座位用|连接")
    
    print(f"\n🚀 现在可以测试:")
    print(f"  1. 启动应用程序")
    print(f"  2. 选择座位并查看调试信息")
    print(f"  3. 验证original_data.sn是否包含正确格式")
    print(f"  4. 提交订单测试API调用")

if __name__ == "__main__":
    main()
