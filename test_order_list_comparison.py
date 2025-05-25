#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比取消未付款订单和订单列表的API调用参数
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_order_list_params():
    """测试订单列表参数对比"""
    print("=== 对比订单列表API调用参数 ===")
    
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
        print(f"✓ 账号详情: {test_account}")
        
        cinemaid = test_account['cinemaid']
        
        # 2. 构建cancel_all_unpaid_orders中的参数
        cancel_params = {
            'pageNo': 1,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': test_account.get('cardno', ''),
            'userid': test_account['userid'],
            'openid': test_account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': test_account['token'],
            'source': '2'
        }
        
        # 3. 构建refresh_order_list中的参数（模拟主窗口中的逻辑）
        refresh_params = {
            'pageNo': 1,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': test_account.get('cardno', ''),
            'userid': test_account['userid'],
            'openid': test_account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': test_account['token'],
            'source': '2'
        }
        
        print(f"\n📋 cancel_all_unpaid_orders参数:")
        for key, value in cancel_params.items():
            print(f"  {key}: {value}")
        
        print(f"\n📋 refresh_order_list参数:")
        for key, value in refresh_params.items():
            print(f"  {key}: {value}")
        
        # 4. 对比参数差异
        print(f"\n🔍 参数差异对比:")
        all_keys = set(cancel_params.keys()) | set(refresh_params.keys())
        has_diff = False
        
        for key in sorted(all_keys):
            cancel_val = cancel_params.get(key, '<缺失>')
            refresh_val = refresh_params.get(key, '<缺失>')
            
            if cancel_val != refresh_val:
                print(f"  ❌ {key}: cancel='{cancel_val}' vs refresh='{refresh_val}'")
                has_diff = True
            else:
                print(f"  ✓ {key}: '{cancel_val}'")
        
        if not has_diff:
            print(f"  ✅ 所有参数完全一致")
        
        # 5. 分别调用两个接口测试
        from services.order_api import get_order_list
        
        print(f"\n🔍 测试cancel_all_unpaid_orders中的get_order_list调用:")
        result1 = get_order_list(cancel_params)
        
        if result1.get('resultCode') == '0':
            orders1 = result1.get('resultData', {}).get('orders', [])
            unpaid_orders1 = [order for order in orders1 if order.get('orderS') == '未付款']
            print(f"  ✓ 总订单数: {len(orders1)}")
            print(f"  ✓ 未付款订单数: {len(unpaid_orders1)}")
            
            if unpaid_orders1:
                print(f"  📋 未付款订单列表:")
                for order in unpaid_orders1[:3]:  # 只显示前3个
                    print(f"    - {order.get('orderno')} | {order.get('orderName', '')} | {order.get('orderS', '')}")
        else:
            print(f"  ❌ 获取订单列表失败: {result1.get('resultDesc')}")
        
        print(f"\n🔍 测试refresh_order_list调用:")
        result2 = get_order_list(refresh_params)
        
        if result2.get('resultCode') == '0':
            orders2 = result2.get('resultData', {}).get('orders', [])
            unpaid_orders2 = [order for order in orders2 if order.get('orderS') == '未付款']
            print(f"  ✓ 总订单数: {len(orders2)}")
            print(f"  ✓ 未付款订单数: {len(unpaid_orders2)}")
            
            if unpaid_orders2:
                print(f"  📋 未付款订单列表:")
                for order in unpaid_orders2[:3]:  # 只显示前3个
                    print(f"    - {order.get('orderno')} | {order.get('orderName', '')} | {order.get('orderS', '')}")
        else:
            print(f"  ❌ 获取订单列表失败: {result2.get('resultDesc')}")
        
        # 6. 对比结果
        if result1.get('resultCode') == '0' and result2.get('resultCode') == '0':
            orders1 = result1.get('resultData', {}).get('orders', [])
            orders2 = result2.get('resultData', {}).get('orders', [])
            unpaid_count1 = len([o for o in orders1 if o.get('orderS') == '未付款'])
            unpaid_count2 = len([o for o in orders2 if o.get('orderS') == '未付款'])
            
            print(f"\n📊 结果对比:")
            print(f"  cancel_all_unpaid_orders: 找到 {unpaid_count1} 个未付款订单")
            print(f"  refresh_order_list: 找到 {unpaid_count2} 个未付款订单")
            
            if unpaid_count1 != unpaid_count2:
                print(f"  ❌ 未付款订单数量不一致！可能存在参数问题")
            else:
                print(f"  ✅ 未付款订单数量一致")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_order_list_params() 