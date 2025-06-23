#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的账号管理组件
验证基于Token验证的账号管理功能
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_account_widget():
    """测试改进后的账号管理组件"""
    try:
        print("🧪 测试改进后的账号管理组件")
        print("=" * 60)
        
        # 导入账号组件
        from ui.widgets.account_widget import AccountWidget
        
        app = QApplication(sys.argv)
        
        # 创建测试窗口
        window = QMainWindow()
        window.setWindowTitle("沃美电影票务系统 - 改进账号管理测试")
        window.setGeometry(200, 200, 400, 700)
        
        # 创建中央部件
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建账号组件
        account_widget = AccountWidget()
        layout.addWidget(account_widget)
        
        # 连接信号进行测试
        def on_account_selected(account_data):
            print(f"[测试] 📋 账号选择信号: {account_data}")
        
        def on_account_login_requested(login_data):
            print(f"[测试] 📋 登录请求信号: {login_data}")
        
        def on_accounts_refreshed(accounts_list):
            print(f"[测试] 📋 账号刷新信号: {len(accounts_list)} 个账号")
        
        account_widget.account_selected.connect(on_account_selected)
        account_widget.account_login_requested.connect(on_account_login_requested)
        account_widget.accounts_refreshed.connect(on_accounts_refreshed)
        
        # 显示窗口
        window.show()
        
        print(f"✅ 测试窗口已显示")
        print(f"📋 改进功能测试:")
        print(f"  1. 手机号输入：只允许数字，最大11位")
        print(f"  2. Token输入：支持长字符串，密码模式")
        print(f"  3. 显示/隐藏Token切换")
        print(f"  4. 实时输入验证和状态提示")
        print(f"  5. Token有效性验证（调用get_cinemas API）")
        print(f"  6. 账号保存和自动选择")
        print(f"  7. 详细的错误处理和用户反馈")
        print(f"=" * 60)
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_input_validation():
    """测试输入验证逻辑"""
    print("\n🧪 测试输入验证逻辑")
    print("=" * 60)
    
    # 模拟验证逻辑
    def validate_input(phone: str, token: str) -> dict:
        """验证输入数据"""
        try:
            # 验证手机号
            if not phone:
                return {"valid": False, "message": "❌ 手机号不能为空，请输入11位手机号"}
            
            if len(phone) != 11 or not phone.isdigit():
                return {"valid": False, "message": "❌ 手机号格式错误，请输入11位数字"}
            
            # 验证Token
            if not token:
                return {"valid": False, "message": "❌ Token不能为空，请输入有效Token"}
            
            if len(token.strip()) < 10:
                return {"valid": False, "message": "❌ Token太短，请输入完整的Token"}
            
            return {"valid": True, "message": "输入验证通过"}
            
        except Exception as e:
            return {"valid": False, "message": f"❌ 输入验证异常: {str(e)}"}
    
    # 测试用例
    test_cases = [
        {"phone": "", "token": "", "expected": False, "desc": "空输入"},
        {"phone": "1234567890", "token": "abc123", "expected": False, "desc": "手机号10位"},
        {"phone": "123456789012", "token": "abc123", "expected": False, "desc": "手机号12位"},
        {"phone": "1234567890a", "token": "abc123", "expected": False, "desc": "手机号包含字母"},
        {"phone": "15155712316", "token": "abc", "expected": False, "desc": "Token太短"},
        {"phone": "15155712316", "token": "dc028617920fcca58086940d7b6b76c3", "expected": True, "desc": "有效输入"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = validate_input(case["phone"], case["token"])
        status = "✅" if result["valid"] == case["expected"] else "❌"
        print(f"  {i}. {status} {case['desc']}")
        print(f"     手机号: '{case['phone']}', Token: '{case['token'][:20]}...'")
        print(f"     结果: {result['message']}")
        print()
    
    print(f"✅ 输入验证逻辑测试完成")

def test_token_verification_simulation():
    """测试Token验证模拟"""
    print("\n🧪 测试Token验证模拟")
    print("=" * 60)
    
    # 模拟Token验证结果
    test_tokens = [
        {
            "token": "invalid_token_123",
            "expected_result": {
                "success": False,
                "error": "Token已失效: 获取TOKEN超时 [5105A]",
                "error_type": "token_expired",
                "cinemas": []
            },
            "desc": "无效Token"
        },
        {
            "token": "dc028617920fcca58086940d7b6b76c3",
            "expected_result": {
                "success": True,
                "cinemas": [{"cinema_id": "400028", "cinema_name": "测试影院"}],
                "total": 1
            },
            "desc": "有效Token"
        }
    ]
    
    for i, case in enumerate(test_tokens, 1):
        print(f"  {i}. 测试 {case['desc']}")
        print(f"     Token: {case['token'][:20]}...")
        
        result = case['expected_result']
        if result.get('success'):
            print(f"     ✅ 验证成功: 获取到 {result.get('total', 0)} 个影院")
        else:
            print(f"     ❌ 验证失败: {result.get('error')}")
            print(f"     错误类型: {result.get('error_type')}")
        print()
    
    print(f"✅ Token验证模拟测试完成")

def test_account_save_simulation():
    """测试账号保存模拟"""
    print("\n🧪 测试账号保存模拟")
    print("=" * 60)
    
    # 模拟账号保存逻辑
    def save_account_simulation(phone: str, token: str, existing_accounts: list) -> dict:
        """模拟账号保存"""
        try:
            # 查找是否已存在该手机号的账号
            existing_account = None
            for account in existing_accounts:
                if account.get('phone') == phone:
                    existing_account = account
                    break
            
            is_new_account = existing_account is None
            
            if existing_account:
                # 更新现有账号的Token
                existing_account['token'] = token
                print(f"     🔄 更新现有账号Token: {phone}")
            else:
                # 添加新账号
                new_account = {"phone": phone, "token": token}
                existing_accounts.append(new_account)
                print(f"     ➕ 添加新账号: {phone}")
            
            return {
                "success": True,
                "is_new": is_new_account,
                "total_accounts": len(existing_accounts)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "is_new": False}
    
    # 测试场景
    existing_accounts = [
        {"phone": "13800138000", "token": "old_token_123"}
    ]
    
    test_cases = [
        {"phone": "15155712316", "token": "new_token_456", "desc": "添加新账号"},
        {"phone": "13800138000", "token": "updated_token_789", "desc": "更新现有账号"},
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['desc']}")
        print(f"     手机号: {case['phone']}")
        print(f"     保存前账号数: {len(existing_accounts)}")
        
        result = save_account_simulation(case['phone'], case['token'], existing_accounts)
        
        if result['success']:
            action = "新增" if result['is_new'] else "更新"
            print(f"     ✅ 保存成功: {action}账号")
            print(f"     保存后账号数: {result['total_accounts']}")
        else:
            print(f"     ❌ 保存失败: {result['error']}")
        print()
    
    print(f"✅ 账号保存模拟测试完成")
    print(f"📋 最终账号列表:")
    for account in existing_accounts:
        print(f"  - {account['phone']}: {account['token'][:20]}...")

def main():
    print("🎬 沃美电影票务系统 - 改进账号管理组件测试")
    print("=" * 60)
    print("📋 测试内容：")
    print("  1. 输入验证逻辑测试")
    print("  2. Token验证模拟测试")
    print("  3. 账号保存模拟测试")
    print("  4. 账号组件界面测试")
    print("=" * 60)
    
    # 运行各项测试
    test_input_validation()
    test_token_verification_simulation()
    test_account_save_simulation()
    
    print(f"\n🚀 开始界面测试...")
    test_account_widget()

if __name__ == "__main__":
    main()
