# MCP 用户反馈系统使用指南

## 🚀 启动方法

### 方法 1: 直接启动 MCP 服务器
```bash
cd user-feedback-mcp
.venv/bin/python server.py
```

### 方法 2: 使用 stdio 传输模式
```bash
cd user-feedback-mcp
.venv/bin/python -m server
```

## 🔧 配置 AI 助手

### Claude Desktop 配置
在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "user-feedback": {
      "command": "python",
      "args": ["/path/to/user-feedback-mcp/server.py"],
      "cwd": "/path/to/user-feedback-mcp",
      "env": {
        "PATH": "/path/to/user-feedback-mcp/.venv/bin:${PATH}"
      }
    }
  }
}
```

### Cline 配置
在 Cline 设置中添加 MCP 服务器：
- 服务器名称: user-feedback
- 命令: python server.py
- 工作目录: /path/to/user-feedback-mcp

## 📱 用户界面功能区域

### 1. 命令执行区域
- **工作目录显示**: 显示当前命令执行的目录路径
- **命令输入框**: 输入要执行的 shell 命令
- **运行按钮**: 执行命令或停止正在运行的命令
- **自动执行复选框**: 启用后，打开界面时自动执行上次的命令
- **保存配置按钮**: 将当前设置保存到项目目录

### 2. 反馈输入区域
- **反馈文本框**: 输入对 AI 助手的反馈信息
- **提交按钮**: 提交反馈并关闭界面
- **快捷键**: Ctrl+Enter 快速提交反馈

### 3. 控制台日志区域
- **实时日志显示**: 显示命令执行的完整输出
- **等宽字体**: 便于阅读代码和格式化输出
- **自动滚动**: 新日志自动滚动到底部
- **清除按钮**: 清空当前显示的日志

## 🎯 实际使用场景

### 场景 1: 代码测试和验证
```python
# AI 助手调用示例
user_feedback(
    project_directory="/path/to/my-project",
    summary="实现了新的用户认证功能，请测试登录流程"
)
```

用户操作：
1. 在命令框输入: `npm test -- --grep="login"`
2. 查看测试结果
3. 在反馈框输入测试结果和建议
4. 点击提交反馈

### 场景 2: 构建和部署验证
```python
user_feedback(
    project_directory="/path/to/web-app",
    summary="更新了构建配置，请验证生产环境构建"
)
```

用户操作：
1. 输入命令: `npm run build:prod`
2. 检查构建输出和错误
3. 测试生成的文件
4. 提供构建结果反馈

### 场景 3: 性能测试
```python
user_feedback(
    project_directory="/path/to/api-server",
    summary="优化了数据库查询，请测试 API 性能"
)
```

用户操作：
1. 运行性能测试: `ab -n 1000 -c 10 http://localhost:3000/api/users`
2. 查看响应时间和吞吐量
3. 对比优化前后的性能数据
4. 提供性能改进建议

## ⚙️ 高级配置

### 自定义工作目录
```python
# 可以指定任何有效的目录路径
user_feedback(
    project_directory="/Users/username/Documents/my-project",
    summary="请在指定目录中测试新功能"
)
```

### 预设命令
在项目目录创建 `.user-feedback.json` 文件：
```json
{
  "run_command": "npm test && npm run lint",
  "execute_automatically": true
}
```

### 环境变量
系统会自动继承用户的环境变量，包括：
- PATH
- NODE_ENV
- PYTHON_PATH
- 其他自定义环境变量

## 🔍 故障排除

### 常见问题

1. **GUI 无法启动**
   - 检查 PySide6 是否正确安装
   - 确认系统支持图形界面
   - 查看错误日志

2. **命令执行失败**
   - 验证工作目录是否存在
   - 检查命令语法是否正确
   - 确认必要的工具已安装

3. **反馈无法提交**
   - 检查临时文件权限
   - 确认磁盘空间充足
   - 查看进程间通信状态

### 调试模式
启用详细日志：
```bash
PYTHONPATH=. python server.py --log-level DEBUG
```
