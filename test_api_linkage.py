#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API联动功能测试脚本
测试影院→影片→日期→场次的四级联动
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_cinema_data_loading():
    """测试影院数据加载"""
    print("🎬 测试影院数据加载...")
    
    try:
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        
        print(f"✅ 成功加载 {len(cinemas)} 个影院:")
        for i, cinema in enumerate(cinemas, 1):
            print(f"  {i}. {cinema.get('cinemaShortName', '未知影院')}")
            print(f"     ID: {cinema.get('cinemaid', 'N/A')}")
            print(f"     域名: {cinema.get('base_url', 'N/A')}")
            print(f"     地址: {cinema.get('cinemaAddress', 'N/A')}")
            print()
        
        return cinemas
        
    except Exception as e:
        print(f"❌ 影院数据加载失败: {e}")
        return []

def test_film_api(cinema_data, test_account):
    """测试影片API"""
    print("🎭 测试影片API...")
    
    try:
        from services.film_service import get_films, normalize_film_data
        
        base_url = cinema_data.get('base_url', '')
        cinemaid = cinema_data.get('cinemaid', '')
        
        print(f"📡 调用API: {base_url}")
        print(f"🏢 影院ID: {cinemaid}")
        print(f"👤 用户: {test_account.get('userid', 'N/A')}")
        
        # 调用API
        films_data = get_films(
            base_url=base_url,
            cinemaid=cinemaid,
            openid=test_account.get('openid', ''),
            userid=test_account.get('userid', ''),
            token=test_account.get('token', '')
        )
        
        if not films_data:
            print("❌ API返回空数据")
            return None, None
        
        # 标准化数据
        normalized_data = normalize_film_data(films_data)
        films = normalized_data.get('films', [])
        shows = normalized_data.get('shows', {})
        
        print(f"✅ 获取到 {len(films)} 部影片:")
        for i, film in enumerate(films[:5], 1):  # 只显示前5部
            film_name = film.get('name', '未知影片')
            film_key = film.get('key', 'N/A')
            print(f"  {i}. {film_name} (key: {film_key})")
        
        if len(films) > 5:
            print(f"  ... 还有 {len(films) - 5} 部影片")
        
        print(f"📅 排期数据: {len(shows)} 部影片有排期")
        
        return films, shows
        
    except Exception as e:
        print(f"❌ 影片API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_show_data(films, shows):
    """测试排期数据"""
    print("📅 测试排期数据...")
    
    if not films or not shows:
        print("❌ 无影片或排期数据")
        return
    
    # 测试第一部影片的排期
    first_film = films[0]
    film_name = first_film.get('name', '未知影片')
    film_key = first_film.get('key', '')
    
    print(f"🎬 测试影片: {film_name}")
    
    film_shows = shows.get(film_key, {})
    if not film_shows:
        print("❌ 该影片无排期数据")
        return
    
    print(f"✅ 该影片有 {len(film_shows)} 个日期的排期:")
    
    for date, sessions in list(film_shows.items())[:3]:  # 只显示前3个日期
        print(f"  📅 {date}: {len(sessions)} 个场次")
        
        for i, session in enumerate(sessions[:2], 1):  # 每个日期只显示前2个场次
            time = session.get('time', session.get('showTime', '未知时间'))
            hall = session.get('hall', session.get('hallName', ''))
            price = session.get('price', session.get('ticketPrice', 0))
            
            session_info = f"    {i}. {time}"
            if hall:
                session_info += f" {hall}"
            if price and price > 0:
                session_info += f" ¥{price}"
            
            print(session_info)
        
        if len(sessions) > 2:
            print(f"    ... 还有 {len(sessions) - 2} 个场次")

def test_account_data():
    """测试账号数据"""
    print("👤 测试账号数据...")
    
    try:
        import json
        
        accounts_file = "data/accounts.json"
        if not os.path.exists(accounts_file):
            print("❌ 账号数据文件不存在")
            return None
        
        with open(accounts_file, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if not accounts:
            print("❌ 无账号数据")
            return None
        
        # 使用第一个账号进行测试
        test_account = accounts[0]
        
        print(f"✅ 使用测试账号:")
        print(f"  手机号: {test_account.get('userid', 'N/A')}")
        print(f"  影院ID: {test_account.get('cinemaid', 'N/A')}")
        print(f"  Token: {test_account.get('token', 'N/A')[:20]}...")
        
        return test_account
        
    except Exception as e:
        print(f"❌ 账号数据加载失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始API联动功能测试")
    print("=" * 50)
    
    # 1. 测试账号数据
    test_account = test_account_data()
    if not test_account:
        print("❌ 测试终止：无可用账号")
        return
    
    print()
    
    # 2. 测试影院数据
    cinemas = test_cinema_data_loading()
    if not cinemas:
        print("❌ 测试终止：无可用影院")
        return
    
    print()
    
    # 3. 测试影片API（使用第一个影院）
    test_cinema = cinemas[0]
    films, shows = test_film_api(test_cinema, test_account)
    
    print()
    
    # 4. 测试排期数据
    test_show_data(films, shows)
    
    print()
    print("=" * 50)
    print("✅ API联动功能测试完成！")
    
    if films and shows:
        print(f"📊 测试结果总结:")
        print(f"  - 影院数量: {len(cinemas)}")
        print(f"  - 影片数量: {len(films)}")
        print(f"  - 有排期影片: {len(shows)}")
        print(f"  - 总场次数: {sum(len(dates) for dates in shows.values())}")
    else:
        print("⚠️  部分功能测试失败，请检查网络连接和账号状态")

if __name__ == "__main__":
    main() 