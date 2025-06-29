#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件成功案例分析
查找实际的券绑定成功案例，对比参数差异
"""

import sys
import os
import json
import requests
import urllib3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_parameter_variations():
    """测试不同的参数组合"""
    print("🧪 测试不同的参数组合")
    print("🎯 找出能让券抵扣生效的正确参数")
    print("=" * 80)
    
    fresh_token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    cinema_id = "400303"
    order_id = "250625184410001025"
    voucher_code = "GZJY01003062558469"
    
    base_url = "https://ct.womovie.cn"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'token': fresh_token,
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    
    # 测试不同的参数组合
    test_cases = [
        {
            "name": "当前参数（基准）",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'VOUCHER',
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'Y',
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_T',
            }
        },
        {
            "name": "修改券类型为VGC_P",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'VOUCHER',
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'Y',
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_P',  # 修改
            }
        },
        {
            "name": "关闭rewards使用",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'VOUCHER',
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'N',  # 修改
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_T',
            }
        },
        {
            "name": "移除支付类型",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'VOUCHER',
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': '',  # 修改
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'Y',
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_T',
            }
        },
        {
            "name": "修改discount_type为TP_VOUCHER",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'TP_VOUCHER',  # 修改回原值测试
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'Y',
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_T',
            }
        },
        {
            "name": "组合优化（VGC_P + 无rewards + 无pay_type）",
            "data": {
                'card_id': '',
                'discount_id': '0',
                'discount_type': 'VOUCHER',
                'limit_cards': '[]',
                'order_id': order_id,
                'pay_type': '',  # 修改
                'rewards': '[]',
                'ticket_pack_goods': ' ',
                'use_limit_cards': 'N',
                'use_rewards': 'N',  # 修改
                'voucher_code': voucher_code,
                'voucher_code_type': 'VGC_P',  # 修改
            }
        }
    ]
    
    results = []
    url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 测试 {i}: {case['name']}")
        print("-" * 60)
        
        # 显示关键参数差异
        if i > 1:
            base_data = test_cases[0]['data']
            current_data = case['data']
            print("📋 参数差异:")
            for key in current_data:
                if current_data[key] != base_data[key]:
                    print(f"   {key}: '{base_data[key]}' → '{current_data[key]}'")
        
        try:
            response = requests.post(url, headers=headers, data=case['data'], verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ret = result.get('ret', -1)
                sub = result.get('sub', -1)
                msg = result.get('msg', '')
                
                print(f"📥 响应: ret={ret}, sub={sub}, msg={msg}")
                
                if ret == 0 and sub == 0:
                    data = result.get('data', {})
                    order_total = data.get('order_total_price', 0)
                    order_payment = data.get('order_payment_price', 0)
                    voucher_use = data.get('voucher_use', {})
                    voucher_discounts = data.get('voucher_discounts', [])
                    
                    print(f"💰 价格: 总价={order_total}, 支付={order_payment}")
                    print(f"🎫 券使用: {len(str(voucher_use))}字符")
                    print(f"🎫 券抵扣: {len(voucher_discounts)}项")
                    
                    # 检查是否有抵扣效果
                    has_discount = order_payment < order_total
                    has_voucher_info = bool(voucher_use) or bool(voucher_discounts)
                    
                    if has_discount:
                        print(f"✅ 发现抵扣效果！支付金额减少了{order_total - order_payment}元")
                    else:
                        print(f"❌ 无抵扣效果，支付金额未变化")
                    
                    if has_voucher_info:
                        print(f"✅ 发现券使用信息")
                    else:
                        print(f"❌ 券使用信息仍为空")
                    
                    results.append({
                        'case': case['name'],
                        'success': True,
                        'has_discount': has_discount,
                        'has_voucher_info': has_voucher_info,
                        'order_total': order_total,
                        'order_payment': order_payment,
                        'voucher_use': voucher_use,
                        'voucher_discounts': voucher_discounts,
                        'data': case['data']
                    })
                else:
                    print(f"❌ API调用失败")
                    results.append({
                        'case': case['name'],
                        'success': False,
                        'ret': ret,
                        'sub': sub,
                        'msg': msg
                    })
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                results.append({
                    'case': case['name'],
                    'success': False,
                    'http_error': response.status_code
                })
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            results.append({
                'case': case['name'],
                'success': False,
                'exception': str(e)
            })
    
    return results

def analyze_test_results(results):
    """分析测试结果"""
    print(f"\n📊 测试结果分析")
    print("=" * 80)
    
    print("📋 测试结果汇总:")
    print(f"{'测试案例':<25} {'API成功':<8} {'有抵扣':<8} {'有券信息':<10} {'支付金额':<10}")
    print("-" * 80)
    
    successful_cases = []
    discount_cases = []
    
    for result in results:
        if result.get('success'):
            api_status = "✅"
            discount_status = "✅" if result.get('has_discount') else "❌"
            voucher_status = "✅" if result.get('has_voucher_info') else "❌"
            payment = f"{result.get('order_payment', 'N/A')}"
            
            if result.get('has_discount'):
                discount_cases.append(result)
            
            successful_cases.append(result)
        else:
            api_status = "❌"
            discount_status = "N/A"
            voucher_status = "N/A"
            payment = "N/A"
        
        print(f"{result['case']:<25} {api_status:<8} {discount_status:<8} {voucher_status:<10} {payment:<10}")
    
    print(f"\n🎯 关键发现:")
    
    if discount_cases:
        print(f"✅ 发现{len(discount_cases)}个有抵扣效果的案例:")
        for case in discount_cases:
            savings = case.get('order_total', 0) - case.get('order_payment', 0)
            print(f"   - {case['case']}: 节省{savings}元")
            
            # 显示成功案例的关键参数
            print(f"     关键参数:")
            key_params = ['discount_type', 'voucher_code_type', 'use_rewards', 'pay_type']
            for param in key_params:
                value = case['data'].get(param, 'N/A')
                print(f"       {param}: {value}")
    else:
        print(f"❌ 所有测试案例都没有抵扣效果")
        print(f"   可能原因:")
        print(f"   1. 参数组合仍不正确")
        print(f"   2. 券码需要特殊的激活步骤")
        print(f"   3. 订单状态不支持券抵扣")
        print(f"   4. 需要调用其他API接口")
    
    if successful_cases:
        print(f"\n📋 所有成功案例的共同特征:")
        common_features = {}
        for case in successful_cases:
            for key, value in case['data'].items():
                if key not in common_features:
                    common_features[key] = set()
                common_features[key].add(str(value))
        
        for key, values in common_features.items():
            if len(values) == 1:
                print(f"   {key}: {list(values)[0]} (一致)")
            else:
                print(f"   {key}: {', '.join(values)} (不一致)")
    
    return discount_cases

def suggest_next_steps(discount_cases):
    """建议下一步操作"""
    print(f"\n💡 下一步操作建议")
    print("=" * 80)
    
    if discount_cases:
        print(f"🎉 找到了有抵扣效果的参数组合！")
        best_case = discount_cases[0]
        
        print(f"\n🔧 建议使用的参数:")
        for key, value in best_case['data'].items():
            print(f"   {key}: {value}")
        
        print(f"\n🚀 下一步行动:")
        print(f"   1. 更新券绑定服务使用成功的参数组合")
        print(f"   2. 测试修改后的券绑定功能")
        print(f"   3. 验证UI中的券抵扣显示")
        print(f"   4. 进行完整的端到端测试")
    else:
        print(f"🔍 需要进一步调试:")
        print(f"   1. 检查HAR文件中的实际成功案例")
        print(f"   2. 确认券码的具体使用条件")
        print(f"   3. 可能需要先调用券价格计算API")
        print(f"   4. 联系沃美技术支持获取帮助")
        
        print(f"\n📋 可能的原因:")
        print(f"   1. 券码需要特定的激活流程")
        print(f"   2. 订单状态不支持券抵扣")
        print(f"   3. 券码有使用限制条件")
        print(f"   4. 需要调用额外的API接口")

def main():
    """主函数"""
    print("🎬 HAR文件成功案例分析")
    print("🎯 通过参数测试找出券抵扣生效的正确方法")
    print("=" * 80)
    
    # 1. 测试不同参数组合
    results = test_parameter_variations()
    
    # 2. 分析测试结果
    discount_cases = analyze_test_results(results)
    
    # 3. 建议下一步操作
    suggest_next_steps(discount_cases)
    
    print(f"\n📋 分析完成")
    print("=" * 80)
    print(f"🎯 通过系统性的参数测试，我们应该能够:")
    print(f"   1. 找出让券抵扣生效的正确参数")
    print(f"   2. 理解券绑定的完整业务逻辑")
    print(f"   3. 修复券抵扣功能")
    print(f"   4. 提供完整的券使用体验")
    
    return {
        'results': results,
        'discount_cases': discount_cases
    }

if __name__ == "__main__":
    main()
