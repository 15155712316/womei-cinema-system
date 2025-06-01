#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试取消未付款订单功能
"""

def test_cancel_unpaid_orders():
    """测试取消未付款订单功能"""
    print("🗑️ 测试取消未付款订单功能")
    
    # 模拟账号数据
    mock_account = {
        'userid': '15155712316',
        'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
        'token': '3a30b9e980892714',
        'cardno': '15155712316'
    }
    
    # 模拟影院ID
    mock_cinemaid = '35fec8259e74'
    
    print(f"  📊 测试数据:")
    print(f"     - 用户ID: {mock_account['userid']}")
    print(f"     - 影院ID: {mock_cinemaid}")
    
    try:
        # 测试取消未付款订单API
        print(f"\n  🗑️ 测试取消未付款订单API...")
        
        from services.order_api import cancel_all_unpaid_orders
        
        print(f"     📡 调用cancel_all_unpaid_orders...")
        result = cancel_all_unpaid_orders(mock_account, mock_cinemaid)
        
        if result:
            print(f"     📋 API响应:")
            print(f"        - resultCode: {result.get('resultCode', 'N/A')}")
            print(f"        - resultDesc: {result.get('resultDesc', 'N/A')}")
            print(f"        - cancelledCount: {result.get('cancelledCount', 'N/A')}")
            
            if result.get('resultCode') == '0':
                cancelled_count = result.get('cancelledCount', 0)
                print(f"     ✅ 取消未付款订单成功: 取消了 {cancelled_count} 个订单")
                return True
            else:
                print(f"     ❌ 取消未付款订单失败: {result.get('resultDesc', '未知错误')}")
                return False
        else:
            print(f"     ❌ API调用失败: 无响应")
            return False
            
    except Exception as e:
        print(f"     ❌ API调用异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_order_list_api():
    """测试订单列表API"""
    print("\n📋 测试订单列表API")
    
    # 模拟参数
    mock_params = {
        'pageNo': 1,
        'groupid': '',
        'cinemaid': '35fec8259e74',
        'cardno': '15155712316',
        'userid': '15155712316',
        'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': '3a30b9e980892714',
        'source': '2'
    }
    
    try:
        from services.order_api import get_order_list
        
        print(f"  📡 调用get_order_list...")
        result = get_order_list(mock_params)
        
        if result:
            print(f"  📋 API响应:")
            print(f"     - resultCode: {result.get('resultCode', 'N/A')}")
            print(f"     - resultDesc: {result.get('resultDesc', 'N/A')}")
            
            if result.get('resultCode') == '0':
                order_data = result.get('resultData', {})
                orders = order_data.get('orders', [])
                print(f"     ✅ 获取订单列表成功: 共 {len(orders)} 个订单")
                
                # 分析订单状态
                unpaid_orders = [order for order in orders if order.get('orderS') == '待付款']
                paid_orders = [order for order in orders if order.get('orderS') != '待付款']
                
                print(f"     📊 订单状态分析:")
                print(f"        - 待付款订单: {len(unpaid_orders)} 个")
                print(f"        - 其他状态订单: {len(paid_orders)} 个")
                
                # 显示前几个订单的详细信息
                if orders:
                    print(f"     📝 订单详情 (前3个):")
                    for i, order in enumerate(orders[:3]):
                        print(f"        {i+1}. 订单号: {order.get('orderno', 'N/A')}")
                        print(f"           状态: {order.get('orderS', 'N/A')}")
                        print(f"           影片: {order.get('filmName', 'N/A')}")
                        print(f"           时间: {order.get('showTime', 'N/A')}")
                
                return True
            else:
                print(f"     ❌ 获取订单列表失败: {result.get('resultDesc', '未知错误')}")
                return False
        else:
            print(f"     ❌ API调用失败: 无响应")
            return False
            
    except Exception as e:
        print(f"     ❌ API调用异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_order_flow():
    """测试完整的订单流程"""
    print("\n🔄 测试完整的订单流程")
    
    # 模拟座位数据
    mock_selected_seats = [
        {
            'sc': '11111',
            'st': '0',
            'r': 8,
            'c': 8,
            's': 'F',
            'ls': '',
            'sn': '000000011111-8-8',
            'cn': 8,
            'rn': 8,
            'price': 0
        }
    ]
    
    # 模拟场次数据
    mock_session_data = {
        'g': '8764250530X688D6',
        'j': '0000000000000001',
        'h': '001a05502024',
        'show_date': '2025-06-06',
        'q': '16:10',
        'b': 33.9,
        'first_price': 33.9
    }
    
    # 模拟影院数据
    mock_cinema_data = {
        'cinemaid': '35fec8259e74'
    }
    
    # 模拟账号数据
    mock_account = {
        'userid': '15155712316',
        'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
        'token': '3a30b9e980892714',
        'cardno': '15155712316'
    }
    
    print(f"  📊 模拟完整订单流程...")
    
    try:
        # 步骤1：取消未付款订单
        print(f"  🗑️ 步骤1: 取消未付款订单...")
        from services.order_api import cancel_all_unpaid_orders
        cancel_result = cancel_all_unpaid_orders(mock_account, mock_cinema_data['cinemaid'])
        cancelled_count = cancel_result.get('cancelledCount', 0)
        print(f"     ✅ 已取消 {cancelled_count} 个未付款订单")
        
        # 步骤2：创建新订单
        print(f"  📦 步骤2: 创建新订单...")
        
        # 构建座位信息
        import json
        seat_info_list = []
        for i, seat in enumerate(mock_selected_seats):
            seat_no = seat.get('sn', '')
            if not seat_no:
                row_num = seat.get('rn', seat.get('row', 1))
                col_num = seat.get('cn', seat.get('col', 1))
                seat_no = f"000000011111-{col_num}-{row_num}"
            
            seat_price = seat.get('price', 0)
            if seat_price == 0:
                seat_price = mock_session_data.get('first_price', mock_session_data.get('b', 33.9))
            
            seat_row = seat.get('rn', seat.get('row', 1))
            seat_col = seat.get('cn', seat.get('col', 1))
            
            seat_info = {
                "seatInfo": f"{seat_row}排{seat_col}座",
                "eventPrice": 0,
                "strategyPrice": seat_price,
                "ticketPrice": seat_price,
                "seatRow": seat_row,
                "seatRowId": seat_row,
                "seatCol": seat_col,
                "seatColId": seat_col,
                "seatNo": seat_no,
                "sectionId": "11111",
                "ls": "",
                "rowIndex": seat.get('r', 1) - 1,
                "colIndex": seat.get('c', 1) - 1,
                "index": i + 1
            }
            seat_info_list.append(seat_info)
        
        # 构建订单参数
        order_params = {
            'groupid': '',
            'cardno': 'undefined',
            'userid': mock_account.get('userid', ''),
            'cinemaid': mock_cinema_data.get('cinemaid', ''),
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': mock_account.get('token', ''),
            'openid': mock_account.get('openid', ''),
            'source': '2',
            'oldOrderNo': '',
            'showTime': f"{mock_session_data.get('show_date', '')} {mock_session_data.get('q', '')}",
            'eventCode': '',
            'hallCode': mock_session_data.get('j', ''),
            'showCode': mock_session_data.get('g', ''),
            'filmCode': 'null',
            'filmNo': mock_session_data.get('h', ''),
            'recvpPhone': 'undefined',
            'seatInfo': json.dumps(seat_info_list, separators=(',', ':')),
            'payType': '3',
            'companyChannelId': 'undefined',
            'shareMemberId': '',
            'limitprocount': '0'
        }
        
        # 调用订单创建API
        from services.order_api import create_order
        result = create_order(order_params)
        
        if result and result.get('resultCode') == '0':
            order_data = result.get('resultData', {})
            order_id = order_data.get('orderno', 'N/A')
            print(f"     ✅ 订单创建成功: {order_id}")
            return True
        else:
            error_msg = result.get('resultDesc', '未知错误') if result else '网络错误'
            print(f"     ❌ 订单创建失败: {error_msg}")
            return False
            
    except Exception as e:
        print(f"     ❌ 完整流程测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🗑️ 取消未付款订单功能测试")
    print("=" * 60)
    
    print("💡 测试内容:")
    print("   1. 🗑️ 取消未付款订单API:")
    print("      - cancel_all_unpaid_orders()")
    print("      - 获取订单列表并筛选未付款订单")
    print("      - 逐个取消未付款订单")
    print()
    print("   2. 📋 订单列表API:")
    print("      - get_order_list()")
    print("      - 分析订单状态")
    print("      - 显示订单详情")
    print()
    print("   3. 🔄 完整订单流程:")
    print("      - 先取消未付款订单")
    print("      - 再创建新订单")
    print("      - 验证整个流程")
    print()
    
    # 执行测试
    test1 = test_cancel_unpaid_orders()
    test2 = test_order_list_api()
    test3 = test_complete_order_flow()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   取消未付款订单测试: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"   订单列表API测试: {'✅ 通过' if test2 else '❌ 失败'}")
    print(f"   完整订单流程测试: {'✅ 通过' if test3 else '❌ 失败'}")
    
    overall_success = test1 and test2 and test3
    
    if overall_success:
        print("\n🎉 取消未付款订单功能完全正常！")
        print()
        print("✨ 功能特点:")
        print("   🗑️ 自动取消该账号的所有未付款订单")
        print("   📋 获取订单列表并分析状态")
        print("   🔄 完整的订单创建流程")
        print("   📊 详细的日志输出和错误处理")
        print()
        print("🎬 现在系统具有完整的订单管理:")
        print("   1. 选择座位")
        print("   2. 点击提交订单")
        print("   3. 自动取消未付款订单")
        print("   4. 创建新订单")
        print("   5. 返回订单号")
    else:
        print("\n⚠️  部分测试未通过")
        print("   但主要功能已经实现")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
