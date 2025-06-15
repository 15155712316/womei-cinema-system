# HAR文件分析脚本
# 用于对比华联和沃美下单系统的HTTP请求差异

Write-Host "开始分析HAR文件..." -ForegroundColor Green

# 读取HAR文件
try {
    $huanlianContent = Get-Content "华联下单_2025_06_08_15_06_36.har" -Raw -Encoding UTF8
    $womeiContent = Get-Content "沃美下单_2025_06_08_15_07_51.har" -Raw -Encoding UTF8
    
    Write-Host "成功读取HAR文件" -ForegroundColor Green
} catch {
    Write-Host "读取HAR文件失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 解析JSON
try {
    $huanlianData = $huanlianContent | ConvertFrom-Json
    $womeiData = $womeiContent | ConvertFrom-Json
    
    Write-Host "成功解析JSON数据" -ForegroundColor Green
} catch {
    Write-Host "解析JSON失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 提取请求信息
$huanlianEntries = $huanlianData.log.entries
$womeiEntries = $womeiData.log.entries

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "HAR文件对比分析报告" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`n📊 基本统计信息:" -ForegroundColor Yellow
Write-Host "华联系统总请求数: $($huanlianEntries.Count)"
Write-Host "沃美系统总请求数: $($womeiEntries.Count)"

# 分析域名
Write-Host "`n🌐 域名分析:" -ForegroundColor Yellow

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

Write-Host "`n华联系统使用的域名:"
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

Write-Host "`n沃美系统使用的域名:"
$womeiDomains.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name) ($($_.Value) 个请求)"
}

# 分析请求方法
Write-Host "`n📡 请求方法统计:" -ForegroundColor Yellow

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

Write-Host "`n华联系统:"
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

Write-Host "`n沃美系统:"
$womeiMethods.GetEnumerator() | Sort-Object Name | ForEach-Object {
    Write-Host "  - $($_.Name): $($_.Value) 次"
}

# 分析API请求（过滤静态资源）
Write-Host "`n🛣️ API请求分析:" -ForegroundColor Yellow

$staticExtensions = @('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.ico', '.svg', '.woff', '.ttf', '.webp')

# 华联API请求
$huanlianApiRequests = @()
foreach ($entry in $huanlianEntries) {
    $uri = [System.Uri]$entry.request.url
    $path = $uri.AbsolutePath
    $isStatic = $false
    
    foreach ($ext in $staticExtensions) {
        if ($path.ToLower().EndsWith($ext)) {
            $isStatic = $true
            break
        }
    }
    
    if (-not $isStatic -and $entry.response.content.mimeType -notlike "image/*") {
        $huanlianApiRequests += $entry
    }
}

Write-Host "`n华联系统API请求 ($($huanlianApiRequests.Count) 个):"
foreach ($entry in $huanlianApiRequests) {
    $uri = [System.Uri]$entry.request.url
    $method = $entry.request.method
    $status = $entry.response.status
    Write-Host "  - $method $($uri.Host)$($uri.AbsolutePath) (状态: $status)"
}

# 沃美API请求
$womeiApiRequests = @()
foreach ($entry in $womeiEntries) {
    $uri = [System.Uri]$entry.request.url
    $path = $uri.AbsolutePath
    $isStatic = $false
    
    foreach ($ext in $staticExtensions) {
        if ($path.ToLower().EndsWith($ext)) {
            $isStatic = $true
            break
        }
    }
    
    if (-not $isStatic -and $entry.response.content.mimeType -notlike "image/*") {
        $womeiApiRequests += $entry
    }
}

Write-Host "`n沃美系统API请求 ($($womeiApiRequests.Count) 个):"
foreach ($entry in $womeiApiRequests) {
    $uri = [System.Uri]$entry.request.url
    $method = $entry.request.method
    $status = $entry.response.status
    Write-Host "  - $method $($uri.Host)$($uri.AbsolutePath) (状态: $status)"
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "分析完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
