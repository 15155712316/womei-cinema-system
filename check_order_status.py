#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查订单状态
"""

from services.order_api import get_order_list
from services.cinema_manager import CinemaManager

def get_hongwan_cinema_info():
    """获取虹湾影城信息"""
    try:
        cinema_manager = CinemaManager()
        cinemas = cinema_manager.load_cinema_list()

        for cinema in cinemas:
            cinema_name = cinema.get('cinemaShortName', '')
            if '虹湾' in cinema_name:
                cinema_id = cinema.get('cinemaid', '')
                print(f"🏛️ 找到虹湾影城: {cinema_name} (ID: {cinema_id})")
                return cinema_id, cinema_name

        print(f"❌ 未找到虹湾影城")
        return None, None

    except Exception as e:
        print(f"❌ 获取虹湾影城信息错误: {e}")
        return None, None

def get_account_info(cinema_id, userid):
    """获取账号信息"""
    try:
        # 从账号文件中读取
        import json
        import os

        accounts_file = os.path.join("data", "accounts.json")
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)

            # 查找指定影院和用户ID的账号
            for account in accounts_data:
                if (account.get('cinemaid') == cinema_id and
                    account.get('userid') == userid):
                    print(f"✅ 找到账号信息: {userid}")
                    return account

        print(f"❌ 未找到账号信息: {userid}")
        return None

    except Exception as e:
        print(f"❌ 获取账号信息错误: {e}")
        return None

def check_order_status():
    """检查订单状态"""
    print("=" * 80)
    print("🔍 检查订单状态")
    print("=" * 80)
    
    # 🎯 获取虹湾影城信息
    print("🏛️ 获取虹湾影城信息...")
    cinema_id, cinema_name = get_hongwan_cinema_info()

    if not cinema_id:
        print("❌ 无法获取虹湾影城信息")
        return

    # 🎯 获取账号信息
    print(f"👤 获取账号信息: 15155712316...")
    account_info = get_account_info(cinema_id, "15155712316")

    if not account_info:
        print("❌ 无法获取账号信息")
        return

    # 🎯 虹湾影城账号认证信息
    test_account = {
        "userid": account_info.get('userid', '15155712316'),
        "openid": account_info.get('openid', ''),
        "token": account_info.get('token', ''),
        "cinemaid": cinema_id
    }

    test_cinema_id = cinema_id
    
    print(f"📋 使用账号: {test_account['userid']}")
    print(f"📋 影院ID: {test_cinema_id}")
    print()
    
    # 🎯 获取订单列表
    print("📋 获取订单列表...")
    order_params = {
        'pageNo': '1',
        'groupid': '',
        'cinemaid': test_cinema_id,
        'cardno': test_account.get('cardno', ''),
        'userid': test_account['userid'],
        'openid': test_account['openid'],
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': test_account['token'],
        'source': '2'
    }
    
    order_result = get_order_list(order_params)
    
    if order_result and order_result.get('resultCode') == '0':
        print("✅ 订单列表获取成功!")
        
        order_data = order_result.get('resultData', {})
        orders = order_data.get('orderList', [])
        
        print(f"📊 找到 {len(orders)} 个订单")
        print()
        
        # 🎯 分析每个订单的状态
        allowed_statuses = ['已完成', '待使用', '已支付', '已付款', '已取票']
        
        for i, order in enumerate(orders):
            order_no = order.get('orderno', '')
            order_name = order.get('orderName', '')
            order_status = order.get('orderS', '')
            
            print(f"📋 订单 {i+1}:")
            print(f"   订单号: {order_no}")
            print(f"   影片: {order_name}")
            print(f"   状态: '{order_status}'")
            
            # 检查是否允许查看二维码
            can_view_qr = any(status in order_status for status in allowed_statuses)
            
            if can_view_qr:
                print(f"   ✅ 可以查看二维码")
            else:
                print(f"   ❌ 不能查看二维码 (状态不符合)")
                print(f"   💡 允许的状态: {allowed_statuses}")
            
            print()
        
        # 🎯 特别检查目标订单
        target_order_no = "2025060239828060"
        print(f"🎯 特别检查目标订单: {target_order_no}")
        
        for order in orders:
            if order.get('orderno') == target_order_no:
                print(f"✅ 找到目标订单!")
                print(f"   完整数据: {order}")
                
                status_text = order.get('orderS', '')
                can_view = any(status in status_text for status in allowed_statuses)
                
                print(f"   状态文本: '{status_text}'")
                print(f"   可以查看二维码: {can_view}")
                
                if not can_view:
                    print(f"   ❌ 这就是问题所在！订单状态不允许查看二维码")
                    print(f"   💡 需要修改状态检查逻辑或订单状态")
                
                break
        else:
            print(f"❌ 未找到目标订单 {target_order_no}")
            
    else:
        error_msg = order_result.get('resultDesc', '获取订单列表失败') if order_result else '网络错误'
        print(f"❌ 订单列表获取失败: {error_msg}")

if __name__ == "__main__":
    check_order_status()
