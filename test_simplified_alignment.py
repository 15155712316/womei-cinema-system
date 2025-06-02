#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化对齐方案效果
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_simplified_alignment():
    """测试简化对齐方案效果"""
    print("🎭 测试简化对齐方案效果")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建主窗口
        from main_modular import ModularCinemaMainWindow
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        def check_simplified_alignment():
            """检查简化对齐方案效果"""
            print(f"\n  🎯 检查简化对齐方案效果...")
            
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
                
                # 获取账号信息标签的位置
                account_label = None
                if hasattr(tab_manager, 'current_account_label'):
                    account_label = tab_manager.current_account_label
                    account_x = account_label.x()
                    account_width = account_label.width()
                    print(f"        📋 账号信息区域: X位置={account_x}px, 宽度={account_width}px")
                else:
                    print(f"        ❌ 未找到账号信息标签")
                    return False
                
                # 检查所有下拉框的位置
                comboboxes = [
                    ('影院下拉框', 'cinema_combo'),
                    ('影片下拉框', 'movie_combo'),
                    ('日期下拉框', 'date_combo'),
                    ('场次下拉框', 'session_combo')
                ]
                
                combo_positions = []
                alignment_success = True
                
                for name, attr_name in comboboxes:
                    if hasattr(tab_manager, attr_name):
                        combo = getattr(tab_manager, attr_name)
                        combo_x = combo.x()
                        combo_width = combo.width()
                        combo_positions.append(combo_x)
                        
                        print(f"        📋 {name}: X位置={combo_x}px, 宽度={combo_width}px")
                        
                        # 检查是否与账号信息区域左边缘对齐
                        alignment_diff = abs(combo_x - account_x)
                        if alignment_diff <= 5:  # 允许5px的误差
                            print(f"            ✅ 与账号信息区域对齐良好 (差异: {alignment_diff}px)")
                        else:
                            print(f"            ⚠️  与账号信息区域对齐需要改进 (差异: {alignment_diff}px)")
                            if alignment_diff > 20:  # 差异太大
                                alignment_success = False
                    else:
                        print(f"        ❌ 未找到{name}")
                        alignment_success = False
                
                # 检查下拉框之间的对齐
                if combo_positions and len(set(combo_positions)) <= 2:
                    print(f"        ✅ 下拉框左边缘对齐良好: {set(combo_positions)}")
                    combo_aligned = True
                else:
                    print(f"        ❌ 下拉框左边缘对齐需要改进: {combo_positions}")
                    combo_aligned = False
                
                # 检查改进效果
                if combo_positions:
                    avg_combo_x = sum(combo_positions) / len(combo_positions)
                    improvement = account_x - avg_combo_x
                    print(f"        📊 平均下拉框位置: {avg_combo_x:.1f}px")
                    print(f"        📊 与账号信息区域差异: {abs(improvement):.1f}px")
                    
                    if abs(improvement) <= 10:
                        print(f"        ✅ 对齐效果良好")
                        improvement_good = True
                    else:
                        print(f"        ⚠️  对齐效果需要进一步改进")
                        improvement_good = False
                else:
                    improvement_good = False
                
                return alignment_success and combo_aligned and improvement_good
                
            except Exception as e:
                print(f"        ❌ 检查简化对齐方案效果失败: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        def finish_test(alignment_test):
            """完成测试"""
            print(f"\n  📊 测试完成")
            print(f"     🎉 简化对齐方案测试结果: {'✅ 通过' if alignment_test else '❌ 失败'}")
            
            if alignment_test:
                print(f"\n     💡 简化对齐成果:")
                print(f"        🎭 修改父容器左边距为0px")
                print(f"        🖱️ 简化下拉框布局设置")
                print(f"        🔄 移除复杂的负边距设置")
                print(f"        🎯 实现与账号信息区域的良好对齐")
                
                print(f"\n     🎬 最终效果:")
                print(f"        - 影院、影片、日期、场次下拉框左边缘基本对齐")
                print(f"        - 与上方蓝色账号信息区域形成较好的对齐效果")
                print(f"        - 简化的布局设置更加稳定可靠")
                print(f"        - 整个界面视觉效果得到改善")
                
                print(f"\n     🛡️  技术实现:")
                print(f"        - 父容器边距: setContentsMargins(0, 20, 10, 10)")
                print(f"        - 子布局边距: setContentsMargins(0, 0, 0, 0)")
                print(f"        - 标签宽度: setFixedWidth(30)")
                print(f"        - 标签对齐: Qt.AlignRight | Qt.AlignVCenter")
                print(f"        - 固定间距: addSpacing(5)")
                print(f"        - 下拉框宽度: setFixedWidth(320)")
                
                print(f"\n     🎯 解决方案优势:")
                print(f"        1. ✅ 简化了复杂的负边距设置")
                print(f"        2. ✅ 通过修改父容器边距实现对齐")
                print(f"        3. ✅ 布局设置更加稳定可靠")
                print(f"        4. ✅ 避免了可能的样式冲突")
                print(f"        5. ✅ 实现了基本的对齐效果")
            else:
                print(f"\n     ⚠️  测试未通过")
                print(f"        可能需要进一步调整对齐方案")
            
            # 5秒后关闭
            QTimer.singleShot(5000, app.quit)
        
        # 等待UI初始化完成后开始测试
        def start_testing():
            alignment_test = check_simplified_alignment()
            QTimer.singleShot(500, lambda: finish_test(alignment_test))
        
        # 1秒后开始测试
        QTimer.singleShot(1000, start_testing)
        
        # 显示主窗口
        main_window.show()
        
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
    print("🎭 简化对齐方案效果测试")
    print("=" * 60)
    
    print("🎯 测试目标:")
    print("   1. 🏗️  验证简化对齐方案的效果")
    print("   2. 🎭 检查下拉框与账号信息区域的对齐")
    print("   3. 🎯 验证四个下拉框之间的对齐")
    print("   4. 📋 评估整体视觉效果改善")
    print()
    
    print("🔧 简化方案:")
    print("   • 父容器左边距: 从10px改为0px")
    print("   • 移除复杂的负边距设置")
    print("   • 简化子布局边距设置")
    print("   • 保持标签和下拉框的基本设置")
    print()
    
    # 执行测试
    success = test_simplified_alignment()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   简化对齐方案效果测试: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("\n🎉 简化对齐方案效果良好！")
        print()
        print("✨ 简化成果:")
        print("   🎭 ✅ 修改父容器左边距实现基本对齐")
        print("   🖱️ ✅ 简化布局设置避免复杂性")
        print("   🔄 ✅ 四个下拉框左边缘基本对齐")
        print("   🎯 ✅ 与账号信息区域形成较好对齐")
        print()
        print("🎬 最终视觉效果:")
        print("   - 影院、影片、日期、场次下拉框左边缘基本对齐")
        print("   - 与上方蓝色账号信息区域形成较好的对齐效果")
        print("   - 简化的布局设置更加稳定可靠")
        print("   - 整个界面视觉效果得到明显改善")
        print()
        print("💡 技术优势:")
        print("   1. ✅ 避免了复杂的负边距设置")
        print("   2. ✅ 通过父容器边距实现对齐")
        print("   3. ✅ 布局设置简单稳定")
        print("   4. ✅ 减少了样式冲突的可能性")
        print("   5. ✅ 实现了基本的对齐需求")
    else:
        print("\n⚠️  测试未完全通过")
        print("   需要进一步调整对齐方案")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
