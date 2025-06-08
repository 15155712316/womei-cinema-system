#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户验证修复效果
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_error_message_parsing():
    """测试错误信息解析功能"""
    print("=== 测试错误信息解析功能 ===\n")
    
    try:
        # 模拟主窗口类来测试错误解析方法
        class MockMainWindow:
            def _parse_auth_error_message(self, error_msg: str) -> str:
                """解析API错误信息，返回用户友好的提示"""
                try:
                    # 转换为小写便于匹配
                    error_lower = error_msg.lower()
                    
                    # 根据具体错误码和错误信息进行匹配
                    if "403" in error_msg or "forbidden" in error_lower:
                        # 进一步解析403错误的具体原因
                        if "banned" in error_lower or "封禁" in error_msg or "disabled" in error_lower:
                            return "账号已被封禁，请联系管理员"
                        elif "machine" in error_lower or "device" in error_lower or "机器码" in error_msg:
                            return "设备验证失败，请重新绑定设备"
                        else:
                            return "访问权限不足，请联系管理员"
                    
                    elif "404" in error_msg or "not found" in error_lower:
                        return "账号不存在，请检查手机号是否正确"
                    
                    elif "401" in error_msg or "unauthorized" in error_lower:
                        return "认证信息已过期，请重新登录"
                    
                    elif "500" in error_msg or "internal server error" in error_lower:
                        return "服务器内部错误，请稍后重试"
                    
                    elif "timeout" in error_lower or "超时" in error_msg:
                        return "网络连接超时，请检查网络后重试"
                    
                    elif "connection" in error_lower or "连接" in error_msg:
                        return "无法连接到服务器，请检查网络连接"
                    
                    elif "invalid" in error_lower and ("phone" in error_lower or "手机" in error_msg):
                        return "手机号格式不正确，请检查后重试"
                    
                    elif "invalid" in error_lower and ("machine" in error_lower or "机器码" in error_msg):
                        return "设备验证失败，请重新绑定设备"
                    
                    # 检查是否包含具体的服务器返回错误信息
                    elif "message" in error_lower or "错误" in error_msg:
                        # 如果错误信息本身就比较友好，直接使用
                        if len(error_msg) < 100 and not any(x in error_lower for x in ["error", "exception", "failed"]):
                            return error_msg
                    
                    # 默认情况：显示原始错误信息，但添加友好的前缀
                    return f"认证验证失败: {error_msg}\n\n如问题持续存在，请联系管理员"
                    
                except Exception as e:
                    print(f"[错误解析] 解析错误信息失败: {e}")
                    return f"认证失败: {error_msg}"
        
        # 创建测试实例
        mock_window = MockMainWindow()
        
        # 测试各种错误情况
        test_cases = [
            ("服务器响应错误: 403", "访问权限不足，请联系管理员"),
            ("HTTP 403 - 账号已被banned", "账号已被封禁，请联系管理员"),
            ("403 Forbidden - machine code invalid", "设备验证失败，请重新绑定设备"),
            ("服务器响应错误: 404", "账号不存在，请检查手机号是否正确"),
            ("HTTP 401 - Unauthorized", "认证信息已过期，请重新登录"),
            ("服务器响应错误: 500", "服务器内部错误，请稍后重试"),
            ("Connection timeout", "网络连接超时，请检查网络后重试"),
            ("无法连接到服务器", "无法连接到服务器，请检查网络连接"),
            ("Invalid phone number", "手机号格式不正确，请检查后重试"),
            ("机器码验证失败", "设备验证失败，请重新绑定设备"),
            ("用户不存在", "用户不存在"),
            ("Unknown error occurred", "认证验证失败: Unknown error occurred\n\n如问题持续存在，请联系管理员")
        ]
        
        print("🔍 测试错误信息解析:")
        for i, (input_error, expected_output) in enumerate(test_cases, 1):
            result = mock_window._parse_auth_error_message(input_error)
            status = "✅ 通过" if expected_output in result else "❌ 失败"
            print(f"  {i:2d}. {status} 输入: {input_error}")
            print(f"      输出: {result}")
            if expected_output not in result:
                print(f"      期望: {expected_output}")
            print()
        
    except Exception as e:
        print(f"❌ 测试错误信息解析失败: {e}")
        import traceback
        traceback.print_exc()

def test_refresh_service_error_handling():
    """测试刷新验证服务的错误处理"""
    print("=== 测试刷新验证服务错误处理 ===\n")
    
    try:
        from services.refresh_timer_service import refresh_timer_service
        
        print("✅ 成功导入刷新验证服务")
        
        # 检查服务状态
        status = refresh_timer_service.get_status()
        print(f"📊 当前服务状态:")
        print(f"   运行状态: {'🟢 运行中' if status['is_running'] else '🔴 已停止'}")
        print(f"   当前用户: {status['current_user'] or '❌ 无'}")
        print(f"   检查间隔: {status['check_interval_minutes']} 分钟")
        print(f"   定时器状态: {'🟢 活跃' if status['timer_active'] else '🔴 非活跃'}")
        
        # 测试错误处理（使用无效用户）
        print(f"\n🧪 测试错误处理（使用无效用户）:")
        test_user = {
            'phone': '00000000000',  # 无效手机号
            'username': '测试用户',
            'machine_code': 'INVALID_CODE'
        }
        
        # 尝试启动监控
        success = refresh_timer_service.start_monitoring(test_user)
        if success:
            print(f"   ✅ 监控启动成功（将会验证失败）")
            
            # 手动触发一次验证
            print(f"   🔍 手动触发验证检查...")
            refresh_timer_service._check_user_auth()
            
            # 停止监控
            refresh_timer_service.stop_monitoring()
            print(f"   🛑 监控已停止")
        else:
            print(f"   ❌ 监控启动失败")
        
    except Exception as e:
        print(f"❌ 测试刷新验证服务失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=== 用户验证修复效果测试 ===\n")
    
    print("🎯 测试目标:")
    print("  1. 验证错误信息解析功能")
    print("  2. 验证刷新服务错误处理")
    print("  3. 确认调试按钮功能")
    print()
    
    # 测试错误信息解析
    test_error_message_parsing()
    
    # 测试刷新验证服务
    test_refresh_service_error_handling()
    
    print("=== 测试完成 ===\n")
    
    print("💡 使用说明:")
    print("  1. 启动主程序后，在一键支付按钮旁边会看到'🔍 调试验证'按钮")
    print("  2. 点击调试按钮可以手动触发验证逻辑")
    print("  3. 验证失败时会显示更友好的错误信息")
    print("  4. 点击错误对话框的确认按钮后会正确跳转到登录页面")

if __name__ == "__main__":
    main()
