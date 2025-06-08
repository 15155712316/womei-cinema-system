#!/bin/bash
# 服务器部署脚本
# 用于在 /www/wwwroot/userapi 目录部署管理后台

echo "🚀 电影票务管理系统 - 服务器部署脚本"
echo "================================================"

# 设置变量
DEPLOY_DIR="/www/wwwroot/userapi"
API_FILE="api1.py"
PORT=5000

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root权限运行此脚本"
    exit 1
fi

echo "📁 检查部署目录: $DEPLOY_DIR"
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ 部署目录不存在，正在创建..."
    mkdir -p "$DEPLOY_DIR"
fi

cd "$DEPLOY_DIR"
echo "✅ 当前目录: $(pwd)"

echo "📦 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，正在安装..."
    apt update
    apt install -y python3 python3-pip
fi

echo "📦 检查pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 未安装，正在安装..."
    apt install -y python3-pip
fi

echo "📦 安装Python依赖..."
pip3 install flask pymongo requests

echo "🔥 检查防火墙设置..."
# 检查ufw状态
if command -v ufw &> /dev/null; then
    echo "检查ufw防火墙..."
    ufw allow $PORT
    echo "✅ 已开放端口 $PORT"
fi

# 检查iptables
if command -v iptables &> /dev/null; then
    echo "检查iptables防火墙..."
    iptables -I INPUT -p tcp --dport $PORT -j ACCEPT
    echo "✅ iptables已开放端口 $PORT"
fi

echo "🔍 检查端口占用..."
if netstat -tlnp | grep ":$PORT " > /dev/null; then
    echo "⚠️  端口 $PORT 已被占用，正在停止相关进程..."
    pkill -f "python.*$API_FILE"
    sleep 2
fi

echo "🚀 启动API服务..."
if [ -f "$API_FILE" ]; then
    echo "✅ 找到API文件: $API_FILE"
    
    # 后台启动服务
    nohup python3 "$API_FILE" > api.log 2>&1 &
    API_PID=$!
    
    echo "✅ API服务已启动，PID: $API_PID"
    echo "📝 日志文件: $DEPLOY_DIR/api.log"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if ps -p $API_PID > /dev/null; then
        echo "✅ 服务运行正常"
        echo "🌐 访问地址: http://$(hostname -I | awk '{print $1}'):$PORT/admin/v2"
        echo "🌐 外网访问: http://43.142.19.28:$PORT/admin/v2"
    else
        echo "❌ 服务启动失败，请检查日志:"
        tail -20 api.log
    fi
else
    echo "❌ 未找到API文件: $API_FILE"
    echo "请确保 $API_FILE 文件存在于 $DEPLOY_DIR 目录中"
fi

echo "📋 部署完成检查清单:"
echo "□ Python3 已安装: $(python3 --version)"
echo "□ Flask 已安装: $(pip3 show flask | grep Version || echo '未安装')"
echo "□ 端口 $PORT 已开放"
echo "□ API服务已启动"
echo "□ 日志文件: $DEPLOY_DIR/api.log"

echo "🔧 常用管理命令:"
echo "查看服务状态: ps aux | grep $API_FILE"
echo "查看端口占用: netstat -tlnp | grep $PORT"
echo "查看日志: tail -f $DEPLOY_DIR/api.log"
echo "停止服务: pkill -f 'python.*$API_FILE'"
echo "重启服务: cd $DEPLOY_DIR && nohup python3 $API_FILE > api.log 2>&1 &"

echo "================================================"
echo "🎉 部署脚本执行完成！"
