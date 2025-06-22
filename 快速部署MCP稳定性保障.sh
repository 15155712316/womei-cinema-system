#!/bin/bash

# MCP 稳定性保障快速部署脚本
# 一键部署本地 MCP 服务器的稳定性保障系统

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo ""
    print_message $BLUE "================================"
    print_message $BLUE "$1"
    print_message $BLUE "================================"
}

# 检查系统要求
check_requirements() {
    print_header "检查系统要求"
    
    local requirements_met=true
    
    # 检查 Node.js
    if command -v node &> /dev/null; then
        local node_version=$(node --version)
        print_message $GREEN "✅ Node.js: $node_version"
    else
        print_message $RED "❌ Node.js 未安装"
        requirements_met=false
    fi
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        local npm_version=$(npm --version)
        print_message $GREEN "✅ npm: v$npm_version"
    else
        print_message $RED "❌ npm 未安装"
        requirements_met=false
    fi
    
    # 检查 MCP 服务器
    if npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
        print_message $GREEN "✅ MCP 服务器可用"
    else
        print_message $YELLOW "⚠️  MCP 服务器需要安装"
        print_message $BLUE "正在安装 MCP 服务器..."
        if npm install -g @upstash/context7-mcp; then
            print_message $GREEN "✅ MCP 服务器安装成功"
        else
            print_message $RED "❌ MCP 服务器安装失败"
            requirements_met=false
        fi
    fi
    
    if [ "$requirements_met" = false ]; then
        print_message $RED "❌ 系统要求不满足，请先安装必要组件"
        exit 1
    fi
    
    print_message $GREEN "✅ 所有系统要求已满足"
}

# 部署稳定性保障
deploy_stability() {
    print_header "部署稳定性保障系统"
    
    # 设置执行权限
    chmod +x *.sh 2>/dev/null
    
    # 创建必要目录
    mkdir -p logs
    
    print_message $YELLOW "📋 请选择部署模式："
    echo ""
    echo "1. 🏠 基础模式"
    echo "   - 守护进程管理"
    echo "   - 自动重启"
    echo "   - 基础日志"
    echo ""
    echo "2. 🚀 完整模式 (推荐)"
    echo "   - 所有基础功能"
    echo "   - 开机自动启动"
    echo "   - 系统服务集成"
    echo "   - 完整监控和告警"
    echo ""
    echo "0. 取消部署"
    echo ""
    
    read -p "请选择部署模式 (0-2): " deploy_mode
    
    case $deploy_mode in
        1)
            deploy_basic_mode
            ;;
        2)
            deploy_full_mode
            ;;
        0)
            print_message $YELLOW "⚠️  部署已取消"
            exit 0
            ;;
        *)
            print_message $RED "❌ 无效选择"
            exit 1
            ;;
    esac
}

# 基础模式部署
deploy_basic_mode() {
    print_message $BLUE "📦 部署基础模式..."
    
    # 启动守护进程
    if ./mcp_daemon_manager.sh start; then
        print_message $GREEN "✅ 基础模式部署成功"
        
        echo ""
        print_message $BLUE "📋 已启用功能："
        echo "   - MCP 守护进程"
        echo "   - 异常自动重启"
        echo "   - 基础日志记录"
        
        echo ""
        print_message $YELLOW "💡 管理命令："
        echo "   查看状态: ./mcp_config_manager.sh --daemon"
        echo "   重启服务: ./mcp_daemon_manager.sh restart"
        echo "   查看日志: tail -f logs/mcp_daemon.log"
    else
        print_message $RED "❌ 基础模式部署失败"
        exit 1
    fi
}

# 完整模式部署
deploy_full_mode() {
    print_message $BLUE "📦 部署完整模式..."
    
    # 安装系统服务
    if ./mcp_daemon_manager.sh install; then
        print_message $GREEN "✅ 完整模式部署成功"
        
        echo ""
        print_message $BLUE "📋 已启用功能："
        echo "   - MCP 守护进程"
        echo "   - 开机自动启动"
        echo "   - 异常自动重启"
        echo "   - 系统服务集成"
        echo "   - 完整日志记录"
        echo "   - 资源监控"
        
        echo ""
        print_message $YELLOW "💡 管理命令："
        echo "   查看状态: ./mcp_config_manager.sh --daemon"
        echo "   管理服务: launchctl list | grep com.mcp.daemon"
        echo "   查看日志: tail -f logs/mcp_daemon.log"
        echo "   卸载服务: ./mcp_daemon_manager.sh uninstall"
    else
        print_message $RED "❌ 完整模式部署失败"
        exit 1
    fi
}

# 验证部署
verify_deployment() {
    print_header "验证部署结果"
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if ./mcp_daemon_manager.sh status > /dev/null 2>&1; then
        print_message $GREEN "✅ MCP 守护进程运行正常"
    else
        print_message $RED "❌ MCP 守护进程异常"
        return 1
    fi
    
    # 检查 MCP 服务器响应
    if npx -y @upstash/context7-mcp --help > /dev/null 2>&1; then
        print_message $GREEN "✅ MCP 服务器响应正常"
    else
        print_message $RED "❌ MCP 服务器无响应"
        return 1
    fi
    
    # 检查 Claude Desktop 配置
    local config_file="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
    if [ -f "$config_file" ]; then
        print_message $GREEN "✅ Claude Desktop 配置文件存在"
    else
        print_message $YELLOW "⚠️  Claude Desktop 配置文件不存在"
        print_message $BLUE "💡 使用以下命令配置："
        echo "   ./mcp_config_manager.sh --local"
    fi
    
    print_message $GREEN "✅ 部署验证完成"
}

# 显示使用指南
show_usage_guide() {
    print_header "使用指南"
    
    echo "🎯 MCP 稳定性保障系统已成功部署！"
    echo ""
    echo "📋 常用管理命令："
    echo ""
    echo "   配置管理："
    echo "   ./mcp_config_manager.sh --status    # 查看配置状态"
    echo "   ./mcp_config_manager.sh --daemon    # 管理守护进程"
    echo "   ./mcp_config_manager.sh --local     # 切换到本地部署"
    echo ""
    echo "   守护进程管理："
    echo "   ./mcp_daemon_manager.sh status      # 查看运行状态"
    echo "   ./mcp_daemon_manager.sh restart     # 重启服务"
    echo "   ./mcp_daemon_manager.sh cleanup     # 清理日志"
    echo ""
    echo "   日志查看："
    echo "   tail -f logs/mcp_daemon.log         # 实时日志"
    echo "   cat logs/mcp_health.log             # 健康检查日志"
    echo ""
    echo "🔧 下一步操作："
    echo ""
    echo "1. 确保 Claude Desktop 配置正确："
    echo "   ./mcp_config_manager.sh --local"
    echo ""
    echo "2. 重启 Claude Desktop 应用"
    echo ""
    echo "3. 验证 MCP 功能是否正常工作"
    echo ""
    print_message $GREEN "🎉 享受稳定的 MCP 服务！"
}

# 主函数
main() {
    print_message $BLUE "🚀 MCP 稳定性保障快速部署工具"
    print_message $BLUE "================================"
    
    # 检查系统要求
    check_requirements
    
    # 部署稳定性保障
    deploy_stability
    
    # 验证部署
    if verify_deployment; then
        # 显示使用指南
        show_usage_guide
    else
        print_message $RED "❌ 部署验证失败，请检查错误信息"
        exit 1
    fi
}

# 运行主函数
main "$@"
