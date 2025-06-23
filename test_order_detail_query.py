#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美订单详情查询功能
验证订单信息接口的调用和数据打印
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_order_detail_query():
    """测试订单详情查询功能"""
    try:
        # 加载账号信息
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not accounts:
            print("❌ 没有可用的账号信息")
            return
        
        account = accounts[0]
        token = account.get('token', '')
        cinema_id = '400028'  # 北京沃美世界城店
        
        if not token:
            print("❌ 账号token为空")
            return
        
        print("🧪 测试沃美订单详情查询功能")
        print("=" * 60)
        print(f"🏪 影院ID: {cinema_id}")
        print(f"🔑 Token: {token[:20]}...")
        print("=" * 60)
        
        # 创建API适配器
        from cinema_api_adapter import create_womei_api
        api = create_womei_api(token)
        
        # 测试订单ID（您提供的示例）
        test_order_id = "250622223010003436"
        
        print(f"📡 查询订单详情: {test_order_id}")
        print("-" * 40)
        
        # 调用订单详情接口
        result = api.get_order_info(cinema_id, test_order_id)
        
        # 模拟主程序中的格式化打印方法
        _print_order_api_response(result, f"沃美订单详情查询 (订单号: {test_order_id})")
        
        # 如果查询成功，打印订单摘要
        if result and result.get('ret') == 0:
            data = result.get('data', {})
            _print_order_summary(data, test_order_id)
        else:
            error_msg = result.get('msg', '查询失败') if result else '网络错误'
            print(f"❌ 查询失败: {error_msg}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()

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
            important_fields = ['ret', 'sub', 'msg', 'data']
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
            if result.get('ret') == 0:
                print(f"✅ 接口调用状态: 成功")
            else:
                error_msg = result.get('msg', '未知错误')
                print(f"❌ 接口调用状态: 失败")
                print(f"🚨 错误信息: {error_msg}")
                
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

def _print_order_summary(order_data: dict, order_id: str):
    """打印订单摘要信息"""
    try:
        print(f"\n" + "📋" * 3 + f" 订单摘要 (订单号: {order_id}) " + "📋" * 3)
        print(f"{'=' * 80}")
        
        # 基本信息
        print(f"🎫 订单状态: {order_data.get('status_desc', 'N/A')} ({order_data.get('status', 'N/A')})")
        print(f"🏪 影院: {order_data.get('cinema_name', 'N/A')}")
        print(f"🎬 影片: {order_data.get('movie_name', 'N/A')}")
        print(f"🕐 场次: {order_data.get('show_date_style', 'N/A')}")
        
        # 座位信息
        ticket_items = order_data.get('ticket_items', {})
        if ticket_items:
            print(f"🎭 影厅: {ticket_items.get('hall_name', 'N/A')}")
            print(f"🪑 座位: {ticket_items.get('seat_info', 'N/A')}")
            print(f"🎟️ 票数: {ticket_items.get('ticket_num', 0)}")
        
        # 价格信息
        print(f"💰 票价: ¥{order_data.get('ticket_total_price', 0)}")
        print(f"💳 总价: ¥{order_data.get('order_total_price', 0)}")
        print(f"💸 实付: ¥{order_data.get('order_payment_price', 0)}")
        print(f"🔢 手续费: ¥{order_data.get('order_total_fee', 0)}")
        
        # 联系信息
        print(f"📱 手机: {order_data.get('phone', 'N/A')}")
        print(f"💳 支付方式: {order_data.get('pay_way', 'N/A')}")
        
        # 取票信息
        ticket_code_arr = order_data.get('ticket_code_arr', [])
        if ticket_code_arr:
            for ticket_code_info in ticket_code_arr:
                code_name = ticket_code_info.get('name', '取票码')
                code_value = ticket_code_info.get('code', '暂无')
                print(f"🎫 {code_name}: {code_value}")
        
        # 订单跟踪
        order_track = order_data.get('order_track', [])
        if order_track:
            print(f"📈 订单跟踪:")
            for track in order_track:
                print(f"   └─ {track.get('time', 'N/A')}: {track.get('title', 'N/A')} - {track.get('mark', 'N/A')}")
        
        print(f"{'=' * 80}")
        print(f"📋" * 3 + f" 订单摘要结束 " + "📋" * 3 + "\n")
        
    except Exception as e:
        print(f"[订单摘要] ❌ 打印摘要失败: {e}")

def main():
    print("🎬 沃美电影票务系统 - 订单详情查询测试")
    print("=" * 60)
    print("📋 测试目标：验证沃美订单信息接口的调用和数据打印")
    print("🔍 测试内容：查询指定订单的详细信息并格式化输出")
    print("=" * 60)
    print()
    
    test_order_detail_query()

if __name__ == "__main__":
    main()
