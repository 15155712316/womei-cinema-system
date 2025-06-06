#!/usr/bin/env powershell
# -*- coding: utf-8 -*-
# PyQt5电影票务系统死代码清理脚本

param(
    [switch]$Force,  # 强制删除，不询问确认
    [switch]$DryRun  # 仅显示将要删除的文件，不实际删除
)

Write-Host "🎬 PyQt5电影票务系统 - 死代码清理工具" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 统计变量
$deletedFiles = 0
$deletedSize = 0

function Remove-SafeItem {
    param(
        [string]$Path,
        [string]$Description = "",
        [switch]$Recurse = $false
    )
    
    if (Test-Path $Path) {
        $item = Get-Item $Path
        $size = if ($item.PSIsContainer) { 
            (Get-ChildItem $Path -Recurse | Measure-Object -Property Length -Sum).Sum 
        } else { 
            $item.Length 
        }
        $sizeKB = [math]::Round($size / 1KB, 2)
        
        if ($DryRun) {
            Write-Host "🔍 [模拟] 将删除: $Path (${sizeKB}KB) - $Description" -ForegroundColor Yellow
            return
        }
        
        if (-not $Force) {
            Write-Host "📋 发现: $Path (${sizeKB}KB) - $Description" -ForegroundColor Cyan
            $confirm = Read-Host "是否删除? (y/N)"
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "⏭️  跳过: $Path" -ForegroundColor Yellow
                return
            }
        }
        
        try {
            if ($Recurse) {
                Remove-Item -Path $Path -Recurse -Force
            } else {
                Remove-Item -Path $Path -Force
            }
            Write-Host "✅ 已删除: $Path (${sizeKB}KB)" -ForegroundColor Green
            $script:deletedFiles++
            $script:deletedSize += $size
        } catch {
            Write-Host "❌ 删除失败: $Path - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "📋 不存在: $Path" -ForegroundColor Gray
    }
}

# 第一阶段：构建产物清理
Write-Host "`n🧹 第一阶段：清理构建产物和缓存" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

Remove-SafeItem -Path "dist" -Description "PyInstaller构建产物" -Recurse
Remove-SafeItem -Path "build" -Description "构建临时文件" -Recurse

# 清理Python缓存
Get-ChildItem -Path . -Name "__pycache__" -Recurse | ForEach-Object {
    Remove-SafeItem -Path $_ -Description "Python缓存目录" -Recurse
}

# 第二阶段：诊断脚本清理
Write-Host "`n🧹 第二阶段：清理开发诊断脚本" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

$diagnosticFiles = @(
    @{Path="diagnose_main_environment.py"; Desc="主程序环境诊断脚本"},
    @{Path="diagnose_qrcode_environment.py"; Desc="二维码环境诊断脚本"},
    @{Path="main_refactored_clean.py"; Desc="重构版本清理启动脚本"},
    @{Path="pre_build_check.py"; Desc="构建前检查脚本"}
)

foreach ($file in $diagnosticFiles) {
    Remove-SafeItem -Path $file.Path -Description $file.Desc
}

# 第三阶段：tkinter遗留文件清理
Write-Host "`n🧹 第三阶段：清理tkinter遗留文件" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

$tkinterFiles = @(
    @{Path="ui\main_window.py"; Desc="tkinter主窗口实现 (2619行)"},
    @{Path="ui\account_list_panel.py"; Desc="tkinter账号列表面板"},
    @{Path="ui\cinema_select_panel.py"; Desc="tkinter影院选择面板"},
    @{Path="ui\seat_map_panel.py"; Desc="tkinter座位图面板"}
)

foreach ($file in $tkinterFiles) {
    Remove-SafeItem -Path $file.Path -Description $file.Desc
}

# 第四阶段：重复实现文件（需要确认）
if (-not $DryRun) {
    Write-Host "`n🧹 第四阶段：检查重复实现文件" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Green
    
    $duplicateFiles = @(
        @{Path="ui\main_window_pyqt5.py"; Desc="旧版PyQt5主窗口实现"},
        @{Path="ui\main_window_modern.py"; Desc="现代化PyQt5主窗口实现"}
    )
    
    Write-Host "⚠️  以下文件可能是重复实现，需要手动确认：" -ForegroundColor Yellow
    foreach ($file in $duplicateFiles) {
        if (Test-Path $file.Path) {
            $fileInfo = Get-Item $file.Path
            $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
            Write-Host "   📋 $($file.Path) (${sizeKB}KB) - $($file.Desc)" -ForegroundColor Cyan
        }
    }
    Write-Host "   💡 建议：手动检查这些文件是否仍在使用中" -ForegroundColor Yellow
}

# 统计结果
Write-Host "`n📊 清理统计" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan
Write-Host "删除文件数量: $deletedFiles" -ForegroundColor Green
Write-Host "释放空间: $([math]::Round($deletedSize / 1MB, 2)) MB" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`n💡 这是模拟运行，没有实际删除文件" -ForegroundColor Yellow
    Write-Host "💡 要实际执行，请运行: .\清理死代码.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ 死代码清理完成！" -ForegroundColor Green
    Write-Host "💡 建议运行测试确认系统正常：python main_modular.py" -ForegroundColor Yellow
}
