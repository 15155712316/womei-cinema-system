#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证沃美影院座位状态API的差异性分析
对比全部座位接口和可售座位接口的数据差异
"""

import requests
import json
import time
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WomeiSeatAPIComparator:
    """沃美座位API对比器"""
    
    def __init__(self):
        self.schedule_id = "16624418"
        self.cinema_id = "400028"
        self.token = "47794858a832916d8eda012e7cabd269"
        
        # API接口配置
        self.full_seats_api = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/hall/info/"
        self.saleable_seats_api = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/hall/saleable/"
        
        # 请求头配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Referer': 'https://servicewechat.com/wx4080846d0cec2fd5/78/page-frame.html',
            'tenant-short': 'wmyc'
        }
        
        # 重点检查的座位
        self.target_seats = [
            (1, 9), (1, 10), (1, 11), (1, 12),  # 1排9-12座
            (8, 6), (8, 7)                       # 8排6-7座
        ]
    
    def make_request(self, url: str, params: Dict) -> Dict:
        """发送API请求"""
        try:
            print(f"🔄 请求API: {url}")
            print(f"📋 参数: {params}")
            
            response = requests.get(url, params=params, headers=self.headers, timeout=30, verify=False)
            
            print(f"📊 响应状态: {response.status_code}")
            print(f"📏 响应大小: {len(response.text)} 字符")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 请求成功")
                return data
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"📄 响应内容: {response.text[:500]}")
                return {}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {}
    
    def get_full_seats_data(self) -> Dict:
        """获取全部座位数据"""
        print(f"\n🎯 获取全部座位数据")
        print("=" * 50)
        
        params = {
            'schedule_id': self.schedule_id,
            'token': self.token
        }
        
        return self.make_request(self.full_seats_api, params)
    
    def get_saleable_seats_data(self) -> Dict:
        """获取可售座位数据"""
        print(f"\n🎯 获取可售座位数据")
        print("=" * 50)
        
        params = {
            'schedule_id': self.schedule_id,
            'token': self.token
        }
        
        return self.make_request(self.saleable_seats_api, params)
    
    def extract_seats_from_full_data(self, data: Dict) -> List[Dict]:
        """从全部座位数据中提取座位信息"""
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
                                    'source': 'full_api'
                                }
                                seats.append(seat_info)
        
        except Exception as e:
            print(f"❌ 解析全部座位数据失败: {e}")
        
        return seats
    
    def extract_seats_from_saleable_data(self, data: Dict) -> List[Dict]:
        """从可售座位数据中提取座位信息"""
        seats = []
        try:
            if 'data' in data:
                # 根据实际API响应结构调整解析逻辑
                seat_data = data['data']
                
                # 如果是列表格式
                if isinstance(seat_data, list):
                    for seat in seat_data:
                        seat_info = {
                            'seat_no': seat.get('seat_no', ''),
                            'row': seat.get('row', 0),
                            'col': seat.get('col', 0),
                            'x': seat.get('x', 0),
                            'y': seat.get('y', 0),
                            'status': seat.get('status', 0),
                            'type': seat.get('type', 0),
                            'area_name': seat.get('area_name', ''),
                            'source': 'saleable_api'
                        }
                        seats.append(seat_info)
                
                # 如果是字典格式（类似全部座位API）
                elif isinstance(seat_data, dict) and 'room_seat' in seat_data:
                    room_seat = seat_data['room_seat']
                    
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
                                        'source': 'saleable_api'
                                    }
                                    seats.append(seat_info)
        
        except Exception as e:
            print(f"❌ 解析可售座位数据失败: {e}")
        
        return seats
    
    def analyze_seat_differences(self, full_seats: List[Dict], saleable_seats: List[Dict]) -> Dict:
        """分析座位数据差异"""
        print(f"\n📊 分析座位数据差异")
        print("=" * 50)
        
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
        
        analysis = {
            'full_seats_count': len(full_seats),
            'saleable_seats_count': len(saleable_seats),
            'full_only_seats': full_only,
            'saleable_only_seats': saleable_only,
            'common_seats': common,
            'full_seats_map': full_seats_map,
            'saleable_seats_map': saleable_seats_map
        }
        
        print(f"📈 统计结果:")
        print(f"  全部座位API: {len(full_seats)} 个座位")
        print(f"  可售座位API: {len(saleable_seats)} 个座位")
        print(f"  仅在全部座位API中: {len(full_only)} 个座位")
        print(f"  仅在可售座位API中: {len(saleable_only)} 个座位")
        print(f"  两个API共有: {len(common)} 个座位")
        
        return analysis
    
    def check_target_seats(self, analysis: Dict):
        """检查重点座位的差异"""
        print(f"\n🎯 检查重点座位差异")
        print("=" * 50)
        
        full_seats_map = analysis['full_seats_map']
        saleable_seats_map = analysis['saleable_seats_map']
        
        for row, col in self.target_seats:
            print(f"\n🔍 检查座位 {row}排{col}座:")
            
            in_full = (row, col) in full_seats_map
            in_saleable = (row, col) in saleable_seats_map
            
            print(f"  全部座位API: {'✅ 存在' if in_full else '❌ 不存在'}")
            print(f"  可售座位API: {'✅ 存在' if in_saleable else '❌ 不存在'}")
            
            if in_full and not in_saleable:
                seat = full_seats_map[(row, col)]
                print(f"  🔴 结论: 该座位已售出")
                print(f"  📋 座位信息: {seat['seat_no']}, 状态: {seat['status']}")
            elif not in_full and in_saleable:
                print(f"  🟡 异常: 仅在可售座位API中存在")
            elif in_full and in_saleable:
                print(f"  🟢 结论: 该座位可售")
            else:
                print(f"  ⚫ 结论: 该座位不存在")
    
    def save_detailed_comparison(self, analysis: Dict):
        """保存详细对比结果"""
        print(f"\n💾 保存详细对比结果")
        print("=" * 50)
        
        try:
            # 保存仅在全部座位API中的座位（可能是已售座位）
            full_only_seats = []
            for row, col in analysis['full_only_seats']:
                seat = analysis['full_seats_map'][(row, col)]
                full_only_seats.append(seat)
            
            # 保存仅在可售座位API中的座位（异常情况）
            saleable_only_seats = []
            for row, col in analysis['saleable_only_seats']:
                seat = analysis['saleable_seats_map'][(row, col)]
                saleable_only_seats.append(seat)
            
            comparison_result = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'schedule_id': self.schedule_id,
                'cinema_id': self.cinema_id,
                'summary': {
                    'full_seats_count': analysis['full_seats_count'],
                    'saleable_seats_count': analysis['saleable_seats_count'],
                    'full_only_count': len(analysis['full_only_seats']),
                    'saleable_only_count': len(analysis['saleable_only_seats']),
                    'common_count': len(analysis['common_seats'])
                },
                'full_only_seats': full_only_seats,
                'saleable_only_seats': saleable_only_seats,
                'target_seats_analysis': {}
            }
            
            # 添加重点座位分析
            for row, col in self.target_seats:
                seat_key = f"{row}排{col}座"
                in_full = (row, col) in analysis['full_seats_map']
                in_saleable = (row, col) in analysis['saleable_seats_map']
                
                comparison_result['target_seats_analysis'][seat_key] = {
                    'in_full_api': in_full,
                    'in_saleable_api': in_saleable,
                    'conclusion': '已售' if (in_full and not in_saleable) else '可售' if (in_full and in_saleable) else '不存在'
                }
            
            # 保存到文件
            filename = f"seat_api_comparison_{self.schedule_id}_{int(time.time())}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(comparison_result, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 对比结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存对比结果失败: {e}")
    
    def run_comparison(self):
        """运行完整的对比分析"""
        print(f"🔍 沃美影院座位状态API差异性分析")
        print(f"🎬 场次ID: {self.schedule_id}")
        print(f"🏢 影院ID: {self.cinema_id}")
        print("=" * 60)
        
        # 获取两个API的数据
        full_data = self.get_full_seats_data()
        time.sleep(1)  # 避免请求过快
        saleable_data = self.get_saleable_seats_data()
        
        if not full_data or not saleable_data:
            print("❌ 无法获取API数据，分析终止")
            return
        
        # 提取座位信息
        print(f"\n📋 解析座位数据")
        print("=" * 50)
        
        full_seats = self.extract_seats_from_full_data(full_data)
        saleable_seats = self.extract_seats_from_saleable_data(saleable_data)
        
        print(f"✅ 全部座位数据解析完成: {len(full_seats)} 个座位")
        print(f"✅ 可售座位数据解析完成: {len(saleable_seats)} 个座位")
        
        # 分析差异
        analysis = self.analyze_seat_differences(full_seats, saleable_seats)
        
        # 检查重点座位
        self.check_target_seats(analysis)
        
        # 保存详细结果
        self.save_detailed_comparison(analysis)
        
        # 输出结论
        self.print_conclusion(analysis)
    
    def print_conclusion(self, analysis: Dict):
        """输出分析结论"""
        print(f"\n🎯 分析结论")
        print("=" * 50)
        
        full_only_count = len(analysis['full_only_seats'])
        saleable_only_count = len(analysis['saleable_only_seats'])
        
        if full_only_count > 0 and saleable_only_count == 0:
            print(f"✅ 验证结论: 可售座位API确实只返回可售座位")
            print(f"📊 证据: 全部座位API比可售座位API多 {full_only_count} 个座位")
            print(f"💡 说明: 这 {full_only_count} 个座位很可能是已售座位")
            print(f"🔧 建议: 使用可售座位API获取准确的可售座位状态")
        elif full_only_count == 0 and saleable_only_count > 0:
            print(f"⚠️ 异常情况: 可售座位API返回了全部座位API中没有的座位")
            print(f"📊 数据: 可售座位API多 {saleable_only_count} 个座位")
            print(f"🔧 建议: 需要进一步调查API数据的一致性")
        elif full_only_count == 0 and saleable_only_count == 0:
            print(f"🤔 相同结果: 两个API返回的座位数据完全一致")
            print(f"💡 说明: 当前场次可能没有已售座位，或API行为相同")
        else:
            print(f"🔄 复杂情况: 两个API都有独有的座位数据")
            print(f"📊 数据: 全部座位API独有 {full_only_count} 个，可售座位API独有 {saleable_only_count} 个")
            print(f"🔧 建议: 需要详细分析具体的座位差异")

def main():
    """主函数"""
    print("🎬 沃美影院座位状态API差异性验证")
    print("=" * 60)
    
    comparator = WomeiSeatAPIComparator()
    comparator.run_comparison()

if __name__ == "__main__":
    main()
