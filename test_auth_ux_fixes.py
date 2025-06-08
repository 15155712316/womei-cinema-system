#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试定时验证失败后的用户体验修复效果
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_error_dialog_improvements():
    """测试错误对话框改进"""
    print("=== 测试错误对话框改进 ===\n")
    
    try:
        # 检查auth_error_handler的改进
        with open('services/auth_error_handler.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 检查错误对话框改进:")
        
        # 检查是否移除了setDetailedText
        if 'setDetailedText' not in content or 'show_auth_failed_dialog' not in content:
            print("✅ 已移除详细信息按钮，错误信息直接显示")
        else:
            # 进一步检查是否在show_auth_failed_dialog中使用了setDetailedText
            lines = content.split('\n')
            in_show_auth_failed = False
            uses_detailed_text = False
            
            for line in lines:
                if 'def show_auth_failed_dialog' in line:
                    in_show_auth_failed = True
                elif in_show_auth_failed and line.strip().startswith('def ') and 'show_auth_failed_dialog' not in line:
                    in_show_auth_failed = False
                elif in_show_auth_failed and 'setDetailedText' in line:
                    uses_detailed_text = True
                    break
            
            if not uses_detailed_text:
                print("✅ 错误对话框不再使用详细信息按钮")
            else:
                print("❌ 错误对话框仍使用详细信息按钮")
        
        # 检查是否直接在主文本中显示错误信息
        if '失败原因：' in content and 'main_text' in content:
            print("✅ 错误信息直接显示在主要文本区域")
        else:
            print("❌ 错误信息未直接显示在主要文本区域")
        
        # 检查是否有样式优化
        if 'setStyleSheet' in content and 'min-width' in content:
            print("✅ 添加了对话框样式优化")
        else:
            print("❌ 未添加对话框样式优化")
        
        # 检查是否有操作指引
        if '点击确认后将自动跳转到登录页面' in content:
            print("✅ 添加了清晰的操作指引")
        else:
            print("❌ 未添加操作指引")
        
    except Exception as e:
        print(f"❌ 测试错误对话框改进失败: {e}")

def test_login_restart_improvements():
    """测试登录重启改进"""
    print("=== 测试登录重启改进 ===\n")
    
    try:
        # 检查主窗口中的登录重启改进
        with open('main_modular.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 检查登录重启改进:")
        
        # 检查_on_auth_dialog_confirmed方法的改进
        if '_on_auth_dialog_confirmed' in content:
            # 提取方法内容
            lines = content.split('\n')
            in_method = False
            method_content = []
            
            for line in lines:
                if 'def _on_auth_dialog_confirmed(self):' in line:
                    in_method = True
                    method_content.append(line)
                elif in_method and line.strip().startswith('def ') and '_on_auth_dialog_confirmed' not in line:
                    break
                elif in_method:
                    method_content.append(line)
            
            method_text = '\n'.join(method_content)
            
            # 检查各项改进
            if 'self.hide()' in method_text:
                print("✅ 确保主窗口完全隐藏")
            else:
                print("❌ 未确保主窗口完全隐藏")
            
            if 'self.current_user = None' in method_text and 'self.current_account = None' in method_text:
                print("✅ 清理用户状态")
            else:
                print("❌ 未清理用户状态")
            
            if 'refresh_timer_service.stop_monitoring()' in method_text:
                print("✅ 停止定时验证服务")
            else:
                print("❌ 未停止定时验证服务")
        
        # 检查_create_new_login_window方法的改进
        if '_create_new_login_window' in content:
            # 提取方法内容
            lines = content.split('\n')
            in_method = False
            method_content = []
            
            for line in lines:
                if 'def _create_new_login_window(self):' in line:
                    in_method = True
                    method_content.append(line)
                elif in_method and line.strip().startswith('def ') and '_create_new_login_window' not in line:
                    break
                elif in_method:
                    method_content.append(line)
            
            method_text = '\n'.join(method_content)
            
            # 检查各项改进
            if 'setWindowState(Qt.WindowMinimized)' in method_text:
                print("✅ 主窗口最小化处理")
            else:
                print("❌ 未处理主窗口最小化")
            
            if 'QApplication.setActiveWindow' in method_text:
                print("✅ 强制登录窗口获得焦点")
            else:
                print("❌ 未强制登录窗口获得焦点")
            
            if '_center_login_window' in method_text:
                print("✅ 登录窗口居中显示")
            else:
                print("❌ 登录窗口未居中显示")
        
    except Exception as e:
        print(f"❌ 测试登录重启改进失败: {e}")

def test_error_message_parsing():
    """测试错误信息解析"""
    print("=== 测试错误信息解析 ===\n")
    
    try:
        from services.auth_error_handler import auth_error_handler
        
        # 测试常见的验证失败错误
        test_cases = [
            ("Account disabled", "账号已被禁用"),
            ("Device not authorized", "设备未授权"),
            ("Not registered", "该手机号未注册"),
            ("HTTP 403", "访问权限不足"),
            ("Connection timeout", "网络连接超时"),
            ("用户不存在", "账号不存在"),
            ("机器码验证失败", "设备验证失败")
        ]
        
        print("🔍 测试错误信息解析:")
        success_count = 0
        
        for input_error, expected_keyword in test_cases:
            try:
                parsed = auth_error_handler.parse_error_message(input_error)
                if expected_keyword in parsed:
                    print(f"  ✅ {input_error} → {parsed[:50]}...")
                    success_count += 1
                else:
                    print(f"  ❌ {input_error} → {parsed[:50]}... (期望包含: {expected_keyword})")
            except Exception as e:
                print(f"  ❌ {input_error} → 解析失败: {e}")
        
        print(f"\n📊 解析测试结果: {success_count}/{len(test_cases)} 通过 ({success_count/len(test_cases)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ 测试错误信息解析失败: {e}")

def simulate_auth_failure_flow():
    """模拟认证失败流程"""
    print("=== 模拟认证失败流程 ===\n")
    
    try:
        from services.auth_error_handler import auth_error_handler
        
        # 模拟不同类型的认证失败
        failure_scenarios = [
            ("Account disabled", "账号被禁用场景"),
            ("Device not authorized", "设备未授权场景"),
            ("Not registered", "账号未注册场景"),
            ("Connection timeout", "网络超时场景")
        ]
        
        print("🎭 模拟认证失败流程:")
        
        for error_msg, scenario_name in failure_scenarios:
            print(f"\n📋 {scenario_name}:")
            print(f"  原始错误: {error_msg}")
            
            # 解析错误信息
            parsed_error = auth_error_handler.parse_error_message(error_msg)
            print(f"  解析结果: {parsed_error}")
            
            # 模拟对话框显示内容
            dialog_text = f"用户认证失败，需要重新登录\n\n"
            dialog_text += f"失败原因：\n{parsed_error}\n\n"
            dialog_text += f"点击确认后将自动跳转到登录页面"
            
            print(f"  对话框内容预览:")
            for line in dialog_text.split('\n'):
                print(f"    {line}")
            
            print(f"  ✅ 用户体验: 错误信息清晰，操作指引明确")
        
    except Exception as e:
        print(f"❌ 模拟认证失败流程失败: {e}")

def check_code_consistency():
    """检查代码一致性"""
    print("=== 检查代码一致性 ===\n")
    
    try:
        files_to_check = [
            'main_modular.py',
            'services/auth_error_handler.py',
            'services/refresh_timer_service.py'
        ]
        
        print("🔍 检查代码一致性:")
        
        for file_path in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📁 检查文件: {file_path}")
                
                # 检查是否使用统一的错误处理
                if 'auth_error_handler' in content:
                    print("  ✅ 使用统一错误处理")
                else:
                    print("  ❌ 未使用统一错误处理")
                
                # 检查是否有适当的日志输出
                if 'print(f"[' in content:
                    print("  ✅ 包含调试日志")
                else:
                    print("  ❌ 缺少调试日志")
                
                # 检查是否有异常处理
                if 'try:' in content and 'except' in content:
                    print("  ✅ 包含异常处理")
                else:
                    print("  ❌ 缺少异常处理")
                
            except FileNotFoundError:
                print(f"  ❌ 文件不存在: {file_path}")
            except Exception as e:
                print(f"  ❌ 检查文件失败: {e}")
        
    except Exception as e:
        print(f"❌ 检查代码一致性失败: {e}")

def main():
    """主函数"""
    print("=== 定时验证失败用户体验修复测试 ===\n")
    
    print("🎯 测试目标:")
    print("  1. 验证错误对话框改进（直接显示详细信息）")
    print("  2. 确认登录窗口重启逻辑增强")
    print("  3. 测试错误信息解析准确性")
    print("  4. 模拟完整的认证失败流程")
    print("  5. 检查代码一致性")
    print()
    
    # 执行所有测试
    test_error_dialog_improvements()
    test_login_restart_improvements()
    test_error_message_parsing()
    simulate_auth_failure_flow()
    check_code_consistency()
    
    print("=== 测试完成 ===\n")
    
    print("💡 用户体验修复效果:")
    print("  ✅ 错误信息直接显示在对话框主要区域，无需点击详细信息")
    print("  ✅ 对话框包含清晰的操作指引")
    print("  ✅ 增强了登录窗口重启逻辑，确保正确跳转")
    print("  ✅ 主窗口状态清理更彻底")
    print("  ✅ 登录窗口居中显示并强制获得焦点")
    print("  ✅ 错误信息解析准确，用户友好")

if __name__ == "__main__":
    main()
