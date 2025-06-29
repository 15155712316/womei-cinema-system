#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试券绑定流程，不依赖订单查询
使用真实订单ID: 250629142310002208
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

def load_token():
    """加载token"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts:
            return accounts[0].get('token', ''), accounts[0].get('phone', '')
        
        return '', ''
    except Exception as e:
        print(f"❌ 加载token失败: {e}")
        return '', ''

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

def test_voucher_flow_all_cinemas(voucher_code, order_id, token):
    """在所有可能的影院测试券绑定流程"""
    print(f"🎫 测试券绑定流程 - 所有影院")
    print("=" * 80)
    
    # 可能的影院ID列表
    cinema_ids = ["400028", "400303", "400001", "400002"]
    
    headers = get_valid_headers(token)
    
    for cinema_id in cinema_ids:
        print(f"\n🏢 测试影院: {cinema_id}")
        print("-" * 60)
        
        # 第一步：券价格计算
        print(f"💰 第一步：券价格计算")
        price_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/"
        price_data = {
            'voucher_code': voucher_code,
            'order_id': order_id
        }
        
        try:
            price_response = requests.post(price_url, headers=headers, data=price_data, verify=False, timeout=15)
            
            if price_response.status_code == 200:
                price_result = price_response.json()
                price_ret = price_result.get('ret', -1)
                price_sub = price_result.get('sub', -1)
                price_msg = price_result.get('msg', '')
                
                print(f"   价格计算响应: ret={price_ret}, sub={price_sub}")
                print(f"   消息: {price_msg}")
                
                if price_ret == 0 and price_sub == 0:
                    print(f"   ✅ 券价格计算成功!")
                    
                    # 显示价格信息
                    price_data_field = price_result.get('data', {})
                    if price_data_field:
                        print(f"   价格信息: {price_data_field}")
                    
                    # 第二步：券绑定
                    print(f"\n🎫 第二步：券绑定")
                    bind_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
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
                        bind_ret = bind_result.get('ret', -1)
                        bind_sub = bind_result.get('sub', -1)
                        bind_msg = bind_result.get('msg', '')
                        
                        print(f"   券绑定响应: ret={bind_ret}, sub={bind_sub}")
                        print(f"   消息: {bind_msg}")
                        
                        if bind_ret == 0 and bind_sub == 0:
                            print(f"   🎉 券绑定成功!")
                            
                            # 显示订单信息
                            order_data = bind_result.get('data', {})
                            if order_data:
                                print(f"   订单信息:")
                                print(f"     order_payment_price: {order_data.get('order_payment_price', 'N/A')}")
                                print(f"     order_total_price: {order_data.get('order_total_price', 'N/A')}")
                                
                                voucher_use = order_data.get('voucher_use', {})
                                if voucher_use:
                                    print(f"   券使用信息: {voucher_use}")
                            
                            print(f"\n🎉 成功！在影院 {cinema_id} 完成券绑定")
                            return True, cinema_id, bind_result
                        else:
                            print(f"   ❌ 券绑定失败: {bind_msg}")
                            if bind_sub == 4004:
                                print(f"   🔍 sub=4004: 获取兑换券验券异常")
                            elif bind_sub == 1000:
                                print(f"   🔍 sub=1000: 参数错误")
                    else:
                        print(f"   ❌ 券绑定HTTP错误: {bind_response.status_code}")
                else:
                    print(f"   ❌ 券价格计算失败: {price_msg}")
                    if price_sub == 1000:
                        print(f"   🔍 sub=1000: 参数错误")
                    elif price_sub == 408:
                        print(f"   🔍 sub=408: TOKEN超时")
            else:
                print(f"   ❌ 券价格计算HTTP错误: {price_response.status_code}")
        
        except Exception as e:
            print(f"   ❌ 请求异常: {e}")
    
    return False, None, None

def test_voucher_availability(token):
    """测试券码可用性"""
    print(f"🎫 检查券码可用性")
    print("-" * 60)
    
    headers = get_valid_headers(token)
    
    # 尝试不同影院的券列表
    cinema_ids = ["400028", "400303"]
    
    for cinema_id in cinema_ids:
        print(f"   影院 {cinema_id}:")
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/"
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    data = result.get('data', {})
                    unused_vouchers = data.get('unused', [])
                    
                    print(f"     可用券数量: {len(unused_vouchers)}")
                    
                    # 查找目标券码
                    for voucher in unused_vouchers:
                        if voucher.get('voucher_code') == 'GZJY01002948416827':
                            print(f"     ✅ 找到目标券码: {voucher.get('voucher_name', 'N/A')}")
                            return True, cinema_id
                    
                    print(f"     ❌ 未找到目标券码")
                else:
                    print(f"     ❌ 券列表查询失败: {result.get('msg', 'N/A')}")
            else:
                print(f"     ❌ HTTP错误: {response.status_code}")
        
        except Exception as e:
            print(f"     ❌ 请求异常: {e}")
    
    return False, None

def main():
    """主函数"""
    print("🎬 直接测试券绑定流程")
    print("🎯 使用真实订单ID: 250629142310002208")
    print("⏰ 开始时间:", time.strftime("%H:%M:%S"))
    print("=" * 80)
    
    # 测试参数
    voucher_code = "GZJY01002948416827"
    order_id = "250629142310002208"
    
    # 加载token
    token, phone = load_token()
    if not token:
        print(f"❌ 未找到token")
        return
    
    print(f"📋 测试信息:")
    print(f"   账号: {phone}")
    print(f"   券码: {voucher_code}")
    print(f"   订单: {order_id}")
    
    # 1. 检查券码可用性
    voucher_available, voucher_cinema = test_voucher_availability(token)
    
    if voucher_available:
        print(f"\n✅ 券码在影院 {voucher_cinema} 可用")
    else:
        print(f"\n⚠️ 券码状态检查失败，继续测试")
    
    # 2. 测试券绑定流程
    success, cinema_id, result = test_voucher_flow_all_cinemas(voucher_code, order_id, token)
    
    # 3. 结果分析
    print(f"\n📊 最终测试结果")
    print("=" * 80)
    print(f"⏰ 完成时间:", time.strftime("%H:%M:%S"))
    
    if success:
        print(f"🎉 券绑定测试成功!")
        print(f"✅ 成功影院: {cinema_id}")
        print(f"✅ 证明:")
        print(f"   1. 券码 {voucher_code} 状态正常")
        print(f"   2. 订单 {order_id} 有效")
        print(f"   3. 两步流程工作正常")
        print(f"   4. 认证方式正确")
        
        print(f"\n💡 根本原因分析:")
        print(f"   之前的失败是因为:")
        print(f"   1. 使用了错误的认证方式 (Bearer vs token)")
        print(f"   2. 可能使用了错误的影院ID")
        print(f"   3. 订单状态问题")
        
        print(f"\n🔧 解决方案:")
        print(f"   1. 使用正确的认证header: 'token': {token[:20]}...")
        print(f"   2. 实施两步流程: 价格计算 → 券绑定")
        print(f"   3. 使用正确的影院ID: {cinema_id}")
    else:
        print(f"❌ 券绑定测试失败")
        print(f"🔍 所有影院都无法成功绑定券码")
        print(f"💡 可能原因:")
        print(f"   1. 订单已过期 (超过10分钟)")
        print(f"   2. 券码有特殊的使用限制")
        print(f"   3. 订单与券码不匹配")
        print(f"   4. 业务规则限制")
        
        print(f"\n⏰ 提醒:")
        print(f"   如果订单已过期，请提供新的订单ID")
        print(f"   订单有效期为10分钟")
    
    # 保存结果
    test_results = {
        "test_info": {
            "voucher_code": voucher_code,
            "order_id": order_id,
            "phone": phone,
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "voucher_available": voucher_available,
        "voucher_cinema": voucher_cinema,
        "binding_success": success,
        "success_cinema": cinema_id,
        "result": result
    }
    
    with open('direct_voucher_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📁 详细测试结果已保存到: direct_voucher_test_results.json")

if __name__ == "__main__":
    main()
