@echo off
title Movie System Server Cache Fix

echo.
echo ========================================
echo Movie System Server Cache Fix Script
echo Fix for: Code updated but server shows old version
echo ========================================
echo.

echo [STEP 1] Stopping Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1
timeout /t 3 >nul
echo SUCCESS: Python processes stopped

echo.
echo [STEP 2] Cleaning Python cache...
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo   Deleting: %%d
    rd /s /q "%%d" >nul 2>&1
)
echo Removing .pyc files...
for /r . %%f in (*.pyc) do @if exist "%%f" (
    echo   Deleting: %%f
    del "%%f" >nul 2>&1
)
echo SUCCESS: Python cache cleaned

echo.
echo [STEP 3] Checking port 5000...
netstat -ano | findstr :5000 >nul
if %errorlevel%==0 (
    echo WARNING: Port 5000 is occupied, trying to free...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000') do (
        echo   Killing process PID: %%a
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 2 >nul
    echo SUCCESS: Port freed
) else (
    echo SUCCESS: Port 5000 is free
)

echo.
echo [STEP 4] Verifying api.py file...
if exist api.py (
    echo SUCCESS: api.py file exists
    for %%i in (api.py) do echo   File size: %%~zi bytes
    for %%i in (api.py) do echo   Last modified: %%~ti

    echo Checking file version...
    findstr /C:"版本: 1.5" api.py >nul
    if %errorlevel%==0 (
        echo SUCCESS: File version is 1.5
    ) else (
        echo WARNING: File version may not be 1.5
    )

    findstr /C:"强制重启" api.py >nul
    if %errorlevel%==0 (
        echo SUCCESS: Contains force restart feature
    ) else (
        echo WARNING: Missing force restart feature
    )
) else (
    echo ERROR: api.py file not found!
    echo Please make sure you are in the correct directory
    pause
    exit /b 1
)

echo.
echo [STEP 5] Starting server...
echo ========================================
start /min python api.py
echo SUCCESS: Server start command executed

echo.
echo [STEP 6] Waiting for server to start...
timeout /t 8 >nul

echo.
echo [STEP 7] Testing server connection...
curl -s http://localhost:5000/ >nul 2>&1
if %errorlevel%==0 (
    echo SUCCESS: Server is responding
) else (
    echo WARNING: Server may still be starting
)

echo.
echo ========================================
echo CACHE FIX COMPLETED!
echo ========================================
echo.
echo Next steps:
echo 1. Open admin panel: http://localhost:5000/admin
echo 2. Press Ctrl+F5 in browser to force refresh
echo 3. Look for "Server Management" section with restart button
echo 4. If still old version, use the "Force Restart Server" button
echo.
echo Troubleshooting:
echo - Clear browser cache and cookies
echo - Try incognito/private browsing mode
echo - Check if version shows 1.5 in page title
echo ========================================

echo.
set /p openAdmin=Open admin panel now? (y/n):
if /i "%openAdmin%"=="y" (
    start http://localhost:5000/admin
    echo Admin panel opened in browser
    echo Remember to press Ctrl+F5 to force refresh!
)

echo.
echo Press any key to exit...
pause >nul
