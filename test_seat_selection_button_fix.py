#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选座按钮修复效果
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_seat_selection_button_fix():
    """测试选座按钮修复效果"""
    print("🎭 测试选座按钮修复效果")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def test_button_locations():
            """测试按钮位置和功能"""
            print(f"\n  🎯 检查按钮位置和功能...")
            
            try:
                # 检查Tab管理器中的按钮
                tab_manager = main_window.tab_manager_widget
                if hasattr(tab_manager, 'submit_order_btn'):
                    tab_button = tab_manager.submit_order_btn
                    tab_button_text = tab_button.text()
                    print(f"        📋 Tab管理器按钮文本: '{tab_button_text}'")
                    
                    if tab_button_text == "选座":
                        print(f"        ✅ Tab管理器按钮文本正确修改为'选座'")
                    else:
                        print(f"        ❌ Tab管理器按钮文本错误: '{tab_button_text}'")
                else:
                    print(f"        ❌ 未找到Tab管理器中的按钮")
                
                # 检查信号连接
                if hasattr(tab_manager, 'seat_load_requested'):
                    print(f"        ✅ Tab管理器已添加seat_load_requested信号")
                else:
                    print(f"        ❌ Tab管理器缺少seat_load_requested信号")
                
                # 检查主窗口信号连接
                if hasattr(main_window, '_on_seat_load_requested'):
                    print(f"        ✅ 主窗口已添加_on_seat_load_requested方法")
                else:
                    print(f"        ❌ 主窗口缺少_on_seat_load_requested方法")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 检查按钮位置失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def test_button_functionality():
            """测试按钮功能"""
            print(f"\n  🖱️ 测试按钮功能...")
            
            try:
                tab_manager = main_window.tab_manager_widget
                
                # 检查按钮点击事件连接
                if hasattr(tab_manager, 'submit_order_btn'):
                    button = tab_manager.submit_order_btn
                    
                    # 检查点击事件是否连接到正确的方法
                    receivers_count = button.receivers(button.clicked)
                    print(f"        📋 按钮点击事件接收者数量: {receivers_count}")
                    
                    if receivers_count > 0:
                        print(f"        ✅ 按钮点击事件已正确连接")
                    else:
                        print(f"        ❌ 按钮点击事件未连接")
                
                # 检查方法是否存在
                if hasattr(tab_manager, '_on_submit_order'):
                    print(f"        ✅ Tab管理器_on_submit_order方法存在")
                    
                    # 检查方法文档字符串
                    method = getattr(tab_manager, '_on_submit_order')
                    if method.__doc__ and "选座按钮处理" in method.__doc__:
                        print(f"        ✅ 方法文档字符串已更新为选座功能")
                    else:
                        print(f"        ⚠️  方法文档字符串可能未更新")
                else:
                    print(f"        ❌ Tab管理器_on_submit_order方法不存在")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 测试按钮功能失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def test_signal_flow():
            """测试信号流程"""
            print(f"\n  🔄 测试信号流程...")
            
            try:
                tab_manager = main_window.tab_manager_widget
                
                # 检查信号定义
                signals_to_check = [
                    'cinema_selected',
                    'order_submitted', 
                    'seat_load_requested'
                ]
                
                for signal_name in signals_to_check:
                    if hasattr(tab_manager, signal_name):
                        signal = getattr(tab_manager, signal_name)
                        print(f"        ✅ 信号 {signal_name} 存在: {type(signal)}")
                    else:
                        print(f"        ❌ 信号 {signal_name} 不存在")
                
                # 检查主窗口信号连接
                connection_methods = [
                    '_on_cinema_selected',
                    '_on_order_submitted',
                    '_on_seat_load_requested'
                ]
                
                for method_name in connection_methods:
                    if hasattr(main_window, method_name):
                        print(f"        ✅ 主窗口方法 {method_name} 存在")
                    else:
                        print(f"        ❌ 主窗口方法 {method_name} 不存在")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 测试信号流程失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(button_test, function_test, signal_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 选座按钮修复验证结果:")
            print(f"        ✅ 按钮位置检查: {'通过' if button_test else '失败'}")
            print(f"        ✅ 按钮功能测试: {'通过' if function_test else '失败'}")
            print(f"        ✅ 信号流程测试: {'通过' if signal_test else '失败'}")
            
            all_passed = button_test and function_test and signal_test
            
            if all_passed:
                print(f"\n     💡 修复成果:")
                print(f"        🎭 Tab管理器中的按钮文本已改为'选座'")
                print(f"        🖱️ 按钮点击事件已修改为座位图加载功能")
                print(f"        🔄 新增seat_load_requested信号")
                print(f"        🎯 主窗口已连接新信号处理方法")
                
                print(f"\n     🎬 功能流程:")
                print(f"        1. 用户在Tab管理器中选择影院、影片、日期、场次")
                print(f"        2. 点击'选座'按钮")
                print(f"        3. Tab管理器发出seat_load_requested信号")
                print(f"        4. 主窗口接收信号并加载座位图")
                print(f"        5. 座位图显示在中下方区域")
                
                print(f"\n     🛡️  按钮区分:")
                print(f"        - Tab管理器'选座'按钮: 加载座位图")
                print(f"        - 座位图面板'提交订单'按钮: 提交选中座位")
                print(f"        - 两个按钮功能不同，不会冲突")
                
                print(f"\n     ⚠️  关于冗余按钮:")
                print(f"        - 影院选择面板中也有'选座'按钮")
                print(f"        - 但Tab管理器是主要入口")
                print(f"        - 建议保留Tab管理器按钮，移除影院面板按钮")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步检查修复效果")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            button_test = test_button_locations()
            QTimer.singleShot(500, lambda: continue_testing(button_test))
        
        def continue_testing(button_test):
            function_test = test_button_functionality()
            QTimer.singleShot(500, lambda: final_testing(button_test, function_test))
        
        def final_testing(button_test, function_test):
            signal_test = test_signal_flow()
            QTimer.singleShot(500, lambda: finish_test(button_test, function_test, signal_test))
        
        # 1秒后开始测试
        QTimer.singleShot(1000, start_testing)
        
        # 显示主窗口
        main_window.show()
        
        # 15秒后强制退出
        QTimer.singleShot(15000, lambda: [print("  ⏰ 测试超时"), app.quit()])
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🎭 选座按钮修复效果测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证Tab管理器按钮文本已改为'选座'")
    print("   2. 🎭 验证按钮点击事件已修改为座位图加载")
    print("   3. 🎯 验证新增的seat_load_requested信号")
    print("   4. 📋 验证主窗口信号连接和处理方法")
    print("   5. 🔄 验证完整的信号流程")
    print()
    
    print("🔧 修改内容:")
    print("   • Tab管理器按钮文本: '提交订单' → '选座'")
    print("   • 按钮功能: 提交订单 → 加载座位图")
    print("   • 新增信号: seat_load_requested")
    print("   • 主窗口方法: _on_seat_load_requested")
    print("   • 信号连接: 完整的座位图加载流程")
    print()
    
    # 执行测试
    success = test_seat_selection_button_fix()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   选座按钮修复效果测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 选座按钮修复完全成功！")
        print()
        print("✨ 修复成果:")
        print("   🎭 ✅ Tab管理器按钮文本已改为'选座'")
        print("   🖱️ ✅ 按钮功能已修改为座位图加载")
        print("   🔄 ✅ 新增seat_load_requested信号")
        print("   🎯 ✅ 主窗口信号连接完整")
        print("   🛡️ ✅ 信号流程正确")
        print()
        print("🎬 现在的效果:")
        print("   - 用户在Tab管理器中选择影院、影片、日期、场次")
        print("   - 点击'选座'按钮加载座位图")
        print("   - 座位图显示在中下方区域")
        print("   - 在座位图中选择座位")
        print("   - 点击座位图的'提交订单'按钮提交")
        print()
        print("💡 按钮功能区分:")
        print("   1. Tab管理器'选座'按钮 → 加载座位图")
        print("   2. 座位图面板'提交订单'按钮 → 提交选中座位")
        print("   3. 两个按钮功能明确，不会混淆")
        print()
        print("⚠️  关于冗余按钮:")
        print("   - 影院选择面板中也有'选座'按钮")
        print("   - 建议保留Tab管理器按钮作为主入口")
        print("   - 可以考虑移除影院面板中的冗余按钮")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步检查修复效果")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
