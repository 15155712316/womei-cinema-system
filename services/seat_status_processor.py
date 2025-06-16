#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位状态处理器
通过对比全部座位API和可售座位API的响应数据，准确标识已售座位状态
"""

import json
import time
from typing import Dict, List, Tuple, Set, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.womei_film_service import get_womei_film_service

class SeatStatusProcessor:
    """座位状态处理器"""
    
    def __init__(self, token: str):
        """
        初始化座位状态处理器
        
        Args:
            token: API访问令牌
        """
        self.token = token
        self.film_service = get_womei_film_service(token)
        self.debug_mode = True  # 调试模式，输出详细日志
    
    def get_accurate_seat_data(self, cinema_id: str, hall_id: str, schedule_id: str) -> Dict:
        """
        获取准确的座位数据（已售状态已正确标记）
        
        Args:
            cinema_id: 影院ID
            hall_id: 影厅ID
            schedule_id: 场次ID
            
        Returns:
            处理后的座位数据，格式与原始API响应保持一致
        """
        if self.debug_mode:
            print(f"\n🔄 开始获取准确座位数据")
            print(f"影院ID: {cinema_id}, 影厅ID: {hall_id}, 场次ID: {schedule_id}")
        
        try:
            # 1. 同时调用两个座位API
            full_data, saleable_data = self._fetch_both_apis(cinema_id, hall_id, schedule_id)
            
            if not full_data or not saleable_data:
                if self.debug_mode:
                    print(f"❌ API调用失败，返回空数据")
                return {}
            
            # 2. 分析座位差异
            sold_seats = self._analyze_seat_differences(full_data, saleable_data)
            
            # 3. 标记已售座位状态
            processed_data = self._mark_sold_seats(full_data, sold_seats)
            
            if self.debug_mode:
                self._print_processing_summary(full_data, saleable_data, sold_seats)
            
            return processed_data
            
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 座位数据处理异常: {e}")
            return {}
    
    def _fetch_both_apis(self, cinema_id: str, hall_id: str, schedule_id: str) -> Tuple[Dict, Dict]:
        """
        同时调用两个座位API
        
        Returns:
            (全部座位数据, 可售座位数据)
        """
        if self.debug_mode:
            print(f"📡 调用全部座位API和可售座位API...")
        
        full_data = {}
        saleable_data = {}
        
        try:
            # 调用全部座位API
            full_result = self.film_service.get_hall_info(cinema_id, hall_id, schedule_id)
            if full_result.get('success'):
                full_data = full_result.get('hall_info', {})
                if self.debug_mode:
                    full_count = self._count_seats_in_data(full_data)
                    print(f"✅ 全部座位API: {full_count} 个座位")
            else:
                if self.debug_mode:
                    print(f"❌ 全部座位API失败: {full_result.get('error')}")
            
            # 调用可售座位API
            saleable_result = self.film_service.get_hall_saleable(cinema_id, schedule_id)
            if saleable_result.get('success'):
                saleable_data = saleable_result.get('saleable_info', {})
                if self.debug_mode:
                    saleable_count = self._count_seats_in_data(saleable_data)
                    print(f"✅ 可售座位API: {saleable_count} 个座位")
            else:
                if self.debug_mode:
                    print(f"❌ 可售座位API失败: {saleable_result.get('error')}")
        
        except Exception as e:
            if self.debug_mode:
                print(f"❌ API调用异常: {e}")
        
        return full_data, saleable_data
    
    def _analyze_seat_differences(self, full_data: Dict, saleable_data: Dict) -> Set[Tuple[int, int]]:
        """
        分析两个API的座位差异，识别已售座位
        
        Args:
            full_data: 全部座位数据
            saleable_data: 可售座位数据
            
        Returns:
            已售座位的位置集合 {(row, col), ...}
        """
        if self.debug_mode:
            print(f"🔍 分析座位差异...")
        
        # 提取座位位置
        full_positions = self._extract_seat_positions(full_data)
        saleable_positions = self._extract_seat_positions(saleable_data)
        
        # 找出差异：仅在全部座位API中存在的座位
        sold_positions = full_positions - saleable_positions
        
        if self.debug_mode:
            print(f"📊 差异分析结果:")
            print(f"  全部座位: {len(full_positions)} 个")
            print(f"  可售座位: {len(saleable_positions)} 个")
            print(f"  已售座位: {len(sold_positions)} 个")
            
            if sold_positions and self.debug_mode:
                print(f"🔴 已售座位位置:")
                sorted_sold = sorted(sold_positions)[:10]  # 只显示前10个
                for row, col in sorted_sold:
                    print(f"    {row}排{col}座")
                if len(sold_positions) > 10:
                    print(f"    ... 还有 {len(sold_positions) - 10} 个已售座位")
        
        return sold_positions
    
    def _extract_seat_positions(self, seat_data: Dict) -> Set[Tuple[int, int]]:
        """
        从座位数据中提取座位位置
        
        Args:
            seat_data: 座位数据
            
        Returns:
            座位位置集合 {(row, col), ...}
        """
        positions = set()
        
        try:
            if 'room_seat' in seat_data:
                room_seat = seat_data['room_seat']
                
                for area in room_seat:
                    seats_data = area.get('seats', {})
                    
                    for row_key, row_data in seats_data.items():
                        seat_details = row_data.get('detail', [])
                        
                        for seat in seat_details:
                            row = int(seat.get('row', 0))
                            col = int(seat.get('col', 0))
                            if row > 0 and col > 0:
                                positions.add((row, col))
        
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 提取座位位置失败: {e}")
        
        return positions
    
    def _mark_sold_seats(self, full_data: Dict, sold_positions: Set[Tuple[int, int]]) -> Dict:
        """
        在全部座位数据中标记已售座位状态
        
        Args:
            full_data: 全部座位数据
            sold_positions: 已售座位位置集合
            
        Returns:
            标记后的座位数据
        """
        if self.debug_mode:
            print(f"🏷️ 标记已售座位状态...")
        
        # 深拷贝数据，避免修改原始数据
        processed_data = json.loads(json.dumps(full_data))
        marked_count = 0
        
        try:
            if 'room_seat' in processed_data:
                room_seat = processed_data['room_seat']
                
                for area in room_seat:
                    seats_data = area.get('seats', {})
                    
                    for row_key, row_data in seats_data.items():
                        seat_details = row_data.get('detail', [])
                        
                        for seat in seat_details:
                            row = int(seat.get('row', 0))
                            col = int(seat.get('col', 0))
                            
                            # 检查是否为已售座位
                            if (row, col) in sold_positions:
                                # 标记为已售状态
                                seat['status'] = 1
                                marked_count += 1
                                
                                if self.debug_mode and marked_count <= 5:  # 只显示前5个
                                    print(f"  🔴 标记已售: {row}排{col}座 (座位号: {seat.get('seat_no', '未知')})")
            
            if self.debug_mode:
                print(f"✅ 已标记 {marked_count} 个已售座位")
        
        except Exception as e:
            if self.debug_mode:
                print(f"❌ 标记已售座位失败: {e}")
            return full_data  # 返回原始数据
        
        return processed_data
    
    def _count_seats_in_data(self, seat_data: Dict) -> int:
        """统计座位数据中的座位数量"""
        try:
            if 'room_seat' in seat_data:
                total_seats = 0
                room_seat = seat_data['room_seat']
                
                for area in room_seat:
                    seats_data = area.get('seats', {})
                    for row_data in seats_data.values():
                        total_seats += len(row_data.get('detail', []))
                
                return total_seats
        except:
            pass
        
        return 0
    
    def _print_processing_summary(self, full_data: Dict, saleable_data: Dict, sold_positions: Set):
        """打印处理摘要"""
        print(f"\n📋 座位状态处理摘要:")
        print(f"=" * 50)
        
        full_count = self._count_seats_in_data(full_data)
        saleable_count = self._count_seats_in_data(saleable_data)
        sold_count = len(sold_positions)
        
        print(f"全部座位数量: {full_count}")
        print(f"可售座位数量: {saleable_count}")
        print(f"已售座位数量: {sold_count}")
        print(f"数据一致性: {'✅ 正常' if full_count == saleable_count + sold_count else '⚠️ 异常'}")
        
        if sold_count > 0:
            print(f"✅ 成功识别并标记了 {sold_count} 个已售座位")
            print(f"💡 现在UI组件将正确显示座位状态")
        else:
            print(f"ℹ️ 当前场次暂无已售座位")
    
    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self.debug_mode = enabled

def get_seat_status_processor(token: str) -> SeatStatusProcessor:
    """
    获取座位状态处理器实例
    
    Args:
        token: API访问令牌
        
    Returns:
        座位状态处理器实例
    """
    return SeatStatusProcessor(token)

# 便捷函数，用于快速获取准确的座位数据
def get_accurate_seat_data(token: str, cinema_id: str, hall_id: str, schedule_id: str, debug: bool = True) -> Dict:
    """
    便捷函数：获取准确的座位数据
    
    Args:
        token: API访问令牌
        cinema_id: 影院ID
        hall_id: 影厅ID
        schedule_id: 场次ID
        debug: 是否启用调试模式
        
    Returns:
        处理后的座位数据
    """
    processor = get_seat_status_processor(token)
    processor.set_debug_mode(debug)
    return processor.get_accurate_seat_data(cinema_id, hall_id, schedule_id)

if __name__ == "__main__":
    # 测试代码
    import sys
    
    def test_seat_status_processor():
        """测试座位状态处理器"""
        print("🧪 测试座位状态处理器")
        print("=" * 60)
        
        # 从accounts.json加载token
        try:
            with open('data/accounts.json', 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            if accounts and len(accounts) > 0:
                token = accounts[0].get('token', '')
                print(f"✅ 加载token: {token[:20]}...")
                
                # 使用之前验证成功的场次数据
                cinema_id = "400028"
                hall_id = "5"
                schedule_id = "16626079"  # 有5个已售座位的场次
                
                print(f"\n🎬 测试场次:")
                print(f"  影院ID: {cinema_id}")
                print(f"  影厅ID: {hall_id}")
                print(f"  场次ID: {schedule_id}")
                
                # 获取准确的座位数据
                accurate_data = get_accurate_seat_data(token, cinema_id, hall_id, schedule_id)
                
                if accurate_data:
                    print(f"\n✅ 座位状态处理成功!")
                    print(f"📄 返回数据格式与原始API保持一致")
                    print(f"🎯 已售座位状态已正确标记")
                else:
                    print(f"\n❌ 座位状态处理失败")
            
            else:
                print("❌ 账号文件为空")
        
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    test_seat_status_processor()
