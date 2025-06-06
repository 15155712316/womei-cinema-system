# 数据目录 (data/)

## 📋 目录说明

本目录包含PyQt5电影票务管理系统的各种数据文件，包括配置数据、用户数据、分析数据等。

## 📁 子目录结构

### 🗂️ configs/ - 配置文件
包含系统配置相关的文件：
- 预留给配置文件使用

### 📸 images/ - 图片文件
包含系统生成或使用的图片：
- qrcode_no_auth_2025060239828060.png - 二维码图片示例

### 🌐 har_files/ - HTTP请求记录
包含网络请求记录文件：
- 预留给HAR文件使用

### 🖼️ img/ - 图片资源
包含系统图片资源：
- 系统图标、界面图片等

## 📄 根目录数据文件

### 📊 分析报告数据
- **ui_component_analysis_report.json** - UI组件分析报告数据
- **ui_deep_analysis_report.json** - UI深度分析报告数据

### ⚙️ 配置文件
- **supervisor_api_config.conf** - Supervisor API配置文件

### 🏢 业务数据
- **accounts.json** - 账号数据
- **cinema_info.json** - 影院信息数据
- **config.json** - 系统配置数据
- **login_history.json** - 登录历史数据
- **login_history_backup.json** - 登录历史备份
- **movies.json** - 电影数据
- **orders.json** - 订单数据

## 🔗 与其他目录的关联

- **与主程序的关联**：主程序读取和写入data/目录中的业务数据
- **与tools/的关联**：分析工具处理data/目录中的数据文件
- **与services/的关联**：业务服务层操作data/目录中的数据

## 📝 使用说明

### 数据文件访问
```python
# 读取账号数据
with open('data/accounts.json', 'r', encoding='utf-8') as f:
    accounts = json.load(f)

# 读取影院信息
with open('data/cinema_info.json', 'r', encoding='utf-8') as f:
    cinemas = json.load(f)
```

### 配置文件管理
- 系统配置文件位于data/config.json
- 影院信息配置位于data/cinema_info.json
- 账号配置位于data/accounts.json

### 图片文件管理
- 二维码图片保存在images/目录
- 系统图标保存在img/目录
- 支持PNG、JPG等常见格式

## ⚠️ 注意事项

1. **数据安全**：
   - 账号数据包含敏感信息，注意保护
   - 定期备份重要数据文件
   - 避免直接编辑JSON文件，使用程序接口

2. **文件格式**：
   - JSON文件使用UTF-8编码
   - 图片文件支持常见格式
   - HAR文件为标准HTTP Archive格式

3. **权限管理**：
   - 确保程序有读写data/目录的权限
   - 生产环境中注意文件权限设置

4. **数据一致性**：
   - 修改数据文件后注意数据一致性
   - 重要操作前备份数据文件

## 🔄 数据维护

- 定期清理过期的日志和临时数据
- 备份重要的业务数据
- 监控数据文件大小，避免过度增长
- 保持数据格式的标准化和一致性
