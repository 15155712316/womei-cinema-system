#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试影院名称获取修复
"""

import sys
import os
from utils.qrcode_generator import get_cinema_name_by_id, generate_ticket_qrcode, save_qrcode_image

def test_cinema_name_mapping():
    """测试影院名称映射"""
    print("=" * 80)
    print("🧪 测试影院名称获取修复")
    print("=" * 80)
    
    # 测试影院ID
    test_cinema_ids = [
        "35fec8259e74",  # 华夏优加荟大都荟
        "unknown_cinema_id",  # 未知影院
        "b8e8b8b8b8b8"   # 其他影院
    ]
    
    print("📋 测试影院名称获取:")
    for cinema_id in test_cinema_ids:
        cinema_name = get_cinema_name_by_id(cinema_id)
        print(f"   {cinema_id} -> {cinema_name}")
    
    print()
    
    # 🎯 测试完整的二维码生成和保存流程
    print("🎯 测试完整的二维码生成和保存流程:")
    
    test_ticket_code = "FIXED_TEST_123456"
    test_order_no = "2025060239828060"
    test_cinema_id = "35fec8259e74"
    
    test_order_info = {
        'filmName': '影院名称修复测试影片',
        'cinemaName': '华夏优加荟大都荟',
        'showTime': '2025-06-02 22:00',
        'seatInfo': '修复测试座位',
        'hallName': '修复测试影厅'
    }
    
    print(f"📋 测试参数:")
    print(f"   取票码: {test_ticket_code}")
    print(f"   订单号: {test_order_no}")
    print(f"   影院ID: {test_cinema_id}")
    
    # 生成二维码
    print(f"\n🖼️ 生成二维码...")
    qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
    
    if qr_bytes:
        print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
        
        # 保存二维码图片
        print(f"\n💾 保存二维码图片...")
        save_path = save_qrcode_image(qr_bytes, test_order_no, test_cinema_id)
        
        if save_path:
            print(f"✅ 二维码图片保存成功: {save_path}")
            
            # 检查文件名是否正确
            filename = os.path.basename(save_path)
            print(f"📁 文件名: {filename}")
            
            if "华夏优加荟大都荟" in filename:
                print(f"✅ 影院名称正确显示在文件名中")
            elif "未知影院" in filename:
                print(f"❌ 影院名称仍然显示为'未知影院'")
            else:
                print(f"⚠️ 影院名称显示异常")
                
            # 检查文件是否存在
            if os.path.exists(save_path):
                file_size = os.path.getsize(save_path)
                print(f"📏 文件大小: {file_size} bytes")
                print(f"✅ 文件保存成功")
            else:
                print(f"❌ 文件保存失败")
                
        else:
            print(f"❌ 二维码图片保存失败")
    else:
        print(f"❌ 二维码生成失败")
    
    print("\n" + "=" * 80)
    print("🏁 测试完成")
    print("=" * 80)

def test_multiple_cinema_names():
    """测试多个影院的名称获取"""
    print("\n🧪 测试多个影院名称获取:")
    
    # 从影院管理器获取所有影院
    try:
        from services.cinema_manager import CinemaManager
        cinema_manager = CinemaManager()
        cinemas = cinema_manager.get_all_cinemas()
        
        print(f"📋 找到 {len(cinemas)} 个影院:")
        
        for cinema in cinemas:
            cinema_id = cinema.get('cinemaid') or cinema.get('id', 'N/A')
            cinema_name = cinema.get('cinemaname') or cinema.get('name', 'N/A')
            print(f"   {cinema_id} -> {cinema_name}")
            
            # 测试获取函数
            retrieved_name = get_cinema_name_by_id(cinema_id)
            if retrieved_name == cinema_name:
                print(f"     ✅ 名称获取正确")
            else:
                print(f"     ❌ 名称获取错误: 期望 {cinema_name}, 实际 {retrieved_name}")
        
    except Exception as e:
        print(f"❌ 获取影院列表失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 影院名称获取修复测试启动")
    
    # 运行测试
    test_cinema_name_mapping()
    test_multiple_cinema_names()
    
    print("\n💡 现在双击订单生成的二维码文件名应该显示正确的影院名称！")
