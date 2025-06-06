#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - UI组件使用情况分析器
分析所有UI组件的使用情况，识别未使用的组件
"""

import os
import re
import ast
import json
from typing import Dict, List, Set, Tuple
from pathlib import Path

class UIComponentAnalyzer:
    """UI组件使用情况分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.ui_files = []
        self.all_python_files = []
        self.defined_classes = {}  # 文件路径 -> 类名列表
        self.defined_functions = {}  # 文件路径 -> 函数名列表
        self.imports = {}  # 文件路径 -> 导入信息
        self.references = {}  # 类名/函数名 -> 引用位置列表
        
    def scan_project(self):
        """扫描项目文件"""
        print("🔍 扫描项目文件...")
        
        # 扫描所有Python文件
        for py_file in self.project_root.rglob("*.py"):
            if self._should_include_file(py_file):
                self.all_python_files.append(py_file)
                if py_file.parts[0] == "ui" or "ui" in py_file.parts:
                    self.ui_files.append(py_file)
        
        print(f"📁 发现 {len(self.all_python_files)} 个Python文件")
        print(f"🎨 发现 {len(self.ui_files)} 个UI文件")
    
    def _should_include_file(self, file_path: Path) -> bool:
        """判断是否应该包含此文件"""
        exclude_dirs = {'.git', '__pycache__', 'build', 'dist', 'copy'}
        return not any(part in exclude_dirs for part in file_path.parts)
    
    def analyze_definitions(self):
        """分析所有定义的类和函数"""
        print("🔍 分析类和函数定义...")
        
        for file_path in self.all_python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析AST
                tree = ast.parse(content)
                
                classes = []
                functions = []
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.append({
                            'name': node.name,
                            'line': node.lineno,
                            'bases': [self._get_base_name(base) for base in node.bases]
                        })
                    elif isinstance(node, ast.FunctionDef):
                        functions.append({
                            'name': node.name,
                            'line': node.lineno,
                            'is_method': self._is_method(node, tree)
                        })
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        imports.append(self._parse_import(node))
                
                self.defined_classes[str(file_path)] = classes
                self.defined_functions[str(file_path)] = functions
                self.imports[str(file_path)] = imports
                
            except Exception as e:
                print(f"⚠️ 解析文件失败 {file_path}: {e}")
    
    def _get_base_name(self, base_node) -> str:
        """获取基类名称"""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{base_node.value.id}.{base_node.attr}" if hasattr(base_node.value, 'id') else base_node.attr
        return "Unknown"
    
    def _is_method(self, func_node, tree) -> bool:
        """判断函数是否是类方法"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if item == func_node:
                        return True
        return False
    
    def _parse_import(self, import_node) -> Dict:
        """解析导入语句"""
        if isinstance(import_node, ast.Import):
            return {
                'type': 'import',
                'module': import_node.names[0].name,
                'alias': import_node.names[0].asname,
                'line': import_node.lineno
            }
        elif isinstance(import_node, ast.ImportFrom):
            return {
                'type': 'from_import',
                'module': import_node.module,
                'names': [(alias.name, alias.asname) for alias in import_node.names],
                'line': import_node.lineno
            }
        return {}
    
    def analyze_references(self):
        """分析所有引用"""
        print("🔍 分析引用关系...")
        
        # 收集所有定义的类名和函数名
        all_classes = set()
        all_functions = set()
        
        for file_path, classes in self.defined_classes.items():
            for cls in classes:
                all_classes.add(cls['name'])
        
        for file_path, functions in self.defined_functions.items():
            for func in functions:
                all_functions.add(func['name'])
        
        # 在所有文件中搜索引用
        for file_path in self.all_python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 搜索类引用
                for class_name in all_classes:
                    if self._find_references(content, class_name, file_path):
                        if class_name not in self.references:
                            self.references[class_name] = []
                        self.references[class_name].append(str(file_path))
                
                # 搜索函数引用
                for func_name in all_functions:
                    if self._find_references(content, func_name, file_path):
                        if func_name not in self.references:
                            self.references[func_name] = []
                        self.references[func_name].append(str(file_path))
                        
            except Exception as e:
                print(f"⚠️ 分析引用失败 {file_path}: {e}")
    
    def _find_references(self, content: str, name: str, file_path: Path) -> bool:
        """查找名称引用"""
        # 排除定义本身的文件
        if str(file_path) in self.defined_classes:
            for cls in self.defined_classes[str(file_path)]:
                if cls['name'] == name:
                    return False
        
        if str(file_path) in self.defined_functions:
            for func in self.defined_functions[str(file_path)]:
                if func['name'] == name:
                    return False
        
        # 搜索引用模式
        patterns = [
            rf'\b{re.escape(name)}\b',  # 直接引用
            rf'from\s+\S+\s+import\s+.*\b{re.escape(name)}\b',  # 导入引用
            rf'import\s+.*\b{re.escape(name)}\b',  # 导入引用
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        print("📊 生成分析报告...")
        
        report = {
            'summary': {
                'total_python_files': len(self.all_python_files),
                'total_ui_files': len(self.ui_files),
                'total_classes': sum(len(classes) for classes in self.defined_classes.values()),
                'total_functions': sum(len(functions) for functions in self.defined_functions.values())
            },
            'unused_ui_components': [],
            'unused_ui_files': [],
            'ui_file_analysis': {},
            'potential_dead_code': []
        }
        
        # 分析未使用的UI组件
        for file_path in self.ui_files:
            file_str = str(file_path)
            if file_str in self.defined_classes:
                for cls in self.defined_classes[file_str]:
                    class_name = cls['name']
                    if class_name not in self.references:
                        report['unused_ui_components'].append({
                            'file': file_str,
                            'class': class_name,
                            'line': cls['line'],
                            'bases': cls['bases']
                        })
        
        # 分析未使用的UI文件
        for ui_file in self.ui_files:
            file_str = str(ui_file)
            has_references = False
            
            # 检查文件中的任何类是否被引用
            if file_str in self.defined_classes:
                for cls in self.defined_classes[file_str]:
                    if cls['name'] in self.references:
                        has_references = True
                        break
            
            if not has_references:
                report['unused_ui_files'].append({
                    'file': file_str,
                    'size_kb': round(ui_file.stat().st_size / 1024, 2),
                    'classes': [cls['name'] for cls in self.defined_classes.get(file_str, [])]
                })
        
        # 详细的UI文件分析
        for ui_file in self.ui_files:
            file_str = str(ui_file)
            analysis = {
                'classes': self.defined_classes.get(file_str, []),
                'functions': self.defined_functions.get(file_str, []),
                'imports': self.imports.get(file_str, []),
                'size_kb': round(ui_file.stat().st_size / 1024, 2),
                'lines': self._count_lines(ui_file)
            }
            
            # 添加引用信息
            for cls in analysis['classes']:
                cls['referenced'] = cls['name'] in self.references
                cls['reference_count'] = len(self.references.get(cls['name'], []))
            
            report['ui_file_analysis'][file_str] = analysis
        
        return report
    
    def _count_lines(self, file_path: Path) -> int:
        """计算文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0

def main():
    """主函数"""
    print("🎬 PyQt5电影票务管理系统 - UI组件使用情况分析")
    print("=" * 60)
    
    analyzer = UIComponentAnalyzer()
    
    # 执行分析
    analyzer.scan_project()
    analyzer.analyze_definitions()
    analyzer.analyze_references()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 保存报告
    with open('ui_component_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 分析完成！报告已保存到 ui_component_analysis_report.json")
    
    # 显示摘要
    print("\n📊 分析摘要:")
    print(f"  总Python文件: {report['summary']['total_python_files']}")
    print(f"  UI文件数量: {report['summary']['total_ui_files']}")
    print(f"  总类数量: {report['summary']['total_classes']}")
    print(f"  总函数数量: {report['summary']['total_functions']}")
    print(f"  未使用UI组件: {len(report['unused_ui_components'])}")
    print(f"  未使用UI文件: {len(report['unused_ui_files'])}")

if __name__ == "__main__":
    main()
