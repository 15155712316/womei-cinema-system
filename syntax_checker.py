#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面语法错误扫描和修复脚本
"""

import os
import ast
import re
import sys
from typing import List, Dict, Tuple

class SyntaxChecker:
    def __init__(self):
        self.errors_found = []
        self.files_checked = 0
        self.files_with_errors = 0
        
    def find_python_files(self, root_dir: str) -> List[str]:
        """查找所有Python文件"""
        python_files = []
        
        # 重点检查的目录和文件
        priority_paths = [
            'main_modular.py',
            'run_app.py',
            'ui/',
            'services/',
            'utils/'
        ]
        
        for path in priority_paths:
            full_path = os.path.join(root_dir, path)
            if os.path.isfile(full_path) and path.endswith('.py'):
                python_files.append(full_path)
            elif os.path.isdir(full_path):
                for root, dirs, files in os.walk(full_path):
                    for file in files:
                        if file.endswith('.py'):
                            python_files.append(os.path.join(root, file))
        
        # 检查根目录下的其他Python文件
        for file in os.listdir(root_dir):
            if file.endswith('.py'):
                full_path = os.path.join(root_dir, file)
                if full_path not in python_files:
                    python_files.append(full_path)
        
        return sorted(python_files)
    
    def check_syntax_with_ast(self, file_path: str) -> List[Dict]:
        """使用AST检查语法错误"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试解析AST
            ast.parse(content)
            
        except SyntaxError as e:
            errors.append({
                'type': 'SyntaxError',
                'line': e.lineno,
                'message': str(e),
                'text': e.text.strip() if e.text else ''
            })
        except IndentationError as e:
            errors.append({
                'type': 'IndentationError', 
                'line': e.lineno,
                'message': str(e),
                'text': e.text.strip() if e.text else ''
            })
        except Exception as e:
            errors.append({
                'type': 'UnknownError',
                'line': 0,
                'message': str(e),
                'text': ''
            })
        
        return errors
    
    def check_incomplete_blocks(self, file_path: str) -> List[Dict]:
        """检查不完整的代码块"""
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # 检查以冒号结尾但下一行没有缩进的语句
                if (stripped.endswith(':') and 
                    any(stripped.startswith(keyword) for keyword in 
                        ['if ', 'else:', 'elif ', 'try:', 'except ', 'finally:', 
                         'for ', 'while ', 'def ', 'class ', 'with '])):
                    
                    # 检查下一行
                    if i < len(lines):
                        next_line = lines[i].rstrip()
                        if (not next_line or 
                            (next_line and not next_line.startswith(' ') and not next_line.startswith('\t'))):
                            # 检查是否是函数/类定义后的空行（这是正常的）
                            if not (stripped.startswith('def ') or stripped.startswith('class ')):
                                errors.append({
                                    'type': 'IncompleteBlock',
                                    'line': i,
                                    'message': f'Incomplete block after: {stripped}',
                                    'text': stripped
                                })
        
        except Exception as e:
            pass
        
        return errors
    
    def scan_file(self, file_path: str) -> Dict:
        """扫描单个文件"""
        self.files_checked += 1
        
        # AST语法检查
        ast_errors = self.check_syntax_with_ast(file_path)
        
        # 不完整代码块检查
        block_errors = self.check_incomplete_blocks(file_path)
        
        all_errors = ast_errors + block_errors
        
        if all_errors:
            self.files_with_errors += 1
            
        return {
            'file': file_path,
            'errors': all_errors
        }
    
    def scan_project(self, root_dir: str = '.') -> List[Dict]:
        """扫描整个项目"""
        print("🔍 开始全面语法错误扫描...")
        
        python_files = self.find_python_files(root_dir)
        print(f"📁 找到 {len(python_files)} 个Python文件")
        
        results = []
        
        for file_path in python_files:
            print(f"🔍 检查: {file_path}")
            result = self.scan_file(file_path)
            
            if result['errors']:
                results.append(result)
                print(f"❌ 发现 {len(result['errors'])} 个错误")
            else:
                print(f"✅ 无错误")
        
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """生成错误报告"""
        report = []
        report.append("=" * 60)
        report.append("🔍 语法错误扫描报告")
        report.append("=" * 60)
        report.append(f"📊 扫描统计:")
        report.append(f"   - 检查文件数: {self.files_checked}")
        report.append(f"   - 有错误文件数: {self.files_with_errors}")
        report.append(f"   - 总错误数: {sum(len(r['errors']) for r in results)}")
        report.append("")
        
        if not results:
            report.append("🎉 恭喜！未发现任何语法错误！")
            return "\n".join(report)
        
        report.append("📋 错误详情:")
        report.append("")
        
        for result in results:
            report.append(f"📄 文件: {result['file']}")
            report.append("-" * 40)
            
            for error in result['errors']:
                report.append(f"   ❌ 第{error['line']}行: {error['type']}")
                report.append(f"      消息: {error['message']}")
                if error['text']:
                    report.append(f"      代码: {error['text']}")
                report.append("")
        
        return "\n".join(report)

def main():
    """主函数"""
    checker = SyntaxChecker()
    results = checker.scan_project()
    
    # 生成报告
    report = checker.generate_report(results)
    print("\n" + report)
    
    # 保存报告到文件
    with open('syntax_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 详细报告已保存到: syntax_report.txt")
    
    # 返回错误数量
    return len(results)

if __name__ == "__main__":
    error_count = main()
    sys.exit(error_count)
