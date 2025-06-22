#!/bin/bash

# MCP 守护进程管理器
# 确保本地 MCP 服务器持续运行

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/mcp_daemon.pid"
LOG_FILE="$LOG_DIR/mcp_daemon.log"
ERROR_LOG="$LOG_DIR/mcp_error.log"
HEALTH_LOG="$LOG_DIR/mcp_health.log"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    echo -e "${GREEN}[$timestamp]${NC} ${BLUE}[$level]${NC} $message"
}

log_error() {
    local message=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [ERROR] $message" >> "$ERROR_LOG"
    echo -e "${GREEN}[$timestamp]${NC} ${RED}[ERROR]${NC} $message"
}

# 检查 MCP 服务器是否运行
is_mcp_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            # 进一步检查是否是正确的进程
            if ps -p "$pid" -o comm= | grep -q "node\|npx"; then
                return 0
            fi
        fi
        # PID文件存在但进程不存在，清理PID文件
        rm -f "$PID_FILE"
    fi
    return 1
}

# 启动 MCP 服务器
start_mcp() {
    if is_mcp_running; then
        log_message "INFO" "MCP 服务器已在运行中"
        return 0
    fi
    
    log_message "INFO" "启动 MCP 服务器..."
    
    # 设置环境变量
    export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
    export NODE_OPTIONS="--max-old-space-size=2048"
    
    # 启动 MCP 服务器（后台运行）
    nohup npx -y @upstash/context7-mcp > "$LOG_DIR/mcp_output.log" 2>&1 &
    local mcp_pid=$!
    
    # 保存 PID
    echo "$mcp_pid" > "$PID_FILE"
    
    # 等待几秒钟验证启动
    sleep 3
    
    if is_mcp_running; then
        log_message "SUCCESS" "MCP 服务器启动成功 (PID: $mcp_pid)"
        return 0
    else
        log_error "MCP 服务器启动失败"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止 MCP 服务器
stop_mcp() {
    if ! is_mcp_running; then
        log_message "INFO" "MCP 服务器未运行"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    log_message "INFO" "停止 MCP 服务器 (PID: $pid)..."
    
    # 优雅停止
    kill "$pid" 2>/dev/null
    
    # 等待进程结束
    local count=0
    while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    # 如果还在运行，强制杀死
    if kill -0 "$pid" 2>/dev/null; then
        log_message "WARN" "优雅停止失败，强制终止进程"
        kill -9 "$pid" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    log_message "SUCCESS" "MCP 服务器已停止"
}

# 重启 MCP 服务器
restart_mcp() {
    log_message "INFO" "重启 MCP 服务器..."
    stop_mcp
    sleep 2
    start_mcp
}

# 健康检查
health_check() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if is_mcp_running; then
        local pid=$(cat "$PID_FILE")
        local memory_usage=$(ps -o pid,vsz,rss,comm -p "$pid" 2>/dev/null | tail -1)
        echo "[$timestamp] [HEALTH] MCP运行正常: $memory_usage" >> "$HEALTH_LOG"
        
        # 检查内存使用是否过高（超过1GB）
        local rss=$(echo "$memory_usage" | awk '{print $3}')
        if [ "$rss" -gt 1048576 ]; then  # 1GB = 1048576 KB
            log_message "WARN" "内存使用过高 (${rss}KB)，重启服务"
            restart_mcp
        fi
        
        return 0
    else
        echo "[$timestamp] [HEALTH] MCP未运行" >> "$HEALTH_LOG"
        log_error "健康检查失败：MCP 服务器未运行"
        return 1
    fi
}

# 监控模式
monitor_mode() {
    log_message "INFO" "启动监控模式..."
    
    while true; do
        if ! health_check; then
            log_message "WARN" "检测到 MCP 服务器异常，尝试重启..."
            start_mcp
        fi
        
        # 每30秒检查一次
        sleep 30
    done
}

# 安装为系统服务（macOS launchd）
install_service() {
    local plist_file="$HOME/Library/LaunchAgents/com.mcp.daemon.plist"
    
    log_message "INFO" "安装 MCP 守护服务..."
    
    cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mcp.daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_DIR/mcp_daemon_manager.sh</string>
        <string>monitor</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/launchd_out.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/launchd_err.log</string>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>NODE_OPTIONS</key>
        <string>--max-old-space-size=2048</string>
    </dict>
</dict>
</plist>
EOF
    
    # 加载服务
    launchctl load "$plist_file"
    
    log_message "SUCCESS" "MCP 守护服务已安装并启动"
    echo "服务文件位置: $plist_file"
}

# 卸载系统服务
uninstall_service() {
    local plist_file="$HOME/Library/LaunchAgents/com.mcp.daemon.plist"
    
    if [ -f "$plist_file" ]; then
        log_message "INFO" "卸载 MCP 守护服务..."
        launchctl unload "$plist_file"
        rm -f "$plist_file"
        log_message "SUCCESS" "MCP 守护服务已卸载"
    else
        log_message "INFO" "未找到已安装的守护服务"
    fi
}

# 显示状态
show_status() {
    echo "================================"
    echo "MCP 守护进程状态"
    echo "================================"
    
    if is_mcp_running; then
        local pid=$(cat "$PID_FILE")
        echo -e "${GREEN}状态: 运行中${NC}"
        echo "PID: $pid"
        echo "内存使用:"
        ps -o pid,vsz,rss,comm -p "$pid" 2>/dev/null || echo "无法获取进程信息"
    else
        echo -e "${RED}状态: 未运行${NC}"
    fi
    
    echo ""
    echo "日志文件:"
    echo "  主日志: $LOG_FILE"
    echo "  错误日志: $ERROR_LOG"
    echo "  健康日志: $HEALTH_LOG"
    
    if [ -f "$HEALTH_LOG" ]; then
        echo ""
        echo "最近健康检查:"
        tail -5 "$HEALTH_LOG"
    fi
}

# 清理日志
cleanup_logs() {
    log_message "INFO" "清理旧日志文件..."
    
    # 保留最近7天的日志
    find "$LOG_DIR" -name "*.log" -mtime +7 -delete
    
    # 如果日志文件过大，截断保留最后1000行
    for log_file in "$LOG_FILE" "$ERROR_LOG" "$HEALTH_LOG"; do
        if [ -f "$log_file" ] && [ $(wc -l < "$log_file") -gt 1000 ]; then
            tail -1000 "$log_file" > "${log_file}.tmp"
            mv "${log_file}.tmp" "$log_file"
        fi
    done
    
    log_message "SUCCESS" "日志清理完成"
}

# 显示帮助
show_help() {
    echo "MCP 守护进程管理器"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start           启动 MCP 服务器"
    echo "  stop            停止 MCP 服务器"
    echo "  restart         重启 MCP 服务器"
    echo "  status          显示运行状态"
    echo "  health          执行健康检查"
    echo "  monitor         启动监控模式（持续运行）"
    echo "  install         安装为系统服务"
    echo "  uninstall       卸载系统服务"
    echo "  cleanup         清理日志文件"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start        # 启动服务"
    echo "  $0 monitor      # 启动监控模式"
    echo "  $0 install      # 安装为开机自启动服务"
}

# 主函数
main() {
    case "${1:-help}" in
        start)
            start_mcp
            ;;
        stop)
            stop_mcp
            ;;
        restart)
            restart_mcp
            ;;
        status)
            show_status
            ;;
        health)
            health_check
            ;;
        monitor)
            monitor_mode
            ;;
        install)
            install_service
            ;;
        uninstall)
            uninstall_service
            ;;
        cleanup)
            cleanup_logs
            ;;
        help|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"
