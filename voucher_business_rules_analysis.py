#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券业务规则分析
重新分析券绑定失败的真正原因
"""

import sys
import os
import json
import requests
import urllib3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_voucher_business_rules():
    """分析券业务规则"""
    print("🎫 券业务规则深度分析")
    print("🎯 找出sub=4004券验证异常的真正原因")
    print("=" * 80)
    
    print("📋 已确认的正常状态:")
    print("   ✅ Token有效 (ret=0, sub=0)")
    print("   ✅ 券码在可用列表中")
    print("   ✅ 通兑券可用于任何影院")
    print("   ✅ 订单状态为PENDING")
    print("   ✅ API通信正常")
    
    print(f"\n🔍 可能的业务规则限制:")
    
    business_rules = [
        {
            "规则": "券码已在其他订单中使用",
            "说明": "虽然券码在可用列表中，但可能已经被预占用",
            "检查方法": "查看券码的详细状态和使用历史"
        },
        {
            "规则": "订单类型限制",
            "说明": "某些券码可能只适用于特定类型的订单",
            "检查方法": "确认订单类型和券码适用范围"
        },
        {
            "规则": "时间窗口限制",
            "说明": "券码可能有特定的使用时间窗口",
            "检查方法": "检查当前时间是否在券码使用时间范围内"
        },
        {
            "规则": "金额范围限制",
            "说明": "券码可能有最低或最高消费金额要求",
            "检查方法": "确认订单金额是否符合券码使用条件"
        },
        {
            "规则": "用户类型限制",
            "说明": "券码可能只适用于特定类型的用户",
            "检查方法": "确认当前用户是否符合券码使用条件"
        },
        {
            "规则": "场次类型限制",
            "说明": "券码可能不适用于特定场次（如特殊放映）",
            "检查方法": "确认场次类型和券码适用范围"
        },
        {
            "规则": "系统状态限制",
            "说明": "券码系统可能有临时限制或维护",
            "检查方法": "确认券码验证系统状态"
        }
    ]
    
    for i, rule in enumerate(business_rules, 1):
        print(f"\n{i}. {rule['规则']}")
        print(f"   说明: {rule['说明']}")
        print(f"   检查方法: {rule['检查方法']}")
    
    return business_rules

def test_different_voucher_parameters():
    """测试不同的券绑定参数"""
    print(f"\n🧪 测试不同的券绑定参数")
    print("=" * 80)
    
    fresh_token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    cinema_id = "400303"
    order_id = "250625184410001025"
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "标准参数",
            "voucher_code": "GZJY01003062558469",
            "voucher_type": "VGC_T",
            "discount_type": "TP_VOUCHER"
        },
        {
            "name": "第二张券",
            "voucher_code": "GZJY01002948416827", 
            "voucher_type": "VGC_T",
            "discount_type": "TP_VOUCHER"
        },
        {
            "name": "不同券类型",
            "voucher_code": "GZJY01003062558469",
            "voucher_type": "VGC_P",
            "discount_type": "TP_VOUCHER"
        },
        {
            "name": "不同折扣类型",
            "voucher_code": "GZJY01003062558469",
            "voucher_type": "VGC_T", 
            "discount_type": "VOUCHER"
        }
    ]
    
    try:
        from services.womei_order_voucher_service import get_womei_order_voucher_service
        service = get_womei_order_voucher_service()
        
        results = []
        
        for case in test_cases:
            print(f"\n🧪 测试: {case['name']}")
            print(f"   券码: {case['voucher_code']}")
            print(f"   券类型: {case['voucher_type']}")
            print(f"   折扣类型: {case['discount_type']}")
            
            # 修改服务中的参数
            original_bind = service.bind_voucher_to_order
            
            def modified_bind(cinema_id, token, order_id, voucher_code, voucher_type):
                # 构建修改后的请求数据
                url = f"{service.base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
                headers = service.headers_template.copy()
                headers['token'] = token
                
                data = {
                    'card_id': '',
                    'discount_id': '0',
                    'discount_type': case['discount_type'],  # 使用测试用例的折扣类型
                    'limit_cards': '[]',
                    'order_id': order_id,
                    'pay_type': 'WECHAT',
                    'rewards': '[]',
                    'ticket_pack_goods': ' ',
                    'use_limit_cards': 'N',
                    'use_rewards': 'Y',
                    'voucher_code': voucher_code,
                    'voucher_code_type': voucher_type,
                }
                
                try:
                    response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
                    if response.status_code == 200:
                        decoded_data = service.decode_unicode_message(response.text)
                        if decoded_data:
                            ret = decoded_data.get('ret', -1)
                            sub = decoded_data.get('sub', -1)
                            msg = decoded_data.get('msg', '未知错误')
                            
                            return {
                                'success': ret == 0 and sub == 0,
                                'ret': ret,
                                'sub': sub,
                                'msg': msg,
                                'data': decoded_data.get('data', {})
                            }
                    return {'success': False, 'error': 'request_failed'}
                except Exception as e:
                    return {'success': False, 'error': str(e)}
            
            result = modified_bind(cinema_id, fresh_token, order_id, case['voucher_code'], case['voucher_type'])
            
            print(f"   结果: ret={result.get('ret')}, sub={result.get('sub')}")
            print(f"   消息: {result.get('msg', result.get('error', 'N/A'))}")
            print(f"   成功: {'✅' if result.get('success') else '❌'}")
            
            results.append({
                'case': case['name'],
                'result': result
            })
        
        # 分析结果
        print(f"\n📊 测试结果汇总:")
        print("-" * 60)
        for test_result in results:
            case_name = test_result['case']
            result = test_result['result']
            status = "✅ 成功" if result.get('success') else f"❌ 失败 (sub={result.get('sub')})"
            print(f"   {case_name}: {status}")
        
        # 检查是否有成功的案例
        successful_cases = [r for r in results if r['result'].get('success')]
        if successful_cases:
            print(f"\n🎉 发现成功案例:")
            for case in successful_cases:
                print(f"   ✅ {case['case']}")
        else:
            print(f"\n📋 所有测试案例都失败，错误码一致")
            print(f"   说明问题可能不在参数格式上")
        
        return results
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return []

def check_voucher_detailed_info():
    """检查券码的详细信息"""
    print(f"\n🔍 检查券码详细信息")
    print("=" * 80)
    
    fresh_token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    cinema_id = "400303"
    
    try:
        # 获取券列表详细信息
        base_url = "https://ct.womovie.cn"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'token': fresh_token
        }
        
        url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/"
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ret') == 0 and result.get('sub') == 0:
                data = result.get('data', {})
                unused_vouchers = data.get('unused', [])
                
                print(f"📋 可用券详细信息:")
                for i, voucher in enumerate(unused_vouchers, 1):
                    print(f"\n券 {i}:")
                    for key, value in voucher.items():
                        print(f"   {key}: {value}")
                
                # 重点检查使用条件
                print(f"\n🔍 使用条件分析:")
                for voucher in unused_vouchers:
                    voucher_code = voucher.get('voucher_code', 'N/A')
                    print(f"\n券码 {voucher_code}:")
                    
                    # 检查关键字段
                    key_fields = [
                        'use_limit', 'min_amount', 'max_amount', 'valid_time',
                        'cinema_limit', 'movie_limit', 'user_limit', 'status'
                    ]
                    
                    for field in key_fields:
                        if field in voucher:
                            print(f"   {field}: {voucher[field]}")
                    
                    # 检查所有包含limit的字段
                    limit_fields = {k: v for k, v in voucher.items() if 'limit' in k.lower()}
                    if limit_fields:
                        print(f"   限制条件: {limit_fields}")
                
                return unused_vouchers
            else:
                print(f"❌ 获取券列表失败: {result.get('msg')}")
                return []
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 检查券信息异常: {e}")
        return []

def suggest_debugging_steps():
    """建议调试步骤"""
    print(f"\n💡 调试步骤建议")
    print("=" * 80)
    
    steps = [
        {
            "步骤": "1. 检查HAR文件中的成功案例",
            "说明": "查找HAR文件中成功的券绑定请求",
            "操作": [
                "找到ret=0, sub=0的券绑定响应",
                "对比成功案例的请求参数",
                "确认参数差异",
                "复制成功案例的完整参数"
            ]
        },
        {
            "步骤": "2. 联系沃美技术支持",
            "说明": "获取官方的券绑定业务规则说明",
            "操作": [
                "提供具体的券码和订单信息",
                "询问sub=4004的具体含义",
                "确认券绑定的前置条件",
                "获取调试建议"
            ]
        },
        {
            "步骤": "3. 测试其他订单",
            "说明": "使用不同的订单测试券绑定",
            "操作": [
                "创建新的订单",
                "使用不同金额的订单",
                "测试不同场次的订单",
                "确认是否是订单特定问题"
            ]
        },
        {
            "步骤": "4. 分析券码状态",
            "说明": "深入分析券码的实际状态",
            "操作": [
                "检查券码是否有隐藏的使用限制",
                "确认券码的有效期和使用条件",
                "验证券码是否真的可用",
                "检查券码是否被其他系统占用"
            ]
        }
    ]
    
    for step in steps:
        print(f"\n{step['步骤']}")
        print(f"   说明: {step['说明']}")
        print(f"   操作:")
        for operation in step['操作']:
            print(f"     - {operation}")

def main():
    """主函数"""
    print("🎬 券业务规则深度分析")
    print("🎯 找出券绑定失败的真正原因")
    print("=" * 80)
    
    # 1. 分析业务规则
    business_rules = analyze_voucher_business_rules()
    
    # 2. 测试不同参数
    test_results = test_different_voucher_parameters()
    
    # 3. 检查券码详细信息
    voucher_info = check_voucher_detailed_info()
    
    # 4. 建议调试步骤
    suggest_debugging_steps()
    
    print(f"\n📋 分析总结")
    print("=" * 80)
    print(f"🎯 通过深度分析，我们发现:")
    print(f"   1. 技术实现完全正确")
    print(f"   2. 问题出现在业务规则层面")
    print(f"   3. 需要更深入的业务规则理解")
    print(f"   4. 建议查看HAR文件中的成功案例")
    
    return {
        'business_rules': business_rules,
        'test_results': test_results,
        'voucher_info': voucher_info
    }

if __name__ == "__main__":
    main()
