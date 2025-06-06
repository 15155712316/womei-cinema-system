#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装打包所需的依赖包
"""

import subprocess
import sys
import os

def install_package(package_name, version=None):
    """安装指定的包"""
    try:
        if version:
            package = f"{package_name}=={version}"
        else:
            package = package_name
            
        print(f"正在安装 {package}...")
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package, '--upgrade'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {package} 安装成功")
            return True
        else:
            print(f"❌ {package} 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装 {package_name} 时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始安装打包依赖...")
    print("=" * 50)
    
    # 必需的包列表
    required_packages = [
        ('PyInstaller', '5.13.2'),
        ('PyQt5', '5.15.9'),
        ('requests', '2.31.0'),
        ('Pillow', '10.0.1'),
        ('pywin32', '306'),
        ('qrcode', '7.4.2'),
        ('setuptools', None),
        ('wheel', None),
    ]
    
    failed_packages = []
    
    for package_name, version in required_packages:
        if not install_package(package_name, version):
            failed_packages.append(package_name)
    
    print("\n" + "=" * 50)
    
    if failed_packages:
        print(f"❌ 以下包安装失败: {', '.join(failed_packages)}")
        print("请手动安装这些包或检查网络连接")
        return False
    else:
        print("✅ 所有依赖包安装成功!")
        print("\n现在可以运行 python build_exe.py 进行打包")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
