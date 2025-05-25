#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试动态base_url系统的功能
验证API请求是否能正确根据影院ID选择对应的base_url
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.api_base import api_base
from services.account_api import login_and_check_card

def test_get_base_url():
    """测试根据影院ID获取base_url"""
    print("=== 测试获取base_url功能 ===")
    
    # 测试影院ID列表
    test_cinemas = [
        "11b7e4bcc265",  # 虹湾影城 - 应该返回 tt7.cityfilms.cn
        "0f1e21d86ac8",  # 万友影城 - 应该返回 zcxzs7.cityfilms.cn  
        "61011571",      # 华夏优加荟大都荟 - 应该返回 www.heibaiyingye.cn
        "nonexistent"    # 不存在的影院ID - 应该返回默认域名
    ]
    
    for cinemaid in test_cinemas:
        base_url = api_base.get_base_url_for_cinema(cinemaid)
        print(f"影院ID: {cinemaid} -> base_url: {base_url}")
    
    print()

def test_login_with_dynamic_url():
    """测试使用动态URL的登录功能"""
    print("=== 测试动态URL登录功能 ===")
    
    # 测试账号信息
    test_accounts = [
        {
            "phone": "15155712316",
            "ck": "3a30b9e980892714", 
            "openid": "oAOCp7VbeeoqMM4yC8e2i3G3lxI8",
            "cinemaid": "61011571"  # 华夏优加荟大都荟
        },
        {
            "phone": "14700283316",
            "ck": "9de4d8353cd30172",
            "openid": "ohA6p7VxLxzcHoBw1_E8VcyEvVVs", 
            "cinemaid": "11b7e4bcc265"  # 虹湾影城
        }
    ]
    
    for i, account in enumerate(test_accounts, 1):
        print(f"测试账号 {i}: {account['phone']} @ 影院 {account['cinemaid']}")
        
        try:
            result = login_and_check_card(
                phone=account["phone"],
                ck=account["ck"], 
                openid=account["openid"],
                cinemaid=account["cinemaid"]
            )
            
            print(f"登录结果: {result.get('resultCode')} - {result.get('resultDesc')}")
            
            if result.get('resultCode') == '0':
                print("✓ 登录成功！")
            else:
                print(f"✗ 登录失败: {result.get('resultDesc')}")
                
        except Exception as e:
            print(f"✗ 登录异常: {e}")
        
        print("-" * 50)

def test_url_building():
    """测试URL构建功能"""
    print("=== 测试URL构建功能 ===")
    
    test_cases = [
        ("tt7.cityfilms.cn", "MiniTicket/index.php/MiniMember/getMemcardList"),
        ("https://zcxzs7.cityfilms.cn", "MiniTicket/index.php/MiniOrder/createOrder"),
        ("www.heibaiyingye.cn", "/MiniTicket/index.php/MiniFilm/getAllFilmsIndexNew")
    ]
    
    for base_url, path in test_cases:
        full_url = api_base.build_url(base_url, path)
        print(f"base_url: {base_url}")
        print(f"path: {path}")
        print(f"完整URL: {full_url}")
        print("-" * 30)

if __name__ == "__main__":
    print("开始测试动态base_url系统...")
    print()
    
    # 运行测试
    test_get_base_url()
    test_url_building()
    test_login_with_dynamic_url()
    
    print("测试完成！")
    print()
    print("注意事项：")
    print("1. 如果看到API基础服务找到了正确的base_url，说明配置正确")
    print("2. 如果登录成功(resultCode=0)，说明动态URL系统工作正常")
    print("3. 如果登录失败但使用了正确的base_url，可能是账号信息过期")
    print("4. 请检查data/cinema_info.json文件中的影院配置是否正确") 