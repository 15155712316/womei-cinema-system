#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析券绑定失败原因
对比成功和失败案例的参数差异
"""

import sys
import os
import json
import requests
import urllib3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_unicode_decode():
    """测试Unicode解码修复"""
    print("🔧 测试Unicode解码修复")
    print("=" * 80)
    
    # 测试原始的Unicode编码消息
    test_message = "\\u83b7\\u53d6\\u5151\\u6362\\u5238\\u9a8c\\u5238\\u5f02\\u5e38\\uff0c\\u8bf7\\u8054\\u7cfb\\u5f71\\u9662"
    
    print(f"原始消息: {test_message}")
    
    try:
        # 使用修复后的解码逻辑
        import codecs
        decoded = codecs.decode(test_message, 'unicode_escape')
        print(f"解码后消息: {decoded}")
        
        # 测试完整的JSON响应
        test_response = {
            "ret": 0,
            "sub": 4004,
            "msg": test_message,
            "data": {}
        }
        
        from services.womei_order_voucher_service import get_womei_order_voucher_service
        service = get_womei_order_voucher_service()
        
        decoded_response = service.decode_unicode_message(json.dumps(test_response))
        print(f"解码后响应: {json.dumps(decoded_response, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unicode解码测试失败: {e}")
        return False

def analyze_parameter_differences():
    """分析参数差异"""
    print(f"\n🔍 分析参数差异")
    print("=" * 80)
    
    # 成功案例的参数（基于之前的测试）
    success_case = {
        "cinema_id": "400303",
        "order_id": "250625184410001025",
        "voucher_code": "GZJY01003062558469",
        "parameters": {
            "card_id": "",
            "discount_id": "0",
            "discount_type": "TP_VOUCHER",
            "limit_cards": "[]",
            "order_id": "250625184410001025",
            "pay_type": "WECHAT",
            "rewards": "[]",
            "ticket_pack_goods": " ",
            "use_limit_cards": "N",
            "use_rewards": "Y",
            "voucher_code": "GZJY01003062558469",
            "voucher_code_type": "VGC_T"
        },
        "result": "完全成功，order_payment_price=0"
    }
    
    # 失败案例的参数（当前日志）
    failure_case = {
        "cinema_id": "400028",
        "order_id": "250625204310001280",
        "voucher_code": "GZJY01002948416827",
        "parameters": {
            "card_id": "",
            "discount_id": "0",
            "discount_type": "TP_VOUCHER",
            "limit_cards": "[]",
            "order_id": "250625204310001280",
            "pay_type": "WECHAT",
            "rewards": "[]",
            "ticket_pack_goods": " ",
            "use_limit_cards": "N",
            "use_rewards": "Y",
            "voucher_code": "GZJY01002948416827",
            "voucher_code_type": "VGC_T"
        },
        "result": "失败，sub=4004，获取兑换券验券异常"
    }
    
    print("📊 参数对比分析:")
    print(f"{'参数':<20} {'成功案例':<25} {'失败案例':<25} {'差异':<10}")
    print("-" * 90)
    
    # 对比基础信息
    basic_fields = ['cinema_id', 'order_id', 'voucher_code']
    for field in basic_fields:
        success_val = success_case[field]
        failure_val = failure_case[field]
        diff = "❌ 不同" if success_val != failure_val else "✅ 相同"
        print(f"{field:<20} {success_val:<25} {failure_val:<25} {diff:<10}")
    
    print()
    
    # 对比请求参数
    print("📋 请求参数对比:")
    for key in success_case['parameters']:
        success_val = success_case['parameters'][key]
        failure_val = failure_case['parameters'][key]
        diff = "❌ 不同" if success_val != failure_val else "✅ 相同"
        print(f"{key:<20} {success_val:<25} {failure_val:<25} {diff:<10}")
    
    print(f"\n🎯 关键差异分析:")
    
    # 分析影院差异
    print(f"1. 影院差异:")
    print(f"   成功案例: 400303 (沃美影城宁波北仑印象里店)")
    print(f"   失败案例: 400028 (北京沃美世界城店)")
    print(f"   影响: 不同影院可能有不同的券使用规则")
    
    # 分析券码差异
    print(f"\n2. 券码差异:")
    print(f"   成功案例: GZJY01003062558469")
    print(f"   失败案例: GZJY01002948416827")
    print(f"   影响: 不同券码可能有不同的使用限制")
    
    # 分析订单差异
    print(f"\n3. 订单差异:")
    print(f"   成功案例: 250625184410001025")
    print(f"   失败案例: 250625204310001280")
    print(f"   影响: 不同订单可能有不同的状态和金额")
    
    return success_case, failure_case

def test_voucher_availability():
    """测试券码可用性"""
    print(f"\n🎫 测试券码可用性")
    print("=" * 80)
    
    cinema_id = "400028"
    token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    voucher_code = "GZJY01002948416827"
    
    try:
        # 获取券列表
        base_url = "https://ct.womovie.cn"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'token': token
        }
        
        url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/"
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ret') == 0 and result.get('sub') == 0:
                data = result.get('data', {})
                unused_vouchers = data.get('unused', [])
                used_vouchers = data.get('used', [])
                
                print(f"📊 券列表信息:")
                print(f"   可用券数量: {len(unused_vouchers)}")
                print(f"   已用券数量: {len(used_vouchers)}")
                
                # 检查目标券码
                target_voucher = None
                voucher_status = "未找到"
                
                for voucher in unused_vouchers:
                    if voucher.get('voucher_code') == voucher_code:
                        target_voucher = voucher
                        voucher_status = "可用"
                        break
                
                if not target_voucher:
                    for voucher in used_vouchers:
                        if voucher.get('voucher_code') == voucher_code:
                            target_voucher = voucher
                            voucher_status = "已使用"
                            break
                
                print(f"\n🔍 目标券码状态:")
                print(f"   券码: {voucher_code}")
                print(f"   状态: {voucher_status}")
                
                if target_voucher:
                    print(f"   券名称: {target_voucher.get('voucher_name', 'N/A')}")
                    print(f"   过期时间: {target_voucher.get('expire_time_string', 'N/A')}")
                    print(f"   券类型: {target_voucher.get('voucher_type', 'N/A')}")
                    
                    # 检查使用限制
                    if 'use_limit' in target_voucher:
                        print(f"   使用限制: {target_voucher['use_limit']}")
                    
                    return voucher_status == "可用", target_voucher
                else:
                    print(f"   ❌ 券码不在用户券列表中")
                    return False, None
            else:
                print(f"❌ 获取券列表失败: {result.get('msg')}")
                return False, None
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ 券码可用性测试异常: {e}")
        return False, None

def test_order_status():
    """测试订单状态"""
    print(f"\n📋 测试订单状态")
    print("=" * 80)
    
    cinema_id = "400028"
    token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    order_id = "250625204310001280"
    
    try:
        base_url = "https://ct.womovie.cn"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'token': token
        }
        
        url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/order/info/?version=tp_version&order_id={order_id}"
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ret') == 0 and result.get('sub') == 0:
                order_data = result.get('data', {})
                
                print(f"📊 订单信息:")
                print(f"   订单ID: {order_data.get('order_id', 'N/A')}")
                print(f"   订单状态: {order_data.get('status', 'N/A')}")
                print(f"   订单总价: {order_data.get('order_total_price', 'N/A')}")
                print(f"   支付金额: {order_data.get('order_payment_price', 'N/A')}")
                print(f"   电影名称: {order_data.get('movie_name', 'N/A')}")
                print(f"   影院名称: {order_data.get('cinema_name', 'N/A')}")
                
                # 检查订单是否已经使用了券
                voucher_fields = {}
                for key, value in order_data.items():
                    if 'voucher' in key.lower() or 'coupon' in key.lower():
                        voucher_fields[key] = value
                
                if voucher_fields:
                    print(f"\n🎫 订单中的券信息:")
                    for field, value in voucher_fields.items():
                        print(f"   {field}: {value}")
                else:
                    print(f"\n📋 订单中无券信息")
                
                return True, order_data
            else:
                print(f"❌ 获取订单信息失败: {result.get('msg')}")
                return False, None
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ 订单状态测试异常: {e}")
        return False, None

def suggest_solutions():
    """建议解决方案"""
    print(f"\n💡 解决方案建议")
    print("=" * 80)
    
    solutions = [
        {
            "问题": "券码已被使用",
            "解决方案": [
                "使用其他未使用的券码进行测试",
                "确认券码的使用状态",
                "检查券码是否有重复使用限制"
            ]
        },
        {
            "问题": "券码不适用于当前影院",
            "解决方案": [
                "确认券码是否为通兑券",
                "检查券码的影院使用限制",
                "尝试在原始影院（400303）进行测试"
            ]
        },
        {
            "问题": "订单状态不支持券绑定",
            "解决方案": [
                "确认订单状态为PENDING",
                "检查订单是否已经绑定了其他券",
                "确认订单金额是否符合券使用条件"
            ]
        },
        {
            "问题": "券码有特殊使用限制",
            "解决方案": [
                "检查券码的详细使用条件",
                "确认当前时间是否在券码有效期内",
                "检查券码是否有最低消费要求"
            ]
        }
    ]
    
    for solution in solutions:
        print(f"\n📋 {solution['问题']}:")
        for step in solution['解决方案']:
            print(f"   - {step}")

def main():
    """主函数"""
    print("🎬 券绑定失败原因分析")
    print("🎯 分析sub=4004错误和参数差异")
    print("=" * 80)
    
    # 1. 测试Unicode解码修复
    unicode_success = test_unicode_decode()
    
    # 2. 分析参数差异
    success_case, failure_case = analyze_parameter_differences()
    
    # 3. 测试券码可用性
    voucher_available, voucher_info = test_voucher_availability()
    
    # 4. 测试订单状态
    order_valid, order_info = test_order_status()
    
    # 5. 建议解决方案
    suggest_solutions()
    
    print(f"\n📋 分析总结")
    print("=" * 80)
    
    print(f"🔧 Unicode解码: {'✅ 已修复' if unicode_success else '❌ 仍有问题'}")
    print(f"🎫 券码可用性: {'✅ 可用' if voucher_available else '❌ 不可用'}")
    print(f"📋 订单状态: {'✅ 正常' if order_valid else '❌ 异常'}")
    
    print(f"\n🎯 可能的失败原因:")
    if not voucher_available:
        print(f"   1. 券码已被使用或不在可用列表中")
    if not order_valid:
        print(f"   2. 订单状态异常或不支持券绑定")
    
    print(f"   3. 影院差异：不同影院可能有不同的券使用规则")
    print(f"   4. 券码限制：券码可能有特定的使用条件")
    
    return {
        'unicode_fixed': unicode_success,
        'voucher_available': voucher_available,
        'order_valid': order_valid,
        'voucher_info': voucher_info,
        'order_info': order_info
    }

if __name__ == "__main__":
    main()
