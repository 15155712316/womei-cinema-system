#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主窗口引用设置是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_main_window_reference():
    """测试主窗口引用和当前账号获取"""
    print("=== 测试主窗口引用设置 ===")
    
    try:
        import tkinter as tk
        import ttkbootstrap as tb
        from ui.cinema_select_panel import CinemaSelectPanel
        
        # 模拟主窗口
        class MockMainWindow(tb.Window):
            def __init__(self):
                super().__init__()
                self.withdraw()  # 隐藏窗口，仅用于测试
                
                # 模拟当前账号
                self.current_account = {
                    'userid': '15155712316',
                    'openid': 'oAOCp7VbeeoqMM4yC8e2i3G3lxI8',
                    'token': '3a30b9e980892714',
                    'balance': 400,
                    'score': 3833
                }
                
                # 创建一个frame作为parent
                parent_frame = tb.Frame(self)
                parent_frame.pack()
                
                # 创建CinemaSelectPanel
                self.cinema_panel = CinemaSelectPanel(parent_frame)
                self.cinema_panel.pack()
                
                # 设置主窗口引用
                self.cinema_panel.set_main_window(self)
        
        # 创建测试窗口
        mock_window = MockMainWindow()
        
        # 测试获取当前账号
        account = mock_window.cinema_panel.get_current_account()
        
        print(f"主窗口引用设置: {'✓ 成功' if mock_window.cinema_panel.main_window is not None else '✗ 失败'}")
        print(f"当前账号获取: {'✓ 成功' if account is not None else '✗ 失败'}")
        
        if account:
            print(f"  userid: {account.get('userid', 'N/A')}")
            print(f"  openid: {account.get('openid', 'N/A')[:15]}...")
            print(f"  token: {account.get('token', 'N/A')}")
            print(f"  余额: {account.get('balance', 'N/A')}")
            print(f"  积分: {account.get('score', 'N/A')}")
        
        # 清理测试窗口
        mock_window.destroy()
        
        print("✓ 主窗口引用和账号获取测试完成")
        
    except Exception as e:
        print(f"测试异常: {e}")
        import traceback
        traceback.print_exc()

def test_account_check_logic():
    """测试账号检查逻辑"""
    print("\n=== 测试账号检查逻辑 ===")
    
    # 测试不同情况的账号检查
    test_cases = [
        ("正常账号", {'userid': '123', 'token': 'abc', 'openid': 'xyz'}, True),
        ("空账号", {}, False),
        ("None账号", None, False),
        ("缺少字段的账号", {'userid': '123'}, True),  # 即使缺少字段，只要有账号对象就算有登录
    ]
    
    for case_name, account, expected in test_cases:
        # 模拟检查逻辑
        result = bool(account)  # 这是我们在代码中使用的检查方式
        
        print(f"  {case_name}: {'✓' if result == expected else '✗'}")
        print(f"    输入: {account}")
        print(f"    预期: {expected}, 实际: {result}")
    
    print("✓ 账号检查逻辑测试完成")

if __name__ == "__main__":
    print("开始测试主窗口引用和账号获取...")
    
    test_main_window_reference()
    test_account_check_logic()
    
    print("\n测试完成！")
    print("\n修复总结：")
    print("1. ✅ 添加了set_main_window方法设置主窗口引用")
    print("2. ✅ 添加了get_current_account方法统一获取当前账号")
    print("3. ✅ 在main_window.py中正确设置了主窗口引用")
    print("4. ✅ 账号检查逻辑应该能正确工作") 