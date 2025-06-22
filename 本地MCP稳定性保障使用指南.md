# 本地 MCP 稳定性保障使用指南

## 🎯 概述

为了确保您的本地 MCP 服务器能够一直稳定运行，我们提供了一套完整的稳定性保障解决方案，包括：

- ✅ **自动启动和重启** - 开机自启动，异常自动恢复
- ✅ **守护进程管理** - 持续监控服务状态
- ✅ **资源监控** - 内存、CPU 使用监控
- ✅ **日志记录** - 完整的运行日志和错误记录
- ✅ **故障恢复** - 自动故障检测和恢复机制
- ✅ **版本管理** - 自动更新检查和管理

## 🚀 快速开始

### 方式一：一键部署（推荐）

```bash
# 运行快速部署脚本
./快速部署MCP稳定性保障.sh
```

这个脚本会：
1. 检查系统要求
2. 引导您选择部署模式
3. 自动配置所有组件
4. 验证部署结果

### 方式二：使用配置管理器

```bash
# 安装稳定性保障
./mcp_config_manager.sh --install

# 管理守护进程
./mcp_config_manager.sh --daemon
```

## 🔧 部署模式选择

### 基础模式 🏠
**适合：** 个人用户，简单需求

**功能：**
- MCP 守护进程
- 异常自动重启
- 基础日志记录

**启动方式：**
```bash
./mcp_daemon_manager.sh start
```

### 完整模式 🚀 (推荐)
**适合：** 需要高稳定性的用户

**功能：**
- 所有基础功能
- 开机自动启动
- 系统服务集成
- 完整监控和告警
- 资源使用监控

**启动方式：**
```bash
./mcp_daemon_manager.sh install  # 安装为系统服务
```

## 📋 管理命令

### 配置管理
```bash
# 查看当前配置状态
./mcp_config_manager.sh --status

# 切换到本地部署
./mcp_config_manager.sh --local

# 管理守护进程
./mcp_config_manager.sh --daemon

# 安装稳定性保障
./mcp_config_manager.sh --install

# 测试连接
./mcp_config_manager.sh --test

# 备份配置
./mcp_config_manager.sh --backup
```

### 守护进程管理
```bash
# 启动服务
./mcp_daemon_manager.sh start

# 停止服务
./mcp_daemon_manager.sh stop

# 重启服务
./mcp_daemon_manager.sh restart

# 查看状态
./mcp_daemon_manager.sh status

# 健康检查
./mcp_daemon_manager.sh health

# 启动监控模式
./mcp_daemon_manager.sh monitor

# 安装为系统服务
./mcp_daemon_manager.sh install

# 卸载系统服务
./mcp_daemon_manager.sh uninstall

# 清理日志
./mcp_daemon_manager.sh cleanup
```

## 📊 监控和日志

### 日志文件位置
```
logs/
├── mcp_daemon.log          # 主要运行日志
├── mcp_error.log           # 错误日志
├── mcp_health.log          # 健康检查日志
├── mcp_output.log          # MCP 服务器输出
└── alerts.log              # 告警日志
```

### 实时监控
```bash
# 查看实时日志
tail -f logs/mcp_daemon.log

# 查看错误日志
tail -f logs/mcp_error.log

# 查看健康检查
tail -f logs/mcp_health.log

# 查看服务状态
./mcp_daemon_manager.sh status
```

## 🚨 故障排除

### 常见问题

#### 1. MCP 服务器无法启动
```bash
# 检查 Node.js 和 npm
node --version
npm --version

# 重新安装 MCP 服务器
npm uninstall -g @upstash/context7-mcp
npm install -g @upstash/context7-mcp

# 重启守护进程
./mcp_daemon_manager.sh restart
```

#### 2. 守护进程异常
```bash
# 查看详细状态
./mcp_daemon_manager.sh status

# 查看错误日志
cat logs/mcp_error.log

# 重置守护进程
./mcp_daemon_manager.sh stop
./mcp_daemon_manager.sh start
```

#### 3. 系统服务问题
```bash
# 检查系统服务状态
launchctl list | grep com.mcp.daemon

# 重新加载服务
./mcp_daemon_manager.sh uninstall
./mcp_daemon_manager.sh install

# 查看系统日志
cat logs/launchd_out.log
cat logs/launchd_err.log
```

#### 4. Claude Desktop 连接问题
```bash
# 检查配置文件
cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# 重新配置
./mcp_config_manager.sh --backup
./mcp_config_manager.sh --local

# 测试连接
./mcp_config_manager.sh --test
```

### 诊断工具
```bash
# 运行完整诊断
./mcp_config_manager.sh --status
./mcp_daemon_manager.sh status
./mcp_config_manager.sh --test

# 查看系统资源使用
ps aux | grep context7-mcp
top -pid $(pgrep context7-mcp)
```

## 🔄 维护建议

### 日常维护
- **每周检查**：`./mcp_daemon_manager.sh status`
- **月度清理**：`./mcp_daemon_manager.sh cleanup`
- **配置备份**：`./mcp_config_manager.sh --backup`

### 定期任务
系统会自动执行以下任务：
- 每5分钟：健康检查
- 每天凌晨1点：日志清理
- 每周日凌晨2点：版本更新检查

### 手动更新
```bash
# 检查更新
npm outdated -g @upstash/context7-mcp

# 更新 MCP 服务器
npm update -g @upstash/context7-mcp

# 重启服务
./mcp_daemon_manager.sh restart
```

## 📈 性能优化

### 资源配置
默认配置已经过优化，如需调整：

```bash
# 编辑环境配置
nano mcp_config.env

# 常用优化参数
export NODE_OPTIONS="--max-old-space-size=2048"
export UV_THREADPOOL_SIZE=8
export MALLOC_ARENA_MAX=2
```

### 监控阈值
可以调整监控阈值：
- 内存告警：1GB（默认）
- CPU 告警：80%（默认）
- 重启尝试：3次（默认）

## 🎯 最佳实践

### 1. 部署后验证
```bash
# 部署完成后必须验证
./mcp_daemon_manager.sh status
./mcp_config_manager.sh --test
```

### 2. 定期备份
```bash
# 重要操作前备份
./mcp_config_manager.sh --backup
```

### 3. 监控日志
```bash
# 定期查看日志，及时发现问题
tail -100 logs/mcp_daemon.log
```

### 4. 系统重启后检查
```bash
# 系统重启后验证服务状态
./mcp_daemon_manager.sh status
```

## 🆘 获取帮助

如果遇到问题：

1. **查看日志**：`tail -f logs/mcp_daemon.log`
2. **运行诊断**：`./mcp_config_manager.sh --status`
3. **重启服务**：`./mcp_daemon_manager.sh restart`
4. **重新部署**：`./快速部署MCP稳定性保障.sh`

## 🎉 总结

通过这套稳定性保障系统，您的本地 MCP 服务器将能够：

- 🔄 **自动运行** - 开机启动，异常重启
- 📊 **持续监控** - 实时状态监控和告警
- 🛡️ **故障恢复** - 自动检测和恢复故障
- 📝 **完整日志** - 详细的运行和错误记录
- 🔧 **简单管理** - 一键式管理和维护

让您的本地 MCP 部署达到生产级别的稳定性和可靠性！
