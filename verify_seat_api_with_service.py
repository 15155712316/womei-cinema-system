#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用沃美电影服务验证座位状态API的差异性分析
处理token过期问题，使用模拟数据进行验证
"""

import json
import time
import requests
import urllib3
from typing import Dict, List, Set, Tuple
from services.womei_film_service import get_womei_film_service

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WomeiSeatAPIVerifier:
    """沃美座位API验证器（使用电影服务）"""
    
    def __init__(self):
        # 从账号文件加载token
        self.token = self.load_token()
        self.film_service = get_womei_film_service(self.token)
        
        # 测试用的影院和场次信息
        self.test_cinema_id = None
        self.test_schedule_id = None
        
        # 请求头配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Referer': 'https://servicewechat.com/wx4080846d0cec2fd5/78/page-frame.html',
            'tenant-short': 'wmyc'
        }
    
    def load_token(self) -> str:
        """从账号文件加载token"""
        try:
            with open('data/accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            if accounts and len(accounts) > 0:
                token = accounts[0].get('token', '')
                print(f"✅ 加载token: {token[:20]}...")
                return token
            else:
                print("❌ 账号文件为空")
                return ""
        except Exception as e:
            print(f"❌ 加载账号文件失败: {e}")
            return ""
    
    def find_valid_cinema_and_schedule(self) -> bool:
        """查找有效的影院和场次"""
        print(f"\n🔍 查找有效的影院和场次")
        print("=" * 50)
        
        # 1. 获取城市列表
        cities_result = self.film_service.get_cities()
        if not cities_result.get('success'):
            print(f"❌ 获取城市失败: {cities_result.get('error')}")
            return False
        
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
                movies_result = self.film_service.get_movies(cinema_id)
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
                    shows_result = self.film_service.get_shows(cinema_id, str(movie_id))
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
                                show_time = schedule.get('show_time', '未知时间')
                                
                                print(f"    🎭 找到场次: {date} {show_time} (ID: {schedule_id})")
                                
                                # 保存找到的有效信息
                                self.test_cinema_id = cinema_id
                                self.test_schedule_id = schedule_id
                                
                                print(f"✅ 找到有效的测试数据:")
                                print(f"  影院: {cinema_name} (ID: {cinema_id})")
                                print(f"  电影: {movie_name} (ID: {movie_id})")
                                print(f"  场次: {date} {show_time} (ID: {schedule_id})")
                                
                                return True
        
        print("❌ 未找到有效的影院和场次")
        return False
    
    def test_seat_apis_with_valid_schedule(self) -> Dict:
        """使用有效场次测试座位API"""
        print(f"\n🪑 测试座位API")
        print("=" * 50)
        
        if not self.test_cinema_id or not self.test_schedule_id:
            print("❌ 缺少有效的影院或场次ID")
            return {}
        
        # 构建API URL
        full_seats_api = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.test_cinema_id}/hall/info/"
        saleable_seats_api = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.test_cinema_id}/hall/saleable/"
        
        params = {
            'schedule_id': self.test_schedule_id,
            'token': self.token
        }
        
        results = {}
        
        # 测试两个API
        apis = [
            ('全部座位API', full_seats_api),
            ('可售座位API', saleable_seats_api)
        ]
        
        for api_name, api_url in apis:
            print(f"\n🔄 测试 {api_name}")
            print(f"URL: {api_url}")
            print(f"参数: {params}")
            
            try:
                response = requests.get(
                    api_url, 
                    params=params, 
                    headers=self.headers, 
                    timeout=30, 
                    verify=False
                )
                
                print(f"状态码: {response.status_code}")
                print(f"响应大小: {len(response.text)} 字符")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"JSON解析成功")
                        
                        # 检查响应状态
                        ret = data.get('ret', -1)
                        msg = data.get('msg', '')
                        
                        if ret == 0 and data.get('data'):
                            print(f"✅ {api_name}获取成功")
                            seats = self.extract_seats_from_response(data, api_name)
                            results[api_name] = {
                                'success': True,
                                'seats': seats,
                                'total': len(seats),
                                'raw_data': data
                            }
                            print(f"座位数量: {len(seats)}")
                        else:
                            print(f"❌ {api_name}返回错误: {msg}")
                            results[api_name] = {
                                'success': False,
                                'error': msg,
                                'seats': [],
                                'total': 0
                            }
                    
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON解析失败: {e}")
                        results[api_name] = {
                            'success': False,
                            'error': f'JSON解析失败: {e}',
                            'seats': [],
                            'total': 0
                        }
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
                    results[api_name] = {
                        'success': False,
                        'error': f'HTTP错误: {response.status_code}',
                        'seats': [],
                        'total': 0
                    }
            
            except Exception as e:
                print(f"❌ 请求异常: {e}")
                results[api_name] = {
                    'success': False,
                    'error': str(e),
                    'seats': [],
                    'total': 0
                }
        
        return results
    
    def extract_seats_from_response(self, data: Dict, api_name: str) -> List[Dict]:
        """从API响应中提取座位信息"""
        seats = []
        try:
            if 'data' in data and 'room_seat' in data['data']:
                room_seat = data['data']['room_seat']
                
                for area in room_seat:
                    area_name = area.get('area_name', '未知区域')
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
                                    'source': api_name
                                }
                                seats.append(seat_info)
        
        except Exception as e:
            print(f"❌ 解析{api_name}座位数据失败: {e}")
        
        return seats
    
    def analyze_api_differences(self, results: Dict):
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
            print("可能原因:")
            print("  1. Token已过期")
            print("  2. 场次已结束或取消")
            print("  3. API接口变更")
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
                print(f"  {row}排{col}座 - {seat['seat_no']} (状态: {seat['status']})")
        
        if saleable_only:
            print(f"\n🟡 仅在可售座位API中的座位（异常情况）:")
            for row, col in sorted(saleable_only)[:10]:  # 只显示前10个
                seat = saleable_seats_map[(row, col)]
                print(f"  {row}排{col}座 - {seat['seat_no']} (状态: {seat['status']})")
        
        # 输出结论
        self.print_verification_conclusion(len(full_seats), len(saleable_seats), len(full_only), len(saleable_only))
    
    def print_verification_conclusion(self, full_count: int, saleable_count: int, full_only: int, saleable_only: int):
        """输出验证结论"""
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
            print(f"🔧 建议: 需要进一步分析具体差异")
    
    def run_verification(self):
        """运行完整的验证流程"""
        print(f"🔍 沃美影院座位状态API差异性验证")
        print(f"🔑 Token: {self.token[:20]}..." if self.token else "❌ 无Token")
        print("=" * 60)
        
        # 1. 查找有效的影院和场次
        if not self.find_valid_cinema_and_schedule():
            print("❌ 无法找到有效的测试数据，验证终止")
            return
        
        # 2. 测试座位API
        results = self.test_seat_apis_with_valid_schedule()
        
        if not results:
            print("❌ 无法获取API测试结果")
            return
        
        # 3. 分析差异
        self.analyze_api_differences(results)
        
        # 4. 保存结果
        self.save_verification_results(results)
    
    def save_verification_results(self, results: Dict):
        """保存验证结果"""
        try:
            verification_result = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'test_cinema_id': self.test_cinema_id,
                'test_schedule_id': self.test_schedule_id,
                'token_used': self.token[:20] + "..." if self.token else "无",
                'results': results
            }
            
            filename = f"seat_api_verification_{int(time.time())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(verification_result, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 验证结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存验证结果失败: {e}")

def main():
    """主函数"""
    print("🎬 沃美影院座位状态API差异性验证（使用电影服务）")
    print("=" * 60)
    
    verifier = WomeiSeatAPIVerifier()
    verifier.run_verification()

if __name__ == "__main__":
    main()
