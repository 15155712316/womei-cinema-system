#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.cinema_info_api import get_cinema_info, format_cinema_data

def test_cinema_domain_binding():
    """验证影院ID与域名的绑定关系"""
    
    print("🔗 验证影院ID与域名的绑定关系")
    print("=" * 70)
    
    # 已知的绑定关系
    known_bindings = [
        {
            "domain": "tt7.cityfilms.cn",
            "query_id": "11b7e4bcc265", 
            "cinema_name": "虹湾影城"
        },
        {
            "domain": "zcxzs7.cityfilms.cn",
            "query_id": "0f1e21d86ac8",
            "cinema_name": "万友影城"
        }
    ]
    
    print(f"\n✅ 测试已知的正确绑定:")
    for binding in known_bindings:
        domain = binding["domain"]
        query_id = binding["query_id"]
        cinema_name = binding["cinema_name"]
        
        print(f"\n【{cinema_name}】")
        print(f"🌐 域名: {domain}")
        print(f"🆔 查询ID: {query_id}")
        
        cinema_info = get_cinema_info(domain, query_id)
        if cinema_info:
            real_id = cinema_info.get('cinemaid', '未知')
            actual_name = cinema_info.get('cinemaShortName', '未知')
            city = cinema_info.get('cityName', '未知')
            
            print(f"✅ 验证成功!")
            print(f"📍 影院名称: {actual_name}")
            print(f"🏙️ 所在城市: {city}")
            print(f"🔄 ID映射: {query_id} -> {real_id}")
            
            if query_id != real_id:
                print(f"💡 存在ID映射关系")
            else:
                print(f"💡 查询ID = 真实ID")
        else:
            print(f"❌ 验证失败!")
    
    print(f"\n" + "=" * 50)
    
    # 测试跨域使用（错误的绑定）
    print(f"\n❌ 测试错误的绑定关系:")
    
    wrong_bindings = [
        {
            "domain": "zcxzs7.cityfilms.cn",  # 万友域名
            "query_id": "11b7e4bcc265",       # 虹湾ID
            "note": "万友域名 + 虹湾ID"
        },
        {
            "domain": "tt7.cityfilms.cn",     # 虹湾域名  
            "query_id": "0f1e21d86ac8",       # 万友ID
            "note": "虹湾域名 + 万友ID"
        }
    ]
    
    for binding in wrong_bindings:
        domain = binding["domain"]
        query_id = binding["query_id"]
        note = binding["note"]
        
        print(f"\n【错误测试】{note}")
        print(f"🌐 域名: {domain}")
        print(f"🆔 查询ID: {query_id}")
        
        cinema_info = get_cinema_info(domain, query_id)
        if cinema_info:
            print(f"⚠️ 意外成功! (可能ID通用)")
            print(f"📍 影院名称: {cinema_info.get('cinemaShortName', '未知')}")
        else:
            print(f"✅ 验证失败 (符合预期)")
    
    print(f"\n" + "=" * 50)
    
    # 测试用户提供的ID
    print(f"\n🔍 测试用户提供的ID: 35fec8259e74")
    
    test_domains = ["tt7.cityfilms.cn", "zcxzs7.cityfilms.cn"]
    user_id = "35fec8259e74"
    
    for domain in test_domains:
        print(f"\n🌐 测试域名: {domain}")
        print(f"🆔 用户ID: {user_id}")
        
        cinema_info = get_cinema_info(domain, user_id)
        if cinema_info:
            print(f"✅ 找到了! 影院: {cinema_info.get('cinemaShortName', '未知')}")
        else:
            print(f"❌ 在此域名中不存在")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 核心结论:")
    print(f"1. ✅ 影院ID和域名必须正确配对")
    print(f"2. ✅ 查询ID可能映射到不同的真实ID")  
    print(f"3. ✅ 不能跨域名使用影院ID")
    print(f"4. ✅ 添加影院需要: 正确的域名 + 对应的查询ID")

if __name__ == "__main__":
    test_cinema_domain_binding() 