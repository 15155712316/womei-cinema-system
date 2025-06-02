#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查找有效的订单（待取票或已使用状态）
用于获取真实的取票码
"""

import sys
import os
from services.order_api import get_order_list, get_order_detail

def find_valid_orders():
    """查找有效的订单"""
    print("=" * 80)
    print("🔍 查找有效订单（待取票/已使用状态）")
    print("=" * 80)
    
    # 账号认证信息
    test_account = {
        "userid": "14700283316",
        "openid": "oAOCp7fvQZ57uCG-5H0XZyUSbO-4",
        "token": "a53201ca598cfcc8",
        "cinemaid": "35fec8259e74"
    }
    
    test_cinema_id = "35fec8259e74"
    
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
        
        # 🎯 分析每个订单
        valid_orders = []
        
        for i, order in enumerate(orders):
            order_no = order.get('orderno', '')
            order_name = order.get('orderName', '')
            order_status = order.get('orderS', '')
            
            print(f"📋 订单 {i+1}:")
            print(f"   订单号: {order_no}")
            print(f"   影片: {order_name}")
            print(f"   状态: {order_status}")
            
            # 检查订单状态
            if order_status in ['待取票', '已使用', '已完成', '已取票']:
                print(f"   ✅ 这是一个可能有取票码的订单")
                valid_orders.append({
                    'orderno': order_no,
                    'orderName': order_name,
                    'orderS': order_status
                })
            else:
                print(f"   ⚠️ 状态不符合要求")
            
            print()
        
        if valid_orders:
            print(f"🎯 找到 {len(valid_orders)} 个可能有取票码的订单:")
            for order in valid_orders:
                print(f"   {order['orderno']} - {order['orderName']} ({order['orderS']})")
            
            # 🎯 检查第一个有效订单的详情
            print(f"\n🔍 检查第一个有效订单的详情...")
            first_order = valid_orders[0]
            return check_order_detail(first_order['orderno'], test_cinema_id, test_account)
        else:
            print("❌ 没有找到有效的订单")
            return None
            
    else:
        error_msg = order_result.get('resultDesc', '获取订单列表失败') if order_result else '网络错误'
        print(f"❌ 订单列表获取失败: {error_msg}")
        return None

def check_order_detail(order_no, cinema_id, account):
    """检查订单详情中的取票码"""
    print(f"📋 检查订单 {order_no} 的详情...")
    
    detail_params = {
        'orderno': order_no,
        'groupid': '',
        'cinemaid': cinema_id,
        'cardno': account.get('cardno', ''),
        'userid': account['userid'],
        'openid': account['openid'],
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': account['token'],
        'source': '2'
    }
    
    detail_result = get_order_detail(detail_params)
    
    if detail_result and detail_result.get('resultCode') == '0':
        print("✅ 订单详情获取成功!")
        
        detail_data = detail_result.get('resultData', {})
        
        # 提取取票码信息
        qr_code = detail_data.get('qrCode', '')
        ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
        ds_code = detail_data.get('dsValidateCode', '')
        
        print(f"📊 取票码信息:")
        print(f"   qrCode: {qr_code}")
        print(f"   ticketCode: {ticket_code}")
        print(f"   dsValidateCode: {ds_code}")
        
        # 确定最终取票码
        final_ticket_code = qr_code or ds_code or ticket_code
        
        if final_ticket_code:
            print(f"✅ 找到取票码: {final_ticket_code}")
            
            # 返回完整的订单信息
            return {
                'order_no': order_no,
                'ticket_code': final_ticket_code,
                'cinema_id': cinema_id,
                'detail_data': detail_data
            }
        else:
            print(f"❌ 此订单没有取票码")
            return None
    else:
        error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
        print(f"❌ 订单详情获取失败: {error_msg}")
        return None

def test_qrcode_with_valid_order(order_info):
    """使用有效订单测试二维码生成"""
    if not order_info:
        print("❌ 没有有效的订单信息")
        return False
    
    print("\n" + "=" * 80)
    print("🎨 使用真实取票码生成二维码")
    print("=" * 80)
    
    from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image
    
    order_no = order_info['order_no']
    ticket_code = order_info['ticket_code']
    cinema_id = order_info['cinema_id']
    detail_data = order_info['detail_data']
    
    print(f"📋 订单信息:")
    print(f"   订单号: {order_no}")
    print(f"   取票码: {ticket_code}")
    print(f"   影院ID: {cinema_id}")
    
    # 提取订单详情用于二维码
    order_detail = {
        'filmName': detail_data.get('filmName', ''),
        'cinemaName': detail_data.get('cinemaName', ''),
        'showTime': detail_data.get('showTime', ''),
        'seatInfo': detail_data.get('seatInfo', ''),
        'hallName': detail_data.get('hallName', '')
    }
    
    print(f"📋 订单详情:")
    for key, value in order_detail.items():
        print(f"   {key}: {value}")
    
    # 🎯 生成二维码
    print(f"\n🖼️ 生成取票码二维码...")
    qr_bytes = generate_ticket_qrcode(ticket_code, order_detail)
    
    if qr_bytes:
        print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
        
        # 保存二维码图片
        save_path = save_qrcode_image(qr_bytes, order_no, cinema_id)
        
        if save_path:
            print(f"✅ 二维码图片保存成功: {save_path}")
            print(f"🎯 扫描此二维码应该能获取到取票码: {ticket_code}")
            return True
        else:
            print("❌ 二维码图片保存失败")
            return False
    else:
        print("❌ 二维码生成失败")
        return False

if __name__ == "__main__":
    print("🔍 查找有效订单并生成真实取票码二维码")
    
    # 查找有效订单
    order_info = find_valid_orders()
    
    # 使用有效订单测试二维码生成
    if order_info:
        success = test_qrcode_with_valid_order(order_info)
        
        if success:
            print("\n🎉 真实取票码二维码生成成功！")
            print("💡 现在可以用手机扫描生成的二维码验证取票码内容")
        else:
            print("\n❌ 二维码生成失败")
    else:
        print("\n❌ 没有找到有效的订单")
