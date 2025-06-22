#!/usr/bin/env python3
"""
轻量级 MCP 客户端
连接到远程服务器，避免本地安装 PySide6
"""

import os
import sys
import json
import requests
import tempfile
import webbrowser
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated

# 轻量级 MCP 服务器（无 GUI 依赖）
mcp = FastMCP("Remote User Feedback Client", log_level="ERROR")

# 远程服务器配置
REMOTE_SERVER_URL = os.getenv("FEEDBACK_SERVER_URL", "http://localhost:8000")

class RemoteFeedbackClient:
    """远程反馈客户端"""
    
    def __init__(self, server_url: str = REMOTE_SERVER_URL):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()
    
    def create_feedback_session(self, project_directory: str, summary: str) -> Dict[str, Any]:
        """在远程服务器创建反馈会话"""
        
        try:
            response = self.session.post(
                f"{self.server_url}/api/feedback",
                json={
                    "project_directory": project_directory,
                    "summary": summary
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到远程服务器: {self.server_url}")
        except requests.exceptions.Timeout:
            raise Exception("远程服务器响应超时")
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
    
    def open_web_interface(self, session_id: str = None):
        """打开 Web 界面"""
        url = f"{self.server_url}/"
        if session_id:
            url += f"?session={session_id}"
        
        print(f"🌐 正在打开 Web 界面: {url}")
        webbrowser.open(url)
        return url
    
    def wait_for_feedback(self, session_id: str, timeout: int = 300) -> Dict[str, Any]:
        """等待用户完成反馈"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(
                    f"{self.server_url}/api/sessions/{session_id}",
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()
                
                if data.get("result"):
                    return data["result"]
                
                time.sleep(2)  # 每2秒检查一次
                
            except requests.exceptions.RequestException:
                time.sleep(5)  # 网络错误时等待更长时间
        
        raise Exception("等待用户反馈超时")

# 全局客户端实例
remote_client = RemoteFeedbackClient()

def launch_remote_feedback_ui(project_directory: str, summary: str) -> Dict[str, str]:
    """启动远程反馈界面"""
    
    print(f"🔗 连接到远程服务器: {remote_client.server_url}")
    
    try:
        # 创建远程会话
        session_result = remote_client.create_feedback_session(project_directory, summary)
        print("✅ 远程会话创建成功")
        
        # 打开 Web 界面
        web_url = remote_client.open_web_interface()
        print(f"📱 Web 界面已打开: {web_url}")
        
        print("⏳ 等待用户完成反馈...")
        print("💡 请在浏览器中完成操作，然后返回此处")
        
        # 等待用户输入确认
        input("按 Enter 键检查反馈结果...")
        
        # 这里可以实现更复杂的等待逻辑
        # 比如轮询检查结果或使用 WebSocket
        
        return {
            "command_logs": "远程执行日志（通过 Web 界面收集）",
            "user_feedback": "用户反馈（通过 Web 界面收集）"
        }
        
    except Exception as e:
        print(f"❌ 远程反馈失败: {str(e)}")
        
        # 降级到本地模式
        print("🔄 尝试降级到本地模式...")
        return fallback_to_local_mode(project_directory, summary)

def fallback_to_local_mode(project_directory: str, summary: str) -> Dict[str, str]:
    """降级到本地模式（无 GUI）"""
    
    print("📝 本地反馈模式")
    print(f"项目目录: {project_directory}")
    print(f"任务描述: {summary}")
    print("-" * 50)
    
    # 简单的命令行交互
    print("请输入要执行的命令（输入 'done' 完成）:")
    
    logs = []
    while True:
        command = input("$ ").strip()
        if command.lower() == 'done':
            break
        
        if command:
            try:
                import subprocess
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=project_directory,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                output = f"$ {command}\n"
                if result.stdout:
                    output += result.stdout
                if result.stderr:
                    output += f"ERROR: {result.stderr}"
                output += f"Exit code: {result.returncode}\n\n"
                
                logs.append(output)
                print(output)
                
            except subprocess.TimeoutExpired:
                logs.append(f"$ {command}\nERROR: 命令执行超时\n\n")
            except Exception as e:
                logs.append(f"$ {command}\nERROR: {str(e)}\n\n")
    
    # 收集用户反馈
    print("\n请输入您的反馈:")
    feedback = input("> ").strip()
    
    return {
        "command_logs": "".join(logs),
        "user_feedback": feedback
    }

def check_remote_server_status() -> bool:
    """检查远程服务器状态"""
    try:
        response = requests.get(f"{remote_client.server_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False

@mcp.tool()
def user_feedback(
    project_directory: Annotated[str, Field(description="项目目录的完整路径")],
    summary: Annotated[str, Field(description="更改内容的简短摘要")],
) -> Dict[str, str]:
    """请求用户反馈（远程模式）"""
    
    # 检查远程服务器状态
    if check_remote_server_status():
        print("🌐 使用远程服务器模式")
        return launch_remote_feedback_ui(project_directory, summary)
    else:
        print("⚠️  远程服务器不可用，使用本地模式")
        return fallback_to_local_mode(project_directory, summary)

@mcp.tool()
def configure_remote_server(
    server_url: Annotated[str, Field(description="远程服务器 URL")]
) -> str:
    """配置远程服务器地址"""
    
    global remote_client
    remote_client = RemoteFeedbackClient(server_url)
    
    if check_remote_server_status():
        return f"✅ 远程服务器配置成功: {server_url}"
    else:
        return f"⚠️  远程服务器不可访问: {server_url}"

if __name__ == "__main__":
    print("🚀 轻量级 MCP 用户反馈客户端")
    print(f"🔗 远程服务器: {REMOTE_SERVER_URL}")
    print(f"📊 服务器状态: {'在线' if check_remote_server_status() else '离线'}")
    
    mcp.run(transport="stdio")
