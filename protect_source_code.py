#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
源代码保护脚本 - 使用PyArmor进行代码混淆和加密
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

def check_pyarmor():
    """检查PyArmor是否已安装"""
    try:
        result = subprocess.run(['pyarmor', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PyArmor已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ PyArmor未正确安装")
            return False
    except FileNotFoundError:
        print("❌ PyArmor未安装")
        return False

def install_pyarmor():
    """安装PyArmor"""
    print("📦 正在安装PyArmor...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyarmor'], check=True)
        print("✅ PyArmor安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyArmor安装失败")
        return False

def backup_source_code():
    """备份原始源代码"""
    print("💾 备份原始源代码...")
    
    backup_dir = 'source_backup'
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)
    
    # 需要备份的目录和文件
    items_to_backup = [
        'main_modular.py',
        'ui/',
        'services/',
        'utils/',
        'controllers/',
        'views/',
        'widgets/',
        'app/',
        'data/',
        'requirements.txt'
    ]
    
    os.makedirs(backup_dir, exist_ok=True)
    
    for item in items_to_backup:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(backup_dir, item))
                print(f"✅ 已备份目录: {item}")
            else:
                shutil.copy2(item, backup_dir)
                print(f"✅ 已备份文件: {item}")
        else:
            print(f"⚠️  跳过不存在的项目: {item}")
    
    print(f"✅ 源代码备份完成: {backup_dir}")

def create_protection_config():
    """创建保护配置文件"""
    config = {
        "restrict_mode": 0,  # 最高限制级别
        "enable_jit": True,  # 启用JIT保护
        "mix_str": True,     # 字符串混淆
        "obf_code": 2,       # 代码混淆级别
        "obf_mod": 1,        # 模块混淆
        "wrap_mode": 1,      # 包装模式
        "advanced": True     # 高级保护
    }
    
    with open('protection_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✅ 保护配置文件已创建")

def obfuscate_source_code():
    """混淆源代码"""
    print("🔒 开始混淆源代码...")
    
    protected_dir = 'protected_source'
    if os.path.exists(protected_dir):
        shutil.rmtree(protected_dir)
    
    # PyArmor混淆命令
    cmd = [
        'pyarmor',
        'obfuscate',
        '--recursive',           # 递归处理子目录
        '--restrict', '0',       # 最高限制级别
        '--enable-jit',          # 启用JIT保护
        '--mix-str',             # 字符串混淆
        '--output', protected_dir,
        'main_modular.py'
    ]
    
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            print("✅ 代码混淆成功")
            print("混淆输出:")
            print(result.stdout)
        else:
            print("❌ 代码混淆失败")
            print("错误信息:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 混淆过程中发生错误: {e}")
        return False
    
    return True

def copy_resources():
    """复制资源文件到保护目录"""
    print("📁 复制资源文件...")
    
    protected_dir = 'protected_source'
    
    # 需要复制的资源文件和目录
    resources = [
        'data/',
        'requirements.txt',
        'README.md',
        'build_exe.py',
        'install_dependencies.py',
        'pre_build_check.py',
        'test_packaged_app.py'
    ]
    
    for resource in resources:
        if os.path.exists(resource):
            dest_path = os.path.join(protected_dir, resource)
            
            if os.path.isdir(resource):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(resource, dest_path)
                print(f"✅ 已复制目录: {resource}")
            else:
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(resource, dest_path)
                print(f"✅ 已复制文件: {resource}")
        else:
            print(f"⚠️  跳过不存在的资源: {resource}")

def encrypt_config_files():
    """加密配置文件"""
    print("🔐 加密配置文件...")
    
    try:
        from cryptography.fernet import Fernet
        
        # 生成加密密钥
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        # 保存密钥到代码中（混淆后会被保护）
        key_file = 'protected_source/encryption_key.py'
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(f'# 加密密钥\nENCRYPTION_KEY = {key!r}\n')
        
        # 加密配置文件
        config_file = 'protected_source/data/config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            
            encrypted_data = cipher.encrypt(config_data.encode())
            
            # 保存加密后的配置
            with open(config_file + '.encrypted', 'wb') as f:
                f.write(encrypted_data)
            
            # 删除原始配置文件
            os.remove(config_file)
            
            print("✅ 配置文件加密完成")
        
    except ImportError:
        print("⚠️  cryptography库未安装，跳过配置文件加密")
        print("可以运行: pip install cryptography")

def add_anti_debug():
    """添加反调试保护"""
    print("🛡️ 添加反调试保护...")
    
    anti_debug_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反调试保护模块
"""

import sys
import os
import time
import threading

class AntiDebug:
    """反调试保护类"""
    
    @staticmethod
    def check_debugger():
        """检测调试器"""
        if sys.gettrace() is not None:
            print("检测到调试器，程序退出")
            os._exit(1)
    
    @staticmethod
    def check_vm():
        """检测虚拟机环境"""
        vm_indicators = [
            r'C:\\windows\\system32\\drivers\\vmmouse.sys',
            r'C:\\windows\\system32\\drivers\\vmhgfs.sys',
            r'C:\\windows\\system32\\drivers\\VBoxMouse.sys',
            r'C:\\windows\\system32\\drivers\\VBoxGuest.sys',
            r'C:\\windows\\system32\\drivers\\VBoxSF.sys',
        ]
        
        for indicator in vm_indicators:
            if os.path.exists(indicator):
                print("检测到虚拟机环境")
                # 可以选择退出或限制功能
                # os._exit(1)
                break
    
    @staticmethod
    def start_protection():
        """启动保护"""
        def protection_thread():
            while True:
                AntiDebug.check_debugger()
                time.sleep(1)
        
        # 在后台线程中运行保护
        thread = threading.Thread(target=protection_thread, daemon=True)
        thread.start()
        
        # 初始检查
        AntiDebug.check_vm()

# 自动启动保护
AntiDebug.start_protection()
'''
    
    anti_debug_file = 'protected_source/utils/anti_debug.py'
    os.makedirs(os.path.dirname(anti_debug_file), exist_ok=True)
    
    with open(anti_debug_file, 'w', encoding='utf-8') as f:
        f.write(anti_debug_code)
    
    print("✅ 反调试保护已添加")

def create_protected_build_script():
    """创建保护版本的打包脚本"""
    print("📝 创建保护版本打包脚本...")
    
    protected_build_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保护版本的打包脚本
"""

import os
import sys

# 添加反调试保护
try:
    from utils.anti_debug import AntiDebug
    AntiDebug.start_protection()
except ImportError:
    pass

# 导入原始的打包脚本
sys.path.insert(0, '.')

if __name__ == "__main__":
    # 检查是否在保护环境中运行
    if not os.path.exists('utils/anti_debug.py'):
        print("❌ 请在保护环境中运行此脚本")
        sys.exit(1)
    
    # 执行原始打包逻辑
    from build_exe import main
    main()
'''
    
    script_file = 'protected_source/build_protected.py'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(protected_build_script)
    
    print("✅ 保护版本打包脚本已创建")

def main():
    """主函数"""
    print("🛡️ 开始源代码保护流程")
    print("=" * 50)
    
    # 1. 检查PyArmor
    if not check_pyarmor():
        if not install_pyarmor():
            print("❌ 无法安装PyArmor，保护流程终止")
            return False
    
    # 2. 备份源代码
    backup_source_code()
    
    # 3. 创建保护配置
    create_protection_config()
    
    # 4. 混淆源代码
    if not obfuscate_source_code():
        print("❌ 代码混淆失败，保护流程终止")
        return False
    
    # 5. 复制资源文件
    copy_resources()
    
    # 6. 加密配置文件
    encrypt_config_files()
    
    # 7. 添加反调试保护
    add_anti_debug()
    
    # 8. 创建保护版本打包脚本
    create_protected_build_script()
    
    print("\n" + "=" * 50)
    print("🎉 源代码保护完成!")
    print("\n📁 输出目录:")
    print("  - source_backup/     # 原始代码备份")
    print("  - protected_source/  # 保护后的代码")
    print("\n📋 下一步操作:")
    print("  1. cd protected_source")
    print("  2. python build_protected.py")
    print("  3. 测试保护后的程序")
    print("\n⚠️  重要提醒:")
    print("  - 请妥善保管source_backup目录")
    print("  - 不要分发protected_source目录")
    print("  - 只分发最终的exe文件")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
