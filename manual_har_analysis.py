#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动分析HAR文件中的会员卡密码差异
"""

import json
import base64
from urllib.parse import unquote

def decode_base64_safely(content):
    """安全解码base64内容"""
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        try:
            return json.loads(decoded)
        except:
            return decoded
    except Exception as e:
        print(f"解码失败: {e}")
        return content

def analyze_order_detail_response(content):
    """分析订单详情响应"""
    if isinstance(content, dict):
        result_data = content.get('resultData', {})
        if result_data:
            print("🔍 订单详情关键字段:")
            print(f"  - enable_mempassword: {result_data.get('enable_mempassword', 'N/A')}")
            print(f"  - memPayONLY: {result_data.get('memPayONLY', 'N/A')}")
            print(f"  - mem_totalprice: {result_data.get('mem_totalprice', 'N/A')}")
            print(f"  - totalprice: {result_data.get('totalprice', 'N/A')}")
            print(f"  - payAmount: {result_data.get('payAmount', 'N/A')}")
            print(f"  - balance: {result_data.get('balance', 'N/A')}")
            return result_data
    return None

def analyze_member_info_response(content):
    """分析会员信息响应"""
    if isinstance(content, dict):
        result_data = content.get('resultData', {})
        if result_data:
            print("👤 会员信息关键字段:")
            print(f"  - cardno: {result_data.get('cardno', 'N/A')}")
            print(f"  - balance: {result_data.get('balance', 'N/A')}")
            print(f"  - cardtype: {result_data.get('cardtype', 'N/A')}")
            print(f"  - cardcinemaid: {result_data.get('cardcinemaid', 'N/A')}")
            return result_data
    return None

def analyze_har_file_detailed(filename):
    """详细分析HAR文件"""
    print(f"\n{'='*80}")
    print(f"📁 分析文件: {filename}")
    print(f"{'='*80}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        har_data = json.load(f)
    
    entries = har_data['log']['entries']
    
    order_detail_data = None
    member_info_data = None
    
    for entry in entries:
        url = entry['request']['url']
        method = entry['request']['method']
        
        # 分析订单详情API
        if 'getUnpaidOrderDetail' in url:
            print(f"\n🎯 订单详情API: {method} {url}")
            if 'content' in entry['response'] and 'text' in entry['response']['content']:
                content = entry['response']['content']['text']
                if entry['response']['content'].get('encoding') == 'base64':
                    decoded_content = decode_base64_safely(content)
                    order_detail_data = analyze_order_detail_response(decoded_content)
        
        # 分析会员信息API
        elif 'getMemberInfo' in url:
            print(f"\n👤 会员信息API: {method} {url}")
            if 'content' in entry['response'] and 'text' in entry['response']['content']:
                content = entry['response']['content']['text']
                if entry['response']['content'].get('encoding') == 'base64':
                    decoded_content = decode_base64_safely(content)
                    member_info_data = analyze_member_info_response(decoded_content)
    
    return {
        'order_detail': order_detail_data,
        'member_info': member_info_data,
        'domain': entries[0]['request']['url'].split('/')[2] if entries else 'unknown'
    }

def main():
    print("🔐 会员卡密码支付差异分析")
    print("="*80)
    
    # 分析需要密码的文件
    password_required_data = analyze_har_file_detailed("需要密码支付www.heibaiyingye.cn_2025_06_04_16_22_38.har")
    
    # 分析不需要密码的文件
    no_password_data = analyze_har_file_detailed("不需要会员卡密码zcxzs7.cityfilms.cn_2025_06_04_16_23_21.har")
    
    # 对比分析
    print(f"\n{'='*80}")
    print("📊 密码策略对比分析")
    print(f"{'='*80}")
    
    print(f"\n🏢 需要密码的影城 ({password_required_data['domain']}):")
    if password_required_data['order_detail']:
        enable_mempassword = password_required_data['order_detail'].get('enable_mempassword', 'N/A')
        print(f"  - enable_mempassword: {enable_mempassword}")
        print(f"  - 需要密码: {'是' if enable_mempassword == '1' else '否'}")
    
    print(f"\n🏢 不需要密码的影城 ({no_password_data['domain']}):")
    if no_password_data['order_detail']:
        enable_mempassword = no_password_data['order_detail'].get('enable_mempassword', 'N/A')
        print(f"  - enable_mempassword: {enable_mempassword}")
        print(f"  - 需要密码: {'是' if enable_mempassword == '1' else '否'}")
    
    # 生成实现建议
    print(f"\n{'='*80}")
    print("💡 实现建议")
    print(f"{'='*80}")
    
    print("""
🎯 核心判断逻辑:
1. 从订单详情API响应中获取 'enable_mempassword' 字段
2. 当 enable_mempassword == '1' 时，需要会员卡密码
3. 当 enable_mempassword == '0' 时，不需要会员卡密码

🔧 实现步骤:
1. 在订单创建后，调用 getUnpaidOrderDetail API
2. 解析响应中的 enable_mempassword 字段
3. 根据该字段动态显示/隐藏密码输入框
4. 在支付时根据策略决定是否包含密码参数

🛡️ 安全考虑:
- 密码输入框应使用密码类型输入
- 密码不应在日志中记录
- 支付失败时提供明确的错误提示
    """)

if __name__ == "__main__":
    main()
