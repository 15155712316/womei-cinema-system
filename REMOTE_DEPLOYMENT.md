# 🌐 远程部署指南

## 问题分析

PySide6 占用 1.2GB 空间确实是一个问题，特别是在以下场景：
- 多台客户端机器需要使用
- 云环境或容器化部署
- 网络带宽有限的环境
- 存储空间受限的设备

## 🚀 解决方案对比

| 方案 | 客户端大小 | 部署复杂度 | 功能完整性 | 网络依赖 |
|------|------------|------------|------------|----------|
| **本地安装** | 1.2GB | 简单 | 完整 | 无 |
| **远程 Web 服务** | <10MB | 中等 | 95% | 中等 |
| **轻量级客户端** | <5MB | 简单 | 90% | 低 |
| **Docker 容器** | 服务器端 | 复杂 | 完整 | 低 |

## 📋 方案 1: 远程 Web 服务

### 优势
- ✅ 客户端无需安装 PySide6
- ✅ 通过浏览器访问，跨平台兼容
- ✅ 集中管理和维护
- ✅ 支持多用户并发

### 部署步骤

1. **服务器端部署**
```bash
# 在服务器上安装完整环境
git clone <repository>
cd user-feedback-mcp
python -m venv .venv
source .venv/bin/activate
pip install pyside6 fastapi uvicorn websockets

# 启动远程服务器
python remote_server.py
```

2. **客户端配置**
```bash
# 客户端只需轻量级依赖
pip install requests fastmcp

# 设置远程服务器地址
export FEEDBACK_SERVER_URL="http://your-server:8000"

# 启动轻量级客户端
python lightweight_client.py
```

3. **AI 助手配置**
```json
{
  "mcpServers": {
    "user-feedback": {
      "command": "python",
      "args": ["lightweight_client.py"],
      "env": {
        "FEEDBACK_SERVER_URL": "http://your-server:8000"
      }
    }
  }
}
```

## 📋 方案 2: Docker 容器化

### 优势
- ✅ 环境隔离，避免依赖冲突
- ✅ 一键部署，易于扩展
- ✅ 支持负载均衡和高可用
- ✅ 资源使用可控

### 部署步骤

1. **构建镜像**
```bash
# 构建 Docker 镜像
docker build -t feedback-server .

# 或使用 docker-compose
docker-compose build
```

2. **启动服务**
```bash
# 单容器启动
docker run -d -p 8000:8000 \
  -v /path/to/projects:/projects:ro \
  feedback-server

# 或使用 docker-compose
docker-compose up -d
```

3. **客户端连接**
```bash
# 客户端配置
export FEEDBACK_SERVER_URL="http://docker-host:8000"
python lightweight_client.py
```

## 📋 方案 3: 云服务部署

### AWS 部署
```yaml
# docker-compose.aws.yml
version: '3.8'
services:
  feedback-server:
    image: your-registry/feedback-server:latest
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-west-2
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### 使用 AWS ECS 或 EKS
```bash
# 推送镜像到 ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-west-2.amazonaws.com
docker tag feedback-server:latest <account>.dkr.ecr.us-west-2.amazonaws.com/feedback-server:latest
docker push <account>.dkr.ecr.us-west-2.amazonaws.com/feedback-server:latest

# 部署到 ECS
aws ecs create-service --cluster feedback-cluster --service-name feedback-service --task-definition feedback-task
```

## 🔧 配置优化

### 1. 性能优化
```python
# remote_server.py 优化配置
app = FastAPI(
    title="远程用户反馈服务",
    docs_url="/docs" if DEBUG else None,  # 生产环境禁用文档
    redoc_url=None
)

# 启用 gzip 压缩
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 启用 CORS（如果需要）
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 指定允许的域名
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2. 安全配置
```python
# 添加认证中间件
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return credentials.credentials

# 保护 API 端点
@app.post("/api/feedback")
async def create_feedback_session(
    request: FeedbackRequest,
    token: str = Depends(verify_token)
):
    # ... 实现逻辑
```

### 3. 监控和日志
```python
# 添加日志配置
import logging
from fastapi import Request
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.3f}s"
    )
    return response
```

## 📊 成本分析

### 本地部署 vs 远程部署

| 项目 | 本地部署 | 远程部署 |
|------|----------|----------|
| **存储成本** | 1.2GB × N台机器 | 1.2GB × 1台服务器 |
| **网络成本** | 无 | 带宽费用 |
| **维护成本** | 高（每台机器） | 低（集中管理） |
| **扩展成本** | 线性增长 | 几乎不变 |

### 示例计算（10台客户端）
- **本地部署**: 12GB 存储 + 高维护成本
- **远程部署**: 1.2GB 存储 + 网络费用 + 服务器费用

## 🎯 推荐方案

### 小团队（1-5人）
**推荐**: 轻量级客户端 + 单服务器
- 部署简单，成本低
- 维护工作量小

### 中型团队（5-20人）
**推荐**: Docker 容器 + 负载均衡
- 支持并发用户
- 易于扩展和维护

### 大型团队（20+人）
**推荐**: 云服务 + 微服务架构
- 高可用性
- 自动扩展
- 专业运维支持

## 🚀 快速开始

1. **选择部署方案**
2. **配置服务器环境**
3. **部署远程服务**
4. **配置客户端连接**
5. **测试功能完整性**

通过远程部署，您可以将 1.2GB 的客户端安装减少到不到 10MB，同时保持完整的功能体验！
