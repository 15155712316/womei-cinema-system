# MCP (Model Context Protocol) 安装和使用说明

## 🎉 安装完成

您的 MCP 服务器已经成功安装并配置完成！

### 📋 安装摘要

- ✅ **Homebrew**: 已安装 (版本 4.5.7)
- ✅ **Node.js**: 已安装 (版本 v24.2.0)
- ✅ **npm**: 已安装 (版本 11.3.0)
- ✅ **@upstash/context7-mcp**: 已安装并测试通过
- ✅ **Claude Desktop 配置**: 已完成

### 📁 文件位置

- **配置文件**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **安装脚本**: `./install_mcp.sh`
- **测试脚本**: `./test_mcp.sh`

## 🚀 如何使用

### 1. 重启 Claude Desktop

**重要**: 必须完全重启 Claude Desktop 应用才能加载新的 MCP 服务器。

1. 完全退出 Claude Desktop 应用
2. 重新启动 Claude Desktop
3. 等待应用完全加载

### 2. 验证 MCP 服务器加载

重启后，您可以在 Claude Desktop 中验证 MCP 服务器是否正常加载：

- MCP 服务器会在后台自动启动
- 您应该能够使用 context7 提供的功能

### 3. 使用 Context7 功能

Context7 MCP 服务器提供以下功能：

#### 📚 文档检索
- 获取最新的库文档和代码示例
- 支持多种编程语言和框架

#### 🔍 智能搜索
- 语义搜索能力
- 上下文感知的内容检索

#### 💡 代码理解
- 代码分析和解释
- 最佳实践建议

## 🛠️ 配置详情

### MCP 服务器配置

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

### 环境要求

- **操作系统**: macOS
- **Node.js**: v24.2.0 或更高版本
- **npm**: 11.3.0 或更高版本
- **Claude Desktop**: 最新版本

## 🔧 故障排除

### 如果 MCP 服务器无法加载

1. **检查 Claude Desktop 是否完全重启**
   ```bash
   # 确保 Claude Desktop 完全退出后重新启动
   ```

2. **验证 Node.js 和 npm 安装**
   ```bash
   eval "$(/opt/homebrew/bin/brew shellenv)"
   node --version
   npm --version
   ```

3. **测试 MCP 服务器**
   ```bash
   ./test_mcp.sh
   ```

4. **检查配置文件**
   ```bash
   cat "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
   ```

### 常见问题

#### Q: MCP 服务器无法启动
A: 确保 PATH 环境变量包含 `/opt/homebrew/bin`，并且 Node.js 正确安装。

#### Q: Claude Desktop 中看不到 MCP 功能
A: 确保完全重启了 Claude Desktop，并且配置文件格式正确。

#### Q: 权限错误
A: 确保配置文件有正确的读取权限：
```bash
chmod 644 "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

## 📞 获取帮助

如果遇到问题，可以：

1. **重新运行安装脚本**:
   ```bash
   ./install_mcp.sh
   ```

2. **重新运行测试脚本**:
   ```bash
   ./test_mcp.sh
   ```

3. **查看 MCP 服务器帮助**:
   ```bash
   eval "$(/opt/homebrew/bin/brew shellenv)"
   npx -y @upstash/context7-mcp --help
   ```

## 🎯 下一步

现在您可以：

1. ✅ 重启 Claude Desktop
2. ✅ 开始使用 Context7 的强大功能
3. ✅ 享受增强的 AI 助手体验

祝您使用愉快！🎉
