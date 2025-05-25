#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试正常的影院和场次功能
验证动态base_url和正常场次的座位获取
"""

import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_valid_cinema_and_sessions():
    """测试正常的影院和场次"""
    print("=== 测试正常影院和场次功能 ===")
    
    try:
        from services.film_service import get_films, get_plan_seat_info
        
        # 测试万友影城的影片获取
        test_cinema = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'cinemaid': '0f1e21d86ac8',
            'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
            'userid': '15155712316',
            'token': '3a30b9e980892714'
        }
        
        print(f"测试影院: {test_cinema['cinemaid']}")
        print(f"API域名: {test_cinema['base_url']}")
        print()
        
        # 1. 获取影片列表
        print("1. 正在获取影片列表...")
        films_result = get_films(
            test_cinema['base_url'],
            test_cinema['cinemaid'],
            test_cinema['openid'],
            test_cinema['userid'],
            test_cinema['token']
        )
        
        if films_result and films_result.get('films'):
            films = films_result['films']
            shows = films_result['shows']
            print(f"   ✓ 获取到 {len(films)} 部影片")
            
            # 显示前3部影片
            for i, film in enumerate(films[:3]):
                print(f"   影片{i+1}: {film.get('fn', '未知')} (编码: {film.get('fc', 'N/A')})")
            
            # 2. 测试第一部影片的场次
            if films and films[0]['fc'] in shows:
                first_film_code = films[0]['fc']
                first_film_shows = shows[first_film_code]
                
                print(f"\n2. 测试影片 '{films[0]['fn']}' 的场次...")
                print(f"   该影片共有 {len(first_film_shows)} 个日期的场次")
                
                # 获取最近日期的场次
                available_dates = sorted(first_film_shows.keys())
                if available_dates:
                    recent_date = available_dates[0]
                    recent_sessions = first_film_shows[recent_date]
                    
                    print(f"   日期 {recent_date} 共有 {len(recent_sessions)} 个场次")
                    
                    # 测试第一个场次的座位
                    if recent_sessions:
                        test_session = recent_sessions[0]
                        print(f"   测试场次: {test_session.get('q', 'N/A')} {test_session.get('t', 'N/A')}")
                        
                        # 3. 获取座位信息
                        print(f"\n3. 正在获取座位信息...")
                        seat_params = {
                            'base_url': test_cinema['base_url'],
                            'showCode': test_session['g'],
                            'hallCode': test_session['j'],
                            'filmCode': test_session.get('h', first_film_code),
                            'filmNo': films[0].get('fno', first_film_code),
                            'showDate': test_session['k'].split(' ')[0],
                            'startTime': test_session['q'],
                            'userid': test_cinema['userid'],
                            'openid': test_cinema['openid'],
                            'token': test_cinema['token'],
                            'cinemaid': test_cinema['cinemaid']
                        }
                        
                        print(f"   座位请求参数:")
                        for key, value in seat_params.items():
                            print(f"     {key}: {value}")
                        
                        seat_result = get_plan_seat_info(**seat_params)
                        
                        print(f"\n   座位API结果:")
                        print(f"     resultCode: {seat_result.get('resultCode', 'N/A')}")
                        print(f"     resultDesc: {seat_result.get('resultDesc', 'N/A')}")
                        print(f"     has resultData: {'Yes' if seat_result.get('resultData') else 'No'}")
                        
                        if seat_result.get('resultData') and 'seats' in seat_result['resultData']:
                            seats = seat_result['resultData']['seats']
                            available_seats = [s for s in seats if s.get('s') == 'F']
                            print(f"     座位总数: {len(seats)}")
                            print(f"     可用座位: {len(available_seats)}")
                            print(f"     已售座位: {len(seats) - len(available_seats)}")
                            
                            # 显示价格信息
                            if 'priceinfo' in seat_result['resultData']:
                                price_info = seat_result['resultData']['priceinfo']
                                print(f"     价格信息: {price_info}")
                            
                            print(f"   ✓ 座位信息获取成功")
                        else:
                            # 分析错误
                            result_desc = seat_result.get('resultDesc', '')
                            if '过期' in result_desc or '已过场' in result_desc:
                                print(f"   ⚠ 该场次已过场: {result_desc}")
                            else:
                                print(f"   ✗ 座位信息获取失败: {result_desc}")
                    else:
                        print(f"   ✗ 该日期没有场次")
                else:
                    print(f"   ✗ 该影片没有可用日期")
            else:
                print(f"   ✗ 第一部影片没有场次信息")
        else:
            print(f"   ✗ 获取影片列表失败: {films_result}")
            
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_dynamic_base_url_working():
    """测试动态base_url系统是否正常工作"""
    print("\n=== 测试动态base_url系统 ===")
    
    try:
        from services.api_base import api_base
        
        # 测试不同影院的base_url获取
        test_cases = [
            ("11b7e4bcc265", "tt7.cityfilms.cn"),    # 虹湾影城
            ("0f1e21d86ac8", "zcxzs7.cityfilms.cn"), # 万友影城
            ("61011571", "www.heibaiyingye.cn"),     # 华夏优加荟
        ]
        
        print("测试影院base_url查找:")
        for cinemaid, expected_url in test_cases:
            actual_url = api_base.get_base_url_for_cinema(cinemaid)
            status = "✓ 正确" if actual_url == expected_url else "✗ 错误"
            print(f"  影院 {cinemaid}: {actual_url} ({status})")
        
        print()
        
        # 测试API调用
        print("测试动态API调用:")
        from services.account_api import login_and_check_card
        
        # 使用万友影城测试登录API
        test_result = login_and_check_card(
            phone='15155712316',
            ck='3a30b9e980892714',
            openid='oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
            cinemaid='0f1e21d86ac8'
        )
        
        print(f"  登录API调用结果:")
        print(f"    resultCode: {test_result.get('resultCode', 'N/A')}")
        print(f"    resultDesc: {test_result.get('resultDesc', 'N/A')}")
        print(f"    has resultData: {'Yes' if test_result.get('resultData') else 'No'}")
        
        if test_result.get('resultCode') == '0':
            print(f"  ✓ 动态base_url系统工作正常")
        else:
            print(f"  ⚠ API调用返回错误，但这可能是正常的（如账号信息过期）")
            
    except Exception as e:
        print(f"动态base_url测试异常: {e}")

if __name__ == "__main__":
    print("开始测试正常影院和场次功能...")
    print()
    
    test_valid_cinema_and_sessions()
    test_dynamic_base_url_working()
    
    print("\n测试完成！")
    print()
    print("总结：")
    print("1. 动态base_url系统应该能正确路由API请求")
    print("2. 影片和场次获取应该正常工作")
    print("3. 座位信息获取应该能正确处理各种情况")
    print("4. 错误处理应该能准确识别'已过场'和其他错误") 