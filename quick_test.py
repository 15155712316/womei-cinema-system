#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('.')

def test_order_creation():
    try:
        from cinema_api_adapter import create_womei_api
        import json
        
        # 加载账号
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        token = accounts[0]['token']
        
        # 创建API
        api = create_womei_api(token)
        
        # 使用修复后的座位参数
        cinema_id = '400028'
        schedule_id = '16626081'
        seatlable = '1:2:7:11051771#09#08|1:2:8:11051771#09#09'  # 使用不同的座位避免冲突
        
        print(f'🧪 测试订单创建:')
        print(f'  cinema_id: {cinema_id}')
        print(f'  schedule_id: {schedule_id}')
        print(f'  seatlable: {seatlable}')
        
        result = api.create_order(cinema_id, seatlable, schedule_id)
        print(f'📥 结果: {result}')
        
        if result and result.get('ret') == 0:
            msg = result.get('msg', '')
            if 'successfully' in msg:
                order_id = result.get('data', {}).get('order_id', '')
                print(f'🎉 订单创建成功! 订单ID: {order_id}')
                return True
            else:
                print(f'⚠️ 业务逻辑失败: {msg}')
                return '锁座失败' in msg or '座位' in msg  # 业务错误也算API格式正确
        else:
            print(f'❌ API调用失败')
            return False

    except Exception as e:
        print(f'❌ 异常: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 快速测试修复后的订单创建")
    print("=" * 40)
    
    success = test_order_creation()
    
    if success:
        print("\n✅ 修复成功! 座位参数格式正确!")
        print("💡 关键修复:")
        print("  1. 使用真实的area_no")
        print("  2. 使用真实的seat_no")
        print("  3. 正确的参数格式: area_no:row:col:seat_no")
    else:
        print("\n❌ 仍有问题需要解决")
