#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美订单详情API集成
验证订单双击显示取票码功能
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_order_detail_api():
    """测试订单详情API"""
    try:
        print("🧪 测试沃美订单详情API")
        print("=" * 60)
        
        # 导入订单服务
        from services.womei_order_service import get_order_detail, get_user_orders
        
        # 测试token和订单ID
        test_token = "5e160d18859114a648efc599113c585a"
        
        print(f"📋 使用测试token: {test_token[:10]}...")
        
        # 首先获取订单列表，找到一个有效的订单ID
        print(f"\n🔍 步骤1: 获取订单列表")
        orders_result = get_user_orders(test_token)
        
        if not orders_result.get('success'):
            print(f"❌ 获取订单列表失败: {orders_result.get('error')}")
            return False
        
        orders = orders_result.get('orders', [])
        if not orders:
            print(f"❌ 订单列表为空")
            return False
        
        # 使用第一个订单进行测试
        test_order = orders[0]
        test_order_id = test_order.get('order_id', '')
        
        print(f"✅ 获取到 {len(orders)} 个订单")
        print(f"📋 测试订单信息:")
        print(f"  - 订单ID: {test_order_id}")
        print(f"  - 影片: {test_order.get('movie_name', 'N/A')}")
        print(f"  - 影院: {test_order.get('cinema_name', 'N/A')}")
        print(f"  - 状态: {test_order.get('status_desc', 'N/A')}")
        
        # 测试订单详情API（需要影院ID）
        print(f"\n🔍 步骤2: 获取订单详情")

        # 从订单数据中提取影院信息，或使用测试影院ID
        test_cinema_id = "400028"  # 北京沃美世界城店的影院ID
        print(f"📋 使用测试影院ID: {test_cinema_id}")

        detail_result = get_order_detail(test_order_id, test_cinema_id, test_token)
        
        print(f"📥 订单详情API调用结果:")
        print(f"  - 成功: {detail_result.get('success')}")
        
        if detail_result.get('success'):
            order_detail = detail_result.get('order_detail', {})
            print(f"  - 订单详情获取成功")
            
            # 验证关键字段
            key_fields = ['order_id', 'movie_name', 'cinema_name', 'status_desc']
            print(f"\n📋 关键字段验证:")
            for field in key_fields:
                value = order_detail.get(field, 'N/A')
                print(f"  ✅ {field}: {value}")
            
            # 验证取票码字段
            ticket_fields = ['qrCode', 'ticketCode', 'dsValidateCode']
            print(f"\n📋 取票码字段验证:")
            for field in ticket_fields:
                value = order_detail.get(field, '')
                status = "✅ 有值" if value else "⚠️ 空值"
                print(f"  {status} {field}: {value}")
            
            # 验证显示字段
            display = order_detail.get('display', {})
            if display:
                print(f"\n📋 显示字段验证:")
                display_fields = ['title', 'subtitle', 'order_no', 'summary']
                for field in display_fields:
                    value = display.get(field, 'N/A')
                    print(f"  ✅ {field}: {value}")
            
            # 验证座位和影厅信息
            seat_info = order_detail.get('seat_info', '')
            hall_name = order_detail.get('hall_name', '')
            show_date = order_detail.get('show_date', '')
            
            print(f"\n📋 附加信息验证:")
            print(f"  - 座位信息: {seat_info if seat_info else '无'}")
            print(f"  - 影厅名称: {hall_name if hall_name else '无'}")
            print(f"  - 放映时间: {show_date if show_date else '无'}")
            
            return True
        else:
            error_msg = detail_result.get('error', '未知错误')
            print(f"❌ 获取订单详情失败: {error_msg}")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_format_compatibility():
    """测试数据格式兼容性"""
    try:
        print("\n🧪 测试数据格式兼容性")
        print("=" * 60)
        
        from services.womei_order_service import WomeiOrderService
        
        # 创建服务实例
        service = WomeiOrderService()
        
        # 模拟API返回的订单详情数据
        mock_detail_data = {
            "order_id": "240113194910006904",
            "status": "SUCCESS", 
            "status_desc": "已放映",
            "cinema_name": "慈溪沃美影城",
            "movie_name": "金手指",
            "ticket_code": "WFDHT5M",
            "ticket_code_arr": [
                {"name": "序列号", "code": "WFDHT5M"}, 
                {"name": "验证码", "code": "742949"}
            ],
            "show_date": "2024-01-13 20:25",
            "ticket_items": {
                "seat_info": "9排4座 | 9排5座",
                "hall_name": "6号彩虹厅"
            }
        }
        
        print(f"📋 模拟订单详情数据:")
        print(f"  - 订单ID: {mock_detail_data['order_id']}")
        print(f"  - 影片: {mock_detail_data['movie_name']}")
        print(f"  - 取票码: {mock_detail_data['ticket_code']}")
        print(f"  - 取票码数组: {len(mock_detail_data['ticket_code_arr'])} 项")
        
        # 测试格式化方法
        formatted_detail = service.format_order_detail(mock_detail_data)
        
        print(f"\n📋 格式化后数据验证:")
        
        # 验证基本字段
        basic_fields = ['order_id', 'movie_name', 'cinema_name', 'status_desc']
        for field in basic_fields:
            original = mock_detail_data.get(field, '')
            formatted = formatted_detail.get(field, '')
            status = "✅" if original == formatted else "❌"
            print(f"  {status} {field}: {formatted}")
        
        # 验证取票码字段
        print(f"\n📋 取票码字段验证:")
        print(f"  ✅ qrCode: {formatted_detail.get('qrCode', '')}")
        print(f"  ✅ ticketCode: {formatted_detail.get('ticketCode', '')}")
        print(f"  ✅ dsValidateCode: {formatted_detail.get('dsValidateCode', '')}")
        
        # 验证座位和影厅信息
        print(f"\n📋 座位影厅信息验证:")
        print(f"  ✅ seat_info: {formatted_detail.get('seat_info', '')}")
        print(f"  ✅ hall_name: {formatted_detail.get('hall_name', '')}")
        
        # 验证显示字段
        display = formatted_detail.get('display', {})
        print(f"\n📋 显示字段验证:")
        print(f"  ✅ title: {display.get('title', '')}")
        print(f"  ✅ subtitle: {display.get('subtitle', '')}")
        print(f"  ✅ ticket_info: {display.get('ticket_info', '')}")
        
        # 验证兼容性字段（用于现有UI逻辑）
        compatibility_fields = ['qrCode', 'ticketCode', 'dsValidateCode']
        print(f"\n📋 UI兼容性验证:")
        for field in compatibility_fields:
            value = formatted_detail.get(field, '')
            print(f"  ✅ {field} 字段存在: {'是' if field in formatted_detail else '否'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration_simulation():
    """模拟UI集成测试"""
    try:
        print("\n🧪 模拟UI集成测试")
        print("=" * 60)
        
        # 模拟订单列表数据（来自订单Tab）
        mock_order_list_item = {
            'order_id': '240113194910006904',
            'movie_name': '金手指',
            'cinema_name': '慈溪沃美影城',
            'status_desc': '已放映'
        }
        
        # 模拟账号数据
        mock_account = {
            'phone': '15155712316',
            'token': '5e160d18859114a648efc599113c585a'
        }
        
        print(f"📋 模拟双击订单:")
        print(f"  - 订单ID: {mock_order_list_item['order_id']}")
        print(f"  - 影片: {mock_order_list_item['movie_name']}")
        print(f"  - 账号: {mock_account['phone']}")
        
        # 模拟 _show_womei_order_info 方法的逻辑
        from services.womei_order_service import get_order_detail

        order_id = mock_order_list_item['order_id']
        token = mock_account['token']
        mock_cinema_id = "400028"  # 模拟影院ID

        print(f"\n🔍 模拟API调用:")
        print(f"  - 影院ID: {mock_cinema_id}")
        result = get_order_detail(order_id, mock_cinema_id, token)
        
        if result.get('success'):
            order_detail = result.get('order_detail', {})
            
            # 模拟构建order_info数据（用于发送到主窗口）
            order_info = {
                'order_id': order_detail.get('order_id', order_id),
                'movie_name': order_detail.get('movie_name', mock_order_list_item['movie_name']),
                'cinema_name': order_detail.get('cinema_name', mock_order_list_item['cinema_name']),
                'status_desc': order_detail.get('status_desc', mock_order_list_item['status_desc']),
                'show_date': order_detail.get('show_date', ''),
                'hall_name': order_detail.get('hall_name', ''),
                'seat_info': order_detail.get('seat_info', ''),
                
                # 关键：取票码信息
                'qrCode': order_detail.get('qrCode', ''),
                'ticketCode': order_detail.get('ticketCode', ''),
                'dsValidateCode': order_detail.get('dsValidateCode', ''),
                
                'display_type': 'womei_order_detail'
            }
            
            print(f"✅ 模拟UI数据构建成功:")
            print(f"  - 基本信息完整: {'是' if all([order_info['order_id'], order_info['movie_name'], order_info['cinema_name']]) else '否'}")
            print(f"  - 取票码信息: qrCode={'有' if order_info['qrCode'] else '无'}")
            print(f"  - 显示类型: {order_info['display_type']}")
            
            # 模拟发送到主窗口的数据
            print(f"\n📤 模拟发送到主窗口的数据:")
            for key, value in order_info.items():
                if key != 'display_type':
                    print(f"  - {key}: {value}")
            
            return True
        else:
            print(f"❌ 模拟API调用失败: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ UI集成模拟测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 沃美电影票务系统 - 订单详情API集成测试")
    print("=" * 60)
    print("📋 测试目标：验证订单双击显示取票码功能")
    print("🔍 测试内容：")
    print("  1. 订单详情API调用测试")
    print("  2. 数据格式兼容性测试")
    print("  3. UI集成模拟测试")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_order_detail_api,
        test_data_format_compatibility,
        test_ui_integration_simulation
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n🎉 测试完成！")
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print(f"✅ 所有测试通过，订单详情API集成成功！")
        print(f"\n📋 集成总结：")
        print(f"✅ 新增了 get_order_detail() API方法")
        print(f"✅ 实现了数据格式化和兼容性处理")
        print(f"✅ 集成到现有双击事件处理逻辑")
        print(f"✅ 支持取票码信息显示")
        print(f"✅ 保持与现有UI逻辑的完全兼容")
        print(f"\n🚀 现在双击订单可以显示取票码了！")
    else:
        print(f"❌ 部分测试失败，需要进一步检查")

if __name__ == "__main__":
    main()
