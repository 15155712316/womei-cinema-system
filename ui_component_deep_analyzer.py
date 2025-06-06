#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件深度清理分析器
专门分析剩余3个UI文件的使用情况
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set

class UIComponentDeepAnalyzer:
    """UI组件深度分析器"""
    
    def __init__(self):
        self.target_files = [
            'ui/components/auto_browser.py',
            'ui/dialogs/auto_parameter_extractor.py', 
            'ui/interfaces/plugin_interface.py'
        ]
        self.all_python_files = []
        self.analysis_results = {}
        
    def scan_project(self):
        """扫描项目文件"""
        print("🔍 扫描项目文件...")
        
        for py_file in Path('.').rglob("*.py"):
            if self._should_include_file(py_file):
                self.all_python_files.append(py_file)
        
        print(f"📁 发现 {len(self.all_python_files)} 个Python文件")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """判断是否应该包含此文件"""
        exclude_dirs = {'.git', '__pycache__', 'build', 'dist', 'copy'}
        return not any(part in exclude_dirs for part in file_path.parts)
    
    def analyze_file_usage(self, target_file: str):
        """分析单个文件的使用情况"""
        print(f"\n🔍 分析文件: {target_file}")
        
        if not os.path.exists(target_file):
            return {
                'exists': False,
                'classes': [],
                'functions': [],
                'references': [],
                'imports': []
            }
        
        # 分析文件内容
        classes, functions = self._analyze_file_content(target_file)
        
        # 搜索引用
        references = self._find_references(target_file, classes, functions)
        
        # 搜索导入
        imports = self._find_imports(target_file)
        
        result = {
            'exists': True,
            'classes': classes,
            'functions': functions,
            'references': references,
            'imports': imports,
            'file_size': os.path.getsize(target_file),
            'line_count': self._count_lines(target_file)
        }
        
        return result
    
    def _analyze_file_content(self, file_path: str):
        """分析文件内容，提取类和函数"""
        classes = []
        functions = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [self._get_base_name(base) for base in node.bases]
                    })
                elif isinstance(node, ast.FunctionDef):
                    # 只记录模块级函数，不记录类方法
                    if not self._is_class_method(node, tree):
                        functions.append({
                            'name': node.name,
                            'line': node.lineno
                        })
        
        except Exception as e:
            print(f"⚠️ 解析文件失败 {file_path}: {e}")
        
        return classes, functions
    
    def _get_base_name(self, base_node) -> str:
        """获取基类名称"""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{base_node.value.id}.{base_node.attr}" if hasattr(base_node.value, 'id') else base_node.attr
        return "Unknown"
    
    def _is_class_method(self, func_node, tree) -> bool:
        """判断函数是否是类方法"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item == func_node:
                        return True
        return False
    
    def _find_references(self, target_file: str, classes: List, functions: List):
        """查找对文件中类和函数的引用"""
        references = []
        
        # 提取文件名（不含扩展名）
        file_name = os.path.basename(target_file).replace('.py', '')
        
        # 搜索模式
        search_patterns = [file_name]
        
        # 添加类名和函数名到搜索模式
        for cls in classes:
            search_patterns.append(cls['name'])
        for func in functions:
            search_patterns.append(func['name'])
        
        # 在所有文件中搜索
        for py_file in self.all_python_files:
            if str(py_file) == target_file:
                continue  # 跳过自身
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in search_patterns:
                    if re.search(rf'\b{re.escape(pattern)}\b', content):
                        references.append({
                            'file': str(py_file),
                            'pattern': pattern,
                            'type': 'reference'
                        })
                        break  # 找到一个引用就够了
                        
            except Exception as e:
                continue
        
        return references
    
    def _find_imports(self, target_file: str):
        """查找对文件的导入"""
        imports = []
        
        # 构建导入模式
        file_path_parts = target_file.replace('/', '.').replace('\\', '.').replace('.py', '')
        import_patterns = [
            f"from {file_path_parts} import",
            f"import {file_path_parts}",
            file_path_parts.split('.')[-1]  # 文件名
        ]
        
        for py_file in self.all_python_files:
            if str(py_file) == target_file:
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in import_patterns:
                    if pattern in content:
                        imports.append({
                            'file': str(py_file),
                            'pattern': pattern
                        })
                        break
                        
            except Exception as e:
                continue
        
        return imports
    
    def _count_lines(self, file_path: str) -> int:
        """计算文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    
    def analyze_all_files(self):
        """分析所有目标文件"""
        print("🎬 开始深度UI组件分析...")
        
        self.scan_project()
        
        for target_file in self.target_files:
            result = self.analyze_file_usage(target_file)
            self.analysis_results[target_file] = result
    
    def generate_report(self):
        """生成分析报告"""
        print("\n📊 生成深度分析报告...")
        
        report = {
            'summary': {
                'total_files_analyzed': len(self.target_files),
                'existing_files': sum(1 for r in self.analysis_results.values() if r['exists'])
            },
            'file_analysis': self.analysis_results,
            'cleanup_recommendations': []
        }
        
        # 生成清理建议
        for file_path, analysis in self.analysis_results.items():
            if not analysis['exists']:
                continue
            
            recommendation = {
                'file': file_path,
                'action': 'unknown',
                'reason': '',
                'risk_level': 'medium',
                'estimated_lines_saved': analysis['line_count']
            }
            
            # 判断清理策略
            if not analysis['references'] and not analysis['imports']:
                recommendation['action'] = 'delete_entire_file'
                recommendation['reason'] = '文件完全未被使用'
                recommendation['risk_level'] = 'low'
            elif len(analysis['references']) <= 2:
                recommendation['action'] = 'cleanup_unused_classes'
                recommendation['reason'] = '文件部分使用，可清理未使用的类'
                recommendation['risk_level'] = 'medium'
            else:
                recommendation['action'] = 'keep_file'
                recommendation['reason'] = '文件被多处引用，建议保留'
                recommendation['risk_level'] = 'high'
            
            report['cleanup_recommendations'].append(recommendation)
        
        return report

def main():
    """主函数"""
    analyzer = UIComponentDeepAnalyzer()
    analyzer.analyze_all_files()
    report = analyzer.generate_report()
    
    # 显示结果
    print("\n" + "="*60)
    print("📊 UI组件深度分析结果")
    print("="*60)
    
    for file_path, analysis in report['file_analysis'].items():
        print(f"\n📁 文件: {file_path}")
        
        if not analysis['exists']:
            print("   ❌ 文件不存在")
            continue
        
        print(f"   📏 大小: {analysis['file_size']} 字节")
        print(f"   📄 行数: {analysis['line_count']} 行")
        print(f"   🏗️  类数量: {len(analysis['classes'])}")
        print(f"   ⚙️  函数数量: {len(analysis['functions'])}")
        print(f"   🔗 引用数量: {len(analysis['references'])}")
        print(f"   📥 导入数量: {len(analysis['imports'])}")
        
        if analysis['classes']:
            print("   📋 定义的类:")
            for cls in analysis['classes']:
                print(f"      - {cls['name']} (第{cls['line']}行)")
        
        if analysis['references']:
            print("   🔗 被引用的文件:")
            for ref in analysis['references'][:3]:  # 只显示前3个
                print(f"      - {ref['file']}")
    
    print("\n" + "="*60)
    print("🎯 清理建议")
    print("="*60)
    
    for rec in report['cleanup_recommendations']:
        risk_color = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
        print(f"\n{risk_color.get(rec['risk_level'], '⚪')} {rec['file']}")
        print(f"   操作: {rec['action']}")
        print(f"   原因: {rec['reason']}")
        print(f"   风险: {rec['risk_level']}")
        print(f"   预计减少: {rec['estimated_lines_saved']} 行")
    
    # 保存详细报告
    import json
    with open('ui_deep_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 详细报告已保存到: ui_deep_analysis_report.json")

if __name__ == "__main__":
    main()
