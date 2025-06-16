#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多个场次的座位API差异
寻找有已售座位的场次来验证API差异
"""

import json
import time
from typing import Dict, List
from services.womei_film_service import get_womei_film_service

def load_token_from_accounts():
    """从accounts.json加载token"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            token = accounts[0].get('token', '')
            phone = accounts[0].get('phone', '')
            return token, phone
        else:
            return "", ""
    except Exception as e:
        print(f"❌ 加载accounts.json失败: {e}")
        return "", ""

def get_all_schedules():
    """获取所有可用的场次"""
    print(f"🔍 获取所有可用的场次")
    print("=" * 50)
    
    token, phone = load_token_from_accounts()
    if not token:
        return []
    
    service = get_womei_film_service(token)
    all_schedules = []
    
    # 获取城市列表
    cities_result = service.get_cities()
    if not cities_result.get('success'):
        return []
    
    cities = cities_result.get('cities', [])
    print(f"✅ 获取到 {len(cities)} 个城市")
    
    # 遍历前3个城市
    for city in cities[:3]:
        city_name = city.get('city_name', '未知')
        cinemas = city.get('cinemas', [])
        
        print(f"\n🏙️ 城市: {city_name} ({len(cinemas)} 个影院)")
        
        # 遍历每个影院
        for cinema in cinemas[:2]:  # 每个城市最多2个影院
            cinema_id = cinema.get('cinema_id', '')
            cinema_name = cinema.get('cinema_name', '未知影院')
            
            print(f"  🏢 影院: {cinema_name}")
            
            # 获取电影列表
            movies_result = service.get_movies(cinema_id)
            if not movies_result.get('success'):
                continue
            
            movies = movies_result.get('movies', [])
            
            # 遍历前2部电影
            for movie in movies[:2]:
                movie_id = movie.get('movie_id', movie.get('id', ''))
                movie_name = movie.get('name', '未知电影')
                
                print(f"    🎬 电影: {movie_name}")
                
                # 获取场次列表
                shows_result = service.get_shows(cinema_id, str(movie_id))
                if not shows_result.get('success'):
                    continue
                
                shows_data = shows_result.get('shows', {})
                
                # 收集所有场次
                for date, date_data in shows_data.items():
                    schedules = date_data.get('schedules', [])
                    for schedule in schedules[:3]:  # 每部电影最多3个场次
                        schedule_info = {
                            'token': token,
                            'city_name': city_name,
                            'cinema_id': cinema_id,
                            'cinema_name': cinema_name,
                            'movie_id': movie_id,
                            'movie_name': movie_name,
                            'schedule_id': schedule.get('schedule_id', ''),
                            'hall_id': schedule.get('hall_id', ''),
                            'hall_name': schedule.get('hall_name', ''),
                            'show_time': schedule.get('show_time', ''),
                            'date': date
                        }
                        all_schedules.append(schedule_info)
                        print(f"      📅 {date} {schedule.get('show_time', '')} - {schedule.get('hall_name', '')}")
    
    print(f"\n✅ 总共收集到 {len(all_schedules)} 个场次")
    return all_schedules

def test_schedule_seat_apis(schedule_info):
    """测试单个场次的座位API"""
    token = schedule_info['token']
    cinema_id = schedule_info['cinema_id']
    hall_id = schedule_info['hall_id']
    schedule_id = schedule_info['schedule_id']
    
    service = get_womei_film_service(token)
    
    result = {
        'schedule_info': schedule_info,
        'full_api': {'success': False, 'seat_count': 0},
        'saleable_api': {'success': False, 'seat_count': 0},
        'difference': 0
    }
    
    try:
        # 测试全部座位API
        hall_info_result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        if hall_info_result.get('success'):
            hall_data = hall_info_result.get('hall_info', {})
            full_count = count_seats_in_hall_data(hall_data)
            result['full_api'] = {'success': True, 'seat_count': full_count}
        
        # 测试可售座位API
        saleable_result = service.get_hall_saleable(cinema_id, schedule_id)
        if saleable_result.get('success'):
            saleable_data = saleable_result.get('saleable_info', {})
            saleable_count = count_seats_in_hall_data(saleable_data)
            result['saleable_api'] = {'success': True, 'seat_count': saleable_count}
        
        # 计算差异
        if result['full_api']['success'] and result['saleable_api']['success']:
            result['difference'] = result['full_api']['seat_count'] - result['saleable_api']['seat_count']
    
    except Exception as e:
        print(f"    ❌ 测试场次失败: {e}")
    
    return result

def count_seats_in_hall_data(hall_data):
    """统计影厅数据中的座位数量"""
    try:
        if 'room_seat' in hall_data:
            total_seats = 0
            room_seat = hall_data['room_seat']
            
            for area in room_seat:
                seats_data = area.get('seats', {})
                for row_data in seats_data.values():
                    total_seats += len(row_data.get('detail', []))
            
            return total_seats
    except:
        pass
    
    return 0

def test_all_schedules():
    """测试所有场次"""
    print(f"\n🧪 测试所有场次的座位API差异")
    print("=" * 60)
    
    # 获取所有场次
    all_schedules = get_all_schedules()
    
    if not all_schedules:
        print("❌ 没有找到可测试的场次")
        return
    
    results = []
    differences_found = []
    
    print(f"\n开始测试 {len(all_schedules)} 个场次...")
    
    for i, schedule_info in enumerate(all_schedules):
        cinema_name = schedule_info['cinema_name']
        movie_name = schedule_info['movie_name']
        show_time = schedule_info['show_time']
        date = schedule_info['date']
        
        print(f"\n[{i+1}/{len(all_schedules)}] 测试场次:")
        print(f"  影院: {cinema_name}")
        print(f"  电影: {movie_name}")
        print(f"  时间: {date} {show_time}")
        
        result = test_schedule_seat_apis(schedule_info)
        results.append(result)
        
        full_success = result['full_api']['success']
        saleable_success = result['saleable_api']['success']
        difference = result['difference']
        
        if full_success and saleable_success:
            full_count = result['full_api']['seat_count']
            saleable_count = result['saleable_api']['seat_count']
            
            print(f"  📊 全部座位: {full_count}, 可售座位: {saleable_count}, 差异: {difference}")
            
            if difference > 0:
                print(f"  🎯 发现差异! 可能有 {difference} 个已售座位")
                differences_found.append(result)
            elif difference == 0:
                print(f"  ✅ 无差异，可能无已售座位")
            else:
                print(f"  ⚠️ 异常差异: {difference}")
        else:
            print(f"  ❌ API调用失败")
        
        # 避免请求过快
        time.sleep(0.5)
    
    # 分析结果
    analyze_all_results(results, differences_found)

def analyze_all_results(results, differences_found):
    """分析所有测试结果"""
    print(f"\n📊 测试结果分析")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['full_api']['success'] and r['saleable_api']['success'])
    differences_count = len(differences_found)
    
    print(f"总测试场次: {total_tests}")
    print(f"成功测试: {successful_tests}")
    print(f"发现差异: {differences_count}")
    
    if differences_count > 0:
        print(f"\n🎯 发现API差异的场次:")
        for i, result in enumerate(differences_found):
            schedule_info = result['schedule_info']
            difference = result['difference']
            
            print(f"\n  [{i+1}] {schedule_info['cinema_name']}")
            print(f"      电影: {schedule_info['movie_name']}")
            print(f"      时间: {schedule_info['date']} {schedule_info['show_time']}")
            print(f"      影厅: {schedule_info['hall_name']}")
            print(f"      差异: {difference} 个座位")
            print(f"      全部座位: {result['full_api']['seat_count']}")
            print(f"      可售座位: {result['saleable_api']['seat_count']}")
        
        print(f"\n✅ 验证结论:")
        print(f"  在 {differences_count} 个场次中发现了API差异")
        print(f"  可售座位API确实过滤了已售座位")
        print(f"  验证了我们的理论分析")
    
    else:
        print(f"\n🤔 未发现API差异:")
        print(f"  所有测试场次的两个API返回相同数量座位")
        print(f"  可能原因:")
        print(f"    1. 测试的场次都没有已售座位")
        print(f"    2. 当前时间段购票较少")
        print(f"    3. 需要测试更多场次或不同时间")
    
    # 保存详细结果
    save_detailed_results(results, differences_found)

def save_detailed_results(results, differences_found):
    """保存详细测试结果"""
    try:
        detailed_result = {
            'title': '沃美影院多场次座位API差异测试结果',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'summary': {
                'total_tests': len(results),
                'successful_tests': sum(1 for r in results if r['full_api']['success'] and r['saleable_api']['success']),
                'differences_found': len(differences_found)
            },
            'all_results': results,
            'differences_found': differences_found
        }
        
        filename = f"multiple_schedules_test_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细测试结果已保存到: {filename}")
        
    except Exception as e:
        print(f"❌ 保存测试结果失败: {e}")

def main():
    """主函数"""
    print("🔍 沃美影院多场次座位API差异测试")
    print("=" * 60)
    print("目标: 寻找有已售座位的场次来验证API差异")
    
    test_all_schedules()

if __name__ == "__main__":
    main()
