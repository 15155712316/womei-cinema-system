# PyQt5电影票务管理系统 - 项目文件清理脚本
# PowerShell版本的自动化清理工具

param(
    [switch]$Preview,
    [switch]$NoBackup,
    [switch]$Force
)

# 设置编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 记录日志
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    Write-ColorOutput $logEntry
    Add-Content -Path "cleanup_log.txt" -Value $logEntry -Encoding UTF8
}

# 创建目录结构
function Create-DirectoryStructure {
    Write-Log "开始创建目录结构"
    
    $directories = @(
        "docs", "docs\reports", "docs\diagrams", "docs\guides",
        "tools", "tools\analyzers", "tools\fixes", "tools\payment",
        "tests", "tests\unit_tests", "tests\integration_tests",
        "data", "data\har_files", "data\images", "data\configs",
        "archive", "archive\old_versions", "archive\deprecated"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "创建目录: $dir"
        }
    }
}

# 创建备份
function Create-Backup {
    Write-Log "开始创建备份"
    
    $backupDir = "backup_before_cleanup"
    if (Test-Path $backupDir) {
        Remove-Item -Path $backupDir -Recurse -Force
    }
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # 备份根目录的所有文件
    Get-ChildItem -Path "." -File | ForEach-Object {
        if ($_.Name -ne "cleanup_log.txt") {
            Copy-Item -Path $_.FullName -Destination $backupDir -Force
            Write-Log "备份文件: $($_.Name)"
        }
    }
    
    Write-ColorOutput "✅ 备份完成: $backupDir" "Green"
}

# 移动文件的函数
function Move-FilesWithPattern {
    param(
        [string]$Pattern,
        [string]$Destination,
        [string[]]$KeepInRoot
    )
    
    $moved = 0
    Get-ChildItem -Path "." -File | Where-Object {
        $_.Name -like $Pattern -and $_.Name -notin $KeepInRoot
    } | ForEach-Object {
        try {
            Move-Item -Path $_.FullName -Destination $Destination -Force
            Write-Log "移动文件: $($_.Name) -> $Destination"
            $moved++
        }
        catch {
            Write-Log "移动失败: $($_.Name) - $($_.Exception.Message)" "ERROR"
        }
    }
    
    return $moved
}

# 执行文件移动
function Move-Files {
    Write-Log "开始移动文件"
    
    # 保留在根目录的文件
    $keepInRoot = @(
        "main_modular.py", "main.py", "requirements.txt",
        "CinemaTicketSystem.spec", "build_info.json",
        "README.md", "使用说明.md", "用户使用手册.md",
        "PyQt5电影票务系统功能架构文档.md",
        "一键打包.bat", "api_validation_report.json"
    )
    
    # 移动规则
    $moveRules = @{
        "docs\reports\" = @("*报告.md", "*总结.md", "*分析*.md")
        "docs\diagrams\" = @("*.mmd", "*图表*.html", "*图表*.md")
        "tools\analyzers\" = @("*analyzer*.py", "*分析器*.py")
        "tools\fixes\" = @("fix_*.py", "quick_*.py")
        "tools\payment\" = @("*payment*.py", "analyze_payment_methods.py", "payment_comparison_analysis.py", "payment_integration_code.py", "enhanced_payment_implementation.py")
        "tests\" = @("test_*.py", "check_*.py")
        "data\har_files\" = @("*.har")
        "data\images\" = @("qrcode_*.png", "*.jpg", "*.jpeg", "*.gif")
        "archive\deprecated\" = @("cleanup-deadcode.ps1", "syntax_report.txt", "result.json")
    }
    
    $totalMoved = 0
    foreach ($destination in $moveRules.Keys) {
        foreach ($pattern in $moveRules[$destination]) {
            $moved = Move-FilesWithPattern -Pattern $pattern -Destination $destination -KeepInRoot $keepInRoot
            $totalMoved += $moved
        }
    }
    
    Write-ColorOutput "📁 总共移动了 $totalMoved 个文件" "Cyan"
}

# 删除临时文件
function Remove-TempFiles {
    Write-Log "开始删除临时文件"
    
    $tempPatterns = @("*.tmp", "*.log", "*.cache", "*.pyc")
    $deleted = 0
    
    foreach ($pattern in $tempPatterns) {
        Get-ChildItem -Path "." -Recurse -File -Include $pattern | ForEach-Object {
            try {
                Remove-Item -Path $_.FullName -Force
                Write-Log "删除临时文件: $($_.Name)"
                $deleted++
            }
            catch {
                Write-Log "删除失败: $($_.Name) - $($_.Exception.Message)" "ERROR"
            }
        }
    }
    
    if ($deleted -gt 0) {
        Write-ColorOutput "🗑️ 删除了 $deleted 个临时文件" "Yellow"
    }
}

# 生成清理摘要
function Generate-Summary {
    $summary = @{
        cleanup_time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        remaining_root_files = (Get-ChildItem -Path "." -File).Count
        root_file_list = (Get-ChildItem -Path "." -File | Select-Object -ExpandProperty Name)
        directories_created = @(
            "docs", "tools", "tests", "data", "archive"
        )
    }
    
    $summary | ConvertTo-Json -Depth 3 | Out-File -FilePath "cleanup_summary.json" -Encoding UTF8
    Write-Log "生成清理摘要: cleanup_summary.json"
    
    return $summary
}

# 预览清理操作
function Show-CleanupPreview {
    Write-ColorOutput "🔍 清理操作预览" "Cyan"
    Write-ColorOutput "=" * 40 "Cyan"
    
    Write-ColorOutput "`n📁 将创建的目录:" "Yellow"
    @("docs", "docs\reports", "docs\diagrams", "tools", "tools\analyzers", "tools\fixes", "tests", "data", "archive") | ForEach-Object {
        Write-ColorOutput "  + $_" "Gray"
    }
    
    Write-ColorOutput "`n📋 文件移动预览:" "Yellow"
    
    # 报告文档
    $reports = Get-ChildItem -Path "." -File | Where-Object { $_.Name -like "*报告.md" -or $_.Name -like "*分析*.md" }
    if ($reports) {
        Write-ColorOutput "  📂 docs\reports\ ($($reports.Count) 个文件)" "Gray"
        $reports | Select-Object -First 3 | ForEach-Object { Write-ColorOutput "    - $($_.Name)" "DarkGray" }
    }
    
    # 工具脚本
    $tools = Get-ChildItem -Path "." -File | Where-Object { $_.Name -like "*analyzer*.py" -or $_.Name -like "fix_*.py" }
    if ($tools) {
        Write-ColorOutput "  📂 tools\ ($($tools.Count) 个文件)" "Gray"
        $tools | Select-Object -First 3 | ForEach-Object { Write-ColorOutput "    - $($_.Name)" "DarkGray" }
    }
    
    # 测试脚本
    $tests = Get-ChildItem -Path "." -File | Where-Object { $_.Name -like "test_*.py" }
    if ($tests) {
        Write-ColorOutput "  📂 tests\ ($($tests.Count) 个文件)" "Gray"
        $tests | Select-Object -First 3 | ForEach-Object { Write-ColorOutput "    - $($_.Name)" "DarkGray" }
    }
    
    Write-ColorOutput "`n✅ 保留在根目录的重要文件:" "Green"
    @("main_modular.py", "main.py", "requirements.txt", "README.md") | ForEach-Object {
        if (Test-Path $_) {
            Write-ColorOutput "  ✓ $_" "Green"
        }
    }
    
    # 临时文件
    $tempFiles = Get-ChildItem -Path "." -Recurse -File -Include "*.tmp", "*.log", "*.cache", "*.pyc"
    if ($tempFiles) {
        Write-ColorOutput "`n🗑️ 将删除的临时文件: $($tempFiles.Count) 个" "Red"
    }
}

# 主执行函数
function Start-Cleanup {
    param(
        [bool]$CreateBackup = $true,
        [bool]$Confirm = $true
    )
    
    Write-ColorOutput "🎬 PyQt5电影票务管理系统 - 项目文件清理" "Cyan"
    Write-ColorOutput "=" * 60 "Cyan"
    
    if ($Confirm -and -not $Force) {
        Write-ColorOutput "`n⚠️  警告：此操作将重组项目文件结构" "Yellow"
        Write-ColorOutput "📋 清理内容：" "White"
        Write-ColorOutput "  - 创建新的目录结构" "Gray"
        Write-ColorOutput "  - 移动文件到相应目录" "Gray"
        Write-ColorOutput "  - 删除临时文件" "Gray"
        Write-ColorOutput "  - 保留核心文件在根目录" "Gray"
        
        if ($CreateBackup) {
            Write-ColorOutput "  - 创建备份到: backup_before_cleanup" "Gray"
        }
        
        $response = Read-Host "`n是否继续执行清理？(y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-ColorOutput "❌ 清理操作已取消" "Red"
            return $false
        }
    }
    
    try {
        # 初始化日志
        if (Test-Path "cleanup_log.txt") {
            Remove-Item "cleanup_log.txt" -Force
        }
        
        Write-Log "开始自动化文件清理"
        
        # 创建备份
        if ($CreateBackup) {
            Create-Backup
        }
        
        # 执行清理步骤
        Create-DirectoryStructure
        Remove-TempFiles
        Move-Files
        
        # 生成摘要
        $summary = Generate-Summary
        
        Write-Log "清理完成"
        
        # 显示结果
        Write-ColorOutput "`n✅ 清理完成！" "Green"
        Write-ColorOutput "📁 根目录剩余文件: $($summary.remaining_root_files) 个" "Cyan"
        Write-ColorOutput "📋 详细日志: cleanup_log.txt" "Gray"
        Write-ColorOutput "📊 清理摘要: cleanup_summary.json" "Gray"
        
        if ($CreateBackup) {
            Write-ColorOutput "💾 备份位置: backup_before_cleanup" "Gray"
        }
        
        return $true
        
    }
    catch {
        Write-Log "清理失败: $($_.Exception.Message)" "ERROR"
        Write-ColorOutput "❌ 清理失败: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 主程序逻辑
if ($Preview) {
    Show-CleanupPreview
}
else {
    $createBackup = -not $NoBackup
    $confirm = -not $Force
    Start-Cleanup -CreateBackup $createBackup -Confirm $confirm
}

# 使用说明
if ($args.Count -eq 0 -and -not $Preview) {
    Write-ColorOutput "`n📋 使用说明:" "Yellow"
    Write-ColorOutput "  .\项目文件清理.ps1                    # 交互式清理（创建备份）" "Gray"
    Write-ColorOutput "  .\项目文件清理.ps1 -Preview           # 预览清理操作" "Gray"
    Write-ColorOutput "  .\项目文件清理.ps1 -Force             # 强制清理（创建备份）" "Gray"
    Write-ColorOutput "  .\项目文件清理.ps1 -NoBackup          # 清理但不创建备份" "Gray"
    Write-ColorOutput "  .\项目文件清理.ps1 -Force -NoBackup   # 强制清理且不创建备份" "Gray"
}
