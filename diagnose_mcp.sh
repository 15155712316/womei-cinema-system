#!/bin/bash

echo "🔍 MCP 服务器诊断工具"
echo "===================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 已安装${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 未安装${NC}"
        return 1
    fi
}

test_mcp_server() {
    local name=$1
    local command=$2
    shift 2
    local args=("$@")
    
    echo -e "\n${BLUE}🧪 测试 $name${NC}"
    echo "命令: $command ${args[*]}"
    
    # 测试命令是否可执行
    timeout 10s $command "${args[@]}" --help > /dev/null 2>&1
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ $name 可正常运行${NC}"
        return 0
    elif [ $exit_code -eq 124 ]; then
        echo -e "${YELLOW}⚠️  $name 响应超时（可能正常）${NC}"
        return 0
    else
        echo -e "${RED}❌ $name 运行失败 (退出码: $exit_code)${NC}"
        return 1
    fi
}

# 1. 检查基础环境
echo -e "\n${BLUE}📋 检查基础环境${NC}"
echo "===================="

check_command "node"
check_command "npm"
check_command "npx"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}Node.js 版本: $NODE_VERSION${NC}"
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}NPM 版本: $NPM_VERSION${NC}"
fi

# 2. 检查配置文件
echo -e "\n${BLUE}📄 检查配置文件${NC}"
echo "===================="

CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ 配置文件存在${NC}"
    
    # 验证 JSON 格式
    if python3 -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ JSON 格式正确${NC}"
    else
        echo -e "${RED}❌ JSON 格式错误${NC}"
    fi
    
    # 显示配置的服务器
    echo -e "\n${BLUE}配置的 MCP 服务器:${NC}"
    python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    for name in config.get('mcpServers', {}):
        print(f'  • {name}')
" 2>/dev/null || echo "无法解析配置文件"
    
else
    echo -e "${RED}❌ 配置文件不存在${NC}"
fi

# 3. 测试各个 MCP 服务器
echo -e "\n${BLUE}🧪 测试 MCP 服务器${NC}"
echo "===================="

# Context 7
test_mcp_server "Context 7" "npx" "-y" "@upstash/context7-mcp@latest"

# Playwright
test_mcp_server "Playwright" "npx" "-y" "@playwright/mcp@latest"

# Sequential Thinking
test_mcp_server "Sequential Thinking" "npx" "-y" "@modelcontextprotocol/server-sequential-thinking@latest"

# User Feedback (本地)
USER_FEEDBACK_PATH="/Users/jiang/data/沃美0617/user-feedback-mcp/remote-mcp-package/dist/cli.js"
if [ -f "$USER_FEEDBACK_PATH" ]; then
    echo -e "\n${BLUE}🧪 测试 User Feedback (本地)${NC}"
    echo "路径: $USER_FEEDBACK_PATH"
    
    if node "$USER_FEEDBACK_PATH" --help > /dev/null 2>&1; then
        echo -e "${GREEN}✅ User Feedback 可正常运行${NC}"
    else
        echo -e "${RED}❌ User Feedback 运行失败${NC}"
    fi
else
    echo -e "\n${RED}❌ User Feedback 文件不存在: $USER_FEEDBACK_PATH${NC}"
fi

# 4. 检查远程服务
echo -e "\n${BLUE}🌐 检查远程服务${NC}"
echo "===================="

if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 远程反馈服务正在运行${NC}"
    HEALTH_INFO=$(curl -s http://localhost:3000/api/health)
    echo "服务信息: $HEALTH_INFO"
else
    echo -e "${RED}❌ 远程反馈服务未运行${NC}"
    echo "请启动服务: cd /Users/jiang/data/沃美0617/user-feedback-mcp/remote-service && node dist/server.js"
fi

# 5. 网络连接测试
echo -e "\n${BLUE}🌐 网络连接测试${NC}"
echo "===================="

# 测试 NPM 注册表连接
if curl -s https://registry.npmjs.org/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ NPM 注册表连接正常${NC}"
else
    echo -e "${RED}❌ NPM 注册表连接失败${NC}"
fi

# 6. 权限检查
echo -e "\n${BLUE}🔐 权限检查${NC}"
echo "===================="

# 检查配置文件权限
if [ -r "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ 配置文件可读${NC}"
else
    echo -e "${RED}❌ 配置文件不可读${NC}"
fi

# 检查 NPX 缓存权限
NPX_CACHE_DIR="$HOME/.npm/_npx"
if [ -d "$NPX_CACHE_DIR" ] && [ -w "$NPX_CACHE_DIR" ]; then
    echo -e "${GREEN}✅ NPX 缓存目录可写${NC}"
else
    echo -e "${YELLOW}⚠️  NPX 缓存目录权限可能有问题${NC}"
fi

# 7. 总结和建议
echo -e "\n${BLUE}📋 诊断总结${NC}"
echo "===================="

echo -e "\n${YELLOW}如果 MCP 服务器仍显示红色状态，请尝试:${NC}"
echo "1. 重启 Claude Desktop"
echo "2. 检查网络连接"
echo "3. 清除 NPX 缓存: npm cache clean --force"
echo "4. 手动测试各个服务器"
echo "5. 查看 Claude Desktop 的日志文件"

echo -e "\n${GREEN}诊断完成！${NC}"
