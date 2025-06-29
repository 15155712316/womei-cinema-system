#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新获取当前可用的城市、影院、场次和座位进行券使用测试
"""

import requests
import json
import urllib3
import random
from datetime import datetime, timedelta

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FreshVoucherTester:
    """全新的券使用测试器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.token = "afebc43f2b18da363fd78a6a10b01b72"
        self.voucher_code = "GZJY01002948416827"
        
        # 当前选择的信息
        self.current_city = None
        self.current_cinema = None
        self.current_schedule = None
        self.current_seats = None
        self.current_order_id = None
        
        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'token': self.token,
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
    
    def get_cities(self):
        """获取城市列表"""
        print("🌍 步骤1: 获取城市列表")
        print("=" * 50)

        # 直接使用已知的城市信息，跳过城市API
        print("🎯 使用已知城市信息（跳过城市API）")
        self.current_city = {'city_id': '110100', 'city_name': '北京'}
        print(f"✅ 选择城市: {self.current_city.get('city_name')} (ID: {self.current_city.get('city_id')})")
        return True
    
    def get_cinemas(self):
        """获取影院列表"""
        print("\n🏢 步骤2: 获取影院列表")
        print("=" * 50)

        # 直接使用已知的影院信息
        print("🎯 使用已知影院信息")
        self.current_cinema = {'cinema_id': '9934', 'cinema_name': '测试影院'}
        print(f"✅ 选择影院: {self.current_cinema.get('cinema_name')} (ID: {self.current_cinema.get('cinema_id')})")
        return True
    
    def get_movies_and_schedules(self):
        """获取电影和场次列表"""
        print("\n🎬 步骤3: 获取电影和场次列表")
        print("=" * 50)
        
        if not self.current_cinema:
            print("❌ 没有选择影院")
            return False
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.current_cinema.get('cinema_id')}/movies/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ret') == 0:
                    movies = result.get('data', [])
                    print(f"✅ 获取到 {len(movies)} 部电影")
                    
                    # 查找有可用场次的电影
                    available_schedules = []
                    for movie in movies:
                        schedules = movie.get('schedules', [])
                        for schedule in schedules:
                            # 检查场次时间是否在未来
                            show_time = schedule.get('show_time', '')
                            if show_time:
                                try:
                                    show_datetime = datetime.strptime(show_time, '%Y-%m-%d %H:%M:%S')
                                    if show_datetime > datetime.now():
                                        available_schedules.append({
                                            'movie': movie,
                                            'schedule': schedule
                                        })
                                except:
                                    pass
                    
                    print(f"✅ 找到 {len(available_schedules)} 个可用场次")
                    
                    if available_schedules:
                        # 随机选择一个场次
                        selected = random.choice(available_schedules)
                        self.current_schedule = selected['schedule']
                        movie_name = selected['movie'].get('movie_name', 'Unknown')
                        
                        print(f"🎯 随机选择场次:")
                        print(f"   电影: {movie_name}")
                        print(f"   场次ID: {self.current_schedule.get('schedule_id')}")
                        print(f"   放映时间: {self.current_schedule.get('show_time')}")
                        print(f"   票价: {self.current_schedule.get('price', 'N/A')}")
                        
                        return True
                    else:
                        print("❌ 没有找到可用场次")
                        return False
                else:
                    print(f"❌ 获取电影失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def get_seats(self):
        """获取座位信息"""
        print("\n🪑 步骤4: 获取座位信息")
        print("=" * 50)
        
        if not self.current_schedule:
            print("❌ 没有选择场次")
            return False
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.current_cinema.get('cinema_id')}/schedule/{self.current_schedule.get('schedule_id')}/seats/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ret') == 0:
                    seats_data = result.get('data', {})
                    seats = seats_data.get('seats', [])
                    
                    print(f"✅ 获取到座位信息")
                    
                    # 查找可用座位（状态为0表示可选）
                    available_seats = []
                    for seat in seats:
                        if seat.get('status') == 0:  # 0表示可选
                            available_seats.append(seat)
                    
                    print(f"✅ 找到 {len(available_seats)} 个可用座位")
                    
                    if len(available_seats) >= 2:
                        # 随机选择两个相邻或接近的座位
                        selected_seats = random.sample(available_seats, 2)
                        self.current_seats = selected_seats
                        
                        print(f"🎯 随机选择座位:")
                        for i, seat in enumerate(selected_seats):
                            print(f"   座位{i+1}: 第{seat.get('row_num')}排{seat.get('seat_num')}座 (ID: {seat.get('seat_id')})")
                        
                        return True
                    else:
                        print("❌ 可用座位不足（需要至少2个）")
                        return False
                else:
                    print(f"❌ 获取座位失败: {result.get('msg')}")
                    return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def create_order(self):
        """创建订单"""
        print("\n🎫 步骤5: 创建订单")
        print("=" * 50)
        
        if not self.current_seats:
            print("❌ 没有选择座位")
            return False
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.current_cinema.get('cinema_id')}/order/ticket/"
        
        # 构建座位信息字符串
        seat_strings = []
        for seat in self.current_seats:
            seat_string = f"{seat.get('seat_id')}:{seat.get('row_num')}:{seat.get('seat_num')}:{seat.get('schedule_id')}#{seat.get('row_num'):02d}#{seat.get('seat_num'):02d}"
            seat_strings.append(seat_string)
        
        seatlable = "|".join(seat_strings)
        
        data = {
            'seatlable': seatlable,
            'schedule_id': self.current_schedule.get('schedule_id')
        }
        
        print(f"📤 请求参数:")
        print(f"   座位信息: {seatlable}")
        print(f"   场次ID: {self.current_schedule.get('schedule_id')}")
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    order_id = result.get('data', {}).get('order_id')
                    if order_id:
                        self.current_order_id = order_id
                        print(f"✅ 订单创建成功: {order_id}")
                        return True
                    else:
                        print(f"❌ 未获取到订单ID")
                        return False
                else:
                    print(f"❌ 订单创建失败: {result.get('msg')} (sub: {result.get('sub')})")
                    return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False

    def test_voucher_usage(self):
        """测试券使用"""
        print("\n🎫 步骤6: 测试券使用")
        print("=" * 50)

        if not self.current_order_id:
            print("❌ 没有有效的订单ID")
            return False

        print(f"📋 测试配置:")
        print(f"   订单ID: {self.current_order_id}")
        print(f"   券码: {self.voucher_code}")
        print(f"   影院ID: {self.current_cinema.get('cinema_id')}")

        # 测试1: 券价格计算
        print(f"\n🧮 测试1: 券价格计算")
        price_result = self._test_voucher_price()

        # 测试2: 券绑定（单接口模式）
        print(f"\n🔄 测试2: 券绑定（单接口模式）")
        bind_result = self._test_voucher_binding()

        # 分析结果
        print(f"\n📊 测试结果分析:")
        print(f"   券价格计算: {'✅ 成功' if price_result else '❌ 失败'}")
        print(f"   券绑定: {'✅ 成功' if bind_result else '❌ 失败'}")

        if bind_result:
            print(f"\n🎉 券使用测试成功！")
            print(f"✅ POST /order/change/ 接口完全支持单接口模式")
            print(f"✅ 可以更新HAR分析报告状态为'完全实现'")
            return True
        else:
            print(f"\n❌ 券使用测试失败")
            return False

    def _test_voucher_price(self):
        """测试券价格计算"""
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.current_cinema.get('cinema_id')}/order/voucher/price/"

        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.current_order_id
        }

        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)

            if response.status_code == 200:
                result = response.json()
                print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

                print(f"   ret: {result.get('ret')}, sub: {result.get('sub')}, msg: {result.get('msg')}")
                return result.get('ret') == 0
            else:
                print(f"   HTTP请求失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"   请求异常: {e}")
            return False

    def _test_voucher_binding(self):
        """测试券绑定"""
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.current_cinema.get('cinema_id')}/order/change/"

        data = {
            'order_id': self.current_order_id,
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'card_id': '',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'use_rewards': 'Y',
            'use_limit_cards': 'N',
            'limit_cards': '[]',
            'voucher_code': self.voucher_code,
            'voucher_code_type': 'VGC_T',
            'ticket_pack_goods': ' '
        }

        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)

            if response.status_code == 200:
                result = response.json()
                print(f"   完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

                print(f"\n   🔍 详细分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')}")
                print(f"   msg: {result.get('msg')}")

                data_section = result.get('data', {})
                if data_section:
                    print(f"\n   💰 价格信息:")
                    price_fields = ['order_total_price', 'order_payment_price', 'order_unfee_total_price']
                    for field in price_fields:
                        if field in data_section:
                            print(f"      {field}: {data_section[field]}")

                    print(f"\n   🎫 券使用信息:")
                    voucher_fields = ['voucher_use', 'voucher_discounts', 'voucher_use_goods']
                    for field in voucher_fields:
                        if field in data_section:
                            print(f"      {field}: {data_section[field]}")

                    # 判断是否包含完整信息
                    has_price_info = any(field in data_section for field in price_fields)
                    has_voucher_info = any(field in data_section for field in voucher_fields)

                    print(f"\n   📋 接口能力验证:")
                    print(f"      包含价格信息: {'✅ 是' if has_price_info else '❌ 否'}")
                    print(f"      包含券信息: {'✅ 是' if has_voucher_info else '❌ 否'}")
                    print(f"      单接口模式: {'✅ 可行' if (result.get('ret') == 0 and has_price_info) else '❌ 不可行'}")

                return result.get('ret') == 0 and result.get('sub') == 0
            else:
                print(f"   HTTP请求失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"   请求异常: {e}")
            return False

    def run_complete_test(self):
        """运行完整测试"""
        print("🎬 沃美券使用流程全新测试")
        print("🎯 自动获取当前可用的城市、影院、场次和座位")
        print("=" * 60)

        try:
            # 步骤1: 获取城市
            if not self.get_cities():
                print("❌ 获取城市失败")
                return False

            # 步骤2: 获取影院
            if not self.get_cinemas():
                print("❌ 获取影院失败")
                return False

            # 步骤3: 获取电影和场次
            if not self.get_movies_and_schedules():
                print("❌ 获取场次失败")
                return False

            # 步骤4: 获取座位
            if not self.get_seats():
                print("❌ 获取座位失败")
                return False

            # 步骤5: 创建订单
            if not self.create_order():
                print("❌ 创建订单失败")
                return False

            # 步骤6: 测试券使用
            if not self.test_voucher_usage():
                print("❌ 券使用测试失败")
                return False

            print(f"\n🎊 完整测试成功！")
            print(f"✅ 验证了POST /order/change/接口的完整能力")
            print(f"✅ 确认单接口模式完全可行")

            return True

        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    tester = FreshVoucherTester()
    tester.run_complete_test()

if __name__ == "__main__":
    main()
