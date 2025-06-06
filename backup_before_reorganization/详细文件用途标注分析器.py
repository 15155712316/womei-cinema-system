#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 详细文件用途标注分析器
对根目录下每个文件进行详细的用途分析和分类标注
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class DetailedFileAnnotator:
    """详细文件标注分析器"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.files_analysis = []
        
        # 加载之前的分析结果
        self.previous_analysis = self._load_previous_analysis()
        
        # 详细的文件用途数据库
        self.file_purposes = {
            # 核心业务文件
            'main_modular.py': {
                'purpose': '主程序文件 - 模块化主窗口实现，包含完整的电影票务业务逻辑',
                'type': 'core_business',
                'importance': 'critical',
                'frequency': 'daily',
                'dependencies': '被整个系统依赖，是程序入口点',
                'details': '4425行代码，实现用户认证、影院管理、座位选择、订单处理、支付系统等核心功能'
            },
            'main.py': {
                'purpose': '原始主程序文件 - 简化版本的程序入口',
                'type': 'core_business',
                'importance': 'critical',
                'frequency': 'occasional',
                'dependencies': '可能被某些启动脚本调用',
                'details': '较小的主程序版本，可能用于测试或简化启动'
            },
            'requirements.txt': {
                'purpose': 'Python依赖包列表 - 定义项目所需的第三方库',
                'type': 'config',
                'importance': 'important',
                'frequency': 'occasional',
                'dependencies': '被pip install和构建脚本使用',
                'details': '包含PyQt5、requests等关键依赖包的版本信息'
            },
            'CinemaTicketSystem.spec': {
                'purpose': 'PyInstaller打包配置文件 - 定义可执行文件生成规则',
                'type': 'build',
                'importance': 'important',
                'frequency': 'occasional',
                'dependencies': '被PyInstaller和构建脚本使用',
                'details': '配置打包参数、图标、隐藏导入等'
            },
            'build_info.json': {
                'purpose': '构建信息配置 - 记录版本号、构建时间等元数据',
                'type': 'config',
                'importance': 'important',
                'frequency': 'occasional',
                'dependencies': '被构建脚本和版本管理使用',
                'details': '包含版本号、构建时间戳等构建相关信息'
            },
            '一键打包.bat': {
                'purpose': 'Windows批处理脚本 - 自动化打包流程',
                'type': 'build',
                'importance': 'important',
                'frequency': 'occasional',
                'dependencies': '依赖PyInstaller和spec文件',
                'details': '简化打包操作，一键生成可执行文件'
            },
            'README.md': {
                'purpose': '项目说明文档 - 项目概述、安装和使用指南',
                'type': 'documentation',
                'importance': 'important',
                'frequency': 'occasional',
                'dependencies': '被开发者和用户参考',
                'details': '项目的主要说明文档，包含基本信息和使用方法'
            },
            'api_validation_report.json': {
                'purpose': 'API验证报告 - 记录API接口的验证结果',
                'type': 'data',
                'importance': 'important',
                'frequency': 'archive',
                'dependencies': '被API验证工具生成和读取',
                'details': '包含API接口的测试结果和验证状态'
            }
        }
        
        # 文件模式匹配规则
        self.pattern_rules = {
            # 分析工具
            r'.*analyzer.*\.py$': {
                'type': 'tool',
                'purpose': '代码分析工具',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            r'.*分析器.*\.py$': {
                'type': 'tool',
                'purpose': '中文命名的分析工具',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            # 修复脚本
            r'^fix_.*\.py$': {
                'type': 'tool',
                'purpose': '问题修复脚本',
                'importance': 'optional',
                'frequency': 'archive'
            },
            r'^quick_.*\.py$': {
                'type': 'tool',
                'purpose': '快速修复脚本',
                'importance': 'optional',
                'frequency': 'archive'
            },
            # 测试脚本
            r'^test_.*\.py$': {
                'type': 'test',
                'purpose': '单元测试脚本',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            r'^check_.*\.py$': {
                'type': 'test',
                'purpose': '检查验证脚本',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            # 报告文档
            r'.*报告\.md$': {
                'type': 'documentation',
                'purpose': '分析报告文档',
                'importance': 'optional',
                'frequency': 'archive'
            },
            r'.*总结\.md$': {
                'type': 'documentation',
                'purpose': '总结文档',
                'importance': 'optional',
                'frequency': 'archive'
            },
            # 支付相关
            r'.*payment.*\.py$': {
                'type': 'tool',
                'purpose': '支付系统相关脚本',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            # HAR文件
            r'.*\.har$': {
                'type': 'data',
                'purpose': 'HTTP请求记录文件',
                'importance': 'optional',
                'frequency': 'archive'
            },
            # 图表文件
            r'.*\.mmd$': {
                'type': 'documentation',
                'purpose': 'Mermaid图表源码',
                'importance': 'optional',
                'frequency': 'occasional'
            },
            # 配置文件
            r'.*\.json$': {
                'type': 'config',
                'purpose': 'JSON配置或数据文件',
                'importance': 'optional',
                'frequency': 'occasional'
            }
        }
    
    def _load_previous_analysis(self) -> Dict:
        """加载之前的分析结果"""
        try:
            with open('项目文件清理分析结果.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'files': []}
    
    def _get_file_from_previous_analysis(self, filename: str) -> Dict:
        """从之前的分析中获取文件信息"""
        for file_info in self.previous_analysis.get('files', []):
            if file_info['name'] == filename:
                return file_info
        return {}
    
    def _analyze_file_content(self, file_path: Path) -> Dict:
        """分析文件内容获取更多信息"""
        analysis = {
            'line_count': 0,
            'has_main_function': False,
            'imports': [],
            'classes': [],
            'functions': []
        }
        
        if file_path.suffix == '.py':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    analysis['line_count'] = len(lines)
                    
                    # 检查是否有main函数
                    if 'if __name__ == "__main__"' in content:
                        analysis['has_main_function'] = True
                    
                    # 简单提取导入和类名
                    for line in lines:
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            analysis['imports'].append(line)
                        elif line.startswith('class '):
                            class_name = line.split('(')[0].replace('class ', '').strip(':')
                            analysis['classes'].append(class_name)
                        elif line.startswith('def ') and not line.startswith('def _'):
                            func_name = line.split('(')[0].replace('def ', '')
                            analysis['functions'].append(func_name)
            except:
                pass
        
        return analysis
    
    def _determine_detailed_purpose(self, file_path: Path, previous_info: Dict, content_analysis: Dict) -> Dict:
        """确定文件的详细用途"""
        filename = file_path.name
        
        # 检查预定义的文件用途
        if filename in self.file_purposes:
            return self.file_purposes[filename]
        
        # 使用模式匹配
        for pattern, info in self.pattern_rules.items():
            if re.match(pattern, filename, re.IGNORECASE):
                purpose_info = info.copy()
                
                # 根据文件内容细化用途描述
                if file_path.suffix == '.py' and content_analysis['line_count'] > 0:
                    purpose_info['details'] = f"{content_analysis['line_count']}行代码"
                    if content_analysis['has_main_function']:
                        purpose_info['details'] += "，包含主函数，可独立运行"
                    if content_analysis['classes']:
                        purpose_info['details'] += f"，定义了{len(content_analysis['classes'])}个类"
                
                return purpose_info
        
        # 基于文件名和内容的启发式分析
        filename_lower = filename.lower()
        
        # 特殊文件类型处理
        if filename == '.cursorrules':
            return {
                'purpose': 'Cursor编辑器配置文件 - 定义AI助手的行为规则',
                'type': 'config',
                'importance': 'optional',
                'frequency': 'occasional',
                'details': 'AI编程助手的配置规则文件'
            }
        elif filename == 'cacert.pem':
            return {
                'purpose': 'CA证书文件 - SSL/TLS连接的根证书',
                'type': 'security',
                'importance': 'optional',
                'frequency': 'occasional',
                'details': 'HTTPS请求验证用的证书文件'
            }
        elif filename.endswith('.ps1'):
            return {
                'purpose': 'PowerShell脚本 - Windows自动化脚本',
                'type': 'tool',
                'importance': 'optional',
                'frequency': 'occasional',
                'details': 'Windows PowerShell自动化脚本'
            }
        elif filename.endswith('.html'):
            return {
                'purpose': 'HTML文档 - 网页格式的文档或报告',
                'type': 'documentation',
                'importance': 'optional',
                'frequency': 'occasional',
                'details': '网页格式的文档展示'
            }
        elif filename.endswith('.png') or filename.endswith('.jpg'):
            return {
                'purpose': '图片文件 - 截图、图标或示例图片',
                'type': 'media',
                'importance': 'optional',
                'frequency': 'archive',
                'details': '项目相关的图片资源'
            }
        
        # 默认分析
        return {
            'purpose': '待详细分析的文件',
            'type': 'unknown',
            'importance': 'optional',
            'frequency': 'occasional',
            'details': '需要进一步分析确定具体用途'
        }
    
    def _determine_cleanup_suggestion(self, file_info: Dict, purpose_info: Dict) -> str:
        """确定清理建议"""
        importance = purpose_info.get('importance', 'optional')
        file_type = purpose_info.get('type', 'unknown')
        frequency = purpose_info.get('frequency', 'occasional')
        
        if importance == 'critical':
            return 'keep - 核心文件必须保留'
        elif importance == 'important':
            return 'keep - 重要文件建议保留'
        elif file_type == 'tool' and frequency == 'archive':
            return 'archive - 工具脚本建议归档'
        elif file_type == 'documentation' and frequency == 'archive':
            return 'archive - 文档建议归档'
        elif file_type == 'test':
            return 'organize - 测试文件建议整理到tests目录'
        elif file_type == 'data' and frequency == 'archive':
            return 'archive - 数据文件建议归档'
        elif frequency == 'deprecated':
            return 'delete - 废弃文件可以删除'
        else:
            return 'review - 需要人工审查决定'
    
    def analyze_all_files(self):
        """分析所有文件"""
        print("🔍 开始详细文件用途标注分析...")
        
        for file_path in self.root_dir.iterdir():
            if file_path.is_file():
                # 获取基本信息
                stat = file_path.stat()
                previous_info = self._get_file_from_previous_analysis(file_path.name)
                content_analysis = self._analyze_file_content(file_path)
                
                # 确定详细用途
                purpose_info = self._determine_detailed_purpose(file_path, previous_info, content_analysis)
                
                # 构建完整的文件信息
                file_analysis = {
                    'filename': file_path.name,
                    'size_bytes': stat.st_size,
                    'size_mb': round(stat.st_size / (1024 * 1024), 3),
                    'modified_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'file_type': purpose_info.get('type', 'unknown'),
                    'purpose': purpose_info.get('purpose', '待确定用途'),
                    'importance': purpose_info.get('importance', 'optional'),
                    'frequency': purpose_info.get('frequency', 'occasional'),
                    'dependencies': purpose_info.get('dependencies', '无明确依赖'),
                    'details': purpose_info.get('details', ''),
                    'cleanup_suggestion': self._determine_cleanup_suggestion(previous_info, purpose_info),
                    'content_analysis': content_analysis
                }
                
                self.files_analysis.append(file_analysis)
        
        # 按文件名排序
        self.files_analysis.sort(key=lambda x: x['filename'].lower())
        
        print(f"✅ 完成 {len(self.files_analysis)} 个文件的详细分析")
    
    def generate_detailed_report(self):
        """生成详细报告"""
        report = {
            'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_files': len(self.files_analysis),
            'files': self.files_analysis,
            'statistics': self._generate_statistics()
        }
        
        # 保存详细分析结果
        with open('详细文件用途标注结果.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def _generate_statistics(self) -> Dict:
        """生成统计信息"""
        stats = {
            'by_type': {},
            'by_importance': {},
            'by_frequency': {},
            'by_cleanup_action': {}
        }
        
        for file_info in self.files_analysis:
            # 按类型统计
            file_type = file_info['file_type']
            if file_type not in stats['by_type']:
                stats['by_type'][file_type] = {'count': 0, 'size_mb': 0}
            stats['by_type'][file_type]['count'] += 1
            stats['by_type'][file_type]['size_mb'] += file_info['size_mb']
            
            # 按重要性统计
            importance = file_info['importance']
            if importance not in stats['by_importance']:
                stats['by_importance'][importance] = {'count': 0, 'size_mb': 0}
            stats['by_importance'][importance]['count'] += 1
            stats['by_importance'][importance]['size_mb'] += file_info['size_mb']
            
            # 按使用频率统计
            frequency = file_info['frequency']
            if frequency not in stats['by_frequency']:
                stats['by_frequency'][frequency] = {'count': 0, 'size_mb': 0}
            stats['by_frequency'][frequency]['count'] += 1
            stats['by_frequency'][frequency]['size_mb'] += file_info['size_mb']
            
            # 按清理操作统计
            cleanup = file_info['cleanup_suggestion'].split(' - ')[0]
            if cleanup not in stats['by_cleanup_action']:
                stats['by_cleanup_action'][cleanup] = {'count': 0, 'size_mb': 0}
            stats['by_cleanup_action'][cleanup]['count'] += 1
            stats['by_cleanup_action'][cleanup]['size_mb'] += file_info['size_mb']
        
        return stats

def main():
    """主函数"""
    print("🎬 PyQt5电影票务管理系统 - 详细文件用途标注分析")
    print("=" * 60)
    
    annotator = DetailedFileAnnotator()
    annotator.analyze_all_files()
    report = annotator.generate_detailed_report()
    
    # 显示统计摘要
    stats = report['statistics']
    print(f"\n📊 分析统计:")
    print(f"  总文件数: {report['total_files']}")
    print(f"  文件类型: {len(stats['by_type'])} 种")
    print(f"  重要性分级: {len(stats['by_importance'])} 级")
    print(f"  使用频率: {len(stats['by_frequency'])} 种")
    
    print(f"\n✅ 详细分析完成！结果已保存到: 详细文件用途标注结果.json")

if __name__ == "__main__":
    main()
