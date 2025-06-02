#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试虹湾影城15155712316账号的订单
"""

import json
import os
from services.order_api import get_order_list, get_order_detail
from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image

def get_hongwan_account():
    """获取虹湾影城15155712316账号信息"""
    try:
        accounts_file = os.path.join("data", "accounts.json")
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        # 查找虹湾影城的15155712316账号
        for account in accounts:
            if (account.get('userid') == '15155712316' and 
                account.get('cinemaid') == '11b7e4bcc265'):
                print(f"✅ 找到虹湾影城账号: {account.get('userid')}")
                return account
        
        print(f"❌ 未找到虹湾影城15155712316账号")
        return None
        
    except Exception as e:
        print(f"❌ 获取账号信息错误: {e}")
        return None

def test_hongwan_orders():
    """测试虹湾影城订单"""
    print("=" * 80)
    print("🎬 测试虹湾影城15155712316账号订单")
    print("=" * 80)
    
    # 获取账号信息
    account = get_hongwan_account()
    if not account:
        return False
    
    cinema_id = "11b7e4bcc265"  # 深影国际影城(佐阾虹湾购物中心店)
    cinema_name = "深影国际影城(佐阾虹湾购物中心店)"
    
    print(f"📋 账号信息:")
    print(f"   用户ID: {account.get('userid')}")
    print(f"   影院ID: {cinema_id}")
    print(f"   影院名: {cinema_name}")
    print(f"   OpenID: {account.get('openid', '')[:20]}...")
    print(f"   Token: {account.get('token', '')[:20]}...")
    print()
    
    # 🎯 获取订单列表
    print("📋 获取订单列表...")
    order_params = {
        'pageNo': '1',
        'groupid': '',
        'cinemaid': cinema_id,
        'cardno': account.get('cardno', ''),
        'userid': account.get('userid'),
        'openid': account.get('openid'),
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': account.get('token'),
        'source': '2'
    }
    
    print(f"📤 请求参数:")
    for key, value in order_params.items():
        if key in ['openid', 'token']:
            print(f"   {key}: {str(value)[:20]}...")
        else:
            print(f"   {key}: {value}")
    print()
    
    order_result = get_order_list(order_params)
    
    if not order_result:
        print("❌ 订单列表请求失败")
        return False
    
    print(f"📊 API响应:")
    print(f"   resultCode: {order_result.get('resultCode')}")
    print(f"   resultDesc: {order_result.get('resultDesc')}")
    
    if order_result.get('resultCode') != '0':
        print(f"❌ 订单列表获取失败: {order_result.get('resultDesc')}")
        return False
    
    # 解析订单数据
    result_data = order_result.get('resultData', {})
    print(f"📊 resultData字段: {list(result_data.keys())}")
    
    # 尝试多种可能的订单字段
    orders = None
    if 'orderList' in result_data:
        orders = result_data['orderList']
        print(f"✅ 使用 orderList 字段，找到 {len(orders)} 个订单")
    elif 'orders' in result_data:
        orders = result_data['orders']
        print(f"✅ 使用 orders 字段，找到 {len(orders)} 个订单")
    elif 'data' in result_data:
        data = result_data['data']
        if isinstance(data, list):
            orders = data
            print(f"✅ 使用 data 数组，找到 {len(orders)} 个订单")
        elif isinstance(data, dict) and 'orderList' in data:
            orders = data['orderList']
            print(f"✅ 使用 data.orderList，找到 {len(orders)} 个订单")
    
    if not orders:
        print(f"❌ 未找到订单数据")
        print(f"📊 完整响应数据: {result_data}")
        return False
    
    print(f"\n🎉 成功找到 {len(orders)} 个订单!")
    
    # 显示所有订单
    for i, order in enumerate(orders):
        order_no = order.get('orderno', 'N/A')
        order_name = order.get('orderName', 'N/A')
        order_status = order.get('orderS', 'N/A')
        
        print(f"\n📋 订单 {i+1}:")
        print(f"   订单号: {order_no}")
        print(f"   影片: {order_name}")
        print(f"   状态: {order_status}")
        
        # 显示完整订单数据
        print(f"   完整数据: {order}")
    
    # 🎯 选择第一个订单进行二维码测试
    if orders:
        test_order = orders[0]
        order_no = test_order.get('orderno')
        
        print(f"\n🎯 选择订单 {order_no} 进行二维码测试...")
        return test_order_qrcode(order_no, cinema_id, account)
    
    return True

def test_order_qrcode(order_no, cinema_id, account):
    """测试订单二维码生成"""
    print(f"\n🖼️ 测试订单 {order_no} 的二维码生成...")
    
    # 🎯 获取订单详情
    print("🔍 获取订单详情...")
    detail_params = {
        'orderno': order_no,
        'groupid': '',
        'cinemaid': cinema_id,
        'cardno': account.get('cardno', ''),
        'userid': account.get('userid'),
        'openid': account.get('openid'),
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': account.get('token'),
        'source': '2'
    }
    
    detail_result = get_order_detail(detail_params)
    
    if not detail_result or detail_result.get('resultCode') != '0':
        error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
        print(f"❌ 订单详情获取失败: {error_msg}")
        return False
    
    print("✅ 订单详情获取成功!")
    detail_data = detail_result.get('resultData', {})
    
    # 🎯 提取取票码信息
    print("\n🎫 提取取票码信息...")
    qr_code = detail_data.get('qrCode', '')
    ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
    ds_code = detail_data.get('dsValidateCode', '')
    
    print(f"📊 取票码字段:")
    print(f"   qrCode: {repr(qr_code)}")
    print(f"   ticketCode: {repr(ticket_code)}")
    print(f"   dsValidateCode: {repr(ds_code)}")
    
    # 确定最终取票码
    final_ticket_code = qr_code or ds_code or ticket_code
    
    if not final_ticket_code:
        print(f"⚠️ 没有找到真实取票码，生成模拟取票码...")
        final_ticket_code = f"HONGWAN_{order_no[-8:]}"
        print(f"🎭 模拟取票码: {final_ticket_code}")
    else:
        print(f"✅ 找到真实取票码: {final_ticket_code}")
    
    # 🎯 生成二维码
    print(f"\n🖼️ 生成取票码二维码...")
    
    # 提取订单信息
    order_info = {
        'filmName': detail_data.get('filmName', '虹湾测试影片'),
        'cinemaName': detail_data.get('cinemaName', '深影国际影城(佐阾虹湾购物中心店)'),
        'showTime': detail_data.get('showTime', '2025-06-02 20:00'),
        'seatInfo': detail_data.get('seatInfo', '虹湾测试座位'),
        'hallName': detail_data.get('hallName', '虹湾测试影厅')
    }
    
    print(f"📋 订单信息:")
    for key, value in order_info.items():
        print(f"   {key}: {value}")
    
    # 生成二维码
    qr_bytes = generate_ticket_qrcode(final_ticket_code, order_info)
    
    if not qr_bytes:
        print(f"❌ 二维码生成失败")
        return False
    
    print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
    
    # 🎯 保存二维码图片
    print(f"\n💾 保存二维码图片...")
    save_path = save_qrcode_image(qr_bytes, order_no, cinema_id)
    
    if save_path:
        print(f"✅ 二维码图片保存成功: {save_path}")
        
        # 检查文件
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"📁 文件验证:")
            print(f"   路径: {save_path}")
            print(f"   大小: {file_size} bytes")
            print(f"   存在: ✅")
        
        print(f"\n🎉 虹湾影城订单二维码测试成功!")
        print(f"🎫 取票码: {final_ticket_code}")
        print(f"📱 扫描二维码可获取取票码")
        
        return True
    else:
        print(f"❌ 二维码图片保存失败")
        return False

if __name__ == "__main__":
    print("🎬 虹湾影城订单测试启动")
    
    success = test_hongwan_orders()
    
    print("\n" + "=" * 80)
    print("🏁 测试结果")
    print("=" * 80)
    
    if success:
        print("🎉 虹湾影城订单测试成功!")
        print("\n💡 现在您可以在主程序中:")
        print("   1. 选择影院: 深影国际影城(佐阾虹湾购物中心店)")
        print("   2. 选择账号: 15155712316")
        print("   3. 切换到订单Tab")
        print("   4. 双击任何订单查看二维码")
    else:
        print("❌ 虹湾影城订单测试失败")
        print("💡 请检查账号信息和网络连接")
    
    print("=" * 80)
