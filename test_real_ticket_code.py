#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用真实取票码格式测试二维码生成
基于常见的电影票取票码格式
"""

import sys
import os
from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image

def test_real_ticket_code_formats():
    """测试真实的取票码格式"""
    print("=" * 80)
    print("🎫 真实取票码格式测试")
    print("=" * 80)
    
    # 🎯 常见的取票码格式
    test_cases = [
        {
            'name': '数字取票码',
            'ticket_code': '123456789012',
            'order_no': '2025060239828060',
            'order_info': {
                'filmName': '测试影片',
                'cinemaName': '华夏优加荟大都荟',
                'showTime': '2025-06-02 19:30',
                'seatInfo': '5排7座',
                'hallName': '1号厅'
            }
        },
        {
            'name': '字母数字混合取票码',
            'ticket_code': 'ABC123DEF456',
            'order_no': '2025060239828061',
            'order_info': {
                'filmName': '复仇者联盟',
                'cinemaName': '华夏优加荟大都荟',
                'showTime': '2025-06-02 21:00',
                'seatInfo': '8排12座',
                'hallName': '2号厅'
            }
        },
        {
            'name': '短取票码',
            'ticket_code': '987654',
            'order_no': '2025060239828062',
            'order_info': {
                'filmName': '阿凡达',
                'cinemaName': '华夏优加荟大都荟',
                'showTime': '2025-06-03 14:30',
                'seatInfo': '3排5座',
                'hallName': '3号厅'
            }
        },
        {
            'name': '长取票码',
            'ticket_code': 'TICKET2025060239828063ABCDEF',
            'order_no': '2025060239828063',
            'order_info': {
                'filmName': '流浪地球',
                'cinemaName': '华夏优加荟大都荟',
                'showTime': '2025-06-03 16:45',
                'seatInfo': '6排9座',
                'hallName': '4号厅'
            }
        }
    ]
    
    successful_tests = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n🧪 测试 {i+1}: {test_case['name']}")
        print(f"📋 取票码: {test_case['ticket_code']}")
        print(f"📋 订单号: {test_case['order_no']}")
        
        # 显示订单信息
        order_info = test_case['order_info']
        print(f"📋 订单信息:")
        for key, value in order_info.items():
            print(f"   {key}: {value}")
        
        # 🎯 生成二维码
        print(f"🖼️ 生成二维码...")
        qr_bytes = generate_ticket_qrcode(test_case['ticket_code'], order_info)
        
        if qr_bytes:
            print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
            
            # 保存二维码图片
            save_path = save_qrcode_image(qr_bytes, test_case['order_no'], "35fec8259e74")
            
            if save_path:
                print(f"✅ 二维码图片保存成功: {save_path}")
                print(f"🎯 扫描此二维码应该能获取到: {test_case['ticket_code']}")
                
                successful_tests.append({
                    'name': test_case['name'],
                    'ticket_code': test_case['ticket_code'],
                    'file_path': save_path,
                    'qr_size': len(qr_bytes)
                })
            else:
                print(f"❌ 二维码图片保存失败")
        else:
            print(f"❌ 二维码生成失败")
        
        print("-" * 60)
    
    # 🎯 测试总结
    print(f"\n📊 测试总结:")
    print(f"✅ 成功生成: {len(successful_tests)}/{len(test_cases)} 个二维码")
    
    if successful_tests:
        print(f"\n📁 生成的二维码文件:")
        for test in successful_tests:
            print(f"   {test['name']}: {test['file_path']} ({test['qr_size']} bytes)")
            print(f"      取票码: {test['ticket_code']}")
    
    return len(successful_tests) > 0

def test_qrcode_display_integration():
    """测试二维码显示集成"""
    print("\n" + "=" * 80)
    print("🎭 二维码显示集成测试")
    print("=" * 80)
    
    # 使用第一个测试用例
    test_ticket_code = "123456789012"
    test_order_no = "2025060239828060"
    test_order_info = {
        'filmName': '测试影片',
        'cinemaName': '华夏优加荟大都荟',
        'showTime': '2025-06-02 19:30',
        'seatInfo': '5排7座',
        'hallName': '1号厅'
    }
    
    print(f"📋 测试数据:")
    print(f"   取票码: {test_ticket_code}")
    print(f"   订单号: {test_order_no}")
    
    # 生成二维码
    qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
    
    if qr_bytes:
        print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
        
        # 🎯 创建主窗口显示数据格式
        display_data = {
            'order_no': test_order_no,
            'qr_bytes': qr_bytes,
            'data_size': len(qr_bytes),
            'data_format': 'PNG',
            'display_type': 'generated_qrcode',
            'ticket_code': test_ticket_code,
            'film_name': test_order_info['filmName'],
            'show_time': test_order_info['showTime'],
            'hall_name': test_order_info['hallName'],
            'seat_info': test_order_info['seatInfo'],
            'cinema_name': test_order_info['cinemaName'],
            'is_generated': True
        }
        
        print(f"📤 主窗口显示数据:")
        print(f"   显示类型: {display_data['display_type']}")
        print(f"   取票码: {display_data['ticket_code']}")
        print(f"   二维码大小: {display_data['data_size']} bytes")
        print(f"   是否生成: {display_data['is_generated']}")
        
        print(f"\n💡 这个数据可以直接发送给主窗口的 _display_generated_qrcode 方法")
        print(f"💡 主窗口将显示包含取票码的二维码图片")
        
        return True
    else:
        print(f"❌ 二维码生成失败")
        return False

def check_generated_files():
    """检查生成的文件"""
    print("\n" + "=" * 80)
    print("📁 检查生成的文件")
    print("=" * 80)
    
    img_dir = os.path.join("data", "img")
    if os.path.exists(img_dir):
        files = [f for f in os.listdir(img_dir) if f.endswith('_取票码.png')]
        
        if files:
            print(f"📁 找到 {len(files)} 个取票码二维码文件:")
            
            for file in files:
                file_path = os.path.join(img_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   {file} ({file_size} bytes)")
            
            print(f"\n💡 您可以用手机扫描这些二维码来验证取票码内容")
            return True
        else:
            print(f"❌ 没有找到取票码二维码文件")
            return False
    else:
        print(f"❌ data/img 目录不存在")
        return False

if __name__ == "__main__":
    print("🎫 真实取票码格式测试启动")
    
    # 运行测试
    success1 = test_real_ticket_code_formats()
    success2 = test_qrcode_display_integration()
    success3 = check_generated_files()
    
    print("\n" + "=" * 80)
    print("🏁 测试完成")
    print("=" * 80)
    
    if success1 and success2 and success3:
        print("🎉 所有测试通过！")
        print("\n🎯 现在您可以:")
        print("   1. 在主程序中双击订单")
        print("   2. 系统会从订单详情获取qrCode字段")
        print("   3. 自动生成包含取票码的二维码")
        print("   4. 显示在取票码区域")
        print("   5. 保存到data/img/目录")
        print("\n📱 用手机扫描生成的二维码可以获取真实的取票码！")
    else:
        print("❌ 部分测试失败")
    
    print("=" * 80)
