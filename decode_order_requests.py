#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解码沃美影院订单请求参数
"""

import base64
import json
import urllib.parse

def decode_base64_content(encoded_content):
    """解码Base64内容"""
    try:
        decoded_bytes = base64.b64decode(encoded_content)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except Exception as e:
        print(f"解码失败: {e}")
        return None

def parse_url_encoded_data(data):
    """解析URL编码的数据"""
    try:
        parsed = urllib.parse.parse_qs(data)
        return parsed
    except Exception as e:
        print(f"解析URL编码数据失败: {e}")
        return None

def analyze_order_requests():
    """分析订单相关请求"""
    print("🎬 沃美影院订单请求参数分析")
    print("=" * 60)
    
    # 从HAR分析中找到的关键订单请求
    order_requests = [
        {
            "name": "创建订单票务",
            "url": "/ticket/wmyc/cinema/400115/order/ticket/",
            "method": "POST",
            "encoded_body": "c2VhdGxhYmxlPTEwMDEzJTNBNyUzQTUlM0ExMTExMjIxMSUyMzA0JTIzMTAlN0MxMDAxMyUzQTclM0E0JTNBMTExMTIyMTElMjMwNCUyMzA5JnNjaGVkdWxlX2lkPTE2NjA3MTg5"
        },
        {
            "name": "订单变更",
            "url": "/ticket/wmyc/cinema/400115/order/change/?version=tp_version",
            "method": "POST", 
            "encoded_body": "b3JkZXJfaWQ9MjUwNjE1MTUyMTEwMDAxMjM5JmRpc2NvdW50X2lkPTAmZGlzY291bnRfdHlwZT1NQVJLRVJJQ1EmY2FyZF9pZD0zNzYzNTQmcGF5X3R5cGU9TUVNQkVSJnJld2FyZHM9JTVCJTVEJnVzZV9yZXdhcmRzPVkmdXNlX2xpbWl0X2NhcmRzPU4mbGltaXRfY2FyZHM9JTVCJTVEJnZvdWNoZXJfY29kZT0mdm91Y2hlcl9jb2RlX3R5cGU9JnRpY2tldF9wYWNrX2dvb2RzPQ=="
        }
    ]
    
    for i, request in enumerate(order_requests, 1):
        print(f"\n{'='*80}")
        print(f"📋 请求 {i}: {request['name']}")
        print(f"URL: {request['url']}")
        print(f"方法: {request['method']}")
        
        # 解码请求体
        decoded_body = decode_base64_content(request['encoded_body'])
        if decoded_body:
            print(f"\n📝 解码后的请求体:")
            print(f"原始数据: {decoded_body}")
            
            # 解析URL编码的参数
            parsed_params = parse_url_encoded_data(decoded_body)
            if parsed_params:
                print(f"\n📊 解析后的参数:")
                for key, values in parsed_params.items():
                    value = values[0] if values else ""
                    print(f"  {key}: {value}")
                    
                    # 特殊处理座位数据
                    if key == 'seatlable':
                        print(f"    🎯 座位数据详细分析:")
                        analyze_seat_data(value)

def analyze_seat_data(seat_data):
    """分析座位数据"""
    print(f"    原始座位数据: {seat_data}")
    
    # 座位数据格式分析
    # 从HAR中看到: 10013%3A7%3A5%3A11112211%23044%2310%7C10013%3A7%3A4%3A11112211%2304%2309
    # URL解码后应该是: 10013:7:5:11112211#04#10|10013:7:4:11112211#04#09
    
    try:
        # URL解码
        decoded_seat = urllib.parse.unquote(seat_data)
        print(f"    URL解码后: {decoded_seat}")
        
        # 分析座位格式
        if '|' in decoded_seat:
            seats = decoded_seat.split('|')
            print(f"    座位数量: {len(seats)}")
            
            for i, seat in enumerate(seats, 1):
                print(f"    座位 {i}: {seat}")
                
                # 分析座位格式 (推测格式: area_id:hall_id:row:seat_id#col#position)
                if ':' in seat:
                    parts = seat.split(':')
                    if len(parts) >= 4:
                        area_id = parts[0]
                        hall_id = parts[1] 
                        row = parts[2]
                        seat_info = parts[3]
                        
                        print(f"      区域ID: {area_id}")
                        print(f"      影厅ID: {hall_id}")
                        print(f"      排号: {row}")
                        print(f"      座位信息: {seat_info}")
                        
                        # 进一步分析座位信息
                        if '#' in seat_info:
                            seat_parts = seat_info.split('#')
                            if len(seat_parts) >= 3:
                                seat_id = seat_parts[0]
                                col_info = seat_parts[1]
                                position = seat_parts[2]
                                
                                print(f"        座位ID: {seat_id}")
                                print(f"        列信息: {col_info}")
                                print(f"        位置: {position}")
        
    except Exception as e:
        print(f"    座位数据分析失败: {e}")

def analyze_order_responses():
    """分析订单响应数据"""
    print(f"\n🔍 订单响应数据分析:")
    print("=" * 60)
    
    # 从HAR中找到的响应数据
    responses = [
        {
            "name": "创建订单票务响应",
            "encoded_response": "eyJyZXQiOjAsInN1YiI6MCwibXNnIjoic3VjY2Vzc2Z1bGx5IiwiZGF0YSI6eyJvcmRlcl9pZCI6IjI1MDYxNTUxNTIxMTAwMDEyMzkiLCJzZXJ2ZXJfdGltZSI6MTc0OTk3MjExNH19"
        },
        {
            "name": "订单变更响应",
            "encoded_response": "eyJyZXQiOjAsInN1YiI6MCwibXNnIjoic3VjY2Vzc2Z1bGx5IiwiZGF0YSI6eyJvcmRlcl9pZCI6IjI1MDYxNTUxNTIxMTAwMDEyMzkiLCJvcmRlcl90b3RhbF9wcmljZSI6MTMwLCJvcmRlcl91bmZlZV90b3RhbF9wcmljZSI6MTMwLCJvcmRlcl9wYXltZW50X3ByaWNlIjoxMzAsIm9yZGVyX3BheW1lbnRfbGltaXRfYmFsYW5jZSI6MCwib3JkZXJfcGF5bWVudF9hZnRlcl9saW1pdF9iYWxhbmNlIjowLCJsaW1pdF9zdWJfY2FyZF9wYXkiOnRydWUsInRpY2tldF90b3RhbF9wcmljZSI6MTMwLCJ0aWNrZXRfdW5mZWVfdG90YWxfcHJpY2UiOjEzMCwidGlja2V0X2Jpc19mZWUiOjQsInRpY2tldF9wYXltZW50X3RvdGFsX3ByaWNlIjoxMzAsInRpY2tldF90b3RhbA=="
        }
    ]
    
    for i, response in enumerate(responses, 1):
        print(f"\n📥 响应 {i}: {response['name']}")
        
        # 解码响应数据
        decoded_response = decode_base64_content(response['encoded_response'])
        if decoded_response:
            print(f"解码后的响应:")
            try:
                # 尝试解析JSON
                json_data = json.loads(decoded_response)
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except:
                print(decoded_response)

def create_order_api_summary():
    """创建订单API总结"""
    print(f"\n📋 沃美影院订单API总结:")
    print("=" * 60)
    
    api_summary = {
        "订单创建流程": [
            "1. 选择座位 → 调用 /order/ticket/ 创建订单",
            "2. 设置支付方式 → 调用 /order/change/ 更新订单",
            "3. 确认支付 → 完成订单"
        ],
        "关键API端点": {
            "/ticket/wmyc/cinema/{cinema_id}/order/ticket/": {
                "方法": "POST",
                "用途": "创建订单票务",
                "关键参数": {
                    "seatlable": "座位数据 (格式: area_id:hall_id:row:seat_id#col#position)",
                    "schedule_id": "场次ID"
                }
            },
            "/ticket/wmyc/cinema/{cinema_id}/order/change/": {
                "方法": "POST", 
                "用途": "订单变更/支付设置",
                "关键参数": {
                    "order_id": "订单ID",
                    "pay_type": "支付类型 (MEMBER=会员卡)",
                    "card_id": "会员卡ID",
                    "discount_type": "折扣类型"
                }
            }
        },
        "座位数据格式": {
            "格式": "area_id:hall_id:row:seat_id#col#position",
            "示例": "10013:7:5:11112211#04#10",
            "说明": {
                "area_id": "区域ID (10013)",
                "hall_id": "影厅ID (7)", 
                "row": "排号 (5)",
                "seat_id": "座位ID (11112211)",
                "col": "列号 (04)",
                "position": "位置 (10)"
            }
        }
    }
    
    print("🔄 订单创建流程:")
    for step in api_summary["订单创建流程"]:
        print(f"  {step}")
    
    print(f"\n🔗 关键API端点:")
    for endpoint, info in api_summary["关键API端点"].items():
        print(f"\n  {endpoint}")
        print(f"    方法: {info['方法']}")
        print(f"    用途: {info['用途']}")
        print(f"    关键参数:")
        for param, desc in info["关键参数"].items():
            print(f"      {param}: {desc}")
    
    print(f"\n🎯 座位数据格式:")
    print(f"  格式: {api_summary['座位数据格式']['格式']}")
    print(f"  示例: {api_summary['座位数据格式']['示例']}")
    print(f"  字段说明:")
    for field, desc in api_summary['座位数据格式']['说明'].items():
        print(f"    {field}: {desc}")

def main():
    """主函数"""
    analyze_order_requests()
    analyze_order_responses()
    create_order_api_summary()
    
    print(f"\n✅ 订单请求参数分析完成！")
    print(f"\n💡 关键发现:")
    print(f"1. 🎯 找到了订单创建的核心API: /order/ticket/")
    print(f"2. 📊 解析了座位数据格式: area_id:hall_id:row:seat_id#col#position")
    print(f"3. 💳 发现了支付设置API: /order/change/")
    print(f"4. 🔢 获得了实际的订单ID: 250615152110001239")

if __name__ == "__main__":
    main()
