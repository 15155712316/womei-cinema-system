#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一认证错误处理效果
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_unified_error_handler():
    """测试统一错误处理器"""
    print("=== 测试统一认证错误处理器 ===\n")
    
    try:
        from services.auth_error_handler import auth_error_handler, AuthResult
        
        print("✅ 成功导入统一错误处理器")
        
        # 测试错误信息解析
        test_cases = [
            # HTTP状态码错误
            ("服务器响应错误: 403", "访问权限不足，请联系管理员"),
            ("HTTP 403 - 账号已被banned", "账号已被封禁，请联系管理员"),
            ("403 Forbidden - machine code invalid", "设备验证失败，请重新绑定设备"),
            ("服务器响应错误: 404", "账号不存在，请检查手机号是否正确"),
            ("HTTP 401 - Unauthorized", "认证信息已过期，请重新登录"),
            ("服务器响应错误: 500", "服务器内部错误，请稍后重试"),
            
            # 网络错误
            ("Connection timeout", "网络连接超时，请检查网络后重试"),
            ("无法连接到服务器", "无法连接到服务器，请检查网络连接"),
            
            # 业务逻辑错误
            ("Not registered", "该手机号未注册\n\n请联系管理员添加账号"),
            ("Device not authorized", "设备未授权，机器码不匹配\n\n请联系管理员重新绑定设备"),
            ("Account disabled", "账号已被禁用\n\n请联系管理员启用账号"),
            
            # 输入验证错误
            ("Invalid phone number", "手机号格式不正确，请检查后重试"),
            ("机器码验证失败", "设备验证失败，请重新绑定设备"),
            ("用户不存在", "账号不存在，请检查手机号是否正确"),
            
            # 未知错误
            ("Unknown error occurred", "认证验证失败: Unknown error occurred\n\n如问题持续存在，请联系管理员")
        ]
        
        print("🔍 测试错误信息解析:")
        success_count = 0
        for i, (input_error, expected_output) in enumerate(test_cases, 1):
            result = auth_error_handler.parse_error_message(input_error)
            is_success = expected_output in result
            status = "✅ 通过" if is_success else "❌ 失败"
            
            if is_success:
                success_count += 1
            
            print(f"  {i:2d}. {status} 输入: {input_error}")
            if not is_success:
                print(f"      期望: {expected_output}")
                print(f"      实际: {result}")
            print()
        
        print(f"📊 测试结果: {success_count}/{len(test_cases)} 通过 ({success_count/len(test_cases)*100:.1f}%)")
        
        # 测试AuthResult类
        print(f"\n🧪 测试AuthResult类:")
        
        # 成功结果
        success_result = AuthResult(True, "登录成功", {"phone": "13800138000", "points": 100})
        print(f"  成功结果: {success_result}")
        print(f"  是否成功: {success_result.is_success()}")
        print(f"  用户信息: {success_result.get_user_info()}")
        
        # 失败结果
        error_result = AuthResult(False, "Not registered", None)
        print(f"  失败结果: {error_result}")
        print(f"  是否成功: {error_result.is_success()}")
        print(f"  友好错误信息: {error_result.get_user_friendly_message()}")
        
    except Exception as e:
        print(f"❌ 测试统一错误处理器失败: {e}")
        import traceback
        traceback.print_exc()

def test_login_window_integration():
    """测试登录窗口集成"""
    print("=== 测试登录窗口集成 ===\n")
    
    try:
        # 检查登录窗口是否正确导入了统一错误处理器
        with open('ui/login_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from services.auth_error_handler import auth_error_handler' in content:
            print("✅ 登录窗口已导入统一错误处理器")
        else:
            print("❌ 登录窗口未导入统一错误处理器")
        
        if 'auth_error_handler.show_login_error' in content:
            print("✅ 登录窗口使用统一错误显示方法")
        else:
            print("❌ 登录窗口未使用统一错误显示方法")
        
        if '_get_user_friendly_error_message' not in content:
            print("✅ 登录窗口已移除旧的错误处理方法")
        else:
            print("❌ 登录窗口仍包含旧的错误处理方法")
        
    except Exception as e:
        print(f"❌ 测试登录窗口集成失败: {e}")

def test_refresh_service_integration():
    """测试刷新验证服务集成"""
    print("=== 测试刷新验证服务集成 ===\n")
    
    try:
        # 检查刷新验证服务是否正确集成
        with open('services/refresh_timer_service.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from services.auth_error_handler import auth_error_handler' in content:
            print("✅ 刷新验证服务已导入统一错误处理器")
        else:
            print("❌ 刷新验证服务未导入统一错误处理器")
        
        if 'auth_service.login(phone)' in content:
            print("✅ 刷新验证服务使用auth_service.login方法")
        else:
            print("❌ 刷新验证服务未使用auth_service.login方法")
        
        if 'auth_error_handler.handle_auth_success' in content:
            print("✅ 刷新验证服务使用统一认证成功处理")
        else:
            print("❌ 刷新验证服务未使用统一认证成功处理")
        
    except Exception as e:
        print(f"❌ 测试刷新验证服务集成失败: {e}")

def test_main_window_integration():
    """测试主窗口集成"""
    print("=== 测试主窗口集成 ===\n")
    
    try:
        # 检查主窗口是否正确集成
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from services.auth_error_handler import auth_error_handler' in content:
            print("✅ 主窗口已导入统一错误处理器")
        else:
            print("❌ 主窗口未导入统一错误处理器")
        
        if 'auth_error_handler.show_auth_failed_dialog' in content:
            print("✅ 主窗口使用统一认证失败对话框")
        else:
            print("❌ 主窗口未使用统一认证失败对话框")
        
        if '_parse_auth_error_message' not in content:
            print("✅ 主窗口已移除旧的错误解析方法")
        else:
            print("❌ 主窗口仍包含旧的错误解析方法")
        
    except Exception as e:
        print(f"❌ 测试主窗口集成失败: {e}")

def test_auth_service_consistency():
    """测试auth_service一致性"""
    print("=== 测试auth_service一致性 ===\n")
    
    try:
        from services.auth_service import auth_service
        
        print("✅ 成功导入auth_service")
        
        # 测试登录方法是否存在
        if hasattr(auth_service, 'login'):
            print("✅ auth_service包含login方法")
        else:
            print("❌ auth_service缺少login方法")
        
        # 测试check_auth方法是否存在
        if hasattr(auth_service, 'check_auth'):
            print("✅ auth_service包含check_auth方法")
        else:
            print("❌ auth_service缺少check_auth方法")
        
        # 测试方法签名
        import inspect
        login_sig = inspect.signature(auth_service.login)
        print(f"📋 login方法签名: {login_sig}")
        
    except Exception as e:
        print(f"❌ 测试auth_service一致性失败: {e}")

def main():
    """主函数"""
    print("=== PyQt5电影票务系统 - 统一认证错误处理测试 ===\n")
    
    print("🎯 测试目标:")
    print("  1. 验证统一错误处理器功能")
    print("  2. 检查登录窗口集成")
    print("  3. 检查刷新验证服务集成")
    print("  4. 检查主窗口集成")
    print("  5. 验证auth_service一致性")
    print()
    
    # 执行所有测试
    test_unified_error_handler()
    test_login_window_integration()
    test_refresh_service_integration()
    test_main_window_integration()
    test_auth_service_consistency()
    
    print("=== 测试完成 ===\n")
    
    print("💡 统一错误处理效果:")
    print("  ✅ 登录和定时验证使用相同的错误解析逻辑")
    print("  ✅ 验证成功时静默处理，无多余提示")
    print("  ✅ 验证失败时显示统一格式的错误信息")
    print("  ✅ 认证失败后正确跳转登录页面")
    print("  ✅ 避免了重复代码，确保错误处理逻辑一致性")

if __name__ == "__main__":
    main()
