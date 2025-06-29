#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细订单信息分析
打印订单的所有字段，分析真实的价格信息
"""

import sys
import os
import json
import requests
import urllib3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_detailed_order_info():
    """获取详细的订单信息"""
    print("📋 详细订单信息分析")
    print("=" * 80)
    
    fresh_token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    cinema_id = "400303"
    order_id = "250625184410001025"
    
    base_url = "https://ct.womovie.cn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'token': fresh_token
    }
    
    print(f"📋 查询参数:")
    print(f"   Token: {fresh_token}")
    print(f"   影院ID: {cinema_id}")
    print(f"   订单ID: {order_id}")
    
    try:
        url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/order/info/?version=tp_version&order_id={order_id}"
        print(f"\n📡 请求URL: {url}")
        
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        print(f"📥 HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 API响应: ret={result.get('ret')}, sub={result.get('sub')}")
            print(f"💬 消息: {result.get('msg')}")
            
            if result.get('ret') == 0 and result.get('sub') == 0:
                order_data = result.get('data', {})
                
                print(f"\n📋 订单完整信息:")
                print("=" * 60)
                
                # 打印所有字段
                for key, value in order_data.items():
                    if isinstance(value, (dict, list)):
                        print(f"   {key}: {json.dumps(value, ensure_ascii=False, indent=6)}")
                    else:
                        print(f"   {key}: {value}")
                
                # 重点分析价格相关字段
                print(f"\n💰 价格字段详细分析:")
                print("=" * 60)
                
                price_fields = [
                    'order_total_price', 'order_payment_price', 'ticket_total_price',
                    'ticket_payment_total_price', 'total_price', 'payment_price',
                    'price', 'amount', 'cost', 'fee', 'money'
                ]
                
                found_price_fields = {}
                for field in price_fields:
                    if field in order_data:
                        found_price_fields[field] = order_data[field]
                        print(f"   ✅ {field}: {order_data[field]}")
                
                # 查找所有包含price的字段
                print(f"\n🔍 所有包含'price'的字段:")
                for key, value in order_data.items():
                    if 'price' in key.lower():
                        print(f"   {key}: {value}")
                
                # 查找所有数字字段
                print(f"\n🔢 所有数字类型字段:")
                for key, value in order_data.items():
                    if isinstance(value, (int, float)) and value != 0:
                        print(f"   {key}: {value}")
                
                # 分析订单状态
                print(f"\n📊 订单状态分析:")
                status = order_data.get('status', 'N/A')
                print(f"   订单状态: {status}")
                
                # 分析电影和场次信息
                print(f"\n🎬 电影和场次信息:")
                movie_fields = ['movie_name', 'movie_id', 'show_date', 'show_time', 'hall_name', 'seat_info']
                for field in movie_fields:
                    if field in order_data:
                        print(f"   {field}: {order_data[field]}")
                
                return order_data
            else:
                print(f"❌ 获取订单信息失败: {result.get('msg')}")
                return None
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_price_discrepancy(order_data):
    """分析价格显示差异的原因"""
    print(f"\n🔍 价格显示差异分析")
    print("=" * 80)
    
    if not order_data:
        print(f"❌ 没有订单数据可分析")
        return
    
    print(f"📋 可能的原因分析:")
    
    # 检查字段类型
    price_fields = {}
    for key, value in order_data.items():
        if 'price' in key.lower() or 'amount' in key.lower() or 'total' in key.lower():
            price_fields[key] = {
                'value': value,
                'type': type(value).__name__,
                'is_zero': value == 0 if isinstance(value, (int, float)) else False
            }
    
    print(f"\n💰 价格字段详情:")
    for field, info in price_fields.items():
        print(f"   {field}:")
        print(f"     值: {info['value']}")
        print(f"     类型: {info['type']}")
        print(f"     是否为0: {info['is_zero']}")
    
    # 分析可能的原因
    print(f"\n🎯 可能的原因:")
    
    zero_price_fields = [field for field, info in price_fields.items() if info['is_zero']]
    if zero_price_fields:
        print(f"   1. 字段确实为0: {', '.join(zero_price_fields)}")
        print(f"      可能原因:")
        print(f"        - 订单是测试订单")
        print(f"        - 订单已经使用了券或优惠")
        print(f"        - 订单状态特殊")
    
    non_zero_fields = [field for field, info in price_fields.items() if not info['is_zero'] and isinstance(info['value'], (int, float))]
    if non_zero_fields:
        print(f"   2. 非零价格字段: {', '.join(non_zero_fields)}")
        print(f"      说明订单确实有价格")
    
    # 检查是否有隐藏的价格字段
    print(f"\n🔍 检查其他可能的价格字段:")
    potential_price_fields = []
    for key, value in order_data.items():
        if isinstance(value, (int, float)) and value > 0:
            potential_price_fields.append((key, value))
    
    if potential_price_fields:
        print(f"   发现非零数值字段:")
        for field, value in potential_price_fields:
            print(f"     {field}: {value}")
    else:
        print(f"   ❌ 没有发现非零数值字段")

def test_voucher_with_detailed_analysis():
    """结合详细订单分析测试券绑定"""
    print(f"\n🧪 结合详细分析测试券绑定")
    print("=" * 80)
    
    # 先获取详细订单信息
    order_data = get_detailed_order_info()
    
    if order_data:
        # 分析价格差异
        analyze_price_discrepancy(order_data)
        
        # 基于真实订单数据重新测试券绑定
        print(f"\n🎫 基于真实订单数据测试券绑定:")
        
        fresh_token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
        cinema_id = "400303"
        order_id = "250625184410001025"
        voucher_code = "GZJY01003062558469"
        
        try:
            from services.womei_order_voucher_service import get_womei_order_voucher_service
            service = get_womei_order_voucher_service()
            
            print(f"🚀 重新测试券绑定...")
            result = service.bind_voucher_to_order(
                cinema_id=cinema_id,
                token=fresh_token,
                order_id=order_id,
                voucher_code=voucher_code,
                voucher_type='VGC_T'
            )
            
            print(f"\n📥 券绑定结果:")
            print(f"   成功状态: {result.get('success')}")
            print(f"   返回码: ret={result.get('ret')}, sub={result.get('sub')}")
            print(f"   消息: {result.get('msg')}")
            
            # 如果仍然失败，分析具体原因
            if not result.get('success'):
                print(f"\n🔍 失败原因深度分析:")
                
                ret = result.get('ret', -1)
                sub = result.get('sub', -1)
                
                if ret == 0 and sub == 4004:
                    print(f"   错误类型: 券验证异常")
                    print(f"   可能原因:")
                    print(f"     1. 券码使用条件不满足")
                    print(f"     2. 券码与订单类型不匹配")
                    print(f"     3. 券码有特定的使用限制")
                    print(f"     4. 订单已经绑定过其他券")
                    print(f"     5. 券码需要特定的订单金额范围")
                    
                    # 检查订单是否已经有券信息
                    if 'voucher' in str(order_data).lower() or 'coupon' in str(order_data).lower():
                        print(f"   ⚠️ 订单可能已经包含券信息")
                        
                        # 查找券相关字段
                        voucher_fields = {}
                        for key, value in order_data.items():
                            if 'voucher' in key.lower() or 'coupon' in key.lower():
                                voucher_fields[key] = value
                        
                        if voucher_fields:
                            print(f"   🎫 发现券相关字段:")
                            for field, value in voucher_fields.items():
                                print(f"     {field}: {value}")
            
            return result
            
        except Exception as e:
            print(f"❌ 券绑定测试异常: {e}")
            return None
    
    return None

def main():
    """主函数"""
    print("🎬 详细订单信息分析")
    print("🎯 查找订单真实价格信息，分析券绑定失败的真正原因")
    print("=" * 80)
    
    # 运行详细分析
    result = test_voucher_with_detailed_analysis()
    
    print(f"\n📋 分析总结")
    print("=" * 80)
    print(f"🎯 通过详细的订单信息分析，我们应该能够:")
    print(f"   1. 确认订单的真实价格信息")
    print(f"   2. 理解为什么之前显示价格为0")
    print(f"   3. 找到券绑定失败的真正原因")
    print(f"   4. 确定是否需要调整券绑定逻辑")
    
    return result

if __name__ == "__main__":
    main()
