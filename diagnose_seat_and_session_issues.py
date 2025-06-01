#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断座位图和场次问题
"""

import json
import sys
import requests
from datetime import datetime


def diagnose_session_loading():
    """诊断场次加载问题"""
    print("🎬 诊断场次加载问题")
    
    try:
        # 模拟获取影片数据
        from services.film_service import get_films
        
        # 测试影院参数
        test_cinema = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'cinemaid': '35fec8259e74',
            'name': '华夏优加荟大都荟'
        }
        
        test_account = {
            'userid': '15155712316',
            'openid': 'oJhOJ5Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8',
            'token': 'test_token'
        }
        
        print(f"  🏢 测试影院: {test_cinema['name']}")
        print(f"  👤 测试账号: {test_account['userid']}")
        
        # 获取影片数据
        print(f"\n  📡 获取影片数据...")
        films_result = get_films(
            base_url=test_cinema['base_url'],
            userid=test_account['userid'],
            openid=test_account['openid'],
            token=test_account['token'],
            cinemaid=test_cinema['cinemaid']
        )
        
        if films_result and films_result.get('resultCode') == '0':
            films_data = films_result.get('resultData', {})
            films = films_data.get('films', [])
            
            print(f"  ✅ 成功获取 {len(films)} 部影片")
            
            # 分析每部影片的排期
            for i, film in enumerate(films[:3]):  # 只分析前3部
                film_name = film.get('fn', 'Unknown')
                plans = film.get('plans', [])
                
                print(f"\n  🎬 影片 {i+1}: {film_name}")
                print(f"     排期数量: {len(plans)}")
                
                if plans:
                    # 分析排期数据结构
                    print(f"     排期示例:")
                    for j, plan in enumerate(plans[:3]):  # 只显示前3个排期
                        show_time = plan.get('k', 'N/A')
                        hall_name = plan.get('j', 'N/A')
                        price = plan.get('b', 'N/A')
                        
                        print(f"       {j+1}. 时间: {show_time}")
                        print(f"          影厅: {hall_name}")
                        print(f"          价格: {price}")
                        
                        # 检查日期格式
                        if show_time and ' ' in show_time:
                            date_part = show_time.split(' ')[0]
                            time_part = show_time.split(' ')[1] if len(show_time.split(' ')) > 1 else ''
                            print(f"          日期部分: {date_part}")
                            print(f"          时间部分: {time_part}")
                        
                        print()
                    
                    # 分析日期分布
                    dates = set()
                    for plan in plans:
                        show_time = plan.get('k', '')
                        if show_time and ' ' in show_time:
                            date_part = show_time.split(' ')[0]
                            dates.add(date_part)
                    
                    print(f"     可用日期: {sorted(list(dates))}")
                else:
                    print(f"     ❌ 无排期数据")
        else:
            error_msg = films_result.get('resultDesc', '未知错误') if films_result else '请求失败'
            print(f"  ❌ 获取影片数据失败: {error_msg}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ 场次诊断异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def diagnose_seat_api():
    """诊断座位图API问题"""
    print("\n🪑 诊断座位图API问题")
    
    try:
        from services.film_service import get_plan_seat_info
        
        # 测试参数（使用真实的场次数据）
        test_params = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'showCode': 'test_show_code',  # 需要真实的showCode
            'hallCode': 'test_hall_code',  # 需要真实的hallCode
            'filmCode': 'test_film_code',  # 需要真实的filmCode
            'filmNo': 'test_film_no',      # 需要真实的filmNo
            'userid': '15155712316',
            'openid': 'oJhOJ5Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8',
            'token': 'test_token',
            'cinemaid': '35fec8259e74',
            'cardno': ''
        }
        
        print(f"  📋 测试参数:")
        for key, value in test_params.items():
            print(f"     {key}: {value}")
        
        # 先检查参数完整性
        required_params = ['base_url', 'showCode', 'hallCode', 'filmCode', 'userid', 'openid', 'token', 'cinemaid']
        missing_params = [p for p in required_params if not test_params.get(p) or test_params[p] == f'test_{p.lower()}']
        
        if missing_params:
            print(f"  ⚠️  缺少真实参数: {missing_params}")
            print(f"  💡 需要从真实的场次选择中获取这些参数")
            return False
        
        print(f"\n  📡 调用座位图API...")
        
        # 调用API
        seat_result = get_plan_seat_info(**test_params)
        
        print(f"  📊 API响应类型: {type(seat_result)}")
        
        if seat_result:
            if isinstance(seat_result, dict):
                result_code = seat_result.get('resultCode', 'N/A')
                result_desc = seat_result.get('resultDesc', 'N/A')
                
                print(f"  📋 响应结构:")
                print(f"     resultCode: {result_code}")
                print(f"     resultDesc: {result_desc}")
                
                if result_code == '0':
                    # 成功响应，分析座位数据
                    result_data = seat_result.get('resultData', {})
                    print(f"  ✅ API调用成功")
                    print(f"  📊 座位数据字段: {list(result_data.keys())}")
                    
                    # 分析座位数据结构
                    if 'seats' in result_data:
                        seats = result_data['seats']
                        print(f"     seats数组长度: {len(seats) if isinstance(seats, list) else 'Not a list'}")
                        
                        if isinstance(seats, list) and len(seats) > 0:
                            print(f"     座位示例:")
                            for i, seat in enumerate(seats[:3]):
                                print(f"       座位 {i+1}: {seat}")
                    
                    # 分析影厅信息
                    hall_info = {
                        'name': result_data.get('hname', 'N/A'),
                        'screen_type': result_data.get('screentype', 'N/A'),
                        'seat_count': result_data.get('seatcount', 'N/A')
                    }
                    print(f"  🏛️  影厅信息: {hall_info}")
                    
                    return True
                else:
                    print(f"  ❌ API返回错误: {result_desc}")
                    return False
            else:
                print(f"  ❌ API响应格式错误: 不是字典类型")
                return False
        else:
            print(f"  ❌ API无响应")
            return False
        
    except Exception as e:
        print(f"  ❌ 座位图API诊断异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def diagnose_data_parsing():
    """诊断数据解析问题"""
    print("\n🔍 诊断数据解析问题")
    
    try:
        # 模拟座位数据解析
        mock_seat_data = {
            'hname': '1号激光厅',
            'screentype': 'IMAX',
            'seatcount': 78,
            'seats': [
                {'rn': 1, 'cn': 1, 'sn': 'A1', 'st': 'A'},
                {'rn': 1, 'cn': 2, 'sn': 'A2', 'st': 'B'},
                {'rn': 2, 'cn': 1, 'sn': 'B1', 'st': 'A'},
                {'rn': 2, 'cn': 2, 'sn': 'B2', 'st': 'A'},
            ]
        }
        
        print(f"  📊 模拟座位数据:")
        print(f"     影厅: {mock_seat_data['hname']}")
        print(f"     类型: {mock_seat_data['screentype']}")
        print(f"     座位数: {mock_seat_data['seatcount']}")
        print(f"     座位数组长度: {len(mock_seat_data['seats'])}")
        
        # 测试解析逻辑
        seats_array = mock_seat_data['seats']
        
        # 计算矩阵大小
        max_row = max(seat.get('rn', 1) for seat in seats_array)
        max_col = max(seat.get('cn', 1) for seat in seats_array)
        
        print(f"  📐 矩阵大小: {max_row} 行 × {max_col} 列")
        
        # 创建座位矩阵
        seat_matrix = [[None for _ in range(max_col)] for _ in range(max_row)]
        
        # 填充座位数据
        for seat in seats_array:
            row_num = seat.get('rn', 1) - 1  # 转换为0基索引
            col_num = seat.get('cn', 1) - 1  # 转换为0基索引
            
            # 状态映射
            seat_state = seat.get('st', 'A')
            if seat_state == 'A':
                status = 'available'
            elif seat_state == 'B':
                status = 'sold'
            else:
                status = 'unavailable'
            
            seat_data = {
                'row': seat.get('rn', row_num + 1),
                'col': seat.get('cn', col_num + 1),
                'num': f"{seat.get('rn', row_num + 1)}-{seat.get('cn', col_num + 1)}",
                'status': status,
                'price': 0,
                'seatname': seat.get('sn', ''),
                'original_data': seat
            }
            
            seat_matrix[row_num][col_num] = seat_data
        
        print(f"  ✅ 座位矩阵创建成功")
        print(f"  📋 座位矩阵示例:")
        for i, row in enumerate(seat_matrix):
            row_seats = []
            for seat in row:
                if seat:
                    row_seats.append(f"{seat['num']}({seat['status'][0]})")
                else:
                    row_seats.append("None")
            print(f"     第{i+1}行: {row_seats}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 数据解析诊断异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def diagnose_ui_integration():
    """诊断UI集成问题"""
    print("\n🖥️  诊断UI集成问题")
    
    try:
        # 检查座位图组件是否存在
        try:
            from ui.components.seat_map_panel_pyqt5 import SeatMapPanelPyQt5
            print(f"  ✅ 座位图组件导入成功")
            
            # 测试组件创建
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            seat_panel = SeatMapPanelPyQt5()
            print(f"  ✅ 座位图组件创建成功")
            
            # 测试数据更新
            mock_data = [
                [
                    {'row': 1, 'col': 1, 'num': '1-1', 'status': 'available'},
                    {'row': 1, 'col': 2, 'num': '1-2', 'status': 'sold'}
                ],
                [
                    {'row': 2, 'col': 1, 'num': '2-1', 'status': 'available'},
                    {'row': 2, 'col': 2, 'num': '2-2', 'status': 'available'}
                ]
            ]
            
            seat_panel.update_seat_data(mock_data)
            print(f"  ✅ 座位图数据更新成功")
            
            return True
            
        except ImportError as e:
            print(f"  ❌ 座位图组件导入失败: {e}")
            return False
        
    except Exception as e:
        print(f"  ❌ UI集成诊断异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主诊断函数"""
    print("=" * 60)
    print("🔍 座位图和场次问题诊断")
    print("=" * 60)
    
    print("🎯 诊断目标:")
    print("   1. 🎬 场次加载问题 - 为什么显示'暂无场次'")
    print("   2. 🪑 座位图API问题 - 为什么数据解析失败")
    print("   3. 🔍 数据解析问题 - 解析逻辑是否正确")
    print("   4. 🖥️  UI集成问题 - 组件是否正常工作")
    print()
    
    # 执行诊断
    results = []
    
    print("开始诊断...")
    print()
    
    # 1. 场次加载诊断
    result1 = diagnose_session_loading()
    results.append(("场次加载", result1))
    
    # 2. 座位图API诊断
    result2 = diagnose_seat_api()
    results.append(("座位图API", result2))
    
    # 3. 数据解析诊断
    result3 = diagnose_data_parsing()
    results.append(("数据解析", result3))
    
    # 4. UI集成诊断
    result4 = diagnose_ui_integration()
    results.append(("UI集成", result4))
    
    # 总结诊断结果
    print("\n" + "=" * 60)
    print("📊 诊断结果总结:")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ 正常" if result else "❌ 异常"
        print(f"   {name}: {status}")
    
    # 分析问题原因
    print("\n🔍 问题分析:")
    
    if not results[0][1]:  # 场次加载问题
        print("   🎬 场次加载问题可能原因:")
        print("      - API返回的数据格式变化")
        print("      - 日期匹配逻辑错误")
        print("      - 排期数据结构解析错误")
        print("      - 网络连接问题")
    
    if not results[1][1]:  # 座位图API问题
        print("   🪑 座位图API问题可能原因:")
        print("      - 缺少真实的场次参数(showCode, hallCode等)")
        print("      - 账号认证问题(token过期)")
        print("      - API接口变更")
        print("      - 参数格式错误")
    
    if not results[2][1]:  # 数据解析问题
        print("   🔍 数据解析问题可能原因:")
        print("      - 座位数据结构变化")
        print("      - 矩阵计算错误")
        print("      - 状态映射错误")
        print("      - 索引越界")
    
    if not results[3][1]:  # UI集成问题
        print("   🖥️  UI集成问题可能原因:")
        print("      - 组件导入路径错误")
        print("      - PyQt5版本兼容性")
        print("      - 信号连接问题")
        print("      - 布局管理错误")
    
    # 提供解决建议
    print("\n💡 解决建议:")
    print("   1. 🔧 立即修复:")
    print("      - 检查API返回的真实数据格式")
    print("      - 验证场次参数的正确性")
    print("      - 测试座位图组件的独立功能")
    print()
    print("   2. 🧪 深入调试:")
    print("      - 添加详细的API调用日志")
    print("      - 保存API响应数据用于分析")
    print("      - 单步调试座位矩阵创建过程")
    print()
    print("   3. 🛠️  长期优化:")
    print("      - 增加错误处理和重试机制")
    print("      - 优化数据解析的健壮性")
    print("      - 改进用户错误提示")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
