#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试新token的API响应
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_latest_token():
    """加载最新的token"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            token = accounts[0].get('token', '')
            print(f"✅ 加载最新token: {token}")
            return token
        else:
            print("❌ 账号文件为空")
            return ""
    except Exception as e:
        print(f"❌ 加载账号文件失败: {e}")
        return ""

def test_all_apis():
    """测试所有API"""
    token = load_latest_token()
    if not token:
        return
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    cinema_id = "400028"
    
    print(f"\n🔍 测试所有API")
    print("=" * 50)
    
    # 测试API列表
    apis = [
        {
            'name': '城市列表',
            'url': 'https://ct.womovie.cn/ticket/wmyc/citys/',
            'params': {'token': token}
        },
        {
            'name': '电影列表',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/movies/',
            'params': {'token': token}
        },
        {
            'name': '全部座位API（测试场次）',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/',
            'params': {'schedule_id': '16626081', 'token': token}
        },
        {
            'name': '可售座位API（测试场次）',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/saleable/',
            'params': {'schedule_id': '16626081', 'token': token}
        }
    ]
    
    for api in apis:
        print(f"\n🔄 测试 {api['name']}")
        print(f"URL: {api['url']}")
        print(f"参数: {api['params']}")
        
        try:
            response = requests.get(api['url'], params=api['params'], headers=headers, timeout=15, verify=False)
            
            print(f"状态码: {response.status_code}")
            print(f"响应大小: {len(response.text)} 字符")
            print(f"原始响应: {response.text}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON解析成功:")
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                    
                    # 分析响应
                    if 'ret' in data:
                        ret = data.get('ret', -1)
                        msg = data.get('msg', '')
                        if ret == 0:
                            if data.get('data'):
                                print(f"✅ API调用成功，有数据")
                            else:
                                print(f"⚠️ API调用成功，但无数据")
                        else:
                            print(f"❌ API返回错误: {msg}")
                    elif 'code' in data:
                        code = data.get('code', -1)
                        msg = data.get('msg', '')
                        print(f"响应码: {code}, 消息: {msg}")
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
        
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        print("-" * 50)

def test_different_cinema_ids():
    """测试不同的影院ID"""
    token = load_latest_token()
    if not token:
        return
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    # 尝试不同的影院ID
    cinema_ids = ["400028", "400001", "400002", "400010"]
    
    print(f"\n🏢 测试不同影院ID")
    print("=" * 50)
    
    for cinema_id in cinema_ids:
        print(f"\n🎬 测试影院ID: {cinema_id}")
        
        url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/movies/'
        params = {'token': token}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
            print(f"状态: {response.status_code}")
            print(f"响应: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('ret') == 0 and data.get('data'):
                        movies = data['data']
                        print(f"✅ 影院 {cinema_id} 有 {len(movies)} 部电影")
                        
                        # 测试第一部电影的场次
                        if movies:
                            movie = movies[0]
                            movie_id = movie.get('movie_id', movie.get('id', ''))
                            movie_name = movie.get('name', '未知')
                            print(f"  电影: {movie_name} (ID: {movie_id})")
                            
                            # 测试场次API
                            shows_url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/shows/'
                            shows_params = {'movie_id': movie_id, 'token': token}
                            
                            shows_response = requests.get(shows_url, params=shows_params, headers=headers, timeout=10, verify=False)
                            if shows_response.status_code == 200:
                                shows_data = shows_response.json()
                                if shows_data.get('ret') == 0 and shows_data.get('data'):
                                    shows_dict = shows_data['data']
                                    total_shows = sum(len(date_data.get('schedules', [])) for date_data in shows_dict.values())
                                    print(f"  ✅ 有 {total_shows} 个场次")
                                    
                                    # 找到第一个场次并测试座位API
                                    for date, date_data in shows_dict.items():
                                        schedules = date_data.get('schedules', [])
                                        if schedules:
                                            schedule = schedules[0]
                                            schedule_id = schedule.get('schedule_id', schedule.get('id', ''))
                                            show_time = schedule.get('show_time', '未知')
                                            print(f"  场次: {date} {show_time} (ID: {schedule_id})")
                                            
                                            # 测试座位API
                                            test_seat_api(cinema_id, schedule_id, token, headers)
                                            return  # 找到有效数据就停止
                    else:
                        print(f"❌ 影院 {cinema_id} 无电影数据")
                except:
                    print(f"❌ 影院 {cinema_id} 响应解析失败")
        except Exception as e:
            print(f"❌ 影院 {cinema_id} 请求失败: {e}")

def test_seat_api(cinema_id, schedule_id, token, headers):
    """测试座位API"""
    print(f"\n🪑 测试座位API")
    print(f"影院: {cinema_id}, 场次: {schedule_id}")
    
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
    
    for api in seat_apis:
        print(f"\n  🔄 {api['name']}")
        try:
            response = requests.get(api['url'], params=params, headers=headers, timeout=15, verify=False)
            print(f"    状态: {response.status_code}")
            print(f"    响应大小: {len(response.text)}")
            print(f"    响应: {response.text[:300]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    ret = data.get('ret', -1)
                    msg = data.get('msg', '')
                    
                    if ret == 0 and data.get('data') and len(str(data.get('data'))) > 10:
                        print(f"    ✅ {api['name']}成功获取座位数据")
                        
                        # 简单统计座位数量
                        if 'room_seat' in data['data']:
                            total_seats = 0
                            for area in data['data']['room_seat']:
                                seats_data = area.get('seats', {})
                                for row_data in seats_data.values():
                                    total_seats += len(row_data.get('detail', []))
                            print(f"    座位总数: {total_seats}")
                        
                        return True
                    else:
                        print(f"    ❌ {api['name']}返回错误: {msg}")
                except:
                    print(f"    ❌ {api['name']}响应解析失败")
        except Exception as e:
            print(f"    ❌ {api['name']}请求失败: {e}")
    
    return False

def main():
    """主函数"""
    print("🔍 调试新token的API响应")
    print("=" * 60)
    
    # 1. 测试所有API
    test_all_apis()
    
    # 2. 测试不同影院ID
    test_different_cinema_ids()

if __name__ == "__main__":
    main()
