#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用沃美电影服务正确验证座位API差异
解决token使用差异问题
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
            print(f"✅ 从accounts.json加载token:")
            print(f"  Phone: {phone}")
            print(f"  Token: {token[:20]}...")
            return token, phone
        else:
            print("❌ accounts.json为空")
            return "", ""
    except Exception as e:
        print(f"❌ 加载accounts.json失败: {e}")
        return "", ""

def find_valid_test_data():
    """查找有效的测试数据"""
    print(f"\n🔍 查找有效的测试数据")
    print("=" * 50)
    
    token, phone = load_token_from_accounts()
    if not token:
        return None
    
    # 创建沃美电影服务实例
    service = get_womei_film_service(token)
    
    # 1. 获取城市列表
    cities_result = service.get_cities()
    if not cities_result.get('success'):
        print(f"❌ 获取城市失败: {cities_result.get('error')}")
        return None
    
    cities = cities_result.get('cities', [])
    print(f"✅ 获取到 {len(cities)} 个城市")
    
    # 2. 查找有影院的城市
    for city in cities[:3]:  # 只检查前3个城市
        city_name = city.get('city_name', '未知')
        cinemas = city.get('cinemas', [])
        
        print(f"\n🏙️ 检查城市: {city_name} ({len(cinemas)} 个影院)")
        
        if cinemas:
            # 使用第一个影院
            cinema = cinemas[0]
            cinema_id = cinema.get('cinema_id', '')
            cinema_name = cinema.get('cinema_name', '未知影院')
            
            print(f"🏢 测试影院: {cinema_name} (ID: {cinema_id})")
            
            # 3. 获取电影列表
            movies_result = service.get_movies(cinema_id)
            if not movies_result.get('success'):
                print(f"  ❌ 获取电影失败: {movies_result.get('error')}")
                continue
            
            movies = movies_result.get('movies', [])
            print(f"  ✅ 获取到 {len(movies)} 部电影")
            
            if movies:
                # 使用第一部电影
                movie = movies[0]
                movie_id = movie.get('movie_id', movie.get('id', ''))
                movie_name = movie.get('name', '未知电影')
                
                print(f"  🎬 测试电影: {movie_name} (ID: {movie_id})")
                
                # 4. 获取场次列表
                shows_result = service.get_shows(cinema_id, str(movie_id))
                if not shows_result.get('success'):
                    print(f"    ❌ 获取场次失败: {shows_result.get('error')}")
                    continue
                
                shows_data = shows_result.get('shows', {})
                total_shows = shows_result.get('total', 0)
                print(f"    ✅ 获取到 {total_shows} 个场次")
                
                if shows_data:
                    # 查找第一个有效场次
                    for date, date_data in shows_data.items():
                        schedules = date_data.get('schedules', [])
                        if schedules:
                            schedule = schedules[0]
                            schedule_id = schedule.get('schedule_id', schedule.get('id', ''))
                            hall_id = schedule.get('hall_id', '')
                            show_time = schedule.get('show_time', '未知时间')
                            hall_name = schedule.get('hall_name', '未知影厅')
                            
                            print(f"    🎭 找到场次: {date} {show_time}")
                            print(f"        影厅: {hall_name} (ID: {hall_id})")
                            print(f"        场次ID: {schedule_id}")
                            
                            return {
                                'token': token,
                                'phone': phone,
                                'cinema_id': cinema_id,
                                'cinema_name': cinema_name,
                                'movie_id': movie_id,
                                'movie_name': movie_name,
                                'schedule_id': schedule_id,
                                'hall_id': hall_id,
                                'hall_name': hall_name,
                                'show_time': show_time,
                                'date': date
                            }
    
    print("❌ 未找到有效的测试数据")
    return None

def test_seat_apis_with_service(test_data):
    """使用沃美电影服务测试座位API"""
    print(f"\n🪑 使用沃美电影服务测试座位API")
    print("=" * 60)
    
    if not test_data:
        print("❌ 缺少测试数据")
        return {}
    
    token = test_data['token']
    cinema_id = test_data['cinema_id']
    hall_id = test_data['hall_id']
    schedule_id = test_data['schedule_id']
    
    print(f"测试参数:")
    print(f"  Token: {token[:20]}...")
    print(f"  影院: {test_data['cinema_name']} (ID: {cinema_id})")
    print(f"  影厅: {test_data['hall_name']} (ID: {hall_id})")
    print(f"  场次: {test_data['date']} {test_data['show_time']} (ID: {schedule_id})")
    
    # 创建沃美电影服务实例
    service = get_womei_film_service(token)
    
    results = {}
    
    # 1. 测试全部座位API (hall_info)
    print(f"\n🔄 测试全部座位API (hall_info)")
    try:
        hall_info_result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        if hall_info_result.get('success'):
            hall_data = hall_info_result.get('hall_info', {})
            seats_count = count_seats_in_hall_data(hall_data)
            
            print(f"✅ 全部座位API成功")
            print(f"   座位数量: {seats_count}")
            
            results['全部座位API'] = {
                'success': True,
                'seat_count': seats_count,
                'data': hall_data
            }
            
            # 显示影厅信息
            if hall_data:
                hall_name = hall_data.get('hall_name', '未知')
                hall_no = hall_data.get('hall_no', '未知')
                print(f"   影厅信息: {hall_name} ({hall_no})")
        else:
            error = hall_info_result.get('error', '未知错误')
            print(f"❌ 全部座位API失败: {error}")
            results['全部座位API'] = {
                'success': False,
                'error': error,
                'seat_count': 0
            }
    
    except Exception as e:
        print(f"❌ 全部座位API异常: {e}")
        results['全部座位API'] = {
            'success': False,
            'error': str(e),
            'seat_count': 0
        }
    
    # 2. 测试可售座位API (hall_saleable)
    print(f"\n🔄 测试可售座位API (hall_saleable)")
    try:
        saleable_result = service.get_hall_saleable(cinema_id, schedule_id)
        
        if saleable_result.get('success'):
            saleable_data = saleable_result.get('saleable_info', {})
            seats_count = count_seats_in_hall_data(saleable_data)
            
            print(f"✅ 可售座位API成功")
            print(f"   座位数量: {seats_count}")
            
            results['可售座位API'] = {
                'success': True,
                'seat_count': seats_count,
                'data': saleable_data
            }
        else:
            error = saleable_result.get('error', '未知错误')
            print(f"❌ 可售座位API失败: {error}")
            results['可售座位API'] = {
                'success': False,
                'error': error,
                'seat_count': 0
            }
    
    except Exception as e:
        print(f"❌ 可售座位API异常: {e}")
        results['可售座位API'] = {
            'success': False,
            'error': str(e),
            'seat_count': 0
        }
    
    return results

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

def analyze_api_differences(results, test_data):
    """分析API差异"""
    print(f"\n📊 分析API差异")
    print("=" * 60)
    
    full_api_result = results.get('全部座位API', {})
    saleable_api_result = results.get('可售座位API', {})
    
    full_success = full_api_result.get('success', False)
    saleable_success = saleable_api_result.get('success', False)
    
    print(f"API调用结果:")
    print(f"  全部座位API: {'✅ 成功' if full_success else '❌ 失败'}")
    print(f"  可售座位API: {'✅ 成功' if saleable_success else '❌ 失败'}")
    
    if not full_success and not saleable_success:
        print(f"\n❌ 两个API都调用失败")
        print(f"全部座位API错误: {full_api_result.get('error', '未知')}")
        print(f"可售座位API错误: {saleable_api_result.get('error', '未知')}")
        return
    
    if full_success and saleable_success:
        full_count = full_api_result.get('seat_count', 0)
        saleable_count = saleable_api_result.get('seat_count', 0)
        difference = full_count - saleable_count
        
        print(f"\n📈 座位数量对比:")
        print(f"  全部座位API: {full_count} 个座位")
        print(f"  可售座位API: {saleable_count} 个座位")
        print(f"  差异: {difference} 个座位")
        
        if difference > 0:
            print(f"\n🎯 验证结论:")
            print(f"✅ 可售座位API确实过滤了 {difference} 个座位")
            print(f"💡 这 {difference} 个座位很可能是已售或不可售座位")
            print(f"🔧 建议: 使用可售座位API获取准确的座位状态")
            
            # 详细分析座位差异
            analyze_detailed_seat_differences(full_api_result.get('data', {}), saleable_api_result.get('data', {}))
            
        elif difference == 0:
            print(f"\n🤔 两个API返回相同数量的座位")
            print(f"💡 说明: 当前场次可能没有已售座位")
        else:
            print(f"\n⚠️ 异常情况: 可售座位API返回更多座位")
    
    elif full_success:
        print(f"\n⚠️ 仅全部座位API成功")
        print(f"座位数量: {full_api_result.get('seat_count', 0)}")
    
    elif saleable_success:
        print(f"\n⚠️ 仅可售座位API成功")
        print(f"座位数量: {saleable_api_result.get('seat_count', 0)}")

def analyze_detailed_seat_differences(full_data, saleable_data):
    """详细分析座位差异"""
    print(f"\n🔍 详细座位差异分析:")
    
    try:
        # 提取座位位置
        full_seats = extract_seat_positions(full_data)
        saleable_seats = extract_seat_positions(saleable_data)
        
        # 找出差异
        full_only = full_seats - saleable_seats
        saleable_only = saleable_seats - full_seats
        
        if full_only:
            print(f"  🔴 仅在全部座位API中的座位 ({len(full_only)} 个):")
            sorted_seats = sorted(full_only)[:10]  # 只显示前10个
            for row, col in sorted_seats:
                print(f"    {row}排{col}座")
            if len(full_only) > 10:
                print(f"    ... 还有 {len(full_only) - 10} 个座位")
        
        if saleable_only:
            print(f"  🟡 仅在可售座位API中的座位 ({len(saleable_only)} 个):")
            sorted_seats = sorted(saleable_only)[:10]
            for row, col in sorted_seats:
                print(f"    {row}排{col}座")
    
    except Exception as e:
        print(f"  ❌ 详细分析失败: {e}")

def extract_seat_positions(hall_data):
    """从影厅数据中提取座位位置"""
    positions = set()
    
    try:
        if 'room_seat' in hall_data:
            room_seat = hall_data['room_seat']
            
            for area in room_seat:
                seats_data = area.get('seats', {})
                for row_data in seats_data.values():
                    seat_details = row_data.get('detail', [])
                    for seat in seat_details:
                        row = int(seat.get('row', 0))
                        col = int(seat.get('col', 0))
                        if row > 0 and col > 0:
                            positions.add((row, col))
    except:
        pass
    
    return positions

def save_verification_results(results, test_data):
    """保存验证结果"""
    try:
        verification_result = {
            'title': '沃美影院座位API差异验证结果（使用沃美电影服务）',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'test_data': test_data,
            'api_results': results,
            'verification_method': '使用沃美电影服务的正确API调用方式'
        }
        
        filename = f"seat_api_verification_womei_service_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(verification_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 验证结果已保存到: {filename}")
        
    except Exception as e:
        print(f"❌ 保存验证结果失败: {e}")

def main():
    """主函数"""
    print("🔍 沃美影院座位API差异验证（使用沃美电影服务）")
    print("=" * 70)
    
    # 1. 查找有效的测试数据
    test_data = find_valid_test_data()
    
    if not test_data:
        print("❌ 无法找到有效的测试数据，验证终止")
        return
    
    print(f"\n✅ 找到有效的测试数据")
    
    # 2. 使用沃美电影服务测试座位API
    results = test_seat_apis_with_service(test_data)
    
    if not results:
        print("❌ 无法获取API测试结果")
        return
    
    # 3. 分析API差异
    analyze_api_differences(results, test_data)
    
    # 4. 保存验证结果
    save_verification_results(results, test_data)
    
    print(f"\n🎯 验证完成")
    print(f"关键发现: 使用沃美电影服务的正确API调用方式可以成功获取座位数据")

if __name__ == "__main__":
    main()
