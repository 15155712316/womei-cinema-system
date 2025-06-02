#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试主窗口显示功能
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_main_window_display():
    """直接测试主窗口显示功能"""
    print("=" * 80)
    print("🖥️ 直接测试主窗口显示功能")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    try:
        # 导入主窗口
        from main_modular import ModularCinemaMainWindow
        
        print("📋 创建主窗口...")
        main_window = ModularCinemaMainWindow()
        main_window.show()
        
        # 等待主窗口初始化完成后测试
        def test_display_methods():
            print("🧪 开始测试显示方法...")
            
            # 🎯 测试1：直接调用 _display_ticket_code_info
            print("\n🧪 测试1: 直接调用 _display_ticket_code_info")
            test_ticket_data = {
                'order_no': '202506021611295648804',
                'ticket_code': '2025060239828060',
                'film_name': '私家侦探',
                'show_time': '2025-06-03 10:00',
                'hall_name': '3号激光OMIS厅',
                'seat_info': '8排8座,8排9座',
                'cinema_name': '深影国际影城(佐阾虹湾购物中心店)',
                'display_type': 'ticket_code'
            }
            
            try:
                main_window._display_ticket_code_info(test_ticket_data)
                print("✅ _display_ticket_code_info 调用成功")
            except Exception as e:
                print(f"❌ _display_ticket_code_info 调用失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 🎯 测试2：通过 _on_show_qrcode 调用
            print("\n🧪 测试2: 通过 _on_show_qrcode 调用")
            try:
                main_window._on_show_qrcode(test_ticket_data)
                print("✅ _on_show_qrcode 调用成功")
            except Exception as e:
                print(f"❌ _on_show_qrcode 调用失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 🎯 测试3：检查 qr_display 属性
            print("\n🧪 测试3: 检查 qr_display 属性")
            if hasattr(main_window, 'qr_display'):
                print("✅ qr_display 属性存在")
                print(f"   类型: {type(main_window.qr_display)}")
                
                # 检查当前内容
                current_text = main_window.qr_display.text()
                print(f"   当前文本: {current_text[:100]}...")
                
                # 检查当前图片
                pixmap = main_window.qr_display.pixmap()
                if pixmap and not pixmap.isNull():
                    print(f"   当前图片: {pixmap.width()}x{pixmap.height()}")
                else:
                    print(f"   当前图片: 无")
                    
            else:
                print("❌ qr_display 属性不存在")
                
                # 查找可能的显示区域
                print("🔍 查找可能的显示区域...")
                for attr_name in dir(main_window):
                    if 'qr' in attr_name.lower() or 'display' in attr_name.lower():
                        attr_value = getattr(main_window, attr_name)
                        if hasattr(attr_value, 'setText'):  # 可能是QLabel
                            print(f"   找到可能的显示区域: {attr_name} ({type(attr_value)})")
            
            # 🎯 测试4：通过事件总线发送
            print("\n🧪 测试4: 通过事件总线发送")
            try:
                from utils.signals import event_bus
                
                # 发送测试数据
                event_bus.show_qrcode.emit(test_ticket_data)
                print("✅ 事件总线发送成功")
                
                # 等待一下，看看是否有反应
                QTimer.singleShot(1000, lambda: print("📋 事件总线发送完成，请检查界面"))
                
            except Exception as e:
                print(f"❌ 事件总线发送失败: {e}")
                import traceback
                traceback.print_exc()
            
            print("\n💡 请观察主窗口右侧取票码区域的变化")
            print("💡 如果显示正常，说明功能没问题")
            print("💡 如果显示异常，说明有其他问题")
        
        # 延迟3秒后开始测试
        QTimer.singleShot(3000, test_display_methods)
        
        print("🖥️ 主窗口已显示，3秒后将开始测试...")
        print("💡 请观察右侧取票码区域的变化")
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_window_display()
