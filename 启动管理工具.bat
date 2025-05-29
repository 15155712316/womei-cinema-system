@echo off
title 乐影系统管理工具
color 0B
echo.
echo ================================================
echo           乐影系统管理工具 v1.0
echo ================================================
echo.
echo 正在启动管理工具...
echo.

rem 切换到脚本所在目录
cd /d "%~dp0"

rem 使用 Python 启动管理工具
"D:\Python\python.exe" admin_tool.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 管理工具启动失败，错误代码: %errorlevel%
    echo.
    echo 可能的解决方案:
    echo 1. 检查 Python 路径是否正确 (当前: D:\Python\python.exe)
    echo 2. 确保已安装所需依赖: pip install requests tkinter
    echo 3. 检查 services 目录下的模块文件是否完整
    echo.
    pause
) else (
    echo.
    echo ✅ 管理工具已正常关闭
    pause
) 