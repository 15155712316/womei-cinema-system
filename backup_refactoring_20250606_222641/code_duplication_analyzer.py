#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 代码重复和冗余分析器
全面检测代码重复、接口冗余和资源浪费
"""

import os
import re
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import difflib

class CodeDuplicationAnalyzer:
    """代码重复和冗余分析器"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.main_file = "main_modular.py"
        self.core_dirs = ["services", "ui", "utils", "modules", "controllers", "views", "widgets"]
        
        self.analysis_results = {
            'duplicate_methods': [],
            'duplicate_code_blocks': [],
            'redundant_imports': [],
            'redundant_apis': [],
            'unused_resources': [],
            'similar_functions': [],
            'optimization_suggestions': [],
            'refactoring_plan': {}
        }
        
        self.code_blocks = {}  # 存储代码块的哈希值
        self.method_signatures = {}  # 存储方法签名
        self.import_usage = defaultdict(list)  # 导入使用情况
        self.api_usage = defaultdict(int)  # API使用频率
    
    def analyze_main_program_duplicates(self):
        """分析主程序中的重复代码"""
        print("🔍 分析主程序代码重复...")
        
        if not Path(self.main_file).exists():
            print(f"❌ 主程序文件不存在: {self.main_file}")
            return
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 分析方法重复
            self._analyze_method_duplicates(content, self.main_file)
            
            # 分析代码块重复
            self._analyze_code_block_duplicates(content, self.main_file)
            
            # 分析导入重复
            self._analyze_import_duplicates(content, self.main_file)
            
            print(f"✅ 主程序重复分析完成")
            
        except Exception as e:
            print(f"❌ 主程序分析失败: {e}")
    
    def _analyze_method_duplicates(self, content: str, file_path: str):
        """分析方法重复"""
        # 提取所有方法
        method_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n((?:\s{4,}.*\n)*)'
        methods = re.finditer(method_pattern, content, re.MULTILINE)
        
        method_bodies = {}
        for match in methods:
            method_name = match.group(1)
            method_body = match.group(2)
            
            # 标准化方法体（去除空白和注释）
            normalized_body = self._normalize_code(method_body)
            body_hash = hashlib.md5(normalized_body.encode()).hexdigest()
            
            if body_hash in method_bodies:
                # 发现重复方法
                self.analysis_results['duplicate_methods'].append({
                    'file1': method_bodies[body_hash]['file'],
                    'method1': method_bodies[body_hash]['name'],
                    'file2': file_path,
                    'method2': method_name,
                    'similarity': 100,
                    'body_hash': body_hash,
                    'lines': len(method_body.split('\n'))
                })
            else:
                method_bodies[body_hash] = {
                    'file': file_path,
                    'name': method_name,
                    'body': method_body
                }
        
        # 检查相似方法（不完全相同但高度相似）
        self._find_similar_methods(method_bodies, file_path)
    
    def _analyze_code_block_duplicates(self, content: str, file_path: str):
        """分析代码块重复"""
        lines = content.split('\n')
        
        # 分析连续的代码块（5行以上）
        for i in range(len(lines) - 5):
            block = '\n'.join(lines[i:i+5])
            normalized_block = self._normalize_code(block)
            
            if len(normalized_block.strip()) < 50:  # 跳过太短的块
                continue
            
            block_hash = hashlib.md5(normalized_block.encode()).hexdigest()
            
            if block_hash in self.code_blocks:
                self.analysis_results['duplicate_code_blocks'].append({
                    'file1': self.code_blocks[block_hash]['file'],
                    'lines1': self.code_blocks[block_hash]['lines'],
                    'file2': file_path,
                    'lines2': f"{i+1}-{i+5}",
                    'block_hash': block_hash,
                    'content': block[:100] + "..." if len(block) > 100 else block
                })
            else:
                self.code_blocks[block_hash] = {
                    'file': file_path,
                    'lines': f"{i+1}-{i+5}",
                    'content': block
                }
    
    def _analyze_import_duplicates(self, content: str, file_path: str):
        """分析导入重复"""
        import_pattern = r'^(from\s+[\w.]+\s+import\s+[\w,\s*]+|import\s+[\w.,\s]+)'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        
        import_counts = Counter(imports)
        for imp, count in import_counts.items():
            if count > 1:
                self.analysis_results['redundant_imports'].append({
                    'file': file_path,
                    'import': imp,
                    'count': count
                })
    
    def _normalize_code(self, code: str) -> str:
        """标准化代码（去除空白、注释等）"""
        # 去除注释
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        # 去除多余空白
        code = re.sub(r'\s+', ' ', code)
        # 去除空行
        code = '\n'.join(line.strip() for line in code.split('\n') if line.strip())
        return code.strip()
    
    def _find_similar_methods(self, method_bodies: Dict, file_path: str):
        """查找相似方法"""
        bodies_list = list(method_bodies.values())
        
        for i, method1 in enumerate(bodies_list):
            for j, method2 in enumerate(bodies_list[i+1:], i+1):
                similarity = self._calculate_similarity(method1['body'], method2['body'])
                
                if similarity > 70:  # 相似度超过70%
                    self.analysis_results['similar_functions'].append({
                        'file1': method1['file'],
                        'method1': method1['name'],
                        'file2': method2['file'],
                        'method2': method2['name'],
                        'similarity': similarity
                    })
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        normalized1 = self._normalize_code(text1)
        normalized2 = self._normalize_code(text2)
        
        matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
        return matcher.ratio() * 100
    
    def analyze_directory_duplicates(self):
        """分析目录中的重复代码"""
        print("🔍 分析目录代码重复...")
        
        for dir_name in self.core_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                self._analyze_directory(dir_path)
                print(f"✅ 分析完成: {dir_name}")
    
    def _analyze_directory(self, dir_path: Path):
        """分析单个目录"""
        for file_path in dir_path.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self._analyze_method_duplicates(content, str(file_path))
                self._analyze_code_block_duplicates(content, str(file_path))
                self._analyze_import_duplicates(content, str(file_path))
                self._analyze_api_usage(content, str(file_path))
                
            except Exception as e:
                print(f"⚠️ 分析文件失败 {file_path}: {e}")
    
    def _analyze_api_usage(self, content: str, file_path: str):
        """分析API使用情况"""
        # 查找API调用模式
        api_patterns = [
            r'def\s+(api_\w+)',  # API方法定义
            r'(\w+\.api_\w+)',   # API方法调用
            r'(requests\.\w+)',  # requests调用
            r'(\w+_api\(\w*\))'  # API函数调用
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                self.api_usage[match] += 1
    
    def analyze_redundant_apis(self):
        """分析冗余API"""
        print("🔍 分析冗余API接口...")
        
        # 查找使用频率低的API
        low_usage_apis = {api: count for api, count in self.api_usage.items() 
                         if count <= 1 and 'api' in api.lower()}
        
        # 查找功能重叠的API
        api_groups = self._group_similar_apis()
        
        self.analysis_results['redundant_apis'] = {
            'low_usage': low_usage_apis,
            'similar_groups': api_groups
        }
        
        print(f"✅ 发现 {len(low_usage_apis)} 个低使用API")
    
    def _group_similar_apis(self) -> List[List[str]]:
        """将相似的API分组"""
        apis = [api for api in self.api_usage.keys() if 'api' in api.lower()]
        groups = []
        
        for api in apis:
            # 简单的相似性检查（基于名称）
            similar_apis = [a for a in apis if a != api and 
                          self._api_name_similarity(api, a) > 0.7]
            
            if similar_apis:
                group = [api] + similar_apis
                if group not in groups:
                    groups.append(group)
        
        return groups
    
    def _api_name_similarity(self, name1: str, name2: str) -> float:
        """计算API名称相似度"""
        # 提取关键词
        words1 = set(re.findall(r'\w+', name1.lower()))
        words2 = set(re.findall(r'\w+', name2.lower()))
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def analyze_unused_resources(self):
        """分析未使用的资源"""
        print("🔍 分析未使用资源...")
        
        # 分析未使用的导入
        self._find_unused_imports()
        
        # 分析未使用的方法
        self._find_unused_methods()
        
        print("✅ 未使用资源分析完成")
    
    def _find_unused_imports(self):
        """查找未使用的导入"""
        for dir_name in self.core_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob("*.py"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取导入
                    imports = re.findall(r'from\s+([\w.]+)\s+import\s+([\w,\s*]+)', content)
                    imports.extend(re.findall(r'import\s+([\w.,\s]+)', content))
                    
                    # 检查使用情况
                    for imp in imports:
                        if isinstance(imp, tuple):
                            module, items = imp
                            for item in items.split(','):
                                item = item.strip()
                                if item and item not in content[content.find(f'import {item}') + 20:]:
                                    self.analysis_results['unused_resources'].append({
                                        'type': 'import',
                                        'file': str(file_path),
                                        'resource': f"{module}.{item}",
                                        'reason': 'imported but not used'
                                    })
                        else:
                            module = imp.strip()
                            if module and module not in content[content.find(f'import {module}') + 20:]:
                                self.analysis_results['unused_resources'].append({
                                    'type': 'import',
                                    'file': str(file_path),
                                    'resource': module,
                                    'reason': 'imported but not used'
                                })
                
                except Exception:
                    continue
    
    def _find_unused_methods(self):
        """查找未使用的方法"""
        # 这里实现一个简化版本，实际项目中需要更复杂的分析
        all_methods = set()
        method_calls = set()
        
        # 收集所有方法定义和调用
        for dir_name in self.core_dirs + ['.']:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue
            
            for file_path in dir_path.rglob("*.py"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 方法定义
                    methods = re.findall(r'def\s+(\w+)', content)
                    all_methods.update(methods)
                    
                    # 方法调用
                    calls = re.findall(r'(\w+)\s*\(', content)
                    method_calls.update(calls)
                
                except Exception:
                    continue
        
        # 找出未被调用的方法
        unused_methods = all_methods - method_calls
        for method in unused_methods:
            if not method.startswith('_'):  # 跳过私有方法
                self.analysis_results['unused_resources'].append({
                    'type': 'method',
                    'resource': method,
                    'reason': 'defined but not called'
                })
    
    def generate_optimization_suggestions(self):
        """生成优化建议"""
        print("🔍 生成优化建议...")
        
        suggestions = []
        
        # 重复方法优化
        if self.analysis_results['duplicate_methods']:
            suggestions.append({
                'type': 'duplicate_methods',
                'priority': 'high',
                'description': f"发现 {len(self.analysis_results['duplicate_methods'])} 个重复方法",
                'action': '提取公共方法到基类或工具模块',
                'estimated_reduction': f"{sum(d['lines'] for d in self.analysis_results['duplicate_methods'])} 行代码"
            })
        
        # 重复代码块优化
        if self.analysis_results['duplicate_code_blocks']:
            suggestions.append({
                'type': 'duplicate_blocks',
                'priority': 'medium',
                'description': f"发现 {len(self.analysis_results['duplicate_code_blocks'])} 个重复代码块",
                'action': '提取为公共函数或常量',
                'estimated_reduction': f"{len(self.analysis_results['duplicate_code_blocks']) * 5} 行代码"
            })
        
        # 冗余导入优化
        if self.analysis_results['redundant_imports']:
            suggestions.append({
                'type': 'redundant_imports',
                'priority': 'low',
                'description': f"发现 {len(self.analysis_results['redundant_imports'])} 个冗余导入",
                'action': '移除重复的导入语句',
                'estimated_reduction': f"{len(self.analysis_results['redundant_imports'])} 行代码"
            })
        
        # 未使用资源优化
        if self.analysis_results['unused_resources']:
            suggestions.append({
                'type': 'unused_resources',
                'priority': 'medium',
                'description': f"发现 {len(self.analysis_results['unused_resources'])} 个未使用资源",
                'action': '移除未使用的导入和方法',
                'estimated_reduction': f"{len(self.analysis_results['unused_resources'])} 个资源"
            })
        
        self.analysis_results['optimization_suggestions'] = suggestions
        print(f"✅ 生成 {len(suggestions)} 个优化建议")
    
    def generate_refactoring_plan(self):
        """生成重构计划"""
        print("🔍 生成重构计划...")
        
        plan = {
            'phase_1': {
                'name': '清理未使用资源',
                'duration': '1-2天',
                'risk': 'low',
                'tasks': [
                    '移除未使用的导入语句',
                    '删除未调用的方法',
                    '清理冗余的变量定义'
                ]
            },
            'phase_2': {
                'name': '合并重复代码块',
                'duration': '2-3天',
                'risk': 'medium',
                'tasks': [
                    '提取重复的代码块为函数',
                    '创建公共常量文件',
                    '统一错误处理逻辑'
                ]
            },
            'phase_3': {
                'name': '重构重复方法',
                'duration': '3-5天',
                'risk': 'high',
                'tasks': [
                    '提取公共方法到基类',
                    '创建工具类和辅助函数',
                    '重构相似的API接口'
                ]
            },
            'phase_4': {
                'name': '优化API接口',
                'duration': '2-3天',
                'risk': 'medium',
                'tasks': [
                    '合并功能重叠的API',
                    '简化API调用链路',
                    '优化API参数设计'
                ]
            }
        }
        
        self.analysis_results['refactoring_plan'] = plan
        print("✅ 重构计划生成完成")
    
    def generate_report(self):
        """生成分析报告"""
        print("📊 生成代码重复分析报告...")
        
        # 计算统计信息
        total_duplicates = (len(self.analysis_results['duplicate_methods']) + 
                          len(self.analysis_results['duplicate_code_blocks']))
        
        total_redundant = (len(self.analysis_results['redundant_imports']) + 
                         len(self.analysis_results['unused_resources']))
        
        # 保存详细报告
        report = {
            'analysis_date': '2025-06-06',
            'summary': {
                'total_duplicates': total_duplicates,
                'total_redundant': total_redundant,
                'optimization_potential': 'high' if total_duplicates > 10 else 'medium'
            },
            'analysis_results': self.analysis_results
        }
        
        with open('code_duplication_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def run_analysis(self):
        """运行完整分析"""
        print("🎬 PyQt5电影票务管理系统 - 代码重复分析")
        print("=" * 60)
        
        self.analyze_main_program_duplicates()
        self.analyze_directory_duplicates()
        self.analyze_redundant_apis()
        self.analyze_unused_resources()
        self.generate_optimization_suggestions()
        self.generate_refactoring_plan()
        
        return self.generate_report()

def main():
    """主函数"""
    analyzer = CodeDuplicationAnalyzer()
    results = analyzer.run_analysis()
    
    # 显示摘要
    summary = results['summary']
    print(f"\n📊 分析摘要:")
    print(f"  发现重复项: {summary['total_duplicates']}")
    print(f"  发现冗余项: {summary['total_redundant']}")
    print(f"  优化潜力: {summary['optimization_potential']}")
    
    print(f"\n✅ 代码重复分析完成！详细报告已保存到: code_duplication_analysis.json")

if __name__ == "__main__":
    main()
