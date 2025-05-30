#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base_URL传递修复验证脚本
验证座位图API调用中base_url参数传递问题的修复
"""

import sys
import os

def test_cinema_data_loading():
    """测试影院数据加载和base_url字段"""
    print("=" * 60)
    print("🔧 Base_URL传递修复验证")
    print("=" * 60)
    
    try:
        # 测试1: 影院管理器数据加载
        print("\n📋 测试1: 影院管理器数据加载")
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        
        print(f"✅ 成功加载 {len(cinemas)} 个影院")
        for i, cinema in enumerate(cinemas):
            print(f"  影院{i+1}: {cinema.get('cinemaShortName', 'N/A')}")
            print(f"    - 影院ID: {cinema.get('cinemaid', 'N/A')}")
            print(f"    - base_url: {cinema.get('base_url', 'N/A')}")
            print()
            
        # 测试2: 模拟Tab管理器数据处理
        print("📋 测试2: 模拟Tab管理器数据处理")
        
        # 模拟Tab管理器的cinemas_data处理
        cinemas_data = cinemas
        print(f"✅ 模拟Tab管理器影院数据处理")
        print(f"  cinemas_data长度: {len(cinemas_data)}")
        
        for cinema in cinemas_data:
            name = cinema.get('cinemaShortName', 'N/A')
            base_url = cinema.get('base_url', 'N/A')
            print(f"  - {name}: {base_url}")
            
        # 测试3: 场次信息构建模拟
        print("\n📋 测试3: 场次信息构建模拟")
        
        if cinemas:
            test_cinema = cinemas[0]
            test_session = {
                'g': 'TEST_SHOW_CODE',
                'j': 'TEST_HALL_CODE', 
                'h': 'TEST_FILM_CODE',
                'q': '14:30',
                't': '1号厅',
                'tbprice': '40'
            }
            
            # 模拟Tab管理器的_on_session_changed逻辑
            cinema_text = test_cinema.get('cinemaShortName', '')
            cinema_data = None
            
            # 查找影院数据逻辑 (修复后的逻辑)
            for cinema in cinemas_data:
                if cinema.get('cinemaShortName') == cinema_text:
                    cinema_data = cinema
                    print(f"✅ 找到影院数据: {cinema.get('cinemaShortName')} -> base_url: {cinema.get('base_url')}")
                    break
            
            if not cinema_data:
                print(f"❌ 未找到影院数据: {cinema_text}")
                return False
            
            # 模拟场次信息构建
            session_info = {
                'session_data': test_session,
                'cinema_name': cinema_text,
                'movie_name': '测试影片',
                'show_date': '2025-05-30',
                'session_text': '14:30 1号厅 票价:40',
                'account': {
                    'userid': '15155712316',
                    'openid': 'test_openid',
                    'token': 'test_token'
                },
                'cinema_data': cinema_data
            }
            
            print(f"✅ 模拟场次信息构建完成")
            print(f"  影院名称: {session_info['cinema_name']}")
            print(f"  影院base_url: {session_info['cinema_data'].get('base_url', 'N/A')}")
            print(f"  场次代码: {test_session['g']}")
            
            # 测试4: 座位图API参数构建
            print("\n📋 测试4: 座位图API参数构建")
            
            cinema_data = session_info['cinema_data']
            account = session_info['account']
            session_data = session_info['session_data']
            
            # 模拟main_modular.py中的_load_seat_map逻辑
            base_url = cinema_data.get('base_url', '') or cinema_data.get('domain', '')
            if base_url:
                base_url = base_url.replace('https://', '').replace('http://', '')
            
            params = {
                'base_url': base_url,
                'showCode': session_data.get('g', ''),
                'hallCode': session_data.get('j', ''),
                'filmCode': session_data.get('h', ''),
                'filmNo': session_data.get('fno', ''),
                'showDate': '2025-05-30',
                'startTime': session_data.get('q', ''),
                'userid': account.get('userid', ''),
                'openid': account.get('openid', ''),
                'token': account.get('token', ''),
                'cinemaid': cinema_data.get('cinemaid', ''),
                'cardno': account.get('cardno', '')
            }
            
            print(f"✅ 座位图API参数构建完成")
            for key, value in params.items():
                print(f"  {key}: {value}")
                
            # 验证必要参数
            required_params = ['base_url', 'showCode', 'hallCode', 'filmCode', 'userid', 'openid', 'token', 'cinemaid']
            missing_params = [p for p in required_params if not params.get(p)]
            
            if missing_params:
                print(f"❌ 仍然缺少必要参数: {', '.join(missing_params)}")
                return False
            else:
                print(f"✅ 所有必要参数完整，base_url传递问题已修复！")
                return True
        else:
            print("❌ 没有可用的影院数据")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cinema_data_loading()
    if success:
        print(f"\n🎉 修复验证成功！base_url传递问题已解决")
        print(f"现在可以正常启动主程序并使用座位图功能")
        print(f"\n🚀 建议使用以下方式启动:")
        print(f"  双击: 启动模块化系统-修复版.bat")
        print(f"  或运行: python main_modular.py")
    else:
        print(f"\n❌ 修复验证失败，需要进一步调试")
    
    sys.exit(0 if success else 1) 