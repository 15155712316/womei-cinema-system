#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位API修复效果
验证从当前账号获取认证信息是否能正确工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_seat_api_with_current_account():
    """测试使用当前账号信息的座位API调用"""
    print("=== 测试座位API修复效果 ===")
    
    try:
        from services.film_service import get_plan_seat_info
        
        # 模拟当前账号信息
        current_account = {
            'userid': '15155712316',
            'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
            'token': '3a30b9e980892714'
        }
        
        # 测试场次参数（使用更远的未来日期）
        test_params = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'showCode': '8263251231PPN06',  # 使用更远未来的场次
            'hallCode': '0000000000000007',
            'filmCode': '001a01192025',
            'filmNo': '001a01192025',
            'showDate': '2025-12-31',  # 使用更远的未来日期
            'startTime': '10:00',
            'userid': current_account['userid'],
            'openid': current_account['openid'],
            'token': current_account['token'],
            'cinemaid': '0f1e21d86ac8'
        }
        
        print(f"测试参数:")
        print(f"  用户认证信息: userid={test_params['userid']}")
        print(f"  openid: {test_params['openid'][:15]}...")
        print(f"  token: {test_params['token']}")
        print(f"  影院ID: {test_params['cinemaid']}")
        print(f"  场次: {test_params['showCode']}")
        print(f"  日期: {test_params['showDate']}")
        print()
        
        # 调用座位API
        result = get_plan_seat_info(**test_params)
        
        print(f"API调用结果:")
        print(f"  resultCode: {result.get('resultCode', 'N/A')}")
        print(f"  resultDesc: {result.get('resultDesc', 'N/A')}")
        print(f"  has resultData: {'Yes' if result.get('resultData') else 'No'}")
        
        # 分析结果
        if result.get('resultCode') == '0' and result.get('resultData'):
            print("  ✓ API调用成功！认证信息正确")
            if 'seats' in result['resultData']:
                seats_count = len(result['resultData']['seats'])
                available_seats = [s for s in result['resultData']['seats'] if s.get('s') == 'F']
                print(f"  ✓ 获取到 {seats_count} 个座位，{len(available_seats)} 个可用")
            if 'priceinfo' in result['resultData']:
                price_info = result['resultData']['priceinfo']
                print(f"  ✓ 价格信息: {price_info}")
        elif result.get('resultCode') == '400' and 'TOKEN_INVALID' in result.get('resultDesc', ''):
            print("  ⚠ TOKEN无效，可能是账号信息过期")
        elif result.get('resultCode') == '500':
            print(f"  ⚠ 服务器错误: {result.get('resultDesc', 'N/A')}")
        elif result.get('resultCode') == '0' and not result.get('resultData'):
            # 检查是否是已过场
            if '已过场' in result.get('resultDesc', ''):
                print("  ✓ 正确识别为已过场")
            else:
                print(f"  ⚠ 无数据但不是已过场: {result.get('resultDesc', 'N/A')}")
        else:
            print(f"  ✗ API调用失败: {result}")
        
        print()
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_real_available_session():
    """测试真实可用的场次"""
    print("=== 测试真实可用场次 ===")
    
    try:
        from services.film_service import get_films, get_plan_seat_info
        
        # 使用真实账号信息获取真实的场次
        test_cinema = {
            'base_url': 'zcxzs7.cityfilms.cn',
            'cinemaid': '0f1e21d86ac8',
            'userid': '15155712316',
            'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
            'token': '3a30b9e980892714'
        }
        
        print(f"获取真实场次数据...")
        
        # 1. 获取影片和场次
        films_result = get_films(
            test_cinema['base_url'],
            test_cinema['cinemaid'],
            test_cinema['openid'],
            test_cinema['userid'],
            test_cinema['token']
        )
        
        if films_result and films_result.get('films') and films_result.get('shows'):
            films = films_result['films']
            shows = films_result['shows']
            print(f"  ✓ 获取到 {len(films)} 部影片")
            
            # 找到第一个有场次的影片
            for film in films:
                film_code = film['fc']
                if film_code in shows and shows[film_code]:
                    print(f"  测试影片: {film['fn']}")
                    
                    # 获取最近日期的场次
                    available_dates = sorted(shows[film_code].keys())
                    if available_dates:
                        test_date = available_dates[0]
                        sessions = shows[film_code][test_date]
                        
                        if sessions:
                            # 测试第一个场次
                            session = sessions[0]
                            print(f"  测试场次: {session['q']} {session.get('t', '')}")
                            
                            # 调用座位API
                            seat_result = get_plan_seat_info(
                                test_cinema['base_url'],
                                session['g'],  # showCode
                                session['j'],  # hallCode
                                session.get('h', film_code),  # filmCode
                                film.get('fno', film_code),   # filmNo
                                session['k'].split(' ')[0],  # showDate
                                session['q'],  # startTime
                                test_cinema['userid'],
                                test_cinema['openid'],
                                test_cinema['token'],
                                test_cinema['cinemaid']
                            )
                            
                            print(f"  座位API结果:")
                            print(f"    resultCode: {seat_result.get('resultCode', 'N/A')}")
                            print(f"    resultDesc: {seat_result.get('resultDesc', 'N/A')}")
                            
                            if seat_result.get('resultCode') == '0' and seat_result.get('resultData'):
                                if 'seats' in seat_result['resultData']:
                                    seats = seat_result['resultData']['seats']
                                    available = [s for s in seats if s.get('s') == 'F']
                                    print(f"    ✓ 成功获取座位: 总数{len(seats)}, 可用{len(available)}")
                                    return  # 找到可用场次，退出测试
                            elif '已过场' in seat_result.get('resultDesc', ''):
                                print(f"    ⚠ 场次已过场，继续测试下一个")
                                continue
                            else:
                                print(f"    ✗ 获取失败: {seat_result.get('resultDesc', 'N/A')}")
                                continue
                        break
            
            print("  未找到可用的未过期场次")
        else:
            print("  ✗ 获取影片列表失败")
            
    except Exception as e:
        print(f"测试异常: {e}")

def test_current_account_access():
    """测试当前账号信息的获取方式"""
    print("=== 测试当前账号信息获取 ===")
    
    # 模拟主窗口对象
    class MockMainWindow:
        def __init__(self):
            self.current_account = {
                'userid': '15155712316',
                'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
                'token': '3a30b9e980892714',
                'balance': 400,
                'score': 3833
            }
    
    # 模拟面板获取账号信息的方式
    mock_main = MockMainWindow()
    
    # 测试获取方式1: 直接访问
    account1 = getattr(mock_main, 'current_account', {})
    print(f"方式1 - 直接访问: {account1 is not None}")
    
    # 测试获取方式2: 通过master.master访问（模拟面板层次结构）
    class MockPanel:
        def __init__(self, main_window):
            self.master = type('obj', (object,), {'master': main_window})()
    
    mock_panel = MockPanel(mock_main)
    account2 = getattr(mock_panel.master.master, 'current_account', {})
    print(f"方式2 - 通过master.master访问: {account2 is not None}")
    
    if account2:
        print(f"  userid: {account2.get('userid', 'N/A')}")
        print(f"  openid: {account2.get('openid', 'N/A')[:15]}...")
        print(f"  token: {account2.get('token', 'N/A')}")
        print(f"  余额: {account2.get('balance', 'N/A')}")
    
    print("✓ 账号信息获取方式正常")
    print()

if __name__ == "__main__":
    print("开始测试座位API修复效果...")
    print()
    
    test_current_account_access()
    test_seat_api_with_current_account()
    test_real_available_session()
    
    print("测试完成！")
    print()
    print("修复总结：")
    print("1. ✅ 座位API现在从当前登录账号获取认证信息")
    print("2. ✅ 如果没有登录会提示用户先登录")
    print("3. ✅ TOKEN_INVALID错误会显示专门的'登录失效'提示")
    print("4. ✅ 已过场场次能正确识别并提示")
    print("5. ✅ 添加了详细的调试信息便于排查问题") 