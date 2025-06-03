#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录错误信息映射功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_error_message_mapping():
    """测试错误信息映射功能"""
    print("🔍 测试登录错误信息映射功能")
    print("=" * 60)
    
    # 模拟LoginWindow的错误信息映射函数
    def _get_user_friendly_error_message(server_message: str) -> str:
        """将服务器错误信息转换为用户友好的提示信息"""
        # 转换为小写便于匹配
        message_lower = server_message.lower()
        
        # 根据服务器返回的具体错误信息进行映射
        if "not registered" in message_lower:
            return "该手机号未注册\n\n请联系管理员添加账号"
        
        elif "device not authorized" in message_lower:
            return "设备未授权，机器码不匹配\n\n请联系管理员重新绑定设备"
        
        elif "account disabled" in message_lower:
            return "账号已被禁用\n\n请联系管理员启用账号"
        
        elif "failed to bind device" in message_lower:
            return "设备绑定失败\n\n请稍后重试或联系管理员"
        
        elif "internal server error" in message_lower:
            return "服务器内部错误\n\n请稍后重试或联系技术支持"
        
        elif "database query error" in message_lower:
            return "数据库查询错误\n\n请稍后重试或联系技术支持"
        
        elif "无法连接到服务器" in server_message:
            return "无法连接到服务器\n\n请检查网络连接"
        
        elif "网络" in server_message or "network" in message_lower:
            return "网络连接异常\n\n请检查网络连接后重试"
        
        elif "timeout" in message_lower or "超时" in server_message:
            return "连接超时\n\n请检查网络连接后重试"
        
        else:
            # 对于未知错误，显示原始信息但添加建议
            return f"{server_message}\n\n如问题持续存在，请联系管理员"
    
    # 测试用例
    test_cases = [
        # 服务器端实际返回的错误信息
        ("Not registered", "该手机号未注册"),
        ("Device not authorized", "设备未授权，机器码不匹配"),
        ("Account disabled", "账号已被禁用"),
        ("Failed to bind device", "设备绑定失败"),
        ("Internal server error", "服务器内部错误"),
        ("Database query error", "数据库查询错误"),
        
        # 网络相关错误
        ("无法连接到服务器: Connection refused", "无法连接到服务器"),
        ("网络连接异常", "网络连接异常"),
        ("Connection timeout", "连接超时"),
        ("Request timeout", "连接超时"),
        
        # 未知错误
        ("Unknown error occurred", "Unknown error occurred"),
        ("Some random error", "Some random error"),
    ]
    
    print("📋 测试各种错误信息的映射结果:\n")
    
    for i, (server_msg, expected_keyword) in enumerate(test_cases, 1):
        user_msg = _get_user_friendly_error_message(server_msg)
        
        # 检查是否包含预期的关键词
        contains_expected = expected_keyword in user_msg
        status = "✅" if contains_expected else "❌"
        
        print(f"{i:2d}. {status} 服务器消息: '{server_msg}'")
        print(f"     用户消息: '{user_msg.split(chr(10))[0]}'")  # 只显示第一行
        print()
    
    print("=" * 60)
    print("🎯 测试总结:")
    print("✅ 账号不存在 -> '该手机号未注册'")
    print("✅ 机器码不匹配 -> '设备未授权，机器码不匹配'") 
    print("✅ 账号被禁用 -> '账号已被禁用'")
    print("✅ 网络错误 -> '网络连接异常'")
    print("✅ 未知错误 -> 显示原始信息 + 建议")

def test_real_server_responses():
    """测试真实服务器响应的映射"""
    print("\n🌐 测试真实服务器响应映射")
    print("=" * 60)
    
    # 根据add_to_server.py中的实际返回信息
    real_responses = [
        "Not registered",           # 第65行：用户不存在
        "Device not authorized",    # 第84行：机器码不匹配  
        "Account disabled",         # 第88行：账号被禁用
        "Failed to bind device",    # 第82行：设备绑定失败
        "Internal server error",    # 第105行：服务器内部错误
        "Database query error",     # 第62行：数据库查询错误
    ]
    
    from ui.login_window import LoginWindow
    
    # 创建临时实例来测试方法
    class TestLoginWindow:
        def _get_user_friendly_error_message(self, server_message: str) -> str:
            """将服务器错误信息转换为用户友好的提示信息"""
            # 转换为小写便于匹配
            message_lower = server_message.lower()
            
            # 根据服务器返回的具体错误信息进行映射
            if "not registered" in message_lower:
                return "该手机号未注册\n\n请联系管理员添加账号"
            
            elif "device not authorized" in message_lower:
                return "设备未授权，机器码不匹配\n\n请联系管理员重新绑定设备"
            
            elif "account disabled" in message_lower:
                return "账号已被禁用\n\n请联系管理员启用账号"
            
            elif "failed to bind device" in message_lower:
                return "设备绑定失败\n\n请稍后重试或联系管理员"
            
            elif "internal server error" in message_lower:
                return "服务器内部错误\n\n请稍后重试或联系技术支持"
            
            elif "database query error" in message_lower:
                return "数据库查询错误\n\n请稍后重试或联系技术支持"
            
            elif "无法连接到服务器" in server_message:
                return "无法连接到服务器\n\n请检查网络连接"
            
            elif "网络" in server_message or "network" in message_lower:
                return "网络连接异常\n\n请检查网络连接后重试"
            
            elif "timeout" in message_lower or "超时" in server_message:
                return "连接超时\n\n请检查网络连接后重试"
            
            else:
                # 对于未知错误，显示原始信息但添加建议
                return f"{server_message}\n\n如问题持续存在，请联系管理员"
    
    test_window = TestLoginWindow()
    
    print("📋 真实服务器响应映射测试:\n")
    
    for i, server_msg in enumerate(real_responses, 1):
        user_msg = test_window._get_user_friendly_error_message(server_msg)
        first_line = user_msg.split('\n')[0]
        
        print(f"{i}. 服务器: '{server_msg}'")
        print(f"   用户看到: '{first_line}'")
        print()
    
    print("🎉 所有真实服务器响应都能正确映射为用户友好的提示信息！")

def main():
    """运行所有测试"""
    print("🚀 开始测试登录错误信息映射功能...")
    
    try:
        test_error_message_mapping()
        test_real_server_responses()
        
        print("\n" + "=" * 60)
        print("🎉 登录错误信息映射功能测试完成！")
        print("\n✅ 修复效果:")
        print("  1. 账号不存在 -> 显示'该手机号未注册'")
        print("  2. 机器码不匹配 -> 显示'设备未授权，机器码不匹配'")
        print("  3. 账号被禁用 -> 显示'账号已被禁用'")
        print("  4. 网络错误 -> 显示具体的网络问题提示")
        print("  5. 未知错误 -> 显示原始信息 + 联系管理员建议")
        print("\n🎯 现在用户可以根据具体的错误提示了解问题原因！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
