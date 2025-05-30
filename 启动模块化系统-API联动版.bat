@echo off
chcp 65001 >nul
title 柴犬影院下单系统 - 模块化版本(API联动版)

echo.
echo ========================================
echo   🎬 柴犬影院下单系统 - 模块化版本
echo   📅 版本: v3.1 (API联动版)
echo   🔧 新功能: 出票Tab真实数据四级联动
echo   📝 更新日期: 2024-12-27
echo ========================================
echo.

echo 🚀 正在启动模块化系统(API联动版)...
echo.

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

echo 🎯 启动主程序(API联动版)...
echo 📋 新功能说明:
echo   - 影院数据从本地JSON文件加载
echo   - 影片数据通过真实API获取
echo   - 支持影院→影片→日期→场次四级联动
echo   - 完整的订单创建流程
echo.

python main_modular.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错
    echo 请检查错误信息并联系技术支持
    pause
) else (
    echo.
    echo ✅ 程序正常退出
)

pause 