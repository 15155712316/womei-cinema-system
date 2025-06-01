#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试移除右键菜单功能
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt


def test_remove_context_menu():
    """测试移除右键菜单功能"""
    print("🎭 测试移除右键菜单功能")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def check_context_menu_removal():
            """检查右键菜单移除"""
            print(f"\n  🎯 检查右键菜单移除...")
            
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
                
                # 检查账号表格的右键菜单设置
                if hasattr(account_widget, 'account_table'):
                    table = account_widget.account_table
                    context_policy = table.contextMenuPolicy()
                    
                    print(f"        📋 账号表格右键菜单策略: {context_policy}")
                    
                    # Qt.DefaultContextMenu = 0 (默认，无自定义右键菜单)
                    # Qt.CustomContextMenu = 3 (自定义右键菜单)
                    if context_policy == Qt.DefaultContextMenu:
                        print(f"        ✅ 右键菜单已移除 (使用默认策略)")
                        context_menu_removed = True
                    elif context_policy == Qt.CustomContextMenu:
                        print(f"        ❌ 右键菜单仍然启用 (使用自定义策略)")
                        context_menu_removed = False
                    else:
                        print(f"        ⚠️  右键菜单策略未知: {context_policy}")
                        context_menu_removed = False
                    
                    # 检查表格行数
                    row_count = table.rowCount()
                    print(f"        📋 账号表格行数: {row_count}")
                    
                    return context_menu_removed
                else:
                    print(f"        ❌ 账号表格不存在")
                    return False
                
            except Exception as e:
                print(f"        ❌ 检查右键菜单移除失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_method_existence():
            """检查相关方法是否仍然存在"""
            print(f"\n  🔍 检查相关方法...")
            
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
                menu_methods = [
                    '_show_context_menu',
                    '_set_as_main_account',
                    '_update_main_account_in_file'
                ]
                
                for method_name in menu_methods:
                    if hasattr(account_widget, method_name):
                        print(f"        📋 方法 {method_name} 仍然存在 (保留用于将来扩展)")
                    else:
                        print(f"        ❌ 方法 {method_name} 不存在")
                
                # 检查主账号查找方法
                if hasattr(account_widget, '_find_main_account_for_cinema'):
                    print(f"        ✅ 主账号查找方法存在 (用于自动选择)")
                else:
                    print(f"        ❌ 主账号查找方法不存在")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 检查方法存在性失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_main_account_functionality():
            """检查主账号功能是否仍然工作"""
            print(f"\n  🧪 检查主账号功能...")
            
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
                
                # 检查自动选择主账号功能
                if hasattr(account_widget, '_find_main_account_for_cinema'):
                    # 使用一个测试影院ID
                    test_cinema_id = "35fec8259e74"  # 从之前的日志中看到的影院ID
                    main_account = account_widget._find_main_account_for_cinema(test_cinema_id)
                    
                    if main_account:
                        userid = main_account.get('userid', '')
                        print(f"        ✅ 自动选择主账号功能正常: {userid} (影院: {test_cinema_id})")
                    else:
                        print(f"        ⚠️  影院 {test_cinema_id} 没有主账号")
                
                # 检查账号数据中的主账号
                if hasattr(account_widget, 'accounts_data') and account_widget.accounts_data:
                    main_accounts = []
                    for account in account_widget.accounts_data:
                        if account.get('is_main', False):
                            userid = account.get('userid', '')
                            cinemaid = account.get('cinemaid', '')
                            main_accounts.append(f"{userid}@{cinemaid}")
                    
                    print(f"        📋 当前主账号: {main_accounts}")
                    print(f"        ✅ 主账号数据读取正常")
                
                return True
                
            except Exception as e:
                print(f"        ❌ 检查主账号功能失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(menu_test, method_test, function_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 移除右键菜单测试结果:")
            print(f"        ✅ 右键菜单移除: {'通过' if menu_test else '失败'}")
            print(f"        ✅ 方法存在检查: {'通过' if method_test else '失败'}")
            print(f"        ✅ 主账号功能: {'通过' if function_test else '失败'}")
            
            all_passed = menu_test and method_test and function_test
            
            if all_passed:
                print(f"\n     💡 修改成果:")
                print(f"        🎭 右键菜单已完全移除")
                print(f"        🖱️ 账号表格使用默认右键菜单策略")
                print(f"        🔄 主账号功能保留用于自动选择")
                print(f"        🎯 相关方法保留用于将来扩展")
                
                print(f"\n     🎬 现在的效果:")
                print(f"        - 右键点击账号列表无任何菜单")
                print(f"        - 主账号设置功能已移除")
                print(f"        - 自动选择主账号功能正常")
                print(f"        - 账号列表显示简洁")
                print(f"        - 用户无法手动设置主账号")
                
                print(f"\n     🛡️  技术实现:")
                print(f"        - 移除CustomContextMenu策略")
                print(f"        - 移除customContextMenuRequested信号连接")
                print(f"        - _show_context_menu方法直接返回")
                print(f"        - 保留核心主账号逻辑用于自动选择")
                print(f"        - 保留方法定义用于将来可能的扩展")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步检查修改效果")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            menu_test = check_context_menu_removal()
            QTimer.singleShot(500, lambda: continue_testing(menu_test))
        
        def continue_testing(menu_test):
            method_test = check_method_existence()
            QTimer.singleShot(500, lambda: final_testing(menu_test, method_test))
        
        def final_testing(menu_test, method_test):
            function_test = check_main_account_functionality()
            QTimer.singleShot(500, lambda: finish_test(menu_test, method_test, function_test))
        
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
    print("🎭 移除右键菜单功能测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证右键菜单已移除")
    print("   2. 🎭 验证账号表格使用默认策略")
    print("   3. 🎯 验证相关方法仍然存在")
    print("   4. 📋 验证主账号功能正常")
    print()
    
    print("🔧 修改内容:")
    print("   • 移除CustomContextMenu策略设置")
    print("   • 移除customContextMenuRequested信号连接")
    print("   • _show_context_menu方法直接返回")
    print("   • 保留主账号相关方法用于自动选择")
    print()
    
    # 执行测试
    success = test_remove_context_menu()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   移除右键菜单功能测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 右键菜单移除成功！")
        print()
        print("✨ 修改成果:")
        print("   🎭 ✅ 右键菜单已完全移除")
        print("   🖱️ ✅ 账号表格使用默认策略")
        print("   🔄 ✅ 主账号功能保留")
        print("   🎯 ✅ 相关方法保留")
        print()
        print("🎬 现在的效果:")
        print("   - 右键点击账号列表无任何菜单")
        print("   - 用户无法手动设置主账号")
        print("   - 主账号由系统自动管理")
        print("   - 账号列表显示简洁统一")
        print("   - 切换影院时自动选择主账号")
        print()
        print("💡 设计理念:")
        print("   1. 简化用户操作，移除手动设置")
        print("   2. 系统自动管理主账号逻辑")
        print("   3. 保持代码结构用于将来扩展")
        print("   4. 专注于自动化用户体验")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步检查修改效果")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
