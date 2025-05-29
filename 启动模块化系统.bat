@echo off
echo 正在启动模块化影院下单系统...
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python环境，请先安装Python
    pause
    exit /b 1
)

REM 检查必要文件
if not exist "main_modular.py" (
    echo 错误：未找到主程序文件 main_modular.py
    pause
    exit /b 1
)

REM 设置字符编码
chcp 65001 >nul

REM 启动模块化系统
echo 启动模块化影院下单系统 v1.0
echo 基于插件架构的模块化设计
echo.
python main_modular.py

REM 等待用户确认
if errorlevel 1 (
    echo.
    echo 程序异常退出，错误代码：%errorlevel%
)
echo.
echo 程序已退出，按任意键关闭窗口...
pause >nul 