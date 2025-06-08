#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器部署诊断脚本
检查管理后台部署问题
"""

import requests
import socket
import subprocess
import sys
import os
from pathlib import Path

def check_server_status(host="43.142.19.28", port=5000):
    """检查服务器状态"""
    print(f"🔍 检查服务器状态: {host}:{port}")
    
    try:
        # 检查端口是否开放
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ 端口 {port} 已开放")
            return True
        else:
            print(f"❌ 端口 {port} 未开放或服务未启动")
            return False
    except Exception as e:
        print(f"❌ 连接检查失败: {e}")
        return False

def check_api_endpoints(base_url="http://43.142.19.28:5000"):
    """检查API端点"""
    print(f"\n🔍 检查API端点: {base_url}")
    
    endpoints = [
        "/",
        "/health",
        "/admin",
        "/admin/v2",
        "/api/v2/login"
    ]
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: 连接失败")
        except requests.exceptions.Timeout:
            print(f"❌ {endpoint}: 超时")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")

def generate_deployment_checklist():
    """生成部署检查清单"""
    print("\n📋 部署检查清单:")
    print("=" * 50)
    
    checklist = [
        "1. 服务器端口5000是否开放？",
        "2. Flask应用是否正在运行？",
        "3. 防火墙是否允许5000端口？",
        "4. api1.py文件是否包含完整的路由？",
        "5. 是否安装了所有依赖包？",
        "6. 是否正确启动了Flask应用？",
        "7. 数据库连接是否正常？",
        "8. 日志文件中是否有错误信息？"
    ]
    
    for item in checklist:
        print(f"□ {item}")

def main():
    """主函数"""
    print("🚀 管理后台部署诊断工具")
    print("=" * 50)
    
    # 检查服务器连接
    server_ok = check_server_status()
    
    # 检查API端点
    if server_ok:
        check_api_endpoints()
    
    # 生成检查清单
    generate_deployment_checklist()
    
    print("\n💡 常见解决方案:")
    print("1. 检查Flask应用是否启动: ps aux | grep python")
    print("2. 检查端口占用: netstat -tlnp | grep 5000")
    print("3. 检查防火墙: ufw status")
    print("4. 查看应用日志: tail -f /var/log/your-app.log")

if __name__ == "__main__":
    main()
