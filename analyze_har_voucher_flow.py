#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析沃美下单用券HAR文件
专注于券码支付流程分析
"""

import json
import base64
import sys
import os
from urllib.parse import urlparse, parse_qs
from datetime import datetime

def analyze_voucher_har_file():
    """分析券码支付HAR文件"""
    har_file = "下单用券对比ct.womovie.cn_2025_06_29_14_51_48.har"
    
    print("=" * 100)
    print("🎫 沃美下单用券流程详细分析")
    print("=" * 100)
    
    if not os.path.exists(har_file):
        print(f"❌ HAR文件不存在: {har_file}")
        return
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        print(f"📊 总共发现 {len(entries)} 个HTTP请求")
        print()
        
        # 按时间排序
        entries.sort(key=lambda x: x['startedDateTime'])
        
        # 分析每个请求
        voucher_related_requests = []
        
        for i, entry in enumerate(entries, 1):
            request = entry['request']
            response = entry['response']
            
            url = request['url']
            method = request['method']
            parsed_url = urlparse(url)
            path = parsed_url.path
            
            # 解析时间
            started_time = entry['startedDateTime']
            time_obj = datetime.fromisoformat(started_time.replace('Z', '+00:00'))
            time_str = time_obj.strftime('%H:%M:%S.%f')[:-3]
            
            print(f"🌐 请求 {i:02d} [{time_str}]: {method} {path}")
            print(f"   完整URL: {url}")
            
            # 检查是否是券码相关请求
            voucher_keywords = ['voucher', 'coupon', 'order', 'change', 'price', 'pay']
            is_voucher_related = any(keyword in path.lower() for keyword in voucher_keywords)
            
            if is_voucher_related:
                voucher_related_requests.append({
                    'index': i,
                    'time': time_str,
                    'method': method,
                    'url': url,
                    'path': path,
                    'request': request,
                    'response': response
                })
                print(f"   ⭐ 券码相关请求")
            
            # 解析请求头
            print(f"   📤 请求头关键信息:")
            key_headers = ['token', 'Content-Type', 'User-Agent']
            for header in request.get('headers', []):
                if header['name'] in key_headers:
                    value = header['value']
                    if header['name'] == 'token':
                        value = f"{value[:20]}...{value[-10:]}" if len(value) > 30 else value
                    elif header['name'] == 'User-Agent':
                        value = value[:80] + "..." if len(value) > 80 else value
                    print(f"     {header['name']}: {value}")
            
            # 解析请求参数
            if request.get('queryString'):
                print(f"   📋 查询参数:")
                for param in request['queryString']:
                    print(f"     {param['name']}: {param['value']}")
            
            if request.get('postData'):
                post_data = request['postData']
                print(f"   📦 请求体类型: {post_data.get('mimeType', 'N/A')}")
                if post_data.get('text'):
                    try:
                        # 尝试解析为JSON
                        if 'json' in post_data.get('mimeType', ''):
                            json_data = json.loads(post_data['text'])
                            print(f"   📦 请求体内容: {json.dumps(json_data, ensure_ascii=False, indent=6)}")
                        else:
                            # URL编码格式
                            print(f"   📦 请求体内容: {post_data['text'][:200]}...")
                    except:
                        print(f"   📦 请求体内容: {post_data['text'][:200]}...")
            
            # 解析响应
            print(f"   📥 响应状态: {response.get('status')}")
            
            if response.get('content', {}).get('text'):
                content_text = response['content']['text']
                encoding = response['content'].get('encoding', '')
                
                try:
                    if encoding == 'base64':
                        decoded_content = base64.b64decode(content_text).decode('utf-8')
                    else:
                        decoded_content = content_text
                    
                    # 尝试解析JSON响应
                    try:
                        response_json = json.loads(decoded_content)
                        print(f"   📥 响应内容: ret={response_json.get('ret')}, sub={response_json.get('sub')}, msg={response_json.get('msg', '')[:50]}")
                        
                        # 如果是券码相关响应，显示更多详情
                        if is_voucher_related and response_json.get('ret') == 0:
                            data = response_json.get('data', {})
                            if 'order_payment_price' in data:
                                print(f"   💰 支付价格: ¥{data.get('order_payment_price')}")
                            if 'voucher_use' in data:
                                voucher_info = data['voucher_use']
                                print(f"   🎫 券使用信息: {voucher_info}")
                        
                    except:
                        print(f"   📥 响应内容: {decoded_content[:100]}...")
                        
                except Exception as e:
                    print(f"   📥 响应解析失败: {e}")
            
            print()
        
        # 详细分析券码相关请求
        if voucher_related_requests:
            print("=" * 100)
            print("🎯 券码支付流程详细分析")
            print("=" * 100)
            
            for req_info in voucher_related_requests:
                analyze_voucher_request_detail(req_info)
        
        return voucher_related_requests
        
    except Exception as e:
        print(f"❌ 解析HAR文件失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_voucher_request_detail(req_info):
    """详细分析券码相关请求"""
    print(f"📋 请求 {req_info['index']:02d} [{req_info['time']}]: {req_info['method']} {req_info['path']}")
    print("=" * 80)
    
    request = req_info['request']
    response = req_info['response']
    
    # 分析请求的业务作用
    path = req_info['path']
    business_purpose = get_business_purpose(path, request)
    print(f"🎯 业务作用: {business_purpose}")
    print()
    
    # 详细请求信息
    print("📤 详细请求信息:")
    print(f"   方法: {request['method']}")
    print(f"   URL: {req_info['url']}")
    
    # 请求头
    print("   请求头:")
    for header in request.get('headers', []):
        name = header['name']
        value = header['value']
        if name.lower() == 'token':
            value = f"{value[:20]}...{value[-10:]}"
        elif len(value) > 100:
            value = value[:100] + "..."
        print(f"     {name}: {value}")
    
    # 请求参数
    if request.get('queryString'):
        print("   查询参数:")
        for param in request['queryString']:
            print(f"     {param['name']}: {param['value']}")
    
    if request.get('postData'):
        post_data = request['postData']
        print(f"   请求体类型: {post_data.get('mimeType')}")
        if post_data.get('text'):
            print(f"   请求体内容:")
            try:
                if 'json' in post_data.get('mimeType', ''):
                    json_data = json.loads(post_data['text'])
                    for key, value in json_data.items():
                        print(f"     {key}: {value}")
                else:
                    # URL编码格式解析
                    from urllib.parse import parse_qs
                    try:
                        parsed_data = parse_qs(post_data['text'])
                        for key, values in parsed_data.items():
                            print(f"     {key}: {values[0] if values else ''}")
                    except:
                        print(f"     原始内容: {post_data['text']}")
            except:
                print(f"     原始内容: {post_data['text'][:200]}...")
    
    print()
    
    # 详细响应信息
    print("📥 详细响应信息:")
    print(f"   状态码: {response.get('status')}")
    
    if response.get('content', {}).get('text'):
        content_text = response['content']['text']
        encoding = response['content'].get('encoding', '')
        
        try:
            if encoding == 'base64':
                decoded_content = base64.b64decode(content_text).decode('utf-8')
            else:
                decoded_content = content_text
            
            try:
                response_json = json.loads(decoded_content)
                print(f"   响应结构:")
                print(f"     ret: {response_json.get('ret')}")
                print(f"     sub: {response_json.get('sub')}")
                print(f"     msg: {response_json.get('msg')}")
                
                data = response_json.get('data', {})
                if data:
                    print(f"   响应数据:")
                    # 只显示关键字段
                    key_fields = ['order_id', 'order_total_price', 'order_payment_price', 
                                'voucher_use', 'pay_price', 'surcharge_price']
                    for field in key_fields:
                        if field in data:
                            print(f"     {field}: {data[field]}")
                
            except:
                print(f"   响应内容: {decoded_content[:200]}...")
                
        except Exception as e:
            print(f"   响应解析失败: {e}")
    
    print()
    print("-" * 80)
    print()

def get_business_purpose(path, request):
    """根据路径和请求内容判断业务作用"""
    if '/order/voucher/price/' in path:
        return "券价格计算 - 计算使用券码后的订单价格"
    elif '/order/change/' in path:
        return "订单变更/券绑定 - 将券码绑定到订单并更新支付信息"
    elif '/order/create/' in path:
        return "订单创建 - 创建新的订单"
    elif '/order/info/' in path:
        return "订单详情 - 获取订单的详细信息"
    elif '/seat/lock/' in path:
        return "座位锁定 - 锁定选中的座位"
    elif '/user/info/' in path:
        return "用户信息 - 获取用户基本信息"
    elif 'voucher' in path.lower():
        return "券码相关操作"
    elif 'order' in path.lower():
        return "订单相关操作"
    else:
        return "其他业务操作"

if __name__ == "__main__":
    voucher_requests = analyze_voucher_har_file()
    
    if voucher_requests:
        print("=" * 100)
        print("📝 券码支付流程总结")
        print("=" * 100)
        
        print("🎯 关键步骤:")
        for i, req in enumerate(voucher_requests, 1):
            purpose = get_business_purpose(req['path'], req['request'])
            print(f"  {i}. [{req['time']}] {req['method']} {req['path']}")
            print(f"     作用: {purpose}")
        
        print("\n💡 实现建议:")
        print("  1. 确保我们的系统包含所有必需的券码相关API调用")
        print("  2. 验证请求参数格式与HAR文件中的格式一致")
        print("  3. 实现正确的错误处理和重试逻辑")
        print("  4. 确保券价格计算和券绑定的顺序正确")
    else:
        print("❌ 未找到券码相关请求")
