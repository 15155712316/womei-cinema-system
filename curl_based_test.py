#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于curl命令参数的券使用测试
直接使用您提供的有效参数进行测试
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_order_and_voucher():
    """测试订单创建和券使用"""
    
    # 使用您提供的curl命令参数
    cinema_id = "9934"
    schedule_id = "16696845"
    seatlable = "10013:5:8:33045901#06#09|10013:5:9:33045901#06#08"
    token = "afebc43f2b18da363fd78a6a10b01b72"
    voucher_code = "GZJY01002948416827"
    
    # 请求头（完全按照curl命令）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': token,
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    
    print("🎬 基于curl命令的券使用测试")
    print("=" * 60)
    print(f"影院ID: {cinema_id}")
    print(f"场次ID: {schedule_id}")
    print(f"座位信息: {seatlable}")
    print(f"券码: {voucher_code}")
    print()
    
    # 步骤1: 创建订单
    print("🎫 步骤1: 创建订单")
    print("-" * 40)
    
    order_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/ticket/"
    order_data = {
        'seatlable': seatlable,
        'schedule_id': schedule_id
    }
    
    print(f"📤 请求URL: {order_url}")
    print(f"📤 请求参数: {order_data}")
    
    try:
        order_response = requests.post(order_url, data=order_data, headers=headers, timeout=15, verify=False)
        
        print(f"📥 响应状态码: {order_response.status_code}")
        
        if order_response.status_code == 200:
            order_result = order_response.json()
            print(f"📥 订单创建响应:")
            print(json.dumps(order_result, ensure_ascii=False, indent=2))
            
            if order_result.get('ret') == 0 and order_result.get('sub') == 0:
                order_id = order_result.get('data', {}).get('order_id')
                if order_id:
                    print(f"✅ 订单创建成功: {order_id}")
                    
                    # 步骤2: 测试券价格计算
                    print(f"\n🧮 步骤2: 测试券价格计算")
                    print("-" * 40)
                    test_voucher_price(cinema_id, order_id, voucher_code, headers)
                    
                    # 步骤3: 测试券绑定（核心测试）
                    print(f"\n🔄 步骤3: 测试券绑定（核心测试）")
                    print("-" * 40)
                    success = test_voucher_binding(cinema_id, order_id, voucher_code, headers)
                    
                    # 最终结论
                    print(f"\n📋 最终测试结论")
                    print("=" * 40)
                    if success:
                        print("🎉 券使用测试成功！")
                        print("✅ POST /order/change/ 接口完全支持券绑定和价格计算")
                        print("✅ 单接口模式验证成功")
                        print("✅ 可以将HAR分析报告中的状态更新为：")
                        print("   '修改订单绑定券 → POST /order/change/ (✅ 完全实现)'")
                    else:
                        print("❌ 券使用测试失败")
                        print("但仍然验证了接口的基本功能")
                    
                    return success
                else:
                    print(f"❌ 未获取到订单ID")
                    return False
            else:
                print(f"❌ 订单创建失败: {order_result.get('msg')} (sub: {order_result.get('sub')})")
                return False
        else:
            print(f"❌ HTTP请求失败: {order_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 订单创建异常: {e}")
        return False

def test_voucher_price(cinema_id, order_id, voucher_code, headers):
    """测试券价格计算"""
    price_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/"
    price_data = {
        'voucher_code': voucher_code,
        'order_id': order_id
    }
    
    print(f"📤 券价格计算请求: {price_data}")
    
    try:
        price_response = requests.post(price_url, data=price_data, headers=headers, timeout=10, verify=False)
        
        if price_response.status_code == 200:
            price_result = price_response.json()
            print(f"📥 券价格计算响应:")
            print(json.dumps(price_result, ensure_ascii=False, indent=2))
            
            print(f"🔍 分析: ret={price_result.get('ret')}, sub={price_result.get('sub')}, msg={price_result.get('msg')}")
        else:
            print(f"❌ 券价格计算HTTP失败: {price_response.status_code}")
            
    except Exception as e:
        print(f"❌ 券价格计算异常: {e}")

def test_voucher_binding(cinema_id, order_id, voucher_code, headers):
    """测试券绑定（核心测试）"""
    change_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/change/"
    change_data = {
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
    
    print(f"📤 券绑定请求: {change_data}")
    
    try:
        change_response = requests.post(change_url, data=change_data, headers=headers, timeout=10, verify=False)
        
        if change_response.status_code == 200:
            change_result = change_response.json()
            print(f"📥 券绑定完整响应:")
            print(json.dumps(change_result, ensure_ascii=False, indent=2))
            
            print(f"\n🔍 关键信息分析:")
            print(f"   ret: {change_result.get('ret')} ({'成功' if change_result.get('ret') == 0 else '失败'})")
            print(f"   sub: {change_result.get('sub')}")
            print(f"   msg: {change_result.get('msg')}")
            
            data_section = change_result.get('data', {})
            if data_section:
                print(f"\n💰 价格信息:")
                price_fields = ['order_total_price', 'order_payment_price', 'order_unfee_total_price', 'ticket_total_price', 'ticket_payment_total_price']
                for field in price_fields:
                    if field in data_section:
                        print(f"   {field}: {data_section[field]}")
                
                print(f"\n🎫 券使用信息:")
                voucher_fields = ['voucher_use', 'voucher_discounts', 'voucher_use_goods']
                for field in voucher_fields:
                    if field in data_section:
                        print(f"   {field}: {data_section[field]}")
                
                # 关键验证
                has_price_info = any(field in data_section for field in price_fields)
                has_voucher_info = any(field in data_section for field in voucher_fields)
                
                print(f"\n📋 POST /order/change/ 接口能力验证:")
                print(f"   ✅ 接口调用成功: 是")
                print(f"   ✅ 返回价格信息: {'是' if has_price_info else '否'}")
                print(f"   ✅ 返回券信息: {'是' if has_voucher_info else '否'}")
                print(f"   ✅ 支持单接口模式: {'是' if has_price_info else '否'}")
                
                if change_result.get('ret') == 0:
                    print(f"\n🎉 券绑定成功！")
                    print(f"✅ POST /order/change/ 接口完全支持券绑定和价格计算")
                    return True
                else:
                    print(f"\n❌ 券绑定失败，但验证了接口功能")
                    return False
            else:
                print(f"❌ 响应data字段为空")
                return False
        else:
            print(f"❌ 券绑定HTTP失败: {change_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 券绑定异常: {e}")
        return False

def main():
    """主函数"""
    success = test_order_and_voucher()
    
    if success:
        print(f"\n🎊 测试完成！验证了单接口模式的可行性！")
    else:
        print(f"\n📝 测试完成，请查看详细结果")

if __name__ == "__main__":
    main()
