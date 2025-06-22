#!/bin/bash
# 远程服务器部署脚本

echo "🌐 开始部署远程用户反馈服务器..."

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ 需要 Python 3.8 或更高版本"
    exit 1
fi

echo "✅ Python 版本检查通过: $(python3 --version)"

# 创建项目目录
PROJECT_DIR="user-feedback-remote"
if [ -d "$PROJECT_DIR" ]; then
    echo "📁 项目目录已存在，正在更新..."
    cd "$PROJECT_DIR"
else
    echo "📁 创建项目目录..."
    mkdir "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "📦 安装服务器依赖..."
pip install --upgrade pip

# 安装核心依赖
pip install \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    websockets==12.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6

# 安装 PySide6（仅在服务器端）
echo "🎨 安装 PySide6（这可能需要几分钟）..."
pip install PySide6==6.6.0

# 安装其他工具
pip install \
    psutil==5.9.6 \
    requests==2.31.0

echo "✅ 依赖安装完成"

# 创建启动脚本
cat > start_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate

echo "🚀 启动远程用户反馈服务器..."
echo "📱 Web 界面: http://localhost:8000"
echo "🔗 API 文档: http://localhost:8000/docs"
echo "⏹️  按 Ctrl+C 停止服务器"

# 设置环境变量
export QT_QPA_PLATFORM=offscreen
export DISPLAY=:99

# 启动虚拟显示服务器（如果在无头服务器上）
if command -v Xvfb >/dev/null 2>&1; then
    echo "🖥️  启动虚拟显示服务器..."
    Xvfb :99 -screen 0 1024x768x24 &
    XVFB_PID=$!
    
    # 设置清理函数
    cleanup() {
        echo "🧹 清理资源..."
        if [ ! -z "$XVFB_PID" ]; then
            kill $XVFB_PID 2>/dev/null
        fi
        exit 0
    }
    trap cleanup SIGINT SIGTERM
fi

# 启动服务器
python remote_server.py
EOF

chmod +x start_server.sh

# 创建系统服务文件（可选）
cat > feedback-server.service << EOF
[Unit]
Description=User Feedback Remote Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_server.sh
Restart=always
RestartSec=10
Environment=PATH=$(pwd)/.venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=QT_QPA_PLATFORM=offscreen
Environment=DISPLAY=:99

[Install]
WantedBy=multi-user.target
EOF

echo "📋 部署完成！"
echo ""
echo "🚀 启动服务器:"
echo "  ./start_server.sh"
echo ""
echo "🔧 安装为系统服务（可选）:"
echo "  sudo cp feedback-server.service /etc/systemd/system/"
echo "  sudo systemctl enable feedback-server"
echo "  sudo systemctl start feedback-server"
echo ""
echo "📱 访问地址:"
echo "  http://localhost:8000"
echo "  http://$(hostname -I | awk '{print $1}'):8000"
