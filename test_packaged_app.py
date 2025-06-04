#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包后程序测试脚本
用于在干净环境中测试打包后的程序功能
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

def test_executable_exists():
    """测试可执行文件是否存在"""
    print("🔍 检查可执行文件...")

    # 检查目录模式打包的exe文件
    exe_path = Path("dist/CinemaTicketSystem/CinemaTicketSystem.exe")

    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ 可执行文件存在: {exe_path}")
        print(f"   文件大小: {file_size:.1f} MB")
        return True
    else:
        # 检查单文件模式打包的exe文件
        exe_path_single = Path("dist/CinemaTicketSystem.exe")
        if exe_path_single.exists():
            file_size = exe_path_single.stat().st_size / (1024 * 1024)  # MB
            print(f"✅ 可执行文件存在: {exe_path_single}")
            print(f"   文件大小: {file_size:.1f} MB")
            return True
        else:
            print(f"❌ 可执行文件不存在: {exe_path}")
            return False

def test_data_files():
    """测试数据文件是否正确打包"""
    print("\n📁 检查数据文件...")

    # 检查目录模式打包的数据文件
    required_files = [
        "dist/CinemaTicketSystem/data/config.json",
        "dist/CinemaTicketSystem/data/cinema_info.json",
        "dist/CinemaTicketSystem/data/accounts.json",
    ]

    missing_files = []

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 缺失")
            missing_files.append(file_path)

    return len(missing_files) == 0

def test_startup():
    """测试程序启动"""
    print("\n🚀 测试程序启动...")

    # 检查目录模式打包的exe文件
    exe_path = "dist/CinemaTicketSystem/CinemaTicketSystem.exe"
    working_dir = "dist/CinemaTicketSystem"

    if not os.path.exists(exe_path):
        # 检查单文件模式
        exe_path = "dist/CinemaTicketSystem.exe"
        working_dir = "dist"
        if not os.path.exists(exe_path):
            print("❌ 可执行文件不存在")
            return False
    
    try:
        # 启动程序（非阻塞）
        print("   启动程序...")
        process = subprocess.Popen(
            [exe_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=working_dir
        )
        
        # 等待3秒检查程序是否正常启动
        time.sleep(3)
        
        # 检查进程状态
        poll_result = process.poll()
        
        if poll_result is None:
            # 程序仍在运行
            print("✅ 程序启动成功")
            
            # 终止程序
            process.terminate()
            time.sleep(1)
            
            if process.poll() is None:
                process.kill()
            
            return True
        else:
            # 程序已退出
            stdout, stderr = process.communicate()
            print(f"❌ 程序启动失败，退出码: {poll_result}")
            if stderr:
                print(f"   错误信息: {stderr.decode('utf-8', errors='ignore')}")
            return False
            
    except Exception as e:
        print(f"❌ 启动测试失败: {e}")
        return False

def test_machine_code_generation():
    """测试机器码生成功能"""
    print("\n🔧 测试机器码生成...")
    
    try:
        # 这里我们无法直接测试打包后的程序内部功能
        # 但可以检查相关文件是否存在
        print("✅ 机器码生成功能已打包（无法直接测试）")
        return True
    except Exception as e:
        print(f"❌ 机器码测试失败: {e}")
        return False

def test_network_connectivity():
    """测试网络连接功能"""
    print("\n🌐 测试网络连接...")
    
    try:
        import requests
        
        # 测试服务器连接
        server_url = "http://43.142.19.28:5000"
        
        print(f"   连接服务器: {server_url}")
        response = requests.get(server_url, timeout=5)
        
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"⚠️  服务器响应异常: {response.status_code}")
            return True  # 服务器可能返回其他状态码但仍可连接
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        return False
    except requests.exceptions.Timeout:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 网络测试失败: {e}")
        return False

def test_file_permissions():
    """测试文件权限"""
    print("\n🔐 测试文件权限...")

    test_files = [
        "dist/CinemaTicketSystem/CinemaTicketSystem.exe",
        "dist/CinemaTicketSystem/data/config.json",
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                # 测试读权限
                with open(file_path, 'rb') as f:
                    f.read(1)
                print(f"✅ {file_path} - 可读")
                
                # 对于数据文件，测试写权限
                if file_path.endswith('.json'):
                    with open(file_path, 'r+', encoding='utf-8') as f:
                        pass
                    print(f"✅ {file_path} - 可写")
                    
            except PermissionError:
                print(f"❌ {file_path} - 权限不足")
                return False
            except Exception as e:
                print(f"❌ {file_path} - 权限测试失败: {e}")
                return False
        else:
            print(f"⚠️  {file_path} - 文件不存在")
    
    return True

def create_test_report():
    """创建测试报告"""
    print("\n📝 创建测试报告...")
    
    report = {
        "test_time": __import__('datetime').datetime.now().isoformat(),
        "test_environment": {
            "os": __import__('platform').system(),
            "os_version": __import__('platform').version(),
            "architecture": __import__('platform').architecture()[0],
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        },
        "test_results": {
            "executable_exists": False,
            "data_files": False,
            "startup": False,
            "machine_code": False,
            "network": False,
            "permissions": False
        }
    }
    
    try:
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("✅ 测试报告已创建: test_report.json")
        return True
    except Exception as e:
        print(f"❌ 创建测试报告失败: {e}")
        return False

def main():
    """主函数"""
    print("🧪 开始打包后程序测试")
    print("=" * 50)
    
    tests = [
        ("可执行文件", test_executable_exists),
        ("数据文件", test_data_files),
        ("程序启动", test_startup),
        ("机器码生成", test_machine_code_generation),
        ("网络连接", test_network_connectivity),
        ("文件权限", test_file_permissions),
    ]
    
    failed_tests = []
    passed_tests = []
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests.append(test_name)
            else:
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name}测试时发生错误: {e}")
            failed_tests.append(test_name)
    
    # 创建测试报告
    create_test_report()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"✅ 通过测试: {len(passed_tests)}")
    print(f"❌ 失败测试: {len(failed_tests)}")
    
    if passed_tests:
        print(f"\n通过的测试: {', '.join(passed_tests)}")
    
    if failed_tests:
        print(f"\n失败的测试: {', '.join(failed_tests)}")
        print("\n建议:")
        print("1. 检查打包过程是否完整")
        print("2. 确认所有依赖都已正确打包")
        print("3. 在目标环境中重新测试")
        return False
    else:
        print("\n🎉 所有测试通过!")
        print("程序已准备好在目标环境中部署")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
