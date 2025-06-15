#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证调试模式是否生效
"""

import sys
import os
sys.path.insert(0, '.')

def verify_debug_mode():
    """验证调试模式配置"""
    print("=== 验证调试模式配置 ===")
    
    try:
        # 读取main_modular.py文件
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查调试模式标识
        if 'DEBUG_SKIP_LOGIN = True' in content:
            print("✅ 调试模式已启用 (DEBUG_SKIP_LOGIN = True)")
        elif 'DEBUG_SKIP_LOGIN = False' in content:
            print("❌ 调试模式已禁用 (DEBUG_SKIP_LOGIN = False)")
        else:
            print("⚠️ 未找到调试模式配置")
            return False
        
        # 检查调试模式相关代码
        debug_indicators = [
            '🚧 [调试模式] 跳过登录验证',
            '_show_main_window_after_debug_login',
            'debug_mode": True'
        ]
        
        found_indicators = []
        for indicator in debug_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        print(f"✅ 找到 {len(found_indicators)}/{len(debug_indicators)} 个调试模式标识")
        
        for indicator in found_indicators:
            print(f"  - {indicator}")
        
        # 检查七级联动相关代码
        cascade_indicators = [
            'system_combo',
            'city_combo', 
            '_init_seven_level_cascade',
            '_on_system_changed',
            '_on_city_changed'
        ]
        
        found_cascade = []
        for indicator in cascade_indicators:
            if indicator in content:
                found_cascade.append(indicator)
        
        print(f"✅ 找到 {len(found_cascade)}/{len(cascade_indicators)} 个七级联动标识")
        
        if len(found_indicators) >= 2 and len(found_cascade) >= 3:
            print("\n🎉 调试模式配置正确，七级联动功能已集成")
            print("\n使用说明:")
            print("1. 程序启动时会跳过登录验证")
            print("2. 窗口标题会显示 [🚧 调试模式 - 已跳过登录]")
            print("3. 可以直接测试七级联动功能")
            print("4. 要恢复登录验证，将 DEBUG_SKIP_LOGIN 改为 False")
            return True
        else:
            print("\n❌ 调试模式配置不完整")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def check_seven_level_cascade():
    """检查七级联动组件"""
    print("\n=== 检查七级联动组件 ===")
    
    try:
        # 检查Tab管理器组件
        with open('ui/widgets/tab_manager_widget.py', 'r', encoding='utf-8') as f:
            tab_content = f.read()
        
        cascade_components = [
            'system_combo',
            'city_combo',
            '_on_system_changed',
            '_on_city_changed',
            '_init_seven_level_cascade'
        ]
        
        found_components = []
        for component in cascade_components:
            if component in tab_content:
                found_components.append(component)
        
        print(f"✅ Tab管理器中找到 {len(found_components)}/{len(cascade_components)} 个七级联动组件")
        
        # 检查配置文件
        from config.cinema_systems_config import CinemaSystemConfig
        systems = CinemaSystemConfig.get_all_systems()
        print(f"✅ 系统配置正常，共 {len(systems)} 个影院系统")
        
        # 检查API服务
        from services.unified_cinema_api import CinemaAPIFactory
        api = CinemaAPIFactory.create_womei_api("test_token")
        print("✅ 统一API服务正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 七级联动组件检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🔍 调试模式验证程序")
    print("="*50)
    
    # 验证调试模式
    debug_ok = verify_debug_mode()
    
    # 检查七级联动
    cascade_ok = check_seven_level_cascade()
    
    print("\n" + "="*50)
    print("📊 验证结果汇总:")
    print("="*50)
    print(f"调试模式配置: {'✅ 正常' if debug_ok else '❌ 异常'}")
    print(f"七级联动组件: {'✅ 正常' if cascade_ok else '❌ 异常'}")
    
    if debug_ok and cascade_ok:
        print("\n🎉 所有验证通过！")
        print("现在可以启动主程序测试七级联动功能：")
        print("  d:/python3.12/python.exe main_modular.py")
    else:
        print("\n⚠️ 存在问题，请检查配置")
    
    return debug_ok and cascade_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
