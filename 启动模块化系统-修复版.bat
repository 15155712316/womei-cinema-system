@echo off
chcp 65001 >nul
echo.
echo ========================================================
echo 🎬 柴犬影院下单系统 - 唯一主程序入口
echo ========================================================
echo.
echo 📌 程序：main_modular.py （唯一主程序）
echo 📌 版本：最新修复版
echo.
echo ✅ 已修复问题：
echo    • 场次时间显示 "未知时间" 问题
echo    • 四级联动失效问题  
echo    • 座位图不显示问题
echo    • base_url字段映射问题
echo.
echo 📋 测试账号：15155712316
echo 📋 机器码：自动生成
echo.
echo 🚀 正在启动系统...
echo.

cd /d "%~dp0"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python环境
    echo 请确保已安装Python并添加到系统PATH
    pause
    exit /b 1
)

REM 检查PyQt5
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到PyQt5库
    echo 请运行: pip install PyQt5
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo ✅ PyQt5库检查通过
echo.

echo 🎯 启动主程序...
python main_modular.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ 启动失败！请检查：
    echo    1. Python是否正确安装
    echo    2. 依赖是否安装：pip install -r requirements.txt
    echo    3. 网络连接是否正常
    echo.
) else (
    echo.
    echo ✅ 程序正常退出
)

pause 