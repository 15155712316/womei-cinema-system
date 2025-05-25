#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证系统测试脚本
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service

def test_machine_code():
    """测试机器码生成"""
    print("=" * 50)
    print("测试1: 机器码生成")
    print("=" * 50)
    
    # 测试机器码生成
    machine_code1 = auth_service.get_machine_code()
    machine_code2 = auth_service.get_machine_code()
    
    print(f"第一次生成: {machine_code1}")
    print(f"第二次生成: {machine_code2}")
    print(f"长度: {len(machine_code1)}")
    print(f"是否一致: {machine_code1 == machine_code2}")
    
    # 验证机器码格式
    assert len(machine_code1) == 32, "机器码长度应为32位"
    assert machine_code1 == machine_code2, "同一台机器的机器码应该一致"
    assert machine_code1.isalnum(), "机器码应只包含字母和数字"
    
    print("✅ 机器码生成测试通过")
    return machine_code1

def test_phone_validation():
    """测试手机号验证"""
    print("=" * 50)
    print("测试2: 手机号格式验证")
    print("=" * 50)
    
    # 测试有效手机号
    valid_phones = ["13800138000", "13900139000", "15012345678", "18612345678"]
    invalid_phones = ["1234567890", "12345678901", "23800138000", "138001380001", "abc", ""]
    
    for phone in valid_phones:
        result = auth_service.validate_phone_number(phone)
        print(f"有效手机号 {phone}: {result}")
        assert result, f"手机号 {phone} 应该被认为有效"
    
    for phone in invalid_phones:
        result = auth_service.validate_phone_number(phone)
        print(f"无效手机号 {phone}: {result}")
        assert not result, f"手机号 {phone} 应该被认为无效"
    
    print("✅ 手机号验证测试通过")

def test_mock_login():
    """测试模拟登录"""
    print("=" * 50)
    print("测试3: 模拟登录系统")
    print("=" * 50)
    
    # 测试正确的手机号登录
    print("测试正确手机号登录...")
    success, message, user_info = auth_service.login("13800138000")
    print(f"登录结果: 成功={success}, 消息={message}")
    if user_info:
        print(f"用户信息: {user_info}")
    
    assert success, "正确手机号应该登录成功"
    assert user_info is not None, "成功登录应该返回用户信息"
    assert user_info.get("phone") == "13800138000", "返回的手机号应该正确"
    
    # 测试不存在的手机号
    print("\n测试不存在的手机号...")
    success, message, user_info = auth_service.login("12345678901")
    print(f"登录结果: 成功={success}, 消息={message}")
    
    assert not success, "不存在的手机号应该登录失败"
    assert user_info is None, "失败登录不应该返回用户信息"
    
    # 测试无效格式的手机号
    print("\n测试无效格式手机号...")
    success, message, user_info = auth_service.login("abc")
    print(f"登录结果: 成功={success}, 消息={message}")
    
    assert not success, "无效格式手机号应该登录失败"
    assert user_info is None, "失败登录不应该返回用户信息"
    
    print("✅ 模拟登录测试通过")

def test_auth_check():
    """测试权限验证"""
    print("=" * 50)
    print("测试4: 权限验证系统")
    print("=" * 50)
    
    # 先清除登录状态
    auth_service.logout()
    
    # 测试未登录状态
    print("测试未登录状态...")
    success, message, user_info = auth_service.check_auth()
    print(f"权限检查: 成功={success}, 消息={message}")
    
    assert not success, "未登录状态应该权限检查失败"
    
    # 先登录
    print("\n先进行登录...")
    login_success, login_message, login_user_info = auth_service.login("13800138000")
    assert login_success, "登录应该成功"
    
    # 测试已登录状态
    print("测试已登录状态...")
    success, message, user_info = auth_service.check_auth()
    print(f"权限检查: 成功={success}, 消息={message}")
    if user_info:
        print(f"用户信息: {user_info}")
    
    assert success, "已登录状态应该权限检查成功"
    assert user_info is not None, "权限检查成功应该返回用户信息"
    
    print("✅ 权限验证测试通过")

def test_points_system():
    """测试积分系统"""
    print("=" * 50)
    print("测试5: 积分管理系统")
    print("=" * 50)
    
    # 确保已登录
    login_success, _, _ = auth_service.login("13800138000")
    assert login_success, "登录应该成功"
    
    # 获取初始积分
    user_info = auth_service.get_user_info()
    initial_points = user_info.get("points", 0)
    print(f"初始积分: {initial_points}")
    
    # 测试正常积分扣除
    print("\n测试正常积分扣除...")
    success, message = auth_service.use_points("测试操作", 5)
    print(f"积分扣除: 成功={success}, 消息={message}")
    
    assert success, "充足积分情况下扣除应该成功"
    
    # 获取扣除后积分
    user_info = auth_service.get_user_info()
    remaining_points = user_info.get("points", 0)
    print(f"剩余积分: {remaining_points}")
    
    # 测试积分不足
    print("\n测试积分不足情况...")
    success, message = auth_service.use_points("大额操作", 1000)
    print(f"大额扣除: 成功={success}, 消息={message}")
    
    assert not success, "积分不足时扣除应该失败"
    assert "积分不足" in message, "应该提示积分不足"
    
    print("✅ 积分系统测试通过")

def test_login_window():
    """测试登录窗口界面"""
    print("=" * 50)
    print("测试6: 登录窗口界面")
    print("=" * 50)
    
    try:
        from PyQt5.QtWidgets import QApplication
        from ui.login_window import LoginWindow
        
        app = QApplication(sys.argv)
        
        # 创建登录窗口
        login_window = LoginWindow()
        
        def on_login_success(user_info):
            print(f"界面登录成功: {user_info}")
            app.quit()
        
        def on_login_failed():
            print("界面登录失败")
            app.quit()
        
        login_window.login_success.connect(on_login_success)
        
        # 显示窗口
        login_window.show()
        
        print("登录窗口已显示，请手动测试...")
        print("推荐测试账号:")
        print("- 13800138000 (管理员)")
        print("- 13900139000 (测试用户)")
        print("- 13700137000 (普通用户)")
        
        # 5秒后自动关闭（如果用户没有操作）
        def auto_close():
            print("自动关闭登录窗口")
            app.quit()
        
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(auto_close)
        timer.start(5000)  # 5秒
        
        app.exec_()
        print("✅ 登录窗口界面测试完成")
        
    except ImportError as e:
        print(f"⚠️  PyQt5未安装，跳过界面测试: {e}")
    except Exception as e:
        print(f"❌ 登录窗口测试失败: {e}")

def main():
    """主测试函数"""
    print("🚀 开始用户认证系统测试")
    print(f"Python版本: {sys.version}")
    print("")
    
    try:
        # 执行所有测试
        machine_code = test_machine_code()
        print("")
        
        test_phone_validation()
        print("")
        
        test_mock_login()
        print("")
        
        test_auth_check()
        print("")
        
        test_points_system()
        print("")
        
        test_login_window()
        print("")
        
        print("🎉 所有测试完成!")
        print("")
        print("=" * 50)
        print("系统状态总结")
        print("=" * 50)
        print(f"当前机器码: {machine_code}")
        
        # 显示预置账号
        print("\n预置测试账号:")
        test_accounts = [
            {"phone": "13800138000", "name": "管理员", "points": 100},
            {"phone": "13900139000", "name": "测试用户", "points": 50},
            {"phone": "13700137000", "name": "普通用户", "points": 30}
        ]
        
        for account in test_accounts:
            print(f"- {account['phone']} ({account['name']}) - {account['points']}积分")
        
        print("\n认证系统已就绪，可以启动主程序进行测试！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 