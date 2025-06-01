#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试券列表显示问题
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def debug_coupon_list():
    """调试券列表显示问题"""
    print("🔍 调试券列表显示问题")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def debug_coupon_components():
            """调试券列表组件"""
            print(f"\n  🔍 调试券列表组件...")
            
            # 检查主窗口的券列表相关属性
            print(f"     📋 主窗口属性检查:")
            print(f"        hasattr(main_window, 'coupon_list'): {hasattr(main_window, 'coupon_list')}")
            print(f"        hasattr(main_window, 'tab_manager_widget'): {hasattr(main_window, 'tab_manager_widget')}")
            
            if hasattr(main_window, 'tab_manager_widget'):
                tab_manager = main_window.tab_manager_widget
                print(f"        tab_manager_widget 类型: {type(tab_manager)}")
                print(f"        hasattr(tab_manager, 'coupon_list'): {hasattr(tab_manager, 'coupon_list')}")
                
                if hasattr(tab_manager, 'coupon_list'):
                    coupon_list = tab_manager.coupon_list
                    print(f"        coupon_list 类型: {type(coupon_list)}")
                    print(f"        coupon_list 是否为None: {coupon_list is None}")
                    print(f"        coupon_list 是否有效: {bool(coupon_list)}")
                    
                    if coupon_list:
                        print(f"        coupon_list 项目数量: {coupon_list.count()}")
                        print(f"        coupon_list 是否可见: {coupon_list.isVisible()}")
                        print(f"        coupon_list 是否启用: {coupon_list.isEnabled()}")
                        
                        # 尝试添加测试项目
                        try:
                            coupon_list.clear()
                            coupon_list.addItem("🔍 调试测试项目")
                            print(f"        ✅ 成功添加测试项目")
                            print(f"        添加后项目数量: {coupon_list.count()}")
                        except Exception as e:
                            print(f"        ❌ 添加测试项目失败: {e}")
                    else:
                        print(f"        ❌ coupon_list 无效")
                else:
                    print(f"        ❌ tab_manager_widget 没有 coupon_list 属性")
            else:
                print(f"        ❌ 主窗口没有 tab_manager_widget 属性")
            
            # 搜索所有QListWidget组件
            print(f"\n     🔍 搜索所有QListWidget组件:")
            from PyQt5.QtWidgets import QListWidget
            list_widgets = main_window.findChildren(QListWidget)
            print(f"        找到 {len(list_widgets)} 个QListWidget组件")
            
            for i, widget in enumerate(list_widgets):
                print(f"        QListWidget {i+1}:")
                print(f"          类型: {type(widget)}")
                print(f"          对象名: {widget.objectName()}")
                print(f"          项目数量: {widget.count()}")
                print(f"          是否可见: {widget.isVisible()}")
                print(f"          父组件: {type(widget.parent()) if widget.parent() else None}")
                
                # 检查父组件是否有title属性
                parent = widget.parent()
                if parent and hasattr(parent, 'title'):
                    try:
                        title = parent.title()
                        print(f"          父组件标题: {title}")
                        if '券' in title:
                            print(f"          ✅ 这可能是券列表组件")
                    except:
                        print(f"          父组件title()调用失败")
        
        def test_show_coupon_list():
            """测试_show_coupon_list方法"""
            print(f"\n  🧪 测试_show_coupon_list方法...")
            
            # 测试数据
            test_coupons = [
                {
                    'couponname': '调试测试券1',
                    'expireddate': '2025-12-31',
                    'couponcode': 'DEBUG001',
                    'coupontype': '测试券'
                },
                {
                    'couponname': '调试测试券2',
                    'expireddate': '2025-12-31',
                    'couponcode': 'DEBUG002',
                    'coupontype': '测试券'
                }
            ]
            
            print(f"     📋 调用_show_coupon_list方法...")
            try:
                main_window._show_coupon_list(test_coupons)
                print(f"     ✅ _show_coupon_list调用成功")
            except Exception as e:
                print(f"     ❌ _show_coupon_list调用失败: {e}")
                import traceback
                traceback.print_exc()
        
        def test_load_available_coupons():
            """测试_load_available_coupons方法"""
            print(f"\n  🧪 测试_load_available_coupons方法...")
            
            # 模拟订单ID和影院ID
            test_order_id = "TEST_ORDER_123"
            test_cinema_id = "35fec8259e74"
            
            print(f"     📋 调用_load_available_coupons方法...")
            print(f"        订单ID: {test_order_id}")
            print(f"        影院ID: {test_cinema_id}")
            
            try:
                main_window._load_available_coupons(test_order_id, test_cinema_id)
                print(f"     ✅ _load_available_coupons调用成功")
            except Exception as e:
                print(f"     ❌ _load_available_coupons调用失败: {e}")
                import traceback
                traceback.print_exc()
        
        def finish_debug():
            """完成调试"""
            print(f"\n  📊 调试完成")
            print(f"     💡 问题分析:")
            print(f"        1. 检查券列表组件是否存在和有效")
            print(f"        2. 检查_show_coupon_list方法的逻辑")
            print(f"        3. 检查API调用和数据解析")
            print(f"        4. 检查组件的可见性和状态")
            
            # 3秒后关闭
            QTimer.singleShot(3000, app.quit)
        
        # 等待UI初始化完成后开始调试
        def start_debugging():
            debug_coupon_components()
            QTimer.singleShot(1000, lambda: test_show_coupon_list())
            QTimer.singleShot(2000, lambda: test_load_available_coupons())
            QTimer.singleShot(3000, lambda: finish_debug())
        
        # 1秒后开始调试
        QTimer.singleShot(1000, start_debugging)
        
        # 显示主窗口
        main_window.show()
        
        # 10秒后强制退出
        QTimer.singleShot(10000, lambda: [print("  ⏰ 调试超时"), app.quit()])
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主调试函数"""
    print("=" * 60)
    print("🔍 券列表显示问题调试")
    print("=" * 60)
    
    print("🎯 调试目标:")
    print("   1. 🔍 检查券列表组件是否存在")
    print("   2. 🧪 测试_show_coupon_list方法")
    print("   3. 🔄 测试_load_available_coupons方法")
    print("   4. 📋 分析券列表显示逻辑")
    print()
    
    # 执行调试
    success = debug_coupon_list()
    
    print("\n" + "=" * 60)
    print("📊 调试结果:")
    print(f"   券列表调试: {'✅ 完成' if success else '❌ 失败'}")
    
    if success:
        print("\n🔍 调试完成！")
        print()
        print("💡 可能的问题原因:")
        print("   1. 券列表组件未正确初始化")
        print("   2. _show_coupon_list方法逻辑问题")
        print("   3. API返回数据格式问题")
        print("   4. 组件查找逻辑问题")
        print()
        print("🔧 建议的解决方案:")
        print("   1. 检查tab_manager_widget的初始化")
        print("   2. 修复_show_coupon_list的组件查找逻辑")
        print("   3. 添加更详细的调试日志")
        print("   4. 确保券列表组件的可见性")
    else:
        print("\n⚠️  调试未完全成功")
        print("   但已收集了有用的信息")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
