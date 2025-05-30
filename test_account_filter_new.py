#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号影院关联过滤功能测试脚本
验证账号列表根据影院过滤的功能
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_account_cinema_filter():
    """测试账号影院关联过滤功能"""
    print("🧪 测试账号影院关联过滤功能")
    print("=" * 50)
    
    # 1. 测试账号数据加载
    print("📋 1. 测试账号数据加载...")
    try:
        import json
        
        accounts_file = "data/accounts.json"
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r', encoding='utf-8') as f:
                accounts = json.load(f)
            
            print(f"✅ 成功加载 {len(accounts)} 个账号")
            
            # 显示所有账号详情
            print("📋 账号详情:")
            for i, account in enumerate(accounts, 1):
                userid = account.get('userid', 'N/A')
                cinema_id = account.get('cinemaid', 'N/A')
                balance = account.get('balance', 0)
                points = account.get('points', account.get('score', 0))
                print(f"  {i}. {userid} | 影院: {cinema_id} | 余额: ¥{balance} | 积分: {points}")
            
            # 统计各影院的账号数量
            cinema_stats = {}
            for account in accounts:
                cinema_id = account.get('cinemaid', 'unknown')
                cinema_stats[cinema_id] = cinema_stats.get(cinema_id, 0) + 1
            
            print("\n📊 各影院账号统计:")
            for cinema_id, count in cinema_stats.items():
                print(f"  影院 {cinema_id}: {count} 个账号")
                
        else:
            print("❌ 账号文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 账号数据加载失败: {e}")
        return False
    
    # 2. 测试影院数据加载
    print("\n🏢 2. 测试影院数据加载...")
    try:
        from services.cinema_manager import cinema_manager
        cinemas = cinema_manager.load_cinema_list()
        
        print(f"✅ 成功加载 {len(cinemas)} 个影院")
        for i, cinema in enumerate(cinemas, 1):
            cinema_name = cinema.get('cinemaShortName', '未知影院')
            cinema_id = cinema.get('cinemaid', 'N/A')
            print(f"  {i}. {cinema_name} (ID: {cinema_id})")
            
    except Exception as e:
        print(f"❌ 影院数据加载失败: {e}")
        return False
    
    # 3. 测试过滤逻辑
    print("\n🔍 3. 测试账号过滤逻辑...")
    try:
        if cinemas and accounts:
            # 测试所有影院的过滤情况
            for i, cinema in enumerate(cinemas, 1):
                cinema_id = cinema.get('cinemaid', '')
                cinema_name = cinema.get('cinemaShortName', '')
                
                # 过滤出属于该影院的账号
                filtered_accounts = [
                    account for account in accounts 
                    if account.get('cinemaid') == cinema_id
                ]
                
                print(f"  {i}. 影院 {cinema_name} ({cinema_id}): {len(filtered_accounts)} 个账号")
                
                for j, account in enumerate(filtered_accounts, 1):
                    userid = account.get('userid', 'N/A')
                    balance = account.get('balance', 0)
                    points = account.get('points', account.get('score', 0))
                    print(f"     {j}. {userid} | 余额: ¥{balance} | 积分: {points}")
                
                if not filtered_accounts:
                    print(f"     (该影院暂无关联账号)")
                
        else:
            print("❌ 缺少影院或账号数据")
            return False
            
    except Exception as e:
        print(f"❌ 过滤逻辑测试失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ 账号影院关联过滤功能测试完成！")
    print("\n📋 测试结果总结:")
    print(f"  - 账号数据加载: ✅ 成功")
    print(f"  - 影院数据加载: ✅ 成功") 
    print(f"  - 过滤逻辑测试: ✅ 成功")
    
    return True

if __name__ == "__main__":
    success = test_account_cinema_filter()
    if not success:
        sys.exit(1) 