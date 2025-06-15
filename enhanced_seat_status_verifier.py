#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版座位状态验证工具 - 集成到主程序中进行实时验证
"""

def create_integrated_verifier():
    """创建集成验证器"""
    print("🔧 创建增强版座位状态验证工具")
    print("=" * 60)
    
    # 修改主程序中的座位解析方法，添加特定座位验证
    verifier_patch = '''
# 在 main_modular.py 的 _process_seat_detail 方法中添加验证逻辑

def _process_seat_detail(self, seat_detail: dict, area_name: str, area_price: float, all_seats: list, row_num: int = None):
    """处理单个座位详情数据（增强版：包含状态验证）"""
    try:
        # 🔧 沃美座位状态映射：数字状态转换为字符串状态
        seat_status = seat_detail.get('status', 0)
        seat_no = seat_detail.get('seat_no', '')
        seat_row = int(seat_detail.get('row', row_num or 1))
        seat_col = int(seat_detail.get('col', 1))

        # 🎯 特定座位验证：1排6座、1排7座
        is_target_seat = (seat_row == 1 and seat_col in [6, 7])
        
        if is_target_seat:
            print(f"\\n🎯 [座位状态验证] 发现目标座位: {seat_row}排{seat_col}座")
            print(f"  座位编号: {seat_no}")
            print(f"  原始状态码: {seat_status}")
            print(f"  区域: {area_name}")
            print(f"  完整数据: {seat_detail}")

        # 详细的状态映射调试
        if seat_status == 0:
            status = 'available'  # 可选
            status_desc = "可选"
        elif seat_status == 1:
            status = 'sold'       # 已售
            status_desc = "已售"
        elif seat_status == 2:
            status = 'locked'     # 锁定
            status_desc = "锁定"
        else:
            status = 'available'  # 默认可选
            status_desc = f"未知状态({seat_status})->默认可选"
            print(f"[主窗口] ⚠️ 未知座位状态: {seat_no} status={seat_status}, 默认设为可选")

        # 🎯 目标座位状态验证
        if is_target_seat:
            print(f"  映射后状态: {status} ({status_desc})")
            
            # 与预期状态对比
            expected_status = "sold"  # 根据真实APP，这两个座位应该是已售
            if status == expected_status:
                print(f"  ✅ 状态映射正确: {status} == {expected_status}")
            else:
                print(f"  ❌ 状态映射不一致!")
                print(f"     系统状态: {status}")
                print(f"     预期状态: {expected_status}")
                print(f"     真实APP显示: 已售")
                
                # 🔧 状态不一致时的详细分析
                print(f"  🔍 状态不一致分析:")
                print(f"     API返回状态码: {seat_status}")
                print(f"     当前映射规则: 0=可选, 1=已售, 2=锁定")
                
                if seat_status == 1:
                    print(f"     ⚠️ 状态码1应该映射为已售，但可能UI显示有问题")
                elif seat_status == 0:
                    print(f"     ⚠️ API返回可选状态，但真实APP显示已售")
                    print(f"     可能原因: API数据不同步或状态码定义不同")
                elif seat_status == 2:
                    print(f"     ⚠️ API返回锁定状态，可能需要映射为已售")

        # 🔧 打印前10个座位的详细信息示例（保持原有逻辑）
        if len(all_seats) < 10:
            row_info = seat_detail.get('row', row_num or 1)
            col_info = seat_detail.get('col', 1)
            x_info = seat_detail.get('x', 1)
            y_info = seat_detail.get('y', row_num or 1)
            type_info = seat_detail.get('type', 0)
            print(f"[座位调试] 座位 {len(all_seats) + 1}: {seat_no}")
            print(f"  - 位置: 第{row_info}行第{col_info}列 (x={x_info}, y={y_info})")
            print(f"  - 状态: {seat_status} → {status}")
            print(f"  - 类型: {type_info}, 价格: {area_price}元")

        # 沃美座位数据格式
        seat = {
            'seat_no': seat_detail.get('seat_no', ''),
            'row': seat_row,
            'col': seat_col,
            'x': seat_detail.get('x', 1),
            'y': seat_detail.get('y', row_num or 1),
            'type': seat_detail.get('type', 0),
            'status': status,  # 使用转换后的字符串状态
            'area_name': area_name,
            'area_price': area_price,
            'price': area_price,  # 添加价格字段
            'num': str(seat_detail.get('col', 1)),  # 添加座位号显示
            'original_status': seat_status,  # 保存原始状态用于调试
            'is_target_seat': is_target_seat  # 🆕 标记是否为目标验证座位
        }

        all_seats.append(seat)
        return seat

    except Exception as e:
        print(f"[座位调试] 处理座位详情错误: {e}")
        return None
'''
    
    print("📋 验证器功能:")
    features = [
        "1. 🎯 自动识别目标座位（1排6座、1排7座）",
        "2. 📊 显示原始API状态码和映射后状态",
        "3. ✅ 自动对比预期状态（已售）",
        "4. 🔍 状态不一致时提供详细分析",
        "5. 📋 记录完整的座位数据用于调试"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    return verifier_patch

def create_ui_status_verifier():
    """创建UI状态验证器"""
    print("\n🎨 UI状态验证器:")
    print("=" * 40)
    
    ui_verifier = '''
# 在座位按钮创建时添加状态验证
# 文件: ui/components/seat_map_panel_pyqt5.py

def _update_seat_button_style(self, seat_btn, status):
    """更新座位按钮样式（增强版：包含状态验证）"""
    try:
        # 获取座位信息
        seat_data = getattr(seat_btn, 'seat_data', {})
        is_target = seat_data.get('is_target_seat', False)
        
        if is_target:
            row = seat_data.get('row', 0)
            col = seat_data.get('col', 0)
            original_status = seat_data.get('original_status', 'N/A')
            print(f"\\n🎨 [UI状态验证] 目标座位UI更新: {row}排{col}座")
            print(f"  原始状态码: {original_status}")
            print(f"  映射状态: {status}")
        
        # 原有的样式设置逻辑
        if status == "available":
            seat_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #45a049;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            if is_target:
                print(f"  UI样式: 绿色（可选）")
                
        elif status == "sold":
            seat_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: 1px solid #da190b;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            seat_btn.setEnabled(False)
            if is_target:
                print(f"  UI样式: 红色（已售）")
                print(f"  ✅ 目标座位正确显示为已售状态")
                
        elif status == "locked":
            seat_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff9800;
                    color: white;
                    border: 1px solid #f57c00;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            seat_btn.setEnabled(False)
            if is_target:
                print(f"  UI样式: 橙色（锁定）")
                
        elif status == "selected":
            seat_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: 2px solid #1976D2;
                    border-radius: 3px;
                    font-size: 10px;
                    font-weight: bold;
                }
            """)
            if is_target:
                print(f"  UI样式: 蓝色（已选）")
        else:
            # 空座位或其他状态
            seat_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #666;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                    font-size: 10px;
                }
            """)
            seat_btn.setEnabled(False)
            if is_target:
                print(f"  UI样式: 灰色（其他状态: {status}）")
                
    except Exception as e:
        print(f"更新座位按钮样式错误: {e}")
'''
    
    print("🎨 UI验证功能:")
    ui_features = [
        "1. 🎯 识别目标座位的UI更新",
        "2. 🎨 显示实际应用的样式和颜色",
        "3. ✅ 验证已售座位是否显示为红色",
        "4. 🔍 检查按钮是否正确禁用",
        "5. 📋 记录UI状态变化过程"
    ]
    
    for feature in ui_features:
        print(f"  {feature}")

def create_comprehensive_verification_plan():
    """创建综合验证计划"""
    print("\n📋 综合验证计划:")
    print("=" * 60)
    
    verification_plan = [
        {
            "阶段": "1. 数据获取验证",
            "目标": "确认API返回的原始数据",
            "操作": [
                "启动主程序并完成六级联动",
                "选择北京龙湖店 -> 新驯龙高手 -> 2025年6月15日 20:20 -> 1厅",
                "观察座位解析过程中的目标座位信息",
                "记录1排6座、1排7座的原始状态码"
            ]
        },
        {
            "阶段": "2. 状态映射验证", 
            "目标": "确认状态码映射的准确性",
            "操作": [
                "检查原始状态码（应该是0、1或2）",
                "验证映射逻辑（0=可选, 1=已售, 2=锁定）",
                "确认目标座位映射为'sold'状态",
                "对比真实APP的显示状态"
            ]
        },
        {
            "阶段": "3. UI显示验证",
            "目标": "确认座位图UI正确显示状态",
            "操作": [
                "检查1排6座、1排7座在座位图中的颜色",
                "确认已售座位显示为红色",
                "验证座位按钮是否正确禁用",
                "测试点击行为（已售座位不可选择）"
            ]
        },
        {
            "阶段": "4. 一致性验证",
            "目标": "确保与真实APP完全一致",
            "操作": [
                "对比沃美影院APP中的座位状态",
                "确认系统显示与APP显示一致",
                "验证其他座位的状态也正确",
                "测试状态变化的实时性"
            ]
        }
    ]
    
    for plan in verification_plan:
        print(f"\n{plan['阶段']}: {plan['目标']}")
        for i, operation in enumerate(plan['操作'], 1):
            print(f"  {i}. {operation}")

def main():
    """主函数"""
    print("🎬 沃美影院系统座位状态映射验证工具")
    print("=" * 60)
    
    create_integrated_verifier()
    create_ui_status_verifier()
    create_comprehensive_verification_plan()
    
    print("\n🎯 立即验证步骤:")
    print("=" * 60)
    
    immediate_steps = [
        "1. 🚀 启动主程序: python main_modular.py",
        "2. 🎯 导航到目标场次:",
        "   - 城市: 北京",
        "   - 影院: 北京龙湖店", 
        "   - 电影: 新驯龙高手",
        "   - 日期: 2025年6月15日",
        "   - 时间: 20:20",
        "   - 影厅: 1厅",
        "3. 👀 观察控制台输出:",
        "   - 查找 '[座位状态验证] 发现目标座位' 信息",
        "   - 记录1排6座、1排7座的原始状态码",
        "   - 确认映射后的状态",
        "4. 🎨 检查座位图UI:",
        "   - 找到1排6座、1排7座",
        "   - 确认颜色是否为红色（已售）",
        "   - 测试是否无法点击选择",
        "5. 📊 分析验证结果:",
        "   - 如果状态正确：验证通过",
        "   - 如果状态不正确：提供详细的错误信息"
    ]
    
    for step in immediate_steps:
        print(f"  {step}")
    
    print("\n💡 验证提示:")
    print("如果发现状态不一致，请提供以下信息：")
    print("1. 控制台中显示的原始状态码")
    print("2. 系统中座位的显示颜色")
    print("3. 真实APP中的座位状态截图")
    print("4. 完整的座位数据（从调试日志中复制）")

if __name__ == "__main__":
    main()
