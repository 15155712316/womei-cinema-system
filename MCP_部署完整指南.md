# MCP (Model Context Protocol) 部署完整指南

## 📋 概述

本指南详细介绍了 MCP 服务器的两种主要部署方式：**本地部署**和**远程部署**，以及它们的配置方法、技术差异和适用场景。

## 🎯 快速决策指南

### 选择本地部署的情况：
- ✅ 个人使用或小团队（1-2人）
- ✅ 注重数据隐私和安全
- ✅ 网络连接不稳定或需要离线工作
- ✅ 预算有限（几乎零成本）
- ✅ 简单的维护需求

### 选择远程部署的情况：
- ✅ 企业团队协作（3+人）
- ✅ 需要高可用性和负载均衡
- ✅ 多地域分布式团队
- ✅ 有专业运维团队和预算
- ✅ 需要集中化管理和监控

## 📁 文件结构

```
MCP部署文件/
├── claude_desktop_config.json          # 基础MCP配置
├── remote_claude_configs.json          # 远程部署配置示例
├── remote_mcp_server_setup.md          # 远程服务器部署指南
├── mcp_deployment_comparison.md        # 详细技术对比
├── mcp_scenario_guide.md              # 场景选择指南
├── mcp_config_manager.sh              # 配置管理工具
├── install_mcp.sh                     # 本地安装脚本
├── test_mcp.sh                        # 测试脚本
└── MCP_使用说明.md                    # 基础使用说明
```

## 🛠️ 配置管理工具使用

我们提供了一个强大的配置管理工具 `mcp_config_manager.sh`：

```bash
# 查看当前状态
./mcp_config_manager.sh --status

# 切换到本地部署
./mcp_config_manager.sh --local

# 切换到远程部署
./mcp_config_manager.sh --remote

# 测试连接
./mcp_config_manager.sh --test

# 备份配置
./mcp_config_manager.sh --backup

# 查看帮助
./mcp_config_manager.sh --help
```

## 📊 技术对比总结

| 特性 | 本地部署 | 远程部署 |
|------|---------|---------|
| **延迟** | 1-5ms ⚡ | 50-500ms 🌐 |
| **可靠性** | 依赖本地机器 💻 | 专业服务器管理 🏢 |
| **安全性** | 本地数据保护 🔒 | 网络传输加密 🛡️ |
| **成本** | 几乎为0 💰 | $50-300/月 💳 |
| **维护** | 个人维护 👤 | 专业运维 👥 |
| **扩展性** | 单机限制 📱 | 水平扩展 📈 |

## 🚀 部署步骤

### 本地部署（推荐个人用户）

1. **安装依赖**：
   ```bash
   # 已完成：Node.js, npm, @upstash/context7-mcp
   ./test_mcp.sh  # 验证安装
   ```

2. **配置Claude Desktop**：
   ```bash
   ./mcp_config_manager.sh --local
   ```

3. **重启Claude Desktop**

### 远程部署（推荐企业用户）

1. **服务器端部署**：
   ```bash
   # 使用Docker（推荐）
   docker run -d -p 3000:3000 --name context7-mcp \
     node:20-alpine sh -c "npm install -g @upstash/context7-mcp && npx @upstash/context7-mcp --transport http --port 3000"
   ```

2. **配置Claude Desktop**：
   ```bash
   ./mcp_config_manager.sh --remote
   # 按提示输入远程服务器地址
   ```

3. **重启Claude Desktop**

## 🔧 高级配置

### 企业级远程部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  context7-mcp:
    image: node:20-alpine
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NODE_OPTIONS=--max-old-space-size=4096
    command: >
      sh -c "npm install -g @upstash/context7-mcp &&
             npx @upstash/context7-mcp --transport http --port 3000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - context7-mcp
```

### 负载均衡配置

```nginx
upstream mcp_backend {
    server mcp-server-1:3000;
    server mcp-server-2:3000;
    server mcp-server-3:3000;
}

server {
    listen 443 ssl;
    server_name mcp.company.com;
    
    ssl_certificate /etc/ssl/certs/company.crt;
    ssl_certificate_key /etc/ssl/private/company.key;
    
    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔍 监控和故障排除

### 健康检查脚本

```bash
#!/bin/bash
# health_check.sh

check_local_mcp() {
    if pgrep -f "context7-mcp" > /dev/null; then
        echo "✅ 本地MCP服务运行正常"
        return 0
    else
        echo "❌ 本地MCP服务未运行"
        return 1
    fi
}

check_remote_mcp() {
    local url=$1
    if curl -s -f "$url/health" > /dev/null; then
        echo "✅ 远程MCP服务运行正常"
        return 0
    else
        echo "❌ 远程MCP服务异常"
        return 1
    fi
}

# 使用示例
check_local_mcp
check_remote_mcp "https://mcp.company.com"
```

### 常见问题解决

1. **MCP服务器无法启动**：
   ```bash
   # 检查Node.js版本
   node --version  # 需要 >= 18.0.0
   
   # 重新安装MCP服务器
   npm uninstall -g @upstash/context7-mcp
   npm install -g @upstash/context7-mcp
   ```

2. **Claude Desktop无法连接**：
   ```bash
   # 验证配置文件
   cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
   
   # 重置配置
   ./mcp_config_manager.sh --backup
   ./mcp_config_manager.sh --local  # 或 --remote
   ```

3. **远程连接超时**：
   ```bash
   # 检查网络连接
   curl -v https://your-mcp-server.com/health
   
   # 检查防火墙设置
   telnet your-mcp-server.com 443
   ```

## 📈 性能优化建议

### 本地部署优化

```bash
# 增加Node.js内存限制
export NODE_OPTIONS="--max-old-space-size=4096"

# 优化npm缓存
npm config set cache ~/.npm-cache
npm config set cache-min 86400
```

### 远程部署优化

```yaml
# 资源限制优化
services:
  context7-mcp:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## 🔄 迁移指南

### 从本地迁移到远程

```bash
# 1. 备份本地配置
./mcp_config_manager.sh --backup

# 2. 部署远程服务器
docker-compose up -d

# 3. 切换配置
./mcp_config_manager.sh --remote

# 4. 测试连接
./mcp_config_manager.sh --test
```

### 从远程迁移到本地

```bash
# 1. 确保本地依赖
./test_mcp.sh

# 2. 备份远程配置
./mcp_config_manager.sh --backup

# 3. 切换配置
./mcp_config_manager.sh --local

# 4. 测试连接
./mcp_config_manager.sh --test
```

## 📞 获取支持

如果遇到问题，请按以下顺序排查：

1. **运行诊断工具**：
   ```bash
   ./mcp_config_manager.sh --status
   ./mcp_config_manager.sh --test
   ```

2. **查看日志**：
   ```bash
   # 本地部署日志
   tail -f ~/.npm/_logs/*.log
   
   # 远程部署日志
   docker logs context7-mcp
   ```

3. **重置配置**：
   ```bash
   ./mcp_config_manager.sh --backup
   ./install_mcp.sh  # 重新安装
   ```

## 🎉 总结

- **本地部署**：适合个人用户，零成本，高隐私，简单维护
- **远程部署**：适合企业用户，高可用，专业运维，支持团队协作
- **配置管理工具**：提供便捷的切换和管理功能
- **完整文档**：涵盖部署、配置、监控、故障排除的全流程

选择适合您需求的部署方式，享受强大的MCP功能！🚀
