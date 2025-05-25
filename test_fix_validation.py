#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证券绑定修复：测试GET请求是否解决TOKEN_INVALID问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def quick_test_bind_coupon():
    """快速测试券绑定修复"""
    print("=== 券绑定修复验证 ===")
    
    try:
        # 1. 加载万友影城账号（余额400，积分3833的账号）
        import json
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        
        # 找到万友影城账号（cinemaid: 0f1e21d86ac8）
        wanyou_account = None
        for acc in accounts:
            if acc.get('cinemaid') == '0f1e21d86ac8' and acc.get('balance') == 400:
                wanyou_account = acc
                break
        
        if not wanyou_account:
            print("❌ 未找到万友影城账号（余额400的账号）")
            return
        
        print(f"✓ 找到万友影城账号: {wanyou_account.get('userid')}")
        print(f"✓ 余额: {wanyou_account.get('balance')}, 积分: {wanyou_account.get('score')}")
        print(f"✓ Token: {wanyou_account.get('token', '')[:10]}...")
        
        # 2. 测试券绑定（使用GET请求）
        from services.order_api import bind_coupon
        
        test_coupon = "54938139116"  # 用户提供的第一个券号
        
        bind_params = {
            'couponcode': test_coupon,
            'cinemaid': wanyou_account['cinemaid'],
            'userid': wanyou_account['userid'],
            'openid': wanyou_account['openid'],
            'token': wanyou_account['token'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2',
            'groupid': '',
            'cardno': wanyou_account.get('cardno', '')
        }
        
        print(f"\n🔍 测试券绑定（修复后的GET请求）")
        print(f"券号: {test_coupon}")
        print(f"影院: 万友影城 ({wanyou_account['cinemaid']})")
        
        result = bind_coupon(bind_params)
        print(f"\n📥 绑定结果: {result}")
        
        if result.get('resultCode') == '0':
            print(f"✅ 券绑定成功！GET请求修复有效")
        else:
            error_desc = result.get('resultDesc', '未知错误')
            print(f"❌ 券绑定失败: {error_desc}")
            
            # 分析错误
            if 'TOKEN_INVALID' in error_desc:
                print(f"💡 仍然是TOKEN_INVALID，可能需要重新登录万友影城账号")
            elif 'COUPON_ALREADY_BIND' in error_desc:
                print(f"✅ 券号有效但已绑定，说明GET请求修复成功")
            elif 'COUPON_NOT_EXIST' in error_desc:
                print(f"💡 券号不存在，尝试其他券号")
            else:
                print(f"💡 其他错误，需要进一步分析")
        
        # 3. 如果第一个券失败，尝试其他券号
        if result.get('resultCode') != '0':
            other_coupons = ["54944529131", "54971977310", "54973324326"]
            print(f"\n🔍 尝试其他券号...")
            
            for coupon in other_coupons:
                print(f"测试券号: {coupon}")
                bind_params['couponcode'] = coupon
                
                try_result = bind_coupon(bind_params)
                if try_result.get('resultCode') == '0':
                    print(f"✅ 券{coupon}绑定成功！")
                    break
                else:
                    error = try_result.get('resultDesc', '未知错误')
                    print(f"❌ 券{coupon}失败: {error}")
                    if 'COUPON_ALREADY_BIND' in error:
                        print(f"✅ 券号有效但已绑定，GET请求修复成功")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test_bind_coupon() 