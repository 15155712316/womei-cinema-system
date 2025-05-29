#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统 - API功能升级验证脚本
用于验证所有新增的API端点是否正常工作
"""

import requests
import json
import sys
from datetime import datetime

class APIValidator:
    def __init__(self, base_url="http://43.142.19.28:5000"):
        self.base_url = base_url
        self.test_phone = "15155712316"
        self.real_machine_code = "9DC6B72833DBFDA6"
        self.old_machine_code = "7DA491096E7B6854"
        
        self.results = {}
        self.passed = 0
        self.total = 0
    
    def print_header(self, title):
        print("=" * 60)
        print(f"🔍 {title}")
        print("=" * 60)
    
    def print_test(self, test_name, description):
        print(f"\n📋 测试: {test_name}")
        print(f"📝 描述: {description}")
        print("-" * 40)
    
    def test_api_endpoint(self, test_name, method, endpoint, data=None, expected_status=200):
        """通用API测试方法"""
        self.total += 1
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            print(f"🌐 请求: {method} {url}")
            if data:
                print(f"📤 数据: {json.dumps(data, ensure_ascii=False)}")
            print(f"📊 状态码: {response.status_code}")
            
            if response.status_code == expected_status:
                try:
                    result = response.json()
                    print(f"✅ 响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                    self.results[test_name] = {"status": "PASS", "response": result}
                    self.passed += 1
                    return True, result
                except:
                    print(f"✅ 响应: {response.text}")
                    self.results[test_name] = {"status": "PASS", "response": response.text}
                    self.passed += 1
                    return True, response.text
            else:
                print(f"❌ 状态码错误，期望: {expected_status}, 实际: {response.status_code}")
                print(f"❌ 响应: {response.text}")
                self.results[test_name] = {"status": "FAIL", "error": f"Status: {response.status_code}"}
                return False, response.text
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
            self.results[test_name] = {"status": "FAIL", "error": str(e)}
            return False, str(e)
    
    def test_basic_endpoints(self):
        """测试基础端点"""
        self.print_header("基础API端点测试")
        
        # 测试根路径
        self.print_test("服务状态", "检查API服务是否正常运行")
        self.test_api_endpoint("service_status", "GET", "/")
        
        # 测试健康检查
        self.print_test("健康检查", "检查数据库连接状态")
        self.test_api_endpoint("health_check", "GET", "/health")
        
        # 测试管理后台
        self.print_test("管理后台", "检查管理界面是否可访问")
        success, _ = self.test_api_endpoint("admin_page", "GET", "/admin")
        if success:
            print(f"🎯 管理后台链接: {self.base_url}/admin")
    
    def test_new_endpoints(self):
        """测试新增的API端点"""
        self.print_header("新增API端点测试")
        
        # 测试更新机器码
        self.print_test("更新机器码", f"将用户 {self.test_phone} 的机器码更新为真实机器码")
        success, result = self.test_api_endpoint(
            "update_machine_code",
            "POST",
            "/update_machine_code",
            {
                "phone": self.test_phone,
                "machineCode": self.real_machine_code
            }
        )
        
        if success and isinstance(result, dict) and result.get("success"):
            print("✅ 机器码更新成功！")
        
        # 测试更新积分
        self.print_test("更新用户积分", f"更新用户 {self.test_phone} 的积分")
        self.test_api_endpoint(
            "update_user_points",
            "POST",
            "/update_user_points",
            {
                "phone": self.test_phone,
                "points": 1500
            }
        )
        
        # 测试切换状态
        self.print_test("切换用户状态", f"切换用户 {self.test_phone} 的状态")
        self.test_api_endpoint(
            "toggle_user_status",
            "POST",
            "/toggle_user_status",
            {
                "phone": self.test_phone
            }
        )
    
    def test_login_flow(self):
        """测试登录流程"""
        self.print_header("登录流程测试")
        
        # 使用真实机器码登录
        self.print_test("真实机器码登录", f"使用机器码 {self.real_machine_code} 登录")
        success, result = self.test_api_endpoint(
            "login_real_machine_code",
            "POST",
            "/login",
            {
                "phone": self.test_phone,
                "machineCode": self.real_machine_code
            }
        )
        
        if success and isinstance(result, dict) and result.get("success"):
            print("🎉 登录成功！用户可以正常使用系统")
        elif isinstance(result, dict) and result.get("message") == "Device not authorized":
            print("⚠️  机器码未匹配，请确认已通过管理后台更新机器码")
    
    def test_old_endpoints(self):
        """测试原有端点兼容性"""
        self.print_header("原有API端点兼容性测试")
        
        # 测试设置积分
        self.print_test("设置积分", "测试原有的积分设置功能")
        self.test_api_endpoint(
            "set_points",
            "POST",
            "/set_points",
            {
                "phone": self.test_phone,
                "points": 888
            }
        )
        
        # 测试设置状态
        self.print_test("设置状态", "测试原有的状态设置功能")
        self.test_api_endpoint(
            "set_status",
            "POST",
            "/set_status",
            {
                "phone": self.test_phone,
                "status": 1
            }
        )
    
    def generate_report(self):
        """生成测试报告"""
        self.print_header("测试报告")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        
        print(f"📊 总测试数: {self.total}")
        print(f"✅ 通过数量: {self.passed}")
        print(f"❌ 失败数量: {self.total - self.passed}")
        print(f"📈 成功率: {success_rate:.1f}%")
        print()
        
        print("📋 详细结果:")
        print("-" * 50)
        for test_name, result in self.results.items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {test_name.ljust(25)} - {result['status']}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 90:
            print("🎉 所有功能基本正常！API升级成功！")
        elif success_rate >= 70:
            print("⚠️  大部分功能正常，建议检查失败的测试项")
        else:
            print("❌ 存在较多问题，建议检查部署和配置")
        
        # 保存报告到文件
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": self.total,
            "passed_tests": self.passed,
            "success_rate": success_rate,
            "results": self.results
        }
        
        with open("api_validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告已保存到: api_validation_report.json")

def main():
    print("🚀 开始验证乐影系统API升级")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    validator = APIValidator()
    
    try:
        # 执行各项测试
        validator.test_basic_endpoints()
        validator.test_new_endpoints()
        validator.test_login_flow()
        validator.test_old_endpoints()
        
        # 生成报告
        validator.generate_report()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        validator.generate_report()
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        validator.generate_report()

if __name__ == "__main__":
    main() 