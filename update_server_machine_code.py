#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新API服务器中的机器码工具
"""

import requests
import json
from services.auth_service import AuthService

def get_current_machine_code():
    """获取当前机器的真实机器码"""
    try:
        auth_service = AuthService()
        machine_code = auth_service.get_machine_code()
        return machine_code
    except Exception as e:
        print(f"获取机器码失败: {e}")
        return None

def test_login_with_machine_code(machine_code, phone="15155712316"):
    """测试使用指定机器码登录"""
    print(f"\n🔐 测试登录 - 手机号: {phone}, 机器码: {machine_code}")
    
    login_data = {
        "phone": phone,
        "machineCode": machine_code,
        "timestamp": int(__import__('time').time())
    }
    
    try:
        response = requests.post(
            "http://43.142.19.28:5000/login", 
            json=login_data, 
            timeout=10,
            verify=False
        )
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("success"):
                print("✅ 登录成功！机器码已匹配")
                return True
            else:
                print(f"❌ 登录失败: {result.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 登录测试失败: {e}")
    
    return False

def update_machine_code_on_server(new_machine_code, phone="15155712316"):
    """尝试更新API服务器中的机器码"""
    print(f"\n🔧 尝试更新服务器机器码...")
    print(f"手机号: {phone}")
    print(f"新机器码: {new_machine_code}")
    
    update_data = {
        "phone": phone,
        "machineCode": new_machine_code,
        "timestamp": int(__import__('time').time())
    }
    
    try:
        response = requests.post(
            "http://43.142.19.28:5000/update_machine_code",
            json=update_data,
            timeout=10,
            verify=False
        )
        
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            if result.get("success"):
                print("✅ 机器码更新成功！")
                return True
            else:
                print(f"❌ 更新失败: {result.get('message')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 更新请求失败: {e}")
    
    return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 乐影系统 - 机器码更新助手")
    print("=" * 60)
    
    # 1. 获取当前机器的真实机器码
    print("\n📱 获取当前机器码...")
    current_machine_code = get_current_machine_code()
    
    if not current_machine_code:
        print("❌ 无法获取当前机器码，程序退出")
        return
    
    print(f"✅ 当前机器码: {current_machine_code}")
    
    # 2. 测试当前机器码是否已经可以登录
    print("\n🧪 测试当前机器码登录状态...")
    if test_login_with_machine_code(current_machine_code):
        print("\n🎉 当前机器码已经可以正常登录，无需更新！")
        return
    
    # 3. 尝试自动更新服务器中的机器码
    print("\n🔄 需要更新服务器中的机器码...")
    if update_machine_code_on_server(current_machine_code):
        print("\n✅ 机器码更新成功！")
        
        # 4. 验证更新后是否可以登录
        print("\n🧪 验证更新后的登录状态...")
        if test_login_with_machine_code(current_machine_code):
            print("\n🎉 机器码更新完成，现在可以正常登录了！")
        else:
            print("\n⚠️  更新后仍无法登录，请检查API服务器状态")
    else:
        print("\n❌ 自动更新失败")
        print("\n📋 手动更新步骤:")
        print("1. 访问管理后台: http://43.142.19.28:5000/admin")
        print("2. 找到用户: 15155712316")
        print(f"3. 将机器码更新为: {current_machine_code}")
        print("4. 保存更改")
        print("5. 重新启动客户端程序测试")
    
    print("\n" + "=" * 60)
    print("更新助手运行完成！")
    print("=" * 60)

if __name__ == "__main__":
    main() 