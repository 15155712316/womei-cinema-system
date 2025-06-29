#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面分析沃美券绑定失败原因
处理Base64编码的HAR响应内容
"""

import sys
import os
import json
import re
import urllib.parse
import base64
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def decode_base64_response(content_text):
    """解码Base64响应内容"""
    try:
        # 尝试Base64解码
        decoded_bytes = base64.b64decode(content_text)
        decoded_text = decoded_bytes.decode('utf-8')
        
        # 尝试解析为JSON
        return json.loads(decoded_text)
    except:
        try:
            # 如果不是Base64，直接尝试JSON解析
            return json.loads(content_text)
        except:
            return None

def decode_base64_post_data(post_text):
    """解码Base64 POST数据"""
    try:
        # 尝试Base64解码
        decoded_bytes = base64.b64decode(post_text)
        decoded_text = decoded_bytes.decode('utf-8')
        
        # 解析URL编码的参数
        parsed = urllib.parse.parse_qs(decoded_text)
        return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
    except:
        try:
            # 如果不是Base64，直接尝试URL解码
            parsed = urllib.parse.parse_qs(post_text)
            return {key: values[0] if len(values) == 1 else values for key, values in parsed.items()}
        except:
            return {'raw_text': post_text}

def analyze_comprehensive_voucher_flow():
    """全面分析券绑定流程"""
    print("🎬 全面分析沃美券绑定失败原因")
    print("🎯 处理Base64编码的HAR响应内容")
    print("=" * 80)
    
    # 加载HAR文件
    har_file = "下单用券对比ct.womovie.cn_2025_06_29_14_51_48.har"
    
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        print(f"✅ HAR文件加载成功: {har_file}")
    except Exception as e:
        print(f"❌ 加载HAR文件失败: {e}")
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
    successful_voucher_bindings = []
    
    for i, req in enumerate(voucher_requests, 1):
        print(f"\n{'='*80}")
        print(f"📋 请求 {i}: {req['method']} {req['url']}")
        print(f"⏰ 时间: {req['timestamp']}")
        
        # 分析请求参数
        post_params = {}
        if req['method'] == 'POST':
            post_data = req['request'].get('postData', {})
            if post_data:
                text = post_data.get('text', '')
                if text:
                    post_params = decode_base64_post_data(text)
                    print(f"📤 POST参数:")
                    for key, value in post_params.items():
                        if key != 'raw_text':
                            print(f"   {key}: {value}")
        
        # 分析响应
        response = req['response']
        status = response.get('status', 0)
        print(f"📥 响应状态: {status}")
        
        # 解析响应内容
        content = response.get('content', {})
        content_text = content.get('text', '')
        
        if content_text:
            response_data = decode_base64_response(content_text)
            
            if response_data:
                print(f"📄 响应数据:")
                ret = response_data.get('ret', 'N/A')
                sub = response_data.get('sub', 'N/A')
                msg = response_data.get('msg', 'N/A')
                
                print(f"   ret: {ret}")
                print(f"   sub: {sub}")
                print(f"   msg: {msg}")
                
                # 检查data字段
                data = response_data.get('data', {})
                if data:
                    print(f"   📊 data字段分析:")
                    
                    # 订单相关信息
                    order_fields = ['order_id', 'order_total_price', 'order_payment_price', 'order_unfee_total_price']
                    for field in order_fields:
                        if field in data:
                            print(f"     {field}: {data[field]}")
                    
                    # 券使用信息
                    voucher_use = data.get('voucher_use', {})
                    if voucher_use:
                        print(f"     🎫 voucher_use:")
                        print(f"       use_codes: {voucher_use.get('use_codes', [])}")
                        print(f"       use_total_price: {voucher_use.get('use_total_price', 0)}")
                        print(f"       use_voucher_count: {voucher_use.get('use_voucher_count', 0)}")
                    
                    # 券折扣信息
                    voucher_discounts = data.get('voucher_discounts', [])
                    if voucher_discounts:
                        print(f"     💰 voucher_discounts: {len(voucher_discounts)} 项")
                        for j, discount in enumerate(voucher_discounts):
                            if isinstance(discount, dict):
                                print(f"       [{j}] code: {discount.get('code', 'N/A')}, amount: {discount.get('amount', 0)}")
                            else:
                                print(f"       [{j}] {discount}")
                    
                    # 检查是否为成功的券绑定
                    if (req['method'] == 'POST' and '/order/change' in req['url'] and 
                        ret == 0 and sub == 0):
                        
                        # 检查是否有券相关参数
                        has_voucher_code = 'voucher_code' in post_params and post_params['voucher_code']
                        has_voucher_discount_type = post_params.get('discount_type') == 'TP_VOUCHER'
                        
                        if has_voucher_code or has_voucher_discount_type:
                            print(f"   🎉 识别为券绑定请求")
                            
                            # 检查是否成功绑定
                            voucher_bound = False
                            if voucher_use and voucher_use.get('use_codes'):
                                voucher_bound = True
                                print(f"   ✅ 券绑定成功: {voucher_use.get('use_codes')}")
                            elif voucher_discounts:
                                voucher_bound = True
                                print(f"   ✅ 券折扣生效: {len(voucher_discounts)} 项")
                            elif data.get('order_payment_price') == 0:
                                voucher_bound = True
                                print(f"   ✅ 订单被完全抵扣")
                            
                            if voucher_bound:
                                successful_voucher_bindings.append({
                                    'request_index': i,
                                    'request': req,
                                    'post_params': post_params,
                                    'response_data': response_data,
                                    'voucher_code': post_params.get('voucher_code', ''),
                                    'order_id': post_params.get('order_id', ''),
                                    'voucher_use': voucher_use,
                                    'voucher_discounts': voucher_discounts,
                                    'order_payment_price': data.get('order_payment_price', 0)
                                })
                            else:
                                print(f"   ⚠️ 券绑定请求但未发现绑定成功证据")
            else:
                print(f"   ❌ 响应内容解析失败")
        else:
            print(f"   ⚠️ 无响应内容")
    
    # 分析成功案例
    print(f"\n🎯 成功券绑定案例分析")
    print("=" * 80)
    print(f"📊 找到成功券绑定案例: {len(successful_voucher_bindings)} 个")
    
    if successful_voucher_bindings:
        for i, case in enumerate(successful_voucher_bindings, 1):
            print(f"\n🎉 成功案例 {i}:")
            print(f"   券码: {case['voucher_code']}")
            print(f"   订单号: {case['order_id']}")
            print(f"   最终支付金额: {case['order_payment_price']}")
            
            if case['voucher_use']:
                print(f"   使用券码: {case['voucher_use'].get('use_codes', [])}")
                print(f"   抵扣金额: {case['voucher_use'].get('use_total_price', 0)}")
    
    # 对比当前失败案例
    analyze_failure_comparison(successful_voucher_bindings)

def analyze_failure_comparison(successful_cases):
    """分析失败案例对比"""
    print(f"\n📊 失败案例对比分析")
    print("=" * 80)
    
    current_failure = {
        "order_id": "250629134710001936",
        "cinema_id": "400028",
        "cinema_name": "北京沃美世界城店",
        "voucher_code": "GZJY01002948416827",
        "error_code": "sub=4004",
        "error_message": "获取兑换券验券异常，请联系影院"
    }
    
    print(f"❌ 当前失败案例:")
    print(f"   订单号: {current_failure['order_id']}")
    print(f"   影院: {current_failure['cinema_name']} (ID: {current_failure['cinema_id']})")
    print(f"   券码: {current_failure['voucher_code']}")
    print(f"   错误: {current_failure['error_code']}, {current_failure['error_message']}")
    
    if not successful_cases:
        print(f"\n⚠️ 未找到成功案例进行对比")
        print(f"💡 可能的原因:")
        print(f"   1. HAR文件中没有成功的券绑定案例")
        print(f"   2. 券绑定流程可能存在问题")
        print(f"   3. 需要检查完整的券绑定工作流程")
        return
    
    # 对比参数
    print(f"\n🔍 参数对比分析:")
    
    for i, case in enumerate(successful_cases, 1):
        print(f"\n✅ 成功案例 {i} 对比:")
        
        success_params = case['post_params']
        
        print(f"   参数对比:")
        print(f"     订单号: 成功={success_params.get('order_id', 'N/A')} vs 失败={current_failure['order_id']}")
        print(f"     券码: 成功={success_params.get('voucher_code', 'N/A')} vs 失败={current_failure['voucher_code']}")
        print(f"     折扣类型: {success_params.get('discount_type', 'N/A')}")
        print(f"     支付类型: {success_params.get('pay_type', 'N/A')}")
        print(f"     券码类型: {success_params.get('voucher_code_type', 'N/A')}")
        
        # 分析关键差异
        differences = []
        
        if success_params.get('voucher_code') != current_failure['voucher_code']:
            differences.append("券码不同")
        
        if success_params.get('order_id') != current_failure['order_id']:
            differences.append("订单号不同")
        
        print(f"   关键差异: {differences if differences else '无明显差异'}")

def generate_root_cause_analysis():
    """生成根本原因分析"""
    print(f"\n📋 根本原因分析报告")
    print("=" * 80)
    
    print(f"🎯 sub=4004错误分析:")
    print(f"   错误代码: sub=4004")
    print(f"   错误信息: '获取兑换券验券异常，请联系影院'")
    print(f"   错误类型: 券验证异常")
    
    print(f"\n💡 可能的根本原因:")
    
    reasons = [
        {
            "原因": "券码状态问题",
            "描述": "券码GZJY01002948416827可能已被使用、过期或冻结",
            "验证方法": "检查券码在用户券列表中的状态和有效期",
            "优先级": "高"
        },
        {
            "原因": "影院限制",
            "描述": "券码可能不适用于北京沃美世界城店(400028)",
            "验证方法": "在其他影院测试相同券码，或检查券码适用范围",
            "优先级": "高"
        },
        {
            "原因": "订单状态不匹配",
            "描述": "订单250629134710001936可能不在可绑券状态",
            "验证方法": "检查订单状态，确保为PENDING或类似可修改状态",
            "优先级": "中"
        },
        {
            "原因": "时序依赖问题",
            "描述": "可能需要先调用券价格计算接口",
            "验证方法": "按HAR文件中的完整序列执行",
            "优先级": "中"
        },
        {
            "原因": "参数格式问题",
            "描述": "请求参数可能与成功案例存在细微差异",
            "验证方法": "严格按照成功案例的参数格式构造请求",
            "优先级": "低"
        }
    ]
    
    for i, reason in enumerate(reasons, 1):
        print(f"\n{i}. {reason['原因']} (优先级: {reason['优先级']}):")
        print(f"   描述: {reason['描述']}")
        print(f"   验证方法: {reason['验证方法']}")
    
    print(f"\n🔧 建议的解决方案:")
    print(f"   1. 立即验证: 检查券码GZJY01002948416827的当前状态")
    print(f"   2. 影院测试: 在其他影院测试相同券码")
    print(f"   3. 流程验证: 按HAR文件中的完整流程执行券绑定")
    print(f"   4. 参数对比: 严格对比成功案例的所有参数")
    print(f"   5. 状态检查: 确认订单状态支持券绑定操作")

def main():
    """主函数"""
    analyze_comprehensive_voucher_flow()
    generate_root_cause_analysis()
    
    print(f"\n✅ 分析完成")
    print(f"📋 建议优先验证券码状态和影院适用性")

if __name__ == "__main__":
    main()
