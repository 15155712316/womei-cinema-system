#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析token使用差异，找出为什么相同token在不同方式下结果不同
"""

import requests
import json
import urllib3
from services.womei_film_service import WomeiFilmService

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_token_from_accounts():
    """从accounts.json加载token"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            token = accounts[0].get('token', '')
            phone = accounts[0].get('phone', '')
            print(f"✅ 从accounts.json加载token:")
            print(f"  Phone: {phone}")
            print(f"  Token: {token}")
            return token, phone
        else:
            print("❌ accounts.json为空")
            return "", ""
    except Exception as e:
        print(f"❌ 加载accounts.json失败: {e}")
        return "", ""

def test_womei_service_approach():
    """测试沃美电影服务的方式"""
    print(f"\n🔍 测试沃美电影服务的API调用方式")
    print("=" * 60)
    
    token, phone = load_token_from_accounts()
    if not token:
        return None
    
    # 创建沃美电影服务实例
    service = WomeiFilmService(token)
    
    print(f"🔄 使用沃美电影服务获取数据...")
    
    # 1. 测试城市API
    cities_result = service.get_cities()
    print(f"城市API结果: {cities_result.get('success', False)}")
    if cities_result.get('success'):
        cities = cities_result.get('cities', [])
        print(f"  获取到 {len(cities)} 个城市")
        
        # 2. 测试影院API
        if cities:
            city = cities[0]
            cinemas = city.get('cinemas', [])
            if cinemas:
                cinema = cinemas[0]
                cinema_id = cinema.get('cinema_id', '')
                cinema_name = cinema.get('cinema_name', '')
                print(f"  测试影院: {cinema_name} (ID: {cinema_id})")
                
                # 3. 测试电影API
                movies_result = service.get_movies(cinema_id)
                print(f"  电影API结果: {movies_result.get('success', False)}")
                if movies_result.get('success'):
                    movies = movies_result.get('movies', [])
                    print(f"    获取到 {len(movies)} 部电影")
                    
                    # 4. 测试场次API
                    if movies:
                        movie = movies[0]
                        movie_id = movie.get('movie_id', movie.get('id', ''))
                        movie_name = movie.get('name', '')
                        print(f"    测试电影: {movie_name} (ID: {movie_id})")
                        
                        shows_result = service.get_shows(cinema_id, str(movie_id))
                        print(f"    场次API结果: {shows_result.get('success', False)}")
                        if shows_result.get('success'):
                            shows_data = shows_result.get('shows', {})
                            total_shows = shows_result.get('total', 0)
                            print(f"      获取到 {total_shows} 个场次")
                            
                            # 找到第一个场次
                            for date, date_data in shows_data.items():
                                schedules = date_data.get('schedules', [])
                                if schedules:
                                    schedule = schedules[0]
                                    schedule_id = schedule.get('schedule_id', schedule.get('id', ''))
                                    show_time = schedule.get('show_time', '')
                                    print(f"      找到场次: {date} {show_time} (ID: {schedule_id})")
                                    
                                    return {
                                        'cinema_id': cinema_id,
                                        'cinema_name': cinema_name,
                                        'movie_id': movie_id,
                                        'movie_name': movie_name,
                                        'schedule_id': schedule_id,
                                        'show_time': show_time,
                                        'token': token
                                    }
    
    return None

def test_direct_api_approach(test_data):
    """测试直接API调用方式"""
    print(f"\n🔍 测试直接API调用方式")
    print("=" * 60)
    
    if not test_data:
        print("❌ 缺少测试数据")
        return
    
    cinema_id = test_data['cinema_id']
    schedule_id = test_data['schedule_id']
    token = test_data['token']
    
    print(f"测试参数:")
    print(f"  影院ID: {cinema_id}")
    print(f"  场次ID: {schedule_id}")
    print(f"  Token: {token[:20]}...")
    
    # 测试不同的请求头配置
    header_configs = [
        {
            'name': '基础请求头',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'tenant-short': 'wmyc'
            }
        },
        {
            'name': '完整请求头（模拟微信小程序）',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Content-Type': 'application/json',
                'Referer': 'https://servicewechat.com/wx4080846d0cec2fd5/78/page-frame.html',
                'tenant-short': 'wmyc'
            }
        },
        {
            'name': '沃美电影服务请求头',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'tenant-short': 'wmyc'
            }
        }
    ]
    
    # 测试两个座位API
    seat_apis = [
        {
            'name': '全部座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/'
        },
        {
            'name': '可售座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/saleable/'
        }
    ]
    
    params = {'schedule_id': schedule_id, 'token': token}
    
    results = {}
    
    for header_config in header_configs:
        print(f"\n🔄 测试 {header_config['name']}")
        print("-" * 40)
        
        for api in seat_apis:
            print(f"  📡 {api['name']}")
            
            try:
                response = requests.get(
                    api['url'], 
                    params=params, 
                    headers=header_config['headers'], 
                    timeout=15, 
                    verify=False
                )
                
                print(f"    状态码: {response.status_code}")
                print(f"    响应大小: {len(response.text)} 字符")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        ret = data.get('ret', -1)
                        msg = data.get('msg', '')
                        
                        if ret == 0:
                            if data.get('data') and len(str(data.get('data'))) > 10:
                                print(f"    ✅ 成功获取数据")
                                
                                # 统计座位数量
                                seat_count = count_seats_in_response(data)
                                print(f"    座位数量: {seat_count}")
                                
                                # 保存成功的结果
                                key = f"{header_config['name']}_{api['name']}"
                                results[key] = {
                                    'success': True,
                                    'seat_count': seat_count,
                                    'data': data
                                }
                            else:
                                print(f"    ⚠️ 成功但无数据")
                        else:
                            print(f"    ❌ API错误: {msg}")
                    except json.JSONDecodeError:
                        print(f"    ❌ JSON解析失败")
                else:
                    print(f"    ❌ HTTP错误: {response.status_code}")
            
            except Exception as e:
                print(f"    ❌ 请求异常: {e}")
    
    return results

def count_seats_in_response(data):
    """统计API响应中的座位数量"""
    try:
        if 'data' in data and 'room_seat' in data['data']:
            total_seats = 0
            room_seat = data['data']['room_seat']
            
            for area in room_seat:
                seats_data = area.get('seats', {})
                for row_data in seats_data.values():
                    total_seats += len(row_data.get('detail', []))
            
            return total_seats
    except:
        pass
    
    return 0

def analyze_successful_requests(results):
    """分析成功的请求"""
    print(f"\n📊 分析成功的请求")
    print("=" * 60)
    
    successful_requests = {k: v for k, v in results.items() if v.get('success')}
    
    if not successful_requests:
        print("❌ 没有成功的请求")
        return
    
    print(f"✅ 成功的请求: {len(successful_requests)} 个")
    
    for key, result in successful_requests.items():
        print(f"  {key}: {result['seat_count']} 个座位")
    
    # 查找API差异
    full_api_results = {k: v for k, v in successful_requests.items() if '全部座位API' in k}
    saleable_api_results = {k: v for k, v in successful_requests.items() if '可售座位API' in k}
    
    if full_api_results and saleable_api_results:
        print(f"\n🔍 API差异分析:")
        
        for full_key, full_result in full_api_results.items():
            header_name = full_key.replace('_全部座位API', '')
            saleable_key = f"{header_name}_可售座位API"
            
            if saleable_key in saleable_api_results:
                saleable_result = saleable_api_results[saleable_key]
                
                full_count = full_result['seat_count']
                saleable_count = saleable_result['seat_count']
                difference = full_count - saleable_count
                
                print(f"  {header_name}:")
                print(f"    全部座位API: {full_count} 个座位")
                print(f"    可售座位API: {saleable_count} 个座位")
                print(f"    差异: {difference} 个座位")
                
                if difference > 0:
                    print(f"    🎯 验证成功: 可售座位API确实过滤了 {difference} 个座位")
                elif difference == 0:
                    print(f"    🤔 两个API返回相同数量的座位")
                else:
                    print(f"    ⚠️ 异常: 可售座位API返回更多座位")

def compare_with_womei_service():
    """对比沃美电影服务的实现"""
    print(f"\n🔍 检查沃美电影服务的实现")
    print("=" * 60)
    
    # 查看沃美电影服务的请求方式
    token, _ = load_token_from_accounts()
    service = WomeiFilmService(token)
    
    print(f"沃美电影服务配置:")
    print(f"  Base URL: {service.base_url}")
    print(f"  Headers: {service.headers}")
    print(f"  Token: {token[:20]}...")
    
    # 检查服务是否有特殊的请求处理
    print(f"\n🔧 建议的修复方案:")
    print(f"  1. 使用与沃美电影服务相同的请求头配置")
    print(f"  2. 确保token参数的传递方式正确")
    print(f"  3. 检查是否需要特殊的认证处理")

def main():
    """主函数"""
    print("🔍 分析token使用差异")
    print("=" * 60)
    
    # 1. 测试沃美电影服务的方式
    test_data = test_womei_service_approach()
    
    if not test_data:
        print("❌ 沃美电影服务测试失败，无法继续")
        return
    
    print(f"\n✅ 沃美电影服务测试成功，获得测试数据")
    
    # 2. 测试直接API调用方式
    results = test_direct_api_approach(test_data)
    
    # 3. 分析成功的请求
    if results:
        analyze_successful_requests(results)
    
    # 4. 对比沃美电影服务的实现
    compare_with_womei_service()

if __name__ == "__main__":
    main()
