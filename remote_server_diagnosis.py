#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程服务器诊断工具
用于诊断服务器版本不匹配问题
"""

import requests
import json
from datetime import datetime

def check_server_status():
    """检查服务器状态"""
    print("🔍 检查服务器状态...")
    
    try:
        response = requests.get("http://43.142.19.28:5000/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ 服务器响应正常")
            print(f"  当前版本: {data.get('version', 'N/A')}")
            print(f"  服务状态: {data.get('status', 'N/A')}")
            print(f"  功能描述: {data.get('features', 'N/A')}")
            print(f"  可用端点: {data.get('endpoints', [])}")
            
            # 检查是否有新端点
            endpoints = data.get('endpoints', [])
            if '/force_restart' in endpoints:
                print("✅ 包含 /force_restart 端点")
            else:
                print("❌ 缺少 /force_restart 端点")
                
            if '/update_refresh_time' in endpoints:
                print("✅ 包含 /update_refresh_time 端点")
            else:
                print("❌ 缺少 /update_refresh_time 端点")
                
            return data.get('version')
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 连接服务器失败: {e}")
        return None

def check_admin_page():
    """检查管理页面"""
    print("\n🔍 检查管理页面...")
    
    try:
        response = requests.get("http://43.142.19.28:5000/admin", timeout=10)
        if response.status_code == 200:
            content = response.text
            print("✅ 管理页面可访问")
            
            # 检查版本信息
            if "版本 1.5" in content:
                print("✅ 页面显示版本 1.5")
            elif "版本 1.4" in content:
                print("⚠️ 页面显示版本 1.4")
            elif "版本 1.2" in content:
                print("❌ 页面显示版本 1.2 (旧版本)")
            else:
                print("❓ 无法确定页面版本")
            
            # 检查新功能
            if "服务器管理" in content:
                print("✅ 包含服务器管理面板")
            else:
                print("❌ 缺少服务器管理面板")
                
            if "强制重启服务器" in content:
                print("✅ 包含强制重启按钮")
            else:
                print("❌ 缺少强制重启按钮")
                
            return True
        else:
            print(f"❌ 管理页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问管理页面失败: {e}")
        return False

def test_new_endpoints():
    """测试新端点"""
    print("\n🔍 测试新端点...")
    
    # 测试 force_restart
    try:
        response = requests.get("http://43.142.19.28:5000/force_restart", timeout=5)
        if response.status_code == 200:
            print("✅ /force_restart 端点可用")
        else:
            print(f"❌ /force_restart 端点返回: {response.status_code}")
    except Exception as e:
        print(f"❌ /force_restart 端点不可用: {e}")
    
    # 测试其他新端点
    new_endpoints = [
        "/update_refresh_time",
        "/update_machine_code", 
        "/update_user_points",
        "/toggle_user_status"
    ]
    
    for endpoint in new_endpoints:
        try:
            # 使用HEAD请求避免实际执行
            response = requests.head(f"http://43.142.19.28:5000{endpoint}", timeout=5)
            if response.status_code in [200, 405]:  # 405表示方法不允许但端点存在
                print(f"✅ {endpoint} 端点存在")
            else:
                print(f"❌ {endpoint} 端点不存在")
        except Exception as e:
            print(f"❌ {endpoint} 端点测试失败")

def generate_restart_commands():
    """生成重启命令"""
    print("\n🛠️ 服务器重启命令:")
    print("=" * 50)
    
    print("方法1: 直接SSH连接服务器")
    print("ssh your-username@43.142.19.28")
    print("ps aux | grep python")
    print("kill -9 [PID]")
    print("cd /path/to/your/project")
    print("python3 api.py")
    
    print("\n方法2: 如果使用PM2")
    print("pm2 list")
    print("pm2 restart api")
    print("pm2 logs api")
    
    print("\n方法3: 如果使用Supervisor")
    print("sudo supervisorctl status")
    print("sudo supervisorctl restart api")
    
    print("\n方法4: 如果使用systemd")
    print("sudo systemctl status your-api-service")
    print("sudo systemctl restart your-api-service")
    
    print("\n方法5: 如果使用Docker")
    print("docker ps")
    print("docker restart container-name")

def main():
    """主函数"""
    print("🚀 远程服务器诊断工具")
    print(f"⏰ 诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 目标服务器: http://43.142.19.28:5000")
    print("=" * 60)
    
    # 执行诊断
    current_version = check_server_status()
    check_admin_page()
    test_new_endpoints()
    
    # 分析结果
    print("\n📊 诊断结果:")
    print("=" * 50)
    
    if current_version == "1.5":
        print("✅ 服务器已运行最新版本 1.5")
        print("💡 如果浏览器仍显示旧版本，请清除浏览器缓存")
    elif current_version == "1.4":
        print("⚠️ 服务器运行版本 1.4，需要更新到 1.5")
        print("💡 请重启服务器进程")
    elif current_version == "1.2":
        print("❌ 服务器运行旧版本 1.2")
        print("💡 服务器进程需要重启以加载新代码")
    else:
        print("❓ 无法确定服务器版本")
    
    print("\n🎯 建议操作:")
    if current_version != "1.5":
        print("1. 通过SSH连接服务器")
        print("2. 停止当前Python进程")
        print("3. 确认api.py文件已更新")
        print("4. 清理Python缓存")
        print("5. 重新启动服务器")
        print("6. 验证版本更新")
    else:
        print("1. 清除浏览器缓存")
        print("2. 使用Ctrl+F5强制刷新")
        print("3. 尝试无痕模式访问")
    
    generate_restart_commands()
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成！")

if __name__ == "__main__":
    main()
