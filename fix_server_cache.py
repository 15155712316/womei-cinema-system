#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
乐影系统 - 服务器缓存问题修复工具
专门解决代码更新后服务器没有变化的问题
版本: 1.0
"""

import os
import sys
import time
import shutil
import subprocess
import requests
import json
from datetime import datetime

def print_step(step, message):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"🔧 步骤 {step}: {message}")
    print('='*60)

def print_success(message):
    """打印成功信息"""
    print(f"✅ {message}")

def print_warning(message):
    """打印警告信息"""
    print(f"⚠️ {message}")

def print_error(message):
    """打印错误信息"""
    print(f"❌ {message}")

def kill_python_processes():
    """停止所有Python进程"""
    print_step(1, "停止Python进程")
    
    try:
        if sys.platform == "win32":
            # Windows系统
            subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                         capture_output=True, check=False)
            subprocess.run(["taskkill", "/f", "/im", "pythonw.exe"], 
                         capture_output=True, check=False)
            print_success("Python进程已停止")
        else:
            # Linux/Mac系统
            subprocess.run(["pkill", "-f", "python.*api.py"], 
                         capture_output=True, check=False)
            print_success("Python进程已停止")
        
        time.sleep(2)  # 等待进程完全停止
        
    except Exception as e:
        print_warning(f"停止进程时出现警告: {e}")

def clear_python_cache():
    """清理Python缓存"""
    print_step(2, "清理Python缓存")
    
    cache_cleared = 0
    
    # 清理 __pycache__ 目录
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_dir = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_dir)
                print_success(f"已删除缓存目录: {cache_dir}")
                cache_cleared += 1
            except Exception as e:
                print_warning(f"删除缓存目录失败 {cache_dir}: {e}")
    
    # 清理 .pyc 文件
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".pyc"):
                pyc_file = os.path.join(root, file)
                try:
                    os.remove(pyc_file)
                    print_success(f"已删除缓存文件: {pyc_file}")
                    cache_cleared += 1
                except Exception as e:
                    print_warning(f"删除缓存文件失败 {pyc_file}: {e}")
    
    if cache_cleared == 0:
        print_success("没有发现需要清理的缓存文件")
    else:
        print_success(f"共清理了 {cache_cleared} 个缓存文件/目录")

def check_port_usage():
    """检查端口占用"""
    print_step(3, "检查端口5000占用")
    
    try:
        if sys.platform == "win32":
            result = subprocess.run(["netstat", "-ano"], 
                                  capture_output=True, text=True)
            port_lines = [line for line in result.stdout.split('\n') if ':5000' in line]
            
            if port_lines:
                print_warning("端口5000被占用:")
                for line in port_lines:
                    print(f"  {line.strip()}")
                
                # 尝试释放端口
                for line in port_lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        if pid.isdigit():
                            try:
                                subprocess.run(["taskkill", "/f", "/pid", pid], 
                                             capture_output=True, check=False)
                                print_success(f"已停止进程 PID: {pid}")
                            except:
                                pass
            else:
                print_success("端口5000未被占用")
        else:
            result = subprocess.run(["netstat", "-tlnp"], 
                                  capture_output=True, text=True)
            port_lines = [line for line in result.stdout.split('\n') if ':5000' in line]
            
            if port_lines:
                print_warning("端口5000被占用:")
                for line in port_lines:
                    print(f"  {line.strip()}")
            else:
                print_success("端口5000未被占用")
                
    except Exception as e:
        print_warning(f"检查端口失败: {e}")

def verify_file_update():
    """验证文件更新"""
    print_step(4, "验证api.py文件更新")
    
    if not os.path.exists("api.py"):
        print_error("api.py文件不存在！")
        return False
    
    # 检查文件信息
    stat = os.stat("api.py")
    print_success(f"文件大小: {stat.st_size} 字节")
    print_success(f"最后修改: {datetime.fromtimestamp(stat.st_mtime)}")
    
    # 检查文件内容
    try:
        with open("api.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        if "版本: 1.5" in content:
            print_success("文件版本: 1.5 ✓")
        else:
            print_error("文件版本不是1.5！")
            return False
            
        if "强制重启" in content:
            print_success("包含强制重启功能 ✓")
        else:
            print_error("缺少强制重启功能！")
            return False
            
        if "服务器管理" in content:
            print_success("包含服务器管理面板 ✓")
        else:
            print_error("缺少服务器管理面板！")
            return False
            
        return True
        
    except Exception as e:
        print_error(f"读取文件失败: {e}")
        return False

def start_server():
    """启动服务器"""
    print_step(5, "启动服务器")
    
    try:
        # 启动服务器进程
        if sys.platform == "win32":
            subprocess.Popen(["python", "api.py"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["python3", "api.py"])
        
        print_success("服务器启动命令已执行")
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(8)
        
        return True
        
    except Exception as e:
        print_error(f"启动服务器失败: {e}")
        return False

def test_server():
    """测试服务器"""
    print_step(6, "测试服务器连接")
    
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"尝试连接服务器 ({i+1}/{max_retries})...")
            response = requests.get("http://localhost:5000/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print_success("服务器连接成功！")
                print(f"  服务名称: {data.get('service', 'N/A')}")
                print(f"  版本: {data.get('version', 'N/A')}")
                print(f"  状态: {data.get('status', 'N/A')}")
                
                if data.get('version') == '1.5':
                    print_success("服务器版本正确: 1.5 ✓")
                    return True
                else:
                    print_warning(f"服务器版本不正确: {data.get('version')}")
                    
            else:
                print_warning(f"服务器响应异常: HTTP {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print_warning("无法连接到服务器，继续等待...")
            time.sleep(3)
        except Exception as e:
            print_warning(f"测试服务器失败: {e}")
            time.sleep(3)
    
    print_error("服务器测试失败")
    return False

def test_admin_page():
    """测试管理页面"""
    print_step(7, "测试管理页面")
    
    try:
        response = requests.get("http://localhost:5000/admin", timeout=10)
        if response.status_code == 200:
            content = response.text
            
            if "版本 1.5" in content:
                print_success("管理页面版本正确: 1.5 ✓")
            else:
                print_warning("管理页面版本不正确")
                
            if "服务器管理" in content:
                print_success("包含服务器管理面板 ✓")
            else:
                print_warning("缺少服务器管理面板")
                
            if "强制重启服务器" in content:
                print_success("包含强制重启按钮 ✓")
                return True
            else:
                print_warning("缺少强制重启按钮")
                
        else:
            print_error(f"管理页面访问失败: HTTP {response.status_code}")
            
    except Exception as e:
        print_error(f"测试管理页面失败: {e}")
    
    return False

def main():
    """主函数"""
    print("🚀 乐影系统服务器缓存问题修复工具 v1.0")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 执行修复步骤
    kill_python_processes()
    clear_python_cache()
    check_port_usage()
    
    if not verify_file_update():
        print_error("文件验证失败，请检查api.py文件是否正确更新")
        return
    
    if not start_server():
        print_error("服务器启动失败")
        return
    
    if not test_server():
        print_error("服务器测试失败")
        return
    
    if not test_admin_page():
        print_warning("管理页面测试失败，但服务器已启动")
    
    # 最终结果
    print_step("完成", "修复结果")
    print_success("服务器缓存问题修复完成！")
    print("🎯 访问地址:")
    print("  📊 管理后台: http://localhost:5000/admin")
    print("  🔄 强制重启: http://localhost:5000/force_restart")
    print("  📡 API状态: http://localhost:5000/")
    
    print("\n💡 使用建议:")
    print("1. 在浏览器中按 Ctrl+F5 强制刷新页面")
    print("2. 如果仍有问题，使用管理后台的'强制重启服务器'按钮")
    print("3. 清除浏览器缓存和Cookie")

if __name__ == "__main__":
    main()
