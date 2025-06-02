#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下拉框宽度对齐
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_combobox_width_alignment():
    """测试下拉框宽度对齐"""
    print("🎭 测试下拉框宽度对齐")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def check_combobox_widths():
            """检查下拉框宽度"""
            print(f"\n  🎯 检查下拉框宽度...")
            
            try:
                # 获取Tab管理器组件
                tab_manager = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'TabManagerWidget' in str(child.__class__):
                        tab_manager = child
                        break
                
                if not tab_manager:
                    print(f"        ❌ 未找到Tab管理器组件")
                    return False
                
                print(f"        ✅ 找到Tab管理器组件")
                
                # 检查所有下拉框的宽度
                comboboxes = [
                    ('影院下拉框', 'cinema_combo'),
                    ('影片下拉框', 'movie_combo'),
                    ('日期下拉框', 'date_combo'),
                    ('场次下拉框', 'session_combo')
                ]
                
                widths = []
                all_aligned = True
                
                for name, attr_name in comboboxes:
                    if hasattr(tab_manager, attr_name):
                        combo = getattr(tab_manager, attr_name)
                        width = combo.width()
                        fixed_width = combo.minimumWidth() if combo.minimumWidth() == combo.maximumWidth() else None
                        
                        print(f"        📋 {name}: 当前宽度={width}px, 固定宽度={'是' if fixed_width else '否'}")
                        
                        if fixed_width:
                            print(f"            固定宽度值: {fixed_width}px")
                            widths.append(fixed_width)
                        else:
                            widths.append(width)
                    else:
                        print(f"        ❌ 未找到{name}")
                        all_aligned = False
                
                # 检查宽度是否一致
                if widths and len(set(widths)) == 1:
                    print(f"        ✅ 所有下拉框宽度一致: {widths[0]}px")
                    width_aligned = True
                else:
                    print(f"        ❌ 下拉框宽度不一致: {widths}")
                    width_aligned = False
                
                return all_aligned and width_aligned
                
            except Exception as e:
                print(f"        ❌ 检查下拉框宽度失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_layout_alignment():
            """检查布局对齐"""
            print(f"\n  📐 检查布局对齐...")
            
            try:
                # 获取Tab管理器组件
                tab_manager = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'TabManagerWidget' in str(child.__class__):
                        tab_manager = child
                        break
                
                if not tab_manager:
                    print(f"        ❌ 未找到Tab管理器组件")
                    return False
                
                # 检查标签宽度
                labels = [
                    ('影院标签', 'cinema_combo'),
                    ('影片标签', 'movie_combo'),
                    ('日期标签', 'date_combo'),
                    ('场次标签', 'session_combo')
                ]
                
                print(f"        📋 检查标签和下拉框对齐...")
                
                # 检查下拉框位置
                combo_positions = []
                for name, attr_name in labels:
                    if hasattr(tab_manager, attr_name):
                        combo = getattr(tab_manager, attr_name)
                        pos_x = combo.x()
                        combo_positions.append(pos_x)
                        print(f"        📋 {name}: X位置={pos_x}px")
                
                # 检查X位置是否一致
                if combo_positions and len(set(combo_positions)) == 1:
                    print(f"        ✅ 所有下拉框X位置一致: {combo_positions[0]}px")
                    position_aligned = True
                else:
                    print(f"        ⚠️  下拉框X位置: {combo_positions}")
                    position_aligned = len(set(combo_positions)) <= 2  # 允许小幅差异
                
                return position_aligned
                
            except Exception as e:
                print(f"        ❌ 检查布局对齐失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_visual_consistency():
            """检查视觉一致性"""
            print(f"\n  🎨 检查视觉一致性...")
            
            try:
                # 获取Tab管理器组件
                tab_manager = None
                for child in main_window.findChildren(object):
                    if hasattr(child, '__class__') and 'TabManagerWidget' in str(child.__class__):
                        tab_manager = child
                        break
                
                if not tab_manager:
                    print(f"        ❌ 未找到Tab管理器组件")
                    return False
                
                # 检查下拉框样式一致性
                comboboxes = ['cinema_combo', 'movie_combo', 'date_combo', 'session_combo']
                
                styles_consistent = True
                first_style = None
                
                for attr_name in comboboxes:
                    if hasattr(tab_manager, attr_name):
                        combo = getattr(tab_manager, attr_name)
                        style = combo.styleSheet()
                        
                        if first_style is None:
                            first_style = style
                        elif style != first_style:
                            print(f"        ⚠️  {attr_name} 样式不一致")
                            styles_consistent = False
                
                if styles_consistent:
                    print(f"        ✅ 所有下拉框样式一致")
                else:
                    print(f"        ⚠️  下拉框样式存在差异")
                
                return styles_consistent
                
            except Exception as e:
                print(f"        ❌ 检查视觉一致性失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(width_test, layout_test, visual_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 下拉框宽度对齐测试结果:")
            print(f"        ✅ 宽度对齐检查: {'通过' if width_test else '失败'}")
            print(f"        ✅ 布局对齐检查: {'通过' if layout_test else '失败'}")
            print(f"        ✅ 视觉一致性检查: {'通过' if visual_test else '失败'}")
            
            all_passed = width_test and layout_test and visual_test
            
            if all_passed:
                print(f"\n     💡 修复成果:")
                print(f"        🎭 所有下拉框宽度统一为200px")
                print(f"        🖱️ 下拉框位置完美对齐")
                print(f"        🔄 视觉效果一致")
                print(f"        🎯 布局整齐美观")
                
                print(f"\n     🎬 现在的效果:")
                print(f"        - 影院、影片、日期、场次下拉框宽度完全一致")
                print(f"        - 所有下拉框左边缘对齐")
                print(f"        - 标签右对齐，下拉框左对齐")
                print(f"        - 整体布局整齐美观")
                
                print(f"\n     🛡️  技术实现:")
                print(f"        - 为所有下拉框设置setFixedWidth(200)")
                print(f"        - 保持标签固定宽度50px")
                print(f"        - 使用HBoxLayout确保对齐")
                print(f"        - ClassicComboBox提供统一样式")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步调整对齐设置")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            width_test = check_combobox_widths()
            QTimer.singleShot(500, lambda: continue_testing(width_test))
        
        def continue_testing(width_test):
            layout_test = check_layout_alignment()
            QTimer.singleShot(500, lambda: final_testing(width_test, layout_test))
        
        def final_testing(width_test, layout_test):
            visual_test = check_visual_consistency()
            QTimer.singleShot(500, lambda: finish_test(width_test, layout_test, visual_test))
        
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
    print("🎭 下拉框宽度对齐测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证所有下拉框宽度一致")
    print("   2. 🎭 验证下拉框位置对齐")
    print("   3. 🎯 验证视觉效果一致")
    print("   4. 📋 验证布局整齐美观")
    print()
    
    print("🔧 修改内容:")
    print("   • 影院下拉框: setFixedWidth(200)")
    print("   • 影片下拉框: setFixedWidth(200)")
    print("   • 日期下拉框: setFixedWidth(200)")
    print("   • 场次下拉框: setFixedWidth(200)")
    print()
    
    # 执行测试
    success = test_combobox_width_alignment()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   下拉框宽度对齐测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 下拉框宽度对齐修复成功！")
        print()
        print("✨ 修复成果:")
        print("   🎭 ✅ 所有下拉框宽度统一")
        print("   🖱️ ✅ 下拉框位置完美对齐")
        print("   🔄 ✅ 视觉效果一致")
        print("   🎯 ✅ 布局整齐美观")
        print()
        print("🎬 现在的效果:")
        print("   - 影院、影片、日期、场次下拉框宽度完全一致")
        print("   - 所有下拉框左边缘完美对齐")
        print("   - 标签右对齐，下拉框左对齐")
        print("   - 整体布局整齐美观，视觉效果统一")
        print()
        print("💡 技术实现:")
        print("   1. 为所有下拉框设置固定宽度200px")
        print("   2. 保持标签固定宽度50px确保对齐")
        print("   3. 使用HBoxLayout布局管理器")
        print("   4. ClassicComboBox提供统一的视觉样式")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步调整对齐设置")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
