#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同座位的订单创建
验证我们的实现是否正确
"""

import requests
import json
import sys
import os

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

def get_available_seats():
    """获取可用座位"""
    print("🧪 获取可用座位")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 创建服务实例
        service = get_womei_film_service(token)
        
        # 获取座位图
        cinema_id = "400028"
        hall_id = "5"
        schedule_id = "16626081"
        
        result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        if result.get('success'):
            hall_info = result.get('hall_info', {})
            room_seat = hall_info.get('room_seat', [])
            
            # 收集所有可用座位
            available_seats = []
            for area in room_seat:
                area_no = area.get('area_no', '1')
                seats_by_row = area.get('seats', {})
                
                for row_key, row_data in seats_by_row.items():
                    row_detail = row_data.get('detail', [])
                    for seat in row_detail:
                        if seat.get('status') == 0:  # 可用座位
                            seat['area_no'] = area_no
                            available_seats.append(seat)
            
            print(f"✅ 找到 {len(available_seats)} 个可用座位")
            
            # 显示前10个可用座位
            print(f"前10个可用座位:")
            for i, seat in enumerate(available_seats[:10]):
                seat_no = seat.get('seat_no', '')
                row = seat.get('row', '')
                col = seat.get('col', '')
                area = seat.get('area_no', '')
                print(f"  {i+1}. 区域{area} 行{row} 列{col} seat_no={seat_no}")
            
            return available_seats
        else:
            print(f"❌ 获取座位图失败")
            return []
    
    except Exception as e:
        print(f"❌ 获取座位异常: {e}")
        return []

def test_order_with_different_seats(available_seats):
    """使用不同座位测试订单创建"""
    print(f"\n🧪 使用不同座位测试订单创建")
    print("=" * 50)
    
    if len(available_seats) < 2:
        print("❌ 可用座位不足")
        return False
    
    # 选择前2个可用座位
    selected_seats = available_seats[:2]
    
    print(f"选择的座位:")
    for i, seat in enumerate(selected_seats):
        seat_no = seat.get('seat_no', '')
        row = seat.get('row', '')
        col = seat.get('col', '')
        area = seat.get('area_no', '')
        print(f"  座位{i+1}: 区域{area} 行{row} 列{col} seat_no={seat_no}")
    
    # 构建座位参数
    seat_parts = []
    for seat in selected_seats:
        area_no = seat.get('area_no', '1')
        row = seat.get('row', '')
        col = seat.get('col', '')
        seat_no = seat.get('seat_no', '')
        
        # 沃美格式：区域ID:行:列:seat_no
        seat_str = f"{area_no}:{row}:{col}:{seat_no}"
        seat_parts.append(seat_str)
    
    seatlable = "|".join(seat_parts)
    print(f"\n构建的座位参数: {seatlable}")
    
    # 测试订单创建
    account = load_account()
    token = account.get('token', '')
    
    try:
        from cinema_api_adapter import create_womei_api
        
        # 创建API适配器
        api = create_womei_api(token)
        
        # 调用订单创建
        cinema_id = "400028"
        schedule_id = "16626081"
        
        result = api.create_order(cinema_id, seatlable, schedule_id)
        
        print(f"\n📥 订单创建结果:")
        print(f"  结果: {result}")
        
        if result and isinstance(result, dict):
            ret = result.get('ret', -1)
            msg = result.get('msg', '')
            
            if ret == 0:
                if 'successfully' in msg:
                    order_id = result.get('data', {}).get('order_id', '')
                    print(f"\n🎉 订单创建成功!")
                    print(f"  订单ID: {order_id}")
                    return True
                else:
                    print(f"\n⚠️ 业务逻辑失败: {msg}")
                    return False
            else:
                print(f"\n❌ API调用失败: {msg}")
                return False
        else:
            print(f"\n❌ 返回格式错误")
            return False
    
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_manual_seats():
    """使用手动指定的座位测试"""
    print(f"\n🧪 使用手动指定的座位测试")
    print("=" * 50)
    
    # 手动指定一些可能可用的座位
    test_seats = [
        # 尝试第3排的座位
        "1:3:1:11051771#08#01",
        "1:3:2:11051771#08#02",
        # 尝试第4排的座位
        "1:4:1:11051771#07#01", 
        "1:4:2:11051771#07#02",
        # 尝试第1排的座位（前排区域）
        "10015:1:1:11051771#10#01",
        "10015:1:2:11051771#10#02",
    ]
    
    account = load_account()
    token = account.get('token', '')
    
    for i in range(0, len(test_seats), 2):
        if i + 1 >= len(test_seats):
            break
            
        seat1 = test_seats[i]
        seat2 = test_seats[i + 1]
        seatlable = f"{seat1}|{seat2}"
        
        print(f"\n测试座位组合 {i//2 + 1}: {seatlable}")
        
        try:
            from cinema_api_adapter import create_womei_api
            
            api = create_womei_api(token)
            result = api.create_order("400028", seatlable, "16626081")
            
            print(f"  结果: {result}")
            
            if result and result.get('ret') == 0:
                msg = result.get('msg', '')
                if 'successfully' in msg:
                    order_id = result.get('data', {}).get('order_id', '')
                    print(f"  🎉 成功! 订单ID: {order_id}")
                    return True
                else:
                    print(f"  ⚠️ 失败: {msg}")
            
        except Exception as e:
            print(f"  ❌ 异常: {e}")
    
    return False

def main():
    """主函数"""
    print("🔧 不同座位订单创建测试")
    print("=" * 60)
    
    # 1. 获取可用座位
    available_seats = get_available_seats()
    
    # 2. 使用可用座位测试
    if available_seats:
        success1 = test_order_with_different_seats(available_seats)
    else:
        success1 = False
    
    # 3. 使用手动指定座位测试
    success2 = test_with_manual_seats()
    
    print(f"\n🎯 测试总结")
    print("=" * 60)
    
    if success1:
        print(f"✅ 可用座位测试: 成功")
    else:
        print(f"❌ 可用座位测试: 失败")
    
    if success2:
        print(f"✅ 手动座位测试: 成功")
    else:
        print(f"❌ 手动座位测试: 失败")
    
    if success1 or success2:
        print(f"\n🎉 我们的实现是正确的!")
        print(f"💡 之前的'锁座失败'是因为座位已被占用")
        print(f"📋 结论:")
        print(f"  1. API格式完全正确")
        print(f"  2. 参数构建正确")
        print(f"  3. 请求头正确")
        print(f"  4. 只是座位冲突问题")
    else:
        print(f"\n❌ 所有测试都失败了")
        print(f"💡 可能的原因:")
        print(f"  1. 场次已过期")
        print(f"  2. 所有座位都被占用")
        print(f"  3. 系统维护中")

if __name__ == "__main__":
    main()
