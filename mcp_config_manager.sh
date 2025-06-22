#!/bin/bash

# MCP 配置管理器
# 用于在本地和远程MCP部署之间切换

CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
BACKUP_DIR="./mcp_configs"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 显示帮助信息
show_help() {
    echo "MCP 配置管理器"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -l, --local     切换到本地部署"
    echo "  -r, --remote    切换到远程部署"
    echo "  -s, --status    显示当前配置状态"
    echo "  -b, --backup    备份当前配置"
    echo "  -t, --test      测试MCP服务器连接"
    echo "  -d, --daemon    管理守护进程（启动/停止/状态）"
    echo "  -i, --install   安装稳定性保障（守护进程+监控）"
    echo "  -h, --help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 --local      # 切换到本地部署"
    echo "  $0 --remote     # 切换到远程部署"
    echo "  $0 --status     # 查看当前状态"
}

# 备份当前配置
backup_config() {
    if [ -f "$CONFIG_FILE" ]; then
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="$BACKUP_DIR/claude_config_backup_$timestamp.json"
        cp "$CONFIG_FILE" "$backup_file"
        print_message $GREEN "✅ 配置已备份到: $backup_file"
    else
        print_message $YELLOW "⚠️  配置文件不存在，无需备份"
    fi
}

# 检查当前配置类型
check_config_type() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "none"
        return
    fi
    
    if grep -q '"command": "npx"' "$CONFIG_FILE" && grep -q '@upstash/context7-mcp' "$CONFIG_FILE"; then
        echo "local"
    elif grep -q '"command": "curl"' "$CONFIG_FILE"; then
        echo "remote"
    else
        echo "unknown"
    fi
}

# 显示当前状态
show_status() {
    print_message $BLUE "📋 MCP 配置状态"
    echo "================================"
    
    local config_type=$(check_config_type)
    case $config_type in
        "local")
            print_message $GREEN "当前配置: 本地部署 🏠"
            ;;
        "remote")
            print_message $GREEN "当前配置: 远程部署 🌐"
            ;;
        "unknown")
            print_message $YELLOW "当前配置: 未知类型 ❓"
            ;;
        "none")
            print_message $RED "当前配置: 未找到配置文件 ❌"
            ;;
    esac
    
    echo ""
    echo "配置文件位置: $CONFIG_FILE"
    
    if [ -f "$CONFIG_FILE" ]; then
        echo "配置文件大小: $(wc -c < "$CONFIG_FILE") 字节"
        echo "最后修改时间: $(stat -f "%Sm" "$CONFIG_FILE")"
    fi
    
    echo ""
    echo "备份文件数量: $(ls -1 "$BACKUP_DIR"/claude_config_backup_*.json 2>/dev/null | wc -l)"
}

# 切换到本地配置
switch_to_local() {
    print_message $BLUE "🔄 切换到本地部署..."
    
    # 备份当前配置
    backup_config
    
    # 检查本地依赖
    if ! command -v npx &> /dev/null; then
        print_message $RED "❌ npx 未安装，请先安装 Node.js"
        return 1
    fi
    
    # 测试本地MCP服务器
    print_message $YELLOW "🧪 测试本地MCP服务器..."
    if npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
        print_message $GREEN "✅ 本地MCP服务器可用"
    else
        print_message $RED "❌ 本地MCP服务器不可用"
        return 1
    fi
    
    # 创建本地配置
    cat > "$CONFIG_FILE" << 'EOF'
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": [
        "-y",
        "@upstash/context7-mcp"
      ],
      "env": {
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin",
        "NODE_OPTIONS": "--max-old-space-size=2048"
      }
    }
  }
}
EOF
    
    print_message $GREEN "✅ 已切换到本地部署"
    print_message $YELLOW "🔄 请重启 Claude Desktop 以应用新配置"
}

# 切换到远程配置
switch_to_remote() {
    print_message $BLUE "🔄 切换到远程部署..."
    
    # 获取远程服务器地址
    read -p "请输入远程MCP服务器地址 (例: https://mcp.example.com): " remote_url
    
    if [ -z "$remote_url" ]; then
        print_message $RED "❌ 远程服务器地址不能为空"
        return 1
    fi
    
    # 备份当前配置
    backup_config
    
    # 测试远程连接
    print_message $YELLOW "🧪 测试远程连接..."
    if curl -s -f "$remote_url/health" > /dev/null 2>&1; then
        print_message $GREEN "✅ 远程服务器连接正常"
    else
        print_message $YELLOW "⚠️  无法连接到远程服务器，但仍将创建配置"
    fi
    
    # 询问是否需要认证
    read -p "是否需要API认证? (y/N): " need_auth
    
    if [[ $need_auth =~ ^[Yy]$ ]]; then
        read -p "请输入API Token: " api_token
        auth_header='"Authorization: Bearer '$api_token'",'
    else
        auth_header=""
    fi
    
    # 创建远程配置
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "context7-remote": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        ${auth_header}
        "-d", "@-",
        "$remote_url"
      ],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
EOF
    
    print_message $GREEN "✅ 已切换到远程部署"
    print_message $YELLOW "🔄 请重启 Claude Desktop 以应用新配置"
}

# 测试MCP连接
test_connection() {
    print_message $BLUE "🧪 测试MCP连接..."
    
    local config_type=$(check_config_type)
    
    case $config_type in
        "local")
            print_message $YELLOW "测试本地MCP服务器..."
            if npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
                print_message $GREEN "✅ 本地MCP服务器正常"
            else
                print_message $RED "❌ 本地MCP服务器异常"
            fi
            ;;
        "remote")
            print_message $YELLOW "测试远程MCP服务器..."
            # 从配置文件中提取URL
            local remote_url=$(grep -o 'https\?://[^"]*' "$CONFIG_FILE" | head -1)
            if [ -n "$remote_url" ]; then
                if curl -s -f "$remote_url/health" > /dev/null 2>&1; then
                    print_message $GREEN "✅ 远程MCP服务器正常"
                else
                    print_message $RED "❌ 远程MCP服务器异常"
                fi
            else
                print_message $RED "❌ 无法从配置中提取远程URL"
            fi
            ;;
        *)
            print_message $RED "❌ 未知的配置类型，无法测试"
            ;;
    esac
}

# 管理守护进程
manage_daemon() {
    if [ ! -f "mcp_daemon_manager.sh" ]; then
        print_message $RED "❌ 守护进程管理器不存在，请先安装稳定性保障"
        return 1
    fi

    print_message $BLUE "🔧 MCP 守护进程管理"
    echo "================================"
    echo "1. 启动守护进程"
    echo "2. 停止守护进程"
    echo "3. 重启守护进程"
    echo "4. 查看守护进程状态"
    echo "5. 查看日志"
    echo "0. 返回"
    echo ""

    read -p "请选择操作 (0-5): " choice

    case $choice in
        1)
            ./mcp_daemon_manager.sh start
            ;;
        2)
            ./mcp_daemon_manager.sh stop
            ;;
        3)
            ./mcp_daemon_manager.sh restart
            ;;
        4)
            ./mcp_daemon_manager.sh status
            ;;
        5)
            if [ -f "logs/mcp_daemon.log" ]; then
                print_message $BLUE "📄 最近的日志 (按 Ctrl+C 退出):"
                tail -f logs/mcp_daemon.log
            else
                print_message $YELLOW "⚠️  日志文件不存在"
            fi
            ;;
        0)
            return 0
            ;;
        *)
            print_message $RED "❌ 无效选择"
            ;;
    esac
}

# 安装稳定性保障
install_stability() {
    print_message $BLUE "🚀 安装 MCP 稳定性保障系统..."

    # 检查必要文件是否存在
    local required_files=("mcp_daemon_manager.sh" "本地MCP稳定性保障方案.md")
    local missing_files=()

    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -gt 0 ]; then
        print_message $RED "❌ 缺少必要文件："
        for file in "${missing_files[@]}"; do
            echo "   - $file"
        done
        print_message $YELLOW "💡 请确保所有稳定性保障文件都已下载到当前目录"
        return 1
    fi

    # 设置执行权限
    chmod +x mcp_daemon_manager.sh

    # 创建日志目录
    mkdir -p logs

    print_message $YELLOW "📋 选择安装模式："
    echo "1. 基础模式 - 仅守护进程"
    echo "2. 完整模式 - 守护进程 + 系统服务 + 监控"
    echo "0. 取消"
    echo ""

    read -p "请选择 (0-2): " install_mode

    case $install_mode in
        1)
            # 基础模式
            print_message $BLUE "📦 安装基础守护进程..."
            ./mcp_daemon_manager.sh start

            if [ $? -eq 0 ]; then
                print_message $GREEN "✅ 基础模式安装成功"
                print_message $YELLOW "💡 使用 '$0 --daemon' 管理守护进程"
            else
                print_message $RED "❌ 基础模式安装失败"
                return 1
            fi
            ;;
        2)
            # 完整模式
            print_message $BLUE "📦 安装完整稳定性保障..."

            # 安装系统服务
            ./mcp_daemon_manager.sh install

            if [ $? -eq 0 ]; then
                print_message $GREEN "✅ 完整模式安装成功"
                print_message $BLUE "📋 已启用功能："
                echo "   - 开机自动启动"
                echo "   - 异常自动重启"
                echo "   - 资源监控"
                echo "   - 日志记录"
                echo ""
                print_message $YELLOW "💡 管理命令："
                echo "   查看状态: $0 --daemon"
                echo "   查看日志: tail -f logs/mcp_daemon.log"
            else
                print_message $RED "❌ 完整模式安装失败"
                return 1
            fi
            ;;
        0)
            print_message $YELLOW "⚠️  安装已取消"
            return 0
            ;;
        *)
            print_message $RED "❌ 无效选择"
            return 1
            ;;
    esac

    # 显示安装后状态
    echo ""
    print_message $BLUE "📊 当前状态："
    ./mcp_daemon_manager.sh status
}

# 主函数
main() {
    case $1 in
        -l|--local)
            switch_to_local
            ;;
        -r|--remote)
            switch_to_remote
            ;;
        -s|--status)
            show_status
            ;;
        -b|--backup)
            backup_config
            ;;
        -t|--test)
            test_connection
            ;;
        -d|--daemon)
            manage_daemon
            ;;
        -i|--install)
            install_stability
            ;;
        -h|--help|"")
            show_help
            ;;
        *)
            print_message $RED "❌ 未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
