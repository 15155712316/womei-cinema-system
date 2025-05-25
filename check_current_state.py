#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前影院和账号状态
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_current_state():
    print("=== 检查当前影院和账号状态 ===")
    
    # 1. 检查影院数据
    try:
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        print(f"\n可用影院 ({len(cinemas)}个):")
        for i, cinema in enumerate(cinemas):
            name = cinema.get('cinemaShortName', '未知影院')
            cinema_id = cinema.get('cinemaid', '未知ID')
            base_url = cinema.get('base_url', '未知域名')
            print(f"  {i+1}. {name} (ID: {cinema_id}, 域名: {base_url})")
    except Exception as e:
        print(f"获取影院数据失败: {e}")
    
    # 2. 检查账号数据
    try:
        with open("data/accounts.json", "r", encoding="utf-8") as f:
            accounts = json.load(f)
        print(f"\n账号数据 ({len(accounts)}个):")
        for i, account in enumerate(accounts):
            userid = account.get('userid', '未知')
            cinemaid = account.get('cinemaid', '未知')
            balance = account.get('balance', 0)
            score = account.get('score', 0)
            is_main = account.get('is_main', False)
            main_tag = " [主账号]" if is_main else ""
            print(f"  {i+1}. {userid} @ {cinemaid} (余额:{balance}, 积分:{score}){main_tag}")
    except Exception as e:
        print(f"获取账号数据失败: {e}")
    
    # 3. 分析匹配情况
    print(f"\n=== 账号与影院匹配分析 ===")
    try:
        # 找到主账号
        main_accounts = [acc for acc in accounts if acc.get('is_main')]
        if main_accounts:
            main_account = main_accounts[0]
            main_cinemaid = main_account['cinemaid']
            main_userid = main_account['userid']
            
            print(f"主账号: {main_userid}")
            print(f"主账号影院ID: {main_cinemaid}")
            
            # 查找对应的影院
            matching_cinema = None
            for cinema in cinemas:
                if cinema.get('cinemaid') == main_cinemaid:
                    matching_cinema = cinema
                    break
            
            if matching_cinema:
                cinema_name = matching_cinema.get('cinemaShortName', '未知影院')
                print(f"✓ 找到匹配影院: {cinema_name}")
                
                # 检查是否应该自动设置
                print(f"\n预期行为:")
                print(f"1. 应该自动选择影院: {cinema_name}")
                print(f"2. 应该自动设置账号: {main_userid} (余额{main_account.get('balance', 0)})")
                print(f"3. 应该能正常选择场次和座位")
            else:
                print(f"✗ 未找到匹配的影院，主账号影院ID {main_cinemaid} 在影院列表中不存在")
        else:
            print("✗ 未找到主账号")
            
    except Exception as e:
        print(f"分析匹配情况失败: {e}")

if __name__ == "__main__":
    check_current_state() 