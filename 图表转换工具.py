#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务系统图表转换工具
将Mermaid图表转换为多种格式
"""

import os
import base64
from pathlib import Path

def create_svg_from_mermaid():
    """创建SVG格式的图表（需要安装mermaid-cli）"""
    print("🔄 正在转换Mermaid图表为SVG格式...")

    # 检查是否安装了mermaid-cli
    try:
        import subprocess
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 未安装mermaid-cli，请先安装：")
            print("   npm install -g @mermaid-js/mermaid-cli")
            return False
    except FileNotFoundError:
        print("❌ 未安装mermaid-cli，请先安装：")
        print("   npm install -g @mermaid-js/mermaid-cli")
        return False

    # 转换业务流程图
    try:
        subprocess.run([
            'mmdc',
            '-i', 'PyQt5电影票务系统业务流程图.mmd',
            '-o', 'PyQt5电影票务系统业务流程图.svg',
            '-t', 'default',
            '-b', 'white'
        ], check=True)
        print("✅ 业务流程图已转换为SVG格式")
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换业务流程图失败: {e}")

    # 转换架构图
    try:
        subprocess.run([
            'mmdc',
            '-i', 'PyQt5电影票务系统架构图.mmd',
            '-o', 'PyQt5电影票务系统架构图.svg',
            '-t', 'default',
            '-b', 'white'
        ], check=True)
        print("✅ 系统架构图已转换为SVG格式")
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换系统架构图失败: {e}")

    return True

def create_png_from_mermaid():
    """创建PNG格式的图表（需要安装mermaid-cli）"""
    print("🔄 正在转换Mermaid图表为PNG格式...")

    # 检查是否安装了mermaid-cli
    try:
        import subprocess
        result = subprocess.run(['mmdc', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 未安装mermaid-cli")
            return False
    except FileNotFoundError:
        print("❌ 未安装mermaid-cli")
        return False

    # 转换业务流程图
    try:
        subprocess.run([
            'mmdc',
            '-i', 'PyQt5电影票务系统业务流程图.mmd',
            '-o', 'PyQt5电影票务系统业务流程图.png',
            '-t', 'default',
            '-b', 'white',
            '-w', '1200',
            '-H', '800'
        ], check=True)
        print("✅ 业务流程图已转换为PNG格式")
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换业务流程图失败: {e}")

    # 转换架构图
    try:
        subprocess.run([
            'mmdc',
            '-i', 'PyQt5电影票务系统架构图.mmd',
            '-o', 'PyQt5电影票务系统架构图.png',
            '-t', 'default',
            '-b', 'white',
            '-w', '1200',
            '-H', '800'
        ], check=True)
        print("✅ 系统架构图已转换为PNG格式")
    except subprocess.CalledProcessError as e:
        print(f"❌ 转换系统架构图失败: {e}")

    return True

def create_markdown_with_images():
    """创建包含图表的Markdown文档"""
    print("📝 创建包含图表的Markdown文档...")

    markdown_content = """# PyQt5电影票务管理系统图表

## 📊 业务流程图

以下图表展示了从用户启动系统到完成购票的完整业务流程：

```mermaid
graph TD
    A[系统启动] --> B[显示登录窗口]
    B --> C{用户登录验证}
    C -->|成功| D[显示主窗口]
    C -->|失败| B

    D --> E[自动选择默认影院]
    E --> F[自动选择关联账号]
    F --> G[用户操作界面]

    G --> H[选择影片]
    H --> I[选择日期和场次]
    I --> J[加载座位图]
    J --> K[用户选择座位]
    K --> L[提交订单]

    L --> M{订单创建}
    M -->|成功| N[显示订单详情]
    M -->|失败| O[显示错误信息]
    O --> G

    N --> P[选择优惠券可选]
    P --> Q[一键支付]

    Q --> R{支付处理}
    R -->|需要密码| S[输入会员卡密码]
    S --> T[调用支付API]
    R -->|无需密码| T

    T --> U{支付结果}
    U -->|成功| V[获取取票码]
    U -->|失败| W[显示支付失败]
    W --> N

    V --> X[显示二维码]
    X --> Y[购票完成]

    subgraph "主要模块"
        Z1[账号管理模块]
        Z2[Tab管理模块]
        Z3[座位订单模块]
        Z4[支付系统]
        Z5[会员系统]
    end

    subgraph "API服务"
        A1[认证API]
        A2[影院API]
        A3[订单API]
        A4[支付API]
        A5[会员API]
    end
```

## 🏗️ 系统架构图

以下图表展示了系统的分层架构设计：

```mermaid
graph TB
    subgraph "用户界面层 (UI Layer)"
        UI1[主窗口<br/>ModularCinemaMainWindow]
        UI2[账号管理组件<br/>AccountWidget]
        UI3[Tab管理组件<br/>TabManagerWidget]
        UI4[座位订单组件<br/>SeatOrderWidget]
        UI5[登录窗口<br/>LoginWindow]
    end

    subgraph "业务逻辑层 (Business Layer)"
        BL1[认证服务<br/>AuthService]
        BL2[影院管理<br/>CinemaManager]
        BL3[会员服务<br/>MemberService]
        BL4[订单详情管理<br/>OrderDetailManager]
        BL5[消息管理<br/>MessageManager]
    end

    subgraph "API接口层 (API Layer)"
        API1[订单API<br/>order_api]
        API2[支付API<br/>pay_order]
        API3[影院API<br/>cinema_api]
        API4[会员API<br/>member_api]
        API5[账号API<br/>account_api]
        API6[基础API<br/>api_base]
    end

    subgraph "数据层 (Data Layer)"
        DATA1[账号数据<br/>account_data]
        DATA2[影院数据<br/>cinema_data]
        DATA3[订单数据<br/>order_data]
        DATA4[会员数据<br/>member_data]
    end

    subgraph "工具层 (Utility Layer)"
        UTIL1[信号总线<br/>event_bus]
        UTIL2[UI工具<br/>ui_utils]
        UTIL3[经典组件<br/>classic_components]
    end

    UI1 --> UI2
    UI1 --> UI3
    UI1 --> UI4
    UI1 --> UI5

    UI1 --> BL1
    UI1 --> BL2
    UI1 --> BL3
    UI1 --> BL4
    UI1 --> BL5

    BL1 --> API1
    BL2 --> API3
    BL3 --> API4
    BL4 --> API1
    BL5 --> API6

    API1 --> DATA3
    API2 --> DATA3
    API3 --> DATA2
    API4 --> DATA4
    API5 --> DATA1

    UI1 --> UTIL1
    UI2 --> UTIL3
    UI3 --> UTIL3
    UI4 --> UTIL3
    BL5 --> UTIL2
```

## 📋 使用说明

### 查看图表
1. **GitHub/GitLab**: 支持直接显示Mermaid图表
2. **Typora**: 支持Mermaid图表渲染
3. **VS Code**: 安装Mermaid插件后可预览
4. **在线编辑器**: 访问 [mermaid.live](https://mermaid.live)

### 转换为图片
如果需要转换为PNG/SVG格式，请安装mermaid-cli：
```bash
npm install -g @mermaid-js/mermaid-cli
```

然后运行转换命令：
```bash
# 转换为PNG
mmdc -i PyQt5电影票务系统业务流程图.mmd -o 业务流程图.png

# 转换为SVG
mmdc -i PyQt5电影票务系统架构图.mmd -o 架构图.svg
```
"""

    with open('PyQt5电影票务系统图表文档.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print("✅ Markdown文档已创建: PyQt5电影票务系统图表文档.md")

def main():
    """主函数"""
    print("🎬 PyQt5电影票务系统图表转换工具")
    print("=" * 50)

    print("\n📁 已创建的文件:")
    print("  ✅ PyQt5电影票务系统业务流程图.mmd")
    print("  ✅ PyQt5电影票务系统架构图.mmd")
    print("  ✅ PyQt5电影票务系统图表.html")

    # 创建Markdown文档
    create_markdown_with_images()

    print("\n🔧 可选转换操作:")
    print("  1. 转换为SVG格式 (需要mermaid-cli)")
    print("  2. 转换为PNG格式 (需要mermaid-cli)")
    print("  3. 跳过转换")

    choice = input("\n请选择操作 (1/2/3): ").strip()

    if choice == '1':
        create_svg_from_mermaid()
    elif choice == '2':
        create_png_from_mermaid()
    else:
        print("⏭️ 跳过图片转换")

    print("\n📋 使用建议:")
    print("  🌐 HTML文件: 双击打开，在浏览器中查看交互式图表")
    print("  📝 Markdown文件: 在支持Mermaid的编辑器中查看")
    print("  🔧 .mmd文件: 在 mermaid.live 在线编辑器中编辑")
    print("  🖼️ 图片文件: 可直接插入文档或演示文稿")

if __name__ == "__main__":
    main()