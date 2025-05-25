#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试券绑定功能
检查token是否有效，API域名是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_coupon_binding():
    """测试券绑定功能"""
    print("=== 测试券绑定功能 ===")
    
    try:
        # 1. 加载账号信息
        import json
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        
        # 找到主账号
        main_account = None
        for acc in accounts:
            if acc.get('is_main'):
                main_account = acc
                break
        
        if not main_account:
            print("❌ 未找到主账号")
            return
        
        print(f"✓ 找到主账号: {main_account.get('userid')} @ {main_account.get('cinemaid')}")
        print(f"✓ Token: {main_account.get('token', '')[:10]}...")
        
        # 2. 测试获取影院信息验证token
        from services.cinema_info_api import get_cinema_info
        cinemaid = main_account.get('cinemaid')
        
        # 根据cinemaid获取对应的域名
        from services.api_base import api_base
        base_url = api_base.get_base_url_for_cinema(cinemaid)
        print(f"✓ 使用API域名: {base_url}")
        
        # 测试token是否有效 - 使用影院信息接口
        print(f"🔍 测试token有效性...")
        cinema_info = get_cinema_info(base_url, cinemaid)
        if cinema_info:
            print(f"✓ Token验证成功，影院信息可获取")
        else:
            print(f"❌ Token验证失败，无法获取影院信息")
            return
        
        # 3. 测试绑定一张测试券
        test_coupon_code = "54938139116"  # 使用用户提供的第一个券号
        
        from services.order_api import bind_coupon
        
        bind_params = {
            'couponcode': test_coupon_code,
            'cinemaid': main_account['cinemaid'],
            'userid': main_account['userid'],
            'openid': main_account['openid'],
            'token': main_account['token'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2',
            'groupid': '',
            'cardno': main_account.get('cardno', '')
        }
        
        print(f"🔍 测试绑定券: {test_coupon_code}")
        print(f"📤 请求参数: {bind_params}")
        
        result = bind_coupon(bind_params)
        print(f"📥 绑定结果: {result}")
        
        if result.get('resultCode') == '0':
            print(f"✅ 券绑定成功！")
        else:
            error_desc = result.get('resultDesc', '未知错误')
            print(f"❌ 券绑定失败: {error_desc}")
            
            # 分析具体错误原因
            if 'TOKEN_INVALID' in error_desc:
                print(f"💡 原因分析: Token无效")
                print(f"   - 可能原因1: Token已过期")
                print(f"   - 可能原因2: Token与当前影院不匹配")
                print(f"   - 可能原因3: 账号状态异常")
            elif 'COUPON_NOT_EXIST' in error_desc:
                print(f"💡 原因分析: 券号不存在或已被使用")
            elif 'COUPON_ALREADY_BIND' in error_desc:
                print(f"💡 原因分析: 券号已被绑定")
            else:
                print(f"💡 原因分析: 其他错误，需要进一步调查")
                
        # 4. 检查API域名映射
        print(f"\n=== API域名映射检查 ===")
        print(f"当前影院ID: {cinemaid}")
        print(f"映射域名: {base_url}")
        
        # 4.5 检查账号匹配情况
        print(f"\n=== 账号与影院匹配检查 ===")
        print(f"主账号信息:")
        print(f"  - 用户ID: {main_account.get('userid')}")
        print(f"  - 影院ID: {main_account.get('cinemaid')}")
        print(f"  - Token: {main_account.get('token', '')[:10]}...")
        print(f"  - 余额: {main_account.get('balance', 0)}")
        print(f"  - 积分: {main_account.get('score', 0)}")
        
        # 查看所有账号的情况
        print(f"\n所有账号列表:")
        for i, acc in enumerate(accounts, 1):
            is_main_tag = " [主账号]" if acc.get('is_main') else ""
            cinema_name = "未知影院"
            # 根据影院ID查找影院名称
            try:
                from services.cinema_manager import cinema_manager
                cinemas = cinema_manager.load_cinema_list()
                for cinema in cinemas:
                    if cinema.get('cinemaid') == acc.get('cinemaid'):
                        cinema_name = cinema.get('cinemaShortName', '未知影院')
                        break
            except:
                pass
            
            print(f"  {i}. {acc.get('userid')} @ {cinema_name} (余额:{acc.get('balance', 0)}, 积分:{acc.get('score', 0)}){is_main_tag}")
        
        # 建议使用万友影城的账号测试
        wanyou_account = None
        for acc in accounts:
            if acc.get('cinemaid') == '0f1e21d86ac8':  # 万友影城ID
                wanyou_account = acc
                break
        
        if wanyou_account:
            print(f"\n🔍 建议：使用万友影城账号测试券绑定")
            print(f"万友影城账号: {wanyou_account.get('userid')} (余额:{wanyou_account.get('balance', 0)})")
            
            # 测试万友影城的券绑定
            wanyou_bind_params = {
                'couponcode': test_coupon_code,
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
            
            print(f"🔍 使用万友影城账号测试绑定券: {test_coupon_code}")
            print(f"📤 万友影城请求参数: {wanyou_bind_params}")
            
            wanyou_result = bind_coupon(wanyou_bind_params)
            print(f"📥 万友影城绑定结果: {wanyou_result}")
            
            if wanyou_result.get('resultCode') == '0':
                print(f"✅ 万友影城券绑定成功！券号确实属于万友影城")
            else:
                wanyou_error = wanyou_result.get('resultDesc', '未知错误')
                print(f"❌ 万友影城券绑定失败: {wanyou_error}")
                if 'TOKEN_INVALID' in wanyou_error:
                    print(f"💡 万友影城账号的Token也无效，可能需要重新登录")
                elif 'COUPON_ALREADY_BIND' in wanyou_error:
                    print(f"✅ 券号有效但已被绑定，说明券号格式正确")
                else:
                    print(f"💡 其他错误: {wanyou_error}")
        
        # 检查是否所有影院都有对应的域名映射
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        print(f"\n影院域名映射情况:")
        for cinema in cinemas:
            cinema_id = cinema.get('cinemaid', '未知')
            cinema_name = cinema.get('cinemaShortName', '未知影院')
            mapped_url = api_base.get_base_url_for_cinema(cinema_id)
            print(f"  {cinema_name} ({cinema_id}) -> {mapped_url}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_coupon_binding() 