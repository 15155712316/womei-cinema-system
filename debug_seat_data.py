#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试座位数据
保存座位图API返回的原始数据到JSON文件
"""

import json
import sys
import os
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_account():
    """加载账号数据"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            return accounts[0]
    except:
        pass
    
    return {}

def get_seat_map_data():
    """获取座位图数据"""
    print("🔍 获取座位图数据")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return None
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 创建服务实例
        service = get_womei_film_service(token)
        
        # 场次信息
        cinema_id = "400028"
        hall_id = "5"
        schedule_id = "16626081"
        
        print(f"🎬 场次信息:")
        print(f"  - 影院ID: {cinema_id}")
        print(f"  - 影厅ID: {hall_id}")
        print(f"  - 场次ID: {schedule_id}")
        print(f"  - Token: {token[:20]}...")
        
        # 获取座位图
        result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        if result.get('success'):
            hall_info = result.get('hall_info', {})
            
            print(f"✅ 座位图获取成功")
            print(f"  - hall_info keys: {list(hall_info.keys())}")
            
            return {
                'session_info': {
                    'cinema_id': cinema_id,
                    'hall_id': hall_id,
                    'schedule_id': schedule_id,
                    'token': token,
                    'timestamp': datetime.now().isoformat(),
                    'cinema_name': '北京沃美世界城店',
                    'hall_name': '5号厅 高亮激光厅'
                },
                'api_response': result,
                'hall_info': hall_info
            }
        else:
            error = result.get('error', '未知错误')
            print(f"❌ 座位图获取失败: {error}")
            return None
    
    except Exception as e:
        print(f"❌ 获取座位图异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_seat_data(seat_data):
    """分析座位数据结构"""
    print(f"\n🔍 分析座位数据结构")
    print("=" * 50)
    
    hall_info = seat_data.get('hall_info', {})
    room_seat = hall_info.get('room_seat', [])
    
    print(f"区域数量: {len(room_seat)}")
    
    all_seats = []
    area_summary = []
    
    for area_idx, area in enumerate(room_seat):
        area_no = area.get('area_no', f'area_{area_idx}')
        area_name = area.get('area_name', f'区域{area_idx}')
        seats_by_row = area.get('seats', {})
        
        area_seats = []
        for row_key, row_data in seats_by_row.items():
            row_detail = row_data.get('detail', [])
            for seat in row_detail:
                # 添加区域信息到座位数据
                seat['area_no'] = area_no
                seat['area_name'] = area_name
                area_seats.extend([seat])
                all_seats.append(seat)
        
        area_info = {
            'area_no': area_no,
            'area_name': area_name,
            'seat_count': len(area_seats),
            'sample_seats': area_seats[:3] if area_seats else []
        }
        area_summary.append(area_info)
        
        print(f"\n区域 {area_idx + 1}:")
        print(f"  - area_no: {area_no}")
        print(f"  - area_name: {area_name}")
        print(f"  - 座位数: {len(area_seats)}")
        
        if area_seats:
            print(f"  - 示例座位:")
            for i, seat in enumerate(area_seats[:3]):
                seat_no = seat.get('seat_no', 'N/A')
                row = seat.get('row', 'N/A')
                col = seat.get('col', 'N/A')
                status = seat.get('status', 'N/A')
                print(f"    {i+1}. row={row} col={col} seat_no={seat_no} status={status}")
    
    print(f"\n📊 总计:")
    print(f"  - 总区域数: {len(room_seat)}")
    print(f"  - 总座位数: {len(all_seats)}")
    print(f"  - 可用座位数: {len([s for s in all_seats if s.get('status') == 0])}")
    
    return {
        'area_summary': area_summary,
        'all_seats': all_seats,
        'available_seats': [s for s in all_seats if s.get('status') == 0]
    }

def save_seat_data_to_json(seat_data, analysis):
    """保存座位数据到JSON文件"""
    print(f"\n💾 保存座位数据到JSON文件")
    print("=" * 50)
    
    # 构建完整的调试数据
    debug_data = {
        'session_info': seat_data.get('session_info', {}),
        'api_response': seat_data.get('api_response', {}),
        'hall_info': seat_data.get('hall_info', {}),
        'analysis': analysis,
        'debug_notes': {
            'area_no_usage': '区域ID应该使用area_no字段，不是固定的1',
            'seat_no_format': 'seat_no应该是类似11051771#09#06的格式',
            'coordinate_mapping': 'row/col是逻辑位置，x/y是物理位置',
            'status_meaning': '0=可选，1=已售，2=锁定'
        }
    }
    
    # 保存到文件
    filename = 'data/座位调试数据.json'
    os.makedirs('data', exist_ok=True)
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(debug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 座位数据已保存到: {filename}")
        print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
        
        return filename
    
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return None

def test_seat_parameter_building(analysis):
    """测试座位参数构建"""
    print(f"\n🧪 测试座位参数构建")
    print("=" * 50)
    
    available_seats = analysis.get('available_seats', [])
    
    if len(available_seats) < 2:
        print("❌ 可用座位不足")
        return
    
    # 选择前2个可用座位
    selected_seats = available_seats[:2]
    
    print(f"选择的座位:")
    for i, seat in enumerate(selected_seats):
        print(f"  座位{i+1}完整数据: {seat}")
    
    # 🔧 修复：使用正确的area_no和seat_no
    seat_parts = []
    for i, seat in enumerate(selected_seats):
        area_no = seat.get('area_no', '1')  # 使用真实的area_no
        row = seat.get('row', '')
        col = seat.get('col', '')
        seat_no = seat.get('seat_no', '')  # 使用真实的seat_no
        
        print(f"\n座位{i+1}参数构建:")
        print(f"  - area_no: {area_no}")
        print(f"  - row: {row}")
        print(f"  - col: {col}")
        print(f"  - seat_no: {seat_no}")
        
        if not seat_no or '#' not in seat_no:
            print(f"  ❌ seat_no格式不正确: {seat_no}")
            continue
        
        # 沃美格式：area_no:row:col:seat_no
        seat_str = f"{area_no}:{row}:{col}:{seat_no}"
        seat_parts.append(seat_str)
        
        print(f"  ✅ 构建结果: {seat_str}")
    
    if seat_parts:
        seatlable = "|".join(seat_parts)
        print(f"\n🎯 最终座位参数: {seatlable}")
        
        # 对比之前的错误格式
        print(f"\n📋 格式对比:")
        print(f"  ❌ 错误格式: 1:3:4:16626083#09#04 (固定area_no=1, 构造的seat_no)")
        print(f"  ✅ 正确格式: {seatlable} (真实area_no, 真实seat_no)")
        
        return seatlable
    else:
        print(f"❌ 无法构建座位参数")
        return None

def main():
    """主函数"""
    print("🔧 座位数据调试工具")
    print("=" * 60)
    
    # 1. 获取座位图数据
    seat_data = get_seat_map_data()
    
    if not seat_data:
        print("❌ 无法获取座位图数据")
        return
    
    # 2. 分析座位数据结构
    analysis = analyze_seat_data(seat_data)
    
    # 3. 保存到JSON文件
    filename = save_seat_data_to_json(seat_data, analysis)
    
    # 4. 测试座位参数构建
    seatlable = test_seat_parameter_building(analysis)
    
    print(f"\n🎯 调试总结")
    print("=" * 60)
    
    if filename:
        print(f"✅ 调试数据已保存: {filename}")
    
    if seatlable:
        print(f"✅ 座位参数构建成功: {seatlable}")
    
    print(f"\n📋 发现的问题:")
    print(f"  1. ❌ 之前使用固定area_no=1，应该使用真实的area_no")
    print(f"  2. ❌ 之前构造seat_no，应该使用API返回的真实seat_no")
    print(f"  3. ✅ 现在使用正确的格式：area_no:row:col:seat_no")
    
    print(f"\n🔧 修复建议:")
    print(f"  1. 修改座位参数构建逻辑，使用seat.get('area_no')")
    print(f"  2. 确保从API返回数据中获取真实的seat_no")
    print(f"  3. 验证座位数据的original_data是否包含正确信息")

if __name__ == "__main__":
    main()
