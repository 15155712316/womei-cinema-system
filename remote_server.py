#!/usr/bin/env python3
"""
远程 MCP 用户反馈服务器
支持通过 HTTP/WebSocket 远程访问 GUI 功能
"""

import os
import sys
import json
import asyncio
import tempfile
import subprocess
import uuid
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加当前目录到 Python 路径
sys.path.append('.')

app = FastAPI(title="远程用户反馈服务", version="1.0.0")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket 连接建立: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket 连接断开: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"发送消息失败 {session_id}: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

class FeedbackRequest(BaseModel):
    project_directory: str
    summary: str
    client_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    command_logs: str
    user_feedback: str
    success: bool
    error_message: Optional[str] = None

# 存储活跃的反馈会话
active_sessions: Dict[str, Dict[str, Any]] = {}

@app.get("/")
async def root():
    """返回 Web 界面"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
    <title>远程用户反馈系统</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1e1e1e; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { margin: 20px 0; padding: 20px; background: #2d2d2d; border-radius: 8px; }
        .command-area { display: flex; gap: 10px; margin: 10px 0; }
        .command-input { flex: 1; padding: 8px; background: #3d3d3d; border: 1px solid #555; color: #fff; }
        .btn { padding: 8px 16px; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #005a9e; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .log-area { height: 300px; overflow-y: auto; background: #1a1a1a; padding: 10px; font-family: monospace; font-size: 12px; border: 1px solid #555; }
        .feedback-area { width: 100%; height: 100px; background: #3d3d3d; border: 1px solid #555; color: #fff; padding: 8px; }
        .status { padding: 5px 10px; border-radius: 4px; margin: 5px 0; }
        .status.success { background: #2d5a2d; }
        .status.error { background: #5a2d2d; }
        .status.info { background: #2d4a5a; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 远程用户反馈系统</h1>
        
        <div class="section">
            <h3>📁 项目信息</h3>
            <div>工作目录: <span id="workdir">未连接</span></div>
            <div>任务描述: <span id="summary">未连接</span></div>
            <div class="status info" id="connection-status">等待连接...</div>
        </div>
        
        <div class="section">
            <h3>💻 命令执行</h3>
            <div class="command-area">
                <input type="text" id="command-input" class="command-input" placeholder="输入要执行的命令..." disabled>
                <button id="run-btn" class="btn" onclick="runCommand()" disabled>运行</button>
                <button id="clear-btn" class="btn" onclick="clearLogs()">清除日志</button>
            </div>
            <div id="log-output" class="log-area">等待连接到远程服务器...</div>
        </div>
        
        <div class="section">
            <h3>📝 反馈提交</h3>
            <textarea id="feedback-input" class="feedback-area" placeholder="请输入您的反馈..." disabled></textarea>
            <br><br>
            <button id="submit-btn" class="btn" onclick="submitFeedback()" disabled>提交反馈</button>
        </div>
    </div>

    <script>
        let ws = null;
        let sessionId = null;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function(event) {
                updateStatus('已连接到服务器', 'success');
                enableControls(true);
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onclose = function(event) {
                updateStatus('连接已断开', 'error');
                enableControls(false);
                setTimeout(connect, 3000); // 3秒后重连
            };
            
            ws.onerror = function(error) {
                updateStatus('连接错误', 'error');
            };
        }
        
        function handleMessage(data) {
            switch(data.type) {
                case 'session_info':
                    sessionId = data.session_id;
                    document.getElementById('workdir').textContent = data.project_directory;
                    document.getElementById('summary').textContent = data.summary;
                    break;
                case 'command_output':
                    appendLog(data.output);
                    break;
                case 'command_finished':
                    appendLog(`\\n命令执行完成，退出码: ${data.exit_code}\\n`);
                    document.getElementById('run-btn').textContent = '运行';
                    document.getElementById('run-btn').disabled = false;
                    break;
                case 'error':
                    updateStatus(data.message, 'error');
                    break;
            }
        }
        
        function runCommand() {
            const command = document.getElementById('command-input').value.trim();
            if (!command) return;
            
            document.getElementById('run-btn').textContent = '执行中...';
            document.getElementById('run-btn').disabled = true;
            
            ws.send(JSON.stringify({
                type: 'run_command',
                command: command,
                session_id: sessionId
            }));
            
            appendLog(`$ ${command}\\n`);
        }
        
        function submitFeedback() {
            const feedback = document.getElementById('feedback-input').value.trim();
            const logs = document.getElementById('log-output').textContent;
            
            ws.send(JSON.stringify({
                type: 'submit_feedback',
                feedback: feedback,
                logs: logs,
                session_id: sessionId
            }));
            
            updateStatus('反馈已提交', 'success');
        }
        
        function clearLogs() {
            document.getElementById('log-output').textContent = '';
        }
        
        function appendLog(text) {
            const logArea = document.getElementById('log-output');
            logArea.textContent += text;
            logArea.scrollTop = logArea.scrollHeight;
        }
        
        function updateStatus(message, type) {
            const status = document.getElementById('connection-status');
            status.textContent = message;
            status.className = `status ${type}`;
        }
        
        function enableControls(enabled) {
            document.getElementById('command-input').disabled = !enabled;
            document.getElementById('run-btn').disabled = !enabled;
            document.getElementById('feedback-input').disabled = !enabled;
            document.getElementById('submit-btn').disabled = !enabled;
        }
        
        // 页面加载时连接
        window.onload = connect;
        
        // 回车键执行命令
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('command-input').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    runCommand();
                }
            });
        });
    </script>
</body>
</html>
    """)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 连接处理"""
    await manager.connect(websocket, session_id)

    try:
        # 发送会话信息
        if session_id in manager.sessions:
            session_info = manager.sessions[session_id]
            await manager.send_message(session_id, {
                "type": "session_info",
                "session_id": session_id,
                "project_directory": session_info["project_directory"],
                "summary": session_info["summary"]
            })

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "run_command":
                await handle_command_execution(session_id, message)
            elif message["type"] == "submit_feedback":
                await handle_feedback_submission(session_id, message)

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect(session_id)

async def handle_command_execution(session_id: str, message: Dict[str, Any]):
    """处理命令执行"""
    command = message["command"]

    if session_id not in manager.sessions:
        await manager.send_message(session_id, {
            "type": "error",
            "message": "无效的会话ID"
        })
        return

    session = manager.sessions[session_id]
    project_dir = session["project_directory"]
    
    try:
        # 执行命令
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=project_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            text=True
        )
        
        # 实时读取输出
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            await websocket.send_text(json.dumps({
                "type": "command_output",
                "output": line
            }))
        
        # 等待进程结束
        exit_code = await process.wait()
        
        await websocket.send_text(json.dumps({
            "type": "command_finished",
            "exit_code": exit_code
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"命令执行失败: {str(e)}"
        }))

async def handle_feedback_submission(websocket: WebSocket, message: Dict[str, Any]):
    """处理反馈提交"""
    session_id = message.get("session_id")
    feedback = message.get("feedback", "")
    logs = message.get("logs", "")
    
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session["result"] = {
            "command_logs": logs,
            "user_feedback": feedback,
            "success": True
        }
        
        # 保存结果到文件
        output_file = session.get("output_file")
        if output_file:
            with open(output_file, "w") as f:
                json.dump(session["result"], f, indent=2)

@app.post("/api/feedback", response_model=FeedbackResponse)
async def create_feedback_session(request: FeedbackRequest):
    """创建新的反馈会话"""
    
    # 验证项目目录
    if not os.path.exists(request.project_directory):
        raise HTTPException(status_code=400, detail="项目目录不存在")
    
    # 创建会话ID
    session_id = f"session_{len(active_sessions) + 1}"
    
    # 创建临时输出文件
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = tmp.name
    
    # 存储会话信息
    active_sessions[session_id] = {
        "project_directory": request.project_directory,
        "summary": request.summary,
        "output_file": output_file,
        "result": None
    }
    
    return FeedbackResponse(
        command_logs="",
        user_feedback="",
        success=True
    )

@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """获取会话信息"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    session = active_sessions[session_id]
    return {
        "session_id": session_id,
        "project_directory": session["project_directory"],
        "summary": session["summary"],
        "result": session.get("result")
    }

if __name__ == "__main__":
    print("🌐 启动远程用户反馈服务器...")
    print("📱 Web 界面: http://localhost:8000")
    print("🔗 API 文档: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
