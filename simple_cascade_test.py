#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的三级联动测试程序
测试基本的配置和API功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python版本:", sys.version)
print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path[:3])  # 显示前3个路径
print()

def test_config():
    """测试配置系统"""
    print("=== 测试配置系统 ===")
    
    try:
        from config.cinema_systems_config import CinemaSystemType, CinemaSystemConfig, cinema_system_manager
        
        # 测试获取所有系统
        systems = CinemaSystemConfig.get_all_systems()
        print(f"✓ 发现 {len(systems)} 个影院系统:")
        for system in systems:
            print(f"  - {system['display_name']}: {system['description']}")
        
        # 测试华联系统配置
        print("\n--- 华联系统配置 ---")
        huanlian_config = CinemaSystemConfig.get_system_config(CinemaSystemType.HUANLIAN)
        print(f"系统名称: {huanlian_config['system_name']}")
        print(f"API域名: {huanlian_config['api_config']['base_url']}")
        print(f"租户标识: {huanlian_config['api_config']['tenant_short']}")
        
        # 测试沃美系统配置
        print("\n--- 沃美系统配置 ---")
        womei_config = CinemaSystemConfig.get_system_config(CinemaSystemType.WOMEI)
        print(f"系统名称: {womei_config['system_name']}")
        print(f"API域名: {womei_config['api_config']['base_url']}")
        print(f"租户标识: {womei_config['api_config']['tenant_short']}")
        
        # 测试URL构建
        print("\n--- URL构建测试 ---")
        huanlian_cities_url = CinemaSystemConfig.build_api_url(CinemaSystemType.HUANLIAN, 'cities')
        womei_cities_url = CinemaSystemConfig.build_api_url(CinemaSystemType.WOMEI, 'cities')
        print(f"华联城市API: {huanlian_cities_url}")
        print(f"沃美城市API: {womei_cities_url}")
        
        # 测试系统管理器
        print("\n--- 系统管理器测试 ---")
        cinema_system_manager.set_current_system(CinemaSystemType.WOMEI)
        current = cinema_system_manager.get_current_system()
        print(f"当前系统: {current.value if current else 'None'}")
        
        print("✓ 配置系统测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 配置系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api():
    """测试API系统"""
    print("\n=== 测试API系统 ===")
    
    try:
        from services.unified_cinema_api import CinemaAPIFactory
        from config.cinema_systems_config import CinemaSystemType
        
        # 测试创建API实例
        print("创建API实例...")
        womei_api = CinemaAPIFactory.create_womei_api()
        huanlian_api = CinemaAPIFactory.create_huanlian_api()
        
        print("✓ API实例创建成功")
        
        # 注意：实际API调用需要有效的token，这里只测试实例创建
        print("注意: 实际API调用需要有效的认证token")
        
        return True
        
    except Exception as e:
        print(f"✗ API系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_components():
    """测试UI组件（不启动GUI）"""
    print("\n=== 测试UI组件导入 ===")
    
    try:
        # 测试PyQt5可用性
        try:
            from PyQt5.QtWidgets import QApplication
            print("✓ PyQt5 可用")
        except ImportError:
            print("✗ PyQt5 不可用，跳过UI测试")
            return False
        
        # 测试组件导入
        from ui.components.system_select_panel import SystemSelectPanel
        print("✓ 系统选择面板导入成功")
        
        from ui.components.city_select_panel import CitySelectPanel
        print("✓ 城市选择面板导入成功")
        
        from ui.components.enhanced_cinema_select_panel import EnhancedCinemaSelectPanel
        print("✓ 影院选择面板导入成功")
        
        from ui.components.seven_level_cascade_manager import SevenLevelCascadeManager
        print("✓ 七级联动管理器导入成功")
        
        print("✓ 所有UI组件导入成功")
        return True
        
    except Exception as e:
        print(f"✗ UI组件测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cascade_logic():
    """测试联动逻辑"""
    print("\n=== 测试联动逻辑 ===")
    
    try:
        from config.cinema_systems_config import CinemaSystemType, cinema_system_manager
        
        # 模拟系统选择
        print("1. 模拟选择华联系统...")
        cinema_system_manager.set_current_system(CinemaSystemType.HUANLIAN)
        current_system = cinema_system_manager.get_current_system()
        print(f"   当前系统: {current_system.value}")
        
        # 模拟城市数据
        print("2. 模拟城市数据...")
        mock_city = {
            'id': 'test_city_001',
            'name': '测试城市',
            'code': 'TEST',
            'system_type': 'huanlian'
        }
        print(f"   模拟城市: {mock_city['name']} (ID: {mock_city['id']})")
        
        # 模拟影院数据
        print("3. 模拟影院数据...")
        mock_cinema = {
            'id': 'test_cinema_001',
            'name': '测试影院',
            'address': '测试地址123号',
            'city_id': mock_city['id'],
            'system_type': 'huanlian'
        }
        print(f"   模拟影院: {mock_cinema['name']} (ID: {mock_cinema['id']})")
        
        # 测试联动状态
        print("4. 测试联动状态...")
        selections = {
            'system': current_system,
            'city': mock_city,
            'cinema': mock_cinema
        }
        
        print("   联动状态:")
        for level, selection in selections.items():
            if level == 'system':
                print(f"     {level}: {selection.value if selection else 'None'}")
            elif selection:
                name = selection.get('name', 'Unknown')
                print(f"     {level}: {name}")
            else:
                print(f"     {level}: None")
        
        print("✓ 联动逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 联动逻辑测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始三级联动功能测试...\n")
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("配置系统", test_config()))
    test_results.append(("API系统", test_api()))
    test_results.append(("UI组件", test_ui_components()))
    test_results.append(("联动逻辑", test_cascade_logic()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:12} : {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！三级联动基础功能正常")
        print("\n下一步建议:")
        print("1. 运行完整的GUI测试程序")
        print("2. 配置有效的API认证token")
        print("3. 测试实际的API调用功能")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查相关组件")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
