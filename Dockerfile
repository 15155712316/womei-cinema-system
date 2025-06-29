# 多阶段构建 Dockerfile
# 阶段 1: 构建阶段（包含完整的 PySide6）
FROM python:3.11-slim as builder

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY pyproject.toml uv.lock ./

# 安装 uv
RUN pip install uv

# 创建虚拟环境并安装依赖
RUN uv venv && \
    uv pip install --no-cache-dir pyside6 fastmcp psutil uvicorn

# 阶段 2: 运行阶段（轻量级）
FROM python:3.11-slim as runtime

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /app/.venv /app/.venv

# 复制应用代码
COPY . .

# 设置环境变量
ENV PATH="/app/.venv/bin:$PATH"
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=offscreen

# 创建启动脚本
RUN echo '#!/bin/bash\n\
# 启动虚拟显示服务器\n\
Xvfb :99 -screen 0 1024x768x24 &\n\
\n\
# 启动远程服务器\n\
exec python remote_server.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 启动命令
CMD ["/app/start.sh"]
