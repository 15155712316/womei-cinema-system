#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件分析脚本 - 解析混合下单流程
"""

import json
import base64
import urllib.parse
from datetime import datetime

def decode_base64_content(content):
    """解码base64内容"""
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        # 尝试解析为JSON
        try:
            return json.loads(decoded)
        except:
            return decoded
    except:
        return content

def parse_har_file(har_path):
    """解析HAR文件"""
    with open(har_path, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    print("🔍 混合下单流程API调用分析")
    print("="*80)
    
    # 按时间排序
    entries.sort(key=lambda x: x['startedDateTime'])
    
    api_calls = []
    
    for i, entry in enumerate(entries, 1):
        request = entry['request']
        response = entry['response']
        
        # 解析URL
        url = request['url']
        method = request['method']
        
        # 解析请求参数
        query_params = {}
        if 'queryString' in request:
            for param in request['queryString']:
                query_params[param['name']] = param['value']
        
        # 解析POST数据
        post_data = None
        if method == 'POST' and 'postData' in request:
            if request['postData'].get('encoding') == 'base64':
                post_data = decode_base64_content(request['postData']['text'])
            else:
                post_data = request['postData'].get('text', '')
        
        # 解析响应数据
        response_data = None
        if 'content' in response and 'text' in response['content']:
            if response['content'].get('encoding') == 'base64':
                response_data = decode_base64_content(response['content']['text'])
            else:
                response_data = response['content']['text']
        
        # 提取API路径
        api_path = url.split('/')[-1].split('?')[0]
        
        api_call = {
            'step': i,
            'timestamp': entry['startedDateTime'],
            'method': method,
            'api_path': api_path,
            'full_url': url,
            'query_params': query_params,
            'post_data': post_data,
            'response_data': response_data,
            'status': response['status']
        }
        
        api_calls.append(api_call)
        
        print(f"\n📋 步骤 {i}: {method} {api_path}")
        print(f"时间: {entry['startedDateTime']}")
        print(f"状态: {response['status']}")
        
        if query_params:
            print("查询参数:")
            for key, value in query_params.items():
                if key in ['orderno', 'couponcode', 'userid']:
                    print(f"  {key}: {value}")
        
        if post_data and isinstance(post_data, str):
            # 解析URL编码的POST数据
            try:
                parsed_post = urllib.parse.parse_qs(post_data)
                print("POST参数:")
                for key, values in parsed_post.items():
                    if key in ['totalprice', 'memberinfo', 'orderno', 'couponcodes', 'price', 'discountprice']:
                        print(f"  {key}: {values[0] if values else ''}")
            except:
                print(f"POST数据: {post_data[:100]}...")
        
        if response_data and isinstance(response_data, dict):
            print("响应数据:")
            if 'resultCode' in response_data:
                print(f"  resultCode: {response_data['resultCode']}")
                print(f"  resultDesc: {response_data.get('resultDesc', '')}")
                
                if 'resultData' in response_data and response_data['resultData']:
                    result_data = response_data['resultData']
                    # 显示关键字段
                    key_fields = ['orderno', 'paymentAmount', 'mempaymentAmount', 'discountprice', 
                                'totalprice', 'totalmemprice', 'mem_totalprice', 'actualPrice']
                    for field in key_fields:
                        if field in result_data:
                            print(f"  {field}: {result_data[field]}")
    
    return api_calls

def analyze_mixed_payment_flow(api_calls):
    """分析混合支付流程"""
    print("\n\n🎯 混合支付流程分析")
    print("="*80)
    
    # 识别关键步骤
    key_steps = {
        'createOrder': None,
        'getMemberInfo': [],
        'getCouponByOrder': [],
        'ordercouponPrepay': None,
        'getUnpaidOrderDetail': [],
        'memcardPay': None,
        'getOrderDetail': None
    }
    
    for call in api_calls:
        api = call['api_path']
        if api in key_steps:
            if isinstance(key_steps[api], list):
                key_steps[api].append(call)
            else:
                key_steps[api] = call
    
    print("📊 关键步骤识别:")
    for step_name, step_data in key_steps.items():
        if step_data:
            if isinstance(step_data, list):
                print(f"  {step_name}: {len(step_data)} 次调用")
            else:
                print(f"  {step_name}: 1 次调用")
    
    # 分析价格计算流程
    print("\n💰 价格计算流程:")
    
    # 1. 订单创建
    if key_steps['createOrder']:
        create_order = key_steps['createOrder']
        print(f"1. 创建订单 (步骤 {create_order['step']})")
        if create_order['response_data'] and isinstance(create_order['response_data'], dict):
            result_data = create_order['response_data'].get('resultData', {})
            print(f"   订单号: {result_data.get('orderno', 'N/A')}")
    
    # 2. 券预支付验证
    if key_steps['ordercouponPrepay']:
        prepay = key_steps['ordercouponPrepay']
        print(f"2. 券预支付验证 (步骤 {prepay['step']})")
        if prepay['response_data'] and isinstance(prepay['response_data'], dict):
            result_data = prepay['response_data'].get('resultData', {})
            print(f"   原价: {result_data.get('totalprice', 'N/A')} 分")
            print(f"   会员价: {result_data.get('totalmemprice', 'N/A')} 分")
            print(f"   券抵扣后支付金额: {result_data.get('paymentAmount', 'N/A')} 分")
            print(f"   券抵扣后会员支付金额: {result_data.get('mempaymentAmount', 'N/A')} 分")
            print(f"   券抵扣金额: {result_data.get('discountprice', 'N/A')} 分")
            print(f"   券抵扣会员价金额: {result_data.get('discountmemprice', 'N/A')} 分")
    
    # 3. 会员卡支付
    if key_steps['memcardPay']:
        pay = key_steps['memcardPay']
        print(f"3. 会员卡支付 (步骤 {pay['step']})")
        if pay['post_data']:
            try:
                parsed_post = urllib.parse.parse_qs(pay['post_data'])
                print(f"   支付总价: {parsed_post.get('totalprice', ['N/A'])[0]} 分")
                print(f"   实际支付价格: {parsed_post.get('price', ['N/A'])[0]} 分")
                print(f"   券抵扣金额: {parsed_post.get('discountprice', ['N/A'])[0]} 分")
                print(f"   券码: {parsed_post.get('couponcodes', ['N/A'])[0]}")
            except:
                pass
    
    return key_steps

if __name__ == "__main__":
    har_file = "大都荟混合下单_05_30_10_58_38.har"
    
    try:
        api_calls = parse_har_file(har_file)
        key_steps = analyze_mixed_payment_flow(api_calls)
        
        print(f"\n✅ 分析完成，共识别 {len(api_calls)} 个API调用")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
