#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试订单调试输出功能
验证格式化打印订单接口返回信息的效果
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_print_order_api_response():
    """测试格式化打印订单API响应的方法"""
    
    # 模拟 _print_order_api_response 方法
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
                
                # 按重要性排序显示字段
                important_fields = ['success', 'resultCode', 'resultDesc', 'error', 'order_id', 'orderno']
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
                
                # 判断接口调用结果
                print(f"{'-' * 80}")
                if result.get('success') is True or result.get('resultCode') == '0':
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

    # 测试用例1：成功的订单响应
    print("🧪 测试用例1：成功的沃美订单响应")
    success_response = {
        'success': True,
        'resultCode': '0',
        'resultDesc': '订单创建成功',
        'order_id': 'WOMEI202506221234567890',
        'order_info': {
            'total_amount': 125.8,
            'seat_count': 2,
            'cinema_name': '北京沃美世界城店',
            'movie_name': '名侦探柯南：独眼的残像',
            'show_time': '14:20',
            'hall_name': '5号厅 高亮激光厅'
        },
        'payment_info': {
            'payment_url': 'https://pay.womovie.cn/pay/12345',
            'expire_time': '2025-06-22 14:35:00'
        },
        'seats': [
            {'row': 8, 'col': 3, 'seat_no': '11051771#01#08', 'price': 62.9},
            {'row': 8, 'col': 4, 'seat_no': '11051771#01#07', 'price': 62.9}
        ]
    }
    _print_order_api_response(success_response, "沃美订单创建API")

    # 测试用例2：失败的订单响应
    print("🧪 测试用例2：失败的订单响应")
    error_response = {
        'success': False,
        'resultCode': '1001',
        'resultDesc': '座位已被占用',
        'error': '选择的座位不可用',
        'error_details': {
            'unavailable_seats': ['8排3座', '8排4座'],
            'reason': '座位状态已变更'
        }
    }
    _print_order_api_response(error_response, "沃美订单创建API")

    # 测试用例3：网络错误
    print("🧪 测试用例3：网络错误（返回None）")
    _print_order_api_response(None, "沃美订单创建API")

    # 测试用例4：复杂的嵌套数据
    print("🧪 测试用例4：复杂的嵌套数据")
    complex_response = {
        'success': True,
        'resultCode': '0',
        'order_id': 'COMPLEX123456',
        'detailed_info': {
            'cinema': {'id': '400028', 'name': '北京沃美世界城店', 'address': '北京市朝阳区金汇路101幢'},
            'movie': {'id': '1539714', 'name': '名侦探柯南：独眼的残像', 'duration': 109},
            'session': {'id': '16626081', 'time': '14:20', 'hall': '5号厅'},
            'seats': [
                {'row': i, 'col': j, 'price': 62.9, 'area': '中心区域'} 
                for i in range(1, 6) for j in range(1, 11)
            ],
            'pricing': {
                'base_price': 62.9,
                'service_fee': 2.0,
                'discount': -5.0,
                'total': 59.9
            }
        },
        'metadata': {
            'request_id': 'req_' + str(datetime.now().timestamp()),
            'server_time': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    }
    _print_order_api_response(complex_response, "复杂数据测试API")

    # 测试用例5：数组类型响应
    print("🧪 测试用例5：数组类型响应")
    array_response = [
        {'order_id': 'ORDER001', 'status': 'pending'},
        {'order_id': 'ORDER002', 'status': 'paid'},
        {'order_id': 'ORDER003', 'status': 'cancelled'}
    ]
    _print_order_api_response(array_response, "订单列表API")

    print("🎉 所有测试用例执行完成！")

def main():
    print("🎬 沃美电影票务系统 - 订单调试输出测试")
    print("=" * 60)
    print("📋 测试目标：验证格式化打印订单接口返回信息的效果")
    print("🔍 测试内容：不同类型的API响应数据格式化输出")
    print("=" * 60)
    print()
    
    test_print_order_api_response()

if __name__ == "__main__":
    main()
