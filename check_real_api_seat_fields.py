#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查真实API座位数据中的字段
"""

def check_real_api_seat_fields():
    """检查真实API座位数据中的字段"""
    print("🔍 检查真实API座位数据中的字段")
    
    # 根据您之前的截图，我们看到座位显示的是"00111"
    # 这说明API返回的数据可能是这样的结构
    
    print("\n📋 根据您的描述和截图分析:")
    print("1. 您说 cn/rn 是物理座位，用于构建座位图")
    print("2. 您说 c/n 是真实座位号，用于显示和提交")
    print("3. 您明确说不是 sn 参数")
    
    print("\n🤔 可能的API数据结构:")
    
    # 可能的结构1：使用 c 和 n 字段
    mock_api_structure_1 = {
        'rn': 1,    # 物理行号
        'cn': 1,    # 物理列号
        'c': 1,     # 真实列号（座位号）
        'n': '1',   # 真实座位号
        's': 'F'    # 状态
    }
    
    # 可能的结构2：使用 col 和 num 字段
    mock_api_structure_2 = {
        'rn': 1,      # 物理行号
        'cn': 1,      # 物理列号
        'col': 1,     # 真实列号
        'num': '1',   # 真实座位号
        's': 'F'      # 状态
    }
    
    # 可能的结构3：使用 row 和 seat 字段
    mock_api_structure_3 = {
        'rn': 1,       # 物理行号
        'cn': 1,       # 物理列号
        'row': 1,      # 真实行号
        'seat': '1',   # 真实座位号
        's': 'F'       # 状态
    }
    
    print("可能的结构1 (c/n字段):")
    print(f"  {mock_api_structure_1}")
    
    print("可能的结构2 (col/num字段):")
    print(f"  {mock_api_structure_2}")
    
    print("可能的结构3 (row/seat字段):")
    print(f"  {mock_api_structure_3}")
    
    print("\n💡 建议的解决方案:")
    print("1. 先运行真实程序，选择一个场次")
    print("2. 查看控制台输出的座位数据")
    print("3. 确认API返回的真实字段名")
    print("4. 根据真实字段名修改代码")
    
    print("\n🔧 如果API数据中确实有 c 和 n 字段:")
    print("我们需要修改代码使用这些字段:")
    
    code_example = '''
    # 修改座位数据解析
    real_seat_num = seat.get('n', '')  # 使用 n 字段作为真实座位号
    if not real_seat_num:
        real_seat_num = str(seat.get('c', col_num + 1))  # 使用 c 字段作为备选
    
    seat_data = {
        'row': seat.get('r', seat.get('rn', row_num + 1)),  # 真实行号
        'col': seat.get('c', seat.get('cn', col_num + 1)),  # 真实列号
        'num': real_seat_num,  # 真实座位号
        # ...
    }
    '''
    
    print(code_example)
    
    print("\n🎯 下一步行动:")
    print("1. 请您运行程序并选择一个场次")
    print("2. 查看控制台输出的完整座位数据")
    print("3. 告诉我真实的字段名")
    print("4. 我会根据真实字段名修改代码")


def analyze_seat_display_issue():
    """分析座位显示问题"""
    print("\n" + "="*60)
    print("🎭 分析座位显示问题")
    print("="*60)
    
    print("🔍 问题现象:")
    print("1. 显示的还是物理座位号")
    print("2. 提交订单也是物理座位号")
    print("3. 不是真实的座位号")
    
    print("\n🤔 可能的原因:")
    print("1. API数据中没有 r 和 n 字段")
    print("2. 字段名不是 r 和 n，而是其他名称")
    print("3. 代码中的字段映射不正确")
    print("4. 备选逻辑使用了物理座位号")
    
    print("\n💡 解决思路:")
    print("1. 首先确认API数据的真实结构")
    print("2. 找到正确的真实座位号字段")
    print("3. 修改代码使用正确的字段")
    print("4. 测试显示和提交功能")
    
    print("\n📋 需要您提供的信息:")
    print("1. 真实API返回的座位数据结构")
    print("2. 真实座位号字段的确切名称")
    print("3. 真实排数字段的确切名称")
    
    print("\n🎯 临时解决方案:")
    print("如果您知道确切的字段名，我可以立即修改代码")
    print("例如：")
    print("- 如果真实座位号字段是 'seatNum'，我会使用 seat.get('seatNum', '')")
    print("- 如果真实排数字段是 'rowNum'，我会使用 seat.get('rowNum', '')")


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 检查真实API座位数据字段")
    print("=" * 60)
    
    check_real_api_seat_fields()
    analyze_seat_display_issue()
    
    print("\n" + "=" * 60)
    print("📊 总结")
    print("=" * 60)
    
    print("🎯 关键问题:")
    print("   需要确认API数据中真实座位号的字段名")
    
    print("\n💡 解决方案:")
    print("   1. 运行程序查看真实API数据")
    print("   2. 确认字段名")
    print("   3. 修改代码使用正确字段")
    
    print("\n🔧 请您:")
    print("   1. 运行 main_modular.py")
    print("   2. 选择一个场次")
    print("   3. 查看控制台输出的座位数据")
    print("   4. 告诉我真实的字段名")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
