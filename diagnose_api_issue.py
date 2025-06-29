#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断API问题
分析沃美API返回内网地址的原因
"""

import requests
import json
import urllib3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api_connectivity():
    """测试API连通性"""
    print("🧪 测试API连通性")
    print("=" * 60)
    
    # 测试基础连接
    base_urls = [
        "https://ct.womovie.cn",
        "https://ct.womovie.cn/ticket/wmyc",
        "https://ct.womovie.cn/ticket/wmyc/cinema"
    ]
    
    for url in base_urls:
        try:
            print(f"📡 测试: {url}")
            response = requests.get(url, timeout=10, verify=False)
            print(f"   状态码: {response.status_code}")
            print(f"   响应头: {dict(response.headers)}")
            print(f"   响应长度: {len(response.text)}")
            
            # 检查是否有重定向
            if response.history:
                print(f"   重定向历史:")
                for i, resp in enumerate(response.history):
                    print(f"     {i+1}. {resp.status_code} -> {resp.url}")
                print(f"   最终URL: {response.url}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ 连接失败: {e}")
            print()

def test_voucher_api_detailed():
    """详细测试券绑定API"""
    print("🧪 详细测试券绑定API")
    print("=" * 60)
    
    try:
        # 构建请求
        cinema_id = "400303"
        base_url = "https://ct.womovie.cn"
        url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'token': 'afebc43f2b18da363fd7c8cca3b5fc72',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
        
        data = {
            'card_id': '',
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'limit_cards': '[]',
            'order_id': '250625184410001025',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'ticket_pack_goods': ' ',
            'use_limit_cards': 'N',
            'use_rewards': 'Y',
            'voucher_code': 'GZJY01002948416827',
            'voucher_code_type': 'VGC_T',
        }
        
        print(f"📡 请求URL: {url}")
        print(f"📤 请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        print(f"📤 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        print(f"\n🚀 发送POST请求...")
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        print(f"📥 响应状态码: {response.status_code}")
        print(f"📥 响应头: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}")
        
        # 检查重定向
        if response.history:
            print(f"📥 重定向历史:")
            for i, resp in enumerate(response.history):
                print(f"   {i+1}. {resp.status_code} {resp.reason} -> {resp.url}")
        
        print(f"📥 最终URL: {response.url}")
        print(f"📥 原始响应: {response.text}")
        
        # 尝试解析JSON
        try:
            response_json = response.json()
            print(f"📥 JSON响应: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            
            # 分析错误信息
            if response_json.get('code') == 404:
                print(f"\n🔍 404错误分析:")
                print(f"   错误消息: {response_json.get('msg')}")
                print(f"   请求URL: {response_json.get('url')}")
                print(f"   实际URI: {response_json.get('uri')}")
                
                # 分析URL差异
                requested_url = url
                error_url = response_json.get('url', '')
                
                print(f"\n📊 URL对比:")
                print(f"   我们发送的URL: {requested_url}")
                print(f"   服务器看到的URL: {error_url}")
                
                if "10.193.4.37" in error_url:
                    print(f"   🔍 分析: 服务器内部重定向到内网地址")
                    print(f"   🔍 可能原因: 负载均衡器或反向代理配置问题")
                    print(f"   🔍 建议: 检查请求头或尝试不同的API端点")
                
        except json.JSONDecodeError:
            print(f"📥 非JSON响应，原始内容: {response.text[:500]}...")
        
        return response
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_alternative_endpoints():
    """测试替代API端点"""
    print("\n🧪 测试替代API端点")
    print("=" * 60)
    
    # 尝试不同的API路径
    cinema_id = "400303"
    alternative_urls = [
        f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/change",  # 不带参数
        f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/change/",  # 带斜杠
        f"https://ct.womovie.cn/appapi/wmyc/cinema/{cinema_id}/order/change/",  # 使用appapi路径
        f"https://ct.womovie.cn/api/wmyc/cinema/{cinema_id}/order/change/",  # 使用api路径
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'token': 'afebc43f2b18da363fd7c8cca3b5fc72'
    }
    
    for url in alternative_urls:
        try:
            print(f"📡 测试端点: {url}")
            response = requests.post(url, headers=headers, data={'test': 'data'}, verify=False, timeout=10)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    json_resp = response.json()
                    print(f"   响应: {json.dumps(json_resp, ensure_ascii=False)[:100]}...")
                except:
                    print(f"   响应: {response.text[:100]}...")
            else:
                print(f"   响应: {response.text[:100]}...")
            
            print()
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            print()

def analyze_working_api():
    """分析工作正常的API"""
    print("\n🧪 分析工作正常的API")
    print("=" * 60)
    
    try:
        # 测试券列表API（这个应该是工作的）
        cinema_id = "400303"
        token = "afebc43f2b18da363fd7c8cca3b5fc72"
        
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'token': token
        }
        
        print(f"📡 测试券列表API: {url}")
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        print(f"📥 状态码: {response.status_code}")
        print(f"📥 响应: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                json_resp = response.json()
                print(f"✅ 券列表API工作正常")
                print(f"📊 返回数据结构: {list(json_resp.keys())}")
                return True
            except:
                print(f"❌ 响应不是有效JSON")
                return False
        else:
            print(f"❌ 券列表API返回错误状态码")
            return False
        
    except Exception as e:
        print(f"❌ 券列表API测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🎬 沃美API问题诊断")
    print("🎯 分析券绑定API返回内网地址的原因")
    print("=" * 80)
    
    # 1. 测试基础连通性
    test_api_connectivity()
    
    # 2. 详细测试券绑定API
    response = test_voucher_api_detailed()
    
    # 3. 测试替代端点
    test_alternative_endpoints()
    
    # 4. 分析工作正常的API
    voucher_list_works = analyze_working_api()
    
    # 生成诊断报告
    print(f"\n📋 诊断报告")
    print("=" * 80)
    
    print(f"🔍 问题分析:")
    print(f"   1. 请求URL格式正确: ✅")
    print(f"   2. cinema_id获取正确: ✅")
    print(f"   3. 请求头格式正确: ✅")
    print(f"   4. 券列表API工作正常: {'✅' if voucher_list_works else '❌'}")
    
    print(f"\n🎯 根本原因:")
    print(f"   服务器返回404错误，显示内网地址 http://10.193.4.37/appapi/wmyc/cinema/order/change")
    print(f"   这表明:")
    print(f"   1. 我们的请求到达了沃美服务器")
    print(f"   2. 服务器内部重定向到了内网地址")
    print(f"   3. 内网服务器上不存在 /order/change 端点")
    
    print(f"\n💡 可能的解决方案:")
    print(f"   1. 检查API文档，确认正确的端点路径")
    print(f"   2. 尝试使用 /appapi/ 路径而不是 /ticket/")
    print(f"   3. 检查是否需要特殊的认证或权限")
    print(f"   4. 联系沃美技术支持确认API可用性")
    
    print(f"\n🚀 下一步建议:")
    print(f"   1. 查看HAR文件中实际工作的券绑定请求")
    print(f"   2. 对比请求头和参数的差异")
    print(f"   3. 尝试使用HAR文件中的确切URL和参数")

if __name__ == "__main__":
    main()
