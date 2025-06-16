#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试token有效性
验证当前token是否可以正常调用API
"""

import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_account():
    """加载账号数据"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            return accounts[0]
    except:
        pass
    
    return {}

def test_token_with_simple_api():
    """使用简单API测试token有效性"""
    print("🔍 测试token有效性")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    phone = account.get('phone', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    print(f"账号: {phone}")
    print(f"Token: {token[:20]}...")
    
    # 测试沃美电影服务
    try:
        from services.womei_film_service import get_womei_film_service
        
        service = get_womei_film_service(token)
        
        # 测试获取城市列表（这是最简单的API）
        print(f"\n🔄 测试获取城市列表...")
        cities_result = service.get_cities()
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            print(f"✅ 城市API调用成功，获取到 {len(cities)} 个城市")
            
            if cities:
                first_city = cities[0]
                print(f"第一个城市: {first_city.get('city_name', 'N/A')}")
                
                # 测试获取影院列表
                cinemas = first_city.get('cinemas', [])
                if cinemas:
                    first_cinema = cinemas[0]
                    cinema_id = first_cinema.get('cinema_id', '')
                    cinema_name = first_cinema.get('cinema_name', '')
                    
                    print(f"\n🔄 测试获取电影列表...")
                    print(f"测试影院: {cinema_name} (ID: {cinema_id})")
                    
                    movies_result = service.get_movies(cinema_id)
                    if movies_result.get('success'):
                        movies = movies_result.get('movies', [])
                        print(f"✅ 电影API调用成功，获取到 {len(movies)} 部电影")
                        return True
                    else:
                        error = movies_result.get('error', '未知错误')
                        print(f"❌ 电影API调用失败: {error}")
                        return False
                else:
                    print(f"⚠️ 城市中没有影院数据")
                    return True  # 城市API成功就算token有效
            else:
                print(f"⚠️ 没有城市数据")
                return True  # API调用成功就算token有效
        else:
            error = cities_result.get('error', '未知错误')
            print(f"❌ 城市API调用失败: {error}")
            return False
    
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_with_direct_api():
    """直接调用API测试token"""
    print(f"\n🔍 直接API调用测试")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    try:
        from services.api_base import api_get
        
        # 测试一个简单的API调用
        # 使用沃美影院的城市列表API
        params = {
            'token': token,
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2'
        }
        
        print(f"🔄 直接调用城市列表API...")
        print(f"参数: {params}")
        
        # 使用沃美影院ID进行测试
        result = api_get('MiniTicket/index.php/MiniCinema/getCinemaList', '400028', params=params)
        
        print(f"API返回结果: {result}")
        
        if result and isinstance(result, dict):
            result_code = result.get('resultCode', '')
            result_desc = result.get('resultDesc', '')
            
            print(f"结果码: {result_code}")
            print(f"结果描述: {result_desc}")
            
            if result_code == '0':
                print(f"✅ 直接API调用成功")
                return True
            else:
                print(f"❌ 直接API调用失败: {result_desc}")
                return False
        else:
            print(f"❌ API返回格式错误")
            return False
    
    except Exception as e:
        print(f"❌ 直接API调用异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_token_format():
    """分析token格式"""
    print(f"\n🔍 分析token格式")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return
    
    print(f"Token长度: {len(token)}")
    print(f"Token格式: {token[:10]}...{token[-10:]}")
    print(f"Token字符类型: {'数字+字母' if token.isalnum() else '包含特殊字符'}")
    
    # 检查token是否过期（基于长度和格式的简单判断）
    if len(token) < 20:
        print(f"⚠️ Token长度较短，可能无效")
    elif len(token) > 100:
        print(f"⚠️ Token长度较长，可能是JWT格式")
    else:
        print(f"✅ Token长度正常")

def main():
    """主函数"""
    print("🔍 Token有效性测试")
    print("=" * 60)
    
    # 分析token格式
    analyze_token_format()
    
    # 测试token有效性
    service_test_ok = test_token_with_simple_api()
    direct_test_ok = test_token_with_direct_api()
    
    print(f"\n🎯 测试结果总结")
    print("=" * 60)
    
    if service_test_ok:
        print(f"✅ 沃美电影服务测试: 通过")
    else:
        print(f"❌ 沃美电影服务测试: 失败")
    
    if direct_test_ok:
        print(f"✅ 直接API调用测试: 通过")
    else:
        print(f"❌ 直接API调用测试: 失败")
    
    if service_test_ok or direct_test_ok:
        print(f"\n✅ Token有效，可以正常调用API")
        print(f"💡 如果订单创建失败，可能是:")
        print(f"  1. 订单参数格式错误")
        print(f"  2. 座位已被其他用户选择")
        print(f"  3. 场次已过期或取消")
        print(f"  4. 账号权限不足")
    else:
        print(f"\n❌ Token可能已失效")
        print(f"💡 建议:")
        print(f"  1. 重新获取token")
        print(f"  2. 检查账号状态")
        print(f"  3. 确认网络连接")

if __name__ == "__main__":
    main()
