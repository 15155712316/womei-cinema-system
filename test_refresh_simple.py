#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试刷新验证服务
"""

import sys
import time
from services.refresh_timer_service import refresh_timer_service

def test_refresh_service():
    """测试刷新验证服务"""
    print("=== 刷新验证服务测试 ===")
    
    # 检查初始状态
    print("1. 检查初始状态:")
    status = refresh_timer_service.get_status()
    print(f"   运行状态: {status['is_running']}")
    print(f"   当前用户: {status['current_user']}")
    print(f"   检查间隔: {status['check_interval_minutes']} 分钟")
    print(f"   定时器状态: {status['timer_active']}")
    
    # 模拟用户信息
    test_user = {
        'phone': '13800138000',
        'username': '测试用户',
        'machine_code': 'TEST123456'
    }
    
    print("\n2. 启动验证服务:")
    print(f"   用户信息: {test_user}")
    
    # 设置较短的检查间隔用于测试
    refresh_timer_service.set_check_interval(1)  # 1分钟
    
    # 启动监控
    success = refresh_timer_service.start_monitoring(test_user)
    print(f"   启动结果: {'成功' if success else '失败'}")
    
    if success:
        print("\n3. 检查启动后状态:")
        status = refresh_timer_service.get_status()
        print(f"   运行状态: {status['is_running']}")
        print(f"   当前用户: {status['current_user']}")
        print(f"   检查间隔: {status['check_interval_minutes']} 分钟")
        print(f"   定时器状态: {status['timer_active']}")
        
        print("\n4. 等待验证执行...")
        print("   (观察控制台输出，应该会看到验证日志)")
        
        # 等待几秒钟观察输出
        for i in range(10):
            print(f"   等待中... {i+1}/10")
            time.sleep(1)
        
        print("\n5. 停止验证服务:")
        refresh_timer_service.stop_monitoring()
        
        status = refresh_timer_service.get_status()
        print(f"   停止后状态: {status['is_running']}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_refresh_service()
