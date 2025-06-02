#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试影院数据结构
"""

from services.cinema_manager import CinemaManager

def debug_cinema_data():
    """调试影院数据结构"""
    print("=" * 80)
    print("🔍 调试影院数据结构")
    print("=" * 80)
    
    try:
        # 获取影院管理器
        cinema_manager = CinemaManager()
        
        # 加载影院列表
        cinemas = cinema_manager.load_cinema_list()
        
        print(f"📋 找到 {len(cinemas)} 个影院")
        print()
        
        # 详细分析每个影院的数据结构
        for i, cinema in enumerate(cinemas):
            print(f"🏛️ 影院 {i+1}:")
            print(f"   数据类型: {type(cinema)}")
            print(f"   所有字段:")
            
            for key, value in cinema.items():
                print(f"     {key}: {value} ({type(value)})")
            
            print()
            
            # 尝试不同的字段名组合
            possible_id_fields = ['cinemaid', 'id', 'cinema_id', 'cinemaId']
            possible_name_fields = ['cinemaname', 'name', 'cinema_name', 'cinemaName', 'title']
            
            print(f"   🔍 查找ID字段:")
            for field in possible_id_fields:
                if field in cinema:
                    print(f"     ✅ {field}: {cinema[field]}")
                else:
                    print(f"     ❌ {field}: 不存在")
            
            print(f"   🔍 查找名称字段:")
            for field in possible_name_fields:
                if field in cinema:
                    print(f"     ✅ {field}: {cinema[field]}")
                else:
                    print(f"     ❌ {field}: 不存在")
            
            print("-" * 60)
        
        # 特别检查目标影院
        target_cinema_id = "35fec8259e74"
        print(f"🎯 特别检查目标影院: {target_cinema_id}")
        
        for cinema in cinemas:
            # 检查所有可能的ID字段
            cinema_ids = [
                cinema.get('cinemaid'),
                cinema.get('id'),
                cinema.get('cinema_id'),
                cinema.get('cinemaId')
            ]
            
            if target_cinema_id in cinema_ids:
                print(f"✅ 找到目标影院!")
                print(f"   完整数据: {cinema}")
                
                # 尝试获取名称
                cinema_names = [
                    cinema.get('cinemaname'),
                    cinema.get('name'),
                    cinema.get('cinema_name'),
                    cinema.get('cinemaName'),
                    cinema.get('title')
                ]
                
                print(f"   可能的名称:")
                for i, name in enumerate(cinema_names):
                    if name:
                        print(f"     选项{i+1}: {name}")
                
                break
        else:
            print(f"❌ 未找到目标影院 {target_cinema_id}")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cinema_data()
