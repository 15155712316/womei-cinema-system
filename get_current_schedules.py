#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取当前可用的场次信息
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_current_schedules():
    """获取当前可用的场次"""
    
    base_url = "https://ct.womovie.cn"
    token = "afebc43f2b18da363fd78a6a10b01b72"
    cinema_id = "9934"
    
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Client-Version': '4.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Priority': 'u=1, i',
        'Referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Tenant-Short': 'wmyc',
        'Token': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'X-Channel-Id': '40000',
        'X-Requested-With': 'wxapp',
        'Xweb_Xhr': '1',
    }
    
    # 获取电影列表
    print("🎬 获取当前电影和场次信息")
    print("=" * 60)
    
    movies_url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/movies/"
    
    try:
        response = requests.get(movies_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"📥 电影列表响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            if result.get('ret') == 0:
                movies = result.get('data', [])
                print(f"\n✅ 获取到 {len(movies)} 部电影")
                
                # 查找有可用场次的电影
                for movie in movies[:3]:  # 只看前3部电影
                    movie_id = movie.get('movie_id')
                    movie_name = movie.get('movie_name')
                    
                    print(f"\n🎬 电影: {movie_name} (ID: {movie_id})")
                    
                    # 获取该电影的场次
                    schedules_url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/movie/{movie_id}/schedules/"
                    
                    try:
                        schedule_response = requests.get(schedules_url, headers=headers, timeout=10, verify=False)
                        
                        if schedule_response.status_code == 200:
                            schedule_result = schedule_response.json()
                            
                            if schedule_result.get('ret') == 0:
                                schedules = schedule_result.get('data', [])
                                print(f"   📅 场次数量: {len(schedules)}")
                                
                                # 显示前几个场次
                                for i, schedule in enumerate(schedules[:3]):
                                    schedule_id = schedule.get('schedule_id')
                                    show_time = schedule.get('show_time')
                                    hall_name = schedule.get('hall_name')
                                    
                                    print(f"   {i+1}. 场次ID: {schedule_id}")
                                    print(f"      时间: {show_time}")
                                    print(f"      影厅: {hall_name}")
                                    
                                    # 如果是第一个场次，尝试获取座位信息
                                    if i == 0:
                                        print(f"\n🪑 获取场次 {schedule_id} 的座位信息:")
                                        get_seats_info(base_url, headers, cinema_id, schedule_id)
                                        
                                        # 返回第一个可用的场次信息
                                        return {
                                            'cinema_id': cinema_id,
                                            'schedule_id': schedule_id,
                                            'movie_name': movie_name,
                                            'show_time': show_time,
                                            'hall_name': hall_name
                                        }
                            else:
                                print(f"   ❌ 获取场次失败: {schedule_result.get('msg')}")
                        else:
                            print(f"   ❌ HTTP失败: {schedule_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ 异常: {e}")
            else:
                print(f"❌ 获取电影失败: {result.get('msg')}")
        else:
            print(f"❌ HTTP失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    
    return None

def get_seats_info(base_url, headers, cinema_id, schedule_id):
    """获取座位信息"""
    seats_url = f"{base_url}/ticket/wmyc/cinema/{cinema_id}/schedule/{schedule_id}/seats/"
    
    try:
        response = requests.get(seats_url, headers=headers, timeout=10, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('ret') == 0:
                data = result.get('data', {})
                seats = data.get('seats', [])
                
                print(f"   📊 座位总数: {len(seats)}")
                
                # 查找可用座位
                available_seats = []
                for seat in seats:
                    if seat.get('status') == 0:  # 0表示可用
                        available_seats.append(seat)
                
                print(f"   ✅ 可用座位: {len(available_seats)}")
                
                # 显示前几个可用座位
                if available_seats:
                    print(f"   🪑 前几个可用座位:")
                    for i, seat in enumerate(available_seats[:5]):
                        row = seat.get('row')
                        col = seat.get('col')
                        seat_id = seat.get('seat_id')
                        print(f"      {i+1}. {row}排{col}座 (ID: {seat_id})")
                    
                    # 生成座位字符串示例
                    if len(available_seats) >= 2:
                        seat1 = available_seats[0]
                        seat2 = available_seats[1]
                        
                        # 构造座位字符串
                        seatlable = f"{seat1['seat_id']}:{seat1['row']}:{seat1['col']}:{schedule_id}#{seat1['row']:02d}#{seat1['col']:02d}|{seat2['seat_id']}:{seat2['row']}:{seat2['col']}:{schedule_id}#{seat2['row']:02d}#{seat2['col']:02d}"
                        
                        print(f"\n   📝 座位字符串示例:")
                        print(f"      {seatlable}")
                        
                        return seatlable
            else:
                print(f"   ❌ 获取座位失败: {result.get('msg')}")
        else:
            print(f"   ❌ HTTP失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 异常: {e}")
    
    return None

def main():
    """主函数"""
    schedule_info = get_current_schedules()
    
    if schedule_info:
        print(f"\n🎯 推荐使用的场次信息:")
        print(f"   影院ID: {schedule_info['cinema_id']}")
        print(f"   场次ID: {schedule_info['schedule_id']}")
        print(f"   电影: {schedule_info['movie_name']}")
        print(f"   时间: {schedule_info['show_time']}")
        print(f"   影厅: {schedule_info['hall_name']}")
    else:
        print(f"\n❌ 未找到可用的场次信息")

if __name__ == "__main__":
    main()
