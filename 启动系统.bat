@echo off
echo.
echo ============================================================
echo   🎬 柴犬影院下单系统 - 模块化版本
echo ============================================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python环境，请先安装Python
    echo.
    pause
    exit /b 1
)

REM 检查主程序文件
if not exist "main.py" (
    echo ❌ 错误：未找到主程序文件 main.py
    echo.
    pause
    exit /b 1
)

REM 设置字符编码
chcp 65001 >nul

REM 启动系统
python main.py

REM 等待用户确认
if errorlevel 1 (
    echo.
    echo ❌ 程序异常退出，错误代码：%errorlevel%
    echo.
)
echo.
echo 程序已退出，按任意键关闭窗口...
pause >nul 