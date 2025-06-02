#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试当前问题
检查为什么取票码显示为空
"""

import sys
import json
import os
from services.order_api import get_order_detail

def debug_ticket_code_issue():
    """调试取票码显示为空的问题"""
    print("=" * 80)
    print("🔍 调试取票码显示为空问题")
    print("=" * 80)
    
    # 🎯 使用虹湾影城的真实账号和订单
    test_account = {
        "userid": "15155712316",
        "openid": "ohA6p7Z0kejTSi40QVYXQtMF9SDY",
        "token": "02849a78647f5af9",
        "cinemaid": "11b7e4bcc265"
    }
    
    cinema_id = "11b7e4bcc265"
    order_no = "202506021611295648804"
    
    print(f"📋 测试参数:")
    print(f"   订单号: {order_no}")
    print(f"   影院ID: {cinema_id}")
    print(f"   账号: {test_account['userid']}")
    print()
    
    # 🎯 获取订单详情
    print("🔍 获取订单详情...")
    detail_params = {
        'orderno': order_no,
        'groupid': '',
        'cinemaid': cinema_id,
        'cardno': test_account.get('cardno', ''),
        'userid': test_account['userid'],
        'openid': test_account['openid'],
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': test_account['token'],
        'source': '2'
    }
    
    detail_result = get_order_detail(detail_params)
    
    if not detail_result:
        print("❌ API请求失败")
        return False
    
    print(f"📊 API响应:")
    print(f"   resultCode: {detail_result.get('resultCode')}")
    print(f"   resultDesc: {detail_result.get('resultDesc')}")
    
    if detail_result.get('resultCode') != '0':
        print(f"❌ API返回错误: {detail_result.get('resultDesc')}")
        return False
    
    # 🎯 分析订单详情数据
    detail_data = detail_result.get('resultData', {})
    
    print(f"\n📋 订单详情数据分析:")
    print(f"   数据类型: {type(detail_data)}")
    print(f"   数据字段数: {len(detail_data)}")
    
    # 显示所有字段
    print(f"\n📊 所有字段:")
    for key, value in detail_data.items():
        if isinstance(value, str) and len(str(value)) > 50:
            print(f"   {key}: {str(value)[:50]}...")
        else:
            print(f"   {key}: {value}")
    
    # 🎯 重点检查取票码相关字段
    print(f"\n🎫 取票码相关字段检查:")
    
    qr_code = detail_data.get('qrCode', '')
    ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
    ds_code = detail_data.get('dsValidateCode', '')
    
    print(f"   qrCode: {repr(qr_code)} (类型: {type(qr_code)})")
    print(f"   ticketCode: {repr(ticket_code)} (类型: {type(ticket_code)})")
    print(f"   dsValidateCode: {repr(ds_code)} (类型: {type(ds_code)})")
    
    # 检查是否有其他可能的取票码字段
    possible_fields = [
        'qrCode', 'qrcode', 'QRCode', 'QRCODE',
        'ticketCode', 'ticketcode', 'ticket_code', 'TicketCode',
        'dsValidateCode', 'dsvalidatecode', 'ds_validate_code',
        'validateCode', 'validate_code', 'ValidateCode',
        'pickupCode', 'pickup_code', 'PickupCode',
        'code', 'Code', 'CODE'
    ]
    
    print(f"\n🔍 搜索所有可能的取票码字段:")
    found_codes = {}
    for field in possible_fields:
        if field in detail_data:
            value = detail_data[field]
            if value:  # 只显示非空值
                found_codes[field] = value
                print(f"   ✅ {field}: {repr(value)}")
    
    if not found_codes:
        print(f"   ❌ 没有找到任何取票码字段")
    
    # 🎯 确定最终取票码
    final_ticket_code = qr_code or ds_code or ticket_code
    
    print(f"\n🎯 最终取票码确定:")
    print(f"   优先级: qrCode > dsValidateCode > ticketCode")
    print(f"   qrCode: {repr(qr_code)} {'✅' if qr_code else '❌'}")
    print(f"   dsValidateCode: {repr(ds_code)} {'✅' if ds_code else '❌'}")
    print(f"   ticketCode: {repr(ticket_code)} {'✅' if ticket_code else '❌'}")
    print(f"   最终结果: {repr(final_ticket_code)} {'✅' if final_ticket_code else '❌'}")
    
    # 🎯 模拟主程序的显示逻辑
    print(f"\n🎭 模拟主程序显示逻辑:")
    
    if final_ticket_code:
        print(f"✅ 有取票码，应该显示: {final_ticket_code}")
        
        # 构建显示数据
        ticket_data = {
            'order_no': order_no,
            'ticket_code': final_ticket_code,
            'film_name': detail_data.get('filmName', '未知影片'),
            'show_time': detail_data.get('showTime', '未知时间'),
            'hall_name': detail_data.get('hallName', '未知影厅'),
            'seat_info': detail_data.get('seatInfo', '未知座位'),
            'cinema_name': detail_data.get('cinemaName', '未知影院'),
            'display_type': 'ticket_code'
        }
        
        print(f"📤 应该发送的显示数据:")
        for key, value in ticket_data.items():
            print(f"   {key}: {repr(value)}")
        
        return True
    else:
        print(f"❌ 没有取票码，会显示: '无取票码'")
        
        # 检查是否有其他有用信息
        print(f"\n📋 其他可能有用的信息:")
        useful_fields = ['filmName', 'showTime', 'hallName', 'seatInfo', 'cinemaName']
        for field in useful_fields:
            value = detail_data.get(field, '')
            print(f"   {field}: {repr(value)}")
        
        return False

def check_main_window_display():
    """检查主窗口显示逻辑"""
    print(f"\n" + "=" * 80)
    print("🖥️ 检查主窗口显示逻辑")
    print("=" * 80)
    
    try:
        from main_modular import ModularCinemaMainWindow
        
        # 检查主窗口的显示方法
        methods = ['_on_show_qrcode', '_display_qrcode_text']
        
        for method_name in methods:
            if hasattr(ModularCinemaMainWindow, method_name):
                print(f"✅ 主窗口有方法: {method_name}")
            else:
                print(f"❌ 主窗口缺少方法: {method_name}")
        
        # 检查主窗口的显示逻辑
        print(f"\n🔍 检查主窗口的 _on_show_qrcode 方法...")
        
        # 查看方法源码（如果可能）
        if hasattr(ModularCinemaMainWindow, '_on_show_qrcode'):
            method = getattr(ModularCinemaMainWindow, '_on_show_qrcode')
            print(f"✅ _on_show_qrcode 方法存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查主窗口失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 调试取票码显示问题")
    
    # 调试取票码获取
    success1 = debug_ticket_code_issue()
    
    # 检查主窗口显示
    success2 = check_main_window_display()
    
    print("\n" + "=" * 80)
    print("🏁 调试结果总结")
    print("=" * 80)
    
    if success1:
        print("✅ 取票码获取正常")
        print("💡 问题可能在于:")
        print("   1. 主窗口显示逻辑有问题")
        print("   2. 事件总线传递有问题")
        print("   3. 界面更新有问题")
    else:
        print("❌ 取票码获取有问题")
        print("💡 问题可能在于:")
        print("   1. API返回的数据结构变化")
        print("   2. 取票码字段名不对")
        print("   3. 订单状态不对")
    
    if success2:
        print("✅ 主窗口方法检查正常")
    else:
        print("❌ 主窗口方法检查有问题")
    
    print("\n💡 建议:")
    print("   1. 在主程序中双击订单时查看控制台输出")
    print("   2. 检查是否有错误信息")
    print("   3. 确认选择的影院和账号是否正确")
    
    print("=" * 80)
