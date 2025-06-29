#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影城订单生成脚本
自动创建真实有效的订单号，供券绑定测试等功能使用
"""

import sys
import os
import json
import requests
import urllib3
import time
import random
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WomeiOrderGenerator:
    """沃美影城订单生成器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn/ticket/wmyc"
        self.token = None
        self.phone = None
        self.preferred_cinema_id = "400028"  # 北京沃美世界城店
        self.load_account()
    
    def load_account(self):
        """加载账号信息"""
        try:
            with open('data/accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            if accounts:
                # 优先使用指定影院的账号
                for account in accounts:
                    if account.get('cinema_id') == self.preferred_cinema_id:
                        self.token = account.get('token', '')
                        self.phone = account.get('phone', '')
                        print(f"✅ 使用指定影院账号: {self.phone}")
                        return
                
                # 如果没有找到，使用第一个账号
                self.token = accounts[0].get('token', '')
                self.phone = accounts[0].get('phone', '')
                print(f"✅ 使用默认账号: {self.phone}")
            else:
                raise Exception("账号列表为空")
                
        except Exception as e:
            print(f"❌ 加载账号失败: {e}")
            raise
    
    def get_headers(self):
        """获取请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'token': self.token,
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9'
        }
    
    def get_available_cinemas(self):
        """获取可用影院列表"""
        print("🏢 获取可用影院列表")
        print("-" * 60)
        
        # 测试常见的影院ID
        test_cinema_ids = [self.preferred_cinema_id, "400303", "400001", "400002", "400010"]
        available_cinemas = []
        
        headers = self.get_headers()
        
        for cinema_id in test_cinema_ids:
            try:
                url = f"{self.base_url}/cinema/{cinema_id}/info/"
                response = requests.get(url, headers=headers, verify=False, timeout=15)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ret') == 0 and result.get('sub') == 0:
                        cinema_data = result.get('data', {})
                        cinema_name = cinema_data.get('cinema_name', f'影院{cinema_id}')
                        available_cinemas.append({
                            'cinema_id': cinema_id,
                            'cinema_name': cinema_name,
                            'data': cinema_data
                        })
                        print(f"   ✅ {cinema_id}: {cinema_name}")
                    else:
                        print(f"   ❌ {cinema_id}: {result.get('msg', '访问失败')}")
                else:
                    print(f"   ❌ {cinema_id}: HTTP {response.status_code}")
            
            except Exception as e:
                print(f"   ❌ {cinema_id}: 请求异常 {e}")
        
        if not available_cinemas:
            raise Exception("没有找到可用的影院")
        
        # 优先选择指定影院
        for cinema in available_cinemas:
            if cinema['cinema_id'] == self.preferred_cinema_id:
                print(f"   🎯 选择优先影院: {cinema['cinema_name']}")
                return cinema
        
        # 随机选择其他影院
        selected = random.choice(available_cinemas)
        print(f"   🎲 随机选择影院: {selected['cinema_name']}")
        return selected
    
    def get_current_movies(self, cinema_id):
        """获取当前上映电影"""
        print(f"🎬 获取影院 {cinema_id} 的上映电影")
        print("-" * 60)

        headers = self.get_headers()
        # 使用正确的沃美API端点
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/movies/"

        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)

            if response.status_code == 200:
                result = response.json()
                if result.get('ret') == 0 and result.get('sub') == 0:
                    films = result.get('data', [])
                    print(f"   找到 {len(films)} 部电影")

                    if films:
                        # 随机选择一部电影
                        selected_film = random.choice(films)
                        film_name = selected_film.get('film_name', '未知电影')
                        film_id = selected_film.get('film_id', '')

                        print(f"   🎲 随机选择: {film_name} (ID: {film_id})")
                        return selected_film
                    else:
                        raise Exception("没有找到上映电影")
                else:
                    raise Exception(f"获取电影失败: {result.get('msg', '未知错误')}")
            else:
                raise Exception(f"HTTP错误: {response.status_code}")

        except Exception as e:
            print(f"   ❌ 获取电影失败: {e}")
            raise
    
    def get_future_schedules(self, cinema_id, film_id):
        """获取未来的场次（优先明天）"""
        print(f"📅 获取电影场次")
        print("-" * 60)

        headers = self.get_headers()
        # 使用正确的沃美API端点
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/shows/"
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)

            if response.status_code == 200:
                result = response.json()
                if result.get('ret') == 0 and result.get('sub') == 0:
                    schedules = result.get('data', [])
                    print(f"   找到 {len(schedules)} 个场次")

                    if not schedules:
                        raise Exception("没有找到场次")

                    # 筛选指定电影的场次
                    film_schedules = [s for s in schedules if s.get('film_id') == film_id]
                    print(f"   指定电影场次: {len(film_schedules)} 个")

                    if not film_schedules:
                        raise Exception("没有找到指定电影的场次")

                    # 筛选未来的场次
                    now = datetime.now()
                    tomorrow = now + timedelta(days=1)
                    future_schedules = []

                    for schedule in film_schedules:
                        show_time = schedule.get('show_time', '')
                        try:
                            # 解析场次时间
                            schedule_time = datetime.strptime(show_time, '%Y-%m-%d %H:%M:%S')

                            # 优先选择明天的场次，其次是今天未来的场次
                            if schedule_time > now:
                                priority = 1 if schedule_time.date() == tomorrow.date() else 2
                                schedule['priority'] = priority
                                future_schedules.append(schedule)
                        except:
                            continue
                    
                    if not future_schedules:
                        raise Exception("没有找到未来的场次")
                    
                    # 按优先级排序，优先选择明天的场次
                    future_schedules.sort(key=lambda x: x.get('priority', 999))
                    
                    # 随机选择一个场次
                    selected_schedule = random.choice(future_schedules[:5])  # 从前5个中随机选择
                    
                    show_time = selected_schedule.get('show_time', '')
                    schedule_id = selected_schedule.get('schedule_id', '')
                    price = selected_schedule.get('price', 0)
                    
                    print(f"   🎲 选择场次: {show_time}")
                    print(f"   场次ID: {schedule_id}")
                    print(f"   票价: {price}")
                    
                    return selected_schedule
                else:
                    raise Exception(f"获取场次失败: {result.get('msg', '未知错误')}")
            else:
                raise Exception(f"HTTP错误: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ 获取场次失败: {e}")
            raise
    
    def get_available_seats(self, cinema_id, schedule_id):
        """获取可用座位"""
        print(f"💺 获取场次 {schedule_id} 的可用座位")
        print("-" * 60)

        headers = self.get_headers()
        # 使用正确的沃美API端点
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/hall/saleable/"

        # 添加场次ID参数
        params = {'schedule_id': schedule_id}
        
        try:
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ret') == 0 and result.get('sub') == 0:
                    seat_data = result.get('data', {})
                    seats = seat_data.get('seats', [])
                    
                    print(f"   总座位数: {len(seats)}")
                    
                    # 筛选可用座位 (status=0)
                    available_seats = [seat for seat in seats if seat.get('status') == 0]
                    print(f"   可用座位数: {len(available_seats)}")
                    
                    if len(available_seats) < 2:
                        raise Exception("可用座位不足（需要至少2个）")
                    
                    # 尝试找相邻座位
                    selected_seats = self.select_adjacent_seats(available_seats)
                    
                    if not selected_seats:
                        # 如果找不到相邻座位，随机选择2个
                        selected_seats = random.sample(available_seats, 2)
                        print(f"   🎲 随机选择2个座位")
                    else:
                        print(f"   🎯 选择相邻座位")
                    
                    for i, seat in enumerate(selected_seats, 1):
                        row = seat.get('row', 'N/A')
                        col = seat.get('col', 'N/A')
                        print(f"   座位{i}: {row}排{col}座")
                    
                    return selected_seats
                else:
                    raise Exception(f"获取座位失败: {result.get('msg', '未知错误')}")
            else:
                raise Exception(f"HTTP错误: {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ 获取座位失败: {e}")
            raise
    
    def select_adjacent_seats(self, available_seats):
        """选择相邻座位"""
        # 按排和列分组
        seat_map = {}
        for seat in available_seats:
            row = seat.get('row', '')
            col = seat.get('col', '')
            if row and col:
                if row not in seat_map:
                    seat_map[row] = {}
                seat_map[row][col] = seat
        
        # 查找相邻座位
        for row, cols in seat_map.items():
            col_numbers = []
            for col in cols.keys():
                try:
                    col_numbers.append(int(col))
                except:
                    continue
            
            col_numbers.sort()
            
            # 查找连续的座位号
            for i in range(len(col_numbers) - 1):
                if col_numbers[i + 1] - col_numbers[i] == 1:
                    seat1 = seat_map[row][str(col_numbers[i])]
                    seat2 = seat_map[row][str(col_numbers[i + 1])]
                    return [seat1, seat2]
        
        return None

    def create_order(self, cinema_id, schedule_id, selected_seats):
        """创建订单"""
        print(f"📝 创建订单")
        print("-" * 60)

        headers = self.get_headers()

        # 尝试不同的API端点和参数格式
        order_variants = [
            {
                "name": "标准创建格式",
                "url": f"{self.base_url}/cinema/{cinema_id}/order/create/",
                "data": {
                    'schedule_id': schedule_id,
                    'seat_info': json.dumps([{
                        'seat_no': seat.get('seat_no', ''),
                        'area_no': seat.get('area_no', ''),
                        'row': seat.get('row', ''),
                        'col': seat.get('col', ''),
                        'price': seat.get('price', 0)
                    } for seat in selected_seats]),
                    'pay_type': 'WECHAT'
                }
            },
            {
                "name": "简化格式",
                "url": f"{self.base_url}/cinema/{cinema_id}/order/create/",
                "data": {
                    'schedule_id': schedule_id,
                    'seat_info': json.dumps([{
                        'row': seat.get('row', ''),
                        'col': seat.get('col', ''),
                        'price': seat.get('price', 0)
                    } for seat in selected_seats])
                }
            },
            {
                "name": "ticket端点",
                "url": f"{self.base_url}/cinema/{cinema_id}/order/ticket/",
                "data": {
                    'schedule_id': schedule_id,
                    'seat_info': '|'.join([
                        f"{seat.get('seat_no', '')}:{seat.get('area_no', '')}:{seat.get('row', '')}:{seat.get('col', '')}"
                        for seat in selected_seats
                    ])
                }
            }
        ]

        for variant in order_variants:
            print(f"   尝试: {variant['name']}")
            print(f"   URL: {variant['url']}")
            print(f"   参数: {variant['data']}")

            try:
                response = requests.post(variant['url'], headers=headers, data=variant['data'], verify=False, timeout=30)

                print(f"   HTTP状态: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"   响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

                    ret = result.get('ret', -1)
                    sub = result.get('sub', -1)
                    msg = result.get('msg', '')

                    if ret == 0 and sub == 0:
                        order_data = result.get('data', {})
                        order_id = order_data.get('order_id', '')

                        print(f"   ✅ 订单创建成功!")
                        print(f"   订单号: {order_id}")
                        print(f"   总价: {order_data.get('total_price', 'N/A')}")
                        print(f"   支付价格: {order_data.get('payment_price', 'N/A')}")

                        return order_id, order_data
                    else:
                        print(f"   ❌ 失败: {msg} (ret={ret}, sub={sub})")
                else:
                    print(f"   ❌ HTTP错误: {response.status_code}")
                    print(f"   响应: {response.text[:200]}...")

            except Exception as e:
                print(f"   ❌ 请求异常: {e}")

        raise Exception("所有订单创建方式都失败")

    def generate_order(self):
        """生成订单的主流程"""
        print("🎬 沃美影城订单生成器")
        print("🎯 自动创建真实有效的订单号")
        print("⏰ 开始时间:", time.strftime("%H:%M:%S"))
        print("=" * 80)

        try:
            # 1. 获取可用影院
            cinema = self.get_available_cinemas()
            cinema_id = cinema['cinema_id']
            cinema_name = cinema['cinema_name']

            # 2. 获取电影
            film = self.get_current_movies(cinema_id)
            film_id = film.get('film_id', '')
            film_name = film.get('film_name', '')

            # 3. 获取场次
            schedule = self.get_future_schedules(cinema_id, film_id)
            schedule_id = schedule.get('schedule_id', '')
            show_time = schedule.get('show_time', '')

            # 4. 获取座位
            seats = self.get_available_seats(cinema_id, schedule_id)

            # 5. 创建订单
            order_id, order_data = self.create_order(cinema_id, schedule_id, seats)

            # 6. 整理结果
            result = {
                "success": True,
                "order_info": {
                    "order_id": order_id,
                    "cinema_id": cinema_id,
                    "cinema_name": cinema_name,
                    "film_id": film_id,
                    "film_name": film_name,
                    "schedule_id": schedule_id,
                    "show_time": show_time,
                    "seat_count": len(seats),
                    "total_price": order_data.get('total_price', 0),
                    "payment_price": order_data.get('payment_price', 0),
                    "created_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 600))  # 10分钟后过期
                },
                "raw_data": {
                    "cinema": cinema,
                    "film": film,
                    "schedule": schedule,
                    "seats": seats,
                    "order": order_data
                }
            }

            print(f"\n🎉 订单生成成功!")
            print("=" * 80)
            print(f"📋 订单信息:")
            print(f"   订单号: {order_id}")
            print(f"   影院: {cinema_name} ({cinema_id})")
            print(f"   电影: {film_name}")
            print(f"   场次: {show_time}")
            print(f"   座位数: {len(seats)}")
            print(f"   总价: {order_data.get('total_price', 0)}")
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
    generator = WomeiOrderGenerator()

    try:
        # 生成订单
        result = generator.generate_order()

        # 保存结果
        filename = f"generated_order_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n📁 结果已保存到: {filename}")

        if result['success']:
            print(f"\n🎯 可用于测试的订单号: {result['order_info']['order_id']}")
            print(f"💡 使用示例:")
            print(f"   python test_voucher_with_provided_order.py")
            print(f"   # 将订单号添加到 test_order_ids 列表中")

            return result['order_info']['order_id']
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
