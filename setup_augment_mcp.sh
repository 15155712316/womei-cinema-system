#!/bin/bash

echo "🚀 为 Augment Agent 配置 MCP 服务器"
echo "=================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目目录
PROJECT_DIR="/Users/jiang/data/沃美0617/user-feedback-mcp"
AUGMENT_CONFIG_DIR="$HOME/.config/augment"

echo -e "\n${BLUE}📋 步骤 1: 检查环境${NC}"
echo "=================================="

# 检查 Python 环境
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 检查 Node.js 环境
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js 未安装${NC}"
    exit 1
fi

# 检查 FastMCP
if python3 -c "import fastmcp" 2>/dev/null; then
    echo -e "${GREEN}✅ FastMCP 已安装${NC}"
else
    echo -e "${YELLOW}⚠️  FastMCP 未安装，正在安装...${NC}"
    cd "$PROJECT_DIR"
    source .venv/bin/activate
    pip install fastmcp
fi

echo -e "\n${BLUE}📋 步骤 2: 创建 Augment 配置目录${NC}"
echo "=================================="

# 创建 Augment 配置目录
mkdir -p "$AUGMENT_CONFIG_DIR"
echo -e "${GREEN}✅ 配置目录: $AUGMENT_CONFIG_DIR${NC}"

echo -e "\n${BLUE}📋 步骤 3: 复制配置文件${NC}"
echo "=================================="

# 复制 MCP 配置文件
cp "$PROJECT_DIR/augment_mcp_settings.json" "$AUGMENT_CONFIG_DIR/mcp_settings.json"
echo -e "${GREEN}✅ MCP 配置文件已复制${NC}"

# 复制 Python MCP 服务器
cp "$PROJECT_DIR/augment_mcp_config.py" "$AUGMENT_CONFIG_DIR/mcp_server.py"
chmod +x "$AUGMENT_CONFIG_DIR/mcp_server.py"
echo -e "${GREEN}✅ Python MCP 服务器已复制${NC}"

echo -e "\n${BLUE}📋 步骤 4: 测试 MCP 服务器${NC}"
echo "=================================="

# 测试 Context 7
echo -e "${BLUE}🧪 测试 Context 7...${NC}"
if timeout 10s npx -y @upstash/context7-mcp@latest --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Context 7 可用${NC}"
else
    echo -e "${RED}❌ Context 7 测试失败${NC}"
fi

# 测试 Playwright
echo -e "${BLUE}🧪 测试 Playwright...${NC}"
if timeout 10s npx -y @playwright/mcp@latest --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Playwright 可用${NC}"
else
    echo -e "${RED}❌ Playwright 测试失败${NC}"
fi

# 测试 Sequential Thinking
echo -e "${BLUE}🧪 测试 Sequential Thinking...${NC}"
if timeout 10s npx -y @modelcontextprotocol/server-sequential-thinking@latest --help > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Sequential Thinking 可用${NC}"
else
    echo -e "${RED}❌ Sequential Thinking 测试失败${NC}"
fi

# 测试 User Feedback 服务
echo -e "${BLUE}🧪 测试 User Feedback 服务...${NC}"
if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ User Feedback 服务正在运行${NC}"
else
    echo -e "${YELLOW}⚠️  User Feedback 服务未运行，正在启动...${NC}"
    cd "$PROJECT_DIR/remote-service"
    nohup node dist/server.js > /tmp/feedback-service.log 2>&1 &
    sleep 3
    if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ User Feedback 服务已启动${NC}"
    else
        echo -e "${RED}❌ User Feedback 服务启动失败${NC}"
    fi
fi

echo -e "\n${BLUE}📋 步骤 5: 创建启动脚本${NC}"
echo "=================================="

# 创建启动脚本
cat > "$AUGMENT_CONFIG_DIR/start_mcp.sh" << 'EOF'
#!/bin/bash

echo "🚀 启动 Augment Agent MCP 服务"

# 启动 User Feedback 远程服务
USER_FEEDBACK_DIR="/Users/jiang/data/沃美0617/user-feedback-mcp/remote-service"
if [ -d "$USER_FEEDBACK_DIR" ]; then
    cd "$USER_FEEDBACK_DIR"
    if ! curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
        echo "启动 User Feedback 服务..."
        nohup node dist/server.js > /tmp/feedback-service.log 2>&1 &
        sleep 3
    fi
    echo "✅ User Feedback 服务状态检查完成"
fi

# 启动 Python MCP 服务器
echo "启动 Python MCP 服务器..."
cd "$HOME/.config/augment"
python3 mcp_server.py
EOF

chmod +x "$AUGMENT_CONFIG_DIR/start_mcp.sh"
echo -e "${GREEN}✅ 启动脚本已创建: $AUGMENT_CONFIG_DIR/start_mcp.sh${NC}"

echo -e "\n${BLUE}📋 步骤 6: 创建 VSCode 配置${NC}"
echo "=================================="

# 创建 VSCode 工作区配置
VSCODE_CONFIG_DIR="$PROJECT_DIR/.vscode"
mkdir -p "$VSCODE_CONFIG_DIR"

cat > "$VSCODE_CONFIG_DIR/settings.json" << EOF
{
  "augment.mcp.enabled": true,
  "augment.mcp.configPath": "$AUGMENT_CONFIG_DIR/mcp_settings.json",
  "augment.mcp.autoStart": true,
  "augment.mcp.servers": {
    "context7": {
      "enabled": true,
      "autoApprove": ["search", "query"]
    },
    "playwright": {
      "enabled": true,
      "autoApprove": ["navigate", "screenshot"]
    },
    "sequential-thinking": {
      "enabled": true,
      "autoApprove": ["think", "analyze"]
    },
    "user-feedback": {
      "enabled": true,
      "autoApprove": ["user_feedback"]
    }
  }
}
EOF

echo -e "${GREEN}✅ VSCode 配置已创建${NC}"

echo -e "\n${GREEN}🎉 Augment Agent MCP 配置完成！${NC}"
echo "=================================="

echo -e "\n${BLUE}📋 使用方法:${NC}"
echo "1. 在 VSCode 中打开项目"
echo "2. 确保 Augment Agent 插件已安装"
echo "3. 重启 VSCode 或重新加载窗口"
echo "4. 使用以下命令测试:"
echo "   - 'context7_search' - 向量搜索"
echo "   - 'playwright_automation' - 浏览器自动化"
echo "   - 'sequential_thinking' - 结构化思维"
echo "   - 'user_feedback' - 用户反馈系统"

echo -e "\n${BLUE}📋 配置文件位置:${NC}"
echo "- MCP 配置: $AUGMENT_CONFIG_DIR/mcp_settings.json"
echo "- Python 服务器: $AUGMENT_CONFIG_DIR/mcp_server.py"
echo "- 启动脚本: $AUGMENT_CONFIG_DIR/start_mcp.sh"
echo "- VSCode 配置: $VSCODE_CONFIG_DIR/settings.json"

echo -e "\n${YELLOW}💡 提示:${NC}"
echo "如果遇到问题，请运行: $AUGMENT_CONFIG_DIR/start_mcp.sh"
