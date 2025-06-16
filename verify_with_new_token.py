#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用最新token验证沃美影院座位API差异
"""

import requests
import json
import time
import urllib3
from typing import Dict, List

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_latest_token():
    """加载最新的token"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            token = accounts[0].get('token', '')
            print(f"✅ 加载最新token: {token[:20]}...")
            return token
        else:
            print("❌ 账号文件为空")
            return ""
    except Exception as e:
        print(f"❌ 加载账号文件失败: {e}")
        return ""

def get_recent_schedule():
    """获取最近的场次ID"""
    token = load_latest_token()
    if not token:
        return None, None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'tenant-short': 'wmyc'
    }
    
    cinema_id = "400028"
    
    print(f"\n🔍 获取最近的场次")
    print("=" * 40)
    
    # 1. 获取电影列表
    movies_url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/movies/'
    try:
        response = requests.get(movies_url, params={'token': token}, headers=headers, timeout=10, verify=False)
        print(f"电影API状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ret') == 0 and data.get('data'):
                movies = data['data']
                print(f"✅ 获取到 {len(movies)} 部电影")
                
                # 使用第一部电影
                movie = movies[0]
                movie_id = movie.get('movie_id', movie.get('id', ''))
                movie_name = movie.get('name', '未知电影')
                print(f"测试电影: {movie_name} (ID: {movie_id})")
                
                # 2. 获取场次
                shows_url = f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/shows/'
                shows_response = requests.get(shows_url, params={'movie_id': movie_id, 'token': token}, headers=headers, timeout=10, verify=False)
                
                if shows_response.status_code == 200:
                    shows_data = shows_response.json()
                    if shows_data.get('ret') == 0 and shows_data.get('data'):
                        shows_dict = shows_data['data']
                        print(f"✅ 获取到场次数据")
                        
                        # 查找最近的场次
                        for date, date_data in shows_dict.items():
                            schedules = date_data.get('schedules', [])
                            if schedules:
                                schedule = schedules[0]
                                schedule_id = schedule.get('schedule_id', schedule.get('id', ''))
                                show_time = schedule.get('show_time', '未知时间')
                                
                                print(f"✅ 找到场次: {date} {show_time} (ID: {schedule_id})")
                                return cinema_id, schedule_id
                
    except Exception as e:
        print(f"❌ 获取场次失败: {e}")
    
    return None, None

def test_seat_apis(cinema_id, schedule_id):
    """测试两个座位API"""
    token = load_latest_token()
    if not token:
        return {}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type': 'application/json',
        'Referer': 'https://servicewechat.com/wx4080846d0cec2fd5/78/page-frame.html',
        'tenant-short': 'wmyc'
    }
    
    params = {
        'schedule_id': schedule_id,
        'token': token
    }
    
    print(f"\n🪑 测试座位API")
    print(f"影院ID: {cinema_id}")
    print(f"场次ID: {schedule_id}")
    print(f"Token: {token[:20]}...")
    print("=" * 50)
    
    # 测试两个API
    apis = [
        {
            'name': '全部座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/info/'
        },
        {
            'name': '可售座位API',
            'url': f'https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/hall/saleable/'
        }
    ]
    
    results = {}
    
    for api in apis:
        print(f"\n🔄 测试 {api['name']}")
        print(f"URL: {api['url']}")
        print(f"参数: {params}")
        
        try:
            response = requests.get(api['url'], params=params, headers=headers, timeout=30, verify=False)
            
            print(f"状态码: {response.status_code}")
            print(f"响应大小: {len(response.text)} 字符")
            print(f"原始响应: {response.text[:200]}...")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"JSON解析成功")
                    
                    ret = data.get('ret', -1)
                    msg = data.get('msg', '')
                    
                    if ret == 0 and data.get('data') and len(str(data.get('data'))) > 10:
                        print(f"✅ {api['name']}获取成功")
                        
                        # 解析座位数据
                        seats = extract_seats_from_response(data)
                        results[api['name']] = {
                            'success': True,
                            'seats': seats,
                            'total': len(seats),
                            'raw_data': data
                        }
                        print(f"座位数量: {len(seats)}")
                        
                        # 显示前几个座位作为示例
                        if seats:
                            print(f"示例座位:")
                            for seat in seats[:3]:
                                print(f"  {seat['row']}排{seat['col']}座 - {seat['area_name']} (状态: {seat['status']})")
                    else:
                        print(f"❌ {api['name']}返回错误: {msg}")
                        results[api['name']] = {
                            'success': False,
                            'error': msg,
                            'seats': [],
                            'total': 0
                        }
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    results[api['name']] = {
                        'success': False,
                        'error': f'JSON解析失败: {e}',
                        'seats': [],
                        'total': 0
                    }
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                results[api['name']] = {
                    'success': False,
                    'error': f'HTTP错误: {response.status_code}',
                    'seats': [],
                    'total': 0
                }
        
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            results[api['name']] = {
                'success': False,
                'error': str(e),
                'seats': [],
                'total': 0
            }
    
    return results

def extract_seats_from_response(data):
    """从API响应中提取座位信息"""
    seats = []
    try:
        if 'data' in data and 'room_seat' in data['data']:
            room_seat = data['data']['room_seat']
            
            for area in room_seat:
                area_name = area.get('area_name', '未知区域')
                area_price = area.get('area_price', 0)
                seats_data = area.get('seats', {})
                
                if isinstance(seats_data, dict):
                    for row_key, row_data in seats_data.items():
                        seat_details = row_data.get('detail', [])
                        
                        for seat_detail in seat_details:
                            seat_info = {
                                'seat_no': seat_detail.get('seat_no', ''),
                                'row': seat_detail.get('row', 0),
                                'col': seat_detail.get('col', 0),
                                'x': seat_detail.get('x', 0),
                                'y': seat_detail.get('y', 0),
                                'status': seat_detail.get('status', 0),
                                'type': seat_detail.get('type', 0),
                                'area_name': area_name,
                                'area_price': area_price
                            }
                            seats.append(seat_info)
    
    except Exception as e:
        print(f"❌ 解析座位数据失败: {e}")
    
    return seats

def analyze_differences(results):
    """分析API差异"""
    print(f"\n📊 分析API差异")
    print("=" * 50)
    
    full_api_result = results.get('全部座位API', {})
    saleable_api_result = results.get('可售座位API', {})
    
    full_seats = full_api_result.get('seats', [])
    saleable_seats = saleable_api_result.get('seats', [])
    
    print(f"全部座位API: {len(full_seats)} 个座位")
    print(f"可售座位API: {len(saleable_seats)} 个座位")
    
    if len(full_seats) == 0 and len(saleable_seats) == 0:
        print("⚠️ 两个API都没有返回座位数据")
        return
    
    # 创建座位映射
    full_seats_map = {}
    saleable_seats_map = {}
    
    for seat in full_seats:
        key = (seat['row'], seat['col'])
        full_seats_map[key] = seat
    
    for seat in saleable_seats:
        key = (seat['row'], seat['col'])
        saleable_seats_map[key] = seat
    
    # 分析差异
    full_only = set(full_seats_map.keys()) - set(saleable_seats_map.keys())
    saleable_only = set(saleable_seats_map.keys()) - set(full_seats_map.keys())
    common = set(full_seats_map.keys()) & set(saleable_seats_map.keys())
    
    print(f"\n📈 差异分析:")
    print(f"  仅在全部座位API中: {len(full_only)} 个座位")
    print(f"  仅在可售座位API中: {len(saleable_only)} 个座位")
    print(f"  两个API共有: {len(common)} 个座位")
    
    # 显示差异座位
    if full_only:
        print(f"\n🔴 仅在全部座位API中的座位（可能已售）:")
        for row, col in sorted(full_only)[:10]:  # 只显示前10个
            seat = full_seats_map[(row, col)]
            print(f"  {row}排{col}座 - {seat['seat_no']} - {seat['area_name']} (状态: {seat['status']})")
    
    if saleable_only:
        print(f"\n🟡 仅在可售座位API中的座位（异常情况）:")
        for row, col in sorted(saleable_only)[:10]:  # 只显示前10个
            seat = saleable_seats_map[(row, col)]
            print(f"  {row}排{col}座 - {seat['seat_no']} - {seat['area_name']} (状态: {seat['status']})")
    
    # 检查重点座位
    target_seats = [(1, 9), (1, 10), (1, 11), (1, 12), (8, 6), (8, 7)]
    print(f"\n🎯 重点座位检查:")
    for row, col in target_seats:
        in_full = (row, col) in full_seats_map
        in_saleable = (row, col) in saleable_seats_map
        
        print(f"  {row}排{col}座:")
        print(f"    全部座位API: {'✅ 存在' if in_full else '❌ 不存在'}")
        print(f"    可售座位API: {'✅ 存在' if in_saleable else '❌ 不存在'}")
        
        if in_full and not in_saleable:
            seat = full_seats_map[(row, col)]
            print(f"    🔴 结论: 该座位已售出 (状态: {seat['status']})")
        elif not in_full and in_saleable:
            print(f"    🟡 异常: 仅在可售座位API中存在")
        elif in_full and in_saleable:
            print(f"    🟢 结论: 该座位可售")
        else:
            print(f"    ⚫ 结论: 该座位不存在")
    
    # 输出最终结论
    print_final_conclusion(len(full_seats), len(saleable_seats), len(full_only), len(saleable_only))

def print_final_conclusion(full_count, saleable_count, full_only, saleable_only):
    """输出最终结论"""
    print(f"\n🎯 验证结论")
    print("=" * 50)
    
    if full_count > saleable_count and full_only > 0 and saleable_only == 0:
        print(f"✅ 验证成功: 可售座位API确实只返回可售座位")
        print(f"📊 证据: 全部座位API比可售座位API多 {full_only} 个座位")
        print(f"💡 说明: 这 {full_only} 个座位很可能是已售座位")
        print(f"🔧 建议: 使用可售座位API获取准确的座位状态")
    elif full_count == saleable_count and full_only == 0 and saleable_only == 0:
        print(f"🤔 相同结果: 两个API返回的座位数据完全一致")
        print(f"💡 说明: 当前场次可能没有已售座位")
    elif full_count == 0 and saleable_count == 0:
        print(f"⚠️ 无数据: 两个API都没有返回座位数据")
        print(f"💡 说明: 可能是token过期或场次无效")
    else:
        print(f"🔄 复杂情况: API返回数据存在差异")
        print(f"📊 数据: 全部座位{full_count}个，可售座位{saleable_count}个")

def save_results(results, cinema_id, schedule_id):
    """保存验证结果"""
    try:
        verification_result = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'cinema_id': cinema_id,
            'schedule_id': schedule_id,
            'token_used': load_latest_token()[:20] + "...",
            'results': results
        }
        
        filename = f"seat_api_verification_new_token_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(verification_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 验证结果已保存到: {filename}")
        
    except Exception as e:
        print(f"❌ 保存验证结果失败: {e}")

def main():
    """主函数"""
    print("🔍 沃美影院座位API差异验证（使用最新token）")
    print("=" * 60)
    
    # 1. 获取最近的场次
    cinema_id, schedule_id = get_recent_schedule()
    
    if not cinema_id or not schedule_id:
        print("❌ 无法获取有效的场次，验证终止")
        return
    
    # 2. 测试座位API
    results = test_seat_apis(cinema_id, schedule_id)
    
    if not results:
        print("❌ 无法获取API测试结果")
        return
    
    # 3. 分析差异
    analyze_differences(results)
    
    # 4. 保存结果
    save_results(results, cinema_id, schedule_id)

if __name__ == "__main__":
    main()
