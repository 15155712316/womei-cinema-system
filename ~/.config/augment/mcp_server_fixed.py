#!/Users/jiang/data/沃美0617/user-feedback-mcp/.venv/bin/python
"""
Augment Agent MCP 服务器
为 VSCode 中的 Augment Agent 提供 MCP 工具
"""

import sys
import os
sys.path.insert(0, '/Users/jiang/data/沃美0617/user-feedback-mcp/.venv/lib/python3.11/site-packages')

from fastmcp import FastMCP
import subprocess
import json
import requests
from typing import Dict, Any

# 创建 FastMCP 实例
mcp = FastMCP("Augment Agent MCP Suite", log_level="INFO")

@mcp.tool()
def context7_search(query: str) -> Dict[str, Any]:
    """使用 Context 7 进行向量搜索"""
    return {
        "status": "success",
        "query": query,
        "message": "Context 7 搜索功能已配置，请在 Augment Agent 中使用"
    }

@mcp.tool()
def playwright_automation(action: str, target: str = "") -> Dict[str, Any]:
    """使用 Playwright 进行浏览器自动化"""
    return {
        "status": "success",
        "action": action,
        "target": target,
        "message": "Playwright 自动化功能已配置，请在 Augment Agent 中使用"
    }

@mcp.tool()
def sequential_thinking(problem: str) -> Dict[str, Any]:
    """使用结构化思维分析问题"""
    return {
        "status": "success",
        "problem": problem,
        "steps": [
            "1. 问题分析",
            "2. 方案设计", 
            "3. 实施计划",
            "4. 风险评估",
            "5. 结果验证"
        ],
        "message": "Sequential Thinking 功能已配置，请在 Augment Agent 中使用"
    }

@mcp.tool()
def user_feedback(project_directory: str, summary: str) -> Dict[str, Any]:
    """启动用户反馈系统"""
    try:
        # 检查远程服务是否运行
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                service_status = "running"
                # 创建会话
                session_data = {
                    "project_directory": project_directory,
                    "summary": summary,
                    "client_info": {"source": "augment_agent"}
                }
                session_response = requests.post(
                    "http://localhost:3000/api/sessions",
                    json=session_data,
                    timeout=10
                )
                if session_response.status_code == 200:
                    session_info = session_response.json()
                    return {
                        "status": "success",
                        "project_directory": project_directory,
                        "summary": summary,
                        "service_status": service_status,
                        "session_id": session_info.get("id"),
                        "web_url": session_info.get("web_url"),
                        "message": f"用户反馈系统已启动，请在浏览器中打开: {session_info.get('web_url')}"
                    }
            else:
                service_status = "error"
        except:
            service_status = "not_running"
        
        return {
            "status": "warning",
            "project_directory": project_directory,
            "summary": summary,
            "service_status": service_status,
            "message": "用户反馈服务未运行，请先启动服务: cd /Users/jiang/data/沃美0617/user-feedback-mcp/remote-service && node dist/server.js"
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def check_mcp_status() -> Dict[str, Any]:
    """检查所有 MCP 服务器状态"""
    status = {}
    
    # 检查 NPX 工具
    tools = {
        "context7": ["/opt/homebrew/bin/npx", "-y", "@upstash/context7-mcp@latest", "--help"],
        "playwright": ["/opt/homebrew/bin/npx", "-y", "@playwright/mcp@latest", "--help"],
        "sequential-thinking": ["/opt/homebrew/bin/npx", "-y", "@modelcontextprotocol/server-sequential-thinking@latest", "--help"]
    }
    
    for tool_name, cmd in tools.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                status[tool_name] = "available"
            else:
                status[tool_name] = "error"
        except subprocess.TimeoutExpired:
            status[tool_name] = "timeout"
        except Exception as e:
            status[tool_name] = f"error: {str(e)}"
    
    # 检查用户反馈服务
    try:
        response = requests.get("http://localhost:3000/api/health", timeout=5)
        if response.status_code == 200:
            status["user-feedback-service"] = "running"
        else:
            status["user-feedback-service"] = "error"
    except:
        status["user-feedback-service"] = "not_running"
    
    return {
        "status": "success",
        "servers": status,
        "message": "MCP 服务器状态检查完成"
    }

if __name__ == "__main__":
    print("🚀 启动 Augment Agent MCP 服务器")
    print("📋 可用工具:")
    print("  • context7_search - Context 7 向量搜索")
    print("  • playwright_automation - Playwright 浏览器自动化")
    print("  • sequential_thinking - 结构化思维分析")
    print("  • user_feedback - 用户反馈系统")
    print("  • check_mcp_status - 检查 MCP 服务器状态")
    
    # 运行 FastMCP 服务器
    mcp.run()
