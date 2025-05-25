#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前会话的待支付订单数量和取消功能测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_current_session():
    """测试当前会话状态"""
    print("=== 检查当前待支付订单状态 ===")
    
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
        
        # 2. 获取当前订单列表
        from services.order_api import get_order_list
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
        
        result = get_order_list(params)
        
        if result.get('resultCode') == '0':
            orders = result.get('resultData', {}).get('orders', [])
            pending_orders = [order for order in orders if order.get('orderS') == '待付款']
            
            print(f"\n📊 当前订单状态:")
            print(f"总订单数: {len(orders)}")
            print(f"待付款订单数: {len(pending_orders)}")
            
            if pending_orders:
                print(f"\n📋 待付款订单详情:")
                for i, order in enumerate(pending_orders, 1):
                    orderno = order.get('orderno', '无订单号')
                    name = order.get('orderName', '无名称')
                    timeout = order.get('orderTimeOutDate', '无超时时间')
                    print(f"  {i}. {orderno} | {name} | 超时时间: {timeout}")
                
                # 3. 测试取消功能 - 使用修复后的cancel_order
                print(f"\n🔧 测试修复后的取消订单功能:")
                
                from services.order_api import cancel_order
                for i, order in enumerate(pending_orders, 1):
                    orderno = order.get('orderno')
                    print(f"\n--- 测试取消订单 {i}: {orderno} ---")
                    
                    cancel_params = {
                        'orderno': orderno,
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
                    
                    cancel_result = cancel_order(cancel_params)
                    print(f"取消结果: {cancel_result}")
                    
                    if cancel_result.get('resultCode') == '0':
                        print(f"✅ 订单 {orderno} 取消成功")
                    else:
                        error_desc = cancel_result.get('resultDesc', '未知错误')
                        print(f"❌ 订单 {orderno} 取消失败: {error_desc}")
                
                # 4. 再次检查订单列表，确认取消效果
                print(f"\n🔍 再次检查订单列表:")
                result2 = get_order_list(params)
                
                if result2.get('resultCode') == '0':
                    orders2 = result2.get('resultData', {}).get('orders', [])
                    pending_orders2 = [order for order in orders2 if order.get('orderS') == '待付款']
                    
                    print(f"取消后总订单数: {len(orders2)}")
                    print(f"取消后待付款订单数: {len(pending_orders2)}")
                    
                    if len(pending_orders2) < len(pending_orders):
                        cancelled_count = len(pending_orders) - len(pending_orders2)
                        print(f"✅ 成功取消了 {cancelled_count} 个订单")
                    elif len(pending_orders2) == len(pending_orders):
                        print(f"⚠️ 订单数量没有变化，可能取消失败")
                    else:
                        print(f"❓ 订单数量异常变化")
                        
            else:
                print(f"✅ 当前没有待付款订单")
                
                # 显示所有订单状态
                print(f"\n📋 所有订单状态:")
                for order in orders:
                    orderno = order.get('orderno', '无订单号')
                    name = order.get('orderName', '无名称')
                    status = order.get('orderS', '无状态')
                    print(f"  - {orderno} | {name} | {status}")
        else:
            print(f"❌ 获取订单列表失败: {result.get('resultDesc')}")
    
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_session() 