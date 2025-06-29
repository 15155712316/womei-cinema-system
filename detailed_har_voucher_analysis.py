#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析HAR文件中的券绑定流程
深入检查每个请求的详细内容
"""

import sys
import os
import json
import re
import urllib.parse
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_har_file():
    """加载HAR文件"""
    har_file = "下单用券对比ct.womovie.cn_2025_06_29_14_51_48.har"
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        print(f"✅ HAR文件加载成功: {har_file}")
        return har_data
        
    except Exception as e:
        print(f"❌ 加载HAR文件失败: {e}")
        return None

def extract_post_data(request):
    """提取POST数据"""
    post_data = request.get('postData', {})
    if not post_data:
        return {}
    
    text = post_data.get('text', '')
    mime_type = post_data.get('mimeType', '')
    
    if 'application/x-www-form-urlencoded' in mime_type and text:
        try:
            parsed = urllib.parse.parse_qs(text)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        except:
            return {'raw_text': text}
    
    return {'raw_text': text}

def analyze_voucher_requests():
    """分析券相关请求"""
    print("🔍 详细分析券相关请求")
    print("=" * 80)
    
    har_data = load_har_file()
    if not har_data:
        return
    
    entries = har_data.get('log', {}).get('entries', [])
    
    # 券相关的URL模式
    voucher_patterns = [
        r'/voucher/',
        r'/order/change',
        r'/order/voucher/price',
        r'/user/voucher/list'
    ]
    
    voucher_requests = []
    
    for entry in entries:
        request = entry.get('request', {})
        url = request.get('url', '')
        method = request.get('method', '')
        
        # 检查是否是券相关请求
        is_voucher_related = any(re.search(pattern, url, re.IGNORECASE) for pattern in voucher_patterns)
        
        if is_voucher_related:
            response = entry.get('response', {})
            voucher_requests.append({
                'url': url,
                'method': method,
                'request': request,
                'response': response,
                'timestamp': entry.get('startedDateTime', ''),
                'time': entry.get('time', 0)
            })
    
    # 按时间排序
    voucher_requests.sort(key=lambda x: x['timestamp'])
    
    print(f"📊 找到券相关请求: {len(voucher_requests)} 个")
    
    # 详细分析每个请求
    for i, req in enumerate(voucher_requests, 1):
        print(f"\n{'='*60}")
        print(f"📋 请求 {i}: {req['method']} {req['url']}")
        print(f"⏰ 时间: {req['timestamp']}")
        
        # 分析请求参数
        if req['method'] == 'POST':
            post_data = extract_post_data(req['request'])
            if post_data:
                print(f"📤 POST参数:")
                for key, value in post_data.items():
                    print(f"   {key}: {value}")
        
        # 分析响应
        response = req['response']
        status = response.get('status', 0)
        print(f"📥 响应状态: {status}")
        
        # 解析响应内容
        content = response.get('content', {})
        content_text = content.get('text', '')
        
        if content_text:
            try:
                response_data = json.loads(content_text)
                print(f"📄 响应数据:")
                print(f"   ret: {response_data.get('ret', 'N/A')}")
                print(f"   sub: {response_data.get('sub', 'N/A')}")
                print(f"   msg: {response_data.get('msg', 'N/A')}")
                
                # 检查是否有data字段
                data = response_data.get('data', {})
                if data:
                    print(f"   data字段:")
                    
                    # 检查订单相关信息
                    if 'order_id' in data:
                        print(f"     order_id: {data['order_id']}")
                    if 'order_payment_price' in data:
                        print(f"     order_payment_price: {data['order_payment_price']}")
                    
                    # 检查券使用信息
                    voucher_use = data.get('voucher_use', {})
                    if voucher_use:
                        print(f"     voucher_use:")
                        print(f"       use_codes: {voucher_use.get('use_codes', [])}")
                        print(f"       use_total_price: {voucher_use.get('use_total_price', 0)}")
                        print(f"       use_voucher_count: {voucher_use.get('use_voucher_count', 0)}")
                    
                    # 检查券折扣信息
                    voucher_discounts = data.get('voucher_discounts', [])
                    if voucher_discounts:
                        print(f"     voucher_discounts: {len(voucher_discounts)} 项")
                        for j, discount in enumerate(voucher_discounts):
                            print(f"       [{j}] code: {discount.get('code', 'N/A')}, amount: {discount.get('amount', 0)}")
                    
                    # 检查其他重要字段
                    important_fields = ['total_price', 'discount_price', 'final_price', 'voucher_price']
                    for field in important_fields:
                        if field in data:
                            print(f"     {field}: {data[field]}")
                
            except json.JSONDecodeError:
                print(f"   响应内容（非JSON）: {content_text[:200]}...")
        else:
            print(f"   无响应内容")
    
    return voucher_requests

def identify_successful_voucher_binding(voucher_requests):
    """识别成功的券绑定"""
    print(f"\n🎯 识别成功的券绑定")
    print("=" * 80)
    
    successful_cases = []
    
    for i, req in enumerate(voucher_requests, 1):
        if req['method'] == 'POST' and '/order/change' in req['url']:
            response = req['response']
            content = response.get('content', {})
            content_text = content.get('text', '')
            
            if content_text:
                try:
                    response_data = json.loads(content_text)
                    ret = response_data.get('ret', -1)
                    sub = response_data.get('sub', -1)
                    
                    print(f"\n📋 请求 {i} 分析:")
                    print(f"   URL: {req['url']}")
                    print(f"   ret: {ret}, sub: {sub}")
                    
                    data = response_data.get('data', {})
                    
                    # 检查是否成功
                    if ret == 0 and sub == 0:
                        print(f"   ✅ API调用成功")
                        
                        # 检查是否有券使用信息
                        voucher_use = data.get('voucher_use', {})
                        voucher_discounts = data.get('voucher_discounts', [])
                        order_payment_price = data.get('order_payment_price', None)
                        
                        print(f"   券使用信息:")
                        print(f"     voucher_use: {bool(voucher_use)}")
                        print(f"     voucher_discounts: {len(voucher_discounts)} 项")
                        print(f"     order_payment_price: {order_payment_price}")
                        
                        # 判断是否真正绑定了券
                        has_voucher_binding = False
                        
                        if voucher_use and voucher_use.get('use_codes'):
                            print(f"   🎫 发现券使用: {voucher_use.get('use_codes')}")
                            has_voucher_binding = True
                        
                        if voucher_discounts:
                            print(f"   💰 发现券折扣: {len(voucher_discounts)} 项")
                            has_voucher_binding = True
                        
                        if order_payment_price == 0:
                            print(f"   💳 订单金额为0，可能被券完全抵扣")
                            has_voucher_binding = True
                        
                        if has_voucher_binding:
                            print(f"   🎉 确认为成功的券绑定案例")
                            successful_cases.append({
                                'request_index': i,
                                'request': req,
                                'response_data': response_data,
                                'voucher_use': voucher_use,
                                'voucher_discounts': voucher_discounts,
                                'order_payment_price': order_payment_price
                            })
                        else:
                            print(f"   ⚠️ API成功但未发现券绑定证据")
                    else:
                        print(f"   ❌ API调用失败: ret={ret}, sub={sub}")
                        if 'msg' in response_data:
                            print(f"   错误信息: {response_data['msg']}")
                
                except json.JSONDecodeError:
                    print(f"   ❌ 响应解析失败")
    
    print(f"\n📊 成功券绑定案例统计: {len(successful_cases)} 个")
    return successful_cases

def compare_with_current_failure(successful_cases):
    """对比成功案例与当前失败案例"""
    print(f"\n📊 对比成功案例与当前失败案例")
    print("=" * 80)
    
    current_failure = {
        "order_id": "250629134710001936",
        "cinema_id": "400028",
        "voucher_code": "GZJY01002948416827",
        "error_code": "sub=4004",
        "error_message": "获取兑换券验券异常，请联系影院"
    }
    
    if not successful_cases:
        print("❌ 没有成功案例可供对比")
        return
    
    print(f"🎯 当前失败案例:")
    print(f"   订单号: {current_failure['order_id']}")
    print(f"   影院ID: {current_failure['cinema_id']}")
    print(f"   券码: {current_failure['voucher_code']}")
    print(f"   错误: {current_failure['error_code']}, {current_failure['error_message']}")
    
    for i, case in enumerate(successful_cases, 1):
        print(f"\n🎉 成功案例 {i}:")
        
        # 提取请求参数
        post_data = extract_post_data(case['request']['request'])
        
        print(f"   请求参数对比:")
        print(f"     order_id: {post_data.get('order_id', 'N/A')}")
        print(f"     voucher_code: {post_data.get('voucher_code', 'N/A')}")
        print(f"     discount_type: {post_data.get('discount_type', 'N/A')}")
        print(f"     pay_type: {post_data.get('pay_type', 'N/A')}")
        
        print(f"   响应结果:")
        voucher_use = case['voucher_use']
        if voucher_use:
            print(f"     使用券码: {voucher_use.get('use_codes', [])}")
            print(f"     抵扣金额: {voucher_use.get('use_total_price', 0)}")
        
        print(f"     最终支付金额: {case['order_payment_price']}")

def main():
    """主函数"""
    print("🎬 详细HAR文件券绑定分析")
    print("🎯 深入分析每个券相关请求的详细内容")
    print("=" * 80)
    
    # 1. 分析券相关请求
    voucher_requests = analyze_voucher_requests()
    
    if not voucher_requests:
        print("❌ 未找到券相关请求")
        return
    
    # 2. 识别成功的券绑定
    successful_cases = identify_successful_voucher_binding(voucher_requests)
    
    # 3. 对比分析
    compare_with_current_failure(successful_cases)
    
    print(f"\n📋 分析总结")
    print("=" * 80)
    print(f"✅ 分析完成")
    print(f"📊 券相关请求: {len(voucher_requests)} 个")
    print(f"🎉 成功券绑定: {len(successful_cases)} 个")

if __name__ == "__main__":
    main()
