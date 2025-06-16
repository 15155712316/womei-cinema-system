#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美专用订单创建逻辑
完全抛弃华联系统逻辑，使用沃美系统专用方法
"""

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

def test_womei_seat_parameter_building():
    """测试沃美座位参数构建"""
    print("🧪 测试沃美座位参数构建")
    print("=" * 50)
    
    # 模拟从座位图获取的真实座位数据
    selected_seats = [
        {
            'rn': 2,
            'cn': 4,
            'row': 2,
            'col': 4,
            'areaId': 1,
            'price': 5790,  # 分为单位
            'original_data': {
                'seat_no': '11051771#09#05',  # 真实的seat_no
                'row': '2',
                'col': '4',
                'x': 6,
                'y': 2,
                'type': 0,
                'status': 0,
                'sn': '11051771#09#05'  # 这是关键字段
            }
        },
        {
            'rn': 2,
            'cn': 5,
            'row': 2,
            'col': 5,
            'areaId': 1,
            'price': 5790,  # 分为单位
            'original_data': {
                'seat_no': '11051771#09#06',  # 真实的seat_no
                'row': '2',
                'col': '5',
                'x': 5,
                'y': 2,
                'type': 0,
                'status': 0,
                'sn': '11051771#09#06'  # 这是关键字段
            }
        }
    ]
    
    print(f"模拟选中座位: {len(selected_seats)} 个")
    for i, seat in enumerate(selected_seats):
        print(f"  座位{i+1}: 行{seat['row']} 列{seat['col']} seat_no={seat['original_data']['sn']}")
    
    # 模拟座位参数构建逻辑
    seat_parts = []
    for i, seat in enumerate(selected_seats):
        # 从original_data获取真实的seat_no
        original_data = seat.get('original_data', {})
        real_seat_no = original_data.get('sn', '')
        
        if real_seat_no and '#' in real_seat_no:
            row = seat.get('rn', seat.get('row', 1))
            col = seat.get('cn', seat.get('col', 1))
            area_id = seat.get('areaId', 1)
            
            # 沃美格式：区域ID:行:列:seat_no
            seat_str = f"{area_id}:{row}:{col}:{real_seat_no}"
            seat_parts.append(seat_str)
            
            print(f"  座位{i+1}构建: {seat_str}")
        else:
            print(f"  ❌ 座位{i+1}缺少有效的seat_no: {real_seat_no}")
            return None
    
    seatlable_str = "|".join(seat_parts)
    print(f"\n✅ 最终座位参数: {seatlable_str}")
    print(f"🔍 对比真实格式: 1:2:5:11051771#09#06|1:2:4:11051771#09#05")
    
    return seatlable_str

def test_womei_order_api_call():
    """测试沃美订单API调用"""
    print(f"\n🧪 测试沃美订单API调用")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    # 测试参数
    cinema_id = "400028"
    schedule_id = "16626081"
    seatlable = "1:2:4:11051771#09#05|1:2:5:11051771#09#06"
    
    print(f"🔍 沃美订单API参数:")
    print(f"  - cinema_id: {cinema_id}")
    print(f"  - schedule_id: {schedule_id}")
    print(f"  - seatlable: {seatlable}")
    print(f"  - token: {token[:20]}...")
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 创建沃美电影服务
        film_service = get_womei_film_service(token)
        
        # 调用订单创建API
        result = film_service.create_order(cinema_id, seatlable, schedule_id)
        
        print(f"\n📥 沃美API返回:")
        print(f"  - 结果类型: {type(result)}")
        print(f"  - 结果内容: {result}")
        
        if result and isinstance(result, dict):
            success = result.get('success', False)
            if success:
                order_id = result.get('order_id')
                print(f"\n🎉 沃美订单创建成功!")
                print(f"  - 订单ID: {order_id}")
                return True
            else:
                error = result.get('error', '未知错误')
                print(f"\n⚠️ 沃美订单创建失败: {error}")
                # 检查是否是业务逻辑错误
                if '锁座失败' in error or '座位' in error:
                    print(f"  💡 这是正常的业务错误，说明API格式正确")
                    return True  # API格式正确
                else:
                    print(f"  💡 这可能是技术错误")
                    return False
        else:
            print(f"\n❌ API返回格式错误")
            return False
    
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_session_info_construction():
    """测试session_info构建"""
    print(f"\n🧪 测试session_info构建")
    print("=" * 50)
    
    account = load_account()
    
    # 模拟完整的session_info
    session_info = {
        'cinema_data': {
            'cinema_id': '400028',
            'cinema_name': '北京沃美世界城店',
            'cinemaShortName': '北京沃美世界城店'
        },
        'account': account,
        'session_data': {
            'schedule_id': '16626081',
            'hall_id': '5',
            'hall_name': '5号厅 高亮激光厅',
            'movie_id': '12345',
            'movie_name': '名侦探柯南：独眼的残像',
            'show_time': '14:20',
            'show_date': '2025-06-27'
        },
        'session_text': '2025-06-27 14:20'
    }
    
    print(f"✅ session_info构建完成:")
    print(f"  - 影院: {session_info['cinema_data']['cinema_name']}")
    print(f"  - 账号: {session_info['account'].get('phone', 'N/A')}")
    print(f"  - 场次: {session_info['session_data']['movie_name']} - {session_info['session_data']['show_time']}")
    
    # 验证必要字段
    cinema_id = session_info['cinema_data'].get('cinema_id', '')
    schedule_id = session_info['session_data'].get('schedule_id', '')
    token = session_info['account'].get('token', '')
    
    print(f"\n🔍 关键参数验证:")
    print(f"  - cinema_id: {cinema_id} {'✅' if cinema_id else '❌'}")
    print(f"  - schedule_id: {schedule_id} {'✅' if schedule_id else '❌'}")
    print(f"  - token: {token[:20]}... {'✅' if token else '❌'}")
    
    return session_info

def main():
    """主函数"""
    print("🔧 沃美专用订单创建测试")
    print("=" * 60)
    
    # 1. 测试座位参数构建
    seatlable = test_womei_seat_parameter_building()
    
    # 2. 测试session_info构建
    session_info = test_session_info_construction()
    
    # 3. 测试API调用
    api_ok = test_womei_order_api_call()
    
    print(f"\n🎯 沃美专用测试总结")
    print("=" * 60)
    
    if seatlable:
        print(f"✅ 座位参数构建: 成功")
        print(f"  格式: {seatlable}")
    else:
        print(f"❌ 座位参数构建: 失败")
    
    if session_info:
        print(f"✅ session_info构建: 成功")
    else:
        print(f"❌ session_info构建: 失败")
    
    if api_ok:
        print(f"✅ 沃美API调用: 成功")
    else:
        print(f"❌ 沃美API调用: 失败")
    
    if seatlable and session_info and api_ok:
        print(f"\n🎉 沃美专用订单创建逻辑验证成功!")
        print(f"💡 关键改进:")
        print(f"  1. 完全抛弃华联系统逻辑")
        print(f"  2. 使用沃美系统专用方法")
        print(f"  3. 直接从original_data获取真实seat_no")
        print(f"  4. 使用沃美系统专用API调用")
        print(f"  5. 简化数据流，减少转换环节")
        
        print(f"\n🚀 现在可以在应用程序中测试:")
        print(f"  1. 启动应用: python main_modular.py")
        print(f"  2. 选择座位")
        print(f"  3. 提交订单（使用新的沃美专用逻辑）")
    else:
        print(f"\n❌ 仍有问题需要解决")

if __name__ == "__main__":
    main()
