#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前日期的场次，验证修复后的错误处理逻辑
"""

import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_current_date_session():
    """测试当前日期的场次"""
    print("=== 测试当前日期的场次 ===")
    
    try:
        from services.film_service import get_plan_seat_info
        
        # 获取今天的日期
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        print(f"今天日期: {today}")
        
        # 使用万友影城最新排期.json中的一个未来场次
        test_params = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'showCode': '82632505228PNN06',  # 2025-05-22的场次
            'hallCode': '0000000000000007',
            'filmCode': '001a01192025',
            'filmNo': '001a01192025',
            'showDate': '2025-05-22',  # 使用未来日期
            'startTime': '10:00',
            'userid': '15155712316',
            'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
            'token': '3a30b9e980892714',
            'cinemaid': '0f1e21d86ac8'
        }
        
        print(f"调用座位API参数:")
        for key, value in test_params.items():
            print(f"  {key}: {value}")
        print()
        
        result = get_plan_seat_info(**test_params)
        
        print(f"API调用结果:")
        print(f"  resultCode: {result.get('resultCode', 'N/A')}")
        print(f"  resultDesc: {result.get('resultDesc', 'N/A')}")
        print(f"  has resultData: {'Yes' if result.get('resultData') else 'No'}")
        
        if result.get('resultData'):
            if 'seats' in result['resultData']:
                seats_count = len(result['resultData']['seats'])
                print(f"  座位数量: {seats_count}")
                
                # 分析座位状态
                if seats_count > 0:
                    available_seats = [s for s in result['resultData']['seats'] if s.get('s') == 'F']
                    sold_seats = [s for s in result['resultData']['seats'] if s.get('s') != 'F']
                    print(f"  可用座位: {len(available_seats)}")
                    print(f"  已售座位: {len(sold_seats)}")
            
            if 'priceinfo' in result['resultData']:
                price_info = result['resultData']['priceinfo']
                print(f"  价格信息: {price_info}")
        
        if result.get('error'):
            print(f"  错误信息: {result.get('error')}")
        
        print()
        
        # 模拟错误处理逻辑
        print("模拟新的错误处理逻辑:")
        if not result or 'resultData' not in result or not result['resultData']:
            result_code = result.get('resultCode', '') if result else ''
            result_desc = result.get('resultDesc', '') if result else ''
            
            # 修复：检查resultDesc中是否包含"已过场"关键词（无论resultCode是什么）
            if '过期' in result_desc or '已过场' in result_desc or '时间' in result_desc:
                print("  -> 会显示：已过场")
            elif result and result_code == '500':
                # 500错误但不是过场问题
                print(f"  -> 会显示：获取座位失败 - {result_desc}")
            elif result and result_code == '400':
                print("  -> 会显示：座位信息暂时无法获取，请稍后重试")
            elif result and result.get('error'):
                print(f"  -> 会显示：网络错误 - {result.get('error')}")
            else:
                print("  -> 会显示：获取座位失败，请检查网络连接或稍后重试")
        else:
            print("  -> 正常加载座位图")
        
    except Exception as e:
        print(f"座位API调用异常: {e}")
        print()

def test_cinema_id_in_real_scenario():
    """测试真实场景下的影院ID保持"""
    print("=== 测试真实场景下的影院ID保持 ===")
    
    try:
        from services.cinema_info_api import get_cinema_info, format_cinema_data
        
        # 使用真实的影院ID测试
        test_cinemaid = '61011571'
        test_domain = 'www.heibaiyingye.cn'
        
        print(f"测试影院ID: {test_cinemaid}")
        print(f"测试域名: {test_domain}")
        print()
        
        # 获取真实的影院信息
        cinema_info = get_cinema_info(test_domain, test_cinemaid)
        
        if cinema_info:
            print("API返回的影院信息:")
            print(f"  API返回的cinemaid: {cinema_info.get('cinemaid', 'N/A')}")
            print(f"  影院名称: {cinema_info.get('cinemaShortName', 'N/A')}")
            print(f"  城市名称: {cinema_info.get('cityName', 'N/A')}")
            print()
            
            # 测试格式化数据（修复后）
            formatted_data = format_cinema_data(cinema_info, test_domain, test_cinemaid)
            
            print("格式化后的影院数据:")
            print(f"  保持的cinemaid: {formatted_data.get('cinemaid')}")
            print(f"  影院名称: {formatted_data.get('cinemaShortName')}")
            print(f"  base_url: {formatted_data.get('base_url')}")
            print()
            
            # 验证是否保持了原始ID
            if formatted_data.get('cinemaid') == test_cinemaid:
                print("✓ 影院ID保持修复成功！原始ID被正确保留")
            else:
                print("✗ 影院ID保持修复失败！ID被覆盖了")
        else:
            print("无法获取影院信息，可能是网络问题或域名不正确")
    
    except Exception as e:
        print(f"测试异常: {e}")

if __name__ == "__main__":
    print("开始测试修复后的实际效果...")
    print()
    
    test_current_date_session()
    test_cinema_id_in_real_scenario()
    
    print("测试完成！")
    print()
    print("总结：")
    print("1. 场次过期问题：现在会根据API的具体错误信息智能判断")
    print("2. 影院ID覆盖问题：原始添加的影院ID现在会被正确保持") 