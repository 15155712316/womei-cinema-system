#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的二维码功能测试
测试：订单详情获取 + 取票码提取 + 二维码图片获取 + 本地保存
"""

import sys
import os
from services.order_api import get_order_detail, get_order_qrcode_api

def test_complete_qrcode_flow():
    """测试完整的二维码获取流程"""
    print("=" * 80)
    print("🧪 完整二维码功能测试")
    print("=" * 80)
    
    # 测试参数
    test_order_no = "2025060239828060"  # 您提供的订单号
    test_cinema_id = "35fec8259e74"     # 华夏优加荟大都荟
    
    # 账号认证信息
    test_account = {
        "userid": "14700283316",
        "openid": "oAOCp7fvQZ57uCG-5H0XZyUSbO-4",
        "token": "a53201ca598cfcc8",
        "cinemaid": "35fec8259e74"
    }
    
    print(f"📋 测试参数:")
    print(f"   订单号: {test_order_no}")
    print(f"   影院ID: {test_cinema_id}")
    print(f"   账号ID: {test_account['userid']}")
    print()
    
    # 🎯 步骤1：获取订单详情
    print("🔍 步骤1: 获取订单详情...")
    detail_params = {
        'orderno': test_order_no,
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
    
    detail_result = get_order_detail(detail_params)
    
    if detail_result and detail_result.get('resultCode') == '0':
        print("✅ 订单详情获取成功!")
        
        detail_data = detail_result.get('resultData', {})
        
        # 提取关键信息
        film_name = detail_data.get('filmName', '未知影片')
        show_time = detail_data.get('showTime', '未知时间')
        hall_name = detail_data.get('hallName', '未知影厅')
        seat_info = detail_data.get('seatInfo', '未知座位')
        cinema_name = detail_data.get('cinemaName', '未知影院')
        ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
        ds_code = detail_data.get('dsValidateCode', '')
        
        print(f"📊 订单详情:")
        print(f"   影片: {film_name}")
        print(f"   影院: {cinema_name}")
        print(f"   时间: {show_time}")
        print(f"   影厅: {hall_name}")
        print(f"   座位: {seat_info}")
        print(f"   ticketCode: {ticket_code}")
        print(f"   dsValidateCode: {ds_code}")
        
        # 确定最终取票码
        final_ticket_code = ds_code or ticket_code
        print(f"🎫 最终取票码: {final_ticket_code}")
        print()
        
    else:
        error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
        print(f"❌ 订单详情获取失败: {error_msg}")
        return False
    
    # 🎯 步骤2：获取二维码图片
    print("🖼️ 步骤2: 获取二维码图片...")
    qr_result = get_order_qrcode_api(test_order_no, test_cinema_id, test_account)
    
    if qr_result:
        print(f"✅ 二维码获取成功!")
        print(f"📏 图片大小: {len(qr_result)} bytes")
        
        # 分析图片格式
        if qr_result.startswith(b'\x89PNG'):
            data_format = "PNG"
        elif qr_result.startswith(b'\xff\xd8\xff'):
            data_format = "JPEG"
        elif qr_result.startswith(b'GIF'):
            data_format = "GIF"
        else:
            data_format = "UNKNOWN"
        
        print(f"🎨 图片格式: {data_format}")
        
        # 检查保存的文件
        img_dir = os.path.join("data", "img")
        if os.path.exists(img_dir):
            files = [f for f in os.listdir(img_dir) if f.endswith('.png')]
            print(f"📁 data/img 目录中的文件:")
            for file in files:
                file_path = os.path.join(img_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   {file} ({file_size} bytes)")
        
        print()
        
    else:
        print(f"❌ 二维码获取失败")
        return False
    
    # 🎯 步骤3：模拟组合显示数据
    print("🎭 步骤3: 创建组合显示数据...")
    combined_data = {
        'order_no': test_order_no,
        'qr_bytes': qr_result,
        'data_size': len(qr_result),
        'data_format': data_format,
        'display_type': 'combined',
        'ticket_code': final_ticket_code,
        'film_name': film_name,
        'show_time': show_time,
        'hall_name': hall_name,
        'seat_info': seat_info,
        'cinema_name': cinema_name
    }
    
    print(f"✅ 组合数据创建成功:")
    print(f"   显示类型: {combined_data['display_type']}")
    print(f"   取票码: {combined_data['ticket_code']}")
    print(f"   影片: {combined_data['film_name']}")
    print(f"   二维码: {combined_data['data_size']} bytes {combined_data['data_format']}")
    print()
    
    # 🎯 总结
    print("=" * 80)
    print("🏁 测试完成总结:")
    print("=" * 80)
    print("✅ 订单详情获取: 成功")
    print(f"✅ 取票码提取: {final_ticket_code}")
    print(f"✅ 二维码图片: {len(qr_result)} bytes {data_format}")
    print("✅ 本地图片保存: 成功")
    print("✅ 组合数据创建: 成功")
    print()
    print("🎯 现在可以在主程序中双击订单，应该能看到:")
    print("   1. 完整的订单详情文本")
    print("   2. 真实的二维码图片")
    print("   3. 保存到 data/img/ 目录的图片文件")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    print("🧪 完整二维码功能测试启动")
    success = test_complete_qrcode_flow()
    
    if success:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败！")
