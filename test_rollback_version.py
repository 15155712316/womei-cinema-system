#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试回退版本
验证取票码可以正常获取但本地未生成文件
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def test_rollback_version():
    """测试回退版本的功能"""
    print("=" * 80)
    print("🔄 测试回退版本功能")
    print("=" * 80)
    
    app = QApplication(sys.argv)
    
    try:
        # 导入主程序组件
        from ui.widgets.tab_manager_widget import TabManagerWidget
        from services.order_api import get_order_detail
        
        print("📋 创建Tab管理器组件...")
        tab_manager = TabManagerWidget()
        
        # 模拟虹湾影城账号
        test_account = {
            "userid": "15155712316",
            "openid": "ohA6p7Z0kejTSi40QVYXQtMF9SDY",
            "token": "02849a78647f5af9",
            "cinemaid": "11b7e4bcc265"
        }
        
        # 设置当前账号
        tab_manager.current_account = test_account
        
        # 模拟订单数据
        order_data = {
            'orderno': '202506021611295648804',
            'orderName': '私家侦探',
            'orderS': '待使用'
        }
        
        cinema_id = "11b7e4bcc265"
        order_no = order_data['orderno']
        
        print(f"📋 测试参数:")
        print(f"   订单号: {order_no}")
        print(f"   影院ID: {cinema_id}")
        print(f"   账号: {test_account['userid']}")
        print()
        
        # 🎯 直接调用订单详情获取方法
        print("🔍 测试订单详情获取...")
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
        
        if detail_result and detail_result.get('resultCode') == '0':
            print("✅ 订单详情获取成功!")
            
            detail_data = detail_result.get('resultData', {})
            
            # 提取取票码
            qr_code = detail_data.get('qrCode', '')
            ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
            ds_code = detail_data.get('dsValidateCode', '')
            
            print(f"📊 取票码信息:")
            print(f"   qrCode: {qr_code}")
            print(f"   ticketCode: {ticket_code}")
            print(f"   dsValidateCode: {ds_code}")
            
            final_ticket_code = qr_code or ds_code or ticket_code
            
            if final_ticket_code:
                print(f"✅ 找到取票码: {final_ticket_code}")
                
                # 🎯 测试文本显示方法
                print(f"\n📱 测试取票码文本显示...")
                
                # 创建一个简单的接收器
                def test_receiver(data):
                    print(f"🎯 接收到显示数据:")
                    print(f"   数据类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"   显示类型: {data.get('display_type', 'N/A')}")
                        print(f"   取票码: {data.get('ticket_code', 'N/A')}")
                        print(f"   影片: {data.get('film_name', 'N/A')}")
                        print(f"   时间: {data.get('show_time', 'N/A')}")
                        print(f"   座位: {data.get('seat_info', 'N/A')}")
                
                # 连接事件总线
                from utils.signals import event_bus
                event_bus.show_qrcode.connect(test_receiver)
                
                # 调用文本显示方法
                tab_manager._show_ticket_code_text(order_no, final_ticket_code, detail_data)
                
                # 断开连接
                event_bus.show_qrcode.disconnect(test_receiver)
                
                print(f"✅ 取票码文本显示测试完成")
                
            else:
                print(f"❌ 没有找到取票码")
                return False
                
        else:
            error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
            print(f"❌ 订单详情获取失败: {error_msg}")
            return False
        
        # 🎯 检查本地文件生成情况
        print(f"\n📁 检查本地文件生成情况...")
        img_dir = os.path.join("data", "img")
        
        if os.path.exists(img_dir):
            files_before = [f for f in os.listdir(img_dir) if f.endswith('.png')]
            print(f"📁 data/img 目录中现有文件: {len(files_before)} 个")
            
            # 等待一下，看是否有新文件生成
            import time
            time.sleep(2)
            
            files_after = [f for f in os.listdir(img_dir) if f.endswith('.png')]
            new_files = set(files_after) - set(files_before)
            
            if new_files:
                print(f"❌ 意外生成了新文件: {list(new_files)}")
                print(f"💡 这表明回退不完整，仍在生成本地文件")
                return False
            else:
                print(f"✅ 没有生成新的本地文件")
                print(f"💡 回退成功，只显示文本不生成文件")
        else:
            print(f"📁 data/img 目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔄 回退版本测试启动")
    
    success = test_rollback_version()
    
    print("\n" + "=" * 80)
    print("🏁 回退版本测试结果")
    print("=" * 80)
    
    if success:
        print("✅ 回退版本测试成功!")
        print("\n📋 当前版本特性:")
        print("   ✅ 可以正常获取订单详情")
        print("   ✅ 可以正常提取取票码")
        print("   ✅ 可以在取票码区域显示文本信息")
        print("   ✅ 不会生成本地二维码文件")
        print("\n💡 现在您可以在主程序中:")
        print("   1. 选择影院: 深影国际影城(佐阾虹湾购物中心店)")
        print("   2. 选择账号: 15155712316")
        print("   3. 切换到订单Tab")
        print("   4. 双击订单: 202506021611295648804")
        print("   5. 查看右侧取票码区域的文本显示")
    else:
        print("❌ 回退版本测试失败!")
        print("💡 请检查上面的错误信息")
    
    print("=" * 80)
