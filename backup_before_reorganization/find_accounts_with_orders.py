#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找有订单的账号
遍历所有影院和账号，找到有订单的账号用于测试
"""

import json
import os
from services.order_api import get_order_list
from services.cinema_manager import CinemaManager

def load_all_accounts():
    """加载所有账号"""
    try:
        accounts_file = os.path.join("data", "accounts.json")
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            print(f"📋 加载了 {len(accounts)} 个账号")
            return accounts
        else:
            print(f"❌ 账号文件不存在: {accounts_file}")
            return []
    except Exception as e:
        print(f"❌ 加载账号失败: {e}")
        return []

def load_all_cinemas():
    """加载所有影院"""
    try:
        cinema_manager = CinemaManager()
        cinemas = cinema_manager.load_cinema_list()
        print(f"🏛️ 加载了 {len(cinemas)} 个影院")
        return cinemas
    except Exception as e:
        print(f"❌ 加载影院失败: {e}")
        return []

def check_account_orders(account, cinema_id, cinema_name):
    """检查账号的订单"""
    try:
        print(f"  🔍 检查账号 {account.get('userid', 'N/A')} 在 {cinema_name} 的订单...")
        
        # 构建订单查询参数
        order_params = {
            'pageNo': '1',
            'groupid': '',
            'cinemaid': cinema_id,
            'cardno': account.get('cardno', ''),
            'userid': account.get('userid', ''),
            'openid': account.get('openid', ''),
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account.get('token', ''),
            'source': '2'
        }
        
        # 获取订单列表
        result = get_order_list(order_params)
        
        if result and result.get('resultCode') == '0':
            result_data = result.get('resultData', {})
            orders = result_data.get('orderList', [])
            
            if orders and len(orders) > 0:
                print(f"  ✅ 找到 {len(orders)} 个订单!")
                
                # 显示订单信息
                for i, order in enumerate(orders):
                    order_no = order.get('orderno', 'N/A')
                    order_name = order.get('orderName', 'N/A')
                    order_status = order.get('orderS', 'N/A')
                    
                    print(f"    📋 订单 {i+1}: {order_no}")
                    print(f"       影片: {order_name}")
                    print(f"       状态: {order_status}")
                
                return {
                    'account': account,
                    'cinema_id': cinema_id,
                    'cinema_name': cinema_name,
                    'orders': orders,
                    'order_count': len(orders)
                }
            else:
                print(f"  ⚪ 没有订单")
                return None
        else:
            error_msg = result.get('resultDesc', '获取失败') if result else '网络错误'
            print(f"  ❌ 获取订单失败: {error_msg}")
            return None
            
    except Exception as e:
        print(f"  ❌ 检查订单错误: {e}")
        return None

def find_accounts_with_orders():
    """查找有订单的账号"""
    print("=" * 80)
    print("🔍 查找有订单的账号")
    print("=" * 80)
    
    # 加载数据
    accounts = load_all_accounts()
    cinemas = load_all_cinemas()
    
    if not accounts:
        print("❌ 没有账号数据")
        return []
    
    if not cinemas:
        print("❌ 没有影院数据")
        return []
    
    # 创建影院映射
    cinema_map = {}
    for cinema in cinemas:
        cinema_id = cinema.get('cinemaid', '')
        cinema_name = cinema.get('cinemaShortName', '未知影院')
        if cinema_id:
            cinema_map[cinema_id] = cinema_name
    
    print(f"📊 影院映射: {len(cinema_map)} 个影院")
    for cid, cname in cinema_map.items():
        print(f"  {cid}: {cname}")
    print()
    
    # 查找有订单的账号
    accounts_with_orders = []
    
    for account in accounts:
        account_userid = account.get('userid', 'N/A')
        account_cinemaid = account.get('cinemaid', '')
        
        print(f"👤 检查账号: {account_userid}")
        
        if account_cinemaid in cinema_map:
            cinema_name = cinema_map[account_cinemaid]
            print(f"  🏛️ 影院: {cinema_name} ({account_cinemaid})")
            
            # 检查这个账号的订单
            result = check_account_orders(account, account_cinemaid, cinema_name)
            
            if result:
                accounts_with_orders.append(result)
                print(f"  🎉 账号 {account_userid} 有 {result['order_count']} 个订单!")
            else:
                print(f"  ⚪ 账号 {account_userid} 没有订单")
        else:
            print(f"  ❌ 影院ID {account_cinemaid} 不在影院列表中")
        
        print("-" * 60)
    
    return accounts_with_orders

def test_qrcode_with_real_orders(accounts_with_orders):
    """使用真实订单测试二维码功能"""
    if not accounts_with_orders:
        print("❌ 没有找到有订单的账号")
        return
    
    print("\n" + "=" * 80)
    print("🧪 使用真实订单测试二维码功能")
    print("=" * 80)
    
    # 选择第一个有订单的账号
    test_data = accounts_with_orders[0]
    account = test_data['account']
    cinema_id = test_data['cinema_id']
    cinema_name = test_data['cinema_name']
    orders = test_data['orders']
    
    print(f"🎯 选择测试账号:")
    print(f"   账号: {account.get('userid', 'N/A')}")
    print(f"   影院: {cinema_name} ({cinema_id})")
    print(f"   订单数: {len(orders)}")
    print()
    
    # 选择第一个订单进行测试
    if orders:
        test_order = orders[0]
        order_no = test_order.get('orderno', '')
        order_name = test_order.get('orderName', '')
        order_status = test_order.get('orderS', '')
        
        print(f"🎬 选择测试订单:")
        print(f"   订单号: {order_no}")
        print(f"   影片: {order_name}")
        print(f"   状态: {order_status}")
        print()
        
        # 检查状态是否允许查看二维码
        allowed_statuses = ['已完成', '待使用', '已支付', '已付款', '已取票']
        can_view_qr = any(status in order_status for status in allowed_statuses)
        
        print(f"🔍 二维码查看权限检查:")
        print(f"   订单状态: '{order_status}'")
        print(f"   允许的状态: {allowed_statuses}")
        print(f"   可以查看二维码: {'✅' if can_view_qr else '❌'}")
        
        if can_view_qr:
            print(f"\n🎉 这个订单可以用来测试二维码功能!")
            print(f"💡 请在主程序中:")
            print(f"   1. 选择影院: {cinema_name}")
            print(f"   2. 选择账号: {account.get('userid', 'N/A')}")
            print(f"   3. 切换到订单Tab")
            print(f"   4. 双击订单: {order_no}")
        else:
            print(f"\n⚠️ 这个订单状态不允许查看二维码")
            print(f"💡 可能需要修改状态检查逻辑")
        
        return {
            'account': account,
            'cinema_id': cinema_id,
            'cinema_name': cinema_name,
            'order': test_order,
            'can_view_qr': can_view_qr
        }
    
    return None

if __name__ == "__main__":
    print("🔍 查找有订单的账号工具启动")
    
    # 查找有订单的账号
    accounts_with_orders = find_accounts_with_orders()
    
    print("\n" + "=" * 80)
    print("📊 查找结果总结")
    print("=" * 80)
    
    if accounts_with_orders:
        print(f"✅ 找到 {len(accounts_with_orders)} 个有订单的账号:")
        
        for i, data in enumerate(accounts_with_orders):
            account = data['account']
            cinema_name = data['cinema_name']
            order_count = data['order_count']
            
            print(f"  {i+1}. 账号 {account.get('userid', 'N/A')} @ {cinema_name} ({order_count} 个订单)")
        
        # 测试二维码功能
        test_result = test_qrcode_with_real_orders(accounts_with_orders)
        
        if test_result and test_result['can_view_qr']:
            print(f"\n🎉 找到可用于测试的订单!")
        else:
            print(f"\n⚠️ 找到的订单可能不适合测试二维码功能")
    else:
        print("❌ 没有找到有订单的账号")
        print("💡 可能的原因:")
        print("   1. 所有账号都没有订单")
        print("   2. 账号认证信息过期")
        print("   3. API接口有问题")
    
    print("=" * 80)
