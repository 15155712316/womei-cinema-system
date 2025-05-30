#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试数据结构脚本
分析API返回的真实数据格式，帮助修复场次显示问题
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_api_data():
    """分析API数据结构"""
    print("🔍 分析API数据结构...")
    
    try:
        # 1. 加载测试账号
        accounts_file = "data/accounts.json"
        if not os.path.exists(accounts_file):
            print("❌ 账号数据文件不存在")
            return
        
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not accounts:
            print("❌ 无账号数据")
            return
        
        test_account = accounts[0]
        print(f"✅ 使用测试账号: {test_account.get('userid', 'N/A')}")
        
        # 2. 加载影院数据
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        
        if not cinemas:
            print("❌ 无影院数据")
            return
        
        test_cinema = cinemas[0]
        print(f"✅ 使用测试影院: {test_cinema.get('cinemaShortName', 'N/A')}")
        
        # 3. 调用API获取数据
        from services.film_service import get_films
        
        raw_data = get_films(
            base_url=test_cinema.get('base_url', ''),
            cinemaid=test_cinema.get('cinemaid', ''),
            openid=test_account.get('openid', ''),
            userid=test_account.get('userid', ''),
            token=test_account.get('token', '')
        )
        
        print(f"\n📊 API返回数据结构分析:")
        print(f"主要键: {list(raw_data.keys())}")
        
        # 分析影片数据
        films = raw_data.get('films', [])
        print(f"\n🎬 影片数据 (共{len(films)}部):")
        if films:
            first_film = films[0]
            print(f"影片字段: {list(first_film.keys())}")
            print(f"示例影片: {first_film.get('fn', 'N/A')} (key: {first_film.get('fc', 'N/A')})")
        
        # 分析场次数据
        shows = raw_data.get('shows', {})
        print(f"\n📅 场次数据 (共{len(shows)}部影片有场次):")
        
        if shows and films:
            first_film_key = films[0].get('fc', '')
            if first_film_key in shows:
                film_shows = shows[first_film_key]
                print(f"第一部影片的场次数据: {list(film_shows.keys())}")
                
                first_date = list(film_shows.keys())[0] if film_shows else None
                if first_date:
                    sessions = film_shows[first_date]
                    print(f"\n🎭 {first_date} 的场次数据 (共{len(sessions)}个场次):")
                    
                    if sessions:
                        first_session = sessions[0]
                        print(f"场次字段: {list(first_session.keys())}")
                        print(f"场次详情:")
                        for key, value in first_session.items():
                            print(f"  {key}: {value}")
                        
                        # 测试场次显示格式
                        start_time = first_session.get('q', '未知时间')
                        hall_name = first_session.get('t', '未知厅名')
                        hall_info = first_session.get('r', '')
                        ticket_price = first_session.get('tbprice', '0')
                        
                        session_display = f"{start_time} {hall_name} {hall_info} 票价:{ticket_price}"
                        print(f"\n✅ 场次显示格式: {session_display}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_api_data() 