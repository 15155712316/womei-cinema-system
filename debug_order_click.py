#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试订单双击功能
模拟双击订单的完整流程
"""

import sys
import os
from services.order_api import get_order_detail
from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image

def simulate_order_double_click():
    """模拟订单双击处理流程"""
    print("=" * 80)
    print("🖱️ 模拟订单双击处理流程")
    print("=" * 80)
    
    # 模拟订单数据
    order_no = "2025060239828060"
    cinemaid = "35fec8259e74"
    
    # 模拟账号数据
    account = {
        "userid": "14700283316",
        "openid": "oAOCp7fvQZ57uCG-5H0XZyUSbO-4",
        "token": "a53201ca598cfcc8",
        "cinemaid": "35fec8259e74"
    }
    
    print(f"📋 模拟双击订单:")
    print(f"   订单号: {order_no}")
    print(f"   影院ID: {cinemaid}")
    print(f"   账号: {account['userid']}")
    print()
    
    try:
        # 🎯 步骤1：获取订单详情
        print("🔍 步骤1: 获取订单详情...")
        detail_params = {
            'orderno': order_no,
            'groupid': '',
            'cinemaid': cinemaid,
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2'
        }
        
        detail_result = get_order_detail(detail_params)
        
        if not detail_result or detail_result.get('resultCode') != '0':
            error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
            print(f"❌ 订单详情获取失败: {error_msg}")
            return False
        
        print("✅ 订单详情获取成功!")
        detail_data = detail_result.get('resultData', {})
        
        # 🎯 步骤2：提取取票码信息
        print("\n🎫 步骤2: 提取取票码信息...")
        qr_code = detail_data.get('qrCode', '')
        ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
        ds_code = detail_data.get('dsValidateCode', '')
        
        print(f"📊 取票码字段:")
        print(f"   qrCode: {repr(qr_code)}")
        print(f"   ticketCode: {repr(ticket_code)}")
        print(f"   dsValidateCode: {repr(ds_code)}")
        
        # 确定最终取票码
        final_ticket_code = qr_code or ds_code or ticket_code
        print(f"🎯 最终取票码: {repr(final_ticket_code)}")
        
        # 🎯 步骤3：根据是否有取票码选择处理方式
        if final_ticket_code:
            print(f"\n✅ 找到取票码，生成二维码...")
            return generate_qrcode_flow(order_no, final_ticket_code, detail_data, cinemaid)
        else:
            print(f"\n⚠️ 没有找到取票码，生成模拟取票码...")
            mock_ticket_code = f"DEMO_{order_no[-8:]}"
            print(f"🎭 模拟取票码: {mock_ticket_code}")
            return generate_qrcode_flow(order_no, mock_ticket_code, detail_data, cinemaid)
            
    except Exception as e:
        print(f"❌ 模拟双击处理错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_qrcode_flow(order_no, ticket_code, detail_data, cinema_id):
    """生成二维码的完整流程"""
    try:
        print(f"🖼️ 开始生成二维码流程...")
        print(f"   订单号: {order_no}")
        print(f"   取票码: {ticket_code}")
        print(f"   影院ID: {cinema_id}")
        
        # 🎯 生成二维码图片
        qr_bytes = generate_ticket_qrcode(ticket_code, detail_data)
        
        if not qr_bytes:
            print(f"❌ 二维码生成失败")
            return False
        
        print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
        
        # 🎯 保存二维码图片到本地
        save_path = save_qrcode_image(qr_bytes, order_no, cinema_id)
        
        if not save_path:
            print(f"❌ 二维码图片保存失败")
            return False
        
        print(f"✅ 二维码图片保存成功: {save_path}")
        
        # 🎯 检查保存的文件
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"📁 文件验证:")
            print(f"   路径: {save_path}")
            print(f"   大小: {file_size} bytes")
            print(f"   存在: ✅")
        else:
            print(f"❌ 保存的文件不存在: {save_path}")
            return False
        
        # 🎯 创建主窗口显示数据
        display_data = {
            'order_no': order_no,
            'qr_bytes': qr_bytes,
            'data_size': len(qr_bytes),
            'data_format': 'PNG',
            'display_type': 'generated_qrcode',
            'ticket_code': ticket_code,
            'film_name': detail_data.get('filmName', ''),
            'show_time': detail_data.get('showTime', ''),
            'hall_name': detail_data.get('hallName', ''),
            'seat_info': detail_data.get('seatInfo', ''),
            'cinema_name': detail_data.get('cinemaName', ''),
            'is_generated': True
        }
        
        print(f"📤 创建显示数据:")
        print(f"   显示类型: {display_data['display_type']}")
        print(f"   取票码: {display_data['ticket_code']}")
        print(f"   数据大小: {display_data['data_size']} bytes")
        
        # 🎯 模拟发送到主窗口
        print(f"📡 模拟发送到主窗口...")
        print(f"   事件类型: show_qrcode")
        print(f"   数据类型: {type(display_data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 生成二维码流程错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_current_files():
    """检查当前的文件状态"""
    print("\n" + "=" * 80)
    print("📁 检查当前文件状态")
    print("=" * 80)
    
    img_dir = os.path.join("data", "img")
    if os.path.exists(img_dir):
        files = [f for f in os.listdir(img_dir) if f.endswith('.png')]
        
        print(f"📁 data/img 目录中的文件:")
        for file in files:
            file_path = os.path.join(img_dir, file)
            file_size = os.path.getsize(file_path)
            
            # 检查是否是最新的
            import time
            file_time = os.path.getmtime(file_path)
            current_time = time.time()
            age_minutes = (current_time - file_time) / 60
            
            if age_minutes < 5:  # 5分钟内的文件
                age_status = f"🆕 {age_minutes:.1f}分钟前"
            else:
                age_status = f"🕐 {age_minutes:.0f}分钟前"
            
            print(f"   {file} ({file_size} bytes) {age_status}")
        
        return len(files) > 0
    else:
        print(f"❌ data/img 目录不存在")
        return False

if __name__ == "__main__":
    print("🖱️ 订单双击调试工具启动")
    
    # 检查当前文件状态
    check_current_files()
    
    # 模拟双击处理
    success = simulate_order_double_click()
    
    # 再次检查文件状态
    check_current_files()
    
    print("\n" + "=" * 80)
    print("🏁 调试结果")
    print("=" * 80)
    
    if success:
        print("✅ 模拟双击处理成功!")
        print("💡 如果主程序中仍然有问题，可能是:")
        print("   1. 事件总线连接问题")
        print("   2. 主窗口显示逻辑问题")
        print("   3. 订单状态检查问题")
    else:
        print("❌ 模拟双击处理失败!")
        print("💡 请检查上面的错误信息")
    
    print("=" * 80)
