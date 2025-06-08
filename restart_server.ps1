#!/usr/bin/env powershell
# 乐影系统 - 服务器重启和缓存清理脚本
# 版本: 1.0
# 用途: 解决代码修改后服务器没有变化的问题

Write-Host "🚀 乐影系统服务器重启脚本 v1.0" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Yellow

# 1. 停止所有Python进程
Write-Host "🔍 正在查找Python进程..." -ForegroundColor Cyan
try {
    $pythonProcesses = Get-Process | Where-Object {$_.ProcessName -like "*python*"}
    if ($pythonProcesses) {
        Write-Host "发现 $($pythonProcesses.Count) 个Python进程，正在停止..." -ForegroundColor Yellow
        foreach ($process in $pythonProcesses) {
            Write-Host "  停止进程: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Red
            Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2
        Write-Host "✅ Python进程已停止" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ 没有发现运行中的Python进程" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ 停止进程时出现警告: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 2. 清理Python缓存
Write-Host "`n🧹 正在清理Python缓存..." -ForegroundColor Cyan

# 清理 __pycache__ 目录
$cacheDirectories = Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" -ErrorAction SilentlyContinue
if ($cacheDirectories) {
    Write-Host "发现 $($cacheDirectories.Count) 个缓存目录" -ForegroundColor Yellow
    foreach ($cacheDir in $cacheDirectories) {
        $fullPath = Join-Path -Path (Get-Location) -ChildPath $cacheDir
        Remove-Item -Path $fullPath -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  已删除: $cacheDir" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️ 没有发现__pycache__目录" -ForegroundColor Gray
}

# 清理 .pyc 文件
$pycFiles = Get-ChildItem -Path . -Recurse -Filter "*.pyc" -ErrorAction SilentlyContinue
if ($pycFiles) {
    Write-Host "发现 $($pycFiles.Count) 个.pyc文件" -ForegroundColor Yellow
    foreach ($pycFile in $pycFiles) {
        Remove-Item -Path $pycFile.FullName -Force -ErrorAction SilentlyContinue
        Write-Host "  已删除: $($pycFile.Name)" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️ 没有发现.pyc文件" -ForegroundColor Gray
}

Write-Host "✅ Python缓存清理完成" -ForegroundColor Green

# 3. 检查端口占用
Write-Host "`n🔍 检查端口5000占用情况..." -ForegroundColor Cyan
try {
    $portCheck = netstat -ano | Select-String ":5000"
    if ($portCheck) {
        Write-Host "⚠️ 端口5000仍被占用:" -ForegroundColor Yellow
        $portCheck | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        
        # 尝试释放端口
        $pids = $portCheck | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Unique
        foreach ($pid in $pids) {
            if ($pid -match '^\d+$') {
                Write-Host "  尝试停止进程 PID: $pid" -ForegroundColor Red
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Seconds 2
    } else {
        Write-Host "✅ 端口5000已释放" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ 端口检查出现警告: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. 验证api.py文件
Write-Host "`n📁 验证api.py文件..." -ForegroundColor Cyan
if (Test-Path "api.py") {
    $fileInfo = Get-Item "api.py"
    Write-Host "✅ api.py文件存在" -ForegroundColor Green
    Write-Host "  文件大小: $([math]::Round($fileInfo.Length/1KB, 2)) KB" -ForegroundColor Gray
    Write-Host "  最后修改: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
    
    # 检查文件内容版本
    $content = Get-Content "api.py" -First 10
    $versionLine = $content | Where-Object { $_ -like "*版本:*" }
    if ($versionLine) {
        Write-Host "  文件版本: $($versionLine.Trim())" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ api.py文件不存在！" -ForegroundColor Red
    Write-Host "请确保在正确的目录中运行此脚本" -ForegroundColor Yellow
    exit 1
}

# 5. 重新启动服务器
Write-Host "`n🚀 正在重新启动服务器..." -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow

try {
    # 启动新的Python进程
    Start-Process -FilePath "python" -ArgumentList "api.py" -NoNewWindow
    Write-Host "✅ 服务器启动命令已执行" -ForegroundColor Green
    
    # 等待服务器启动
    Write-Host "⏳ 等待服务器启动..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # 测试服务器连接
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/" -TimeoutSec 10 -ErrorAction Stop
        $jsonResponse = $response.Content | ConvertFrom-Json
        Write-Host "✅ 服务器启动成功！" -ForegroundColor Green
        Write-Host "  服务名称: $($jsonResponse.service)" -ForegroundColor Gray
        Write-Host "  版本: $($jsonResponse.version)" -ForegroundColor Gray
        Write-Host "  状态: $($jsonResponse.status)" -ForegroundColor Gray
        if ($jsonResponse.server_restart_time) {
            Write-Host "  重启时间: $($jsonResponse.server_restart_time)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "⚠️ 服务器可能仍在启动中，请稍后手动检查" -ForegroundColor Yellow
        Write-Host "  访问地址: http://localhost:5000/" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ 启动服务器失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请手动运行: python api.py" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 60 -ForegroundColor Yellow
Write-Host "🎯 重启脚本执行完成！" -ForegroundColor Green
Write-Host "📊 管理后台: http://localhost:5000/admin" -ForegroundColor Cyan
Write-Host "🔄 强制重启API: http://localhost:5000/force_restart" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Yellow

# 询问是否打开管理后台
$openAdmin = Read-Host "`n是否打开管理后台？(y/n)"
if ($openAdmin -eq 'y' -or $openAdmin -eq 'Y') {
    Start-Process "http://localhost:5000/admin"
    Write-Host "✅ 管理后台已在浏览器中打开" -ForegroundColor Green
}

Write-Host "`n按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
