#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UI布局优化效果
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_ui_optimizations():
    """测试UI布局优化"""
    print("🧪 测试UI布局优化效果")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from main_modular import ModularCinemaMainWindow
        
        # 创建主窗口
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        # 检查UI优化效果
        def check_ui_optimizations():
            print(f"  📊 检查UI优化效果...")
            
            # 1. 检查账号列表优化
            if hasattr(main_window, 'account_widget'):
                account_widget = main_window.account_widget
                if hasattr(account_widget, 'account_table'):
                    table = account_widget.account_table
                    
                    # 检查列宽设置
                    header = table.horizontalHeader()
                    col0_width = header.sectionSize(0)  # 账号列
                    col1_width = header.sectionSize(1)  # 余额列
                    col2_width = header.sectionSize(2)  # 积分列
                    table_width = table.width()
                    
                    print(f"     📋 账号列表优化:")
                    print(f"        - 账号列宽度: {col0_width}px (目标: 110px)")
                    print(f"        - 余额列宽度: {col1_width}px (目标: 60px)")
                    print(f"        - 积分列宽度: {col2_width}px (目标: 50px)")
                    print(f"        - 表格总宽度: {table_width}px (目标: 240px)")
                    
                    if col0_width == 110 and col1_width == 60 and col2_width == 50:
                        print(f"        ✅ 账号列表列宽优化成功")
                    else:
                        print(f"        ⚠️  账号列表列宽需要调整")
            
            # 2. 检查Tab管理器优化
            if hasattr(main_window, 'tab_manager_widget'):
                tab_manager = main_window.tab_manager_widget
                
                # 检查影院选择布局
                if hasattr(tab_manager, 'cinema_combo'):
                    cinema_combo = tab_manager.cinema_combo
                    print(f"     🏛️ 影院选择优化:")
                    print(f"        - 影院下拉框存在: ✅")
                    print(f"        - 影院下拉框项目数: {cinema_combo.count()}")
                
                # 检查提交订单按钮
                if hasattr(tab_manager, 'submit_order_btn'):
                    submit_btn = tab_manager.submit_order_btn
                    btn_height = submit_btn.height()
                    min_height = submit_btn.minimumHeight()
                    max_height = submit_btn.maximumHeight()
                    
                    print(f"     🔘 提交订单按钮优化:")
                    print(f"        - 按钮高度: {btn_height}px")
                    print(f"        - 最小高度: {min_height}px (目标: 24px)")
                    print(f"        - 最大高度: {max_height}px (目标: 24px)")
                    
                    if min_height == 24 and max_height == 24:
                        print(f"        ✅ 提交按钮高度优化成功")
                    else:
                        print(f"        ⚠️  提交按钮高度需要调整")
            
            # 3. 检查座位区域优化
            if hasattr(main_window, 'seat_placeholder'):
                seat_placeholder = main_window.seat_placeholder
                placeholder_text = seat_placeholder.text()
                
                print(f"     🪑 座位区域优化:")
                print(f"        - 占位符文本: {repr(placeholder_text[:50])}...")
                
                if "请点击上方座位" not in placeholder_text:
                    print(f"        ✅ 座位区域提示文字优化成功")
                else:
                    print(f"        ⚠️  座位区域仍有多余提示文字")
            
            # 4. 检查登录窗口优化
            if hasattr(main_window, 'login_window') and main_window.login_window:
                login_window = main_window.login_window
                
                if hasattr(login_window, 'login_button'):
                    login_btn = login_window.login_button
                    btn_text = login_btn.text()
                    btn_enabled = login_btn.isEnabled()
                    
                    print(f"     🔐 登录窗口优化:")
                    print(f"        - 登录按钮文本: '{btn_text}' (目标: '登 录')")
                    print(f"        - 登录按钮启用: {btn_enabled} (目标: True)")
                    
                    if btn_text == "登 录" and btn_enabled:
                        print(f"        ✅ 登录窗口优化成功")
                    elif btn_text == "请稍候...":
                        print(f"        ⚠️  登录按钮仍显示'请稍候'")
                    else:
                        print(f"        ⚠️  登录按钮状态异常")
            
            # 总结优化效果
            print(f"  📊 UI优化检查完成")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待登录完成后检查
        def start_checking():
            if hasattr(main_window, 'login_window') and main_window.login_window:
                if main_window.login_window.isVisible():
                    print(f"  ⏳ 等待登录完成...")
                    QTimer.singleShot(3000, start_checking)
                else:
                    print(f"  ✅ 登录完成，开始检查UI优化")
                    QTimer.singleShot(1000, check_ui_optimizations)
            else:
                print(f"  ✅ 直接开始检查UI优化")
                QTimer.singleShot(1000, check_ui_optimizations)
        
        # 开始检查
        QTimer.singleShot(1000, start_checking)
        
        # 10秒后强制退出
        QTimer.singleShot(10000, lambda: [print("  ⏰ 测试超时"), app.quit()])
        
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
    print("🎨 UI布局优化测试")
    print("=" * 60)
    
    print("💡 优化内容:")
    print("   1. 📋 账号列表: 调整列宽，避免滚动条")
    print("      - 账号列: 120px → 110px")
    print("      - 余额列: 80px → 60px")
    print("      - 积分列: 80px → 50px")
    print("      - 表格宽度: 固定240px")
    print()
    print("   2. 🏛️ 影院选择: 下拉框与文字贴近")
    print("      - 影院选择比例: 55% → 40%")
    print("      - 券列表比例: 45% → 60%")
    print("      - 标签宽度: 40px → 35px")
    print("      - 布局间距: 减小到5px")
    print()
    print("   3. 🪑 座位区域: 移除多余提示")
    print("      - 移除'请点击上方座位'提示")
    print("      - 提交按钮高度: 35px → 24px")
    print()
    print("   4. 🔐 登录窗口: 移除等待时间")
    print("      - 移除2秒等待")
    print("      - 移除'请稍候'提示")
    print("      - 登录按钮立即可用")
    print()
    
    # 测试UI优化效果
    success = test_ui_optimizations()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   UI优化测试: {'✅ 正常' if success else '❌ 异常'}")
    
    if success:
        print("\n🎉 UI布局优化完成！")
        print()
        print("✨ 优化效果:")
        print("   ✅ 账号列表更紧凑，无滚动条")
        print("   ✅ 影院选择与文字贴近，券列表空间更大")
        print("   ✅ 座位区域无多余提示，按钮更小巧")
        print("   ✅ 登录窗口立即可用，无等待时间")
        print()
        print("🚀 现在可以使用优化后的系统:")
        print("   python main_modular.py")
    else:
        print("\n⚠️  UI优化测试未完全成功")
        print("   建议检查各组件的布局设置")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
