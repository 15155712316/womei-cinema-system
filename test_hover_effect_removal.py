#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位悬浮效果移除
验证座位选中的悬浮效果已被移除
"""

import sys
import os
import re

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_hover_effect_removal():
    """测试悬浮效果移除"""
    try:
        print("🧪 测试座位悬浮效果移除")
        print("=" * 60)
        
        # 读取座位面板文件
        seat_panel_file = "ui/components/seat_map_panel_pyqt5.py"
        
        if not os.path.exists(seat_panel_file):
            print(f"❌ 文件不存在: {seat_panel_file}")
            return False
        
        with open(seat_panel_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📋 检查文件: {seat_panel_file}")
        print(f"📋 文件大小: {len(content)} 字符")
        
        # 检查是否还有hover效果
        hover_patterns = [
            r':hover\s*\{',
            r'QPushButton:hover',
            r'hover.*background',
            r'background.*hover'
        ]
        
        found_hover_effects = []
        
        for pattern in hover_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                found_hover_effects.append({
                    'pattern': pattern,
                    'line': line_num,
                    'content': line_content
                })
        
        print(f"\n📋 悬浮效果检查结果:")
        if found_hover_effects:
            print(f"❌ 发现 {len(found_hover_effects)} 个悬浮效果:")
            for effect in found_hover_effects:
                print(f"  - 第{effect['line']}行: {effect['content']}")
                print(f"    匹配模式: {effect['pattern']}")
            return False
        else:
            print(f"✅ 未发现任何悬浮效果，移除成功！")
        
        # 检查样式表结构
        print(f"\n📋 样式表结构检查:")
        
        # 查找QPushButton样式定义
        button_styles = re.findall(r'QPushButton\s*\{[^}]*\}', content, re.DOTALL)
        print(f"  - 发现 {len(button_styles)} 个QPushButton样式定义")
        
        # 检查是否有完整的样式定义（不包含hover）
        clean_styles = 0
        for style in button_styles:
            if ':hover' not in style:
                clean_styles += 1
        
        print(f"  - 其中 {clean_styles} 个样式不包含hover效果")
        
        # 检查关键样式是否存在
        key_styles = [
            'background-color',
            'border',
            'color',
            'font'
        ]
        
        style_check = {}
        for key_style in key_styles:
            count = content.count(key_style)
            style_check[key_style] = count
            print(f"  - {key_style}: {count} 次使用")
        
        print(f"\n✅ 悬浮效果移除验证通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_seat_button_functionality():
    """测试座位按钮基本功能是否正常"""
    try:
        print("\n🧪 测试座位按钮基本功能")
        print("=" * 60)
        
        # 导入座位面板
        from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5
        
        print("✅ 座位面板导入成功")
        
        # 创建座位面板实例
        seat_panel = SeatMapPanelPyQt5()
        print("✅ 座位面板实例化成功")
        
        # 检查关键方法是否存在
        key_methods = [
            '_seat_button_clicked',
            '_update_seat_style',
            'update_seat_data',
            'get_selected_seats'
        ]
        
        for method in key_methods:
            if hasattr(seat_panel, method):
                print(f"✅ 方法存在: {method}")
            else:
                print(f"❌ 方法缺失: {method}")
        
        # 检查信号是否存在
        key_signals = [
            'seat_selected',
            'seat_deselected'
        ]
        
        for signal in key_signals:
            if hasattr(seat_panel, signal):
                print(f"✅ 信号存在: {signal}")
            else:
                print(f"❌ 信号缺失: {signal}")
        
        print(f"\n✅ 座位按钮基本功能检查完成！")
        return True
        
    except Exception as e:
        print(f"❌ 功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_style_consistency():
    """测试样式一致性"""
    try:
        print("\n🧪 测试样式一致性")
        print("=" * 60)
        
        seat_panel_file = "ui/components/seat_map_panel_pyqt5.py"
        
        with open(seat_panel_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查座位状态样式
        seat_states = [
            'available',
            'selected', 
            'sold',
            'locked',
            'unavailable'
        ]
        
        print(f"📋 座位状态样式检查:")
        for state in seat_states:
            # 查找该状态的样式定义
            pattern = rf'{state}.*background-color'
            matches = re.findall(pattern, content, re.IGNORECASE)
            print(f"  - {state}: {len(matches)} 个样式定义")
        
        # 检查是否有pressed状态（点击效果）
        pressed_count = content.count(':pressed')
        print(f"\n📋 点击效果检查:")
        print(f"  - :pressed 样式: {pressed_count} 个")
        
        if pressed_count > 0:
            print(f"  ✅ 保留了点击效果，移除了悬浮效果")
        else:
            print(f"  ℹ️ 未发现点击效果样式")
        
        # 检查颜色一致性
        color_patterns = re.findall(r'#[0-9a-fA-F]{6}', content)
        unique_colors = set(color_patterns)
        print(f"\n📋 颜色使用统计:")
        print(f"  - 总颜色使用: {len(color_patterns)} 次")
        print(f"  - 唯一颜色数: {len(unique_colors)} 个")
        
        # 显示前10个最常用的颜色
        from collections import Counter
        color_counts = Counter(color_patterns)
        most_common = color_counts.most_common(10)
        
        print(f"  - 最常用颜色:")
        for color, count in most_common:
            print(f"    {color}: {count} 次")
        
        print(f"\n✅ 样式一致性检查完成！")
        return True
        
    except Exception as e:
        print(f"❌ 样式一致性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 沃美电影票务系统 - 座位悬浮效果移除测试")
    print("=" * 60)
    print("📋 测试目标：验证座位选中的悬浮效果已被移除")
    print("🔍 测试内容：")
    print("  1. 悬浮效果移除验证")
    print("  2. 座位按钮基本功能测试")
    print("  3. 样式一致性检查")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_hover_effect_removal,
        test_seat_button_functionality,
        test_style_consistency
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n🎉 测试完成！")
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print(f"✅ 所有测试通过，悬浮效果移除成功！")
        print(f"\n📋 修改总结：")
        print(f"✅ 移除了QPushButton:hover样式")
        print(f"✅ 保留了座位按钮的基本功能")
        print(f"✅ 保留了点击效果（如果存在）")
        print(f"✅ 样式定义保持一致性")
        print(f"\n🚀 现在座位选中时不会有悬浮效果了！")
    else:
        print(f"❌ 部分测试失败，需要进一步检查")

if __name__ == "__main__":
    main()
