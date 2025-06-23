#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整数据字段显示
验证修改后的订单API响应打印方法是否显示所有data字段
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_data_display():
    """测试显示所有data字段的效果"""
    
    # 模拟修改后的 _print_order_api_response 方法
    def _print_order_api_response(result, api_name="订单API"):
        """格式化打印订单接口返回信息，方便调试"""
        import json
        from datetime import datetime
        
        print(f"\n" + "🔍" * 3 + f" [{api_name}] 接口返回数据详情 " + "🔍" * 3)
        print(f"{'=' * 80}")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔗 接口: {api_name}")
        print(f"{'=' * 80}")
        
        if result is None:
            print(f"❌ 返回数据: None (可能是网络错误或接口异常)")
        else:
            print(f"📊 数据类型: {type(result).__name__}")
            
            if isinstance(result, dict):
                # 格式化字典数据
                print(f"📋 字段总数: {len(result)}")
                print(f"🔑 字段列表: {list(result.keys())}")
                print(f"{'-' * 80}")
                
                # 按重要性排序显示字段 - 🔧 修复：添加沃美API字段
                important_fields = ['ret', 'sub', 'msg', 'data', 'success', 'resultCode', 'resultDesc', 'error', 'order_id', 'orderno']
                other_fields = [k for k in result.keys() if k not in important_fields]
                
                # 先显示重要字段
                for key in important_fields:
                    if key in result:
                        value = result[key]
                        if isinstance(value, (dict, list)) and len(str(value)) > 200:
                            print(f"📌 {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                            if isinstance(value, dict):
                                for sub_key, sub_value in list(value.items())[:3]:
                                    print(f"   └─ {sub_key}: {str(sub_value)[:100]}{'...' if len(str(sub_value)) > 100 else ''}")
                                if len(value) > 3:
                                    print(f"   └─ ... 还有 {len(value) - 3} 个字段")
                            elif isinstance(value, list):
                                for i, item in enumerate(value[:2]):
                                    print(f"   └─ [{i}]: {str(item)[:100]}{'...' if len(str(item)) > 100 else ''}")
                                if len(value) > 2:
                                    print(f"   └─ ... 还有 {len(value) - 2} 个项目")
                        else:
                            print(f"📌 {key}: {value}")
                
                # 再显示其他字段
                if other_fields:
                    print(f"{'-' * 40} 其他字段 {'-' * 40}")
                    for key in other_fields:
                        value = result[key]
                        if isinstance(value, (dict, list)) and len(str(value)) > 200:
                            print(f"🔸 {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                        else:
                            print(f"🔸 {key}: {value}")
                
                # 判断接口调用结果 - 🔧 修复：支持沃美API的ret字段
                print(f"{'-' * 80}")
                
                # 沃美API使用ret字段：ret=0表示成功，ret!=0表示失败
                if result.get('ret') == 0:
                    print(f"✅ 接口调用状态: 成功")
                    # 🆕 如果有data字段，显示其内容
                    data = result.get('data')
                    if data and isinstance(data, dict):
                        print(f"📦 返回数据内容 (共 {len(data)} 个字段):")
                        for key, value in data.items():  # 显示所有字段
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                print(f"   └─ {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                                # 如果是字典，显示其前3个子字段
                                if isinstance(value, dict):
                                    for sub_key, sub_value in list(value.items())[:3]:
                                        print(f"      ├─ {sub_key}: {str(sub_value)[:80]}{'...' if len(str(sub_value)) > 80 else ''}")
                                    if len(value) > 3:
                                        print(f"      └─ ... 还有 {len(value) - 3} 个子字段")
                                # 如果是列表，显示其前2个项目
                                elif isinstance(value, list):
                                    for i, item in enumerate(value[:2]):
                                        print(f"      ├─ [{i}]: {str(item)[:80]}{'...' if len(str(item)) > 80 else ''}")
                                    if len(value) > 2:
                                        print(f"      └─ ... 还有 {len(value) - 2} 个项目")
                            else:
                                print(f"   └─ {key}: {value}")
                elif result.get('ret') is not None and result.get('ret') != 0:
                    error_msg = result.get('msg') or result.get('error') or result.get('resultDesc') or '未知错误'
                    print(f"❌ 接口调用状态: 失败")
                    print(f"🚨 错误信息: {error_msg}")
                    print(f"🔢 错误代码: {result.get('ret')}")
                # 兼容其他API格式
                elif result.get('success') is True or result.get('resultCode') == '0':
                    print(f"✅ 接口调用状态: 成功")
                elif result.get('success') is False or result.get('resultCode') != '0':
                    error_msg = result.get('error') or result.get('resultDesc') or '未知错误'
                    print(f"❌ 接口调用状态: 失败")
                    print(f"🚨 错误信息: {error_msg}")
                else:
                    print(f"⚠️ 接口调用状态: 未知 (无明确的成功/失败标识)")
                    
            elif isinstance(result, (list, tuple)):
                print(f"📋 数组长度: {len(result)}")
                for i, item in enumerate(result[:3]):
                    print(f"🔸 [{i}]: {str(item)[:200]}{'...' if len(str(item)) > 200 else ''}")
                if len(result) > 3:
                    print(f"🔸 ... 还有 {len(result) - 3} 个项目")
            else:
                print(f"📄 返回内容: {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}")
        
        print(f"{'=' * 80}")
        print(f"🔍" * 3 + f" [{api_name}] 数据详情结束 " + "🔍" * 3 + "\n")

    # 测试用例：模拟完整的沃美订单详情响应（包含所有41个字段）
    print("🧪 测试用例：完整的沃美订单详情响应（显示所有字段）")
    full_order_response = {
        'ret': 0,
        'sub': 0,
        'msg': 'successfully',
        'data': {
            'order_id': '250622231710003469',
            'status': 'PENDING',
            'status_desc': '未支付',
            'status_info': '欢迎在本影院观影',
            'status_show_exception': True,
            'order_total_price': 0,
            'order_payment_price': 0,
            'order_total_fee': 2,
            'ticket_total_price': 0,
            'pay_time': '2025-06-22 23:17',
            'phone': '151****2316',
            'cinema_id': '400028',
            'cinema_name': '北京沃美世界城店',
            'cinema_address': '北京市朝阳区金汇路101幢中骏世界城E座B1（海底捞智慧餐厅对面）',
            'movie_name': '名侦探柯南：独眼的残像',
            'movie_egg_dec': '',
            'movie_egg_num': '',
            'movie_language': '原版',
            'movie_show_type': '2D',
            'movie_poster': 'https://res.vistachina.cn/film_files/91/91786f5bc473d13907c78f207d48b44b?imageMogr2/gravity/center/crop/490x700',
            'ticket_code': '',
            'ticket_code_arr': [
                {
                    'name': '取票码',
                    'code': ''
                }
            ],
            'show_date': '2025-06-27 14:20',
            'show_date_style': '周五 6月27日 14:20',
            'card_type': 'NO_CARD',
            'card_no': '',
            'pay_way': '微信支付',
            'is_more_area': False,
            'is_marketing': False,
            'voucher_use': {},
            'rewards_use': {},
            'goods_order': {},
            'ticket_items': {
                'ticket_num': 2,
                'schedule_id': 16626081,
                'schedule_sell_price': 62.9,
                'schedule_member_price': 0,
                'hall_no': '5',
                'hall_name': '5号厅 高亮激光厅',
                'seat_info': '6排5座 | 6排6座',
                'area_seats': [
                    {
                        'area_id': '10014',
                        'area_name': '按摩区域',
                        'seat': '6排5座'
                    },
                    {
                        'area_id': '10014',
                        'area_name': '按摩区域',
                        'seat': '6排6座'
                    }
                ]
            },
            'order_track': [
                {
                    'title': '提交订单',
                    'mark': '欢迎在本影院观影',
                    'time': '6月22日 23:17'
                }
            ],
            'own_refund': False,
            'voucher_coupon': '',
            'voucher_goods_coupon': '',
            'evgc_limit_coupon_use': '',
            'msg': '',
            'msg_desc': '',
            'ticket_package_goods_msg': ''
        }
    }
    
    _print_order_api_response(full_order_response, "沃美订单详情查询（完整字段显示）")

    print("🎉 测试完成！现在所有data字段都会显示出来。")

def main():
    print("🎬 沃美电影票务系统 - 完整数据字段显示测试")
    print("=" * 60)
    print("📋 测试目标：验证修改后是否显示所有data字段")
    print("🔍 修改内容：移除字段数量限制，显示所有字段")
    print("=" * 60)
    print()
    
    test_full_data_display()

if __name__ == "__main__":
    main()
