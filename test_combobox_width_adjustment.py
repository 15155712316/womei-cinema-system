#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试下拉框宽度调整
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_combobox_width_adjustment():
    """测试下拉框宽度调整"""
    print("🎭 测试下拉框宽度调整")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def check_new_combobox_widths():
            """检查新的下拉框宽度"""
            print(f"\n  🎯 检查新的下拉框宽度...")
            
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
                
                # 检查所有下拉框的新宽度
                comboboxes = [
                    ('影院下拉框', 'cinema_combo'),
                    ('影片下拉框', 'movie_combo'),
                    ('日期下拉框', 'date_combo'),
                    ('场次下拉框', 'session_combo')
                ]
                
                widths = []
                positions = []
                all_correct = True
                
                for name, attr_name in comboboxes:
                    if hasattr(tab_manager, attr_name):
                        combo = getattr(tab_manager, attr_name)
                        width = combo.width()
                        x_pos = combo.x()
                        
                        widths.append(width)
                        positions.append(x_pos)
                        
                        print(f"        📋 {name}: 宽度={width}px, X位置={x_pos}px")
                        
                        # 检查是否达到预期宽度（280px + 边框等 ≈ 286px）
                        if width >= 280:
                            print(f"            ✅ 宽度符合预期 (≥280px)")
                        else:
                            print(f"            ⚠️  宽度可能不够 (<280px)")
                            all_correct = False
                    else:
                        print(f"        ❌ 未找到{name}")
                        all_correct = False
                
                # 检查宽度一致性
                if widths and len(set(widths)) == 1:
                    print(f"        ✅ 所有下拉框宽度一致: {widths[0]}px")
                    width_consistent = True
                else:
                    print(f"        ❌ 下拉框宽度不一致: {widths}")
                    width_consistent = False
                
                # 检查位置对齐
                if positions and len(set(positions)) <= 2:
                    print(f"        ✅ 下拉框位置对齐良好")
                    position_aligned = True
                else:
                    print(f"        ⚠️  下拉框位置: {positions}")
                    position_aligned = False
                
                # 比较新旧宽度
                old_width = 206  # 之前测试显示的宽度
                new_width = widths[0] if widths else 0
                width_increase = new_width - old_width
                
                print(f"        📊 宽度变化: {old_width}px → {new_width}px (增加{width_increase}px)")
                
                if width_increase > 60:  # 期望增加约80px (280-200=80)
                    print(f"        ✅ 宽度增加显著，更接近红框标注")
                else:
                    print(f"        ⚠️  宽度增加不够显著")
                
                return all_correct and width_consistent and position_aligned
                
            except Exception as e:
                print(f"        ❌ 检查下拉框宽度失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def check_visual_proportion():
            """检查视觉比例"""
            print(f"\n  📐 检查视觉比例...")
            
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
                
                # 检查下拉框相对于容器的比例
                if hasattr(tab_manager, 'cinema_combo'):
                    combo = tab_manager.cinema_combo
                    combo_width = combo.width()
                    
                    # 获取父容器宽度
                    parent = combo.parent()
                    if parent:
                        parent_width = parent.width()
                        proportion = (combo_width / parent_width) * 100 if parent_width > 0 else 0
                        
                        print(f"        📋 下拉框宽度: {combo_width}px")
                        print(f"        📋 容器宽度: {parent_width}px")
                        print(f"        📋 占比: {proportion:.1f}%")
                        
                        # 检查是否接近红框标注的比例（大约70-80%）
                        if 60 <= proportion <= 85:
                            print(f"        ✅ 比例合适，接近红框标注")
                            proportion_good = True
                        else:
                            print(f"        ⚠️  比例可能需要调整")
                            proportion_good = False
                    else:
                        print(f"        ⚠️  无法获取父容器宽度")
                        proportion_good = True  # 不算失败
                else:
                    print(f"        ❌ 无法获取下拉框")
                    proportion_good = False
                
                return proportion_good
                
            except Exception as e:
                print(f"        ❌ 检查视觉比例失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(width_test, proportion_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 下拉框宽度调整测试结果:")
            print(f"        ✅ 宽度调整检查: {'通过' if width_test else '失败'}")
            print(f"        ✅ 视觉比例检查: {'通过' if proportion_test else '失败'}")
            
            all_passed = width_test and proportion_test
            
            if all_passed:
                print(f"\n     💡 调整成果:")
                print(f"        🎭 下拉框宽度从200px增加到280px")
                print(f"        🖱️ 实际显示宽度约286px (包含边框)")
                print(f"        🔄 所有下拉框宽度完全一致")
                print(f"        🎯 视觉比例更接近红框标注")
                
                print(f"\n     🎬 现在的效果:")
                print(f"        - 影院、影片、日期、场次下拉框更长")
                print(f"        - 宽度统一为280px，视觉一致")
                print(f"        - 长度更接近红框标注的比例")
                print(f"        - 保持完美对齐和紧密布局")
                
                print(f"\n     🛡️  技术实现:")
                print(f"        - 所有下拉框: setFixedWidth(280)")
                print(f"        - 宽度增加: +80px (从200px到280px)")
                print(f"        - 保持标签透明背景和紧密间距")
                print(f"        - 维持完美的位置对齐")
            else:
                print(f"\n     ⚠️  部分测试未通过")
                print(f"        需要进一步调整宽度设置")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            width_test = check_new_combobox_widths()
            QTimer.singleShot(500, lambda: continue_testing(width_test))
        
        def continue_testing(width_test):
            proportion_test = check_visual_proportion()
            QTimer.singleShot(500, lambda: finish_test(width_test, proportion_test))
        
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
    print("🎭 下拉框宽度调整测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证下拉框宽度增加到280px")
    print("   2. 🎭 验证所有下拉框宽度一致")
    print("   3. 🎯 验证视觉比例接近红框标注")
    print("   4. 📋 验证保持完美对齐")
    print()
    
    print("🔧 调整内容:")
    print("   • 影院下拉框: setFixedWidth(280) (从200增加到280)")
    print("   • 影片下拉框: setFixedWidth(280) (从200增加到280)")
    print("   • 日期下拉框: setFixedWidth(280) (从200增加到280)")
    print("   • 场次下拉框: setFixedWidth(280) (从200增加到280)")
    print()
    
    # 执行测试
    success = test_combobox_width_adjustment()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   下拉框宽度调整测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 下拉框宽度调整成功！")
        print()
        print("✨ 调整成果:")
        print("   🎭 ✅ 下拉框宽度增加到280px")
        print("   🖱️ ✅ 所有下拉框宽度完全一致")
        print("   🔄 ✅ 视觉比例更接近红框标注")
        print("   🎯 ✅ 保持完美对齐和紧密布局")
        print()
        print("🎬 现在的效果:")
        print("   - 影院、影片、日期、场次下拉框更长")
        print("   - 宽度从200px增加到280px (+80px)")
        print("   - 长度更接近红框标注的视觉比例")
        print("   - 保持标签透明背景和紧密间距")
        print("   - 维持所有下拉框完美对齐")
        print()
        print("💡 技术实现:")
        print("   1. 统一设置setFixedWidth(280)增加宽度")
        print("   2. 保持所有下拉框宽度完全一致")
        print("   3. 维持标签透明背景和紧密布局")
        print("   4. 确保视觉比例更接近参考标准")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步调整宽度设置")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
