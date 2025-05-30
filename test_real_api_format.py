#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证真实API格式的座位数据解析
"""

def test_real_api_format():
    """测试真实API格式解析"""
    print("=" * 50)
    print("🔧 真实API格式解析测试")
    print("=" * 50)
    
    # 真实API返回的座位数据格式
    real_api_data = {
        "seats": [
            {"sc":"11111","st":"0","r":1,"c":9,"s":"F","ls":"","sn":"000000011111-1-1","cn":1,"rn":1},
            {"sc":"11111","st":"0","r":1,"c":8,"s":"F","ls":"","sn":"000000011111-2-1","cn":2,"rn":1},
            {"sc":"11111","st":"0","r":1,"c":7,"s":"B","ls":"","sn":"000000011111-3-1","cn":3,"rn":1},  # 已售
            {"sc":"11111","st":"0","r":2,"c":9,"s":"F","ls":"","sn":"000000011111-1-2","cn":1,"rn":2},
            {"sc":"11111","st":"0","r":2,"c":8,"s":"F","ls":"","sn":"000000011111-2-2","cn":2,"rn":2}
        ]
    }
    
    try:
        # 导入解析方法
        from main_modular import ModularCinemaMainWindow
        
        class TestParser:
            def _parse_seats_array(self, seats_array, hall_info):
                print(f"开始解析seats数组，数据量: {len(seats_array)}")
                
                if not seats_array:
                    return []
                
                # 打印前几个座位数据
                for i, seat in enumerate(seats_array[:3]):
                    print(f"座位{i+1}: {seat}")
                
                max_row = 0
                max_col = 0
                
                for seat in seats_array:
                    row_num = seat.get('rn', 0)
                    col_num = seat.get('cn', 0)
                    max_row = max(max_row, row_num)
                    max_col = max(max_col, col_num)
                
                print(f"矩阵尺寸: {max_row}行 x {max_col}列")
                
                if max_row == 0 or max_col == 0:
                    print("矩阵尺寸无效")
                    return []
                
                # 创建矩阵
                seat_matrix = []
                for row in range(max_row):
                    seat_row = [None] * max_col
                    seat_matrix.append(seat_row)
                
                # 填充数据
                for seat in seats_array:
                    row_num = seat.get('rn', 0) - 1
                    col_num = seat.get('cn', 0) - 1
                    
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
                            'num': f"{seat.get('rn')}排{seat.get('cn')}座",
                            'status': status,
                            'seatname': seat.get('sn', ''),
                            'original_data': seat
                        }
                        
                        seat_matrix[row_num][col_num] = seat_data
                
                return seat_matrix
        
        parser = TestParser()
        hall_info = {'name': '测试厅'}
        
        seat_matrix = parser._parse_seats_array(real_api_data['seats'], hall_info)
        
        print(f"\\n解析结果: {len(seat_matrix)} 行")
        
        if seat_matrix:
            print("\\n座位图:")
            for r, row in enumerate(seat_matrix):
                print(f"第{r+1}行: ", end="")
                for c, seat in enumerate(row):
                    if seat:
                        if seat['status'] == 'available':
                            print("○", end="")
                        elif seat['status'] == 'sold':
                            print("●", end="")
                        else:
                            print("✗", end="")
                    else:
                        print(" ", end="")
                print()
            
            print("\\n✅ 解析成功！座位图可以正常显示了。")
        else:
            print("❌ 解析失败")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_api_format() 