# 简化的HAR文件分析脚本

Write-Host "开始分析HAR文件..." -ForegroundColor Green

# 读取HAR文件
try {
    $huanlianFile = Get-ChildItem "*华联*.har" | Select-Object -First 1
    $womeiFile = Get-ChildItem "*沃美*.har" | Select-Object -First 1

    $huanlianContent = Get-Content $huanlianFile.FullName -Raw -Encoding UTF8
    $womeiContent = Get-Content $womeiFile.FullName -Raw -Encoding UTF8
    
    Write-Host "成功读取HAR文件" -ForegroundColor Green
} catch {
    Write-Host "读取HAR文件失败" -ForegroundColor Red
    exit 1
}

# 解析JSON
try {
    $huanlianData = $huanlianContent | ConvertFrom-Json
    $womeiData = $womeiContent | ConvertFrom-Json
    
    Write-Host "成功解析JSON数据" -ForegroundColor Green
} catch {
    Write-Host "解析JSON失败" -ForegroundColor Red
    exit 1
}

# 提取请求信息
$huanlianEntries = $huanlianData.log.entries
$womeiEntries = $womeiData.log.entries

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "HAR文件对比分析报告" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "基本统计信息:" -ForegroundColor Yellow
Write-Host "华联系统总请求数: $($huanlianEntries.Count)"
Write-Host "沃美系统总请求数: $($womeiEntries.Count)"

# 分析域名
Write-Host ""
Write-Host "域名分析:" -ForegroundColor Yellow

# 华联系统域名
$huanlianDomains = @{}
foreach ($entry in $huanlianEntries) {
    $uri = [System.Uri]$entry.request.url
    $domain = $uri.Host
    if ($huanlianDomains.ContainsKey($domain)) {
        $huanlianDomains[$domain]++
    } else {
        $huanlianDomains[$domain] = 1
    }
}

Write-Host ""
Write-Host "华联系统使用的域名:"
$huanlianDomains.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name) ($($_.Value) 个请求)"
}

# 沃美系统域名
$womeiDomains = @{}
foreach ($entry in $womeiEntries) {
    $uri = [System.Uri]$entry.request.url
    $domain = $uri.Host
    if ($womeiDomains.ContainsKey($domain)) {
        $womeiDomains[$domain]++
    } else {
        $womeiDomains[$domain] = 1
    }
}

Write-Host ""
Write-Host "沃美系统使用的域名:"
$womeiDomains.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name) ($($_.Value) 个请求)"
}

# 分析请求方法
Write-Host ""
Write-Host "请求方法统计:" -ForegroundColor Yellow

# 华联系统请求方法
$huanlianMethods = @{}
foreach ($entry in $huanlianEntries) {
    $method = $entry.request.method
    if ($huanlianMethods.ContainsKey($method)) {
        $huanlianMethods[$method]++
    } else {
        $huanlianMethods[$method] = 1
    }
}

Write-Host ""
Write-Host "华联系统:"
$huanlianMethods.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.Value) 次"
}

# 沃美系统请求方法
$womeiMethods = @{}
foreach ($entry in $womeiEntries) {
    $method = $entry.request.method
    if ($womeiMethods.ContainsKey($method)) {
        $womeiMethods[$method]++
    } else {
        $womeiMethods[$method] = 1
    }
}

Write-Host ""
Write-Host "沃美系统:"
$womeiMethods.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.Value) 次"
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "分析完成" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
