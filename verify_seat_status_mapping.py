#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证沃美影院系统座位状态映射准确性
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def verify_seat_status_mapping():
    """验证座位状态映射逻辑"""
    print("🎬 沃美影院系统座位状态映射验证")
    print("=" * 60)
    
    print("📋 验证目标:")
    print("影院: 北京龙湖店")
    print("电影: 新驯龙高手")
    print("场次: 2025年6月15日 20:20")
    print("影厅: 1厅")
    print("目标座位: 1排6座、1排7座")
    print("预期状态: 已售（与真实APP一致）")
    
    print("\n🔍 当前座位状态映射逻辑:")
    status_mapping = {
        0: "available (可选)",
        1: "sold (已售)", 
        2: "locked (锁定)",
        "其他": "available (默认可选)"
    }
    
    for code, desc in status_mapping.items():
        print(f"  {code}: {desc}")
    
    print("\n📊 需要验证的关键点:")
    verification_points = [
        "1. API返回的原始座位状态数据",
        "2. 状态码到字符串的映射转换",
        "3. UI显示的座位状态",
        "4. 与真实APP的状态对比"
    ]
    
    for point in verification_points:
        print(f"  {point}")
    
    return True

def create_seat_status_debug_tool():
    """创建座位状态调试工具"""
    print("\n🛠️ 创建座位状态调试工具...")
    
    debug_tool = '''#!/usr/bin/env python3
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
    
    print("\\n🎯 目标座位:")
    for seat in target_seats:
        print(f"  {seat['row']}排{seat['col']}座 - 预期状态: {seat['expected']}")
    
    # 这里需要实际的场次ID和影厅ID
    # 您需要从实际的六级联动中获取这些ID
    print("\\n⚠️ 使用说明:")
    print("1. 请先在主程序中完成六级联动选择")
    print("2. 找到对应的cinema_id, hall_id, schedule_id")
    print("3. 更新下面的参数后运行调试")
    
    # 示例参数（需要替换为实际值）
    cinema_id = "请替换为实际的cinema_id"
    hall_id = "请替换为实际的hall_id" 
    schedule_id = "请替换为实际的schedule_id"
    token = "47794858a832916d8eda012e7cabd269"  # 使用实际token
    
    print(f"\\n📋 当前参数:")
    print(f"  cinema_id: {cinema_id}")
    print(f"  hall_id: {hall_id}")
    print(f"  schedule_id: {schedule_id}")
    print(f"  token: {token[:20]}...")
    
    if cinema_id == "请替换为实际的cinema_id":
        print("\\n❌ 请先更新实际的场次参数！")
        return False
    
    try:
        # 调用沃美座位图API
        film_service = get_womei_film_service(token)
        result = film_service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        if not result or not result.get('success'):
            print(f"\\n❌ 获取座位图失败: {result.get('error', '未知错误')}")
            return False
        
        hall_info = result.get('hall_info', {})
        room_seat = hall_info.get('room_seat', [])
        
        print(f"\\n✅ 成功获取座位图数据")
        print(f"区域数量: {len(room_seat)}")
        
        # 分析目标座位状态
        analyze_target_seats(room_seat, target_seats)
        
        return True
        
    except Exception as e:
        print(f"\\n❌ 调试过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_target_seats(room_seat, target_seats):
    """分析目标座位的状态"""
    print("\\n🔍 分析目标座位状态:")
    print("=" * 40)
    
    found_seats = []
    
    for area_index, area in enumerate(room_seat):
        area_name = area.get('area_name', '未知区域')
        seats_data = area.get('seats', [])
        
        print(f"\\n区域 {area_index + 1}: {area_name}")
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
    print("\\n📊 目标座位状态分析结果:")
    print("=" * 40)
    
    for target in target_seats:
        target_key = f"{target['row']}-{target['col']}"
        found = False
        
        for found_seat in found_seats:
            if found_seat['row'] == target['row'] and found_seat['col'] == target['col']:
                found = True
                print(f"\\n🎯 {target['row']}排{target['col']}座:")
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
            print(f"\\n❌ 未找到 {target['row']}排{target['col']}座")

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
                
                print(f"\\n🎯 找到目标座位: {seat_row}排{seat_col}座 ({seat_no})")
                print(f"  区域: {area_name}")
                print(f"  原始状态: {seat_status}")
                print(f"  映射状态: {mapped_status}")
                break
                
    except Exception as e:
        print(f"检查座位详情错误: {e}")

if __name__ == "__main__":
    debug_specific_seats()
'''
    
    with open("debug_seat_status.py", "w", encoding="utf-8") as f:
        f.write(debug_tool)
    
    print("✅ 座位状态调试工具已创建: debug_seat_status.py")

def create_status_mapping_analysis():
    """创建状态映射分析"""
    print("\n📊 座位状态映射分析:")
    print("=" * 60)
    
    print("🔍 当前映射逻辑 (main_modular.py _process_seat_detail方法):")
    current_mapping = '''
# 🔧 沃美座位状态映射：数字状态转换为字符串状态
seat_status = seat_detail.get('status', 0)

if seat_status == 0:
    status = 'available'  # 可选
elif seat_status == 1:
    status = 'sold'       # 已售
elif seat_status == 2:
    status = 'locked'     # 锁定
else:
    status = 'available'  # 默认可选
'''
    print(current_mapping)
    
    print("🎯 验证重点:")
    verification_focus = [
        "1. 确认API返回的1排6座、1排7座的status字段值",
        "2. 验证status=1是否正确映射为'sold'状态",
        "3. 检查UI显示是否正确反映'sold'状态",
        "4. 对比真实APP确认状态一致性"
    ]
    
    for focus in verification_focus:
        print(f"  {focus}")
    
    print("\n🔧 可能的问题和解决方案:")
    potential_issues = [
        {
            "问题": "API返回的状态码与预期不符",
            "原因": "沃美API的状态码定义可能不同",
            "解决": "通过实际API调用确认状态码含义"
        },
        {
            "问题": "状态映射逻辑错误",
            "原因": "映射关系定义不正确",
            "解决": "根据实际数据调整映射逻辑"
        },
        {
            "问题": "UI显示状态不正确",
            "原因": "座位按钮样式映射问题",
            "解决": "检查座位按钮的状态样式设置"
        },
        {
            "问题": "数据传递过程中状态丢失",
            "原因": "座位数据在处理过程中被修改",
            "解决": "添加调试日志跟踪状态变化"
        }
    ]
    
    for i, issue in enumerate(potential_issues, 1):
        print(f"  问题 {i}: {issue['问题']}")
        print(f"    原因: {issue['原因']}")
        print(f"    解决: {issue['解决']}")
        print()

def create_verification_steps():
    """创建验证步骤"""
    print("\n📋 详细验证步骤:")
    print("=" * 60)
    
    steps = [
        {
            "步骤": "1. 获取实际场次参数",
            "操作": "在主程序中完成六级联动，记录cinema_id, hall_id, schedule_id",
            "目的": "获取准确的API调用参数"
        },
        {
            "步骤": "2. 运行座位状态调试工具",
            "操作": "更新debug_seat_status.py中的参数并运行",
            "目的": "获取目标座位的原始状态数据"
        },
        {
            "步骤": "3. 分析API返回数据",
            "操作": "检查1排6座、1排7座的status字段值",
            "目的": "确认API返回的状态码"
        },
        {
            "步骤": "4. 验证状态映射",
            "操作": "确认状态码是否正确映射为'sold'",
            "目的": "验证映射逻辑的准确性"
        },
        {
            "步骤": "5. 检查UI显示",
            "操作": "在座位图中查看这两个座位的显示状态",
            "目的": "确认UI正确反映座位状态"
        },
        {
            "步骤": "6. 对比真实APP",
            "操作": "与沃美影院APP的显示进行对比",
            "目的": "确保状态一致性"
        }
    ]
    
    for step in steps:
        print(f"{step['步骤']}: {step['操作']}")
        print(f"  目的: {step['目的']}")
        print()

def main():
    """主函数"""
    verify_seat_status_mapping()
    create_seat_status_debug_tool()
    create_status_mapping_analysis()
    create_verification_steps()
    
    print("🎯 下一步操作指南:")
    print("=" * 60)
    
    print("1. 📋 准备工作:")
    print("   - 启动主程序: python main_modular.py")
    print("   - 完成六级联动选择到目标场次")
    print("   - 记录控制台中显示的cinema_id, hall_id, schedule_id")
    
    print("\n2. 🔧 运行调试:")
    print("   - 编辑 debug_seat_status.py，更新实际参数")
    print("   - 运行调试工具: python debug_seat_status.py")
    print("   - 查看目标座位的状态分析结果")
    
    print("\n3. ✅ 验证结果:")
    print("   - 确认1排6座、1排7座的原始状态码")
    print("   - 验证映射后的状态是否为'sold'")
    print("   - 检查与真实APP的一致性")
    
    print("\n4. 🔧 如需修复:")
    print("   - 如果状态映射不正确，请提供实际的API数据")
    print("   - 我将根据实际数据调整映射逻辑")

if __name__ == "__main__":
    main()
