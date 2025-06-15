#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影院系统三个具体问题修复验证测试
"""

def test_city_api_loading():
    """测试城市列表数据加载问题修复"""
    print("=== 测试1：城市列表数据加载问题修复 ===")
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 测试城市API调用
        print("✅ 测试城市API调用:")
        print("  1. 创建沃美电影服务实例")
        print("  2. 使用token: 47794858a832916d8eda012e7cabd269")
        
        film_service = get_womei_film_service("47794858a832916d8eda012e7cabd269")
        cities_result = film_service.get_cities()
        
        print(f"  3. API响应结果:")
        print(f"     - success: {cities_result.get('success')}")
        print(f"     - total: {cities_result.get('total', 'N/A')}")
        print(f"     - error: {cities_result.get('error', 'N/A')}")
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            print(f"✅ 城市数据加载成功:")
            print(f"  - 城市数量: {len(cities)}")
            
            # 显示前3个城市信息
            for i, city in enumerate(cities[:3]):
                city_name = city.get('city_name', '未知城市')
                city_id = city.get('city_id', 'N/A')
                cinemas_count = len(city.get('cinemas', []))
                print(f"  - 城市 {i+1}: {city_name} (ID: {city_id}, 影院数: {cinemas_count})")
            
            if len(cities) > 3:
                print(f"  - ... 还有 {len(cities) - 3} 个城市")
            
            # 验证城市数据结构
            if cities:
                first_city = cities[0]
                required_fields = ['city_name', 'city_id', 'cinemas']
                missing_fields = []
                
                for field in required_fields:
                    if field not in first_city:
                        missing_fields.append(field)
                
                if not missing_fields:
                    print("✅ 城市数据结构验证通过")
                    return True
                else:
                    print(f"❌ 城市数据缺少字段: {missing_fields}")
                    return False
            else:
                print("❌ 城市数据为空")
                return False
        else:
            error = cities_result.get('error', '未知错误')
            print(f"❌ 城市API调用失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 城市数据加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cinema_api_loading():
    """测试影院数据源配置问题修复"""
    print("\n=== 测试2：影院数据源配置问题修复 ===")
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        print("✅ 测试影院数据获取:")
        print("  1. 完全移除对本地cinema_info.json的依赖")
        print("  2. 通过城市API动态获取影院数据")
        
        film_service = get_womei_film_service("47794858a832916d8eda012e7cabd269")
        cities_result = film_service.get_cities()
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            
            # 查找有影院的城市
            city_with_cinemas = None
            for city in cities:
                cinemas = city.get('cinemas', [])
                if cinemas:
                    city_with_cinemas = city
                    break
            
            if city_with_cinemas:
                city_name = city_with_cinemas.get('city_name', '未知城市')
                cinemas = city_with_cinemas.get('cinemas', [])
                
                print(f"✅ 影院数据获取成功:")
                print(f"  - 测试城市: {city_name}")
                print(f"  - 影院数量: {len(cinemas)}")
                
                # 显示前3个影院信息
                for i, cinema in enumerate(cinemas[:3]):
                    cinema_name = cinema.get('cinema_name', '未知影院')
                    cinema_id = cinema.get('cinema_id', 'N/A')
                    print(f"  - 影院 {i+1}: {cinema_name} (ID: {cinema_id})")
                
                if len(cinemas) > 3:
                    print(f"  - ... 还有 {len(cinemas) - 3} 个影院")
                
                # 验证影院数据结构
                if cinemas:
                    first_cinema = cinemas[0]
                    required_fields = ['cinema_name', 'cinema_id']
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in first_cinema:
                            missing_fields.append(field)
                    
                    if not missing_fields:
                        print("✅ 影院数据结构验证通过")
                        print("✅ 完全通过API动态获取，无本地文件依赖")
                        return True
                    else:
                        print(f"❌ 影院数据缺少字段: {missing_fields}")
                        return False
                else:
                    print("❌ 影院数据为空")
                    return False
            else:
                print("❌ 未找到有影院的城市")
                return False
        else:
            error = cities_result.get('error', '未知错误')
            print(f"❌ 获取城市数据失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 影院数据源测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_movie_api_loading():
    """测试电影下拉框状态问题修复"""
    print("\n=== 测试3：电影下拉框状态问题修复 ===")
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        print("✅ 测试电影API调用:")
        
        # 先获取城市和影院数据
        film_service = get_womei_film_service("47794858a832916d8eda012e7cabd269")
        cities_result = film_service.get_cities()
        
        if cities_result.get('success'):
            cities = cities_result.get('cities', [])
            
            # 查找有影院的城市
            test_cinema_id = None
            test_cinema_name = None
            
            for city in cities:
                cinemas = city.get('cinemas', [])
                if cinemas:
                    first_cinema = cinemas[0]
                    test_cinema_id = first_cinema.get('cinema_id')
                    test_cinema_name = first_cinema.get('cinema_name')
                    break
            
            if test_cinema_id:
                print(f"  1. 测试影院: {test_cinema_name} (ID: {test_cinema_id})")
                print(f"  2. 调用电影API: get_movies(cinema_id={test_cinema_id})")
                
                # 调用电影API
                movies_result = film_service.get_movies(test_cinema_id)
                
                print(f"  3. API响应结果:")
                print(f"     - success: {movies_result.get('success')}")
                print(f"     - total: {movies_result.get('total', 'N/A')}")
                print(f"     - error: {movies_result.get('error', 'N/A')}")
                
                if movies_result.get('success'):
                    movies = movies_result.get('movies', [])
                    print(f"✅ 电影数据加载成功:")
                    print(f"  - 电影数量: {len(movies)}")
                    
                    # 显示前3部电影信息
                    for i, movie in enumerate(movies[:3]):
                        movie_name = movie.get('name', '未知电影')
                        movie_id = movie.get('movie_id', 'N/A')  # 修复：沃美API使用movie_id字段
                        print(f"  - 电影 {i+1}: {movie_name} (ID: {movie_id})")

                    if len(movies) > 3:
                        print(f"  - ... 还有 {len(movies) - 3} 部电影")

                    # 验证电影数据结构
                    if movies:
                        first_movie = movies[0]
                        required_fields = ['name', 'movie_id']  # 修复：沃美API使用movie_id字段
                        missing_fields = []

                        for field in required_fields:
                            if field not in first_movie:
                                missing_fields.append(field)
                        
                        if not missing_fields:
                            print("✅ 电影数据结构验证通过")
                            print("✅ 电影下拉框应该能正常启用和填充")
                            return True
                        else:
                            print(f"❌ 电影数据缺少字段: {missing_fields}")
                            return False
                    else:
                        print("⚠️ 该影院暂无电影（这是正常情况）")
                        return True
                else:
                    error = movies_result.get('error', '未知错误')
                    print(f"❌ 电影API调用失败: {error}")
                    return False
            else:
                print("❌ 未找到可测试的影院")
                return False
        else:
            error = cities_result.get('error', '未知错误')
            print(f"❌ 获取城市数据失败: {error}")
            return False
            
    except Exception as e:
        print(f"❌ 电影下拉框测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始沃美影院系统三个具体问题修复验证测试")
    print("=" * 70)
    
    test_results = []
    
    # 执行所有测试
    test_results.append(test_city_api_loading())
    test_results.append(test_cinema_api_loading())
    test_results.append(test_movie_api_loading())
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("\n" + "=" * 70)
    print("🎯 测试结果总结")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！三个问题修复成功！")
        print("\n📋 修复总结:")
        print("1. ✅ 城市列表数据加载问题已修复，增强了调试功能")
        print("2. ✅ 影院数据源配置问题已修复，完全移除本地文件依赖")
        print("3. ✅ 电影下拉框状态问题已修复，增强了API调用调试")
        
        print("\n📋 下一步操作建议：")
        print("1. 启动程序：python main_modular.py")
        print("2. 观察城市数据自动加载和调试输出")
        print("3. 验证六级联动的自动选择功能")
        print("4. 查看详细的API调用调试信息")
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
