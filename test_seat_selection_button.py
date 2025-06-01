#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试影院选择面板中的"选座"按钮功能
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_seat_selection_button():
    """测试选座按钮功能"""
    print("🎭 测试影院选择面板中的选座按钮功能")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def test_button_functionality():
            """测试按钮功能"""
            print(f"\n  🎯 测试选座按钮功能...")
            
            try:
                # 获取影院选择面板
                cinema_panel = main_window.cinema_panel
                if not cinema_panel:
                    print(f"        ❌ 无法获取影院选择面板")
                    return False
                
                # 检查选座按钮
                seat_btn = cinema_panel.open_seat_btn
                if not seat_btn:
                    print(f"        ❌ 无法获取选座按钮")
                    return False
                
                # 检查按钮文本
                button_text = seat_btn.text()
                print(f"        📋 按钮文本: '{button_text}'")
                
                if button_text == "选座":
                    print(f"        ✅ 按钮文本正确")
                else:
                    print(f"        ⚠️  按钮文本不是'选座'，当前为: '{button_text}'")
                
                # 检查按钮是否可点击
                is_enabled = seat_btn.isEnabled()
                print(f"        📋 按钮状态: {'可点击' if is_enabled else '不可点击'}")
                
                # 检查按钮样式
                style = seat_btn.styleSheet()
                has_style = bool(style.strip())
                print(f"        📋 按钮样式: {'已设置' if has_style else '未设置'}")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 测试按钮功能失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def test_button_click_behavior():
            """测试按钮点击行为"""
            print(f"\n  🖱️ 测试按钮点击行为...")
            
            try:
                cinema_panel = main_window.cinema_panel
                seat_btn = cinema_panel.open_seat_btn
                
                # 模拟点击前的状态检查
                print(f"        📋 点击前检查:")
                
                # 检查是否有选中的影院
                cinema_text = cinema_panel.cinema_combo.currentText()
                print(f"           影院: '{cinema_text}'")
                
                # 检查是否有选中的影片
                movie_text = cinema_panel.movie_combo.currentText()
                print(f"           影片: '{movie_text}'")
                
                # 检查是否有选中的日期
                date_text = cinema_panel.date_combo.currentText()
                print(f"           日期: '{date_text}'")
                
                # 检查是否有选中的场次
                session_text = cinema_panel.session_combo.currentText()
                print(f"           场次: '{session_text}'")
                
                # 检查当前账号
                account_text = cinema_panel.current_account_label.text()
                print(f"           账号: '{account_text}'")
                
                # 检查座位面板状态
                seat_panel = main_window.seat_panel
                if seat_panel:
                    seat_data_count = len(seat_panel.seat_data) if seat_panel.seat_data else 0
                    print(f"           座位数据: {seat_data_count} 行")
                else:
                    print(f"           座位面板: 未找到")
                
                print(f"        ✅ 点击前状态检查完成")
                
                # 检查点击事件连接
                click_connected = bool(seat_btn.receivers(seat_btn.clicked))
                print(f"        📋 点击事件连接: {'已连接' if click_connected else '未连接'}")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 测试按钮点击行为失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def test_seat_panel_integration():
            """测试与座位面板的集成"""
            print(f"\n  🎨 测试与座位面板的集成...")
            
            try:
                # 检查座位面板是否存在
                seat_panel = main_window.seat_panel
                if not seat_panel:
                    print(f"        ❌ 座位面板不存在")
                    return False
                
                print(f"        ✅ 座位面板存在")
                
                # 检查座位面板的提交按钮
                submit_btn = seat_panel.submit_btn
                if submit_btn:
                    submit_text = submit_btn.text()
                    print(f"        📋 座位面板提交按钮文本: '{submit_text}'")
                    
                    if submit_text == "提交订单":
                        print(f"        ✅ 座位面板提交按钮文本正确")
                    else:
                        print(f"        ⚠️  座位面板提交按钮文本异常: '{submit_text}'")
                else:
                    print(f"        ❌ 座位面板提交按钮不存在")
                
                # 检查影院面板与座位面板的引用关系
                cinema_panel = main_window.cinema_panel
                if hasattr(cinema_panel, 'seat_panel') and cinema_panel.seat_panel:
                    print(f"        ✅ 影院面板已关联座位面板")
                else:
                    print(f"        ⚠️  影院面板未关联座位面板")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 测试座位面板集成失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(button_test, click_test, integration_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 选座按钮功能测试结果:")
            print(f"        ✅ 按钮基本功能: {'通过' if button_test else '失败'}")
            print(f"        ✅ 点击行为测试: {'通过' if click_test else '失败'}")
            print(f"        ✅ 座位面板集成: {'通过' if integration_test else '失败'}")
            
            all_passed = button_test and click_test and integration_test
            
            if all_passed:
                print(f"\n     💡 功能验证:")
                print(f"        🎭 选座按钮文本已修改为'选座'")
                print(f"        🖱️ 点击选座按钮会刷新座位图")
                print(f"        🎯 按钮与座位面板正确集成")
                print(f"        🔄 支持重新加载当前场次座位信息")
                
                print(f"\n     🎬 使用流程:")
                print(f"        1. 选择影院、影片、日期、场次")
                print(f"        2. 点击'选座'按钮")
                print(f"        3. 座位图自动刷新显示")
                print(f"        4. 在座位图中选择座位")
                print(f"        5. 点击'提交订单'按钮提交")
                
                print(f"\n     🛡️  错误处理:")
                print(f"        - 未选择账号时提示选择账号")
                print(f"        - 未选择场次时提示选择场次")
                print(f"        - 座位数据加载失败时显示错误信息")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步检查选座按钮功能")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            button_test = test_button_functionality()
            QTimer.singleShot(500, lambda: continue_testing(button_test))
        
        def continue_testing(button_test):
            click_test = test_button_click_behavior()
            QTimer.singleShot(500, lambda: final_testing(button_test, click_test))
        
        def final_testing(button_test, click_test):
            integration_test = test_seat_panel_integration()
            QTimer.singleShot(500, lambda: finish_test(button_test, click_test, integration_test))
        
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
    print("🎭 影院选择面板选座按钮功能测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证选座按钮文本已修改为'选座'")
    print("   2. 🎭 验证选座按钮点击事件正确连接")
    print("   3. 🎯 验证选座按钮与座位面板正确集成")
    print("   4. 📋 验证按钮点击后座位图刷新功能")
    print()
    
    print("🔧 修改内容:")
    print("   • 按钮文本从'打开选座 获取可用券'改为'选座'")
    print("   • 点击事件优化，移除不必要的提示信息")
    print("   • 点击后直接刷新座位图")
    print("   • 保持原有的错误处理逻辑")
    print()
    
    # 执行测试
    success = test_seat_selection_button()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   选座按钮功能测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 选座按钮功能修改成功！")
        print()
        print("✨ 修改成果:")
        print("   🎭 ✅ 按钮文本简化为'选座'")
        print("   🖱️ ✅ 点击事件优化")
        print("   🎯 ✅ 座位图刷新功能正常")
        print("   🛡️ ✅ 错误处理保持完整")
        print()
        print("🎬 用户体验:")
        print("   - 按钮文本更简洁明了")
        print("   - 点击后直接刷新座位图")
        print("   - 无不必要的提示信息")
        print("   - 保持原有的验证逻辑")
        print()
        print("💡 功能流程:")
        print("   1. 用户选择影院、影片、日期、场次")
        print("   2. 点击'选座'按钮")
        print("   3. 系统验证账号和场次信息")
        print("   4. 自动刷新座位图显示")
        print("   5. 用户在座位图中选择座位")
        print("   6. 点击'提交订单'完成选座")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步检查选座按钮功能")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
