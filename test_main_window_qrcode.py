#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主窗口二维码显示功能
直接调用主窗口的显示方法
"""

import sys
from PyQt5.QtWidgets import QApplication
from utils.qrcode_generator import generate_ticket_qrcode
from utils.signals import event_bus

def test_main_window_qrcode():
    """测试主窗口二维码显示"""
    print("=" * 80)
    print("🧪 测试主窗口二维码显示功能")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口
        from main_modular import ModularCinemaMainWindow
        
        print("📋 创建主窗口...")
        main_window = ModularCinemaMainWindow()
        
        # 不显示登录窗口，直接测试二维码功能
        print("📋 跳过登录，直接测试二维码显示...")
        
        # 生成测试二维码
        test_ticket_code = "TEST123456789"
        test_order_info = {
            'filmName': '测试影片名称',
            'cinemaName': '测试影院名称',
            'showTime': '2025-06-02 20:00',
            'seatInfo': '测试座位',
            'hallName': '测试影厅'
        }
        
        print(f"📋 生成测试二维码...")
        print(f"   取票码: {test_ticket_code}")
        
        qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
        
        if qr_bytes:
            print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
            
            # 创建测试数据
            test_data = {
                'order_no': 'TEST_ORDER_123',
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
            
            print(f"📤 准备测试数据:")
            print(f"   显示类型: {test_data['display_type']}")
            print(f"   取票码: {test_data['ticket_code']}")
            print(f"   数据大小: {test_data['data_size']} bytes")
            
            # 方法1：直接调用主窗口的显示方法
            print(f"\n🧪 方法1: 直接调用 _on_show_qrcode 方法...")
            try:
                main_window._on_show_qrcode(test_data)
                print(f"✅ 直接调用成功")
            except Exception as e:
                print(f"❌ 直接调用失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 方法2：通过事件总线发送
            print(f"\n🧪 方法2: 通过事件总线发送...")
            try:
                event_bus.show_qrcode.emit(test_data)
                print(f"✅ 事件总线发送成功")
            except Exception as e:
                print(f"❌ 事件总线发送失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 方法3：测试文本显示
            print(f"\n🧪 方法3: 测试文本显示...")
            try:
                text_data = {
                    'order_no': 'TEST_ORDER_456',
                    'ticket_code': 'TEXT_TEST_789',
                    'film_name': '文本测试影片',
                    'show_time': '2025-06-02 21:00',
                    'hall_name': '文本测试影厅',
                    'seat_info': '文本测试座位',
                    'cinema_name': '文本测试影院',
                    'display_type': 'ticket_code'
                }
                
                main_window._on_show_qrcode(text_data)
                print(f"✅ 文本显示测试成功")
            except Exception as e:
                print(f"❌ 文本显示测试失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 检查主窗口是否有qr_display属性
            print(f"\n🔍 检查主窗口qr_display属性...")
            if hasattr(main_window, 'qr_display'):
                print(f"✅ qr_display 属性存在")
                print(f"   类型: {type(main_window.qr_display)}")
                print(f"   当前文本: {main_window.qr_display.text()[:50]}...")
                
                # 检查是否有图片
                pixmap = main_window.qr_display.pixmap()
                if pixmap and not pixmap.isNull():
                    print(f"   当前图片: {pixmap.width()}x{pixmap.height()}")
                else:
                    print(f"   当前图片: 无")
            else:
                print(f"❌ qr_display 属性不存在")
                
                # 查找可能的显示区域
                print(f"🔍 查找可能的显示区域...")
                for attr_name in dir(main_window):
                    if 'qr' in attr_name.lower() or 'display' in attr_name.lower():
                        attr_value = getattr(main_window, attr_name)
                        print(f"   {attr_name}: {type(attr_value)}")
            
            print(f"\n💡 如果要查看实际效果，请运行主程序并双击订单")
            
        else:
            print(f"❌ 二维码生成失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("🏁 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    test_main_window_qrcode()
