#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统 - 服务器状态检查工具
用于诊断服务器缓存和更新问题
版本: 1.0
"""

import requests
import json
import os
import sys
from datetime import datetime
import subprocess

def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def check_server_status():
    """检查服务器状态"""
    print_header("服务器状态检查")
    
    try:
        response = requests.get("http://localhost:5000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务器运行正常")
            print(f"  服务名称: {data.get('service', 'N/A')}")
            print(f"  版本: {data.get('version', 'N/A')}")
            print(f"  状态: {data.get('status', 'N/A')}")
            print(f"  功能: {data.get('features', 'N/A')}")
            if 'server_restart_time' in data:
                print(f"  重启时间: {data['server_restart_time']}")
            if 'last_updated' in data:
                print(f"  最后更新: {data['last_updated']}")
            return True
        else:
            print(f"❌ 服务器响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器 (localhost:5000)")
        return False
    except Exception as e:
        print(f"❌ 检查服务器状态失败: {e}")
        return False

def check_file_status():
    """检查文件状态"""
    print_header("文件状态检查")
    
    if os.path.exists("api.py"):
        stat = os.stat("api.py")
        print("✅ api.py文件存在")
        print(f"  文件大小: {stat.st_size} 字节")
        print(f"  最后修改: {datetime.fromtimestamp(stat.st_mtime)}")
        
        # 检查文件版本
        try:
            with open("api.py", "r", encoding="utf-8") as f:
                content = f.read()
                if "版本: 1.5" in content:
                    print("✅ 文件版本: 1.5 (最新)")
                elif "版本: 1.4" in content:
                    print("⚠️ 文件版本: 1.4 (旧版本)")
                else:
                    print("❓ 无法确定文件版本")
                    
                if "强制缓存清理" in content:
                    print("✅ 包含缓存清理功能")
                else:
                    print("❌ 缺少缓存清理功能")
        except Exception as e:
            print(f"⚠️ 读取文件内容失败: {e}")
    else:
        print("❌ api.py文件不存在")

def check_python_processes():
    """检查Python进程"""
    print_header("Python进程检查")
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(["tasklist", "/fi", "imagename eq python.exe"], 
                                  capture_output=True, text=True)
            if "python.exe" in result.stdout:
                print("✅ 发现Python进程:")
                lines = result.stdout.split('\n')
                for line in lines:
                    if "python.exe" in line:
                        print(f"  {line.strip()}")
            else:
                print("❌ 没有发现Python进程")
        else:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            python_processes = [line for line in result.stdout.split('\n') if 'python' in line and 'api.py' in line]
            if python_processes:
                print("✅ 发现Python进程:")
                for process in python_processes:
                    print(f"  {process.strip()}")
            else:
                print("❌ 没有发现运行api.py的Python进程")
    except Exception as e:
        print(f"⚠️ 检查进程失败: {e}")

def check_port_usage():
    """检查端口占用"""
    print_header("端口占用检查")
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
            port_lines = [line for line in result.stdout.split('\n') if ':5000' in line]
            if port_lines:
                print("✅ 端口5000被占用:")
                for line in port_lines:
                    print(f"  {line.strip()}")
            else:
                print("❌ 端口5000未被占用")
        else:
            result = subprocess.run(["netstat", "-tlnp"], capture_output=True, text=True)
            port_lines = [line for line in result.stdout.split('\n') if ':5000' in line]
            if port_lines:
                print("✅ 端口5000被占用:")
                for line in port_lines:
                    print(f"  {line.strip()}")
            else:
                print("❌ 端口5000未被占用")
    except Exception as e:
        print(f"⚠️ 检查端口失败: {e}")

def check_cache_files():
    """检查缓存文件"""
    print_header("缓存文件检查")
    
    cache_dirs = []
    pyc_files = []
    
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_dirs.append(os.path.join(root, "__pycache__"))
        for file in files:
            if file.endswith(".pyc"):
                pyc_files.append(os.path.join(root, file))
    
    if cache_dirs:
        print(f"⚠️ 发现 {len(cache_dirs)} 个缓存目录:")
        for cache_dir in cache_dirs:
            print(f"  {cache_dir}")
    else:
        print("✅ 没有发现__pycache__目录")
    
    if pyc_files:
        print(f"⚠️ 发现 {len(pyc_files)} 个.pyc文件:")
        for pyc_file in pyc_files:
            print(f"  {pyc_file}")
    else:
        print("✅ 没有发现.pyc文件")

def test_force_restart():
    """测试强制重启功能"""
    print_header("强制重启功能测试")
    
    try:
        print("🔄 发送强制重启请求...")
        response = requests.post("http://localhost:5000/force_restart", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 强制重启请求成功")
            print(f"  消息: {data.get('message', 'N/A')}")
            print(f"  重启时间: {data.get('restart_time', 'N/A')}")
            print("⏳ 等待服务器重启...")
            import time
            time.sleep(5)
            return True
        else:
            print(f"❌ 强制重启请求失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 强制重启测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 乐影系统服务器诊断工具 v1.0")
    print(f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行各项检查
    server_running = check_server_status()
    check_file_status()
    check_python_processes()
    check_port_usage()
    check_cache_files()
    
    # 提供解决方案
    print_header("诊断结果和建议")
    
    if not server_running:
        print("❌ 服务器未运行，建议:")
        print("  1. 运行 restart_server.bat 重启服务器")
        print("  2. 手动运行: python api.py")
        print("  3. 检查Python环境和依赖")
    else:
        print("✅ 服务器运行正常")
        
        # 询问是否测试强制重启
        try:
            test_restart = input("\n是否测试强制重启功能？(y/n): ").lower()
            if test_restart == 'y':
                if test_force_restart():
                    print("✅ 强制重启功能正常")
                    # 重新检查服务器状态
                    import time
                    time.sleep(3)
                    check_server_status()
                else:
                    print("❌ 强制重启功能异常")
        except KeyboardInterrupt:
            print("\n\n👋 检查已取消")
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成！")
    print("📊 管理后台: http://localhost:5000/admin")
    print("🔄 强制重启: http://localhost:5000/force_restart")
    print("=" * 60)

if __name__ == "__main__":
    main()
