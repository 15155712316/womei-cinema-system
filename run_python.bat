@echo off
REM 设置Python路径并运行程序
set PYTHON_PATH=D:\python3.12\python.exe

echo 🐍 使用Python 3.12运行程序...
echo 📍 Python路径: %PYTHON_PATH%

REM 检查Python是否存在
if not exist "%PYTHON_PATH%" (
    echo ❌ 错误: 未找到Python 3.12，请检查安装路径
    pause
    exit /b 1
)

REM 显示Python版本
echo 📋 Python版本信息:
"%PYTHON_PATH%" --version

echo.
echo 🚀 启动主程序...
echo.

REM 运行主程序
"%PYTHON_PATH%" main_modular.py

echo.
echo 📝 程序执行完成
pause
