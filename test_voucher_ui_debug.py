#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券UI组件详细调试测试
用于捕获券组件加载过程中的所有问题
"""

import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

def test_voucher_widget_detailed():
    """详细测试券组件"""
    print("🧪 开始详细测试券组件...")
    
    app = QApplication(sys.argv)
    
    try:
        # 1. 创建券组件
        print("\n📋 步骤1: 创建券组件")
        from ui.widgets.voucher_widget import VoucherWidget
        voucher_widget = VoucherWidget()
        print("✅ 券组件创建成功")
        
        # 2. 设置账号信息
        print("\n📋 步骤2: 设置账号信息")
        test_account = {
            'phone': '15155712316',
            'token': 'c33d6b500b34c87b71ac8fad4cfb6769'
        }
        cinema_id = '400028'
        
        voucher_widget.set_account_info(test_account, cinema_id)
        print("✅ 账号信息设置成功")
        print(f"   当前账号: {voucher_widget.current_account}")
        print(f"   当前影院: {voucher_widget.current_cinema_id}")
        
        # 3. 添加信号监听
        print("\n📋 步骤3: 添加信号监听")
        
        def on_data_loaded(data):
            print(f"🎉 数据加载信号触发: {type(data)}")
            print(f"   数据keys: {list(data.keys()) if isinstance(data, dict) else '不是字典'}")
            if isinstance(data, dict) and 'vouchers' in data:
                print(f"   券数量: {len(data['vouchers'])}")
        
        def on_error_occurred(error_msg):
            print(f"❌ 错误信号触发: {error_msg}")
        
        def on_progress_updated(message):
            print(f"📊 进度信号触发: {message}")
        
        # 连接信号（注意：这些信号是在加载线程中发出的）
        # 我们需要在刷新之前连接
        
        # 4. 手动触发刷新
        print("\n📋 步骤4: 手动触发刷新")
        
        # 检查刷新前的状态
        print(f"   刷新前券数据数量: {len(voucher_widget.vouchers_data)}")
        
        # 触发刷新
        voucher_widget.refresh_vouchers()
        print("✅ 刷新触发成功")
        
        # 5. 等待异步操作完成
        print("\n📋 步骤5: 等待异步操作完成")
        
        # 使用QTimer来检查状态
        check_count = 0
        max_checks = 10
        
        def check_status():
            nonlocal check_count
            check_count += 1
            
            print(f"   检查 {check_count}/{max_checks}:")
            print(f"     券数据数量: {len(voucher_widget.vouchers_data)}")
            print(f"     加载线程状态: {voucher_widget.load_thread.isRunning() if voucher_widget.load_thread else '无线程'}")
            print(f"     状态标签: {voucher_widget.status_label.text()}")
            print(f"     刷新按钮: {voucher_widget.refresh_btn.text()}")
            
            if check_count >= max_checks or len(voucher_widget.vouchers_data) > 0:
                app.quit()
        
        timer = QTimer()
        timer.timeout.connect(check_status)
        timer.start(1000)  # 每秒检查一次
        
        # 6. 运行事件循环
        print("\n📋 步骤6: 运行事件循环")
        app.exec_()
        
        # 7. 最终检查
        print("\n📋 步骤7: 最终检查")
        print(f"   最终券数据数量: {len(voucher_widget.vouchers_data)}")
        print(f"   最终状态: {voucher_widget.status_label.text()}")
        
        if voucher_widget.vouchers_data:
            first_voucher = voucher_widget.vouchers_data[0]
            print(f"   第一张券: {first_voucher.get('voucher_name', '未知')}")
            print("🎉 券组件测试成功！")
        else:
            print("❌ 券组件没有加载到数据")
            
            # 尝试直接测试API
            print("\n🔍 直接测试API...")
            from api.voucher_api import get_valid_vouchers
            result = get_valid_vouchers(cinema_id, test_account['token'])
            if result['success']:
                print(f"   API直接调用成功，券数量: {len(result['data']['vouchers'])}")
            else:
                print(f"   API直接调用失败: {result['message']}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        app.quit()

def main():
    """主函数"""
    print("🚀 券UI组件详细调试测试")
    print("=" * 60)
    
    test_voucher_widget_detailed()

if __name__ == "__main__":
    main()
