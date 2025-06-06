#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_modular.py 代码功能分析器
全面分析PyQt5电影票务管理系统的功能架构
"""

import ast
import re
from typing import Dict, List, Tuple, Any
from pathlib import Path

class MainModularAnalyzer:
    """main_modular.py 功能分析器"""
    
    def __init__(self, file_path: str = "main_modular.py"):
        self.file_path = file_path
        self.content = ""
        self.lines = []
        self.ast_tree = None
        
        # 分析结果存储
        self.imports = []
        self.classes = []
        self.methods = []
        self.signals = []
        self.ui_components = []
        self.business_logic = []
        self.api_calls = []
        self.event_handlers = []
        
    def load_file(self):
        """加载文件内容"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.split('\n')
            
            # 解析AST
            self.ast_tree = ast.parse(self.content)
            print(f"✅ 成功加载文件: {self.file_path} ({len(self.lines)} 行)")
            return True
        except Exception as e:
            print(f"❌ 加载文件失败: {e}")
            return False
    
    def analyze_imports(self):
        """分析导入语句"""
        print("\n🔍 分析导入语句...")
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno,
                        'category': self._categorize_import(alias.name)
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    self.imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno,
                        'category': self._categorize_import(module)
                    })
        
        print(f"   发现 {len(self.imports)} 个导入语句")
    
    def _categorize_import(self, module_name: str) -> str:
        """分类导入模块"""
        if not module_name:
            return 'unknown'
        
        if module_name.startswith('PyQt5'):
            return 'ui_framework'
        elif module_name.startswith('ui.'):
            return 'ui_components'
        elif module_name.startswith('services.'):
            return 'business_services'
        elif module_name.startswith('modules.'):
            return 'business_modules'
        elif module_name.startswith('utils.'):
            return 'utilities'
        elif module_name in ['sys', 'os', 'json', 'time', 'traceback']:
            return 'system'
        else:
            return 'external'
    
    def analyze_class_structure(self):
        """分析类结构"""
        print("\n🔍 分析类结构...")
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'line_start': node.lineno,
                    'line_end': self._get_node_end_line(node),
                    'bases': [self._get_base_name(base) for base in node.bases],
                    'methods': [],
                    'signals': [],
                    'properties': []
                }
                
                # 分析类中的方法
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = self._analyze_method(item)
                        class_info['methods'].append(method_info)
                    elif isinstance(item, ast.Assign):
                        # 查找信号定义
                        if self._is_signal_assignment(item):
                            signal_info = self._extract_signal_info(item)
                            class_info['signals'].append(signal_info)
                
                self.classes.append(class_info)
        
        print(f"   发现 {len(self.classes)} 个类")
    
    def _analyze_method(self, node: ast.FunctionDef) -> Dict:
        """分析方法"""
        method_info = {
            'name': node.name,
            'line_start': node.lineno,
            'line_end': self._get_node_end_line(node),
            'args': [arg.arg for arg in node.args.args],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'category': self._categorize_method(node.name),
            'calls_apis': self._method_calls_apis(node),
            'handles_events': self._method_handles_events(node),
            'docstring': ast.get_docstring(node)
        }
        
        self.methods.append(method_info)
        return method_info
    
    def _categorize_method(self, method_name: str) -> str:
        """分类方法"""
        if method_name.startswith('_on_'):
            return 'event_handler'
        elif method_name.startswith('_init'):
            return 'initialization'
        elif method_name.startswith('_create'):
            return 'ui_creation'
        elif method_name.startswith('_connect'):
            return 'signal_connection'
        elif method_name.startswith('_load'):
            return 'data_loading'
        elif method_name.startswith('_show') or method_name.startswith('_display'):
            return 'ui_display'
        elif method_name.startswith('_get') or method_name.startswith('_fetch'):
            return 'data_retrieval'
        elif method_name.startswith('_save') or method_name.startswith('_update'):
            return 'data_persistence'
        elif 'api' in method_name.lower():
            return 'api_call'
        elif 'pay' in method_name.lower() or 'order' in method_name.lower():
            return 'business_logic'
        else:
            return 'utility'
    
    def _method_calls_apis(self, node: ast.FunctionDef) -> List[str]:
        """检查方法是否调用API"""
        api_calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    func_name = child.func.id
                    if any(api in func_name.lower() for api in ['api', 'get_', 'post_', 'create_order', 'pay_order']):
                        api_calls.append(func_name)
        return api_calls
    
    def _method_handles_events(self, node: ast.FunctionDef) -> bool:
        """检查方法是否处理事件"""
        return (node.name.startswith('_on_') or 
                any(d.id == 'pyqtSlot' for d in node.decorator_list if isinstance(d, ast.Name)))
    
    def analyze_ui_components(self):
        """分析UI组件"""
        print("\n🔍 分析UI组件...")
        
        # 查找UI组件创建
        ui_creation_pattern = r'self\.(\w+)\s*=\s*(\w+)\('
        for i, line in enumerate(self.lines, 1):
            matches = re.findall(ui_creation_pattern, line)
            for var_name, class_name in matches:
                if any(ui_class in class_name for ui_class in ['Widget', 'Button', 'Label', 'Layout', 'Edit', 'Combo']):
                    self.ui_components.append({
                        'variable': var_name,
                        'class': class_name,
                        'line': i,
                        'type': self._categorize_ui_component(class_name)
                    })
        
        print(f"   发现 {len(self.ui_components)} 个UI组件")
    
    def _categorize_ui_component(self, class_name: str) -> str:
        """分类UI组件"""
        if 'Button' in class_name:
            return 'button'
        elif 'Label' in class_name:
            return 'label'
        elif 'Edit' in class_name or 'Input' in class_name:
            return 'input'
        elif 'Layout' in class_name:
            return 'layout'
        elif 'Widget' in class_name:
            return 'widget'
        elif 'Combo' in class_name:
            return 'selector'
        else:
            return 'other'
    
    def analyze_business_logic(self):
        """分析业务逻辑"""
        print("\n🔍 分析业务逻辑...")
        
        # 查找业务逻辑方法
        business_keywords = [
            'login', 'auth', 'order', 'pay', 'seat', 'cinema', 'movie', 
            'coupon', 'member', 'ticket', 'qr', 'account'
        ]
        
        for method in self.methods:
            method_name_lower = method['name'].lower()
            if any(keyword in method_name_lower for keyword in business_keywords):
                self.business_logic.append({
                    'method': method['name'],
                    'line_start': method['line_start'],
                    'line_end': method['line_end'],
                    'category': method['category'],
                    'business_type': self._identify_business_type(method['name'])
                })
        
        print(f"   发现 {len(self.business_logic)} 个业务逻辑方法")
    
    def _identify_business_type(self, method_name: str) -> str:
        """识别业务类型"""
        name_lower = method_name.lower()
        if 'login' in name_lower or 'auth' in name_lower:
            return 'authentication'
        elif 'order' in name_lower:
            return 'order_management'
        elif 'pay' in name_lower:
            return 'payment'
        elif 'seat' in name_lower:
            return 'seat_selection'
        elif 'cinema' in name_lower or 'movie' in name_lower:
            return 'cinema_management'
        elif 'coupon' in name_lower:
            return 'coupon_management'
        elif 'member' in name_lower:
            return 'member_management'
        elif 'qr' in name_lower or 'ticket' in name_lower:
            return 'ticket_management'
        else:
            return 'general'
    
    def analyze_api_calls(self):
        """分析API调用"""
        print("\n🔍 分析API调用...")
        
        # 查找API调用模式
        api_patterns = [
            r'(\w+_api)\(',
            r'(get_\w+)\(',
            r'(create_\w+)\(',
            r'(pay_\w+)\(',
            r'api_(\w+)\('
        ]
        
        for i, line in enumerate(self.lines, 1):
            for pattern in api_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    api_name = match if isinstance(match, str) else match[0]
                    self.api_calls.append({
                        'api': api_name,
                        'line': i,
                        'context': line.strip(),
                        'type': self._categorize_api_call(api_name)
                    })
        
        print(f"   发现 {len(self.api_calls)} 个API调用")
    
    def _categorize_api_call(self, api_name: str) -> str:
        """分类API调用"""
        name_lower = api_name.lower()
        if 'order' in name_lower:
            return 'order_api'
        elif 'pay' in name_lower:
            return 'payment_api'
        elif 'member' in name_lower:
            return 'member_api'
        elif 'cinema' in name_lower or 'film' in name_lower:
            return 'cinema_api'
        elif 'coupon' in name_lower:
            return 'coupon_api'
        elif 'auth' in name_lower or 'login' in name_lower:
            return 'auth_api'
        else:
            return 'general_api'
    
    def generate_report(self) -> Dict:
        """生成分析报告"""
        print("\n📊 生成分析报告...")
        
        report = {
            'file_info': {
                'path': self.file_path,
                'total_lines': len(self.lines),
                'total_classes': len(self.classes),
                'total_methods': len(self.methods)
            },
            'imports': {
                'total': len(self.imports),
                'by_category': self._group_by_category(self.imports, 'category')
            },
            'classes': self.classes,
            'methods': {
                'total': len(self.methods),
                'by_category': self._group_by_category(self.methods, 'category')
            },
            'ui_components': {
                'total': len(self.ui_components),
                'by_type': self._group_by_category(self.ui_components, 'type')
            },
            'business_logic': {
                'total': len(self.business_logic),
                'by_type': self._group_by_category(self.business_logic, 'business_type')
            },
            'api_calls': {
                'total': len(self.api_calls),
                'by_type': self._group_by_category(self.api_calls, 'type')
            }
        }
        
        return report
    
    def _group_by_category(self, items: List[Dict], category_key: str) -> Dict:
        """按类别分组"""
        groups = {}
        for item in items:
            category = item.get(category_key, 'unknown')
            if category not in groups:
                groups[category] = []
            groups[category].append(item)
        return {k: len(v) for k, v in groups.items()}
    
    # 辅助方法
    def _get_node_end_line(self, node) -> int:
        """获取AST节点的结束行号"""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno
        return node.lineno
    
    def _get_base_name(self, base_node) -> str:
        """获取基类名称"""
        if isinstance(base_node, ast.Name):
            return base_node.id
        elif isinstance(base_node, ast.Attribute):
            return f"{base_node.value.id}.{base_node.attr}" if hasattr(base_node.value, 'id') else base_node.attr
        return "Unknown"
    
    def _get_decorator_name(self, decorator) -> str:
        """获取装饰器名称"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
            return decorator.func.id
        return "Unknown"
    
    def _is_signal_assignment(self, node: ast.Assign) -> bool:
        """检查是否是信号赋值"""
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute):
            return isinstance(node.value, ast.Call) and \
                   isinstance(node.value.func, ast.Name) and \
                   'Signal' in node.value.func.id
        return False
    
    def _extract_signal_info(self, node: ast.Assign) -> Dict:
        """提取信号信息"""
        target = node.targets[0]
        signal_name = target.attr if isinstance(target, ast.Attribute) else 'unknown'
        signal_type = node.value.func.id if isinstance(node.value.func, ast.Name) else 'unknown'
        
        return {
            'name': signal_name,
            'type': signal_type,
            'line': node.lineno
        }

def main():
    """主函数"""
    print("🎬 PyQt5电影票务管理系统 - main_modular.py 功能分析")
    print("=" * 60)
    
    analyzer = MainModularAnalyzer()
    
    if not analyzer.load_file():
        return
    
    # 执行各项分析
    analyzer.analyze_imports()
    analyzer.analyze_class_structure()
    analyzer.analyze_ui_components()
    analyzer.analyze_business_logic()
    analyzer.analyze_api_calls()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 保存详细报告
    import json
    with open('main_modular_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析完成！详细报告已保存到: main_modular_analysis_report.json")
    
    # 显示摘要
    print(f"\n📊 分析摘要:")
    print(f"  文件行数: {report['file_info']['total_lines']}")
    print(f"  类数量: {report['file_info']['total_classes']}")
    print(f"  方法数量: {report['file_info']['total_methods']}")
    print(f"  导入模块: {report['imports']['total']}")
    print(f"  UI组件: {report['ui_components']['total']}")
    print(f"  业务逻辑方法: {report['business_logic']['total']}")
    print(f"  API调用: {report['api_calls']['total']}")

if __name__ == "__main__":
    main()
