#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试取消未付款订单功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cancel_unpaid_orders():
    """测试取消未付款订单功能"""
    print("=== 测试取消未付款订单功能 ===")
    
    try:
        # 1. 加载账号信息
        import json
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        
        # 找到华夏优加荟大都荟账号（cinemaid: 35fec8259e74）
        test_account = None
        for acc in accounts:
            if acc.get('cinemaid') == '35fec8259e74':
                test_account = acc
                break
        
        if not test_account:
            print("❌ 未找到华夏优加荟大都荟账号")
            return
        
        print(f"✓ 找到测试账号: {test_account.get('userid')}")
        print(f"✓ 影院ID: {test_account.get('cinemaid')}")
        print(f"✓ Token: {test_account.get('token', '')[:10]}...")
        
        # 2. 测试取消未付款订单功能
        from services.order_api import cancel_all_unpaid_orders
        
        cinemaid = test_account['cinemaid']
        
        print(f"\n🔍 开始测试取消未付款订单功能")
        print(f"影院: 华夏优加荟大都荟 ({cinemaid})")
        print(f"用户: {test_account['userid']}")
        
        # 调用取消未付款订单函数
        result = cancel_all_unpaid_orders(test_account, cinemaid)
        
        print(f"\n📥 取消结果: {result}")
        
        if result and result.get('resultCode') == '0':
            cancelled_count = result.get('cancelledCount', 0)
            print(f"✅ 取消未付款订单成功！取消了 {cancelled_count} 个订单")
        else:
            print(f"❌ 取消未付款订单失败")
            if result:
                print(f"错误描述: {result.get('resultDesc', '未知错误')}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cancel_unpaid_orders() 