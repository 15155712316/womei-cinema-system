#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模块化系统的各个组件
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

def test_plugin_interface():
    """测试插件接口系统"""
    try:
        from ui.interfaces.plugin_interface import (
            IWidgetInterface, IPluginInterface, EventBus, PluginManager,
            event_bus, plugin_manager
        )
        print("✅ 插件接口系统导入成功")
        return True
    except Exception as e:
        print(f"❌ 插件接口系统导入失败: {e}")
        return False

def test_classic_components():
    """测试经典组件库"""
    try:
        from ui.widgets.classic_components import (
            ClassicGroupBox, ClassicButton, ClassicLineEdit, ClassicComboBox,
            ClassicTableWidget, ClassicTabWidget, ClassicTextEdit, ClassicLabel,
            ClassicListWidget, apply_classic_theme_to_widget
        )
        print("✅ 经典组件库导入成功")
        return True
    except Exception as e:
        print(f"❌ 经典组件库导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("模块化系统测试开始")
    print("=" * 50)
    
    tests = [
        ("插件接口系统", test_plugin_interface),
        ("经典组件库", test_classic_components)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n测试 {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果：{passed}/{total} 通过")
    print("=" * 50)

if __name__ == "__main__":
    main() 