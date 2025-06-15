#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整分析沃美影院座位数据结构 - 修正版
"""

import json

def complete_seat_analysis():
    """完整分析座位数据"""
    print("🎬 沃美影院座位数据结构完整分析（修正版）")
    print("=" * 80)
    
    # 加载数据
    with open('real_seat_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    hall_data = data['data']
    room_seat = hall_data['room_seat']
    
    print(f"🏛️ 影厅信息:")
    print(f"  影厅编号: {hall_data['hall_no']}")
    print(f"  影厅名称: {hall_data['hall_name']}")
    print(f"  区域数量: {len(room_seat)}")
    
    # 分区域详细分析
    all_seats = []
    for area_index, area in enumerate(room_seat, 1):
        area_name = area['area_name']
        area_price = area['area_price']
        seats_data = area['seats']
        
        print(f"\n📍 区域 {area_index}: {area_name}")
        print(f"  价格: {area_price}元")
        print(f"  行数: {len(seats_data)}")
        
        area_seats = []
        for row_key, row_data in seats_data.items():
            seat_details = row_data['detail']
            area_seats.extend(seat_details)
            print(f"    第{row_key}行: {len(seat_details)}个座位")
        
        print(f"  区域总座位: {len(area_seats)}个")
        
        # 分析这个区域的坐标关系
        analyze_area_coordinates(area_name, area_seats)
        
        all_seats.extend(area_seats)
    
    print(f"\n📊 全影厅统计:")
    print(f"  总座位数: {len(all_seats)}")
    
    # 全局坐标关系分析
    analyze_global_coordinates(all_seats)
    
    return all_seats

def analyze_area_coordinates(area_name, seats):
    """分析单个区域的坐标关系"""
    print(f"\n    🔍 {area_name} 坐标关系分析:")
    
    if not seats:
        print(f"      ⚠️ 该区域无座位数据")
        return
    
    # 统计row=y和col=x的匹配情况
    row_y_matches = 0
    col_x_matches = 0
    
    # 显示前3个座位的详细对比
    print(f"      {'序号':<4} {'seat_no':<18} {'row':<4} {'y':<4} {'row=y?':<8} {'col':<4} {'x':<4} {'col=x?':<8}")
    print(f"      {'-'*4} {'-'*18} {'-'*4} {'-'*4} {'-'*8} {'-'*4} {'-'*4} {'-'*8}")
    
    for i, seat in enumerate(seats[:3], 1):
        seat_no = seat['seat_no'][:16]
        row = seat['row']
        col = seat['col']
        x = seat['x']
        y = seat['y']
        
        row_y_match = str(row) == str(y)
        col_x_match = str(col) == str(x)
        
        if row_y_match:
            row_y_matches += 1
        if col_x_match:
            col_x_matches += 1
        
        print(f"      {i:<4} {seat_no:<18} {row:<4} {y:<4} {'✅' if row_y_match else '❌':<8} {col:<4} {x:<4} {'✅' if col_x_match else '❌':<8}")
    
    # 统计整个区域的匹配率
    total_row_y = sum(1 for seat in seats if str(seat['row']) == str(seat['y']))
    total_col_x = sum(1 for seat in seats if str(seat['col']) == str(seat['x']))
    
    print(f"      📊 区域统计: row=y {total_row_y}/{len(seats)} ({total_row_y/len(seats)*100:.1f}%), col=x {total_col_x}/{len(seats)} ({total_col_x/len(seats)*100:.1f}%)")

def analyze_global_coordinates(all_seats):
    """分析全局坐标关系"""
    print(f"\n🔢 全局坐标关系分析:")
    print("=" * 60)
    
    # 统计所有座位的坐标关系
    row_y_matches = sum(1 for seat in all_seats if str(seat['row']) == str(seat['y']))
    col_x_matches = sum(1 for seat in all_seats if str(seat['col']) == str(seat['x']))
    
    print(f"📊 全影厅坐标匹配统计:")
    print(f"  row=y: {row_y_matches}/{len(all_seats)} ({row_y_matches/len(all_seats)*100:.1f}%)")
    print(f"  col=x: {col_x_matches}/{len(all_seats)} ({col_x_matches/len(all_seats)*100:.1f}%)")
    
    # 找出不匹配的座位样本
    mismatched_seats = []
    for seat in all_seats:
        if str(seat['row']) != str(seat['y']) or str(seat['col']) != str(seat['x']):
            mismatched_seats.append(seat)
    
    if mismatched_seats:
        print(f"\n⚠️ 发现 {len(mismatched_seats)} 个坐标不匹配的座位:")
        print(f"{'序号':<4} {'seat_no':<18} {'row':<4} {'y':<4} {'col':<4} {'x':<4} {'不匹配原因'}")
        print(f"{'-'*4} {'-'*18} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*20}")
        
        for i, seat in enumerate(mismatched_seats[:10], 1):  # 显示前10个
            seat_no = seat['seat_no'][:16]
            row = seat['row']
            col = seat['col']
            x = seat['x']
            y = seat['y']
            
            reasons = []
            if str(row) != str(y):
                reasons.append(f"row({row})≠y({y})")
            if str(col) != str(x):
                reasons.append(f"col({col})≠x({x})")
            
            print(f"{i:<4} {seat_no:<18} {row:<4} {y:<4} {col:<4} {x:<4} {', '.join(reasons)}")

def analyze_coordinate_patterns(all_seats):
    """分析坐标模式"""
    print(f"\n🗺️ 坐标模式分析:")
    print("=" * 60)
    
    # 按区域分组分析
    areas = {}
    for seat in all_seats:
        # 通过seat_no推断区域（这里简化处理）
        seat_no = seat['seat_no']
        area_key = f"y{seat['y']}_pattern"  # 按y坐标分组
        
        if area_key not in areas:
            areas[area_key] = []
        areas[area_key].append(seat)
    
    print(f"📋 发现的坐标模式:")
    
    for area_key, seats in sorted(areas.items()):
        if len(seats) < 3:  # 跳过座位太少的组
            continue
            
        # 分析这组座位的坐标规律
        y_values = [seat['y'] for seat in seats]
        row_values = [int(seat['row']) for seat in seats]
        
        y_unique = list(set(y_values))
        row_unique = list(set(row_values))
        
        print(f"\n  {area_key}: {len(seats)}个座位")
        print(f"    y值范围: {y_unique}")
        print(f"    row值范围: {row_unique}")
        
        # 检查是否有规律
        if len(y_unique) == 1 and len(row_unique) == 1:
            if y_unique[0] == row_unique[0]:
                print(f"    ✅ 规律: row = y = {y_unique[0]}")
            else:
                print(f"    ⚠️ 规律: row = {row_unique[0]}, y = {y_unique[0]} (不相等)")

def generate_corrected_conclusion(all_seats):
    """生成修正后的结论"""
    print(f"\n📋 修正后的座位数据结构分析结论:")
    print("=" * 80)
    
    # 重新统计
    total_seats = len(all_seats)
    row_y_matches = sum(1 for seat in all_seats if str(seat['row']) == str(seat['y']))
    col_x_matches = sum(1 for seat in all_seats if str(seat['col']) == str(seat['x']))
    
    type_stats = {}
    for seat in all_seats:
        seat_type = seat['type']
        type_stats[seat_type] = type_stats.get(seat_type, 0) + 1
    
    print(f"🔧 修正后的分析结果:")
    print(f"")
    print(f"1. ✅ seat_no: 确实是座位唯一标识符")
    print(f"   格式: 'ID#编号#位置' (如: 11051771#09#17)")
    print(f"")
    print(f"2. ⚠️ row vs y: 并非完全一致！")
    print(f"   匹配率: {row_y_matches}/{total_seats} ({row_y_matches/total_seats*100:.1f}%)")
    if row_y_matches/total_seats < 1.0:
        print(f"   🔍 结论: row和y有不同含义，可能分别表示逻辑排数和物理排数")
    else:
        print(f"   ✅ 结论: row和y基本一致")
    print(f"")
    print(f"3. ⚠️ col vs x: 并非完全一致！")
    print(f"   匹配率: {col_x_matches}/{total_seats} ({col_x_matches/total_seats*100:.1f}%)")
    if col_x_matches/total_seats < 1.0:
        print(f"   🔍 结论: col和x有不同含义，可能分别表示逻辑列数和物理列数")
    else:
        print(f"   ✅ 结论: col和x基本一致")
    print(f"")
    print(f"4. ✅ type字段: 确实表示座位类型")
    for seat_type, count in sorted(type_stats.items()):
        if seat_type == 0:
            print(f"   type=0: 普通座位 ({count}个)")
        elif seat_type in [1, 2]:
            print(f"   type={seat_type}: 情侣座 ({count}个)")
        else:
            print(f"   type={seat_type}: 未知类型 ({count}个)")
    print(f"")
    print(f"5. 📊 总体数据: {total_seats}个座位，分布在多个价格区域")
    print(f"")
    print(f"💡 重要发现:")
    print(f"  - 不同区域的座位可能使用不同的坐标系统")
    print(f"  - row/col 可能是逻辑坐标（用于系统内部计算）")
    print(f"  - x/y 可能是物理坐标（用于实际座位图显示）")
    print(f"  - 需要根据具体使用场景选择合适的坐标字段")

def main():
    """主函数"""
    seats = complete_seat_analysis()
    analyze_coordinate_patterns(seats)
    generate_corrected_conclusion(seats)
    
    print(f"\n🎉 完整分析完成！")
    print(f"📝 关键修正:")
    print(f"  ❌ 之前错误: row=y, col=x 完全一致")
    print(f"  ✅ 实际情况: row/col 与 x/y 在某些区域存在差异")
    print(f"  💡 建议: 根据实际需求选择使用 row/col 或 x/y")

if __name__ == "__main__":
    main()
