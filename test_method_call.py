#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试_cancel_unpaid_orders方法调用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_method_call():
    """测试方法调用"""
    print("=== 测试_cancel_unpaid_orders方法调用 ===")
    
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
        
        # 2. 创建主窗口实例并调用方法
        from ui.main_window import CinemaOrderSimulatorUI
        
        print("创建主窗口实例...")
        app = CinemaOrderSimulatorUI()
        
        print("直接调用_cancel_unpaid_orders方法...")
        app._cancel_unpaid_orders(test_account, test_account['cinemaid'])
        
        print("方法调用完成")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_method_call() 