@echo off
echo 正在启动模块化系统演示...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

REM 设置字符编码
chcp 65001 >nul

REM 启动演示程序
echo 启动模块化系统演示 v1.0
echo 展示模块化架构和事件总线通信
echo.
python demo_modular.py

REM 等待用户确认
if errorlevel 1 (
    echo.
    echo 程序异常退出，错误代码：%errorlevel%
)
echo.
echo 演示程序已退出，按任意键关闭窗口...
pause >nul 