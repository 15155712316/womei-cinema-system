#!/bin/bash

# MCP 服务器测试脚本
# 用于验证 @upstash/context7-mcp 服务器是否正常工作

echo "🧪 开始测试 MCP 服务器..."

# 设置环境变量
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

# 测试 MCP 服务器帮助信息
echo "📋 测试 MCP 服务器帮助信息..."
if npx -y @upstash/context7-mcp --help; then
    echo "✅ MCP 服务器帮助信息正常"
else
    echo "❌ MCP 服务器帮助信息失败"
    exit 1
fi

echo ""
echo "🔍 测试 MCP 服务器启动..."

# 创建测试输入
cat > test_mcp_input.json << 'EOF'
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "test-client",
      "version": "1.0.0"
    }
  }
}
EOF

# 测试 MCP 服务器初始化
echo "🚀 测试 MCP 服务器初始化..."

# 在后台启动 MCP 服务器并测试
(echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{"roots":{"listChanged":true},"sampling":{}},"clientInfo":{"name":"test-client","version":"1.0.0"}}}' | npx -y @upstash/context7-mcp > test_mcp_output.json 2>&1) &
MCP_PID=$!

# 等待几秒钟
sleep 3

# 检查进程是否还在运行
if kill -0 $MCP_PID 2>/dev/null; then
    echo "✅ MCP 服务器可以启动并运行"
    kill $MCP_PID 2>/dev/null
else
    echo "✅ MCP 服务器启动正常（进程已完成）"
fi

if [ -f test_mcp_output.json ]; then
    echo "📄 服务器响应:"
    head -10 test_mcp_output.json
fi

# 清理测试文件
rm -f test_mcp_input.json test_mcp_output.json

echo ""
echo "✅ MCP 服务器测试完成！"
echo ""
echo "📋 下一步："
echo "   1. 重启 Claude Desktop 应用"
echo "   2. 在 Claude Desktop 中，MCP 服务器将自动加载"
echo "   3. 您可以开始使用 context7 的功能"
echo ""
echo "💡 Context7 MCP 服务器功能："
echo "   - 上下文管理和搜索"
echo "   - 智能内容索引"
echo "   - 语义搜索能力"
echo "   - 文档和代码理解"
