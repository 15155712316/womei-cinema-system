#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统打包脚本
使用PyInstaller创建独立可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查打包依赖"""
    print("🔍 检查打包依赖...")

    # 修复：使用正确的导入名称映射
    required_packages = {
        'PyInstaller': 'PyInstaller',
        'PyQt5': 'PyQt5.QtCore',
        'requests': 'requests',
        'Pillow': 'PIL',
        'pywin32': 'win32api'
    }

    missing_packages = []

    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name} - 已安装")
        except ImportError:
            missing_packages.append(package_name)
            print(f"❌ {package_name} - 未安装")

    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    print("✅ 所有依赖包已安装")
    return True

def clean_build_dirs():
    """清理构建目录"""
    print("\n🧹 清理构建目录...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ 已删除 {dir_name}")
            except PermissionError:
                print(f"⚠️  无法删除 {dir_name} (权限不足，可能有文件正在使用)")
    
    # 清理spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"✅ 已删除 {spec_file}")

def create_spec_file():
    """创建PyInstaller spec文件"""
    print("\n📝 创建PyInstaller配置文件...")
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 数据文件和资源文件
datas = [
    ('data', 'data'),
    ('ui', 'ui'),
    ('services', 'services'),
    ('utils', 'utils'),
    ('controllers', 'controllers'),
    ('views', 'views'),
    ('widgets', 'widgets'),
    ('app', 'app'),
    ('cacert.pem', '.'),
]

# 隐藏导入的模块
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtNetwork',
    'requests',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    'json',
    'hashlib',
    'platform',
    'subprocess',
    'uuid',
    'time',
    'datetime',
    'os',
    'sys',
    'traceback',
    'threading',
    'queue',
    'urllib.parse',
    'urllib.request',
    'base64',
    'io',
    'tempfile',
    'shutil',
    'pathlib',
    'typing',
    'collections',
    'functools',
    'itertools',
    'operator',
    'copy',
    'pickle',
    'sqlite3',
    'csv',
    'configparser',
    'logging',
    'warnings',
    'inspect',
    'importlib',
    'pkgutil',
    'zipfile',
    'tarfile',
    'gzip',
    'bz2',
    'lzma',
    'zlib',
    'email',
    'html',
    'xml',
    'http',
    'ftplib',
    'smtplib',
    'poplib',
    'imaplib',
    'telnetlib',
    'socketserver',
    'xmlrpc',
    'webbrowser',
    'cgi',
    'cgitb',
    'wsgiref',
    'distutils',
    'site',
    'sysconfig',
    'pywin32',
    'win32api',
    'win32con',
    'win32gui',
    'win32process',
    'win32service',
    'win32serviceutil',
    'win32event',
    'win32file',
    'win32pipe',
    'win32security',
    'win32net',
    'win32netcon',
    'win32wnet',
    'win32clipboard',
    'win32com',
    'pythoncom',
    'pywintypes',
]

a = Analysis(
    ['main_modular.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'unittest',
        'doctest',
        'pdb',
        'profile',
        'cProfile',
        'pstats',
        'timeit',
        'trace',
        'turtle',
        'audioop',
        'chunk',
        'colorsys',
        'imghdr',
        'sndhdr',
        'sunau',
        'wave',
        'aifc',
        'ossaudiodev',
        'winsound',
        'msilib',
        'msvcrt',
        'winreg',
        '_winapi',
        'nt',
        'posix',
        'pwd',
        'grp',
        'termios',
        'tty',
        'pty',
        'fcntl',
        'resource',
        'syslog',
        'curses',
        'readline',
        'rlcompleter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CinemaTicketSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='data/img/icon.ico' if os.path.exists('data/img/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CinemaTicketSystem',
)
'''
    
    with open('CinemaTicketSystem.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建 CinemaTicketSystem.spec")

def build_executable():
    """构建可执行文件"""
    print("\n🔨 开始构建可执行文件...")
    
    try:
        # 运行PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'CinemaTicketSystem.spec'
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 构建成功!")
            print("\n📋 构建输出:")
            print(result.stdout)
        else:
            print("❌ 构建失败!")
            print("\n📋 错误输出:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中发生错误: {e}")
        return False
    
    return True

def copy_additional_files():
    """复制额外的文件到dist目录"""
    print("\n📁 复制额外文件...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ dist目录不存在")
        return False
    
    # 要复制的文件和目录
    additional_files = [
        ('README.md', 'README.md'),
        ('requirements.txt', 'requirements.txt'),
        ('使用说明.md', '使用说明.md'),
    ]
    
    for src, dst in additional_files:
        if os.path.exists(src):
            dst_path = dist_dir / dst
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_path)
            print(f"✅ 已复制 {src} -> {dst}")
        else:
            print(f"⚠️  文件不存在: {src}")
    
    return True

def create_installer_script():
    """创建安装脚本"""
    print("\n📦 创建安装脚本...")
    
    installer_content = '''@echo off
echo ========================================
echo   柴犬影院票务管理系统 安装程序
echo ========================================
echo.

echo 正在检查系统要求...

:: 检查Windows版本
ver | findstr /i "10\\." >nul
if %errorlevel%==0 (
    echo [OK] Windows 10 检测通过
    goto :install
)

ver | findstr /i "11\\." >nul
if %errorlevel%==0 (
    echo [OK] Windows 11 检测通过
    goto :install
)

echo [ERROR] 不支持的Windows版本，需要Windows 10或更高版本
pause
exit /b 1

:install
echo.
echo 正在安装柴犬影院票务管理系统...

:: 创建程序目录
if not exist "%ProgramFiles%\\CinemaTicketSystem" (
    mkdir "%ProgramFiles%\\CinemaTicketSystem"
)

:: 复制文件
echo 正在复制程序文件...
xcopy /E /I /Y "." "%ProgramFiles%\\CinemaTicketSystem\\"

:: 创建桌面快捷方式
echo 正在创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\柴犬影院票务系统.lnk'); $Shortcut.TargetPath = '%ProgramFiles%\\CinemaTicketSystem\\CinemaTicketSystem.exe'; $Shortcut.WorkingDirectory = '%ProgramFiles%\\CinemaTicketSystem'; $Shortcut.Description = '柴犬影院票务管理系统'; $Shortcut.Save()"

:: 创建开始菜单快捷方式
echo 正在创建开始菜单快捷方式...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\柴犬影院票务系统" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\柴犬影院票务系统"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\柴犬影院票务系统\\柴犬影院票务系统.lnk'); $Shortcut.TargetPath = '%ProgramFiles%\\CinemaTicketSystem\\CinemaTicketSystem.exe'; $Shortcut.WorkingDirectory = '%ProgramFiles%\\CinemaTicketSystem'; $Shortcut.Description = '柴犬影院票务管理系统'; $Shortcut.Save()"

echo.
echo [OK] 安装完成！
echo.
echo 您可以通过以下方式启动程序：
echo 1. 双击桌面上的"柴犬影院票务系统"图标
echo 2. 从开始菜单启动
echo 3. 直接运行: %ProgramFiles%\\CinemaTicketSystem\\CinemaTicketSystem.exe
echo.
pause
'''
    
    with open('dist/install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print("✅ 已创建安装脚本 dist/install.bat")

def main():
    """主函数"""
    print("🚀 开始打包PyQt5电影票务管理系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 复制额外文件
    copy_additional_files()
    
    # 创建安装脚本
    create_installer_script()
    
    print("\n" + "=" * 50)
    print("🎉 打包完成!")
    print("\n📁 输出文件:")
    print("  - dist/CinemaTicketSystem.exe - 主程序")
    print("  - dist/install.bat - 安装脚本")
    print("  - dist/ - 完整程序目录")
    
    print("\n📋 使用说明:")
    print("  1. 将整个dist目录复制到目标电脑")
    print("  2. 以管理员身份运行install.bat进行安装")
    print("  3. 或直接运行CinemaTicketSystem.exe")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
