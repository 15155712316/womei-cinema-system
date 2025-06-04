#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包前环境检查脚本
确保所有必要的文件和依赖都已准备就绪
"""

import os
import sys
import json
import importlib
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.8或更高版本")
        return False

def check_required_packages():
    """检查必需的包"""
    print("\n📦 检查必需的包...")
    
    required_packages = {
        'PyQt5': 'PyQt5',
        'requests': 'requests',
        'PIL': 'Pillow',
        'qrcode': 'qrcode',
        'PyInstaller': 'PyInstaller'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_packages.items():
        try:
            importlib.import_module(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️  缺少包: {', '.join(missing_packages)}")
        print("请运行: python install_dependencies.py")
        return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        'main_modular.py',
        'requirements.txt',
        'data/config.json',
        'ui/login_window.py',
        'services/auth_service.py',
        'utils/signals.py',
    ]
    
    required_dirs = [
        'data',
        'ui',
        'services',
        'utils',
        'controllers',
        'views',
        'widgets'
    ]
    
    missing_files = []
    missing_dirs = []
    
    # 检查文件
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            missing_files.append(file_path)
    
    # 检查目录
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 目录不存在")
            missing_dirs.append(dir_path)
    
    if missing_files or missing_dirs:
        print(f"\n⚠️  缺少文件: {missing_files}")
        print(f"⚠️  缺少目录: {missing_dirs}")
        return False
    
    return True

def check_data_files():
    """检查数据文件"""
    print("\n📄 检查数据文件...")
    
    data_files = {
        'data/config.json': '配置文件',
        'data/cinema_info.json': '影院信息',
        'data/accounts.json': '账号信息'
    }
    
    for file_path, description in data_files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json.load(f)
                print(f"✅ {description}: {file_path}")
            except json.JSONDecodeError:
                print(f"⚠️  {description}: {file_path} - JSON格式错误")
            except Exception as e:
                print(f"❌ {description}: {file_path} - 读取错误: {e}")
        else:
            # 创建空的数据文件
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                if 'config.json' in file_path:
                    default_data = {
                        "server_url": "http://43.142.19.28:5000",
                        "timeout": 10,
                        "debug": False
                    }
                elif 'cinema_info.json' in file_path:
                    default_data = []
                elif 'accounts.json' in file_path:
                    default_data = []
                else:
                    default_data = {}
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ {description}: {file_path} - 已创建默认文件")
            except Exception as e:
                print(f"❌ {description}: {file_path} - 创建失败: {e}")
                return False
    
    return True

def check_imports():
    """检查主要模块的导入"""
    print("\n🔍 检查模块导入...")
    
    try:
        # 测试主程序导入
        sys.path.insert(0, '.')
        
        print("  检查主程序模块...")
        import main_modular
        print("✅ main_modular.py 导入成功")
        
        print("  检查UI模块...")
        from ui.login_window import LoginWindow
        print("✅ LoginWindow 导入成功")
        
        print("  检查服务模块...")
        from services.auth_service import AuthService
        print("✅ AuthService 导入成功")
        
        print("  检查工具模块...")
        from utils.signals import event_bus
        print("✅ event_bus 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def check_machine_code_consistency():
    """检查机器码一致性"""
    print("\n🔧 检查机器码一致性...")
    
    try:
        from services.auth_service import auth_service
        from ui.login_window import LoginWindow
        from PyQt5.QtWidgets import QApplication
        
        # 创建临时QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 获取两个来源的机器码
        auth_code = auth_service.get_machine_code()
        
        login_window = LoginWindow()
        login_code = login_window.machine_code
        login_window.close()
        
        if auth_code == login_code:
            print(f"✅ 机器码一致: {auth_code}")
            return True
        else:
            print(f"❌ 机器码不一致:")
            print(f"   auth_service: {auth_code}")
            print(f"   login_window: {login_code}")
            return False
            
    except Exception as e:
        print(f"❌ 机器码检查失败: {e}")
        return False

def create_build_info():
    """创建构建信息文件"""
    print("\n📝 创建构建信息...")
    
    build_info = {
        "build_time": __import__('datetime').datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
        "architecture": __import__('platform').architecture()[0],
        "machine": __import__('platform').machine(),
        "version": "1.0.0"
    }
    
    try:
        with open('build_info.json', 'w', encoding='utf-8') as f:
            json.dump(build_info, f, ensure_ascii=False, indent=2)
        print("✅ 构建信息已创建: build_info.json")
        return True
    except Exception as e:
        print(f"❌ 创建构建信息失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始打包前环境检查")
    print("=" * 50)
    
    checks = [
        ("Python版本", check_python_version),
        ("必需包", check_required_packages),
        ("项目结构", check_project_structure),
        ("数据文件", check_data_files),
        ("模块导入", check_imports),
        ("机器码一致性", check_machine_code_consistency),
        ("构建信息", create_build_info),
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                failed_checks.append(check_name)
        except Exception as e:
            print(f"❌ {check_name}检查时发生错误: {e}")
            failed_checks.append(check_name)
    
    print("\n" + "=" * 50)
    
    if failed_checks:
        print(f"❌ 以下检查失败: {', '.join(failed_checks)}")
        print("\n请解决上述问题后再进行打包")
        return False
    else:
        print("✅ 所有检查通过!")
        print("\n现在可以运行打包脚本:")
        print("  python build_exe.py")
        return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
