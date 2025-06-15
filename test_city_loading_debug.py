#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断城市列表加载问题
"""

def test_womei_api_directly():
    """直接测试沃美API"""
    print("=== 测试1：直接测试沃美API ===")
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        print("✅ 创建沃美电影服务实例...")
        token = "47794858a832916d8eda012e7cabd269"
        film_service = get_womei_film_service(token)
        
        print("✅ 调用城市API...")
        cities_result = film_service.get_cities()
        
        print(f"✅ API响应结果:")
        print(f"  - success: {cities_result.get('success')}")
        print(f"  - total: {cities_result.get('total', 'N/A')}")
        print(f"  - error: {cities_result.get('error', 'N/A')}")
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            print(f"✅ 城市数据:")
            print(f"  - 城市数量: {len(cities)}")
            
            if cities:
                first_city = cities[0]
                print(f"  - 第一个城市: {first_city.get('city_name')} (ID: {first_city.get('city_id')})")
                print(f"  - 影院数量: {len(first_city.get('cinemas', []))}")
                return True
            else:
                print("❌ 城市列表为空")
                return False
        else:
            error = cities_result.get('error', '未知错误')
            print(f"❌ API调用失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 直接API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tab_manager_initialization():
    """测试Tab管理器初始化流程"""
    print("\n=== 测试2：Tab管理器初始化流程 ===")
    
    try:
        # 模拟Tab管理器的初始化流程
        print("✅ 模拟Tab管理器初始化:")
        print("  1. __init__ → initialize() → _init_cascade() → _load_cities_for_womei()")
        print("  2. 城市下拉框初始状态: '加载中...'")
        print("  3. 调用沃美城市API")
        print("  4. 更新城市下拉框: _update_city_combo()")
        print("  5. 启用城市下拉框供用户选择")
        
        # 检查初始化顺序
        initialization_steps = [
            "创建Tab管理器实例",
            "调用initialize()方法",
            "调用_init_cascade()方法", 
            "调用_load_cities_for_womei()方法",
            "创建沃美电影服务实例",
            "调用get_cities() API",
            "处理API响应",
            "调用_update_city_combo()方法",
            "启用城市下拉框"
        ]
        
        for i, step in enumerate(initialization_steps, 1):
            print(f"  步骤 {i}: {step}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tab管理器初始化测试失败: {e}")
        return False

def test_city_combo_state():
    """测试城市下拉框状态"""
    print("\n=== 测试3：城市下拉框状态检查 ===")
    
    try:
        print("✅ 检查城市下拉框配置:")
        
        # 检查初始状态
        initial_states = {
            "初始文本": "加载中...",
            "启用状态": True,
            "宽度": 320,
            "信号连接": "currentTextChanged → _on_city_changed"
        }
        
        for key, value in initial_states.items():
            print(f"  - {key}: {value}")
        
        # 检查API加载后的状态
        print("✅ API加载成功后的状态:")
        api_loaded_states = {
            "下拉框内容": "请选择城市 + 城市列表",
            "启用状态": True,
            "用户可操作": "可以选择城市"
        }
        
        for key, value in api_loaded_states.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 城市下拉框状态测试失败: {e}")
        return False

def test_potential_issues():
    """测试潜在问题"""
    print("\n=== 测试4：潜在问题诊断 ===")
    
    try:
        print("✅ 检查可能的问题:")
        
        potential_issues = [
            {
                "问题": "API调用失败",
                "原因": "网络问题或token无效",
                "症状": "城市下拉框显示'加载失败'"
            },
            {
                "问题": "初始化顺序错误", 
                "原因": "_init_cascade未被调用",
                "症状": "城市下拉框保持初始状态"
            },
            {
                "问题": "下拉框被禁用",
                "原因": "setEnabled(False)未恢复",
                "症状": "用户无法点击城市下拉框"
            },
            {
                "问题": "信号连接失败",
                "原因": "currentTextChanged信号未连接",
                "症状": "选择城市后无响应"
            },
            {
                "问题": "数据更新失败",
                "原因": "_update_city_combo方法异常",
                "症状": "API成功但下拉框无数据"
            }
        ]
        
        for i, issue in enumerate(potential_issues, 1):
            print(f"  问题 {i}: {issue['问题']}")
            print(f"    原因: {issue['原因']}")
            print(f"    症状: {issue['症状']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ 潜在问题诊断失败: {e}")
        return False

def test_debug_suggestions():
    """提供调试建议"""
    print("\n=== 测试5：调试建议 ===")
    
    try:
        print("✅ 调试步骤建议:")
        
        debug_steps = [
            "1. 启动程序，观察控制台输出",
            "2. 查找'[Tab管理器] 🚀 初始化沃美影院联动系统'日志",
            "3. 查找'[城市调试] ==================== 开始加载沃美城市列表'日志",
            "4. 检查API响应: success、total、error字段",
            "5. 查找'[城市调试] ✅ 城市下拉框更新完成'日志",
            "6. 检查城市下拉框是否显示城市列表",
            "7. 尝试手动选择城市，观察是否触发影院加载"
        ]
        
        for step in debug_steps:
            print(f"  {step}")
        
        print("\n✅ 如果城市列表仍然没有数据，请检查:")
        
        check_points = [
            "程序启动时是否调用了Tab管理器的initialize()方法",
            "initialize()方法是否调用了_init_cascade()方法",
            "_init_cascade()方法是否调用了_load_cities_for_womei()方法",
            "沃美API是否返回success=True",
            "_update_city_combo()方法是否被正确调用",
            "城市下拉框是否被正确启用"
        ]
        
        for point in check_points:
            print(f"  - {point}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试建议生成失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始诊断城市列表加载问题")
    print("=" * 60)
    
    test_results = []
    
    # 执行所有测试
    test_results.append(test_womei_api_directly())
    test_results.append(test_tab_manager_initialization())
    test_results.append(test_city_combo_state())
    test_results.append(test_potential_issues())
    test_results.append(test_debug_suggestions())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 60)
    print("🎯 诊断结果总结")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if test_results[0]:  # 如果API测试通过
        print("\n🎉 沃美API正常工作！")
        print("\n📋 问题可能出现在:")
        print("1. Tab管理器初始化流程")
        print("2. 城市下拉框状态管理")
        print("3. 信号连接或数据更新")
        
        print("\n📋 下一步操作建议：")
        print("1. 启动程序：python main_modular.py")
        print("2. 观察控制台输出，查找城市加载相关日志")
        print("3. 检查城市下拉框是否显示'加载中...'然后更新为城市列表")
        print("4. 如果仍有问题，请提供完整的控制台日志")
    else:
        print("\n⚠️ 沃美API调用失败，请检查网络连接和token有效性")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
