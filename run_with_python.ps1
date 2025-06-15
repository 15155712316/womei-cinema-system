# PowerShell脚本：设置Python环境并运行程序

Write-Host "🐍 配置Python 3.12环境..." -ForegroundColor Yellow

# 设置Python路径
$pythonPath = "D:\python3.12\python.exe"

# 检查Python是否存在
if (Test-Path $pythonPath) {
    Write-Host "✅ 找到Python 3.12: $pythonPath" -ForegroundColor Green
    
    # 显示Python版本
    Write-Host "📋 Python版本信息:" -ForegroundColor Cyan
    & $pythonPath --version
    
    # 设置别名（仅当前会话有效）
    Set-Alias python $pythonPath
    Write-Host "✅ 已设置python别名" -ForegroundColor Green
    
    Write-Host "`n🚀 启动主程序..." -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Gray
    
    # 运行主程序
    & python main_modular.py
    
    Write-Host "=" * 50 -ForegroundColor Gray
    Write-Host "📝 程序执行完成" -ForegroundColor Green
    
} else {
    Write-Host "❌ 错误: 未找到Python 3.12" -ForegroundColor Red
    Write-Host "请检查Python是否安装在: $pythonPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n💡 提示: 如果需要在其他PowerShell会话中使用python命令，请执行:" -ForegroundColor Cyan
Write-Host "Set-Alias python '$pythonPath'" -ForegroundColor White
