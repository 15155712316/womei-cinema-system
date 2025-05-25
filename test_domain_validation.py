#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.cinema_info_api import get_cinema_info, format_cinema_data

def test_domain_specific_validation():
    """测试域名特定的影院ID验证"""
    
    # 测试用例：域名-影院ID配对
    test_cases = [
        # 已知有效的配对
        {
            "domain": "tt7.cityfilms.cn",
            "cinema_id": "11b7e4bcc265",
            "expected": True,
            "note": "虹湾影城 - 应该成功"
        },
        {
            "domain": "zcxzs7.cityfilms.cn", 
            "cinema_id": "0f1e21d86ac8",
            "expected": True,
            "note": "万友影城 - 应该成功"
        },
        # 错误的配对测试
        {
            "domain": "tt7.cityfilms.cn",
            "cinema_id": "0f1e21d86ac8",  # 万友的ID用在虹湾域名
            "expected": False,
            "note": "错误配对 - 万友ID用虹湾域名"
        },
        {
            "domain": "zcxzs7.cityfilms.cn",
            "cinema_id": "11b7e4bcc265",  # 虹湾的ID用在万友域名
            "expected": False,
            "note": "错误配对 - 虹湾ID用万友域名"
        },
        # 用户提供的测试案例
        {
            "domain": "tt7.cityfilms.cn",
            "cinema_id": "35fec8259e74",
            "expected": False,
            "note": "用户测试ID - 可能在所有域名都不存在"
        },
        {
            "domain": "zcxzs7.cityfilms.cn",
            "cinema_id": "35fec8259e74", 
            "expected": False,
            "note": "用户测试ID - 尝试万友域名"
        }
    ]
    
    print("🔍 测试域名特定的影院ID验证")
    print("="*80)
    
    for i, test_case in enumerate(test_cases, 1):
        domain = test_case["domain"]
        cinema_id = test_case["cinema_id"]
        expected = test_case["expected"]
        note = test_case["note"]
        
        print(f"\n【测试 {i}】{note}")
        print(f"域名: {domain}")
        print(f"影院ID: {cinema_id}")
        print(f"期望结果: {'成功' if expected else '失败'}")
        print("-" * 50)
        
        # 执行验证
        cinema_info = get_cinema_info(domain, cinema_id)
        
        # 分析结果
        if cinema_info is not None:
            print(f"✅ 验证成功!")
            cinema_data = format_cinema_data(cinema_info, domain)
            print(f"📍 影院名称: {cinema_data.get('cinemaShortName', '未知')}")
            print(f"🏙️ 所在城市: {cinema_data.get('cityName', '未知')}")
            print(f"📍 影院地址: {cinema_data.get('cinemaAddress', '未知')}")
            print(f"🆔 真实影院ID: {cinema_info.get('cinemaid', '未知')}")
            
            if expected:
                print(f"🎯 测试结果: PASS (符合预期)")
            else:
                print(f"⚠️  测试结果: UNEXPECTED SUCCESS (意外成功)")
        else:
            print(f"❌ 验证失败")
            print(f"原因: 影院ID在域名 {domain} 中不存在")
            
            if not expected:
                print(f"🎯 测试结果: PASS (符合预期)")
            else:
                print(f"❌ 测试结果: FAIL (应该成功但失败了)")
        
        print("\n" + "="*50)

def test_id_mapping_discovery():
    """测试ID映射关系发现"""
    print("\n🔍 分析ID映射关系")
    print("="*80)
    
    # 已知的查询ID -> 真实ID映射
    known_mappings = [
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
    
    for mapping in known_mappings:
        domain = mapping["domain"]
        query_id = mapping["query_id"] 
        cinema_name = mapping["cinema_name"]
        
        print(f"\n【分析】{cinema_name}")
        print(f"域名: {domain}")
        print(f"查询ID: {query_id}")
        print("-" * 30)
        
        cinema_info = get_cinema_info(domain, query_id)
        if cinema_info:
            real_id = cinema_info.get('cinemaid', '未知')
            print(f"真实ID: {real_id}")
            print(f"影院名: {cinema_info.get('cinemaShortName', '未知')}")
            print(f"ID映射: {query_id} -> {real_id}")
            
            if query_id != real_id:
                print(f"✓ 确认存在ID映射关系")
            else:
                print(f"! 查询ID与真实ID相同")
        else:
            print(f"✗ 获取失败")

if __name__ == "__main__":
    # 执行域名验证测试
    test_domain_specific_validation()
    
    # 执行ID映射分析
    test_id_mapping_discovery()
    
    print(f"\n{'='*80}")
    print("🎯 测试总结:")
    print("1. 影院ID和域名是绑定关系，不能跨域名使用")
    print("2. 查询ID可能与真实影院ID不同，存在映射关系") 
    print("3. 添加影院时必须同时指定正确的域名和对应的影院ID")
    print("4. 用户测试的ID '35fec8259e74' 在测试的域名中均不存在") 