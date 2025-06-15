#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试座位图调试信息
"""

def test_seat_map_debug():
    """测试座位图调试信息"""
    print("=== 快速测试座位图调试 ===\n")
    
    try:
        # 模拟完整的选择流程
        print("模拟用户选择流程:")
        
        # 1. 模拟沃美场次数据
        session_data = {
            'schedule_id': '16626081',
            'hall_id': '5',
            'hall_name': '5号厅 高亮激光厅',
            'show_time': '14:20',
            'selling_price': 32.9,
            'show_type': '2D',
            'language': '原版'
        }
        print(f"1. 场次数据: {session_data}")
        
        # 2. 模拟沃美影院数据
        cinema_data = {
            'cinema_id': '400028',
            'cinema_name': '北京沃美世界城店',
            'cinema_addr': '北京市朝阳区...',
            # 映射字段（主窗口需要）
            'cinemaid': '400028',
            'cinemaShortName': '北京沃美世界城店'
        }
        print(f"2. 影院数据: {cinema_data}")
        
        # 3. 模拟账号数据
        account_data = {
            'userid': 'test_user',
            'token': '47794858a832916d8eda012e7cabd269',
            'openid': 'test_openid'
        }
        print(f"3. 账号数据: {account_data}")
        
        # 4. 构建session_info（TabManagerWidget发送的）
        session_info = {
            'session_data': session_data,
            'account': account_data,
            'cinema_data': cinema_data,
            'session_text': '14:20 5号厅 高亮激光厅 2D 原版 ¥32.9'
        }
        print(f"4. session_info: {session_info}")
        
        # 5. 模拟主窗口的参数提取
        print(f"\n=== 模拟主窗口参数提取 ===")
        
        # 获取必要参数
        cinema_id = cinema_data.get('cinemaid', '')
        schedule_id = session_data.get('schedule_id', '')
        hall_id = session_data.get('hall_id', '')
        
        print(f"提取的参数:")
        print(f"  - cinema_id: {cinema_id} (来源: cinema_data.cinemaid)")
        print(f"  - schedule_id: {schedule_id} (来源: session_data.schedule_id)")
        print(f"  - hall_id: {hall_id} (来源: session_data.hall_id)")
        
        # 6. 验证参数完整性
        if all([cinema_id, schedule_id, hall_id]):
            print(f"✅ 参数验证通过")
            
            # 7. 调用座位图API
            print(f"\n=== 调用座位图API ===")
            from services.womei_film_service import get_womei_film_service
            
            service = get_womei_film_service("47794858a832916d8eda012e7cabd269")
            seat_result = service.get_hall_info(cinema_id, hall_id, schedule_id)
            
            print(f"API响应:")
            print(f"  - success: {seat_result.get('success')}")
            
            if seat_result.get('success'):
                hall_info = seat_result.get('hall_info', {})
                room_seat = hall_info.get('room_seat', [])
                
                print(f"  - hall_info字段: {list(hall_info.keys())}")
                print(f"  - room_seat区域数: {len(room_seat)}")
                
                if room_seat:
                    print(f"✅ 座位数据存在，可以解析")
                    
                    # 8. 模拟座位数据解析
                    print(f"\n=== 模拟座位数据解析 ===")
                    total_seats = 0
                    for i, area in enumerate(room_seat):
                        area_name = area.get('area_name', '未知区域')
                        area_price = area.get('area_price', 0)
                        seats_dict = area.get('seats', {})
                        
                        area_seat_count = 0
                        for row_data in seats_dict.values():
                            area_seat_count += len(row_data.get('detail', []))
                        
                        total_seats += area_seat_count
                        print(f"  区域 {i+1}: {area_name}, 价格: ¥{area_price}, 座位数: {area_seat_count}")
                    
                    print(f"  总座位数: {total_seats}")
                    
                    if total_seats > 0:
                        print(f"\n🎉 完整流程测试成功！")
                        print(f"座位图数据完整，应该能正常显示")
                        return True
                    else:
                        print(f"\n❌ 座位数据为空")
                        return False
                else:
                    print(f"❌ room_seat数据为空")
                    return False
            else:
                error = seat_result.get('error', '未知错误')
                print(f"  - error: {error}")
                return False
        else:
            print(f"❌ 参数验证失败:")
            print(f"  - cinema_id: {cinema_id} ({'✓' if cinema_id else '✗'})")
            print(f"  - schedule_id: {schedule_id} ({'✓' if schedule_id else '✗'})")
            print(f"  - hall_id: {hall_id} ({'✓' if hall_id else '✗'})")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_debug_instructions():
    """显示调试说明"""
    print("\n" + "=" * 60)
    print("🔧 座位图调试说明")
    print("=" * 60)
    
    print("\n📋 问题分析:")
    print("1. 系统混合了华联和沃美的影院数据")
    print("2. 需要选择沃美系统的城市和影院")
    print("3. 华联影院（如华夏优加荟大都荟）不在沃美系统中")
    
    print("\n✅ 正确操作步骤:")
    print("1. 在城市下拉框中选择 '北京'")
    print("2. 在影院下拉框中选择 '北京沃美世界城店'")
    print("3. 选择一部电影（如 '名侦探柯南：独眼的残像'）")
    print("4. 选择日期（如 '20250627'）")
    print("5. 选择场次（如 '14:20 5号厅 高亮激光厅 2D 原版 ¥32.9'）")
    
    print("\n🎯 预期结果:")
    print("- 选择场次后，终端会显示详细的调试信息")
    print("- 包括参数提取、API调用、座位数据解析等")
    print("- 最终应该能正常显示座位图")
    
    print("\n⚠️ 注意事项:")
    print("- 必须选择沃美系统的影院")
    print("- 华联系统的影院不支持沃美API")
    print("- 如果仍然无法加载，请检查token是否有效")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print("沃美影院系统座位图调试测试")
    print("=" * 50)
    
    # 快速测试
    success = test_seat_map_debug()
    
    # 显示调试说明
    show_debug_instructions()
    
    if success:
        print("\n🎉 快速测试成功！")
        print("请按照上述步骤在UI中进行操作")
    else:
        print("\n⚠️ 快速测试部分通过")
        print("请检查网络连接和token有效性")

if __name__ == "__main__":
    main()
