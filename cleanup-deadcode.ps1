# PyQt5 Cinema Ticket System - Dead Code Cleanup Script

param(
    [switch]$Force,  # Force delete without confirmation
    [switch]$DryRun  # Show what would be deleted without actually deleting
)

Write-Host "PyQt5 Cinema Ticket System - Dead Code Cleanup Tool" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Statistics
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
            Write-Host "[SIMULATE] Would delete: $Path ($sizeKB KB) - $Description" -ForegroundColor Yellow
            return
        }
        
        if (-not $Force) {
            Write-Host "Found: $Path ($sizeKB KB) - $Description" -ForegroundColor Cyan
            $confirm = Read-Host "Delete this item? (y/N)"
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "Skipped: $Path" -ForegroundColor Yellow
                return
            }
        }
        
        try {
            if ($Recurse) {
                Remove-Item -Path $Path -Recurse -Force
            } else {
                Remove-Item -Path $Path -Force
            }
            Write-Host "Deleted: $Path ($sizeKB KB)" -ForegroundColor Green
            $script:deletedFiles++
            $script:deletedSize += $size
        } catch {
            Write-Host "Failed to delete: $Path - $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "Not found: $Path" -ForegroundColor Gray
    }
}

# Stage 1: Build artifacts cleanup
Write-Host "`nStage 1: Cleaning build artifacts and cache" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

Remove-SafeItem -Path "dist" -Description "PyInstaller build output" -Recurse
Remove-SafeItem -Path "build" -Description "Build temporary files" -Recurse

# Clean Python cache
Get-ChildItem -Path . -Name "__pycache__" -Recurse | ForEach-Object {
    Remove-SafeItem -Path $_ -Description "Python cache directory" -Recurse
}

# Stage 2: Diagnostic scripts cleanup
Write-Host "`nStage 2: Cleaning diagnostic scripts" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

$diagnosticFiles = @(
    @{Path="diagnose_main_environment.py"; Desc="Main environment diagnostic script"},
    @{Path="diagnose_qrcode_environment.py"; Desc="QRCode environment diagnostic script"},
    @{Path="main_refactored_clean.py"; Desc="Refactored clean startup script"},
    @{Path="pre_build_check.py"; Desc="Pre-build check script"}
)

foreach ($file in $diagnosticFiles) {
    Remove-SafeItem -Path $file.Path -Description $file.Desc
}

# Stage 3: tkinter legacy files cleanup
Write-Host "`nStage 3: Cleaning tkinter legacy files" -ForegroundColor Green
Write-Host "-" * 40 -ForegroundColor Green

$tkinterFiles = @(
    @{Path="ui\main_window.py"; Desc="tkinter main window implementation (2619 lines)"},
    @{Path="ui\account_list_panel.py"; Desc="tkinter account list panel"},
    @{Path="ui\cinema_select_panel.py"; Desc="tkinter cinema selection panel"},
    @{Path="ui\seat_map_panel.py"; Desc="tkinter seat map panel"}
)

foreach ($file in $tkinterFiles) {
    Remove-SafeItem -Path $file.Path -Description $file.Desc
}

# Stage 4: Check duplicate implementations
if (-not $DryRun) {
    Write-Host "`nStage 4: Checking duplicate implementation files" -ForegroundColor Green
    Write-Host "-" * 40 -ForegroundColor Green
    
    $duplicateFiles = @(
        @{Path="ui\main_window_pyqt5.py"; Desc="Old PyQt5 main window implementation"},
        @{Path="ui\main_window_modern.py"; Desc="Modern PyQt5 main window implementation"}
    )
    
    Write-Host "WARNING: The following files may be duplicate implementations:" -ForegroundColor Yellow
    foreach ($file in $duplicateFiles) {
        if (Test-Path $file.Path) {
            $fileInfo = Get-Item $file.Path
            $sizeKB = [math]::Round($fileInfo.Length / 1KB, 2)
            Write-Host "   $($file.Path) ($sizeKB KB) - $($file.Desc)" -ForegroundColor Cyan
        }
    }
    Write-Host "   Suggestion: Manually check if these files are still in use" -ForegroundColor Yellow
}

# Statistics
Write-Host "`nCleanup Statistics" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan
Write-Host "Files deleted: $deletedFiles" -ForegroundColor Green
Write-Host "Space freed: $([math]::Round($deletedSize / 1MB, 2)) MB" -ForegroundColor Green

if ($DryRun) {
    Write-Host "`nThis was a simulation run, no files were actually deleted" -ForegroundColor Yellow
    Write-Host "To actually execute, run: .\cleanup-deadcode.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`nDead code cleanup completed!" -ForegroundColor Green
    Write-Host "Suggestion: Run tests to confirm system works: python main_modular.py" -ForegroundColor Yellow
}
