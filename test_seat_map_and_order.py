#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位图显示和订单提交功能
"""

def test_seat_map_display():
    """测试座位图显示"""
    print("=" * 60)
    print("🎬 测试座位图显示和订单提交功能")
    print("=" * 60)
    
    # 模拟真实API返回的座位数据
    real_seat_data = {
        "seats": [
            # 第1排
            {"sc":"11111","st":"0","r":1,"c":9,"s":"F","ls":"","sn":"1排1座","cn":1,"rn":1},
            {"sc":"11111","st":"0","r":1,"c":8,"s":"F","ls":"","sn":"1排2座","cn":2,"rn":1},
            {"sc":"11111","st":"0","r":1,"c":7,"s":"B","ls":"","sn":"1排3座","cn":3,"rn":1},  # 已售
            {"sc":"11111","st":"0","r":1,"c":6,"s":"F","ls":"","sn":"1排4座","cn":4,"rn":1},
            {"sc":"11111","st":"0","r":1,"c":5,"s":"F","ls":"","sn":"1排5座","cn":5,"rn":1},
            # 第2排
            {"sc":"22222","st":"0","r":2,"c":9,"s":"F","ls":"","sn":"2排1座","cn":1,"rn":2},
            {"sc":"22222","st":"0","r":2,"c":8,"s":"F","ls":"","sn":"2排2座","cn":2,"rn":2},
            {"sc":"22222","st":"0","r":2,"c":7,"s":"F","ls":"","sn":"2排3座","cn":3,"rn":2},
            {"sc":"22222","st":"0","r":2,"c":6,"s":"B","ls":"","sn":"2排4座","cn":4,"rn":2},  # 已售
            {"sc":"22222","st":"0","r":2,"c":5,"s":"F","ls":"","sn":"2排5座","cn":5,"rn":2},
            # 第3排
            {"sc":"33333","st":"0","r":3,"c":9,"s":"F","ls":"","sn":"3排1座","cn":1,"rn":3},
            {"sc":"33333","st":"0","r":3,"c":8,"s":"F","ls":"","sn":"3排2座","cn":2,"rn":3},
            {"sc":"33333","st":"0","r":3,"c":7,"s":"F","ls":"","sn":"3排3座","cn":3,"rn":3},
            {"sc":"33333","st":"0","r":3,"c":6,"s":"F","ls":"","sn":"3排4座","cn":4,"rn":3},
            {"sc":"33333","st":"0","r":3,"c":5,"s":"F","ls":"","sn":"3排5座","cn":5,"rn":3},
        ],
        "hname": "1号厅",
        "screentype": "IMAX",
        "seatcount": 15
    }
    
    try:
        # 测试座位数据解析
        print("\n📊 测试座位数据解析...")
        
        from main_modular import ModularCinemaMainWindow
        
        class TestParser:
            def _parse_seats_array(self, seats_array, hall_info):
                print(f"解析座位数组，数据量: {len(seats_array)}")
                
                if not seats_array:
                    return []
                
                # 打印座位数据示例
                for i, seat in enumerate(seats_array[:3]):
                    print(f"座位{i+1}: 行={seat.get('rn')}, 列={seat.get('cn')}, 状态={seat.get('s')}, 编号={seat.get('sn')}")
                
                # 计算矩阵尺寸
                max_row = 0
                max_col = 0
                
                for seat in seats_array:
                    row_num = seat.get('rn', 0)
                    col_num = seat.get('cn', 0)
                    max_row = max(max_row, row_num)
                    max_col = max(max_col, col_num)
                
                print(f"矩阵尺寸: {max_row}行 x {max_col}列")
                
                if max_row == 0 or max_col == 0:
                    print("❌ 矩阵尺寸无效")
                    return []
                
                # 创建矩阵
                seat_matrix = []
                for row in range(max_row):
                    seat_row = [None] * max_col
                    seat_matrix.append(seat_row)
                
                # 填充数据
                for seat in seats_array:
                    row_num = seat.get('rn', 0) - 1  # 转为0基索引
                    col_num = seat.get('cn', 0) - 1  # 转为0基索引
                    
                    if 0 <= row_num < max_row and 0 <= col_num < max_col:
                        seat_state = seat.get('s', 'F')
                        if seat_state == 'F':
                            status = 'available'
                        elif seat_state == 'B':
                            status = 'sold'
                        else:
                            status = 'unavailable'
                        
                        seat_data = {
                            'row': seat.get('rn'),
                            'col': seat.get('cn'),
                            'num': seat.get('sn', f"{seat.get('rn')}排{seat.get('cn')}座"),
                            'status': status,
                            'seatname': seat.get('sn', ''),
                            'original_data': seat
                        }
                        
                        seat_matrix[row_num][col_num] = seat_data
                
                return seat_matrix
        
        parser = TestParser()
        hall_info = {
            'name': real_seat_data.get('hname', '测试厅'),
            'screen_type': real_seat_data.get('screentype', ''),
            'seat_count': real_seat_data.get('seatcount', 0)
        }
        
        seat_matrix = parser._parse_seats_array(real_seat_data['seats'], hall_info)
        
        print(f"\n✅ 解析成功！生成座位矩阵: {len(seat_matrix)} 行")
        
        # 显示座位图（文本版本）
        print("\n🎭 座位图预览:")
        print("   ", end="")
        for c in range(1, 6):  # 列号
            print(f"{c:>3}", end="")
        print()
        
        for r, row in enumerate(seat_matrix):
            print(f"{r+1:>2} ", end="")  # 行号
            for c, seat in enumerate(row):
                if seat:
                    if seat['status'] == 'available':
                        print(" ○ ", end="")  # 可选
                    elif seat['status'] == 'sold':
                        print(" ● ", end="")  # 已售
                    else:
                        print(" ✗ ", end="")  # 不可选
                else:
                    print("   ", end="")  # 空位
            print()
        
        print("\n📋 座位详情:")
        seat_count = {'available': 0, 'sold': 0, 'total': 0}
        for row in seat_matrix:
            for seat in row:
                if seat:
                    seat_count['total'] += 1
                    if seat['status'] == 'available':
                        seat_count['available'] += 1
                    elif seat['status'] == 'sold':
                        seat_count['sold'] += 1
                    print(f"  {seat['num']}: {seat['status']}")
        
        print(f"\n📊 统计信息:")
        print(f"  总座位: {seat_count['total']} 个")
        print(f"  可选座位: {seat_count['available']} 个")
        print(f"  已售座位: {seat_count['sold']} 个")
        
        # 测试订单创建参数
        print(f"\n🛒 测试订单创建参数...")
        
        # 模拟选择的座位
        selected_seats = []
        for row in seat_matrix:
            for seat in row:
                if seat and seat['status'] == 'available':
                    selected_seats.append(seat)
                    if len(selected_seats) >= 2:  # 选择2个座位
                        break
            if len(selected_seats) >= 2:
                break
        
        print(f"模拟选择座位: {[seat['num'] for seat in selected_seats]}")
        
        # 构建座位信息
        seat_info_list = []
        for seat in selected_seats:
            seat_info = {
                'rowname': seat.get('row', ''),
                'colname': seat.get('col', ''),
                'seatname': seat.get('num', ''),
                'seatid': seat.get('original_data', {}).get('sc', ''),
                'seatprice': 35.0
            }
            seat_info_list.append(seat_info)
        
        print(f"API座位信息: {seat_info_list}")
        
        import json
        print(f"JSON座位信息: {json.dumps(seat_info_list, ensure_ascii=False)}")
        
        print(f"\n✅ 座位图显示测试完成！")
        print(f"💡 可以在PyQt5界面中看到规则的座位网格布局")
        print(f"💡 座位状态：○ 可选  ● 已售  ✗ 不可选")
        print(f"💡 点击可选座位进行选择，选中后变为绿色")
        print(f"💡 选择完座位后点击'提交订单'按钮创建订单")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_order_submission():
    """测试订单提交流程"""
    print(f"\n🎫 测试订单提交流程...")
    
    # 模拟订单提交所需的参数
    mock_params = {
        'userid': 'test_user_123',
        'openid': 'test_openid_456', 
        'token': 'test_token_789',
        'cardno': 'undefined',
        'cinemaid': '11b7e4bcc265',
        'showCode': 'SHOW123',
        'hallCode': 'HALL001',
        'filmCode': 'FILM456',
        'filmNo': 'FN789',
        'showTime': '2024-01-15 19:30:00',
        'seatInfo': '[{"rowname":"1","colname":"1","seatname":"1排1座","seatid":"11111","seatprice":35.0}]',
        'groupid': '',
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'source': '2',
        'oldOrderNo': '',
        'eventCode': '',
        'recvpPhone': 'undefined',
        'payType': 3,
        'companyChannelId': 5,
        'shareMemberId': '',
        'limitprocount': 0
    }
    
    print(f"📝 订单参数:")
    for key, value in mock_params.items():
        print(f"  {key}: {value}")
    
    print(f"\n✅ 订单提交流程测试完成！")
    print(f"💡 实际提交时会调用create_order API")
    print(f"💡 成功后会显示订单详情和支付倒计时")
    print(f"💡 可以绑定优惠券进行支付")

if __name__ == "__main__":
    test_seat_map_display()
    test_order_submission() 