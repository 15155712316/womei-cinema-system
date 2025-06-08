#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查刷新验证服务状态
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_refresh_service():
    """检查刷新验证服务"""
    print("=== 刷新验证服务状态检查 ===\n")
    
    try:
        # 导入刷新验证服务
        from services.refresh_timer_service import refresh_timer_service
        print("✅ 成功导入刷新验证服务")
        
        # 检查服务状态
        status = refresh_timer_service.get_status()
        print(f"\n📊 当前服务状态:")
        print(f"   运行状态: {'🟢 运行中' if status['is_running'] else '🔴 已停止'}")
        print(f"   当前用户: {status['current_user'] or '❌ 无'}")
        print(f"   检查间隔: {status['check_interval_minutes']} 分钟")
        print(f"   定时器状态: {'🟢 活跃' if status['timer_active'] else '🔴 非活跃'}")
        
        # 检查配置
        print(f"\n⚙️ 服务配置:")
        print(f"   API地址: {refresh_timer_service.api_base_url}")
        print(f"   超时时间: {refresh_timer_service.request_timeout} 秒")
        print(f"   检查间隔: {refresh_timer_service.check_interval} 毫秒")
        
        # 测试API连接
        print(f"\n🌐 测试API连接:")
        test_api_connection(refresh_timer_service.api_base_url)
        
        # 如果服务正在运行，显示详细信息
        if status['is_running']:
            print(f"\n🔍 服务运行详情:")
            print(f"   监控用户: {status['current_user']}")
            print(f"   下次检查: 约 {status['check_interval_minutes']} 分钟后")
        else:
            print(f"\n💡 服务未运行 - 这是正常的，只有在用户登录后才会启动")
        
    except ImportError as e:
        print(f"❌ 导入刷新验证服务失败: {e}")
    except Exception as e:
        print(f"❌ 检查服务状态失败: {e}")
        import traceback
        traceback.print_exc()

def test_api_connection(api_url):
    """测试API连接"""
    try:
        import requests
        
        # 测试基本连接
        test_url = f"{api_url}/health"  # 假设有健康检查端点
        
        print(f"   正在测试连接到: {api_url}")
        
        try:
            response = requests.get(test_url, timeout=5)
            print(f"   ✅ 服务器响应: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"   ❌ 无法连接到服务器")
        except requests.exceptions.Timeout:
            print(f"   ⏰ 连接超时")
        except Exception as e:
            print(f"   ⚠️ 连接测试异常: {e}")
            
    except ImportError:
        print(f"   ⚠️ 无法导入requests模块，跳过连接测试")

def check_main_program_integration():
    """检查主程序集成"""
    print(f"\n🔗 检查主程序集成:")
    
    try:
        # 检查主程序是否正确导入了验证服务
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'refresh_timer_service' in content:
            print(f"   ✅ 主程序已导入刷新验证服务")
            
            if '_start_refresh_monitoring' in content:
                print(f"   ✅ 主程序包含启动监控方法")
            else:
                print(f"   ❌ 主程序缺少启动监控方法")
                
            if 'QTimer.singleShot(1000, lambda: self._start_refresh_monitoring' in content:
                print(f"   ✅ 主程序会在登录后启动验证服务")
            else:
                print(f"   ❌ 主程序未配置自动启动验证服务")
        else:
            print(f"   ❌ 主程序未导入刷新验证服务")
            
    except FileNotFoundError:
        print(f"   ⚠️ 找不到main_modular.py文件")
    except Exception as e:
        print(f"   ❌ 检查主程序集成失败: {e}")

if __name__ == "__main__":
    check_refresh_service()
    check_main_program_integration()
    
    print(f"\n=== 检查完成 ===")
    print(f"\n💡 如果您没有看到验证输出，可能的原因:")
    print(f"   1. 用户还没有成功登录")
    print(f"   2. API服务器无法访问")
    print(f"   3. 用户信息缺少phone字段")
    print(f"   4. 验证间隔太长（当前设置为10分钟）")
    print(f"\n🔧 建议:")
    print(f"   1. 确保完成登录流程")
    print(f"   2. 检查网络连接")
    print(f"   3. 查看控制台输出中的验证日志")
    print(f"   4. 可以临时将验证间隔改为1分钟进行测试")
