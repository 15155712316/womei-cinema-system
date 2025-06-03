#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试curl解析器功能
"""

from ui.components.curl_parser import CurlParser

def test_your_curl_example():
    """测试您提供的curl命令示例"""
    
    curl_command = """curl -X GET 'https://www.heibaiyingye.cn/MiniTicket/index.php/MiniCommonSystem/getCinemaSettings?sortType=1&groupid&cinemaid=35fec8259e74&cardno&userid=15155712316&openid=oAOCp7VbeeoqMM4yC8e2i3G3lxI8&CVersion=3.9.12&OS=Windows&token=3a30b9e980892714&source=2' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639' -H 'Accept: application/json' -H 'xweb_xhr: 1' -H 'content-type: application/x-www-form-urlencoded' -H 'sec-fetch-site: cross-site' -H 'sec-fetch-mode: cors' -H 'sec-fetch-dest: empty' -H 'referer: https://servicewechat.com/wx99daf24d11d78b1a/2/page-frame.html' -H 'accept-language: zh-CN,zh;q=0.9' -H 'priority: u=1, i'"""
    
    print("🧪 测试您提供的curl命令...")
    print("=" * 60)
    
    # 解析curl命令
    params, report = CurlParser.analyze_curl_example(curl_command)
    
    print(report)
    print("\n" + "=" * 60)
    print("📊 详细参数列表:")
    
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    
    # 验证关键参数
    required_params = ['base_url', 'cinema_id']
    missing = [p for p in required_params if p not in params]
    
    if not missing:
        print("🎉 所有必要参数都已成功提取！")
        print("📋 可以直接用于影院配置：")
        print(f"  • 影院API域名: {params.get('base_url')}")
        print(f"  • 影院ID: {params.get('cinema_id')}")
        print(f"  • 用户OpenID: {params.get('openid', '未提取')}")
        print(f"  • 访问Token: {params.get('token', '未提取')}")
        print(f"  • 用户ID: {params.get('user_id', '未提取')}")
    else:
        print(f"⚠️ 缺少必要参数: {', '.join(missing)}")

def test_other_curl_formats():
    """测试其他格式的curl命令"""
    
    print("\n\n🧪 测试其他curl格式...")
    print("=" * 60)
    
    # 测试不同格式的curl命令
    test_cases = [
        {
            "name": "简单GET请求",
            "curl": "curl 'https://api.cinema.com/movies?cinema_id=12345&token=abc123'"
        },
        {
            "name": "带Authorization头",
            "curl": "curl -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiJ9' 'https://api.cinema.com/cinema/67890'"
        },
        {
            "name": "POST请求",
            "curl": "curl -X POST 'https://api.cinema.com/order' -d 'cinemaid=54321&openid=ox123456'"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 测试案例 {i}: {test_case['name']}")
        print("-" * 40)
        
        params, report = CurlParser.analyze_curl_example(test_case['curl'])
        
        if params:
            print("✅ 提取成功:")
            for key, value in params.items():
                print(f"  • {key}: {value}")
        else:
            print("❌ 未提取到参数")

if __name__ == "__main__":
    # 测试您的curl命令
    test_your_curl_example()
    
    # 测试其他格式
    test_other_curl_formats()
    
    print("\n\n🎉 所有测试完成！")
    print("现在您可以：")
    print("1. 启动应用程序: python run_app.py")
    print("2. 点击'采集影院'按钮")
    print("3. 选择'curl解析'Tab")
    print("4. 粘贴您的curl命令")
    print("5. 点击'解析curl命令'按钮")
    print("6. 确认采集参数")
