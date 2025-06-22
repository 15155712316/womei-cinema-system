#!/bin/bash

# MCP (Model Context Protocol) 安装脚本
# 用于安装和配置 @upstash/context7-mcp 服务器

echo "🚀 开始安装 MCP 服务器..."

# 检查 Node.js 是否已安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

# 检查 npm 是否已安装
if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"

# 测试 MCP 服务器是否可以运行
echo "🔍 测试 MCP 服务器..."
if npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
    echo "✅ MCP 服务器安装成功"
else
    echo "❌ MCP 服务器安装失败"
    exit 1
fi

# 创建 Claude Desktop 配置目录
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# 备份现有配置文件（如果存在）
if [ -f "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" ]; then
    echo "📋 备份现有配置文件..."
    cp "$CLAUDE_CONFIG_DIR/claude_desktop_config.json" "$CLAUDE_CONFIG_DIR/claude_desktop_config.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# 复制配置文件
echo "📝 安装 MCP 配置文件..."
cp "claude_desktop_config.json" "$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo "✅ MCP 安装完成！"
echo ""
echo "📋 配置信息："
echo "   - MCP 服务器: @upstash/context7-mcp"
echo "   - 配置文件位置: $CLAUDE_CONFIG_DIR/claude_desktop_config.json"
echo "   - 传输方式: stdio"
echo ""
echo "🔄 请重启 Claude Desktop 应用以加载新的 MCP 服务器"
echo ""
echo "💡 使用说明："
echo "   1. 重启 Claude Desktop"
echo "   2. 在对话中，MCP 服务器将自动可用"
echo "   3. 您可以使用 context7 提供的功能来管理和搜索上下文信息"
echo ""
echo "🔧 如果遇到问题，请检查："
echo "   - Node.js 和 npm 是否正确安装"
echo "   - PATH 环境变量是否包含 /opt/homebrew/bin"
echo "   - Claude Desktop 是否已完全重启"
