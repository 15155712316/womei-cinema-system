@echo off
chcp 65001 >nul
echo ========================================
echo 🎬 乐影系统 - 柴犬影院下单系统
echo ========================================
echo.
echo 📋 最新修复内容:
echo   ✅ 登录历史记忆 - 自动保存/填入手机号
echo   ✅ 券列表错误处理 - 修复账号无券时的崩溃问题
echo   ✅ API异常处理增强 - 提升系统稳定性
echo.
echo 🚀 正在启动程序...
echo.

REM 使用完整Python路径启动，确保依赖正确
D:\Python\python.exe main.py

REM 如果上面的路径不存在，尝试使用系统Python
if errorlevel 1 (
    echo.
    echo ⚠️  使用完整路径启动失败，尝试系统Python...
    python main.py
)

REM 如果还是失败，显示帮助信息
if errorlevel 1 (
    echo.
    echo ❌ 启动失败！请检查以下问题：
    echo.
    echo 1. Python是否已正确安装？
    echo    - 推荐版本：Python 3.10+ 
    echo    - 当前测试版本：Python 3.13.2
    echo.
    echo 2. 依赖包是否已安装？
    echo    - 运行命令：pip install -r requirements.txt
    echo.
    echo 3. Python路径是否正确？
    echo    - 当前使用：D:\Python\python.exe
    echo    - 请根据实际安装路径修改此脚本
    echo.
    echo 💡 手动启动方法：
    echo    1. 打开命令提示符
    echo    2. 切换到项目目录：cd /d "D:\cursor_data\乐影"
    echo    3. 运行：python main.py
    echo.
)

echo.
echo 按任意键退出...
pause >nul 