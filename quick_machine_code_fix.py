#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速机器码修复方案
临时解决方案：在客户端直接使用真实机器码，同时保持与服务器的兼容性
"""

from services.auth_service import AuthService
import requests
import json

def get_real_machine_code():
    """获取真实机器码"""
    auth_service = AuthService()
    return auth_service.get_machine_code()

def test_login_compatibility():
    """测试登录兼容性"""
    print("=" * 60)
    print("🔧 机器码兼容性测试")
    print("=" * 60)
    
    # 获取真实机器码
    real_machine_code = get_real_machine_code()
    print(f"✅ 真实机器码: {real_machine_code}")
    
    # 测试使用真实机器码登录
    print("\n🧪 测试使用真实机器码登录...")
    login_data = {
        "phone": "15155712316",
        "machineCode": real_machine_code,
        "timestamp": int(__import__('time').time())
    }
    
    try:
        response = requests.post(
            "http://43.142.19.28:5000/login",
            json=login_data,
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 使用真实机器码登录成功！")
                print("🎉 无需修改服务器，客户端已可正常使用")
                return True
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                print("📋 需要更新服务器中的机器码")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 网络错误: {e}")
    
    return False

def create_compatibility_solution():
    """创建兼容性解决方案"""
    print("\n🔧 创建兼容性解决方案...")
    
    real_machine_code = get_real_machine_code()
    
    # 方案1：联系服务器管理员
    print("\n📋 解决方案:")
    print("1. 联系服务器管理员，请求将以下信息更新到用户数据库:")
    print(f"   用户手机号: 15155712316")
    print(f"   新机器码: {real_machine_code}")
    print(f"   原机器码: 7DA491096E7B6854")
    
    # 方案2：如果有数据库访问权限
    print("\n2. 如果您有数据库访问权限，请执行以下SQL:")
    print(f"   UPDATE users SET machineCode = '{real_machine_code}' WHERE phone = '15155712316';")
    
    # 方案3：如果有服务器文件访问权限
    print("\n3. 如果用户数据存储在JSON文件中，请找到该文件并修改:")
    print(f"   将 \"machineCode\": \"7DA491096E7B6854\" 改为 \"machineCode\": \"{real_machine_code}\"")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print("🚀 启动机器码兼容性检查...")
    
    # 测试当前状态
    if test_login_compatibility():
        print("\n🎉 系统已正常工作，无需额外操作！")
    else:
        create_compatibility_solution()
        
        print("\n⚠️  在服务器更新完成之前，您可以:")
        print("1. 继续使用固定机器码 7DA491096E7B6854 (临时)")
        print("2. 等待服务器更新后使用真实机器码")
        print("3. 部署完整的API管理功能到服务器")

if __name__ == "__main__":
    main() 