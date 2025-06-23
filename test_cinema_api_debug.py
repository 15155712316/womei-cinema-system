#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试影院API调试
专门用于分析token失效时的API响应格式
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cinema_api_with_current_token():
    """使用当前token测试影院API"""
    try:
        print("🧪 测试影院API - 当前token")
        print("=" * 60)
        
        # 导入沃美电影服务
        from services.womei_film_service import WomeiFilmService
        
        # 使用当前token
        current_token = "5e160d18859114a648efc599113c585a"
        
        print(f"📋 使用token: {current_token[:10]}...")
        
        # 创建服务实例
        service = WomeiFilmService(current_token)
        
        # 测试城市API
        print(f"\n🔍 步骤1: 测试城市API")
        cities_result = service.get_cities()
        
        print(f"📥 城市API结果:")
        print(f"  - success: {cities_result.get('success')}")
        print(f"  - total: {cities_result.get('total')}")
        print(f"  - error: {cities_result.get('error', 'N/A')}")
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            print(f"  - 城市数量: {len(cities)}")
            if cities:
                print(f"  - 第一个城市: {cities[0]}")
        
        # 测试影院API
        print(f"\n🔍 步骤2: 测试影院API")
        cinemas_result = service.get_cinemas()
        
        print(f"📥 影院API结果:")
        print(f"  - success: {cinemas_result.get('success')}")
        print(f"  - error: {cinemas_result.get('error', 'N/A')}")
        
        # 检查调试信息
        debug_info = cinemas_result.get('debug_info', {})
        if debug_info:
            print(f"  - 调试信息:")
            print(f"    - 数据类型: {debug_info.get('data_type')}")
            print(f"    - 数据内容: {debug_info.get('data_content')}")
            
            cities_response = debug_info.get('cities_response', {})
            if cities_response:
                print(f"    - 原始响应:")
                print(f"      - ret: {cities_response.get('ret')}")
                print(f"      - sub: {cities_response.get('sub')}")
                print(f"      - msg: {cities_response.get('msg')}")
                print(f"      - data类型: {type(cities_response.get('data'))}")
                print(f"      - data内容: {cities_response.get('data')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cinema_api_with_invalid_token():
    """使用无效token测试影院API"""
    try:
        print("\n🧪 测试影院API - 无效token")
        print("=" * 60)
        
        # 导入沃美电影服务
        from services.womei_film_service import WomeiFilmService
        
        # 使用无效token
        invalid_token = "invalid_token_12345"
        
        print(f"📋 使用无效token: {invalid_token}")
        
        # 创建服务实例
        service = WomeiFilmService(invalid_token)
        
        # 测试城市API
        print(f"\n🔍 步骤1: 测试城市API（无效token）")
        cities_result = service.get_cities()
        
        print(f"📥 城市API结果（无效token）:")
        print(f"  - success: {cities_result.get('success')}")
        print(f"  - total: {cities_result.get('total')}")
        print(f"  - error: {cities_result.get('error', 'N/A')}")
        
        # 测试影院API
        print(f"\n🔍 步骤2: 测试影院API（无效token）")
        cinemas_result = service.get_cinemas()
        
        print(f"📥 影院API结果（无效token）:")
        print(f"  - success: {cinemas_result.get('success')}")
        print(f"  - error: {cinemas_result.get('error', 'N/A')}")
        
        # 检查调试信息
        debug_info = cinemas_result.get('debug_info', {})
        if debug_info:
            print(f"  - 调试信息:")
            print(f"    - 数据类型: {debug_info.get('data_type')}")
            print(f"    - 数据内容: {debug_info.get('data_content')}")
            
            cities_response = debug_info.get('cities_response', {})
            if cities_response:
                print(f"    - 原始响应:")
                print(f"      - ret: {cities_response.get('ret')}")
                print(f"      - sub: {cities_response.get('sub')}")
                print(f"      - msg: {cities_response.get('msg')}")
                print(f"      - data类型: {type(cities_response.get('data'))}")
                print(f"      - data内容: {cities_response.get('data')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_api_call():
    """直接测试API调用"""
    try:
        print("\n🧪 直接测试API调用")
        print("=" * 60)
        
        # 导入API适配器
        from cinema_api_adapter import create_womei_api
        
        # 测试当前token
        current_token = "5e160d18859114a648efc599113c585a"
        api = create_womei_api(current_token)
        
        print(f"📋 直接调用城市API")
        
        # 直接调用API
        response = api.get_cities()
        
        print(f"📥 直接API调用结果:")
        print(f"  - 响应类型: {type(response)}")
        print(f"  - 响应内容: {response}")
        
        if isinstance(response, dict):
            print(f"  - ret: {response.get('ret')}")
            print(f"  - sub: {response.get('sub')}")
            print(f"  - msg: {response.get('msg')}")
            
            data = response.get('data')
            print(f"  - data类型: {type(data)}")
            print(f"  - data内容: {data}")
            
            if isinstance(data, list):
                print(f"  - 列表长度: {len(data)}")
                if data:
                    print(f"  - 第一个元素: {data[0]}")
            elif isinstance(data, dict):
                print(f"  - 字典键: {list(data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 直接API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_validation():
    """测试token有效性"""
    try:
        print("\n🧪 测试token有效性")
        print("=" * 60)
        
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # 测试token
        test_tokens = [
            "5e160d18859114a648efc599113c585a",  # 当前token
            "invalid_token_12345",  # 无效token
            "",  # 空token
        ]
        
        for i, token in enumerate(test_tokens, 1):
            print(f"\n📋 测试token {i}: {token[:10] if token else '(空)'}...")
            
            # 构建请求
            url = "https://ct.womovie.cn/ticket/wmyc/citys/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'token': token,
                'x-channel-id': '40000',
                'tenant-short': 'wmyc',
                'client-version': '4.0'
            }
            
            try:
                response = requests.get(url, headers=headers, verify=False, timeout=10)
                
                print(f"  - HTTP状态: {response.status_code}")
                print(f"  - 响应长度: {len(response.text)}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  - JSON解析: 成功")
                        print(f"  - ret: {data.get('ret')}")
                        print(f"  - sub: {data.get('sub')}")
                        print(f"  - msg: {data.get('msg')}")
                        print(f"  - data类型: {type(data.get('data'))}")
                        
                        if data.get('ret') == 0:
                            print(f"  - ✅ token有效")
                        else:
                            print(f"  - ❌ token无效或其他错误")
                            
                    except json.JSONDecodeError:
                        print(f"  - JSON解析: 失败")
                        print(f"  - 原始响应: {response.text[:200]}...")
                else:
                    print(f"  - ❌ HTTP错误")
                    
            except Exception as e:
                print(f"  - ❌ 请求异常: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ token验证测试失败: {e}")
        return False

def main():
    print("🎬 沃美电影票务系统 - 影院API调试测试")
    print("=" * 60)
    print("📋 测试目标：分析token失效时的API响应格式")
    print("🔍 测试内容：")
    print("  1. 当前token的影院API测试")
    print("  2. 无效token的影院API测试")
    print("  3. 直接API调用测试")
    print("  4. token有效性验证")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_cinema_api_with_current_token,
        test_cinema_api_with_invalid_token,
        test_direct_api_call,
        test_token_validation
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n🎉 测试完成！")
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    print(f"\n📋 分析总结：")
    print(f"✅ 已添加详细的API调试日志")
    print(f"✅ 可以分析token有效和无效时的响应差异")
    print(f"✅ 提供了完整的错误诊断信息")
    print(f"\n🚀 现在可以通过日志分析API响应格式问题了！")

if __name__ == "__main__":
    main()
