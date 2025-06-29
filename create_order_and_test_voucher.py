#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新订单并立即测试券绑定流程
使用指定的沃美影城系统参数
"""

import sys
import os
import json
import requests
import urllib3
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_valid_headers(token):
    """获取有效的请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'token': token,
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }

def create_new_order(token):
    """创建新订单"""
    print("📝 创建新订单")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/ticket/"
    
    # 使用指定的参数
    data = {
        'schedule_id': '16626092',
        'seat_info': '10013:7:3:11051771#02#05|10013:7:4:11051771#02#04'
    }
    
    print(f"📤 订单创建请求:")
    print(f"   URL: {url}")
    print(f"   参数: {data}")
    print(f"   认证: token header")
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        print(f"\n📥 订单创建响应:")
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            ret = result.get('ret', -1)
            sub = result.get('sub', -1)
            msg = result.get('msg', '')
            
            print(f"\n   关键字段:")
            print(f"     ret: {ret}")
            print(f"     sub: {sub}")
            print(f"     msg: {msg}")
            
            if ret == 0 and sub == 0:
                order_data = result.get('data', {})
                order_id = order_data.get('order_id', '')
                
                print(f"   ✅ 订单创建成功!")
                print(f"   📋 订单信息:")
                print(f"     订单号: {order_id}")
                print(f"     总价: {order_data.get('total_price', 'N/A')}")
                print(f"     支付价格: {order_data.get('payment_price', 'N/A')}")
                print(f"     座位数: {order_data.get('seat_count', 'N/A')}")
                
                return order_id, order_data
            else:
                print(f"   ❌ 订单创建失败: {msg}")
                return None, None
        else:
            print(f"   ❌ HTTP请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return None, None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_voucher_price_calculation(voucher_code, order_id, token):
    """第一步：券价格计算"""
    print(f"\n💰 第一步：券价格计算")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/voucher/price/"
    
    data = {
        'voucher_code': voucher_code,
        'order_id': order_id
    }
    
    print(f"📤 券价格计算请求:")
    print(f"   URL: {url}")
    print(f"   参数: {data}")
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        print(f"\n📥 券价格计算响应:")
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            ret = result.get('ret', -1)
            sub = result.get('sub', -1)
            msg = result.get('msg', '')
            
            print(f"\n   关键字段:")
            print(f"     ret: {ret}")
            print(f"     sub: {sub}")
            print(f"     msg: {msg}")
            
            if ret == 0 and sub == 0:
                print(f"   ✅ 券价格计算成功!")
                
                price_data = result.get('data', {})
                if price_data:
                    print(f"   💰 价格信息:")
                    for key, value in price_data.items():
                        print(f"     {key}: {value}")
                
                return True, result
            else:
                print(f"   ❌ 券价格计算失败: {msg}")
                if sub == 1000:
                    print(f"   🔍 sub=1000: 参数错误")
                elif sub == 408:
                    print(f"   🔍 sub=408: TOKEN超时")
                elif sub == 4004:
                    print(f"   🔍 sub=4004: 券验证异常")
                return False, result
        else:
            print(f"   ❌ HTTP请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False, {"error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False, {"error": str(e)}

def test_voucher_binding(voucher_code, order_id, token):
    """第二步：券绑定"""
    print(f"\n🎫 第二步：券绑定")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/change/?version=tp_version"
    
    # 按照HAR文件中成功案例的参数
    data = {
        'order_id': order_id,
        'discount_id': '0',
        'discount_type': 'TP_VOUCHER',
        'card_id': '',
        'pay_type': 'WECHAT',
        'rewards': '[]',
        'use_rewards': 'Y',
        'use_limit_cards': 'N',
        'limit_cards': '[]',
        'voucher_code': voucher_code,
        'voucher_code_type': 'VGC_T',
        'ticket_pack_goods': ' '
    }
    
    print(f"📤 券绑定请求:")
    print(f"   URL: {url}")
    print(f"   参数: {data}")
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        print(f"\n📥 券绑定响应:")
        print(f"   HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            ret = result.get('ret', -1)
            sub = result.get('sub', -1)
            msg = result.get('msg', '')
            
            print(f"\n   关键字段:")
            print(f"     ret: {ret}")
            print(f"     sub: {sub}")
            print(f"     msg: {msg}")
            
            if ret == 0 and sub == 0:
                print(f"   ✅ 券绑定成功!")
                
                order_data = result.get('data', {})
                if order_data:
                    print(f"   💳 订单信息:")
                    important_fields = ['order_id', 'order_total_price', 'order_payment_price', 'order_unfee_total_price']
                    for field in important_fields:
                        if field in order_data:
                            print(f"     {field}: {order_data[field]}")
                    
                    voucher_use = order_data.get('voucher_use', {})
                    if voucher_use:
                        print(f"   🎫 券使用信息:")
                        for key, value in voucher_use.items():
                            print(f"     {key}: {value}")
                    
                    voucher_discounts = order_data.get('voucher_discounts', [])
                    if voucher_discounts:
                        print(f"   💰 券折扣信息: {len(voucher_discounts)} 项")
                        for i, discount in enumerate(voucher_discounts):
                            print(f"     [{i}] {discount}")
                
                return True, result
            else:
                print(f"   ❌ 券绑定失败: {msg}")
                if sub == 4004:
                    print(f"   🔍 sub=4004: 获取兑换券验券异常，请联系影院")
                elif sub == 1000:
                    print(f"   🔍 sub=1000: 参数错误")
                elif sub == 408:
                    print(f"   🔍 sub=408: TOKEN超时")
                return False, result
        else:
            print(f"   ❌ HTTP请求失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False, {"error": f"HTTP {response.status_code}"}
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False, {"error": str(e)}

def main():
    """主函数"""
    print("🎬 创建订单并测试券绑定流程")
    print("🎯 使用指定的沃美影城系统参数")
    print("⏰ 开始时间:", time.strftime("%H:%M:%S"))
    print("=" * 80)
    
    # 测试参数
    token = "bd871543a2419bb6c61ba1868ba5bf1d"
    voucher_code = "GZJY01002948416827"
    cinema_id = "400028"
    schedule_id = "16626092"
    
    print(f"📋 测试参数:")
    print(f"   影院ID: {cinema_id} (北京沃美世界城店)")
    print(f"   场次ID: {schedule_id}")
    print(f"   券码: {voucher_code}")
    print(f"   Token: {token[:20]}...")
    print(f"   座位: 10013:7:3:11051771#02#05|10013:7:4:11051771#02#04 (2个座位)")
    
    # 第一步：创建订单
    order_id, order_data = create_new_order(token)
    
    if not order_id:
        print(f"\n❌ 订单创建失败，无法继续测试")
        return
    
    print(f"\n✅ 订单创建成功，订单号: {order_id}")
    print(f"⏰ 订单创建时间:", time.strftime("%H:%M:%S"))
    print(f"⚠️ 订单有效期: 10分钟")
    
    # 第二步：立即测试券价格计算
    price_success, price_result = test_voucher_price_calculation(voucher_code, order_id, token)
    
    # 第三步：如果价格计算成功，进行券绑定
    if price_success:
        print(f"\n✅ 第一步成功，立即进行第二步")
        
        bind_success, bind_result = test_voucher_binding(voucher_code, order_id, token)
        
        # 最终结果分析
        print(f"\n📊 最终测试结果")
        print("=" * 80)
        print(f"⏰ 完成时间:", time.strftime("%H:%M:%S"))
        
        if bind_success:
            print(f"🎉 完整的券绑定流程测试成功!")
            print(f"✅ 验证结果:")
            print(f"   1. ✅ 订单创建成功 (订单号: {order_id})")
            print(f"   2. ✅ 券价格计算成功")
            print(f"   3. ✅ 券绑定成功")
            print(f"   4. ✅ 认证方式正确 (token header)")
            print(f"   5. ✅ 两步流程有效")
            
            print(f"\n🎯 根本原因确认:")
            print(f"   之前的失败确实是因为:")
            print(f"   1. 错误的认证方式 (Bearer token → token header)")
            print(f"   2. 缺少券价格计算前置步骤")
            print(f"   3. 可能使用了过期的订单")
            
            print(f"\n💡 解决方案验证成功:")
            print(f"   1. 使用正确的认证header格式")
            print(f"   2. 实施两步流程: 价格计算 → 券绑定")
            print(f"   3. 使用有效的订单")
            
            # 显示券使用详情
            bind_data = bind_result.get('data', {})
            if bind_data:
                voucher_use = bind_data.get('voucher_use', {})
                if voucher_use:
                    print(f"\n🎫 券使用详情:")
                    print(f"   使用券码: {voucher_use.get('use_codes', [])}")
                    print(f"   抵扣金额: {voucher_use.get('use_total_price', 0)}")
                    print(f"   最终支付: {bind_data.get('order_payment_price', 'N/A')}")
        else:
            print(f"❌ 券绑定失败")
            print(f"🔍 失败分析:")
            
            bind_sub = bind_result.get('sub', -1) if bind_result else -1
            bind_msg = bind_result.get('msg', '') if bind_result else ''
            
            if bind_sub == 4004:
                print(f"   仍然是sub=4004错误: {bind_msg}")
                print(f"   说明即使使用正确的流程，券码仍有问题")
                print(f"   可能原因:")
                print(f"   1. 券码有特殊的使用限制")
                print(f"   2. 券码与当前订单类型不匹配")
                print(f"   3. 券码的适用范围限制")
            else:
                print(f"   其他错误: sub={bind_sub}, msg={bind_msg}")
    else:
        print(f"\n❌ 第一步失败，无法继续")
        print(f"🔍 失败分析:")
        
        price_sub = price_result.get('sub', -1) if price_result else -1
        price_msg = price_result.get('msg', '') if price_result else ''
        
        print(f"   券价格计算失败: sub={price_sub}, msg={price_msg}")
        
        if price_sub == 1000:
            print(f"   参数错误，可能是订单或券码格式问题")
        elif price_sub == 408:
            print(f"   TOKEN超时，认证问题")
        elif price_sub == 4004:
            print(f"   券验证异常，券码问题")
    
    # 保存测试结果
    test_results = {
        "test_info": {
            "voucher_code": voucher_code,
            "order_id": order_id,
            "cinema_id": cinema_id,
            "schedule_id": schedule_id,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "order_creation": {
            "success": order_id is not None,
            "order_data": order_data
        },
        "step1_price_calculation": {
            "success": price_success,
            "result": price_result
        }
    }
    
    if price_success:
        test_results["step2_voucher_binding"] = {
            "success": bind_success,
            "result": bind_result
        }
    
    with open('complete_voucher_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细测试结果已保存到: complete_voucher_test_results.json")

if __name__ == "__main__":
    main()
