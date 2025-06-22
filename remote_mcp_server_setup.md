# 远程 MCP 服务器部署指南

## 1. 远程服务器端配置

### 1.1 服务器环境准备

```bash
# 在远程服务器上安装 Node.js 和 npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 1.2 启动 HTTP 模式的 MCP 服务器

```bash
# 方式1：直接启动（测试用）
npx -y @upstash/context7-mcp --transport http --port 3000

# 方式2：使用 PM2 管理（生产环境推荐）
npm install -g pm2
pm2 start "npx -y @upstash/context7-mcp --transport http --port 3000" --name "context7-mcp"
pm2 save
pm2 startup
```

### 1.3 使用 Docker 部署（推荐）

创建 `Dockerfile`：
```dockerfile
FROM node:20-alpine

WORKDIR /app

# 安装 MCP 服务器
RUN npm install -g @upstash/context7-mcp

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["npx", "@upstash/context7-mcp", "--transport", "http", "--port", "3000"]
```

创建 `docker-compose.yml`：
```yaml
version: '3.8'
services:
  context7-mcp:
    build: .
    ports:
      - "3000:3000"
    restart: unless-stopped
    environment:
      - NODE_ENV=production
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

启动服务：
```bash
docker-compose up -d
```

### 1.4 Nginx 反向代理配置

```nginx
server {
    listen 80;
    server_name your-mcp-server.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### 1.5 HTTPS 配置（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-mcp-server.com

# 自动续期
sudo crontab -e
# 添加：0 12 * * * /usr/bin/certbot renew --quiet
```
