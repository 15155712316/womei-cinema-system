#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全打包脚本 - 集成代码保护和打包流程
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path

class SecureBuildPipeline:
    """安全构建流水线"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / 'source_backup'
        self.protected_dir = self.project_root / 'protected_source'
        self.dist_dir = self.project_root / 'secure_dist'
    
    def step1_backup_source(self):
        """步骤1: 备份源代码"""
        print("📦 步骤1: 备份源代码")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # 要备份的文件和目录
        items_to_backup = [
            'main_modular.py',
            'ui', 'services', 'utils', 'controllers', 'views', 'widgets', 'app',
            'data', 'requirements.txt', 'README.md'
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        
        for item in items_to_backup:
            item_path = self.project_root / item
            if item_path.exists():
                if item_path.is_dir():
                    shutil.copytree(item_path, self.backup_dir / item)
                else:
                    shutil.copy2(item_path, self.backup_dir)
                print(f"  ✅ 已备份: {item}")
        
        print("✅ 源代码备份完成\n")
    
    def step2_install_protection_tools(self):
        """步骤2: 安装保护工具"""
        print("🛠️ 步骤2: 安装保护工具")
        
        tools = [
            ('pyarmor', 'PyArmor代码混淆工具'),
            ('cryptography', '加密库')
        ]
        
        for tool, description in tools:
            try:
                __import__(tool)
                print(f"  ✅ {description}已安装")
            except ImportError:
                print(f"  📦 正在安装{description}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', tool], check=True)
                print(f"  ✅ {description}安装完成")
        
        print("✅ 保护工具安装完成\n")
    
    def step3_obfuscate_code(self):
        """步骤3: 混淆代码"""
        print("🔒 步骤3: 混淆代码")
        
        if self.protected_dir.exists():
            shutil.rmtree(self.protected_dir)
        
        # PyArmor混淆命令
        cmd = [
            'pyarmor', 'obfuscate',
            '--recursive',
            '--restrict', '0',
            '--enable-jit',
            '--mix-str',
            '--output', str(self.protected_dir),
            'main_modular.py'
        ]
        
        print(f"  执行: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ 代码混淆成功")
        else:
            print(f"  ❌ 代码混淆失败: {result.stderr}")
            return False
        
        print("✅ 代码混淆完成\n")
        return True
    
    def step4_encrypt_configs(self):
        """步骤4: 加密配置文件"""
        print("🔐 步骤4: 加密配置文件")
        
        # 复制配置加密工具到保护目录
        config_enc_source = self.project_root / 'config_encryption.py'
        config_enc_dest = self.protected_dir / 'config_encryption.py'
        
        if config_enc_source.exists():
            shutil.copy2(config_enc_source, config_enc_dest)
        
        # 加密配置文件
        config_files = [
            self.protected_dir / 'data' / 'config.json',
            self.protected_dir / 'data' / 'cinema_info.json',
            self.protected_dir / 'data' / 'accounts.json'
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    # 使用配置加密工具
                    cmd = [
                        sys.executable, str(config_enc_dest),
                        'encrypt', '--file', str(config_file)
                    ]
                    subprocess.run(cmd, check=True, cwd=str(self.protected_dir))
                    
                    # 删除原始文件
                    config_file.unlink()
                    print(f"  ✅ 已加密: {config_file.name}")
                    
                except Exception as e:
                    print(f"  ⚠️ 加密失败 {config_file.name}: {e}")
        
        print("✅ 配置文件加密完成\n")
    
    def step5_add_security_features(self):
        """步骤5: 添加安全特性"""
        print("🛡️ 步骤5: 添加安全特性")
        
        # 创建安全加载器
        security_loader = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全加载器 - 在程序启动时进行安全检查
"""

import os
import sys
import time
import threading
import json
from config_encryption import SecureConfigLoader

class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.config_loader = SecureConfigLoader()
        self._running = True
    
    def check_environment(self):
        """检查运行环境"""
        # 检查调试器
        if sys.gettrace() is not None:
            print("检测到调试环境")
            # 可以选择退出或限制功能
            # os._exit(1)
        
        # 检查虚拟机
        vm_files = [
            r'C:\\windows\\system32\\drivers\\vmmouse.sys',
            r'C:\\windows\\system32\\drivers\\VBoxMouse.sys'
        ]
        
        for vm_file in vm_files:
            if os.path.exists(vm_file):
                print("检测到虚拟机环境")
                break
    
    def load_secure_config(self, config_name):
        """安全加载配置"""
        try:
            config_file = f'data/{config_name}'
            return self.config_loader.load_config(config_file)
        except Exception as e:
            print(f"配置加载失败: {e}")
            return {}
    
    def start_monitoring(self):
        """启动安全监控"""
        def monitor_thread():
            while self._running:
                self.check_environment()
                time.sleep(5)
        
        thread = threading.Thread(target=monitor_thread, daemon=True)
        thread.start()
    
    def stop_monitoring(self):
        """停止安全监控"""
        self._running = False

# 全局安全管理器实例
security_manager = SecurityManager()
'''
        
        security_file = self.protected_dir / 'security_manager.py'
        with open(security_file, 'w', encoding='utf-8') as f:
            f.write(security_loader)
        
        print("  ✅ 安全管理器已创建")
        
        # 修改主程序以集成安全检查
        main_file = self.protected_dir / 'main_modular.py'
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 在文件开头添加安全检查
            security_import = '''
# 安全检查
try:
    from security_manager import security_manager
    security_manager.check_environment()
    security_manager.start_monitoring()
except ImportError:
    pass

'''
            
            # 插入安全检查代码
            if 'from security_manager import' not in content:
                lines = content.split('\n')
                # 找到第一个import语句的位置
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        insert_pos = i
                        break
                
                lines.insert(insert_pos, security_import)
                
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("  ✅ 主程序安全集成完成")
        
        print("✅ 安全特性添加完成\n")
    
    def step6_build_executable(self):
        """步骤6: 构建可执行文件"""
        print("🔨 步骤6: 构建可执行文件")
        
        # 复制构建脚本到保护目录
        build_script = self.project_root / 'build_exe.py'
        if build_script.exists():
            shutil.copy2(build_script, self.protected_dir)
        
        # 在保护目录中执行构建
        original_cwd = os.getcwd()
        try:
            os.chdir(self.protected_dir)
            
            # 执行构建
            result = subprocess.run([sys.executable, 'build_exe.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("  ✅ 可执行文件构建成功")
                
                # 移动构建结果到安全目录
                protected_dist = self.protected_dir / 'dist'
                if protected_dist.exists():
                    if self.dist_dir.exists():
                        shutil.rmtree(self.dist_dir)
                    shutil.move(str(protected_dist), str(self.dist_dir))
                    print(f"  ✅ 构建结果已移动到: {self.dist_dir}")
                
                return True
            else:
                print(f"  ❌ 构建失败: {result.stderr}")
                return False
                
        finally:
            os.chdir(original_cwd)
        
        print("✅ 可执行文件构建完成\n")
        return True
    
    def step7_cleanup(self):
        """步骤7: 清理临时文件"""
        print("🧹 步骤7: 清理临时文件")
        
        # 删除保护目录（保留备份）
        if self.protected_dir.exists():
            shutil.rmtree(self.protected_dir)
            print("  ✅ 已清理保护目录")
        
        # 清理构建缓存
        for cache_dir in ['build', '__pycache__']:
            cache_path = self.project_root / cache_dir
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"  ✅ 已清理: {cache_dir}")
        
        print("✅ 清理完成\n")
    
    def build(self):
        """执行完整的安全构建流程"""
        print("🚀 开始安全构建流程")
        print("=" * 60)
        
        try:
            # 执行所有步骤
            self.step1_backup_source()
            self.step2_install_protection_tools()
            
            if not self.step3_obfuscate_code():
                return False
            
            self.step4_encrypt_configs()
            self.step5_add_security_features()
            
            if not self.step6_build_executable():
                return False
            
            self.step7_cleanup()
            
            print("=" * 60)
            print("🎉 安全构建完成!")
            print(f"\n📁 输出目录: {self.dist_dir}")
            print(f"📁 源码备份: {self.backup_dir}")
            print("\n⚠️ 重要提醒:")
            print("  - 只分发secure_dist目录中的文件")
            print("  - 妥善保管source_backup目录")
            print("  - 定期更新保护策略")
            
            return True
            
        except Exception as e:
            print(f"❌ 构建过程中发生错误: {e}")
            return False

def main():
    """主函数"""
    builder = SecureBuildPipeline()
    success = builder.build()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
