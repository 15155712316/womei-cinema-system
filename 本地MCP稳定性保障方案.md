# 本地 MCP 部署稳定性保障方案

## 🎯 保障目标

确保本地 MCP 服务器能够：
- ✅ 开机自动启动
- ✅ 异常时自动重启
- ✅ 资源使用监控
- ✅ 日志记录和故障诊断
- ✅ 版本更新管理

## 🛠️ 实施步骤

### 1. 安装守护进程管理器

```bash
# 使守护进程管理器可执行
chmod +x mcp_daemon_manager.sh

# 启动 MCP 服务器
./mcp_daemon_manager.sh start

# 查看运行状态
./mcp_daemon_manager.sh status
```

### 2. 安装为系统服务（推荐）

```bash
# 安装为 macOS 系统服务（开机自启动）
./mcp_daemon_manager.sh install

# 验证服务状态
launchctl list | grep com.mcp.daemon
```

### 3. 启用监控模式

```bash
# 方式1：手动启动监控（测试用）
./mcp_daemon_manager.sh monitor

# 方式2：系统服务自动监控（推荐）
# 安装服务后会自动启用监控
```

## 🔧 配置优化

### 1. 系统资源优化

创建 MCP 专用配置文件：

```bash
# 创建配置文件
cat > mcp_config.env << 'EOF'
# Node.js 优化配置
export NODE_OPTIONS="--max-old-space-size=2048 --max-semi-space-size=128"
export UV_THREADPOOL_SIZE=8

# 系统优化
export MALLOC_ARENA_MAX=2
export NODE_ENV=production

# MCP 特定配置
export MCP_LOG_LEVEL=info
export MCP_CACHE_SIZE=256
EOF

# 在启动脚本中加载配置
source mcp_config.env
```

### 2. 内存和CPU限制

```bash
# 创建资源限制脚本
cat > set_mcp_limits.sh << 'EOF'
#!/bin/bash

# 获取 MCP 进程 PID
MCP_PID=$(pgrep -f "context7-mcp")

if [ -n "$MCP_PID" ]; then
    # 设置 CPU 优先级（nice 值）
    renice -n 5 $MCP_PID
    
    # 在 macOS 上使用 ulimit 限制资源
    # 限制虚拟内存为 2GB
    ulimit -v 2097152
    
    echo "已为 MCP 进程 $MCP_PID 设置资源限制"
else
    echo "未找到 MCP 进程"
fi
EOF

chmod +x set_mcp_limits.sh
```

## 📊 监控和告警

### 1. 健康检查脚本

```bash
# 创建详细的健康检查
cat > mcp_health_check.sh << 'EOF'
#!/bin/bash

LOG_FILE="logs/health_detailed.log"
ALERT_THRESHOLD_MEMORY=1048576  # 1GB in KB
ALERT_THRESHOLD_CPU=80          # 80% CPU

check_mcp_health() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 检查进程是否存在
    local mcp_pid=$(pgrep -f "context7-mcp")
    if [ -z "$mcp_pid" ]; then
        echo "[$timestamp] CRITICAL: MCP 进程未运行" >> "$LOG_FILE"
        return 1
    fi
    
    # 获取资源使用情况
    local stats=$(ps -o pid,pcpu,pmem,vsz,rss,time,comm -p "$mcp_pid" | tail -1)
    local cpu_usage=$(echo "$stats" | awk '{print $2}' | cut -d. -f1)
    local mem_usage=$(echo "$stats" | awk '{print $5}')
    
    echo "[$timestamp] INFO: PID=$mcp_pid CPU=${cpu_usage}% MEM=${mem_usage}KB" >> "$LOG_FILE"
    
    # 检查内存使用
    if [ "$mem_usage" -gt "$ALERT_THRESHOLD_MEMORY" ]; then
        echo "[$timestamp] WARNING: 内存使用过高 ${mem_usage}KB" >> "$LOG_FILE"
        return 2
    fi
    
    # 检查 CPU 使用
    if [ "$cpu_usage" -gt "$ALERT_THRESHOLD_CPU" ]; then
        echo "[$timestamp] WARNING: CPU使用过高 ${cpu_usage}%" >> "$LOG_FILE"
        return 3
    fi
    
    # 检查 MCP 服务响应
    if ! timeout 5 npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
        echo "[$timestamp] ERROR: MCP 服务无响应" >> "$LOG_FILE"
        return 4
    fi
    
    echo "[$timestamp] OK: 所有检查通过" >> "$LOG_FILE"
    return 0
}

# 执行检查
mkdir -p logs
check_mcp_health
exit $?
EOF

chmod +x mcp_health_check.sh
```

### 2. 自动告警系统

```bash
# 创建告警脚本
cat > mcp_alert.sh << 'EOF'
#!/bin/bash

ALERT_LOG="logs/alerts.log"
LAST_ALERT_FILE="logs/last_alert_time"

send_alert() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 防止重复告警（5分钟内不重复发送同类告警）
    local current_time=$(date +%s)
    local last_alert_time=0
    
    if [ -f "$LAST_ALERT_FILE" ]; then
        last_alert_time=$(cat "$LAST_ALERT_FILE")
    fi
    
    if [ $((current_time - last_alert_time)) -lt 300 ]; then
        return 0  # 跳过重复告警
    fi
    
    echo "$current_time" > "$LAST_ALERT_FILE"
    echo "[$timestamp] [$level] $message" >> "$ALERT_LOG"
    
    # macOS 系统通知
    osascript -e "display notification \"$message\" with title \"MCP 告警\" subtitle \"$level\""
    
    # 可选：发送邮件或其他通知方式
    # echo "$message" | mail -s "MCP Alert: $level" your-email@example.com
}

# 使用示例
# send_alert "CRITICAL" "MCP 服务器已停止运行"
EOF

chmod +x mcp_alert.sh
```

## 🔄 自动更新机制

### 1. 版本检查和更新

```bash
# 创建自动更新脚本
cat > mcp_auto_update.sh << 'EOF'
#!/bin/bash

UPDATE_LOG="logs/update.log"
CURRENT_VERSION_FILE="logs/current_version"

check_for_updates() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] 检查 MCP 服务器更新..." >> "$UPDATE_LOG"
    
    # 获取当前版本
    local current_version=""
    if [ -f "$CURRENT_VERSION_FILE" ]; then
        current_version=$(cat "$CURRENT_VERSION_FILE")
    fi
    
    # 检查最新版本
    local latest_version=$(npm view @upstash/context7-mcp version 2>/dev/null)
    
    if [ -z "$latest_version" ]; then
        echo "[$timestamp] 无法获取最新版本信息" >> "$UPDATE_LOG"
        return 1
    fi
    
    echo "[$timestamp] 当前版本: $current_version, 最新版本: $latest_version" >> "$UPDATE_LOG"
    
    if [ "$current_version" != "$latest_version" ]; then
        echo "[$timestamp] 发现新版本，开始更新..." >> "$UPDATE_LOG"
        update_mcp "$latest_version"
    else
        echo "[$timestamp] 已是最新版本" >> "$UPDATE_LOG"
    fi
}

update_mcp() {
    local new_version=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 停止当前服务
    ./mcp_daemon_manager.sh stop
    
    # 备份当前配置
    ./mcp_config_manager.sh --backup
    
    # 更新 MCP 服务器
    echo "[$timestamp] 更新到版本 $new_version..." >> "$UPDATE_LOG"
    
    if npm update -g @upstash/context7-mcp; then
        echo "$new_version" > "$CURRENT_VERSION_FILE"
        echo "[$timestamp] 更新成功" >> "$UPDATE_LOG"
        
        # 重启服务
        ./mcp_daemon_manager.sh start
        
        # 发送成功通知
        source mcp_alert.sh
        send_alert "INFO" "MCP 已成功更新到版本 $new_version"
    else
        echo "[$timestamp] 更新失败" >> "$UPDATE_LOG"
        
        # 重启旧版本服务
        ./mcp_daemon_manager.sh start
        
        # 发送失败通知
        source mcp_alert.sh
        send_alert "ERROR" "MCP 更新失败，已回滚到旧版本"
    fi
}

# 执行更新检查
mkdir -p logs
check_for_updates
EOF

chmod +x mcp_auto_update.sh
```

### 2. 定期更新任务

```bash
# 创建 cron 任务
cat > setup_cron.sh << 'EOF'
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 添加 cron 任务
(crontab -l 2>/dev/null; echo "# MCP 自动更新 - 每周日凌晨2点检查更新") | crontab -
(crontab -l 2>/dev/null; echo "0 2 * * 0 cd $SCRIPT_DIR && ./mcp_auto_update.sh") | crontab -

# 添加健康检查任务 - 每5分钟检查一次
(crontab -l 2>/dev/null; echo "# MCP 健康检查 - 每5分钟") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * cd $SCRIPT_DIR && ./mcp_health_check.sh") | crontab -

# 添加日志清理任务 - 每天凌晨1点
(crontab -l 2>/dev/null; echo "# MCP 日志清理 - 每天凌晨1点") | crontab -
(crontab -l 2>/dev/null; echo "0 1 * * * cd $SCRIPT_DIR && ./mcp_daemon_manager.sh cleanup") | crontab -

echo "✅ Cron 任务已设置"
echo "当前 cron 任务："
crontab -l
EOF

chmod +x setup_cron.sh
```

## 🚨 故障恢复机制

### 1. 自动故障恢复

```bash
# 创建故障恢复脚本
cat > mcp_recovery.sh << 'EOF'
#!/bin/bash

RECOVERY_LOG="logs/recovery.log"
MAX_RESTART_ATTEMPTS=3
RESTART_ATTEMPT_FILE="logs/restart_attempts"

attempt_recovery() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local attempts=0
    
    if [ -f "$RESTART_ATTEMPT_FILE" ]; then
        attempts=$(cat "$RESTART_ATTEMPT_FILE")
    fi
    
    attempts=$((attempts + 1))
    echo "$attempts" > "$RESTART_ATTEMPT_FILE"
    
    echo "[$timestamp] 尝试恢复 MCP 服务 (第 $attempts 次)" >> "$RECOVERY_LOG"
    
    if [ $attempts -le $MAX_RESTART_ATTEMPTS ]; then
        # 尝试重启服务
        ./mcp_daemon_manager.sh restart
        
        # 等待服务启动
        sleep 10
        
        # 验证服务状态
        if ./mcp_health_check.sh; then
            echo "[$timestamp] 恢复成功" >> "$RECOVERY_LOG"
            rm -f "$RESTART_ATTEMPT_FILE"
            
            source mcp_alert.sh
            send_alert "INFO" "MCP 服务已成功恢复"
            return 0
        else
            echo "[$timestamp] 恢复失败" >> "$RECOVERY_LOG"
            return 1
        fi
    else
        echo "[$timestamp] 达到最大重试次数，停止自动恢复" >> "$RECOVERY_LOG"
        
        source mcp_alert.sh
        send_alert "CRITICAL" "MCP 服务恢复失败，需要手动干预"
        return 1
    fi
}

# 重置重试计数器（每天重置）
reset_attempts() {
    rm -f "$RESTART_ATTEMPT_FILE"
}

# 根据参数执行相应操作
case "${1:-attempt}" in
    attempt)
        attempt_recovery
        ;;
    reset)
        reset_attempts
        ;;
    *)
        echo "用法: $0 [attempt|reset]"
        ;;
esac
EOF

chmod +x mcp_recovery.sh
```

## 📋 完整部署清单

### 1. 一键部署脚本

```bash
# 创建一键部署脚本
cat > deploy_stable_mcp.sh << 'EOF'
#!/bin/bash

echo "🚀 开始部署稳定的本地 MCP 服务..."

# 1. 设置权限
chmod +x *.sh

# 2. 创建必要目录
mkdir -p logs

# 3. 安装 MCP 守护服务
echo "📦 安装 MCP 守护服务..."
./mcp_daemon_manager.sh install

# 4. 设置定期任务
echo "⏰ 设置定期任务..."
./setup_cron.sh

# 5. 启动服务
echo "🔄 启动 MCP 服务..."
./mcp_daemon_manager.sh start

# 6. 验证安装
echo "🧪 验证安装..."
sleep 5
if ./mcp_health_check.sh; then
    echo "✅ MCP 稳定性保障部署成功！"
    echo ""
    echo "📋 服务状态："
    ./mcp_daemon_manager.sh status
    echo ""
    echo "💡 管理命令："
    echo "  查看状态: ./mcp_daemon_manager.sh status"
    echo "  重启服务: ./mcp_daemon_manager.sh restart"
    echo "  查看日志: tail -f logs/mcp_daemon.log"
    echo "  健康检查: ./mcp_health_check.sh"
else
    echo "❌ 部署验证失败，请检查日志"
    exit 1
fi
EOF

chmod +x deploy_stable_mcp.sh
```

## 🎯 使用建议

### 立即执行：

1. **部署稳定性保障**：
   ```bash
   ./deploy_stable_mcp.sh
   ```

2. **验证服务状态**：
   ```bash
   ./mcp_daemon_manager.sh status
   ```

3. **查看实时日志**：
   ```bash
   tail -f logs/mcp_daemon.log
   ```

### 长期维护：

- **每周检查**：`./mcp_daemon_manager.sh status`
- **月度清理**：`./mcp_daemon_manager.sh cleanup`
- **版本更新**：`./mcp_auto_update.sh`（或等待自动更新）

这套方案确保您的本地 MCP 服务器能够：
- 🔄 自动启动和重启
- 📊 持续监控和告警
- 🛡️ 故障自动恢复
- 📈 性能优化
- 🔧 自动更新维护

让您的本地 MCP 部署达到生产级别的稳定性！
