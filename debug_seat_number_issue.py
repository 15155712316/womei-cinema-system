#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试座位号显示问题
"""

def debug_seat_number_issue():
    """调试座位号显示问题"""
    print("🔍 调试座位号显示问题")
    
    # 模拟真实的API座位数据（基于您看到的"00111"问题）
    print("\n📋 模拟真实API座位数据:")
    
    # 可能的情况1：sn字段包含长字符串
    mock_api_data_case1 = [
        {
            'rn': 1,  # 行号
            'cn': 1,  # 列号
            'sn': '00111',  # 真实座位号（可能是这样的格式）
            's': 'F'   # 状态
        },
        {
            'rn': 1,
            'cn': 2,
            'sn': '00111',  # 重复的座位号？
            's': 'F'
        },
        {
            'rn': 1,
            'cn': 3,
            'sn': '00111',
            's': 'F'
        }
    ]
    
    # 可能的情况2：sn字段为空或null
    mock_api_data_case2 = [
        {
            'rn': 1,
            'cn': 1,
            'sn': '',  # 空的座位号
            's': 'F'
        },
        {
            'rn': 1,
            'cn': 2,
            'sn': None,  # null座位号
            's': 'F'
        },
        {
            'rn': 1,
            'cn': 3,
            # 缺少sn字段
            's': 'F'
        }
    ]
    
    # 可能的情况3：正常的座位号
    mock_api_data_case3 = [
        {
            'rn': 1,
            'cn': 1,
            'sn': '1',  # 正常座位号
            's': 'F'
        },
        {
            'rn': 1,
            'cn': 2,
            'sn': '2',
            's': 'F'
        },
        {
            'rn': 1,
            'cn': 3,
            'sn': '3',
            's': 'F'
        }
    ]
    
    def test_seat_parsing(case_name, seats_data):
        """测试座位解析逻辑"""
        print(f"\n🧪 测试 {case_name}:")
        
        for i, seat in enumerate(seats_data):
            print(f"   原始数据: {seat}")
            
            # 模拟当前的解析逻辑
            real_seat_num = seat.get('sn', '')  # 真实座位号
            if not real_seat_num:
                # 如果没有真实座位号，使用列号作为备选
                real_seat_num = str(seat.get('cn', i + 1))
            
            print(f"   解析结果: 显示座位号='{real_seat_num}'")
            
            # 分析问题
            if real_seat_num == '00111':
                print(f"   ⚠️  问题发现: 座位号为'00111'，这可能不是正确的座位号")
            elif not real_seat_num or real_seat_num == 'None':
                print(f"   ⚠️  问题发现: 座位号为空，使用备选逻辑")
            else:
                print(f"   ✅ 座位号正常")
    
    # 测试各种情况
    test_seat_parsing("情况1: sn字段包含'00111'", mock_api_data_case1)
    test_seat_parsing("情况2: sn字段为空或null", mock_api_data_case2)
    test_seat_parsing("情况3: 正常座位号", mock_api_data_case3)
    
    print("\n🔧 可能的解决方案:")
    print("1. 检查API返回的真实数据格式")
    print("2. 如果sn字段确实是'00111'这样的格式，可能需要:")
    print("   - 使用cn字段作为座位号")
    print("   - 或者解析sn字段的特定部分")
    print("   - 或者使用其他字段作为座位号")
    
    print("\n💡 建议的修复逻辑:")
    print("""
    def get_seat_number(seat, col_num):
        # 优先级1: 检查sn字段是否为有效的座位号
        sn = seat.get('sn', '')
        if sn and sn != '00111' and len(sn) <= 3:  # 过滤异常值
            return sn
        
        # 优先级2: 使用cn字段作为座位号
        cn = seat.get('cn', 0)
        if cn > 0:
            return str(cn)
        
        # 优先级3: 使用数组索引+1
        return str(col_num + 1)
    """)
    
    print("\n🎯 下一步行动:")
    print("1. 运行真实程序，查看控制台输出的座位数据")
    print("2. 根据真实数据调整解析逻辑")
    print("3. 测试修复效果")


def test_improved_parsing_logic():
    """测试改进的解析逻辑"""
    print("\n" + "="*60)
    print("🧪 测试改进的座位号解析逻辑")
    print("="*60)
    
    def get_seat_number_improved(seat, col_num):
        """改进的座位号获取逻辑"""
        # 优先级1: 检查sn字段是否为有效的座位号
        sn = seat.get('sn', '')
        if sn and sn != '00111' and len(str(sn)) <= 3 and str(sn).isdigit():
            return str(sn)
        
        # 优先级2: 使用cn字段作为座位号
        cn = seat.get('cn', 0)
        if cn > 0:
            return str(cn)
        
        # 优先级3: 使用数组索引+1
        return str(col_num + 1)
    
    # 测试数据
    test_cases = [
        # 正常情况
        {'rn': 1, 'cn': 1, 'sn': '1', 's': 'F'},
        {'rn': 1, 'cn': 2, 'sn': '2', 's': 'F'},
        
        # 异常情况：sn为'00111'
        {'rn': 1, 'cn': 3, 'sn': '00111', 's': 'F'},
        {'rn': 1, 'cn': 4, 'sn': '00111', 's': 'F'},
        
        # 空sn情况
        {'rn': 1, 'cn': 5, 'sn': '', 's': 'F'},
        {'rn': 1, 'cn': 6, 's': 'F'},  # 缺少sn字段
        
        # 其他异常情况
        {'rn': 1, 'cn': 7, 'sn': None, 's': 'F'},
        {'rn': 1, 'cn': 8, 'sn': 'ABC', 's': 'F'},  # 非数字
    ]
    
    print("📋 测试结果:")
    for i, seat in enumerate(test_cases):
        col_num = i  # 数组索引
        result = get_seat_number_improved(seat, col_num)
        
        print(f"   座位{i+1}: {seat}")
        print(f"   → 显示座位号: '{result}'")
        
        # 验证结果
        if result in ['1', '2', '3', '4', '5', '6', '7', '8']:
            print(f"   ✅ 结果正常")
        else:
            print(f"   ⚠️  结果异常")
        print()
    
    print("🎯 改进的解析逻辑特点:")
    print("1. ✅ 过滤掉'00111'这样的异常sn值")
    print("2. ✅ 优先使用cn字段作为座位号")
    print("3. ✅ 有完善的备选机制")
    print("4. ✅ 验证座位号的有效性（数字且长度合理）")


def main():
    """主函数"""
    debug_seat_number_issue()
    test_improved_parsing_logic()
    
    print("\n" + "="*60)
    print("📊 调试总结")
    print("="*60)
    print("🔍 问题分析:")
    print("   座位按钮显示'00111'密密麻麻，说明:")
    print("   1. API的sn字段可能包含异常值'00111'")
    print("   2. 当前解析逻辑直接使用了sn字段")
    print("   3. 需要添加数据验证和过滤逻辑")
    
    print("\n💡 解决方案:")
    print("   1. 添加sn字段的有效性验证")
    print("   2. 过滤掉'00111'这样的异常值")
    print("   3. 优先使用cn字段作为座位号")
    print("   4. 保持备选机制的完整性")
    
    print("\n🎯 下一步:")
    print("   1. 修改main_modular.py中的座位解析逻辑")
    print("   2. 添加数据验证和过滤")
    print("   3. 测试修复效果")


if __name__ == "__main__":
    main()
