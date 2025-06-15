# 提取HAR文件中的URL信息

Write-Host "分析华联下单HAR文件..." -ForegroundColor Green

# 读取华联HAR文件并提取URL
$huanlianContent = Get-Content "华联下单_2025_06_08_15_06_36.har" -Raw
$huanlianUrls = [regex]::Matches($huanlianContent, '"url":"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }

Write-Host "华联系统发现的URL ($($huanlianUrls.Count) 个):" -ForegroundColor Yellow
$huanlianUrls | Sort-Object -Unique | ForEach-Object {
    $uri = [System.Uri]$_
    Write-Host "  - $($uri.Host)$($uri.AbsolutePath)"
}

Write-Host "`n分析沃美下单HAR文件..." -ForegroundColor Green

# 读取沃美HAR文件并提取URL
$womeiContent = Get-Content "沃美下单_2025_06_08_15_07_51.har" -Raw
$womeiUrls = [regex]::Matches($womeiContent, '"url":"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }

Write-Host "沃美系统发现的URL ($($womeiUrls.Count) 个):" -ForegroundColor Yellow
$womeiUrls | Sort-Object -Unique | ForEach-Object {
    $uri = [System.Uri]$_
    Write-Host "  - $($uri.Host)$($uri.AbsolutePath)"
}

# 对比域名
Write-Host "`n域名对比分析:" -ForegroundColor Cyan

$huanlianDomains = $huanlianUrls | ForEach-Object { ([System.Uri]$_).Host } | Sort-Object -Unique
$womeiDomains = $womeiUrls | ForEach-Object { ([System.Uri]$_).Host } | Sort-Object -Unique

Write-Host "华联系统使用的域名:"
$huanlianDomains | ForEach-Object { Write-Host "  - $_" }

Write-Host "`n沃美系统使用的域名:"
$womeiDomains | ForEach-Object { Write-Host "  - $_" }

# 找出差异
$commonDomains = $huanlianDomains | Where-Object { $_ -in $womeiDomains }
$huanlianOnly = $huanlianDomains | Where-Object { $_ -notin $womeiDomains }
$womeiOnly = $womeiDomains | Where-Object { $_ -notin $huanlianDomains }

if ($commonDomains) {
    Write-Host "`n共同使用的域名:" -ForegroundColor Green
    $commonDomains | ForEach-Object { Write-Host "  - $_" }
}

if ($huanlianOnly) {
    Write-Host "`n华联独有的域名:" -ForegroundColor Red
    $huanlianOnly | ForEach-Object { Write-Host "  - $_" }
}

if ($womeiOnly) {
    Write-Host "`n沃美独有的域名:" -ForegroundColor Blue
    $womeiOnly | ForEach-Object { Write-Host "  - $_" }
}

Write-Host "`n分析完成!" -ForegroundColor Green
