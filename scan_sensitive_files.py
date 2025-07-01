#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面扫描项目中不能上传到GitHub的敏感文件
"""

import os
import glob
import json
import re
from pathlib import Path
from typing import List, Dict

class SensitiveFileScanner:
    def __init__(self):
        self.project_root = Path('.')
        self.sensitive_files = {
            'high_risk': [],      # 绝对不能上传
            'medium_risk': [],    # 需要审查
            'low_risk': []        # 建议排除
        }
        
    def scan_by_filename_patterns(self):
        """按文件名模式扫描敏感文件"""
        print("🔍 按文件名模式扫描敏感文件")
        print("-" * 50)
        
        # 高风险文件模式
        high_risk_patterns = [
            '*.har',              # HAR文件包含完整API数据
            'accounts.json',      # 账号信息
            'data/accounts.json', # 数据目录中的账号信息
            '.env',              # 环境变量文件
            'config.json',       # 可能包含敏感配置
            '*.log',             # 日志文件可能包含敏感信息
            'password*',         # 密码相关文件
            'secret*',           # 密钥相关文件
            'token*',            # Token相关文件
        ]
        
        # 中风险文件模式
        medium_risk_patterns = [
            'test_*.py',         # 测试文件可能包含真实数据
            '*_test.py',         # 测试文件
            'debug_*.py',        # 调试文件
            'analyze_*.py',      # 分析文件
            'check_*.py',        # 检查文件
            'compare_*.py',      # 对比文件
            'extract_*.py',      # 提取文件
            'generate_*.py',     # 生成文件
            'har_*.py',          # HAR相关文件
            'security_*.py',     # 安全相关文件
            'voucher_*.py',      # 券相关测试文件
            'simple_*.py',       # 简单测试文件
            'comprehensive_*.py', # 综合分析文件
            'detailed_*.py',     # 详细分析文件
            'corrected_*.py',    # 修正文件
            'final_*.py',        # 最终版本文件
            'fresh_*.py',        # 新版本文件
            'curl_*.py',         # curl相关文件
            'diagnose_*.py',     # 诊断文件
            'direct_*.py',       # 直接调用文件
            'create_*.py',       # 创建文件
            'get_*.py',          # 获取文件
            'cleanup_*.py',      # 清理文件
            'verify_*.py',       # 验证文件
            'scan_*.py',         # 扫描文件
        ]
        
        # 低风险文件模式
        low_risk_patterns = [
            '*指南.md',          # 中文指南文档
            '*方案.md',          # 中文方案文档
            '*总结.md',          # 中文总结文档
            '*分析报告.md',      # 中文分析报告
            '*_report.md',       # 英文报告
            '*_analysis.md',     # 英文分析
            '*_results.json',    # 结果文件
            'temp/*',            # 临时文件
            'tmp/*',             # 临时文件
            '__pycache__/*',     # Python缓存
            '*.pyc',             # Python编译文件
            '*.pyo',             # Python优化文件
            '.DS_Store',         # macOS系统文件
            'Thumbs.db',         # Windows系统文件
            '绑券.py',           # 中文命名文件
            '订单列表.py',       # 中文命名文件
            '优惠券*.py',        # 中文命名文件
        ]
        
        # 扫描高风险文件
        for pattern in high_risk_patterns:
            files = glob.glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    self.sensitive_files['high_risk'].append({
                        'path': file_path,
                        'size': file_size,
                        'reason': '包含敏感数据或配置信息'
                    })
        
        # 扫描中风险文件
        for pattern in medium_risk_patterns:
            files = glob.glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    self.sensitive_files['medium_risk'].append({
                        'path': file_path,
                        'size': file_size,
                        'reason': '测试或分析文件，可能包含真实数据'
                    })
        
        # 扫描低风险文件
        for pattern in low_risk_patterns:
            files = glob.glob(pattern, recursive=True)
            for file_path in files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    self.sensitive_files['low_risk'].append({
                        'path': file_path,
                        'size': file_size,
                        'reason': '临时文件或文档，建议排除'
                    })
    
    def scan_by_content(self):
        """按文件内容扫描敏感信息"""
        print(f"\n🔍 按内容扫描敏感信息")
        print("-" * 50)
        
        # 敏感内容模式
        sensitive_patterns = {
            'api_domains': r'ct\.womovie\.cn',
            'tokens': r'[a-f0-9]{32}',
            'phone_numbers': r'1[3-9]\d{9}',
            'ip_addresses': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        }
        
        # 扫描Python文件
        python_files = glob.glob('*.py', recursive=True)
        content_sensitive_files = []
        
        for file_path in python_files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    found_patterns = []
                    for pattern_name, pattern in sensitive_patterns.items():
                        matches = re.findall(pattern, content)
                        if matches:
                            found_patterns.append(f"{pattern_name}: {len(matches)}处")
                    
                    if found_patterns:
                        content_sensitive_files.append({
                            'path': file_path,
                            'patterns': found_patterns,
                            'size': os.path.getsize(file_path)
                        })
                        
                except Exception as e:
                    print(f"⚠️ 无法读取文件 {file_path}: {e}")
        
        return content_sensitive_files
    
    def check_specific_directories(self):
        """检查特定目录"""
        print(f"\n🔍 检查特定目录")
        print("-" * 50)
        
        sensitive_dirs = [
            'data/',
            'logs/',
            'temp/',
            'tmp/',
            '__pycache__/',
            '.git/',
            '.vscode/',
            '.idea/',
            '../票根/',
            '票根/',
        ]
        
        found_dirs = []
        for dir_path in sensitive_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                # 计算目录大小
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.exists(file_path):
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                
                found_dirs.append({
                    'path': dir_path,
                    'size': total_size,
                    'file_count': file_count,
                    'reason': '可能包含敏感数据或临时文件'
                })
        
        return found_dirs
    
    def generate_report(self):
        """生成扫描报告"""
        print(f"\n" + "=" * 80)
        print("📋 敏感文件扫描报告")
        print("=" * 80)
        
        # 按文件名扫描
        self.scan_by_filename_patterns()
        
        # 按内容扫描
        content_files = self.scan_by_content()
        
        # 检查目录
        sensitive_dirs = self.check_specific_directories()
        
        # 输出高风险文件
        if self.sensitive_files['high_risk']:
            print(f"\n🔴 高风险文件 ({len(self.sensitive_files['high_risk'])} 个) - 绝对不能上传:")
            total_size = 0
            for file_info in self.sensitive_files['high_risk']:
                print(f"  • {file_info['path']} ({file_info['size']} bytes)")
                print(f"    原因: {file_info['reason']}")
                total_size += file_info['size']
            print(f"  总大小: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        
        # 输出中风险文件
        if self.sensitive_files['medium_risk']:
            print(f"\n🟡 中风险文件 ({len(self.sensitive_files['medium_risk'])} 个) - 需要审查:")
            for file_info in self.sensitive_files['medium_risk'][:10]:  # 只显示前10个
                print(f"  • {file_info['path']} ({file_info['size']} bytes)")
            if len(self.sensitive_files['medium_risk']) > 10:
                print(f"  ... 还有 {len(self.sensitive_files['medium_risk']) - 10} 个文件")
        
        # 输出低风险文件
        if self.sensitive_files['low_risk']:
            print(f"\n🟢 低风险文件 ({len(self.sensitive_files['low_risk'])} 个) - 建议排除:")
            for file_info in self.sensitive_files['low_risk'][:5]:  # 只显示前5个
                print(f"  • {file_info['path']} ({file_info['size']} bytes)")
            if len(self.sensitive_files['low_risk']) > 5:
                print(f"  ... 还有 {len(self.sensitive_files['low_risk']) - 5} 个文件")
        
        # 输出内容敏感文件
        if content_files:
            print(f"\n🔍 内容包含敏感信息的文件 ({len(content_files)} 个):")
            for file_info in content_files[:10]:  # 只显示前10个
                print(f"  • {file_info['path']}")
                print(f"    发现: {', '.join(file_info['patterns'])}")
            if len(content_files) > 10:
                print(f"  ... 还有 {len(content_files) - 10} 个文件")
        
        # 输出敏感目录
        if sensitive_dirs:
            print(f"\n📁 敏感目录 ({len(sensitive_dirs)} 个):")
            for dir_info in sensitive_dirs:
                print(f"  • {dir_info['path']} ({dir_info['file_count']} 文件, {dir_info['size']:,} bytes)")
                print(f"    原因: {dir_info['reason']}")
        
        return {
            'high_risk': self.sensitive_files['high_risk'],
            'medium_risk': self.sensitive_files['medium_risk'],
            'low_risk': self.sensitive_files['low_risk'],
            'content_sensitive': content_files,
            'sensitive_dirs': sensitive_dirs
        }
    
    def generate_gitignore_recommendations(self, scan_results):
        """生成.gitignore建议"""
        print(f"\n" + "=" * 80)
        print("📄 .gitignore 建议更新")
        print("=" * 80)
        
        gitignore_additions = set()
        
        # 从高风险文件中提取模式
        for file_info in scan_results['high_risk']:
            path = file_info['path']
            if path.endswith('.har'):
                gitignore_additions.add('*.har')
            elif 'accounts.json' in path:
                gitignore_additions.add('accounts.json')
                gitignore_additions.add('data/accounts.json')
            elif path == '.env':
                gitignore_additions.add('.env')
            elif path.endswith('.log'):
                gitignore_additions.add('*.log')
        
        # 从中风险文件中提取模式
        for file_info in scan_results['medium_risk']:
            path = file_info['path']
            if path.startswith('test_'):
                gitignore_additions.add('test_*.py')
            elif path.endswith('_test.py'):
                gitignore_additions.add('*_test.py')
            elif path.startswith('debug_'):
                gitignore_additions.add('debug_*.py')
            elif path.startswith('analyze_'):
                gitignore_additions.add('analyze_*.py')
        
        # 从敏感目录中提取模式
        for dir_info in scan_results['sensitive_dirs']:
            path = dir_info['path']
            gitignore_additions.add(path)
            if not path.endswith('/'):
                gitignore_additions.add(path + '/')
        
        if gitignore_additions:
            print("建议添加到 .gitignore 的内容:")
            for pattern in sorted(gitignore_additions):
                print(f"  {pattern}")
        else:
            print("当前 .gitignore 已经足够完善")

def main():
    """主函数"""
    scanner = SensitiveFileScanner()
    
    print("🛡️ 沃美电影院项目敏感文件全面扫描")
    print("=" * 80)
    print("扫描目标: 识别所有不能上传到GitHub的文件")
    
    # 生成扫描报告
    scan_results = scanner.generate_report()
    
    # 生成.gitignore建议
    scanner.generate_gitignore_recommendations(scan_results)
    
    # 总结
    print(f"\n" + "=" * 80)
    print("📊 扫描总结")
    print("=" * 80)
    
    total_high = len(scan_results['high_risk'])
    total_medium = len(scan_results['medium_risk'])
    total_low = len(scan_results['low_risk'])
    total_content = len(scan_results['content_sensitive'])
    total_dirs = len(scan_results['sensitive_dirs'])
    
    print(f"🔴 高风险文件: {total_high} 个 (绝对不能上传)")
    print(f"🟡 中风险文件: {total_medium} 个 (需要审查)")
    print(f"🟢 低风险文件: {total_low} 个 (建议排除)")
    print(f"🔍 内容敏感文件: {total_content} 个 (包含敏感信息)")
    print(f"📁 敏感目录: {total_dirs} 个 (需要排除)")
    
    if total_high > 0:
        print(f"\n⚠️ 警告: 发现 {total_high} 个高风险文件，必须在上传前删除或排除！")
    else:
        print(f"\n✅ 未发现高风险文件")
    
    print(f"\n💡 建议:")
    print(f"  1. 立即删除或排除所有高风险文件")
    print(f"  2. 审查中风险文件，确定是否需要保留")
    print(f"  3. 更新 .gitignore 文件")
    print(f"  4. 运行 git status 确认敏感文件已被排除")

if __name__ == "__main__":
    main()
