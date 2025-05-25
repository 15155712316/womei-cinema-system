#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看订单列表的详细数据结构
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_order_structure():
    """测试订单数据结构"""
    print("=== 查看订单列表详细数据结构 ===")
    
    try:
        # 1. 加载账号信息
        import json
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        
        # 找到华夏优加荟大都荟账号
        test_account = None
        for acc in accounts:
            if acc.get('cinemaid') == '35fec8259e74':
                test_account = acc
                break
        
        if not test_account:
            print("❌ 未找到华夏优加荟大都荟账号")
            return
        
        print(f"✓ 找到测试账号: {test_account.get('userid')}")
        
        # 2. 调用订单列表接口
        params = {
            'pageNo': 1,
            'groupid': '',
            'cinemaid': test_account['cinemaid'],
            'cardno': test_account.get('cardno', ''),
            'userid': test_account['userid'],
            'openid': test_account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': test_account['token'],
            'source': '2'
        }
        
        from services.order_api import get_order_list
        result = get_order_list(params)
        
        print(f"\n📋 API调用结果:")
        print(f"resultCode: {result.get('resultCode')}")
        print(f"resultDesc: {result.get('resultDesc')}")
        
        if result.get('resultCode') == '0':
            data = result.get('resultData', {})
            orders = data.get('orders', [])
            
            print(f"\n📊 订单数据概况:")
            print(f"总订单数: {len(orders)}")
            
            if orders:
                print(f"\n📋 详细订单数据结构:")
                
                # 分析所有订单的字段
                all_fields = set()
                status_values = set()
                
                for i, order in enumerate(orders):
                    print(f"\n--- 订单 {i+1} ---")
                    for key, value in order.items():
                        print(f"  {key}: {value}")
                        all_fields.add(key)
                        
                        # 收集可能的状态字段
                        if 'status' in key.lower() or 'state' in key.lower() or key.lower() in ['orders', 'orderstatus']:
                            status_values.add(f"{key}={value}")
                
                print(f"\n🔍 所有字段汇总:")
                print(f"字段列表: {sorted(all_fields)}")
                
                print(f"\n🔍 可能的状态字段值:")
                for status in sorted(status_values):
                    print(f"  {status}")
                
                # 特别检查orderS字段
                orders_field_values = [order.get('orderS', '无') for order in orders]
                unique_orders_values = set(orders_field_values)
                
                print(f"\n📊 orderS字段值统计:")
                for value in unique_orders_values:
                    count = orders_field_values.count(value)
                    print(f"  '{value}': {count}个订单")
                
                # 检查可能的未付款订单状态
                possible_unpaid_statuses = ['未付款', '待付款', '未支付', 'unpaid', 'pending']
                unpaid_orders = []
                
                for status in possible_unpaid_statuses:
                    found_orders = [order for order in orders if 
                                  any(str(v).lower() == status.lower() for v in order.values())]
                    if found_orders:
                        print(f"\n✓ 找到状态为'{status}'的订单: {len(found_orders)}个")
                        unpaid_orders.extend(found_orders)
                    else:
                        print(f"  ✗ 未找到状态为'{status}'的订单")
                
                if unpaid_orders:
                    print(f"\n📋 疑似未付款订单:")
                    for order in unpaid_orders[:3]:  # 只显示前3个
                        orderno = order.get('orderno', '无订单号')
                        name = order.get('orderName', '无名称')
                        status = order.get('orderS', '无状态')
                        print(f"  - {orderno} | {name} | {status}")
                else:
                    print(f"\n❌ 未找到任何未付款订单")
                    
                    # 如果没找到，显示所有订单的状态
                    print(f"\n📋 所有订单状态:")
                    for order in orders:
                        orderno = order.get('orderno', '无订单号')
                        name = order.get('orderName', '无名称')
                        status = order.get('orderS', '无状态')
                        print(f"  - {orderno} | {name} | {status}")
            
            else:
                print("❌ 没有订单数据")
        else:
            print(f"❌ 获取订单列表失败: {result.get('resultDesc')}")
    
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_structure() 