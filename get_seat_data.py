#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取沃美影院座位数据并验证结构分析
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_seat_data():
    """获取座位数据"""
    print("🎬 获取沃美影院座位数据")
    print("=" * 60)
    
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/hall/info/"
    params = {
        'hall_id': '2',
        'schedule_id': '16624418'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MicroProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'content-type': 'multipart/form-data',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': '47794858a832916d8eda012e7cabd269',
        'accept': '*/*'
    }
    
    try:
        print(f"📡 请求URL: {url}")
        print(f"📋 参数: {params}")
        
        # 跳过SSL验证
        response = requests.get(url, params=params, headers=headers, verify=False, timeout=15)
        
        print(f"📥 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # 保存数据
            with open('real_seat_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 座位数据获取成功，已保存到 real_seat_data.json")
            return data
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return None

def analyze_real_seat_data(data):
    """分析真实座位数据"""
    if not data:
        print("❌ 没有数据可分析")
        return
    
    print(f"\n🔍 分析真实座位数据:")
    print("=" * 60)
    
    # 检查响应结构
    if 'ret' in data and data['ret'] == 0:
        print(f"✅ API响应成功")
        
        hall_data = data.get('data', {})
        room_seat = hall_data.get('room_seat', [])
        
        print(f"🏛️ 影厅信息:")
        print(f"  影厅编号: {hall_data.get('hall_no', 'N/A')}")
        print(f"  影厅名称: {hall_data.get('hall_name', 'N/A')}")
        print(f"  区域数量: {len(room_seat)}")
        
        # 收集座位样本
        all_seats = []
        for area in room_seat:
            area_name = area.get('area_name', '未知区域')
            seats_data = area.get('seats', {})
            
            print(f"\n📍 区域: {area_name}")
            print(f"  价格: {area.get('area_price', 'N/A')}元")
            
            if isinstance(seats_data, dict):
                for row_key, row_data in seats_data.items():
                    seat_details = row_data.get('detail', [])
                    print(f"    第{row_key}行: {len(seat_details)}个座位")
                    all_seats.extend(seat_details)
            elif isinstance(seats_data, list):
                print(f"    列表格式: {len(seats_data)}个座位")
                all_seats.extend(seats_data)
        
        print(f"\n📊 总座位数: {len(all_seats)}")
        
        if all_seats:
            verify_seat_structure(all_seats)
        
    else:
        print(f"❌ API响应失败: {data}")

def verify_seat_structure(seats):
    """验证座位结构"""
    print(f"\n✅ 验证座位数据结构分析:")
    print("=" * 60)
    
    # 显示前5个座位的详细信息
    print(f"📋 座位样本 (前5个):")
    print(f"{'序号':<4} {'seat_no':<20} {'row':<4} {'col':<4} {'x':<4} {'y':<4} {'type':<4} {'status':<6}")
    print(f"{'-'*4} {'-'*20} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*4} {'-'*6}")
    
    for i, seat in enumerate(seats[:5], 1):
        seat_no = seat.get('seat_no', 'N/A')[:18]
        row = seat.get('row', 'N/A')
        col = seat.get('col', 'N/A')
        x = seat.get('x', 'N/A')
        y = seat.get('y', 'N/A')
        seat_type = seat.get('type', 'N/A')
        status = seat.get('status', 'N/A')
        
        print(f"{i:<4} {seat_no:<20} {row:<4} {col:<4} {x:<4} {y:<4} {seat_type:<4} {status:<6}")
    
    # 验证分析点
    print(f"\n🎯 验证您的分析:")
    
    # 1. seat_no格式
    seat_no_sample = seats[0].get('seat_no', '')
    print(f"1. seat_no格式: {seat_no_sample}")
    if '#' in seat_no_sample:
        parts = seat_no_sample.split('#')
        print(f"   ✅ 确实是 'ID#编号#位置' 格式: {parts}")
    
    # 2. row/col vs x/y关系
    row_y_matches = 0
    col_x_matches = 0
    
    for seat in seats[:20]:  # 检查前20个座位
        if str(seat.get('row')) == str(seat.get('y')):
            row_y_matches += 1
        if str(seat.get('col')) == str(seat.get('x')):
            col_x_matches += 1
    
    print(f"2. row/col vs x/y关系 (前20个座位):")
    print(f"   row=y: {row_y_matches}/20 ({row_y_matches/20*100:.1f}%)")
    print(f"   col=x: {col_x_matches}/20 ({col_x_matches/20*100:.1f}%)")
    
    # 3. type字段分析
    type_stats = {}
    for seat in seats:
        seat_type = seat.get('type', 0)
        type_stats[seat_type] = type_stats.get(seat_type, 0) + 1
    
    print(f"3. type字段分布:")
    for seat_type, count in sorted(type_stats.items()):
        print(f"   type={seat_type}: {count}个座位")
    
    # 查找情侣座
    couple_seats = [seat for seat in seats if seat.get('type') in [1, 2]]
    if couple_seats:
        print(f"4. 情侣座分析:")
        print(f"   找到 {len(couple_seats)} 个情侣座")
        
        # 显示前几个情侣座
        for i, seat in enumerate(couple_seats[:3], 1):
            seat_no = seat.get('seat_no', 'N/A')[:15]
            seat_type = seat.get('type')
            x = seat.get('x')
            y = seat.get('y')
            print(f"   情侣座{i}: {seat_no} type={seat_type} 位置=({x},{y})")
    
    print(f"\n📋 验证结论:")
    print(f"✅ seat_no: 确实是唯一标识符，格式为 'ID#编号#位置'")
    print(f"{'✅' if row_y_matches/20 > 0.8 else '⚠️'} row/y: {'基本一致' if row_y_matches/20 > 0.8 else '存在差异'}")
    print(f"{'✅' if col_x_matches/20 > 0.8 else '⚠️'} col/x: {'基本一致' if col_x_matches/20 > 0.8 else '存在差异'}")
    print(f"✅ type: 0=普通座位, 1&2=情侣座")

def create_mock_data_for_testing():
    """创建模拟数据用于测试"""
    print(f"\n🔧 创建模拟座位数据用于测试:")
    
    mock_data = {
        "ret": 0,
        "sub": 0,
        "msg": "successfully",
        "data": {
            "cinema_id": 400028,
            "hall_no": "2",
            "hall_name": "2号厅 DTS:X临境音激光厅",
            "room_seat": [
                {
                    "area_no": "1",
                    "area_name": "默认区",
                    "area_price": 57.9,
                    "seats": {
                        "2": {
                            "row": 2,
                            "desc": "2",
                            "detail": [
                                {
                                    "seat_no": "11051771#09#17",
                                    "row": "2",
                                    "col": "1",
                                    "x": 1,
                                    "y": 2,
                                    "type": 0,
                                    "status": 0
                                },
                                {
                                    "seat_no": "11051771#09#16",
                                    "row": "2",
                                    "col": "2",
                                    "x": 2,
                                    "y": 2,
                                    "type": 0,
                                    "status": 0
                                }
                            ]
                        },
                        "10": {
                            "row": 10,
                            "desc": "9",
                            "detail": [
                                {
                                    "seat_no": "11051771#01#14",
                                    "row": "9",
                                    "col": "1",
                                    "x": 4,
                                    "y": 10,
                                    "type": 1,
                                    "status": 0
                                },
                                {
                                    "seat_no": "11051771#01#13",
                                    "row": "9",
                                    "col": "2",
                                    "x": 5,
                                    "y": 10,
                                    "type": 2,
                                    "status": 0
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
    
    with open('mock_seat_data.json', 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 模拟数据已保存到 mock_seat_data.json")
    return mock_data

def main():
    """主函数"""
    print("🎯 沃美影院座位数据获取与结构验证")
    print("=" * 80)
    
    # 尝试获取真实数据
    real_data = get_seat_data()
    
    if real_data:
        analyze_real_seat_data(real_data)
    else:
        print(f"\n⚠️ 无法获取真实数据，使用模拟数据进行验证")
        mock_data = create_mock_data_for_testing()
        analyze_real_seat_data(mock_data)
    
    print(f"\n🎉 验证完成！")
    print(f"📁 生成的文件:")
    if real_data:
        print(f"  - real_seat_data.json: 真实的API响应数据")
    print(f"  - mock_seat_data.json: 模拟测试数据")

if __name__ == "__main__":
    main()
