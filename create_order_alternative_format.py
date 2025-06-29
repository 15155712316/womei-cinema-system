#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试不同的订单创建参数格式
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

def try_different_order_formats(token):
    """尝试不同的订单创建格式"""
    print("📝 尝试不同的订单创建格式")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    
    # 不同的API端点和参数格式
    order_variants = [
        {
            "name": "原始格式",
            "url": "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/ticket/",
            "data": {
                'schedule_id': '16626092',
                'seat_info': '10013:7:3:11051771#02#05|10013:7:4:11051771#02#04'
            }
        },
        {
            "name": "标准创建格式",
            "url": "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/create/",
            "data": {
                'schedule_id': '16626092',
                'seat_info': json.dumps([
                    {
                        'seat_no': '10013',
                        'area_no': '7',
                        'row': '3',
                        'col': '11051771#02#05'
                    },
                    {
                        'seat_no': '10013',
                        'area_no': '7',
                        'row': '4',
                        'col': '11051771#02#04'
                    }
                ])
            }
        },
        {
            "name": "简化格式",
            "url": "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/create/",
            "data": {
                'schedule_id': '16626092',
                'seat_info': json.dumps([
                    {'row': '7', 'col': '3'},
                    {'row': '7', 'col': '4'}
                ])
            }
        },
        {
            "name": "字符串格式",
            "url": "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/create/",
            "data": {
                'schedule_id': '16626092',
                'seats': '10013:7:3:11051771#02#05|10013:7:4:11051771#02#04'
            }
        }
    ]
    
    for i, variant in enumerate(order_variants, 1):
        print(f"\n📋 尝试格式 {i}: {variant['name']}")
        print(f"   URL: {variant['url']}")
        print(f"   参数: {variant['data']}")
        
        try:
            response = requests.post(variant['url'], headers=headers, data=variant['data'], verify=False, timeout=30)
            
            print(f"   HTTP状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ret = result.get('ret', -1)
                sub = result.get('sub', -1)
                msg = result.get('msg', '')
                
                print(f"   响应: ret={ret}, sub={sub}, msg={msg}")
                
                if ret == 0 and sub == 0:
                    order_data = result.get('data', {})
                    order_id = order_data.get('order_id', '')
                    
                    print(f"   ✅ 订单创建成功!")
                    print(f"   订单号: {order_id}")
                    print(f"   完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                    
                    return order_id, order_data, variant
                else:
                    print(f"   ❌ 失败: {msg}")
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}...")
        
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    return None, None, None

def test_voucher_with_created_order(order_id, voucher_code, token):
    """使用创建的订单测试券绑定"""
    print(f"\n🎫 使用订单 {order_id} 测试券绑定")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    
    # 第一步：券价格计算
    print(f"💰 第一步：券价格计算")
    price_url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/voucher/price/"
    price_data = {
        'voucher_code': voucher_code,
        'order_id': order_id
    }
    
    try:
        price_response = requests.post(price_url, headers=headers, data=price_data, verify=False, timeout=15)
        
        if price_response.status_code == 200:
            price_result = price_response.json()
            print(f"   价格计算响应: {json.dumps(price_result, indent=2, ensure_ascii=False)}")
            
            if price_result.get('ret') == 0 and price_result.get('sub') == 0:
                print(f"   ✅ 券价格计算成功!")
                
                # 第二步：券绑定
                print(f"\n🎫 第二步：券绑定")
                bind_url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/change/?version=tp_version"
                bind_data = {
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
                
                bind_response = requests.post(bind_url, headers=headers, data=bind_data, verify=False, timeout=30)
                
                if bind_response.status_code == 200:
                    bind_result = bind_response.json()
                    print(f"   券绑定响应: {json.dumps(bind_result, indent=2, ensure_ascii=False)}")
                    
                    if bind_result.get('ret') == 0 and bind_result.get('sub') == 0:
                        print(f"   🎉 券绑定成功!")
                        
                        order_data = bind_result.get('data', {})
                        voucher_use = order_data.get('voucher_use', {})
                        
                        print(f"   最终支付金额: {order_data.get('order_payment_price', 'N/A')}")
                        if voucher_use:
                            print(f"   券使用信息: {voucher_use}")
                        
                        return True, bind_result
                    else:
                        print(f"   ❌ 券绑定失败: {bind_result.get('msg', 'N/A')}")
                        if bind_result.get('sub') == 4004:
                            print(f"   🔍 sub=4004: 获取兑换券验券异常")
                        return False, bind_result
                else:
                    print(f"   ❌ 券绑定HTTP错误: {bind_response.status_code}")
                    return False, None
            else:
                print(f"   ❌ 券价格计算失败: {price_result.get('msg', 'N/A')}")
                return False, price_result
        else:
            print(f"   ❌ 券价格计算HTTP错误: {price_response.status_code}")
            return False, None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False, None

def main():
    """主函数"""
    print("🎬 尝试不同格式创建订单并测试券绑定")
    print("⏰ 开始时间:", time.strftime("%H:%M:%S"))
    print("=" * 80)
    
    token = "bd871543a2419bb6c61ba1868ba5bf1d"
    voucher_code = "GZJY01002948416827"
    
    print(f"📋 测试参数:")
    print(f"   Token: {token[:20]}...")
    print(f"   券码: {voucher_code}")
    
    # 1. 尝试不同格式创建订单
    order_id, order_data, successful_variant = try_different_order_formats(token)
    
    if order_id:
        print(f"\n✅ 订单创建成功!")
        print(f"   订单号: {order_id}")
        print(f"   成功格式: {successful_variant['name']}")
        print(f"⏰ 订单创建时间:", time.strftime("%H:%M:%S"))
        
        # 2. 立即测试券绑定
        success, result = test_voucher_with_created_order(order_id, voucher_code, token)
        
        print(f"\n📊 最终结果")
        print("=" * 80)
        print(f"⏰ 完成时间:", time.strftime("%H:%M:%S"))
        
        if success:
            print(f"🎉 完整流程成功!")
            print(f"✅ 订单创建: 成功 (格式: {successful_variant['name']})")
            print(f"✅ 券价格计算: 成功")
            print(f"✅ 券绑定: 成功")
            print(f"✅ 根本原因已解决!")
        else:
            print(f"❌ 券绑定失败")
            print(f"✅ 订单创建: 成功")
            print(f"❌ 券绑定: 失败")
            
            if result and result.get('sub') == 4004:
                print(f"🔍 仍然是sub=4004错误，说明券码确实有问题")
    else:
        print(f"\n❌ 所有格式的订单创建都失败")
        print(f"💡 可能原因:")
        print(f"   1. 场次ID过期或无效")
        print(f"   2. 座位参数格式错误")
        print(f"   3. Token权限不足")
        print(f"   4. 座位已被占用")

if __name__ == "__main__":
    main()
