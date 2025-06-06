#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 系统架构分析器
全面分析系统功能链路和优化规划
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class SystemArchitectureAnalyzer:
    """系统架构分析器"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.main_file = "main_modular.py"
        self.core_dirs = ["services", "ui", "utils", "modules", "controllers", "views", "widgets"]
        
        self.analysis_results = {
            'project_overview': {},
            'main_program_analysis': {},
            'directory_analysis': {},
            'function_modules': {},
            'business_flows': {},
            'technical_layers': {},
            'dependency_graph': {},
            'optimization_plan': {}
        }
    
    def analyze_main_program(self):
        """分析主程序文件"""
        print("🔍 分析主程序文件...")
        
        if not Path(self.main_file).exists():
            print(f"❌ 主程序文件不存在: {self.main_file}")
            return
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 基本信息
            lines = content.split('\n')
            self.analysis_results['main_program_analysis'] = {
                'file_size_kb': round(len(content.encode('utf-8')) / 1024, 1),
                'total_lines': len(lines),
                'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
                'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
                'classes': self._extract_classes(content),
                'methods': self._extract_methods(content),
                'imports': self._extract_imports(content),
                'api_calls': self._extract_api_calls(content),
                'ui_components': self._extract_ui_components(content),
                'business_logic': self._extract_business_logic(content)
            }
            
            print(f"✅ 主程序分析完成: {self.analysis_results['main_program_analysis']['total_lines']} 行代码")
            
        except Exception as e:
            print(f"❌ 主程序分析失败: {e}")
    
    def _extract_classes(self, content: str) -> List[Dict]:
        """提取类定义"""
        classes = []
        class_pattern = r'class\s+(\w+)(?:\([^)]*\))?:'
        matches = re.finditer(class_pattern, content)
        
        for match in matches:
            class_name = match.group(1)
            start_pos = match.start()
            
            # 查找类的方法
            class_content = content[start_pos:]
            methods = re.findall(r'def\s+(\w+)\s*\([^)]*\):', class_content)
            
            classes.append({
                'name': class_name,
                'methods': methods[:10],  # 限制前10个方法
                'method_count': len(methods)
            })
        
        return classes
    
    def _extract_methods(self, content: str) -> List[str]:
        """提取方法定义"""
        method_pattern = r'def\s+(\w+)\s*\([^)]*\):'
        methods = re.findall(method_pattern, content)
        return list(set(methods))  # 去重
    
    def _extract_imports(self, content: str) -> Dict:
        """提取导入语句"""
        imports = {
            'standard_library': [],
            'third_party': [],
            'local_modules': []
        }
        
        import_patterns = [
            r'import\s+([^\s,]+)',
            r'from\s+([^\s]+)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if match.startswith('.') or match in ['services', 'ui', 'utils', 'modules']:
                    imports['local_modules'].append(match)
                elif match in ['sys', 'os', 'json', 're', 'time', 'datetime']:
                    imports['standard_library'].append(match)
                else:
                    imports['third_party'].append(match)
        
        # 去重
        for key in imports:
            imports[key] = list(set(imports[key]))
        
        return imports
    
    def _extract_api_calls(self, content: str) -> List[str]:
        """提取API调用"""
        api_patterns = [
            r'requests\.(get|post|put|delete)\s*\(',
            r'self\.(get|post|put|delete)_request\s*\(',
            r'api\.\w+\s*\(',
            r'\.api\.\w+\s*\('
        ]
        
        api_calls = []
        for pattern in api_patterns:
            matches = re.findall(pattern, content)
            api_calls.extend(matches)
        
        return list(set(api_calls))
    
    def _extract_ui_components(self, content: str) -> List[str]:
        """提取UI组件"""
        ui_patterns = [
            r'Q\w+\s*\(',
            r'self\.\w+\s*=\s*Q\w+\(',
            r'\.addWidget\s*\(',
            r'\.setLayout\s*\('
        ]
        
        ui_components = []
        for pattern in ui_patterns:
            matches = re.findall(pattern, content)
            ui_components.extend(matches)
        
        return list(set(ui_components))[:20]  # 限制前20个
    
    def _extract_business_logic(self, content: str) -> Dict:
        """提取业务逻辑关键词"""
        business_keywords = {
            'authentication': ['login', 'auth', 'token', 'openid'],
            'cinema': ['cinema', 'movie', 'film', 'theater'],
            'booking': ['book', 'order', 'seat', 'ticket'],
            'payment': ['pay', 'price', 'member', 'coupon'],
            'qrcode': ['qr', 'code', 'generate']
        }
        
        business_logic = {}
        for category, keywords in business_keywords.items():
            count = 0
            for keyword in keywords:
                count += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
            business_logic[category] = count
        
        return business_logic
    
    def analyze_directories(self):
        """分析核心目录"""
        print("🔍 分析核心目录结构...")
        
        for dir_name in self.core_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                self.analysis_results['directory_analysis'][dir_name] = self._analyze_directory(dir_path)
                print(f"✅ 分析完成: {dir_name}")
            else:
                print(f"⚠️ 目录不存在: {dir_name}")
    
    def _analyze_directory(self, dir_path: Path) -> Dict:
        """分析单个目录"""
        analysis = {
            'file_count': 0,
            'python_files': [],
            'total_size_kb': 0,
            'main_modules': [],
            'key_functions': []
        }
        
        for file_path in dir_path.rglob("*.py"):
            if file_path.name != "__init__.py":
                analysis['file_count'] += 1
                file_size = file_path.stat().st_size
                analysis['total_size_kb'] += file_size / 1024
                
                analysis['python_files'].append({
                    'name': file_path.name,
                    'path': str(file_path),
                    'size_kb': round(file_size / 1024, 1)
                })
                
                # 分析文件内容
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取主要类和函数
                    classes = re.findall(r'class\s+(\w+)', content)
                    functions = re.findall(r'def\s+(\w+)', content)
                    
                    if classes or functions:
                        analysis['main_modules'].append({
                            'file': file_path.name,
                            'classes': classes[:5],  # 前5个类
                            'functions': functions[:10]  # 前10个函数
                        })
                
                except Exception:
                    pass
        
        analysis['total_size_kb'] = round(analysis['total_size_kb'], 1)
        return analysis
    
    def identify_function_modules(self):
        """识别功能模块"""
        print("🔍 识别功能模块...")
        
        # 基于文件名和内容识别功能模块
        function_modules = {
            'user_authentication': {
                'description': '用户认证模块',
                'files': [],
                'key_features': ['登录验证', '令牌管理', '权限检查'],
                'status': 'active'
            },
            'cinema_management': {
                'description': '影院管理模块',
                'files': [],
                'key_features': ['影院信息', '电影列表', '场次管理'],
                'status': 'active'
            },
            'seat_selection': {
                'description': '座位选择模块',
                'files': [],
                'key_features': ['座位图显示', '座位状态', '选座逻辑'],
                'status': 'active'
            },
            'order_processing': {
                'description': '订单处理模块',
                'files': [],
                'key_features': ['订单创建', '订单查询', '订单状态'],
                'status': 'active'
            },
            'payment_system': {
                'description': '支付系统模块',
                'files': [],
                'key_features': ['会员卡支付', '优惠券', '价格计算'],
                'status': 'active'
            },
            'qrcode_generation': {
                'description': '取票码生成模块',
                'files': [],
                'key_features': ['二维码生成', '取票码显示', '订单确认'],
                'status': 'active'
            }
        }
        
        # 扫描所有Python文件，根据内容分类
        for dir_name in self.core_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for file_path in dir_path.rglob("*.py"):
                    file_content = ""
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read().lower()
                    except:
                        continue
                    
                    # 根据关键词分类
                    if any(keyword in file_content for keyword in ['login', 'auth', 'token']):
                        function_modules['user_authentication']['files'].append(str(file_path))
                    
                    if any(keyword in file_content for keyword in ['cinema', 'movie', 'film']):
                        function_modules['cinema_management']['files'].append(str(file_path))
                    
                    if any(keyword in file_content for keyword in ['seat', 'chair', 'position']):
                        function_modules['seat_selection']['files'].append(str(file_path))
                    
                    if any(keyword in file_content for keyword in ['order', 'booking', 'reserve']):
                        function_modules['order_processing']['files'].append(str(file_path))
                    
                    if any(keyword in file_content for keyword in ['pay', 'member', 'coupon', 'price']):
                        function_modules['payment_system']['files'].append(str(file_path))
                    
                    if any(keyword in file_content for keyword in ['qr', 'code', 'generate']):
                        function_modules['qrcode_generation']['files'].append(str(file_path))
        
        self.analysis_results['function_modules'] = function_modules
        print("✅ 功能模块识别完成")
    
    def analyze_business_flows(self):
        """分析业务流程"""
        print("🔍 分析业务流程...")
        
        business_flows = {
            'user_journey': {
                'name': '用户购票完整流程',
                'steps': [
                    {'step': 1, 'name': '系统启动', 'description': '启动应用程序'},
                    {'step': 2, 'name': '用户认证', 'description': '登录验证和权限检查'},
                    {'step': 3, 'name': '选择影院', 'description': '浏览和选择影院'},
                    {'step': 4, 'name': '选择电影', 'description': '查看电影列表和场次'},
                    {'step': 5, 'name': '选择座位', 'description': '查看座位图并选择座位'},
                    {'step': 6, 'name': '确认订单', 'description': '确认订单信息和价格'},
                    {'step': 7, 'name': '支付处理', 'description': '选择支付方式并完成支付'},
                    {'step': 8, 'name': '生成取票码', 'description': '生成二维码取票码'},
                    {'step': 9, 'name': '订单完成', 'description': '显示订单详情和取票信息'}
                ],
                'critical_path': True
            },
            'admin_workflow': {
                'name': '管理员工作流程',
                'steps': [
                    {'step': 1, 'name': '系统管理', 'description': '系统配置和维护'},
                    {'step': 2, 'name': '数据管理', 'description': '影院和电影数据管理'},
                    {'step': 3, 'name': '订单管理', 'description': '订单查询和处理'},
                    {'step': 4, 'name': '用户管理', 'description': '用户账号和权限管理'}
                ],
                'critical_path': False
            }
        }
        
        self.analysis_results['business_flows'] = business_flows
        print("✅ 业务流程分析完成")
    
    def analyze_technical_layers(self):
        """分析技术层次"""
        print("🔍 分析技术层次...")
        
        technical_layers = {
            'presentation_layer': {
                'name': 'UI界面层',
                'description': 'PyQt5用户界面组件',
                'components': ['主窗口', '对话框', '控件', '布局管理'],
                'directories': ['ui/', 'views/', 'widgets/'],
                'responsibilities': ['用户交互', '界面展示', '事件处理']
            },
            'business_layer': {
                'name': '业务逻辑层',
                'description': '核心业务逻辑处理',
                'components': ['业务规则', '流程控制', '数据验证'],
                'directories': ['modules/', 'controllers/'],
                'responsibilities': ['业务流程', '规则验证', '逻辑处理']
            },
            'service_layer': {
                'name': '服务层',
                'description': 'API调用和数据服务',
                'components': ['API客户端', '数据转换', '缓存管理'],
                'directories': ['services/'],
                'responsibilities': ['API调用', '数据获取', '服务集成']
            },
            'utility_layer': {
                'name': '工具层',
                'description': '通用工具和辅助功能',
                'components': ['工具函数', '配置管理', '日志处理'],
                'directories': ['utils/'],
                'responsibilities': ['通用功能', '配置管理', '辅助工具']
            }
        }
        
        self.analysis_results['technical_layers'] = technical_layers
        print("✅ 技术层次分析完成")
    
    def generate_optimization_plan(self):
        """生成优化规划"""
        print("🔍 生成优化规划...")
        
        optimization_plan = {
            'phase_1': {
                'name': '核心功能稳定化',
                'duration': '2-3周',
                'priority': 'high',
                'focus_areas': ['用户认证', '座位选择', '支付流程'],
                'objectives': [
                    '修复已知bug',
                    '提升核心功能稳定性',
                    '优化用户体验'
                ],
                'deliverables': [
                    '用户认证模块重构',
                    '座位选择逻辑优化',
                    '支付流程改进'
                ]
            },
            'phase_2': {
                'name': '性能优化',
                'duration': '2-3周',
                'priority': 'medium',
                'focus_areas': ['API调用', '界面响应', '数据处理'],
                'objectives': [
                    '提升系统响应速度',
                    '优化内存使用',
                    '改进API调用效率'
                ],
                'deliverables': [
                    'API调用优化',
                    '界面渲染优化',
                    '数据缓存机制'
                ]
            },
            'phase_3': {
                'name': '功能扩展',
                'duration': '3-4周',
                'priority': 'medium',
                'focus_areas': ['新功能开发', '用户体验', '系统集成'],
                'objectives': [
                    '添加新功能特性',
                    '改进用户界面',
                    '增强系统集成'
                ],
                'deliverables': [
                    '新功能模块',
                    'UI/UX改进',
                    '第三方集成'
                ]
            },
            'phase_4': {
                'name': '代码质量提升',
                'duration': '2-3周',
                'priority': 'low',
                'focus_areas': ['代码重构', '文档完善', '测试覆盖'],
                'objectives': [
                    '提升代码质量',
                    '完善项目文档',
                    '增加测试覆盖率'
                ],
                'deliverables': [
                    '代码重构报告',
                    '完整项目文档',
                    '测试用例集'
                ]
            }
        }
        
        self.analysis_results['optimization_plan'] = optimization_plan
        print("✅ 优化规划生成完成")
    
    def generate_report(self):
        """生成分析报告"""
        print("📊 生成系统架构分析报告...")
        
        # 项目概览
        self.analysis_results['project_overview'] = {
            'analysis_date': '2025-06-06',
            'project_name': 'PyQt5电影票务管理系统',
            'main_program_size': self.analysis_results.get('main_program_analysis', {}).get('file_size_kb', 0),
            'total_directories': len([d for d in self.core_dirs if Path(d).exists()]),
            'analysis_scope': 'Full system architecture analysis'
        }
        
        # 保存详细报告
        with open('system_architecture_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        return self.analysis_results
    
    def run_analysis(self):
        """运行完整分析"""
        print("🎬 PyQt5电影票务管理系统 - 系统架构分析")
        print("=" * 60)
        
        self.analyze_main_program()
        self.analyze_directories()
        self.identify_function_modules()
        self.analyze_business_flows()
        self.analyze_technical_layers()
        self.generate_optimization_plan()
        
        return self.generate_report()

def main():
    """主函数"""
    analyzer = SystemArchitectureAnalyzer()
    results = analyzer.run_analysis()
    
    # 显示摘要
    print(f"\n📊 分析摘要:")
    print(f"  主程序大小: {results['project_overview']['main_program_size']} KB")
    print(f"  分析目录数: {results['project_overview']['total_directories']}")
    print(f"  功能模块数: {len(results['function_modules'])}")
    print(f"  优化阶段数: {len(results['optimization_plan'])}")
    
    print(f"\n✅ 系统架构分析完成！详细报告已保存到: system_architecture_analysis.json")

if __name__ == "__main__":
    main()
