#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试accounts.json文件
"""

def test_accounts_file():
    """测试accounts.json文件"""
    try:
        import json
        import os
        
        print("=== 测试accounts.json文件 ===")
        
        # 读取文件
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        print(f"✅ 文件读取成功")
        print(f"账号数量: {len(accounts)}")
        
        if accounts:
            account = accounts[0]
            print(f"第一个账号: {account}")
            phone = account.get('phone')
            token = account.get('token')
            print(f"手机号: {phone}")
            print(f"Token: {token[:20]}...")
            
            # 测试API调用
            print("\n=== 测试API调用 ===")
            from services.womei_film_service import get_womei_film_service
            
            service = get_womei_film_service(token)
            cities_result = service.get_cities()
            
            if cities_result.get('success'):
                cities = cities_result.get('cities', [])
                print(f"✅ API调用成功，获取到 {len(cities)} 个城市")
                return True
            else:
                print(f"❌ API调用失败: {cities_result.get('error')}")
                return False
        else:
            print("❌ 账号文件为空")
            return False
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_accounts_file()
    if success:
        print("\n🎉 accounts.json文件测试成功！")
        print("现在可以重新启动程序测试座位图加载了")
    else:
        print("\n⚠️ accounts.json文件测试失败")
