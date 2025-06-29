#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比HAR文件中成功的券绑定请求与我们的测试请求
找出参数差异
"""

import json
import base64
from urllib.parse import unquote

def decode_content(content_data):
    """解码内容"""
    if not content_data or 'text' not in content_data:
        return ''
    
    try:
        if content_data.get('encoding') == 'base64':
            return base64.b64decode(content_data['text']).decode('utf-8')
        else:
            return content_data['text']
    except Exception as e:
        return f'解码失败: {e}'

def parse_form_data(form_data):
    """解析表单数据"""
    if not form_data:
        return {}
    
    try:
        # URL解码
        decoded_data = unquote(form_data)
        # 解析键值对
        pairs = decoded_data.split('&')
        result = {}
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                result[key] = value
        return result
    except Exception as e:
        print(f"解析表单数据失败: {e}")
        return {}

def analyze_har_voucher_requests():
    """分析HAR文件中的券绑定请求"""
    try:
        # 读取HAR文件
        with open('沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        
        print("🔍 分析HAR文件中的券绑定请求")
        print("=" * 80)
        
        # 找出所有的 order/change 请求
        order_change_requests = []
        for i, entry in enumerate(entries):
            if '/order/change/' in entry['request']['url'] and entry['request']['method'] == 'POST':
                order_change_requests.append((i+1, entry))
        
        print(f"📊 找到 {len(order_change_requests)} 个订单修改请求")
        print("=" * 80)
        
        # 分析每个请求
        for req_num, (index, entry) in enumerate(order_change_requests):
            print(f"\n🔗 HAR请求 #{req_num+1} (第{index}个请求)")
            print(f"⏰ 时间: {entry['startedDateTime']}")
            print(f"🌐 URL: {entry['request']['url']}")
            
            # 解析请求参数
            request_data = decode_content(entry['request'].get('postData', {}))
            parsed_params = parse_form_data(request_data)
            
            print(f"📤 HAR请求参数:")
            for key, value in sorted(parsed_params.items()):
                print(f"   {key}: '{value}'")
            
            # 解析响应数据
            response_content = decode_content(entry['response'].get('content', {}))
            try:
                response_json = json.loads(response_content)
                print(f"📥 HAR响应状态: ret={response_json.get('ret')}, sub={response_json.get('sub')}, msg={response_json.get('msg')}")
                
                # 检查是否是券绑定请求
                if 'voucher_code' in parsed_params and parsed_params['voucher_code']:
                    print(f"🎫 这是券绑定请求:")
                    print(f"   券码: {parsed_params.get('voucher_code', 'N/A')}")
                    print(f"   券类型: {parsed_params.get('voucher_code_type', 'N/A')}")
                    print(f"   折扣类型: {parsed_params.get('discount_type', 'N/A')}")
                    
                    if response_json.get('ret') == 0 and response_json.get('sub') == 0:
                        print(f"   ✅ 券绑定成功！")
                        return parsed_params, response_json
                    else:
                        print(f"   ❌ 券绑定失败")
                else:
                    print(f"📋 这是普通订单修改请求")
                
            except json.JSONDecodeError:
                print(f"📥 响应解析失败")
            
            print("-" * 60)
        
        return None, None
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None, None

def compare_with_our_request():
    """对比我们的请求参数"""
    print("\n🔄 我们的测试请求参数")
    print("=" * 80)
    
    our_params = {
        'order_id': '250624183610000972',
        'discount_id': '0',
        'discount_type': 'TP_VOUCHER',
        'card_id': '',
        'pay_type': 'WECHAT',
        'rewards': '[]',
        'use_rewards': 'Y',
        'use_limit_cards': 'N',
        'limit_cards': '[]',
        'voucher_code': 'GZJY01002948416827',
        'voucher_code_type': 'VGC_T',
        'ticket_pack_goods': ' '
    }
    
    print(f"📤 我们的请求参数:")
    for key, value in sorted(our_params.items()):
        print(f"   {key}: '{value}'")
    
    return our_params

def find_parameter_differences(har_params, our_params):
    """找出参数差异"""
    print("\n🔍 参数差异分析")
    print("=" * 80)
    
    if not har_params:
        print("❌ 没有找到HAR中成功的券绑定请求")
        return
    
    print(f"📋 参数对比:")
    
    # 找出HAR中有但我们没有的参数
    har_only = set(har_params.keys()) - set(our_params.keys())
    if har_only:
        print(f"\n🔴 HAR中有但我们缺少的参数:")
        for key in sorted(har_only):
            print(f"   {key}: '{har_params[key]}'")
    
    # 找出我们有但HAR中没有的参数
    our_only = set(our_params.keys()) - set(har_params.keys())
    if our_only:
        print(f"\n🟡 我们有但HAR中没有的参数:")
        for key in sorted(our_only):
            print(f"   {key}: '{our_params[key]}'")
    
    # 找出值不同的参数
    common_keys = set(har_params.keys()) & set(our_params.keys())
    different_values = []
    for key in common_keys:
        if har_params[key] != our_params[key]:
            different_values.append(key)
    
    if different_values:
        print(f"\n🟠 值不同的参数:")
        for key in sorted(different_values):
            print(f"   {key}:")
            print(f"     HAR: '{har_params[key]}'")
            print(f"     我们: '{our_params[key]}'")
    
    # 找出值相同的参数
    same_values = []
    for key in common_keys:
        if har_params[key] == our_params[key]:
            same_values.append(key)
    
    if same_values:
        print(f"\n✅ 值相同的参数:")
        for key in sorted(same_values):
            print(f"   {key}: '{har_params[key]}'")

def generate_corrected_request(har_params):
    """生成修正后的请求参数"""
    if not har_params:
        return
    
    print(f"\n🔧 建议的修正请求参数")
    print("=" * 80)
    
    # 使用HAR中的参数，但替换订单ID和券码
    corrected_params = har_params.copy()
    corrected_params['order_id'] = '250624183610000972'  # 我们的订单ID
    corrected_params['voucher_code'] = 'GZJY01002948416827'  # 我们的券码
    
    print(f"📤 修正后的请求参数:")
    for key, value in sorted(corrected_params.items()):
        print(f"   {key}: '{value}'")
    
    print(f"\n🐍 Python代码:")
    print("data = {")
    for key, value in sorted(corrected_params.items()):
        print(f"    '{key}': '{value}',")
    print("}")

def main():
    """主函数"""
    print("🎬 HAR文件券绑定请求参数对比分析")
    print("🎯 找出我们的请求与HAR成功请求的差异")
    print("=" * 80)
    
    # 分析HAR文件中的券绑定请求
    har_params, har_response = analyze_har_voucher_requests()
    
    # 我们的请求参数
    our_params = compare_with_our_request()
    
    # 对比差异
    find_parameter_differences(har_params, our_params)
    
    # 生成修正建议
    generate_corrected_request(har_params)
    
    print(f"\n" + "=" * 80)
    print("✅ 参数对比分析完成！")

if __name__ == "__main__":
    main()
