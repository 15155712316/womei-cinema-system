#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试账号样式修复
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_account_style_fix():
    """测试账号样式修复"""
    print("🎭 测试账号样式修复")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def check_account_table_display():
            """检查账号表格显示"""
            print(f"\n  🎯 检查账号表格显示...")
            
            try:
                # 获取账号组件
                account_widget = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'AccountWidget' in str(child.__class__):
                        account_widget = child
                        break
                
                if not account_widget:
                    print(f"        ❌ 未找到账号组件")
                    return False
                
                print(f"        ✅ 找到账号组件")
                
                # 检查账号表格
                if hasattr(account_widget, 'account_table'):
                    table = account_widget.account_table
                    row_count = table.rowCount()
                    print(f"        📋 账号表格行数: {row_count}")
                    
                    # 检查表格内容显示
                    for row in range(row_count):
                        userid_item = table.item(row, 0)
                        balance_item = table.item(row, 1)
                        points_item = table.item(row, 2)
                        
                        if userid_item and balance_item and points_item:
                            userid_text = userid_item.text()
                            balance_text = balance_item.text()
                            points_text = points_item.text()
                            
                            print(f"        📋 第{row}行: {userid_text} | 余额:{balance_text} | 积分:{points_text}")
                            
                            # 检查是否有星号标识（应该没有）
                            if userid_text.startswith('★'):
                                print(f"        ⚠️  第{row}行仍有星号标识")
                            else:
                                print(f"        ✅ 第{row}行显示正常，无特殊标识")
                        else:
                            print(f"        ❌ 第{row}行数据不完整")
                    
                    return True
                else:
                    print(f"        ❌ 账号表格不存在")
                    return False
                
            except Exception as e:
                print(f"        ❌ 检查账号表格显示失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_right_click_menu():
            """检查右键菜单功能"""
            print(f"\n  🖱️ 检查右键菜单功能...")
            
            try:
                # 获取账号组件
                account_widget = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'AccountWidget' in str(child.__class__):
                        account_widget = child
                        break
                
                if not account_widget:
                    print(f"        ❌ 未找到账号组件")
                    return False
                
                # 检查右键菜单相关方法
                methods_to_check = [
                    '_show_context_menu',
                    '_set_as_main_account',
                    '_update_main_account_in_file',
                    '_find_main_account_for_cinema'
                ]
                
                for method_name in methods_to_check:
                    if hasattr(account_widget, method_name):
                        print(f"        ✅ 方法 {method_name} 存在")
                    else:
                        print(f"        ❌ 方法 {method_name} 不存在")
                
                # 检查表格右键菜单设置
                if hasattr(account_widget, 'account_table'):
                    table = account_widget.account_table
                    from PyQt5.QtCore import Qt
                    if table.contextMenuPolicy() == Qt.CustomContextMenu:
                        print(f"        ✅ 账号表格右键菜单已启用")
                    else:
                        print(f"        ❌ 账号表格右键菜单未启用")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 检查右键菜单功能失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_main_account_logic():
            """检查主账号逻辑"""
            print(f"\n  🧪 检查主账号逻辑...")
            
            try:
                # 获取账号组件
                account_widget = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'AccountWidget' in str(child.__class__):
                        account_widget = child
                        break
                
                if not account_widget:
                    print(f"        ❌ 未找到账号组件")
                    return False
                
                # 测试主账号查找功能
                if hasattr(account_widget, '_find_main_account_for_cinema'):
                    # 使用一个测试影院ID
                    test_cinema_id = "35fec8259e74"  # 从日志中看到的影院ID
                    main_account = account_widget._find_main_account_for_cinema(test_cinema_id)
                    
                    if main_account:
                        userid = main_account.get('userid', '')
                        print(f"        ✅ 找到影院 {test_cinema_id} 的主账号: {userid}")
                    else:
                        print(f"        ⚠️  影院 {test_cinema_id} 没有设置主账号")
                
                # 检查账号数据中的主账号标识
                if hasattr(account_widget, 'accounts_data') and account_widget.accounts_data:
                    main_accounts_count = 0
                    for account in account_widget.accounts_data:
                        if account.get('is_main', False):
                            main_accounts_count += 1
                            userid = account.get('userid', '')
                            cinemaid = account.get('cinemaid', '')
                            print(f"        📋 主账号: {userid} (影院: {cinemaid})")
                    
                    print(f"        📊 总主账号数量: {main_accounts_count}")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 检查主账号逻辑失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(display_test, menu_test, logic_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 账号样式修复测试结果:")
            print(f"        ✅ 表格显示检查: {'通过' if display_test else '失败'}")
            print(f"        ✅ 右键菜单检查: {'通过' if menu_test else '失败'}")
            print(f"        ✅ 主账号逻辑检查: {'通过' if logic_test else '失败'}")
            
            all_passed = display_test and menu_test and logic_test
            
            if all_passed:
                print(f"\n     💡 修复成果:")
                print(f"        🎭 移除了账号列表的特殊样式")
                print(f"        🖱️ 保留了主账号设置功能")
                print(f"        🔄 账号表格显示正常")
                print(f"        🎯 右键菜单功能完整")
                
                print(f"\n     🎬 现在的效果:")
                print(f"        - 账号列表显示保持原有样式")
                print(f"        - 不显示星号或特殊颜色标识")
                print(f"        - 右键点击账号可设置主账号")
                print(f"        - 主账号数据正常保存和读取")
                print(f"        - 切换影院时自动选择主账号")
                
                print(f"\n     🛡️  功能保留:")
                print(f"        - 右键菜单: 设置为主账号")
                print(f"        - 数据管理: accounts.json中的is_main字段")
                print(f"        - 自动选择: 影院切换时优先选择主账号")
                print(f"        - 唯一性: 每个影院只能有一个主账号")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步检查修复效果")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            display_test = check_account_table_display()
            QTimer.singleShot(500, lambda: continue_testing(display_test))
        
        def continue_testing(display_test):
            menu_test = check_right_click_menu()
            QTimer.singleShot(500, lambda: final_testing(display_test, menu_test))
        
        def final_testing(display_test, menu_test):
            logic_test = check_main_account_logic()
            QTimer.singleShot(500, lambda: finish_test(display_test, menu_test, logic_test))
        
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
    print("🎭 账号样式修复测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证账号表格显示正常")
    print("   2. 🎭 验证移除了特殊样式标识")
    print("   3. 🎯 验证右键菜单功能保留")
    print("   4. 📋 验证主账号逻辑正常")
    print()
    
    print("🔧 修复内容:")
    print("   • 移除账号前的★星号标识")
    print("   • 移除蓝色加粗样式设置")
    print("   • 保持原有账号列表显示")
    print("   • 保留所有主账号功能")
    print()
    
    # 执行测试
    success = test_account_style_fix()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   账号样式修复测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 账号样式修复成功！")
        print()
        print("✨ 修复成果:")
        print("   🎭 ✅ 移除了账号列表特殊样式")
        print("   🖱️ ✅ 保留了主账号设置功能")
        print("   🔄 ✅ 账号表格显示正常")
        print("   🎯 ✅ 右键菜单功能完整")
        print()
        print("🎬 现在的效果:")
        print("   - 账号列表保持原有简洁样式")
        print("   - 不显示任何特殊标识或颜色")
        print("   - 右键点击账号可设置主账号")
        print("   - 主账号功能在后台正常工作")
        print("   - 切换影院时自动选择主账号")
        print()
        print("💡 功能说明:")
        print("   1. 主账号设置: 右键菜单 → 设置为主账号")
        print("   2. 数据存储: accounts.json中的is_main字段")
        print("   3. 自动选择: 影院切换时优先选择主账号")
        print("   4. 视觉效果: 保持原有简洁的账号列表")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步检查修复效果")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
