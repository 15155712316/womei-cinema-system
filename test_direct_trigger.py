#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接触发主程序二维码显示测试
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from utils.qrcode_generator import generate_ticket_qrcode
from utils.signals import event_bus

def test_direct_trigger():
    """直接触发主程序二维码显示"""
    print("=" * 80)
    print("🎯 直接触发主程序二维码显示测试")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口
        from main_modular import ModularCinemaMainWindow
        
        print("📋 创建主窗口...")
        main_window = ModularCinemaMainWindow()
        main_window.show()
        
        # 等待主窗口初始化完成
        def trigger_qrcode():
            print("🎯 开始触发二维码显示...")
            
            # 生成测试二维码
            test_ticket_code = "DIRECT_TEST_123456"
            test_order_info = {
                'filmName': '直接触发测试影片',
                'cinemaName': '深影国际影城(佐阾虹湾购物中心店)',
                'showTime': '2025-06-02 20:00',
                'seatInfo': '直接测试座位',
                'hallName': '直接测试影厅'
            }
            
            print(f"📋 生成测试二维码...")
            qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
            
            if qr_bytes:
                print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
                
                # 创建测试数据
                test_data = {
                    'order_no': 'DIRECT_TEST_ORDER',
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
                
                print(f"📤 发送测试数据到主窗口...")
                print(f"   显示类型: {test_data['display_type']}")
                print(f"   取票码: {test_data['ticket_code']}")
                print(f"   数据大小: {test_data['data_size']} bytes")
                
                # 通过事件总线发送
                event_bus.show_qrcode.emit(test_data)
                
                print(f"✅ 测试数据已发送")
                print(f"💡 请查看主窗口右侧取票码区域是否显示二维码")
                
            else:
                print(f"❌ 二维码生成失败")
        
        # 延迟3秒后触发
        QTimer.singleShot(3000, trigger_qrcode)
        
        print("🖥️ 主窗口已显示，3秒后将自动触发二维码显示...")
        print("💡 请观察右侧取票码区域的变化")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_trigger()
