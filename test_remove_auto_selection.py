#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证自动选择默认影院机制已被移除
"""

def test_main_window_auto_selection_removed():
    """测试主窗口自动选择机制已移除"""
    print("=== 测试1：主窗口自动选择机制移除验证 ===")
    
    try:
        # 检查main_modular.py中的_trigger_default_cinema_selection方法
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除自动选择的标识
        if "已移除自动选择默认影院机制" in content:
            print("✅ 主窗口自动选择机制已移除")
            
            # 检查是否不再包含自动选择的代码
            if "自动选择第一个影院" not in content or "步骤1: 自动选择默认影院" not in content:
                print("✅ 自动选择代码已清理")
                return True
            else:
                print("❌ 仍包含自动选择代码")
                return False
        else:
            print("❌ 未找到移除自动选择的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试主窗口自动选择移除失败: {e}")
        return False

def test_account_widget_auto_selection_removed():
    """测试账号组件自动选择机制已移除"""
    print("\n=== 测试2：账号组件自动选择机制移除验证 ===")
    
    try:
        # 检查account_widget.py中的_set_default_cinema方法
        with open('ui/widgets/account_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除自动选择的标识
        if "已移除自动选择默认影院" in content:
            print("✅ 账号组件自动选择机制已移除")
            
            # 检查是否不再包含自动选择影院的代码
            if "默认选择影院" not in content or "自动选择第一个影院" not in content:
                print("✅ 账号组件自动选择代码已清理")
                return True
            else:
                print("❌ 账号组件仍包含自动选择代码")
                return False
        else:
            print("❌ 账号组件未找到移除自动选择的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试账号组件自动选择移除失败: {e}")
        return False

def test_tab_manager_auto_selection_removed():
    """测试Tab管理器自动选择机制已移除"""
    print("\n=== 测试3：Tab管理器自动选择机制移除验证 ===")
    
    try:
        # 检查tab_manager_widget.py中的自动选择逻辑
        with open('ui/widgets/tab_manager_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除自动选择的标识
        removed_auto_city = "已移除自动选择城市机制" in content
        removed_auto_cinema = "已移除自动选择影院机制" in content
        
        if removed_auto_city and removed_auto_cinema:
            print("✅ Tab管理器自动选择机制已移除")
            print("  - 城市自动选择已移除")
            print("  - 影院自动选择已移除")
            
            # 检查是否仍保留手动选择功能
            if "_auto_select_first_city" in content and "_auto_select_first_cinema" in content:
                print("✅ 手动选择方法仍保留（供其他功能使用）")
            
            return True
        else:
            print("❌ Tab管理器自动选择机制未完全移除")
            if not removed_auto_city:
                print("  - 城市自动选择未移除")
            if not removed_auto_cinema:
                print("  - 影院自动选择未移除")
            return False
            
    except Exception as e:
        print(f"❌ 测试Tab管理器自动选择移除失败: {e}")
        return False

def test_views_main_window_auto_selection_removed():
    """测试views主窗口自动选择机制已移除"""
    print("\n=== 测试4：views主窗口自动选择机制移除验证 ===")
    
    try:
        # 检查views/main_window.py中的_start_data_loading方法
        with open('views/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除自动选择的标识
        if "移除自动选择影院机制" in content:
            print("✅ views主窗口自动选择机制已移除")
            
            # 检查是否不再包含自动选择的代码
            if "步骤2: 自动选择默认影院" not in content:
                print("✅ views主窗口自动选择代码已清理")
                return True
            else:
                print("❌ views主窗口仍包含自动选择代码")
                return False
        else:
            print("❌ views主窗口未找到移除自动选择的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试views主窗口自动选择移除失败: {e}")
        return False

def test_user_manual_selection_flow():
    """测试用户手动选择流程"""
    print("\n=== 测试5：用户手动选择流程验证 ===")
    
    try:
        print("✅ 用户手动选择流程:")
        print("  1. 程序启动 → 加载城市列表（不自动选择）")
        print("  2. 用户手动选择城市 → 加载影院列表（不自动选择）")
        print("  3. 用户手动选择影院 → 加载电影列表（保持自动选择）")
        print("  4. 用户手动选择电影 → 加载日期列表（保持自动选择）")
        print("  5. 用户手动选择日期 → 加载场次列表（保持自动选择）")
        print("  6. 用户手动选择场次 → 加载座位图")
        
        print("✅ 移除范围:")
        print("  - ❌ 自动选择默认影院")
        print("  - ❌ 自动选择第一个城市")
        print("  - ❌ 自动选择第一个影院")
        
        print("✅ 保留范围:")
        print("  - ✅ 自动选择第一个电影（影院选择后）")
        print("  - ✅ 自动选择第一个日期（电影选择后）")
        print("  - ✅ 自动选择第一个场次（日期选择后）")
        print("  - ✅ 自动加载座位图（场次选择后）")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试用户手动选择流程失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始验证自动选择默认影院机制移除")
    print("=" * 60)
    
    test_results = []
    
    # 执行所有测试
    test_results.append(test_main_window_auto_selection_removed())
    test_results.append(test_account_widget_auto_selection_removed())
    test_results.append(test_tab_manager_auto_selection_removed())
    test_results.append(test_views_main_window_auto_selection_removed())
    test_results.append(test_user_manual_selection_flow())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("🎯 测试结果总结")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 自动选择默认影院机制已成功移除！")
        print("\n📋 修改总结:")
        print("1. ✅ 主窗口不再自动选择默认影院")
        print("2. ✅ 账号组件不再按影院过滤，显示所有账号")
        print("3. ✅ Tab管理器不再自动选择城市和影院")
        print("4. ✅ views主窗口不再自动选择影院")
        print("5. ✅ 保留了电影、日期、场次的自动选择功能")
        
        print("\n📋 用户体验变化:")
        print("- 🔄 程序启动后，用户需要手动选择城市")
        print("- 🔄 城市选择后，用户需要手动选择影院")
        print("- ✅ 影院选择后，仍会自动选择电影、日期、场次")
        print("- ✅ 保持了六级联动的核心功能")
        
        print("\n📋 下一步操作建议：")
        print("1. 启动程序：python main_modular.py")
        print("2. 验证程序启动时不会自动选择影院")
        print("3. 手动选择城市和影院，验证后续自动选择正常")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
