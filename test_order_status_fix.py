#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试订单状态判断修复
验证沃美API状态判断逻辑的修复效果
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_print_order_api_response_fix():
    """测试修复后的订单API响应打印方法"""
    
    # 模拟修复后的 _print_order_api_response 方法
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
                        print(f"📦 返回数据内容:")
                        for key, value in list(data.items())[:5]:  # 显示前5个字段
                            if isinstance(value, (dict, list)) and len(str(value)) > 100:
                                print(f"   └─ {key}: {type(value).__name__} (长度: {len(value) if isinstance(value, (list, dict)) else len(str(value))})")
                            else:
                                print(f"   └─ {key}: {value}")
                        if len(data) > 5:
                            print(f"   └─ ... 还有 {len(data) - 5} 个字段")
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

    # 测试用例1：修复前的问题场景 - 沃美API成功响应
    print("🧪 测试用例1：沃美API成功响应（修复前显示失败）")
    success_response_womei = {
        'ret': 0,
        'sub': 0,
        'msg': 'successfully',
        'data': {
            'order_id': '250622223010003436',
            'status': 'PENDING',
            'status_desc': '未支付',
            'cinema_name': '北京沃美世界城店',
            'movie_name': '分手清单',
            'show_date_style': '周一 6月23日 21:20',
            'ticket_items': {
                'hall_name': 'VIP厅 DTS:X临境音激光厅',
                'seat_info': '4排1座 | 4排2座',
                'ticket_num': 2
            },
            'order_total_price': 0,
            'order_payment_price': 0,
            'ticket_total_price': 0,
            'order_total_fee': 2,
            'phone': '151****2316',
            'pay_way': '微信支付'
        }
    }
    _print_order_api_response(success_response_womei, "沃美订单创建API（修复后）")

    # 测试用例2：沃美API失败响应
    print("🧪 测试用例2：沃美API失败响应")
    error_response_womei = {
        'ret': 1001,
        'sub': 0,
        'msg': '座位已被占用',
        'data': {}
    }
    _print_order_api_response(error_response_womei, "沃美订单创建API（失败场景）")

    # 测试用例3：其他API格式（兼容性测试）
    print("🧪 测试用例3：其他API格式（兼容性测试）")
    other_api_response = {
        'success': True,
        'resultCode': '0',
        'resultDesc': '操作成功',
        'resultData': {
            'orderno': 'OTHER123456',
            'amount': 125.8
        }
    }
    _print_order_api_response(other_api_response, "其他API格式（兼容性测试）")

    # 测试用例4：简单的沃美成功响应（验证data内容显示）
    print("🧪 测试用例4：简单的沃美成功响应（验证data内容显示）")
    simple_success = {
        'ret': 0,
        'msg': 'successfully',
        'data': {
            'order_id': 'SIMPLE123',
            'amount': 62.9,
            'status': 'created'
        }
    }
    _print_order_api_response(simple_success, "沃美简单成功响应")

    print("🎉 所有测试用例执行完成！")

def main():
    print("🎬 沃美电影票务系统 - 订单状态判断修复测试")
    print("=" * 60)
    print("📋 测试目标：验证沃美API状态判断逻辑的修复效果")
    print("🔍 修复内容：ret=0表示成功，ret!=0表示失败")
    print("🆕 新增功能：成功时显示data字段内容")
    print("=" * 60)
    print()
    
    test_print_order_api_response_fix()

if __name__ == "__main__":
    main()
