#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from services.cinema_info_api import get_cinema_info, format_cinema_data

def test_simple_domain_validation():
    """简化的域名验证测试"""
    
    print("🎯 简化域名验证测试")
    print("="*60)
    
    # 测试虹湾影城
    print("\n【测试1】虹湾影城")
    print("域名: tt7.cityfilms.cn")
    print("影院ID: 11b7e4bcc265")
    
    cinema_info = get_cinema_info("tt7.cityfilms.cn", "11b7e4bcc265")
    if cinema_info:
        print("✅ 验证成功!")
        cinema_data = format_cinema_data(cinema_info, "tt7.cityfilms.cn")
        print(f"影院名称: {cinema_data.get('cinemaShortName', '未知')}")
        print(f"真实ID: {cinema_info.get('cinemaid', '未知')}")
        print(f"查询ID -> 真实ID: 11b7e4bcc265 -> {cinema_info.get('cinemaid')}")
    else:
        print("❌ 验证失败")
    
    print("\n" + "-"*60)
    
    # 测试万友影城
    print("\n【测试2】万友影城")
    print("域名: zcxzs7.cityfilms.cn")
    print("影院ID: 0f1e21d86ac8")
    
    cinema_info = get_cinema_info("zcxzs7.cityfilms.cn", "0f1e21d86ac8")
    if cinema_info:
        print("✅ 验证成功!")
        cinema_data = format_cinema_data(cinema_info, "zcxzs7.cityfilms.cn")
        print(f"影院名称: {cinema_data.get('cinemaShortName', '未知')}")
        print(f"真实ID: {cinema_info.get('cinemaid', '未知')}")
        print(f"查询ID -> 真实ID: 0f1e21d86ac8 -> {cinema_info.get('cinemaid')}")
    else:
        print("❌ 验证失败")
    
    print("\n" + "-"*60)
    
    # 测试用户ID在已知域名
    print("\n【测试3】用户ID在虹湾域名")
    print("域名: tt7.cityfilms.cn")
    print("影院ID: 35fec8259e74")
    
    cinema_info = get_cinema_info("tt7.cityfilms.cn", "35fec8259e74")
    if cinema_info:
        print("⚠️ 意外成功!")
        cinema_data = format_cinema_data(cinema_info, "tt7.cityfilms.cn")
        print(f"影院名称: {cinema_data.get('cinemaShortName', '未知')}")
    else:
        print("✅ 验证失败 (符合预期)")
    
    print("\n" + "="*60)
    print("🎯 核心结论:")
    print("✓ 影院ID和域名存在绑定关系")
    print("✓ 查询ID可能映射到不同的真实ID")
    print("✓ 必须使用正确的域名+ID组合")

if __name__ == "__main__":
    test_simple_domain_validation() 