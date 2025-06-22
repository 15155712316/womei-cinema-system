#!/bin/bash

# 用户反馈服务启动脚本

SERVICE_DIR="/Users/jiang/data/沃美0617/user-feedback-mcp/remote-service"
PID_FILE="/tmp/feedback-service.pid"

echo "🚀 启动用户反馈服务..."

# 检查服务是否已经在运行
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "✅ 服务已在运行 (PID: $PID)"
        echo "🌐 服务地址: http://localhost:3000"
        echo "📱 健康检查: http://localhost:3000/api/health"
        exit 0
    else
        echo "🧹 清理旧的 PID 文件"
        rm -f "$PID_FILE"
    fi
fi

# 切换到服务目录
cd "$SERVICE_DIR"

# 启动服务
echo "🔧 启动远程服务..."
nohup node dist/server.js > /tmp/feedback-service.log 2>&1 &
SERVICE_PID=$!

# 保存 PID
echo $SERVICE_PID > "$PID_FILE"

# 等待服务启动
sleep 3

# 检查服务是否成功启动
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功!"
    echo "🆔 进程 ID: $SERVICE_PID"
    echo "🌐 服务地址: http://localhost:3000"
    echo "📱 健康检查: http://localhost:3000/api/health"
    echo "📋 日志文件: /tmp/feedback-service.log"
    echo ""
    echo "🔧 管理命令:"
    echo "  查看日志: tail -f /tmp/feedback-service.log"
    echo "  停止服务: kill $SERVICE_PID"
    echo "  重启服务: $0"
else
    echo "❌ 服务启动失败"
    echo "📋 查看日志: cat /tmp/feedback-service.log"
    exit 1
fi
