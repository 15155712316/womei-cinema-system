# 工具目录 (tools/)

## 📋 目录说明

本目录包含PyQt5电影票务管理系统的各种开发工具、脚本和实用程序，按功能分类组织。

## 📁 子目录结构

### 🔍 analyzers/ - 分析工具
包含代码分析、项目分析等工具：
- 详细文件用途标注分析器.py - 文件用途分析工具

### 🔧 fixes/ - 修复脚本
包含历史修复脚本（已归档）：
- 各种问题修复的历史脚本
- 主要用于参考和学习

### 💳 payment/ - 支付相关工具
包含支付系统分析和处理工具：
- analyze_member_password_differences.py - 会员密码差异分析
- dynamic_member_password_handler.py - 动态密码处理器

## 📄 根目录工具文件

### 🌐 服务器相关
- **add_to_server.py** - 服务器管理工具（Flask应用）
- **admin_tool.py** - 管理工具（Tkinter GUI）
- **server_api_sample.py** - 服务器API示例
- **server_deployment_guide.py** - 服务器部署指南
- **update_server_machine_code.py** - 服务器机器码更新

### 🏗️ 构建相关
- **build_exe.py** - 可执行文件构建工具
- **secure_build.py** - 安全构建脚本
- **install_dependencies.py** - 依赖安装脚本
- **install_browser_dependencies.py** - 浏览器依赖安装

### 📊 数据分析
- **decode_har_responses.py** - HAR响应解码
- **har_analysis.py** - HAR文件分析
- **manual_har_analysis.py** - 手动HAR分析
- **find_accounts_with_orders.py** - 查找有订单的账号
- **find_valid_order.py** - 查找有效订单

### 🔍 诊断工具
- **diagnose_seat_and_session_issues.py** - 座位和场次问题诊断
- **syntax_checker.py** - 语法检查器

### 🛠️ 实用工具
- **config_encryption.py** - 配置加密工具
- **自动化文件清理脚本.py** - 文件清理自动化
- **项目文件清理.ps1** - PowerShell清理脚本

## 🔗 与其他目录的关联

- **与主程序的关联**：部分工具用于分析和维护主程序
- **与data/的关联**：数据分析工具处理data/目录中的文件
- **与docs/的关联**：分析工具生成的报告保存在docs/reports/中

## 📝 使用说明

### 运行分析工具
```bash
# 运行文件分析
python tools/analyzers/详细文件用途标注分析器.py

# 运行支付分析
python tools/payment/analyze_member_password_differences.py
```

### 使用构建工具
```bash
# 构建可执行文件
python tools/build_exe.py

# 安装依赖
python tools/install_dependencies.py
```

### 数据分析
```bash
# 分析HAR文件
python tools/har_analysis.py

# 查找订单
python tools/find_valid_order.py
```

## ⚠️ 注意事项

1. **运行环境**：确保在正确的Python环境中运行工具
2. **依赖关系**：某些工具可能依赖特定的库或文件
3. **权限要求**：部分工具可能需要管理员权限
4. **备份重要性**：运行修改性工具前请备份重要文件
5. **工具版本**：注意工具的适用版本和兼容性

## 🔄 工具维护

- 定期检查工具的有效性和兼容性
- 更新过时的工具和脚本
- 添加新的实用工具到相应分类
- 保持工具文档的更新
