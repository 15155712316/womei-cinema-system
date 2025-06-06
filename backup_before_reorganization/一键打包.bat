@echo off
chcp 65001 >nul
echo ========================================
echo   柴犬影院票务管理系统 - 一键打包工具
echo ========================================
echo.

echo 🚀 开始自动打包流程...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

:: 第一步：安装依赖
echo 📦 第一步：安装打包依赖...
python install_dependencies.py
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo.

:: 第二步：环境检查
echo 🔍 第二步：环境检查...
python pre_build_check.py
if %errorlevel% neq 0 (
    echo ❌ 环境检查失败，请解决上述问题后重试
    pause
    exit /b 1
)
echo.

:: 第三步：执行打包
echo 🔨 第三步：执行打包...
python build_exe.py
if %errorlevel% neq 0 (
    echo ❌ 打包失败
    pause
    exit /b 1
)
echo.

:: 第四步：测试验证
echo 🧪 第四步：测试验证...
python test_packaged_app.py
if %errorlevel% neq 0 (
    echo ⚠️  测试发现问题，但打包已完成
    echo 请检查test_report.json了解详情
) else (
    echo ✅ 所有测试通过
)
echo.

:: 显示结果
echo ========================================
echo 🎉 打包完成！
echo ========================================
echo.
echo 📁 输出文件位置：
echo   - dist\CinemaTicketSystem.exe  (主程序)
echo   - dist\install.bat             (安装脚本)
echo   - dist\                        (完整程序目录)
echo.
echo 📋 使用说明：
echo   1. 将dist目录复制到目标电脑
echo   2. 运行install.bat进行安装
echo   3. 或直接运行CinemaTicketSystem.exe
echo.
echo 📖 详细说明请查看：
echo   - 用户使用手册.md
echo   - 打包部署指南.md
echo.

:: 询问是否打开输出目录
set /p choice="是否打开输出目录？(y/n): "
if /i "%choice%"=="y" (
    explorer dist
)

echo.
echo 按任意键退出...
pause >nul
