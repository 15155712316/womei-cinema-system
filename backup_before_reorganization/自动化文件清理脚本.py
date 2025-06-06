#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 自动化文件清理脚本
基于分析报告执行文件清理和重组
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class AutoFileCleanup:
    """自动化文件清理器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.backup_dir = self.root_dir / "backup_before_cleanup"
        self.log_file = self.root_dir / "cleanup_log.txt"
        
        # 清理规则配置
        self.cleanup_rules = {
            'create_directories': [
                'docs', 'docs/reports', 'docs/diagrams', 'docs/guides',
                'tools', 'tools/analyzers', 'tools/fixes', 'tools/payment',
                'tests', 'tests/unit_tests', 'tests/integration_tests',
                'data', 'data/har_files', 'data/images', 'data/configs',
                'archive', 'archive/old_versions', 'archive/deprecated'
            ],
            'move_rules': {
                'docs/reports/': [
                    '*报告.md', '*总结.md', '*分析*.md', 
                    'main_modular功能分析总结报告.md',
                    'PyQt5电影票务系统死代码分析报告.md',
                    'PyQt5电影票务系统代码优化分析报告.md',
                    'UI组件深度清理分析报告.md',
                    '支付方式对比分析报告.md'
                ],
                'docs/diagrams/': [
                    '*.mmd', '*图表*.html', '*图表*.md',
                    'PyQt5电影票务系统业务流程图.mmd',
                    'PyQt5电影票务系统架构图.mmd',
                    'PyQt5电影票务系统图表.html',
                    '图表保存使用说明.md'
                ],
                'tools/analyzers/': [
                    '*analyzer*.py', '*分析器*.py',
                    'main_modular_analyzer.py',
                    'ui_component_deep_analyzer.py',
                    'ui_component_usage_analyzer.py',
                    '项目文件清理分析器.py'
                ],
                'tools/fixes/': [
                    'fix_*.py', 'quick_*.py',
                    'fix_account_selection.py',
                    'fix_api_authentication.py',
                    'fix_auto_account_selection.py',
                    'quick_fix_token_refresh.py',
                    'quick_machine_code_fix.py'
                ],
                'tools/payment/': [
                    '*payment*.py', 'analyze_payment_methods.py',
                    'payment_comparison_analysis.py',
                    'payment_integration_code.py',
                    'enhanced_payment_implementation.py'
                ],
                'tests/': [
                    'test_*.py', 'check_*.py',
                    'test_enhanced_payment_system.py',
                    'test_member_password_policy.py',
                    'test_order_detail_display.py',
                    'test_qrcode_display_consistency.py'
                ],
                'data/har_files/': [
                    '*.har'
                ],
                'data/images/': [
                    'qrcode_*.png', '*.jpg', '*.jpeg', '*.gif'
                ],
                'archive/deprecated/': [
                    'cleanup-deadcode.ps1',
                    'syntax_report.txt',
                    'result.json'
                ]
            },
            'keep_in_root': [
                'main_modular.py', 'main.py', 'requirements.txt',
                'CinemaTicketSystem.spec', 'build_info.json',
                'README.md', '使用说明.md', '用户使用手册.md',
                'PyQt5电影票务系统功能架构文档.md',
                '一键打包.bat', 'api_validation_report.json'
            ],
            'delete_files': [
                '*.tmp', '*.log', '*.cache', '*.pyc'
            ]
        }
    
    def log_action(self, action: str, details: str = ""):
        """记录操作日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {action}"
        if details:
            log_entry += f" - {details}"
        
        print(log_entry)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def create_backup(self):
        """创建备份"""
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        self.log_action("创建备份", f"备份目录: {self.backup_dir}")
        
        # 备份所有文件
        for item in self.root_dir.iterdir():
            if item.is_file() and item.name != 'cleanup_log.txt':
                try:
                    shutil.copy2(item, self.backup_dir)
                    self.log_action("备份文件", str(item.name))
                except Exception as e:
                    self.log_action("备份失败", f"{item.name}: {e}")
    
    def create_directories(self):
        """创建目录结构"""
        self.log_action("开始创建目录结构")
        
        for dir_path in self.cleanup_rules['create_directories']:
            full_path = self.root_dir / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                self.log_action("创建目录", dir_path)
    
    def match_pattern(self, filename: str, pattern: str) -> bool:
        """模式匹配"""
        if pattern.startswith('*') and pattern.endswith('*'):
            return pattern[1:-1] in filename
        elif pattern.startswith('*'):
            return filename.endswith(pattern[1:])
        elif pattern.endswith('*'):
            return filename.startswith(pattern[:-1])
        else:
            return filename == pattern
    
    def move_files(self):
        """移动文件到指定目录"""
        self.log_action("开始移动文件")
        
        for target_dir, patterns in self.cleanup_rules['move_rules'].items():
            target_path = self.root_dir / target_dir
            
            for pattern in patterns:
                for file_path in self.root_dir.iterdir():
                    if file_path.is_file() and self.match_pattern(file_path.name, pattern):
                        try:
                            # 检查是否应该保留在根目录
                            if file_path.name in self.cleanup_rules['keep_in_root']:
                                continue
                            
                            target_file = target_path / file_path.name
                            shutil.move(str(file_path), str(target_file))
                            self.log_action("移动文件", f"{file_path.name} -> {target_dir}")
                        except Exception as e:
                            self.log_action("移动失败", f"{file_path.name}: {e}")
    
    def delete_temp_files(self):
        """删除临时文件"""
        self.log_action("开始删除临时文件")
        
        for pattern in self.cleanup_rules['delete_files']:
            for file_path in self.root_dir.rglob(pattern):
                if file_path.is_file():
                    try:
                        file_path.unlink()
                        self.log_action("删除临时文件", str(file_path.name))
                    except Exception as e:
                        self.log_action("删除失败", f"{file_path.name}: {e}")
    
    def generate_summary(self):
        """生成清理摘要"""
        summary = {
            'cleanup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'directories_created': len(self.cleanup_rules['create_directories']),
            'move_rules_applied': len(self.cleanup_rules['move_rules']),
            'files_kept_in_root': len(self.cleanup_rules['keep_in_root']),
            'backup_location': str(self.backup_dir),
            'log_file': str(self.log_file)
        }
        
        # 统计根目录文件数
        root_files = [f for f in self.root_dir.iterdir() if f.is_file()]
        summary['remaining_root_files'] = len(root_files)
        summary['root_file_list'] = [f.name for f in root_files]
        
        # 保存摘要
        summary_file = self.root_dir / 'cleanup_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        self.log_action("生成清理摘要", str(summary_file))
        return summary
    
    def run_cleanup(self, create_backup: bool = True, confirm: bool = True):
        """执行完整清理流程"""
        print("🎬 PyQt5电影票务管理系统 - 自动化文件清理")
        print("=" * 60)
        
        if confirm:
            print("\n⚠️  警告：此操作将重组项目文件结构")
            print("📋 清理内容：")
            print("  - 创建新的目录结构")
            print("  - 移动文件到相应目录")
            print("  - 删除临时文件")
            print("  - 保留核心文件在根目录")
            
            if create_backup:
                print(f"  - 创建备份到: {self.backup_dir}")
            
            response = input("\n是否继续执行清理？(y/N): ").strip().lower()
            if response != 'y':
                print("❌ 清理操作已取消")
                return False
        
        try:
            # 初始化日志
            if self.log_file.exists():
                self.log_file.unlink()
            
            self.log_action("开始自动化文件清理")
            
            # 创建备份
            if create_backup:
                self.create_backup()
            
            # 执行清理步骤
            self.create_directories()
            self.delete_temp_files()
            self.move_files()
            
            # 生成摘要
            summary = self.generate_summary()
            
            self.log_action("清理完成")
            
            # 显示结果
            print(f"\n✅ 清理完成！")
            print(f"📁 根目录剩余文件: {summary['remaining_root_files']} 个")
            print(f"📋 详细日志: {self.log_file}")
            print(f"📊 清理摘要: cleanup_summary.json")
            
            if create_backup:
                print(f"💾 备份位置: {self.backup_dir}")
            
            return True
            
        except Exception as e:
            self.log_action("清理失败", str(e))
            print(f"❌ 清理失败: {e}")
            return False
    
    def preview_cleanup(self):
        """预览清理操作"""
        print("🔍 清理操作预览")
        print("=" * 40)
        
        print("\n📁 将创建的目录:")
        for dir_path in self.cleanup_rules['create_directories']:
            print(f"  + {dir_path}")
        
        print("\n📋 文件移动规则:")
        for target_dir, patterns in self.cleanup_rules['move_rules'].items():
            print(f"  📂 {target_dir}")
            for pattern in patterns:
                matching_files = []
                for file_path in self.root_dir.iterdir():
                    if file_path.is_file() and self.match_pattern(file_path.name, pattern):
                        if file_path.name not in self.cleanup_rules['keep_in_root']:
                            matching_files.append(file_path.name)
                
                if matching_files:
                    print(f"    {pattern} -> {len(matching_files)} 个文件")
                    for filename in matching_files[:3]:  # 只显示前3个
                        print(f"      - {filename}")
                    if len(matching_files) > 3:
                        print(f"      ... 还有 {len(matching_files) - 3} 个文件")
        
        print("\n✅ 保留在根目录的文件:")
        for filename in self.cleanup_rules['keep_in_root']:
            if (self.root_dir / filename).exists():
                print(f"  ✓ {filename}")
        
        print("\n🗑️ 将删除的临时文件:")
        for pattern in self.cleanup_rules['delete_files']:
            temp_files = list(self.root_dir.rglob(pattern))
            if temp_files:
                print(f"  {pattern} -> {len(temp_files)} 个文件")

def main():
    """主函数"""
    cleanup = AutoFileCleanup()
    
    print("请选择操作:")
    print("1. 预览清理操作")
    print("2. 执行清理 (创建备份)")
    print("3. 执行清理 (不创建备份)")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == '1':
        cleanup.preview_cleanup()
    elif choice == '2':
        cleanup.run_cleanup(create_backup=True)
    elif choice == '3':
        cleanup.run_cleanup(create_backup=False)
    elif choice == '4':
        print("👋 退出程序")
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
