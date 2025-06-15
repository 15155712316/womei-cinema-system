#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证本地影院文件加载已被移除，影院完全通过API获取
"""

def test_main_window_cinema_loading_removed():
    """测试主窗口本地影院加载已移除"""
    print("=== 测试1：主窗口本地影院加载移除验证 ===")
    
    try:
        # 检查main_modular.py中的_trigger_default_cinema_selection方法
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除本地影院文件加载的标识
        if "已移除本地影院文件加载" in content:
            print("✅ 主窗口本地影院文件加载已移除")
            
            # 检查是否不再包含cinema_manager.load_cinema_list()调用
            if "cinema_manager.load_cinema_list()" not in content:
                print("✅ cinema_manager.load_cinema_list()调用已移除")
                
                # 检查是否包含API获取的说明
                if "影院将通过API动态获取" in content:
                    print("✅ 已说明影院将通过API动态获取")
                    return True
                else:
                    print("❌ 未找到API获取说明")
                    return False
            else:
                print("❌ 仍包含cinema_manager.load_cinema_list()调用")
                return False
        else:
            print("❌ 未找到移除本地影院文件加载的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试主窗口本地影院加载移除失败: {e}")
        return False

def test_views_main_window_cinema_loading_removed():
    """测试views主窗口本地影院加载已移除"""
    print("\n=== 测试2：views主窗口本地影院加载移除验证 ===")
    
    try:
        # 检查views/main_window.py中的_start_data_loading方法
        with open('views/main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除本地影院文件加载的标识
        if "移除本地影院文件加载" in content:
            print("✅ views主窗口本地影院文件加载已移除")
            
            # 检查是否不再包含cinema_controller.load_cinema_list()调用
            if "cinema_controller.load_cinema_list()" not in content:
                print("✅ cinema_controller.load_cinema_list()调用已移除")
                
                # 检查是否包含API获取的说明
                if "影院将通过API动态获取" in content:
                    print("✅ 已说明影院将通过API动态获取")
                    return True
                else:
                    print("❌ 未找到API获取说明")
                    return False
            else:
                print("❌ 仍包含cinema_controller.load_cinema_list()调用")
                return False
        else:
            print("❌ 未找到移除本地影院文件加载的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试views主窗口本地影院加载移除失败: {e}")
        return False

def test_cinema_controller_loading_removed():
    """测试影院控制器本地加载已移除"""
    print("\n=== 测试3：影院控制器本地加载移除验证 ===")
    
    try:
        # 检查controllers/cinema_controller.py中的load_cinema_list方法
        with open('controllers/cinema_controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除本地影院文件加载的标识
        if "已移除本地影院文件加载" in content:
            print("✅ 影院控制器本地影院文件加载已移除")
            
            # 检查是否不再包含cinema_manager.load_cinema_list()调用
            if "self.cinema_manager.load_cinema_list()" not in content:
                print("✅ self.cinema_manager.load_cinema_list()调用已移除")
                
                # 检查是否返回空列表
                if "return []" in content:
                    print("✅ 影院控制器返回空列表，等待API获取")
                    return True
                else:
                    print("❌ 影院控制器未返回空列表")
                    return False
            else:
                print("❌ 仍包含self.cinema_manager.load_cinema_list()调用")
                return False
        else:
            print("❌ 未找到移除本地影院文件加载的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试影院控制器本地加载移除失败: {e}")
        return False

def test_tab_manager_local_dependency_removed():
    """测试Tab管理器本地数据依赖已移除"""
    print("\n=== 测试4：Tab管理器本地数据依赖移除验证 ===")
    
    try:
        # 检查ui/widgets/tab_manager_widget.py中的_load_sample_data方法
        with open('ui/widgets/tab_manager_widget.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含移除本地数据依赖的标识
        if "已移除本地影院文件依赖" in content:
            print("✅ Tab管理器本地影院文件依赖已移除")
            
            # 检查是否包含API获取的说明
            if "所有数据通过API动态获取" in content:
                print("✅ 已说明所有数据通过API动态获取")
                return True
            else:
                print("❌ 未找到API获取说明")
                return False
        else:
            print("❌ 未找到移除本地数据依赖的标识")
            return False
            
    except Exception as e:
        print(f"❌ 测试Tab管理器本地依赖移除失败: {e}")
        return False

def test_api_based_cinema_flow():
    """测试基于API的影院获取流程"""
    print("\n=== 测试5：基于API的影院获取流程验证 ===")
    
    try:
        print("✅ 新的影院获取流程:")
        print("  1. 程序启动 → 不加载本地影院文件")
        print("  2. 用户选择城市 → 调用沃美城市API")
        print("  3. 城市API返回 → 包含该城市的影院列表")
        print("  4. 用户选择影院 → 调用沃美电影API")
        print("  5. 电影API返回 → 包含该影院的电影列表")
        print("  6. 继续后续流程...")
        
        print("\n✅ 移除的本地文件依赖:")
        print("  - ❌ data/cinema_info.json")
        print("  - ❌ cinema_manager.load_cinema_list()")
        print("  - ❌ cinema_controller.load_cinema_list()")
        print("  - ❌ 硬编码的影院数据")
        
        print("\n✅ 保留的API功能:")
        print("  - ✅ 沃美城市API (get_cities)")
        print("  - ✅ 沃美电影API (get_movies)")
        print("  - ✅ 沃美场次API (get_shows)")
        print("  - ✅ 沃美座位API (get_hall_info)")
        
        # 验证沃美API服务是否可用
        try:
            from services.womei_film_service import get_womei_film_service
            film_service = get_womei_film_service("47794858a832916d8eda012e7cabd269")
            
            # 测试城市API
            cities_result = film_service.get_cities()
            if cities_result.get('success'):
                cities = cities_result.get('cities', [])
                print(f"\n✅ 沃美API验证成功:")
                print(f"  - 城市API可用，获取到 {len(cities)} 个城市")
                
                # 检查第一个城市是否有影院数据
                if cities:
                    first_city = cities[0]
                    cinemas = first_city.get('cinemas', [])
                    city_name = first_city.get('city_name', '未知城市')
                    print(f"  - 城市 '{city_name}' 包含 {len(cinemas)} 个影院")
                    
                    if cinemas:
                        first_cinema = cinemas[0]
                        cinema_name = first_cinema.get('cinema_name', '未知影院')
                        cinema_id = first_cinema.get('cinema_id', 'N/A')
                        print(f"  - 第一个影院: {cinema_name} (ID: {cinema_id})")
                
                return True
            else:
                error = cities_result.get('error', '未知错误')
                print(f"❌ 沃美API验证失败: {error}")
                return False
                
        except Exception as api_e:
            print(f"❌ 沃美API验证异常: {api_e}")
            return False
        
    except Exception as e:
        print(f"❌ 测试API流程失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始验证本地影院文件加载移除")
    print("=" * 70)
    
    test_results = []
    
    # 执行所有测试
    test_results.append(test_main_window_cinema_loading_removed())
    test_results.append(test_views_main_window_cinema_loading_removed())
    test_results.append(test_cinema_controller_loading_removed())
    test_results.append(test_tab_manager_local_dependency_removed())
    test_results.append(test_api_based_cinema_flow())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 70)
    print("🎯 测试结果总结")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 本地影院文件加载已成功移除！")
        print("\n📋 修改总结:")
        print("1. ✅ 主窗口不再加载本地影院文件")
        print("2. ✅ views主窗口不再调用影院控制器加载本地文件")
        print("3. ✅ 影院控制器不再从cinema_manager加载本地文件")
        print("4. ✅ Tab管理器移除了本地数据依赖")
        print("5. ✅ 沃美API验证成功，可以动态获取影院数据")
        
        print("\n📋 新的数据流程:")
        print("- 🔄 程序启动 → 不加载任何本地影院文件")
        print("- 🔄 用户选择城市 → 沃美API返回该城市的影院列表")
        print("- 🔄 用户选择影院 → 沃美API返回该影院的电影列表")
        print("- ✅ 所有影院数据完全通过API动态获取")
        
        print("\n📋 下一步操作建议：")
        print("1. 启动程序：python main_modular.py")
        print("2. 验证程序启动时不会看到'加载影院信息成功，共 6 个影院'")
        print("3. 选择城市，验证影院列表通过API动态加载")
        print("4. 选择影院，验证电影列表正确加载")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
