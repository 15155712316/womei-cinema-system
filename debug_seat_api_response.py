#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试沃美影院座位API响应内容
查看实际的API响应数据结构
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_api_response():
    """调试API响应"""
    
    # 配置参数
    schedule_id = "16624418"
    cinema_id = "400028"
    token = "47794858a832916d8eda012e7cabd269"
    
    # 请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/json',
        'Referer': 'https://servicewechat.com/wx4080846d0cec2fd5/78/page-frame.html',
        'tenant-short': 'wmyc'
    }
    
    # API接口
    apis = [
        {
            'name': '全部座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/',
            'params': {'schedule_id': schedule_id, 'token': token}
        },
        {
            'name': '可售座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/saleable/',
            'params': {'schedule_id': schedule_id, 'token': token}
        }
    ]
    
    print("🔍 调试沃美影院座位API响应")
    print("=" * 60)
    
    for api in apis:
        print(f"\n🎯 测试 {api['name']}")
        print("-" * 40)
        print(f"URL: {api['url']}")
        print(f"参数: {api['params']}")
        
        try:
            response = requests.get(
                api['url'], 
                params=api['params'], 
                headers=headers, 
                timeout=30, 
                verify=False
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            print(f"响应大小: {len(response.text)} 字符")
            print(f"原始响应:")
            print(response.text)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON解析成功:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except json.JSONDecodeError as e:
                    print(f"JSON解析失败: {e}")
            
        except Exception as e:
            print(f"请求失败: {e}")
        
        print("\n" + "=" * 60)

def test_different_schedule_ids():
    """测试不同的场次ID"""
    
    # 尝试一些可能有效的场次ID
    test_schedule_ids = [
        "16624418",  # 原始ID
        "16624419",  # 相邻ID
        "16624420",  # 相邻ID
        "16624400",  # 较小ID
        "16624500",  # 较大ID
    ]
    
    cinema_id = "400028"
    token = "47794858a832916d8eda012e7cabd269"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    print("\n🔄 测试不同场次ID")
    print("=" * 60)
    
    for schedule_id in test_schedule_ids:
        print(f"\n🎬 测试场次ID: {schedule_id}")
        print("-" * 30)
        
        url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/'
        params = {'schedule_id': schedule_id, 'token': token}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
            print(f"状态: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'data' in data and data['data']:
                        print(f"✅ 找到有效数据!")
                        print(f"数据结构: {list(data.keys())}")
                        if 'data' in data:
                            print(f"data字段: {list(data['data'].keys()) if isinstance(data['data'], dict) else type(data['data'])}")
                        break
                except:
                    pass
            
        except Exception as e:
            print(f"请求失败: {e}")

def test_cinema_list():
    """测试获取影院列表"""
    
    token = "47794858a832916d8eda012e7cabd269"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    print("\n🏢 测试获取影院列表")
    print("=" * 60)
    
    # 尝试获取影院列表
    cinema_list_urls = [
        'https://ct.womovie.cn/ticket/wmyc/cinema/list/',
        'https://ct.womovie.cn/ticket/wmyc/cinemas/',
        'https://ct.womovie.cn/ticket/wmyc/cinema/',
    ]
    
    for url in cinema_list_urls:
        print(f"\n🔗 测试URL: {url}")
        try:
            response = requests.get(url, params={'token': token}, headers=headers, timeout=10, verify=False)
            print(f"状态: {response.status_code}")
            print(f"响应: {response.text[:300]}...")
            
            if response.status_code == 200 and len(response.text) > 100:
                try:
                    data = response.json()
                    print(f"✅ 获取到影院数据!")
                    print(f"数据结构: {list(data.keys())}")
                    
                    # 如果有影院数据，显示前几个影院
                    if 'data' in data and isinstance(data['data'], list):
                        cinemas = data['data'][:3]  # 只显示前3个
                        for cinema in cinemas:
                            cinema_id = cinema.get('cinema_id', cinema.get('id', '未知'))
                            cinema_name = cinema.get('cinema_name', cinema.get('name', '未知'))
                            print(f"  影院: {cinema_name} (ID: {cinema_id})")
                    
                    break
                except:
                    pass
        except Exception as e:
            print(f"请求失败: {e}")

def test_movies_api():
    """测试电影列表API"""
    
    cinema_id = "400028"
    token = "47794858a832916d8eda012e7cabd269"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    print("\n🎬 测试电影列表API")
    print("=" * 60)
    
    url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/movies/'
    params = {'token': token}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        print(f"URL: {url}")
        print(f"状态: {response.status_code}")
        print(f"响应大小: {len(response.text)}")
        print(f"响应内容: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 获取到电影数据!")
                print(f"数据结构: {list(data.keys())}")
                
                if 'data' in data and isinstance(data['data'], list):
                    movies = data['data'][:3]  # 只显示前3部电影
                    for movie in movies:
                        movie_id = movie.get('movie_id', movie.get('id', '未知'))
                        movie_name = movie.get('name', movie.get('title', '未知'))
                        print(f"  电影: {movie_name} (ID: {movie_id})")
                        
                        # 尝试获取这部电影的场次
                        test_movie_schedule(cinema_id, movie_id, token, headers)
                        break  # 只测试第一部电影
                
            except Exception as e:
                print(f"解析JSON失败: {e}")
    
    except Exception as e:
        print(f"请求失败: {e}")

def test_movie_schedule(cinema_id, movie_id, token, headers):
    """测试电影场次API"""
    
    print(f"\n  🎭 测试电影 {movie_id} 的场次")
    
    url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/movie/{movie_id}/shows/'
    params = {'token': token}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        print(f"    场次API状态: {response.status_code}")
        print(f"    响应大小: {len(response.text)}")
        
        if response.status_code == 200 and len(response.text) > 50:
            try:
                data = response.json()
                print(f"    ✅ 获取到场次数据!")
                
                if 'data' in data and isinstance(data['data'], dict):
                    shows_data = data['data']
                    for date, shows in list(shows_data.items())[:2]:  # 只显示前2个日期
                        print(f"    日期 {date}: {len(shows)} 个场次")
                        for show in shows[:2]:  # 只显示前2个场次
                            schedule_id = show.get('schedule_id', show.get('id', '未知'))
                            show_time = show.get('show_time', show.get('time', '未知'))
                            print(f"      场次: {show_time} (ID: {schedule_id})")
                            
                            # 使用这个场次ID测试座位API
                            if schedule_id != '未知':
                                test_seat_api_with_schedule(cinema_id, schedule_id, token, headers)
                                return  # 找到有效场次就停止
                
            except Exception as e:
                print(f"    解析场次JSON失败: {e}")
    
    except Exception as e:
        print(f"    场次请求失败: {e}")

def test_seat_api_with_schedule(cinema_id, schedule_id, token, headers):
    """使用有效的场次ID测试座位API"""
    
    print(f"\n    🪑 测试场次 {schedule_id} 的座位")
    
    # 测试两个座位API
    apis = [
        f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/',
        f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/saleable/'
    ]
    
    for api_url in apis:
        api_name = "全部座位" if "info" in api_url else "可售座位"
        params = {'schedule_id': schedule_id, 'token': token}
        
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=10, verify=False)
            print(f"      {api_name}API: {response.status_code}, {len(response.text)} 字符")
            
            if response.status_code == 200 and len(response.text) > 100:
                try:
                    data = response.json()
                    if 'data' in data and data['data']:
                        print(f"      ✅ {api_name}API有数据!")
                        print(f"      数据结构: {list(data.keys())}")
                        
                        # 简单统计座位数量
                        if 'room_seat' in data['data']:
                            total_seats = 0
                            for area in data['data']['room_seat']:
                                seats_data = area.get('seats', {})
                                for row_data in seats_data.values():
                                    total_seats += len(row_data.get('detail', []))
                            print(f"      座位总数: {total_seats}")
                        
                        return True  # 找到有效数据
                except Exception as e:
                    print(f"      解析座位JSON失败: {e}")
        
        except Exception as e:
            print(f"      {api_name}请求失败: {e}")
    
    return False

def main():
    """主函数"""
    print("🔍 沃美影院API调试工具")
    print("=" * 60)
    
    # 1. 调试原始API响应
    debug_api_response()
    
    # 2. 测试不同场次ID
    test_different_schedule_ids()
    
    # 3. 测试影院列表
    test_cinema_list()
    
    # 4. 测试电影和场次API
    test_movies_api()

if __name__ == "__main__":
    main()
