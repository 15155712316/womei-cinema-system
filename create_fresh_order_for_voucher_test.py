#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建新的有效订单来测试券绑定流程
"""

import sys
import os
import json
import requests
import urllib3
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

def get_current_movies(token):
    """获取当前上映的电影"""
    print("🎬 获取当前上映电影")
    print("-" * 60)
    
    headers = get_valid_headers(token)
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/film/list/"
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('ret') == 0 and result.get('sub') == 0:
                films = result.get('data', [])
                print(f"   找到 {len(films)} 部电影")
                
                if films:
                    # 选择第一部电影
                    film = films[0]
                    print(f"   选择电影: {film.get('film_name', 'N/A')}")
                    print(f"   电影ID: {film.get('film_id', 'N/A')}")
                    return film
                else:
                    print(f"   ❌ 没有找到电影")
                    return None
            else:
                print(f"   ❌ 获取电影失败: {result.get('msg', 'N/A')}")
                return None
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return None

def get_film_schedules(film_id, token):
    """获取电影场次"""
    print(f"📅 获取电影场次")
    print("-" * 60)
    
    headers = get_valid_headers(token)
    url = f"https://ct.womovie.cn/ticket/wmyc/cinema/400028/film/{film_id}/schedule/"
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('ret') == 0 and result.get('sub') == 0:
                schedules = result.get('data', [])
                print(f"   找到 {len(schedules)} 个场次")
                
                if schedules:
                    # 选择第一个场次
                    schedule = schedules[0]
                    print(f"   选择场次: {schedule.get('show_time', 'N/A')}")
                    print(f"   场次ID: {schedule.get('schedule_id', 'N/A')}")
                    print(f"   价格: {schedule.get('price', 'N/A')}")
                    return schedule
                else:
                    print(f"   ❌ 没有找到场次")
                    return None
            else:
                print(f"   ❌ 获取场次失败: {result.get('msg', 'N/A')}")
                return None
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return None

def get_available_seats(schedule_id, token):
    """获取可用座位"""
    print(f"💺 获取可用座位")
    print("-" * 60)
    
    headers = get_valid_headers(token)
    url = f"https://ct.womovie.cn/ticket/wmyc/cinema/400028/schedule/{schedule_id}/seat/"
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('ret') == 0 and result.get('sub') == 0:
                seat_data = result.get('data', {})
                seats = seat_data.get('seats', [])
                
                # 找到可用座位
                available_seats = []
                for seat in seats:
                    if seat.get('status') == 0:  # 0表示可用
                        available_seats.append(seat)
                        if len(available_seats) >= 2:  # 只需要2个座位
                            break
                
                print(f"   找到 {len(available_seats)} 个可用座位")
                
                if available_seats:
                    for i, seat in enumerate(available_seats):
                        print(f"   座位{i+1}: {seat.get('row', 'N/A')}排{seat.get('col', 'N/A')}座")
                    return available_seats
                else:
                    print(f"   ❌ 没有找到可用座位")
                    return None
            else:
                print(f"   ❌ 获取座位失败: {result.get('msg', 'N/A')}")
                return None
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return None

def create_order(schedule_id, seats, token):
    """创建订单"""
    print(f"📝 创建订单")
    print("-" * 60)
    
    headers = get_valid_headers(token)
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/create/"
    
    # 构建座位信息
    seat_info = []
    for seat in seats:
        seat_info.append({
            'seat_no': seat.get('seat_no', ''),
            'area_no': seat.get('area_no', ''),
            'row': seat.get('row', ''),
            'col': seat.get('col', ''),
            'price': seat.get('price', 0)
        })
    
    data = {
        'schedule_id': schedule_id,
        'seat_info': json.dumps(seat_info),
        'pay_type': 'WECHAT'
    }
    
    print(f"   参数: {data}")
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('ret') == 0 and result.get('sub') == 0:
                order_data = result.get('data', {})
                order_id = order_data.get('order_id', '')
                
                print(f"   ✅ 订单创建成功!")
                print(f"   订单号: {order_id}")
                print(f"   总价: {order_data.get('total_price', 'N/A')}")
                print(f"   支付价格: {order_data.get('payment_price', 'N/A')}")
                
                return order_id, order_data
            else:
                print(f"   ❌ 订单创建失败: {result.get('msg', 'N/A')}")
                return None, None
        else:
            print(f"   ❌ HTTP错误: {response.status_code}")
            return None, None
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return None, None

def test_voucher_with_new_order(order_id, voucher_code, token):
    """使用新订单测试券绑定"""
    print(f"\n🎫 使用新订单测试券绑定")
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
            print(f"   价格计算响应: ret={price_result.get('ret')}, sub={price_result.get('sub')}")
            print(f"   消息: {price_result.get('msg', 'N/A')}")
            
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
                    print(f"   券绑定响应: ret={bind_result.get('ret')}, sub={bind_result.get('sub')}")
                    print(f"   消息: {bind_result.get('msg', 'N/A')}")
                    
                    if bind_result.get('ret') == 0 and bind_result.get('sub') == 0:
                        print(f"   🎉 券绑定成功!")
                        
                        order_data = bind_result.get('data', {})
                        print(f"   最终支付金额: {order_data.get('order_payment_price', 'N/A')}")
                        
                        voucher_use = order_data.get('voucher_use', {})
                        if voucher_use:
                            print(f"   券使用信息: {voucher_use}")
                        
                        return True
                    else:
                        print(f"   ❌ 券绑定失败: {bind_result.get('msg', 'N/A')}")
                        if bind_result.get('sub') == 4004:
                            print(f"   🔍 仍然是sub=4004错误")
                        return False
                else:
                    print(f"   ❌ 券绑定HTTP错误: {bind_response.status_code}")
                    return False
            else:
                print(f"   ❌ 券价格计算失败: {price_result.get('msg', 'N/A')}")
                return False
        else:
            print(f"   ❌ 券价格计算HTTP错误: {price_response.status_code}")
            return False
    
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

def main():
    """主函数"""
    print("🎬 创建新订单并测试券绑定流程")
    print("🎯 使用有效订单验证券绑定功能")
    print("=" * 80)
    
    voucher_code = "GZJY01002948416827"
    
    # 加载token
    token, phone = load_token()
    if not token:
        print(f"❌ 未找到token")
        return
    
    print(f"📋 测试信息:")
    print(f"   账号: {phone}")
    print(f"   券码: {voucher_code}")
    
    # 1. 获取电影
    film = get_current_movies(token)
    if not film:
        print(f"❌ 无法获取电影信息")
        return
    
    # 2. 获取场次
    schedule = get_film_schedules(film.get('film_id'), token)
    if not schedule:
        print(f"❌ 无法获取场次信息")
        return
    
    # 3. 获取座位
    seats = get_available_seats(schedule.get('schedule_id'), token)
    if not seats:
        print(f"❌ 无法获取可用座位")
        return
    
    # 4. 创建订单
    order_id, order_data = create_order(schedule.get('schedule_id'), seats[:1], token)  # 只选1个座位
    if not order_id:
        print(f"❌ 订单创建失败")
        return
    
    # 5. 测试券绑定
    success = test_voucher_with_new_order(order_id, voucher_code, token)
    
    if success:
        print(f"\n🎉 完整的券绑定流程测试成功!")
        print(f"✅ 证明券码和技术实现都没有问题")
        print(f"✅ 之前的失败是因为订单过期")
    else:
        print(f"\n❌ 券绑定仍然失败")
        print(f"💡 可能是券码的业务规则限制")

if __name__ == "__main__":
    main()
