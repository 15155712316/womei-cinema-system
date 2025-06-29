#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单订单生成器 - 直接使用现有的沃美影院服务
"""

import sys
import os
import json
import time
import random
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_account():
    """加载账号信息"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts:
            account = accounts[0]
            return account.get('token', ''), account.get('phone', '')
        
        return '', ''
    except Exception as e:
        print(f"❌ 加载账号失败: {e}")
        return '', ''

def generate_order():
    """生成订单"""
    print("🎬 简单订单生成器")
    print("🎯 使用现有沃美影院服务")
    print("⏰ 开始时间:", time.strftime("%H:%M:%S"))
    print("=" * 80)
    
    # 1. 加载账号
    token, phone = load_account()
    if not token:
        print("❌ 未找到token")
        return None
    
    print(f"📋 账号信息: {phone}")
    print(f"📋 Token: {token[:20]}...")
    
    try:
        # 2. 导入现有的沃美电影服务
        from services.womei_film_service import get_womei_film_service
        
        film_service = get_womei_film_service(token)
        
        # 🔧 修复：优先使用HAR文件中成功的影院ID
        test_cinema_ids = ["400303", "400028", "400001", "400002"]
        
        cinema_id = None
        for cid in test_cinema_ids:
            print(f"\n🏢 测试影院: {cid}")
            
            # 获取电影列表来验证影院是否可用
            movies_result = film_service.get_movies(cid)
            
            if movies_result.get('success'):
                movies = movies_result.get('movies', [])
                print(f"   ✅ 影院可用，找到 {len(movies)} 部电影")
                
                if movies:
                    cinema_id = cid
                    break
            else:
                print(f"   ❌ 影院不可用: {movies_result.get('error', '未知错误')}")
        
        if not cinema_id:
            print("❌ 没有找到可用的影院")
            return None
        
        print(f"\n✅ 选择影院: {cinema_id}")
        
        # 4. 获取电影列表
        print(f"\n🎬 获取电影列表")
        movies_result = film_service.get_movies(cinema_id)
        
        if not movies_result.get('success'):
            print(f"❌ 获取电影失败: {movies_result.get('error')}")
            return None
        
        movies = movies_result.get('movies', [])
        if not movies:
            print("❌ 没有找到电影")
            return None
        
        # 随机选择一部电影
        selected_movie = random.choice(movies)
        movie_id = selected_movie.get('movie_id')  # 沃美API返回的字段是movie_id
        movie_name = selected_movie.get('name', '未知电影')
        
        print(f"   🎲 随机选择电影: {movie_name} (ID: {movie_id})")
        
        # 5. 获取场次列表
        print(f"\n📅 获取场次列表")
        shows_result = film_service.get_shows(cinema_id, movie_id)
        
        if not shows_result.get('success'):
            print(f"❌ 获取场次失败: {shows_result.get('error')}")
            return None
        
        shows_data = shows_result.get('shows', {})
        if not shows_data:
            print("❌ 没有找到场次")
            return None
        
        # 找到未来的场次
        now = datetime.now()
        future_shows = []
        
        for date_str, date_shows in shows_data.items():
            schedules = date_shows.get('schedules', [])
            for schedule in schedules:
                show_time_str = schedule.get('show_time', '')
                show_date_str = schedule.get('show_date', '')
                try:
                    # 沃美API返回的格式：show_date='20250629', show_time='23:00'
                    full_time_str = f"{show_date_str} {show_time_str}:00"
                    show_time = datetime.strptime(full_time_str, '%Y%m%d %H:%M:%S')
                    if show_time > now:
                        # 添加完整的时间字符串到schedule中
                        schedule['full_show_time'] = show_time.strftime('%Y-%m-%d %H:%M:%S')
                        future_shows.append(schedule)
                except Exception as e:
                    print(f"   时间解析失败: {show_time_str}, {show_date_str}, 错误: {e}")
                    continue
        
        if not future_shows:
            print("❌ 没有找到未来的场次")
            return None
        
        # 随机选择一个场次
        selected_show = random.choice(future_shows)
        schedule_id = selected_show.get('schedule_id')
        show_time = selected_show.get('full_show_time', selected_show.get('show_time'))
        
        print(f"   🎲 随机选择场次: {show_time} (ID: {schedule_id})")
        
        # 6. 获取座位信息
        print(f"\n💺 获取座位信息")
        # 使用正确的方法名和参数
        seats_result = film_service.get_hall_saleable(cinema_id, schedule_id)
        
        if not seats_result.get('success'):
            print(f"❌ 获取座位失败: {seats_result.get('error')}")
            return None
        
        # 沃美API返回的座位数据结构
        seats_data = seats_result.get('saleable_info', {})
        room_seat = seats_data.get('room_seat', [])

        if not room_seat:
            print("❌ 没有找到座位数据")
            return None

        # 解析座位数据
        all_seats = []
        for area in room_seat:
            seats_by_row = area.get('seats', {})
            for row_key, row_data in seats_by_row.items():
                row_seats = row_data.get('detail', [])
                for seat in row_seats:
                    all_seats.append(seat)

        print(f"   总座位数: {len(all_seats)}")

        # 筛选可用座位 (status=0)
        available_seats = [seat for seat in all_seats if seat.get('status') == 0]
        
        if len(available_seats) < 1:
            print("❌ 没有可用座位")
            return None
        
        # 选择多个座位备选
        max_attempts = min(5, len(available_seats))  # 最多尝试5个座位
        selected_seats_pool = random.sample(available_seats, max_attempts)

        print(f"   准备尝试 {len(selected_seats_pool)} 个座位:")
        
        # 7. 创建订单（尝试多个座位）
        print(f"\n📝 创建订单")

        order_result = None
        selected_seats = None

        for i, seat in enumerate(selected_seats_pool, 1):
            row = seat.get('row', 'N/A')
            col = seat.get('col', 'N/A')
            seat_no = seat.get('seat_no', '')

            # 🔧 修复：构建正确的沃美座位参数格式
            # 格式：area_id:row:col:seat_no
            # 从座位数据中获取区域信息
            area_no = "1"  # 默认区域，可以从API响应中获取

            # 构建完整的座位参数
            seatlable_param = f"{area_no}:{row}:{col}:{seat_no}"

            print(f"   尝试座位{i}: {row}排{col}座")
            print(f"   座位参数: {seatlable_param}")

            order_result = film_service.create_order(
                cinema_id=cinema_id,
                seatlable=seatlable_param,
                schedule_id=schedule_id
            )

            if order_result and order_result.get('success'):
                selected_seats = [seat]  # 成功的座位
                print(f"   ✅ 座位{i}创建订单成功!")
                break
            else:
                error_msg = order_result.get('error', '未知错误') if order_result else '网络错误'
                print(f"   ❌ 座位{i}失败: {error_msg}")

                # 如果是最后一个座位，记录失败
                if i == len(selected_seats_pool):
                    print(f"   ❌ 所有座位都尝试失败")
        
        if not order_result.get('success'):
            print(f"❌ 订单创建失败: {order_result.get('error')}")
            return None
        
        order_id = order_result.get('order_id')
        order_info = order_result.get('order_info', {})
        
        print(f"   ✅ 订单创建成功!")
        print(f"   订单号: {order_id}")
        
        # 8. 整理结果
        result = {
            "success": True,
            "order_info": {
                "order_id": order_id,
                "cinema_id": cinema_id,
                "movie_id": movie_id,
                "movie_name": movie_name,
                "schedule_id": schedule_id,
                "show_time": show_time,
                "seat_count": len(selected_seats),
                "created_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "expires_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 600))  # 10分钟后过期
            },
            "raw_data": {
                "movie": selected_movie,
                "show": selected_show,
                "seats": selected_seats,
                "order": order_info
            }
        }
        
        print(f"\n🎉 订单生成成功!")
        print("=" * 80)
        print(f"📋 订单信息:")
        print(f"   订单号: {order_id}")
        print(f"   影院ID: {cinema_id}")
        print(f"   电影: {movie_name}")
        print(f"   场次: {show_time}")
        print(f"   座位数: {len(selected_seats)}")
        print(f"   创建时间: {result['order_info']['created_time']}")
        print(f"   过期时间: {result['order_info']['expires_at']}")
        
        print(f"\n⏰ 重要提醒:")
        print(f"   订单有效期: 10分钟")
        print(f"   请在 {result['order_info']['expires_at']} 前使用")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 订单生成失败: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

def main():
    """主函数"""
    try:
        # 生成订单
        result = generate_order()
        
        # 保存结果
        filename = f"simple_order_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n📁 结果已保存到: {filename}")
        
        if result and result.get('success'):
            order_id = result['order_info']['order_id']
            print(f"\n🎯 可用于测试的订单号: {order_id}")
            print(f"💡 现在可以立即测试券绑定:")
            print(f"   python test_voucher_with_provided_order.py")
            print(f"   # 将订单号 {order_id} 添加到测试脚本中")
            
            return order_id
        else:
            print(f"\n❌ 订单生成失败，请检查错误信息")
            return None
            
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
