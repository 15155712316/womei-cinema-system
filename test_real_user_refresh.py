#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实用户的刷新验证服务
"""

import sys
import os
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_real_user_refresh():
    """测试真实用户的刷新验证"""
    print("=== 真实用户刷新验证测试 ===\n")
    
    try:
        from services.refresh_timer_service import refresh_timer_service
        from services.auth_service import auth_service
        
        print("✅ 成功导入服务模块")
        
        # 获取真实用户输入
        print("\n📱 请输入要测试的手机号:")
        phone = input("手机号 (11位): ").strip()
        
        if not phone or len(phone) != 11 or not phone.isdigit():
            print("❌ 手机号格式不正确")
            return
        
        print(f"\n🔍 测试用户: {phone}")
        
        # 首先测试登录API
        print(f"\n1️⃣ 测试登录API:")
        success, message, user_info = auth_service.login(phone)
        
        if success:
            print(f"   ✅ 登录成功: {message}")
            print(f"   📋 用户信息: {user_info}")
            
            # 测试刷新验证服务
            print(f"\n2️⃣ 测试刷新验证服务:")
            
            # 设置较短的检查间隔
            refresh_timer_service.set_check_interval(1)  # 1分钟
            
            # 启动监控
            success = refresh_timer_service.start_monitoring(user_info)
            
            if success:
                print(f"   ✅ 刷新验证服务启动成功")
                print(f"   ⏰ 检查间隔: 1分钟")
                print(f"   🔄 等待验证执行...")
                
                # 等待几秒钟观察输出
                for i in range(10):
                    print(f"   等待中... {i+1}/10")
                    time.sleep(1)
                
                # 检查服务状态
                status = refresh_timer_service.get_status()
                print(f"\n3️⃣ 服务状态:")
                print(f"   运行状态: {'🟢 运行中' if status['is_running'] else '🔴 已停止'}")
                print(f"   当前用户: {status['current_user']}")
                print(f"   定时器状态: {'🟢 活跃' if status['timer_active'] else '🔴 非活跃'}")
                
                # 停止服务
                print(f"\n4️⃣ 停止验证服务:")
                refresh_timer_service.stop_monitoring()
                print(f"   ✅ 服务已停止")
                
            else:
                print(f"   ❌ 刷新验证服务启动失败")
        else:
            print(f"   ❌ 登录失败: {message}")
            print(f"   💡 请确保手机号已注册且机器码正确")
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {e}")
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户中断测试")
        try:
            refresh_timer_service.stop_monitoring()
        except:
            pass
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n=== 测试完成 ===")

if __name__ == "__main__":
    test_real_user_refresh()
