#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 详细代码分析器
深入分析具体的重复模式和优化机会
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class DetailedCodeAnalyzer:
    """详细代码分析器"""
    
    def __init__(self):
        self.main_file = "main_modular.py"
        self.analysis_results = {
            'api_patterns': [],
            'ui_patterns': [],
            'error_handling_patterns': [],
            'data_processing_patterns': [],
            'import_analysis': {},
            'method_complexity': [],
            'refactoring_opportunities': []
        }
    
    def analyze_main_program_patterns(self):
        """分析主程序中的重复模式"""
        print("🔍 深入分析主程序重复模式...")
        
        if not Path(self.main_file).exists():
            return
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析API调用模式
        self._analyze_api_patterns(content)
        
        # 分析UI组件模式
        self._analyze_ui_patterns(content)
        
        # 分析错误处理模式
        self._analyze_error_handling_patterns(content)
        
        # 分析数据处理模式
        self._analyze_data_processing_patterns(content)
        
        # 分析导入使用情况
        self._analyze_import_usage(content)
        
        print("✅ 主程序模式分析完成")
    
    def _analyze_api_patterns(self, content: str):
        """分析API调用模式"""
        # 查找API调用模式
        api_patterns = [
            # requests调用模式
            r'(requests\.(get|post|put|delete)\s*\([^)]+\))',
            # 自定义API调用模式
            r'(api_(get|post|put|delete)\s*\([^)]+\))',
            # 服务调用模式
            r'(\w+_service\.\w+\([^)]*\))',
            # API错误处理模式
            r'(try:\s*\n\s*.*?api.*?\n\s*except.*?:)',
        ]
        
        api_calls = []
        for pattern in api_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                api_calls.append({
                    'pattern': pattern,
                    'call': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # 分组相似的API调用
        grouped_calls = self._group_similar_patterns(api_calls)
        self.analysis_results['api_patterns'] = grouped_calls
        
        print(f"  发现 {len(api_calls)} 个API调用，{len(grouped_calls)} 个模式组")
    
    def _analyze_ui_patterns(self, content: str):
        """分析UI组件模式"""
        ui_patterns = [
            # PyQt5组件创建模式
            r'(Q\w+\([^)]*\))',
            # 布局设置模式
            r'(\w+\.setLayout\([^)]+\))',
            # 样式设置模式
            r'(\w+\.setStyleSheet\([^)]+\))',
            # 信号连接模式
            r'(\w+\.connect\([^)]+\))',
            # 组件添加模式
            r'(\w+\.addWidget\([^)]+\))',
        ]
        
        ui_calls = []
        for pattern in ui_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                ui_calls.append({
                    'pattern': pattern,
                    'call': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        grouped_ui = self._group_similar_patterns(ui_calls)
        self.analysis_results['ui_patterns'] = grouped_ui
        
        print(f"  发现 {len(ui_calls)} 个UI调用，{len(grouped_ui)} 个模式组")
    
    def _analyze_error_handling_patterns(self, content: str):
        """分析错误处理模式"""
        error_patterns = [
            # try-except模式
            r'(try:\s*\n.*?\nexcept.*?:.*?\n)',
            # 错误消息显示模式
            r'(QMessageBox\.(warning|critical|information)\([^)]+\))',
            # 日志记录模式
            r'(print\(["\'].*?error.*?["\'][^)]*\))',
            # 异常抛出模式
            r'(raise\s+\w+\([^)]*\))',
        ]
        
        error_calls = []
        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                error_calls.append({
                    'pattern': pattern,
                    'call': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        grouped_errors = self._group_similar_patterns(error_calls)
        self.analysis_results['error_handling_patterns'] = grouped_errors
        
        print(f"  发现 {len(error_calls)} 个错误处理，{len(grouped_errors)} 个模式组")
    
    def _analyze_data_processing_patterns(self, content: str):
        """分析数据处理模式"""
        data_patterns = [
            # JSON处理模式
            r'(json\.(loads|dumps)\([^)]+\))',
            # 字典操作模式
            r'(\w+\.get\([^)]+\))',
            # 列表操作模式
            r'(\[.*?for.*?in.*?\])',
            # 字符串格式化模式
            r'(f["\'].*?\{.*?\}.*?["\'])',
            # 数据验证模式
            r'(if\s+\w+\s+is\s+(None|not\s+None))',
        ]
        
        data_calls = []
        for pattern in data_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                data_calls.append({
                    'pattern': pattern,
                    'call': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        grouped_data = self._group_similar_patterns(data_calls)
        self.analysis_results['data_processing_patterns'] = grouped_data
        
        print(f"  发现 {len(data_calls)} 个数据处理，{len(grouped_data)} 个模式组")
    
    def _analyze_import_usage(self, content: str):
        """分析导入使用情况"""
        # 提取所有导入
        import_pattern = r'^(from\s+([\w.]+)\s+import\s+([\w,\s*]+)|import\s+([\w.,\s]+))'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        
        import_usage = {}
        for imp in imports:
            if imp[1]:  # from ... import ...
                module = imp[1]
                items = [item.strip() for item in imp[2].split(',')]
                for item in items:
                    # 计算使用次数
                    usage_count = len(re.findall(rf'\b{item}\b', content))
                    import_usage[f"{module}.{item}"] = usage_count
            elif imp[3]:  # import ...
                modules = [mod.strip() for mod in imp[3].split(',')]
                for module in modules:
                    usage_count = len(re.findall(rf'\b{module}\b', content))
                    import_usage[module] = usage_count
        
        # 找出未使用或低使用的导入
        unused_imports = {k: v for k, v in import_usage.items() if v <= 1}
        
        self.analysis_results['import_analysis'] = {
            'total_imports': len(import_usage),
            'unused_imports': unused_imports,
            'usage_stats': import_usage
        }
        
        print(f"  分析 {len(import_usage)} 个导入，{len(unused_imports)} 个未使用")
    
    def _group_similar_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """将相似的模式分组"""
        groups = []
        used_indices = set()
        
        for i, pattern1 in enumerate(patterns):
            if i in used_indices:
                continue
            
            group = [pattern1]
            used_indices.add(i)
            
            for j, pattern2 in enumerate(patterns[i+1:], i+1):
                if j in used_indices:
                    continue
                
                # 简单的相似性检查
                if self._patterns_similar(pattern1['call'], pattern2['call']):
                    group.append(pattern2)
                    used_indices.add(j)
            
            if len(group) > 1:  # 只保留有重复的组
                groups.append({
                    'count': len(group),
                    'pattern_type': self._classify_pattern(group[0]['call']),
                    'examples': group[:3],  # 只保留前3个例子
                    'refactoring_suggestion': self._suggest_refactoring(group)
                })
        
        return groups
    
    def _patterns_similar(self, pattern1: str, pattern2: str) -> bool:
        """检查两个模式是否相似"""
        # 移除变量名和具体值，只保留结构
        normalized1 = re.sub(r'\b\w+\b', 'VAR', pattern1)
        normalized2 = re.sub(r'\b\w+\b', 'VAR', pattern2)
        
        # 移除字符串和数字
        normalized1 = re.sub(r'["\'].*?["\']', 'STR', normalized1)
        normalized2 = re.sub(r'["\'].*?["\']', 'STR', normalized2)
        normalized1 = re.sub(r'\d+', 'NUM', normalized1)
        normalized2 = re.sub(r'\d+', 'NUM', normalized2)
        
        return normalized1 == normalized2
    
    def _classify_pattern(self, pattern: str) -> str:
        """分类模式类型"""
        if 'api' in pattern.lower() or 'request' in pattern.lower():
            return 'API调用'
        elif any(ui in pattern for ui in ['Q', 'Widget', 'Layout', 'Button']):
            return 'UI组件'
        elif 'except' in pattern or 'error' in pattern.lower():
            return '错误处理'
        elif 'json' in pattern.lower() or 'get(' in pattern:
            return '数据处理'
        else:
            return '其他'
    
    def _suggest_refactoring(self, group: List[Dict]) -> str:
        """建议重构方案"""
        pattern_type = self._classify_pattern(group[0]['call'])
        
        suggestions = {
            'API调用': '提取为通用API调用方法，统一错误处理和参数验证',
            'UI组件': '创建UI组件工厂类，统一组件创建和样式设置',
            '错误处理': '创建统一的错误处理装饰器或基类方法',
            '数据处理': '提取为数据处理工具类的静态方法',
            '其他': '考虑提取为公共函数或常量'
        }
        
        return suggestions.get(pattern_type, '考虑提取为公共函数')
    
    def analyze_method_complexity(self):
        """分析方法复杂度"""
        print("🔍 分析方法复杂度...")
        
        if not Path(self.main_file).exists():
            return
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取所有方法
        method_pattern = r'def\s+(\w+)\s*\([^)]*\):\s*\n((?:\s{4,}.*\n)*)'
        methods = re.finditer(method_pattern, content, re.MULTILINE)
        
        complex_methods = []
        for match in methods:
            method_name = match.group(1)
            method_body = match.group(2)
            
            # 计算复杂度指标
            lines = len([line for line in method_body.split('\n') if line.strip()])
            if_count = len(re.findall(r'\bif\b', method_body))
            for_count = len(re.findall(r'\bfor\b', method_body))
            try_count = len(re.findall(r'\btry\b', method_body))
            
            complexity_score = lines + if_count * 2 + for_count * 2 + try_count * 3
            
            if complexity_score > 50:  # 复杂度阈值
                complex_methods.append({
                    'name': method_name,
                    'lines': lines,
                    'if_count': if_count,
                    'for_count': for_count,
                    'try_count': try_count,
                    'complexity_score': complexity_score,
                    'refactoring_suggestion': self._suggest_method_refactoring(complexity_score, lines)
                })
        
        self.analysis_results['method_complexity'] = complex_methods
        print(f"  发现 {len(complex_methods)} 个复杂方法需要重构")
    
    def _suggest_method_refactoring(self, complexity: int, lines: int) -> str:
        """建议方法重构"""
        if lines > 100:
            return "方法过长，建议拆分为多个小方法"
        elif complexity > 100:
            return "逻辑复杂，建议使用策略模式或状态模式"
        elif complexity > 70:
            return "建议提取部分逻辑为私有方法"
        else:
            return "建议简化条件判断和循环逻辑"
    
    def generate_refactoring_opportunities(self):
        """生成重构机会"""
        print("🔍 生成重构机会...")
        
        opportunities = []
        
        # API模式重构机会
        api_groups = self.analysis_results.get('api_patterns', [])
        for group in api_groups:
            if group['count'] >= 3:
                opportunities.append({
                    'type': 'API统一化',
                    'priority': 'high',
                    'description': f"发现 {group['count']} 个相似的{group['pattern_type']}模式",
                    'suggestion': group['refactoring_suggestion'],
                    'estimated_reduction': f"{group['count'] * 5} 行代码"
                })
        
        # UI模式重构机会
        ui_groups = self.analysis_results.get('ui_patterns', [])
        for group in ui_groups:
            if group['count'] >= 5:
                opportunities.append({
                    'type': 'UI组件化',
                    'priority': 'medium',
                    'description': f"发现 {group['count']} 个相似的{group['pattern_type']}模式",
                    'suggestion': group['refactoring_suggestion'],
                    'estimated_reduction': f"{group['count'] * 3} 行代码"
                })
        
        # 错误处理重构机会
        error_groups = self.analysis_results.get('error_handling_patterns', [])
        for group in error_groups:
            if group['count'] >= 3:
                opportunities.append({
                    'type': '错误处理统一化',
                    'priority': 'medium',
                    'description': f"发现 {group['count']} 个相似的{group['pattern_type']}模式",
                    'suggestion': group['refactoring_suggestion'],
                    'estimated_reduction': f"{group['count'] * 4} 行代码"
                })
        
        # 复杂方法重构机会
        complex_methods = self.analysis_results.get('method_complexity', [])
        for method in complex_methods:
            opportunities.append({
                'type': '方法简化',
                'priority': 'high' if method['complexity_score'] > 100 else 'medium',
                'description': f"方法 {method['name']} 复杂度过高 ({method['complexity_score']})",
                'suggestion': method['refactoring_suggestion'],
                'estimated_reduction': f"{method['lines'] // 3} 行代码"
            })
        
        self.analysis_results['refactoring_opportunities'] = opportunities
        print(f"  生成 {len(opportunities)} 个重构机会")
    
    def run_analysis(self):
        """运行完整分析"""
        print("🎬 PyQt5电影票务管理系统 - 详细代码分析")
        print("=" * 60)
        
        self.analyze_main_program_patterns()
        self.analyze_method_complexity()
        self.generate_refactoring_opportunities()
        
        return self.analysis_results

def main():
    """主函数"""
    analyzer = DetailedCodeAnalyzer()
    results = analyzer.run_analysis()
    
    # 保存结果
    import json
    with open('detailed_code_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 显示摘要
    print(f"\n📊 详细分析摘要:")
    print(f"  API模式组: {len(results.get('api_patterns', []))}")
    print(f"  UI模式组: {len(results.get('ui_patterns', []))}")
    print(f"  错误处理模式组: {len(results.get('error_handling_patterns', []))}")
    print(f"  复杂方法: {len(results.get('method_complexity', []))}")
    print(f"  重构机会: {len(results.get('refactoring_opportunities', []))}")
    
    print(f"\n✅ 详细代码分析完成！结果已保存到: detailed_code_analysis.json")

if __name__ == "__main__":
    main()
