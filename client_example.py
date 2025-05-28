#!/usr/bin/env python3
"""
客户端SDK示例
演示如何与账号积分管理系统API进行交互
"""

import requests
import hashlib
import platform
import uuid
import json
from typing import Dict, Any, Optional

class UserAPIClient:
    """用户API客户端"""
    
    def __init__(self, base_url: str = "http://43.142.19.28:5000"):
        """
        初始化客户端
        
        Args:
            base_url: API服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'UserAPIClient/1.0'
        })
    
    def get_machine_code(self) -> str:
        """
        获取机器码 - 基于硬件信息生成唯一标识
        
        Returns:
            机器码字符串
        """
        try:
            # 获取系统信息
            system_info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'node': platform.node(),
            }
            
            # 尝试获取MAC地址
            try:
                mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                              for elements in range(0, 2*6, 2)][::-1])
                system_info['mac'] = mac
            except:
                pass
            
            # 生成机器码
            info_str = json.dumps(system_info, sort_keys=True)
            machine_code = hashlib.md5(info_str.encode()).hexdigest()
            
            return machine_code[:16].upper()  # 取前16位并转为大写
            
        except Exception as e:
            # 如果获取失败，生成一个随机的机器码
            return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16].upper()
    
    def login(self, phone: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            phone: 手机号
            
        Returns:
            API响应结果
        """
        machine_code = self.get_machine_code()
        
        data = {
            "phone": phone,
            "machineCode": machine_code
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json=data,
                timeout=10
            )
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "data": response.json() if response.content else {},
                "machine_code": machine_code
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"网络请求失败: {str(e)}",
                "machine_code": machine_code
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"响应解析失败: {str(e)}",
                "machine_code": machine_code
            }
    
    def check_connection(self) -> bool:
        """
        检查服务器连接
        
        Returns:
            是否连接成功
        """
        try:
            # 使用健康检查接口测试连接
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except:
            # 如果健康检查失败，尝试根路径
            try:
                response = self.session.get(f"{self.base_url}/", timeout=5)
                return response.status_code == 200
            except:
                return False
    
    def get_user_info(self, phone: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息（通过登录接口）
        
        Args:
            phone: 手机号
            
        Returns:
            用户信息或None
        """
        result = self.login(phone)
        if result.get("success") and result.get("data", {}).get("success"):
            return result["data"]["data"]
        return None

class ClientDemo:
    """客户端演示程序"""
    
    def __init__(self):
        self.client = UserAPIClient()
        print("=== 账号积分管理系统 - 客户端演示 ===")
        print(f"服务器地址: {self.client.base_url}")
        print(f"本机机器码: {self.client.get_machine_code()}")
        print("=" * 50)
    
    def test_connection(self):
        """测试连接"""
        print("🔗 测试服务器连接...")
        if self.client.check_connection():
            print("✅ 服务器连接正常")
            return True
        else:
            print("❌ 服务器连接失败")
            return False
    
    def demo_login(self):
        """演示登录功能"""
        print("\n📱 登录功能演示:")
        
        # 测试用户（需要在管理后台添加）
        test_phones = ["15155712316", "13800138000", "13900139000"]
        
        for phone in test_phones:
            print(f"\n尝试登录用户: {phone}")
            result = self.client.login(phone)
            
            if result["success"]:
                data = result["data"]
                if data.get("success"):
                    user_info = data["data"]
                    print(f"✅ 登录成功!")
                    print(f"   手机号: {user_info.get('phone')}")
                    print(f"   积分: {user_info.get('points', 0)}")
                    print(f"   状态: {'启用' if user_info.get('status') == 1 else '禁用'}")
                    print(f"   机器码: {user_info.get('machineCode', '未绑定')}")
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
            else:
                print(f"❌ 请求失败: {result.get('error', '未知错误')}")
    
    def interactive_login(self):
        """交互式登录"""
        print("\n🔐 交互式登录:")
        
        while True:
            phone = input("请输入手机号 (输入q退出): ").strip()
            if phone.lower() == 'q':
                break
            
            if len(phone) != 11 or not phone.isdigit():
                print("❌ 手机号格式错误，请输入11位数字")
                continue
            
            print(f"正在验证用户: {phone}")
            result = self.client.login(phone)
            
            if result["success"]:
                data = result["data"]
                if data.get("success"):
                    user_info = data["data"]
                    print(f"✅ 登录成功!")
                    print(f"   用户积分: {user_info.get('points', 0)}")
                    print(f"   账号状态: {'正常' if user_info.get('status') == 1 else '已禁用'}")
                    print(f"   设备绑定: {'已绑定' if user_info.get('machineCode') else '未绑定'}")
                    
                    # 可以在这里添加更多业务逻辑
                    # 比如检查积分、记录登录日志等
                    
                else:
                    print(f"❌ 登录失败: {data.get('message')}")
                    
                    # 根据不同错误提供不同提示
                    message = data.get('message', '')
                    if 'Not registered' in message:
                        print("💡 提示: 该手机号未注册，请联系管理员添加账号")
                    elif 'Device not authorized' in message:
                        print("💡 提示: 设备未授权，请在授权设备上登录")
                    elif 'Account disabled' in message:
                        print("💡 提示: 账号已被禁用，请联系管理员")
            else:
                print(f"❌ 连接失败: {result.get('error', '未知错误')}")
    
    def show_machine_info(self):
        """显示机器信息"""
        print(f"\n🖥️  机器信息:")
        print(f"   系统平台: {platform.platform()}")
        print(f"   处理器: {platform.processor()}")
        print(f"   机器类型: {platform.machine()}")
        print(f"   主机名: {platform.node()}")
        print(f"   机器码: {self.client.get_machine_code()}")
        print(f"   💡 机器码说明: 基于硬件信息生成，用于设备绑定")
    
    def run(self):
        """运行演示程序"""
        # 测试连接
        if not self.test_connection():
            print("⚠️  无法连接到服务器，请检查:")
            print("   1. 服务器是否正常运行")
            print("   2. 网络连接是否正常")
            print("   3. 防火墙设置是否正确")
            return
        
        while True:
            print("\n" + "=" * 30)
            print("📋 功能菜单:")
            print("1. 演示登录功能")
            print("2. 交互式登录")
            print("3. 查看机器信息")
            print("4. 测试服务器连接")
            print("0. 退出")
            print("=" * 30)
            
            choice = input("请选择功能 (0-4): ").strip()
            
            if choice == "1":
                self.demo_login()
            elif choice == "2":
                self.interactive_login()
            elif choice == "3":
                self.show_machine_info()
            elif choice == "4":
                self.test_connection()
            elif choice == "0":
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请重新输入")

def main():
    """主程序"""
    try:
        demo = ClientDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 