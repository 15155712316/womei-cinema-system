#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试券列表接口
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coupon_list():
    """测试券列表接口"""
    print("=== 测试券列表接口 ===")
    
    try:
        # 1. 加载万友影城账号
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
        
        # 2. 测试券列表接口
        from services.order_api import get_coupon_list
        
        params = {
            'voucherType': -1,  # -1表示获取所有类型券
            'pageNo': 1,
            'groupid': '',
            'cinemaid': wanyou_account['cinemaid'],
            'cardno': wanyou_account.get('cardno', ''),
            'userid': wanyou_account['userid'],
            'openid': wanyou_account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': wanyou_account['token'],
            'source': '2'
        }
        
        print(f"\n🔍 测试券列表接口")
        print(f"影院: 万友影城 ({wanyou_account['cinemaid']})")
        print(f"用户: {wanyou_account['userid']}")
        
        result = get_coupon_list(params)
        print(f"\n📥 券列表结果: {result}")
        
        if result.get('resultCode') == '0':
            print(f"✅ 券列表获取成功！")
            
            # 解析券数据
            coupon_data = result.get('resultData', {})
            vouchers = coupon_data.get('vouchers', []) or coupon_data.get('coupons', []) or coupon_data.get('data', [])
            
            if vouchers:
                print(f"📋 券列表详情（只显示可用券）：")
                
                # 过滤券：只保留未使用且未过期的券
                valid_vouchers = []
                total_count = len(vouchers)
                used_count = 0
                expired_count = 0
                
                for voucher in vouchers:
                    # 检查是否已使用 (redeemed=1表示已使用)
                    is_used = str(voucher.get('redeemed', '0')) == '1'
                    # 检查是否已过期 (expired=1表示已过期)
                    is_expired = str(voucher.get('expired', '0')) == '1'
                    
                    if is_used:
                        used_count += 1
                    elif is_expired:
                        expired_count += 1
                    else:
                        # 未使用且未过期的券
                        valid_vouchers.append(voucher)
                
                # 按有效期分组统计
                expire_stats = {}
                
                for i, voucher in enumerate(valid_vouchers, 1):
                    name = voucher.get('couponname') or voucher.get('voucherName') or voucher.get('name', f'券{i}')
                    expire = voucher.get('expireddate') or voucher.get('expiredDate') or '未知'
                    code = voucher.get('couponcode') or voucher.get('voucherCode') or voucher.get('code', f'未知券号{i}')
                    
                    print(f"  {i}. {name} | 有效期至 {expire} | 券号 {code}")
                    
                    # 统计有效期
                    if expire != '未知':
                        expire_key = expire.split(' ')[0]  # 只取日期部分
                        expire_stats[expire_key] = expire_stats.get(expire_key, 0) + 1
                
                # 显示有效期统计
                print(f"\n📊 可用券有效期统计：")
                for expire_date in sorted(expire_stats.keys()):
                    count = expire_stats[expire_date]
                    print(f"  {expire_date}到期 {count}张")
                    
                print(f"\n📈 券统计总结：")
                print(f"  总券数: {total_count}张")
                print(f"  可用券: {len(valid_vouchers)}张")
                print(f"  已使用: {used_count}张")
                print(f"  已过期: {expired_count}张")
            else:
                print(f"📋 暂无可用优惠券")
        else:
            error_desc = result.get('resultDesc', '未知错误')
            print(f"❌ 券列表获取失败: {error_desc}")
            
            # 分析错误
            if 'TOKEN_INVALID' in error_desc:
                print(f"💡 Token无效，可能需要重新登录")
            else:
                print(f"💡 其他错误，需要进一步分析")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coupon_list() 