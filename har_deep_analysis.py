#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件深度分析 - 券使用流程优化验证
重点分析 POST /order/change/ 接口的券绑定能力
"""

import json
import base64
from urllib.parse import unquote, parse_qs
from datetime import datetime

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

def analyze_order_change_requests():
    """分析订单修改请求"""
    try:
        # 读取HAR文件
        with open('沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        
        print("🔍 深度分析：POST /order/change/ 接口的券绑定能力")
        print("=" * 80)
        
        # 找出所有的 order/change 请求
        order_change_requests = []
        for i, entry in enumerate(entries):
            if '/order/change/' in entry['request']['url'] and entry['request']['method'] == 'POST':
                order_change_requests.append((i+1, entry))
        
        print(f"📊 找到 {len(order_change_requests)} 个订单修改请求")
        print("=" * 80)
        
        # 详细分析每个请求
        for req_num, (index, entry) in enumerate(order_change_requests):
            print(f"\n🔗 请求 #{req_num+1} (HAR中第{index}个请求)")
            print(f"⏰ 时间: {entry['startedDateTime']}")
            
            # 解析请求参数
            request_data = decode_content(entry['request'].get('postData', {}))
            parsed_params = parse_form_data(request_data)
            
            print(f"📤 请求参数:")
            for key, value in parsed_params.items():
                print(f"   {key}: {value}")
            
            # 解析响应数据
            response_content = decode_content(entry['response'].get('content', {}))
            try:
                response_json = json.loads(response_content)
                print(f"📥 响应状态: ret={response_json.get('ret')}, msg={response_json.get('msg')}")
                
                # 重点分析价格相关字段
                data = response_json.get('data', {})
                price_fields = [
                    'order_total_price', 'order_payment_price', 'order_unfee_total_price',
                    'ticket_total_price', 'ticket_payment_total_price',
                    'voucher_discounts', 'voucher_use'
                ]
                
                print(f"💰 价格相关字段:")
                for field in price_fields:
                    if field in data:
                        print(f"   {field}: {data[field]}")
                
                # 检查券相关字段
                voucher_fields = ['voucher_use', 'voucher_discounts', 'voucher_use_goods']
                print(f"🎫 券相关字段:")
                for field in voucher_fields:
                    if field in data:
                        print(f"   {field}: {data[field]}")
                
            except json.JSONDecodeError:
                print(f"📥 响应解析失败: {response_content[:200]}...")
            
            print("-" * 60)
        
        # 特别分析券绑定前后的对比
        print("\n🎯 券绑定前后对比分析")
        print("=" * 80)
        
        if len(order_change_requests) >= 2:
            # 找到券绑定相关的请求
            voucher_requests = []
            for req_num, (index, entry) in enumerate(order_change_requests):
                request_data = decode_content(entry['request'].get('postData', {}))
                parsed_params = parse_form_data(request_data)
                
                if 'voucher_code' in parsed_params and parsed_params['voucher_code']:
                    voucher_requests.append((req_num+1, index, entry, parsed_params))
            
            if voucher_requests:
                print(f"📋 找到 {len(voucher_requests)} 个券绑定请求:")
                
                for req_num, index, entry, params in voucher_requests:
                    print(f"\n🎫 券绑定请求 #{req_num} (HAR第{index}个):")
                    print(f"   券码: {params.get('voucher_code', 'N/A')}")
                    print(f"   券类型: {params.get('voucher_code_type', 'N/A')}")
                    print(f"   折扣类型: {params.get('discount_type', 'N/A')}")
                    print(f"   支付方式: {params.get('pay_type', 'N/A')}")
                    
                    # 分析响应中的价格变化
                    response_content = decode_content(entry['response'].get('content', {}))
                    try:
                        response_json = json.loads(response_content)
                        data = response_json.get('data', {})
                        
                        print(f"   💰 价格结果:")
                        print(f"      订单总价: {data.get('order_total_price', 'N/A')}")
                        print(f"      支付金额: {data.get('order_payment_price', 'N/A')}")
                        print(f"      券折扣: {data.get('voucher_discounts', 'N/A')}")
                        print(f"      券使用: {data.get('voucher_use', 'N/A')}")
                        
                    except json.JSONDecodeError:
                        print(f"   ❌ 响应解析失败")
        
        return order_change_requests
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def analyze_voucher_price_requests():
    """分析券价格计算请求"""
    try:
        with open('沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        
        print("\n🧮 券价格计算接口分析")
        print("=" * 80)
        
        # 找出券价格计算请求
        voucher_price_requests = []
        for i, entry in enumerate(entries):
            if '/order/voucher/price/' in entry['request']['url'] and entry['request']['method'] == 'POST':
                voucher_price_requests.append((i+1, entry))
        
        if voucher_price_requests:
            print(f"📊 找到 {len(voucher_price_requests)} 个券价格计算请求")
            
            for index, entry in voucher_price_requests:
                print(f"\n🔗 券价格计算请求 (HAR第{index}个):")
                print(f"⏰ 时间: {entry['startedDateTime']}")
                
                # 解析请求参数
                request_data = decode_content(entry['request'].get('postData', {}))
                parsed_params = parse_form_data(request_data)
                
                print(f"📤 请求参数:")
                for key, value in parsed_params.items():
                    print(f"   {key}: {value}")
                
                # 解析响应
                response_content = decode_content(entry['response'].get('content', {}))
                try:
                    response_json = json.loads(response_content)
                    print(f"📥 响应状态: ret={response_json.get('ret')}, msg={response_json.get('msg')}")
                    
                    data = response_json.get('data', {})
                    print(f"💰 价格计算结果:")
                    print(f"   手续费: {data.get('surcharge_price', 'N/A')}")
                    print(f"   支付金额: {data.get('pay_price', 'N/A')}")
                    print(f"   手续费说明: {data.get('surcharge_msg', 'N/A')}")
                    
                except json.JSONDecodeError:
                    print(f"📥 响应解析失败: {response_content[:200]}...")
        else:
            print("📊 未找到独立的券价格计算请求")
            print("💡 这表明券价格计算可能已集成在订单修改接口中")
        
        return voucher_price_requests
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return []

def generate_optimization_conclusion(order_change_requests, voucher_price_requests):
    """生成优化结论"""
    print("\n🎯 流程优化可行性结论")
    print("=" * 80)
    
    # 分析是否存在独立的券价格计算
    has_separate_price_calc = len(voucher_price_requests) > 0
    
    # 分析订单修改接口是否包含价格计算
    has_integrated_price_calc = False
    voucher_binding_success = False
    
    for req_num, (index, entry) in enumerate(order_change_requests):
        request_data = decode_content(entry['request'].get('postData', {}))
        parsed_params = parse_form_data(request_data)
        
        if 'voucher_code' in parsed_params and parsed_params['voucher_code']:
            response_content = decode_content(entry['response'].get('content', {}))
            try:
                response_json = json.loads(response_content)
                if response_json.get('ret') == 0:
                    data = response_json.get('data', {})
                    if 'voucher_discounts' in data or 'voucher_use' in data:
                        has_integrated_price_calc = True
                        voucher_binding_success = True
                        break
            except:
                pass
    
    print(f"📊 分析结果:")
    print(f"   独立券价格计算接口: {'✅ 存在' if has_separate_price_calc else '❌ 不存在'}")
    print(f"   订单修改接口集成价格计算: {'✅ 是' if has_integrated_price_calc else '❌ 否'}")
    print(f"   券绑定成功案例: {'✅ 有' if voucher_binding_success else '❌ 无'}")
    
    print(f"\n💡 优化建议:")
    if has_integrated_price_calc and not has_separate_price_calc:
        print("   🎯 推荐使用单接口模式 (POST /order/change/)")
        print("   ✅ 优势: 减少网络请求，提高响应速度，简化错误处理")
        print("   ⚠️  注意: 需要完善错误信息处理，确保用户体验")
    elif has_separate_price_calc and has_integrated_price_calc:
        print("   🤔 两种模式都可行，建议根据用户体验需求选择")
        print("   📋 双接口模式: 可预先显示价格，用户确认后绑定")
        print("   🚀 单接口模式: 直接绑定，响应更快")
    else:
        print("   ❓ 需要进一步验证接口能力")

def main():
    """主函数"""
    print("🎬 沃美券使用流程深度分析")
    print("🎯 目标: 验证是否可以简化双接口调用模式")
    print("=" * 80)
    
    # 分析订单修改请求
    order_change_requests = analyze_order_change_requests()
    
    # 分析券价格计算请求
    voucher_price_requests = analyze_voucher_price_requests()
    
    # 生成优化结论
    generate_optimization_conclusion(order_change_requests, voucher_price_requests)
    
    print("\n" + "=" * 80)
    print("✅ 深度分析完成！")

if __name__ == "__main__":
    main()
