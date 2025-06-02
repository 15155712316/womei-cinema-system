#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试主程序双击流程
模拟主程序中的完整双击订单流程
"""

import sys
import json
import os
from PyQt5.QtWidgets import QApplication

def simulate_main_program_click():
    """模拟主程序中的双击订单流程"""
    print("=" * 80)
    print("🖱️ 模拟主程序双击订单流程")
    print("=" * 80)
    
    # 🎯 模拟虹湾影城的真实订单数据
    order_data = {
        'orderType': 1,
        'evaState': '0',
        'orderno': '202506021611295648804',
        'ticketCount': '2',
        'orderTimeOut': -16538000,
        'count': '2张',
        'showStartTime': '2025-06-03 10:00',
        'confirmFlag': '1',
        'orderState': '1',
        'showState': '0',
        'createTime': 1748851889000,
        'sellCount': 0,
        'orderPrice': 0,
        'orderS': '待使用',  # 这是关键的状态字段
        'refundtime': None,
        'payTime': '2025-06-02 16:11:48',
        'poster': 'https://tt7.cityfilms.cn/WebTicket/filmimgs/36563406.jpg',
        'orderTimeOutDate': '2025-06-02 16:18:29',
        'orderName': '私家侦探'
    }
    
    # 🎯 模拟虹湾影城账号
    account_data = {
        "userid": "15155712316",
        "openid": "ohA6p7Z0kejTSi40QVYXQtMF9SDY",
        "token": "02849a78647f5af9",
        "cinemaid": "11b7e4bcc265"
    }
    
    cinema_id = "11b7e4bcc265"
    order_no = order_data['orderno']
    status_text = order_data['orderS']
    
    print(f"📋 模拟数据:")
    print(f"   订单号: {order_no}")
    print(f"   影片: {order_data['orderName']}")
    print(f"   状态: {status_text}")
    print(f"   影院ID: {cinema_id}")
    print(f"   账号: {account_data['userid']}")
    print()
    
    # 🎯 步骤1：状态检查
    print("🔍 步骤1: 状态检查...")
    allowed_statuses = ['已完成', '待使用', '已支付', '已付款', '已取票']
    
    print(f"[订单二维码] 订单状态检查: '{status_text}'")
    print(f"[订单二维码] 允许的状态: {allowed_statuses}")
    
    status_check_passed = any(status in status_text for status in allowed_statuses)
    print(f"[订单二维码] 状态检查结果: {status_check_passed}")
    
    if status_check_passed:
        print("✅ 状态检查通过，可以查看二维码")
    else:
        print("❌ 状态检查失败，但继续执行（测试模式）")
    
    # 🎯 步骤2：获取订单详情
    print(f"\n🔍 步骤2: 获取订单详情...")
    
    from services.order_api import get_order_detail
    
    detail_params = {
        'orderno': order_no,
        'groupid': '',
        'cinemaid': cinema_id,
        'cardno': account_data.get('cardno', ''),
        'userid': account_data['userid'],
        'openid': account_data['openid'],
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': account_data['token'],
        'source': '2'
    }
    
    detail_result = get_order_detail(detail_params)
    
    if not detail_result or detail_result.get('resultCode') != '0':
        error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
        print(f"❌ 获取订单详情失败: {error_msg}")
        return False
    
    print("✅ 订单详情获取成功!")
    detail_data = detail_result.get('resultData', {})
    
    # 🎯 步骤3：提取取票码
    print(f"\n🎫 步骤3: 提取取票码...")
    qr_code = detail_data.get('qrCode', '')
    ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
    ds_code = detail_data.get('dsValidateCode', '')
    
    print(f"[订单二维码] 📋 - qrCode: {qr_code}")
    print(f"[订单二维码] 📋 - ticketCode: {ticket_code}")
    print(f"[订单二维码] 📋 - dsValidateCode: {ds_code}")
    
    final_ticket_code = qr_code or ds_code or ticket_code
    
    if final_ticket_code:
        print(f"✅ 找到真实取票码: {final_ticket_code}")
    else:
        print(f"⚠️ 没有找到真实取票码，生成模拟取票码")
        final_ticket_code = f"DEMO_{order_no[-8:]}"
        print(f"🎭 模拟取票码: {final_ticket_code}")
    
    # 🎯 步骤4：生成二维码
    print(f"\n🖼️ 步骤4: 生成取票码二维码...")
    
    from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image
    
    qr_bytes = generate_ticket_qrcode(final_ticket_code, detail_data)
    
    if not qr_bytes:
        print(f"❌ 二维码生成失败")
        return False
    
    print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
    
    # 🎯 步骤5：保存二维码图片
    print(f"\n💾 步骤5: 保存二维码图片...")
    save_path = save_qrcode_image(qr_bytes, order_no, cinema_id)
    
    if save_path:
        print(f"✅ 二维码图片保存成功: {save_path}")
    else:
        print(f"❌ 二维码图片保存失败")
        return False
    
    # 🎯 步骤6：创建显示数据
    print(f"\n🎭 步骤6: 创建主窗口显示数据...")
    
    combined_data = {
        'order_no': order_no,
        'qr_bytes': qr_bytes,
        'data_size': len(qr_bytes),
        'data_format': 'PNG',
        'display_type': 'generated_qrcode',
        'ticket_code': final_ticket_code,
        'film_name': detail_data.get('filmName', ''),
        'show_time': detail_data.get('showTime', ''),
        'hall_name': detail_data.get('hallName', ''),
        'seat_info': detail_data.get('seatInfo', ''),
        'cinema_name': detail_data.get('cinemaName', ''),
        'is_generated': True
    }
    
    print(f"📤 显示数据:")
    print(f"   显示类型: {combined_data['display_type']}")
    print(f"   取票码: {combined_data['ticket_code']}")
    print(f"   图片大小: {combined_data['data_size']} bytes")
    print(f"   影片: {combined_data['film_name']}")
    
    # 🎯 步骤7：测试事件总线发送
    print(f"\n📡 步骤7: 测试事件总线发送...")
    
    try:
        from utils.signals import event_bus
        
        # 创建一个简单的接收器来测试
        def test_receiver(data):
            print(f"🎯 事件总线接收到数据:")
            print(f"   数据类型: {type(data)}")
            if isinstance(data, dict):
                print(f"   显示类型: {data.get('display_type', 'N/A')}")
                print(f"   取票码: {data.get('ticket_code', 'N/A')}")
                print(f"   数据大小: {data.get('data_size', 'N/A')}")
        
        # 连接测试接收器
        event_bus.show_qrcode.connect(test_receiver)
        
        # 发送数据
        print(f"📤 发送数据到事件总线...")
        event_bus.show_qrcode.emit(combined_data)
        
        print(f"✅ 事件总线发送成功")
        
        # 断开测试接收器
        event_bus.show_qrcode.disconnect(test_receiver)
        
    except Exception as e:
        print(f"❌ 事件总线测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n🎉 模拟双击流程完成!")
    return True

def check_main_window_connection():
    """检查主窗口的事件连接"""
    print(f"\n" + "=" * 80)
    print("🔗 检查主窗口事件连接")
    print("=" * 80)
    
    try:
        # 尝试导入主窗口
        from main_modular import ModularCinemaMainWindow
        
        print(f"✅ 主窗口类导入成功")
        
        # 检查主窗口是否有正确的方法
        methods_to_check = [
            '_on_show_qrcode',
            '_display_generated_qrcode',
            '_display_combined_ticket_info'
        ]
        
        for method_name in methods_to_check:
            if hasattr(ModularCinemaMainWindow, method_name):
                print(f"✅ 主窗口有方法: {method_name}")
            else:
                print(f"❌ 主窗口缺少方法: {method_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查主窗口失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🖱️ 主程序双击流程调试启动")
    
    # 创建QApplication（事件总线需要）
    app = QApplication(sys.argv)
    
    # 运行模拟测试
    success1 = simulate_main_program_click()
    
    # 检查主窗口连接
    success2 = check_main_window_connection()
    
    print("\n" + "=" * 80)
    print("🏁 调试结果")
    print("=" * 80)
    
    if success1 and success2:
        print("✅ 模拟双击流程成功!")
        print("💡 如果主程序中仍然有问题，可能是:")
        print("   1. 主程序中的账号信息不正确")
        print("   2. 主程序中的事件总线连接有问题")
        print("   3. 主程序中的显示逻辑被其他代码覆盖")
        print("\n🔧 建议:")
        print("   1. 在主程序中添加更多调试输出")
        print("   2. 检查控制台输出，看是否有错误信息")
        print("   3. 确认选择的影院和账号是否正确")
    else:
        print("❌ 调试发现问题!")
        print("💡 请检查上面的错误信息")
    
    print("=" * 80)
