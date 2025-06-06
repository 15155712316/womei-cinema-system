#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 第二阶段重构规划器
基于第一阶段创建的工具类，规划具体的模式重构方案
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class Phase2RefactoringPlanner:
    """第二阶段重构规划器"""
    
    def __init__(self):
        self.main_file = "main_modular.py"
        self.refactoring_plan = {
            'ui_patterns': [],
            'data_patterns': [],
            'error_patterns': [],
            'refactoring_tasks': [],
            'execution_order': [],
            'risk_assessment': {}
        }
    
    def analyze_main_file_patterns(self):
        """分析主文件中的具体重复模式"""
        print("🔍 分析main_modular.py中的重复模式...")
        
        if not Path(self.main_file).exists():
            print(f"❌ 主文件不存在: {self.main_file}")
            return
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分析UI模式
        self._analyze_ui_patterns(content)
        
        # 分析数据处理模式
        self._analyze_data_patterns(content)
        
        # 分析错误处理模式
        self._analyze_error_patterns(content)
        
        print("✅ 模式分析完成")
    
    def _analyze_ui_patterns(self, content: str):
        """分析UI重复模式"""
        print("  🎨 分析UI组件重复模式...")
        
        ui_patterns = [
            {
                'name': 'QPushButton创建模式',
                'pattern': r'(\w+)\s*=\s*QPushButton\([^)]*\)\s*\n\s*\1\.setStyleSheet\([^)]*\)\s*\n\s*\1\.clicked\.connect\([^)]*\)',
                'replacement_template': 'from ui.ui_component_factory import UIComponentFactory\n{var} = UIComponentFactory.create_styled_button({text}, {callback})',
                'priority': 'high',
                'estimated_savings': 3
            },
            {
                'name': 'QVBoxLayout创建模式',
                'pattern': r'(\w+)\s*=\s*QVBoxLayout\(\)\s*\n\s*\w+\.setLayout\(\1\)\s*\n\s*\1\.addWidget\([^)]*\)',
                'replacement_template': 'from ui.ui_component_factory import UIComponentFactory\n{var} = UIComponentFactory.create_vertical_layout({widget})',
                'priority': 'medium',
                'estimated_savings': 2
            },
            {
                'name': 'QLabel创建模式',
                'pattern': r'(\w+)\s*=\s*QLabel\([^)]*\)\s*\n\s*\1\.setAlignment\([^)]*\)\s*\n\s*\1\.setStyleSheet\([^)]*\)',
                'replacement_template': 'from ui.ui_component_factory import UIComponentFactory\n{var} = UIComponentFactory.create_styled_label({text}, {alignment})',
                'priority': 'medium',
                'estimated_savings': 2
            }
        ]
        
        for pattern_info in ui_patterns:
            matches = list(re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.DOTALL))
            if matches:
                pattern_info['matches'] = len(matches)
                pattern_info['total_savings'] = len(matches) * pattern_info['estimated_savings']
                pattern_info['examples'] = [match.group(0)[:100] + "..." for match in matches[:3]]
                self.refactoring_plan['ui_patterns'].append(pattern_info)
                print(f"    ✅ 发现 {pattern_info['name']}: {len(matches)} 个实例")
    
    def _analyze_data_patterns(self, content: str):
        """分析数据处理重复模式"""
        print("  📊 分析数据处理重复模式...")
        
        data_patterns = [
            {
                'name': '字典安全获取模式',
                'pattern': r'(\w+)\.get\([\'"](\w+)[\'"],\s*([^)]+)\)\s*\n\s*if\s+\1\s+is\s+not\s+None:',
                'replacement_template': 'from utils.data_utils import DataUtils\nvalue = DataUtils.safe_get({dict}, "{key}", {default})',
                'priority': 'high',
                'estimated_savings': 3
            },
            {
                'name': 'JSON响应解析模式',
                'pattern': r'try:\s*\n\s*(\w+)\s*=\s*json\.loads\([^)]+\)\s*\n\s*if\s+\1\.get\([\'"]success[\'"].*?\n.*?except.*?:',
                'replacement_template': 'from utils.data_utils import DataUtils\nresult = DataUtils.parse_json_response({response_text})',
                'priority': 'high',
                'estimated_savings': 5
            },
            {
                'name': '数据验证模式',
                'pattern': r'if\s+not\s+(\w+)\s+or\s+not\s+\1\.get\([\'"](\w+)[\'"].*?\):',
                'replacement_template': 'from utils.data_utils import DataUtils\nis_valid, missing = DataUtils.validate_required_fields({data}, ["{fields}"])',
                'priority': 'medium',
                'estimated_savings': 2
            },
            {
                'name': '价格格式化模式',
                'pattern': r'f[\'"]¥\{(\w+):.2f\}[\'"]',
                'replacement_template': 'from utils.data_utils import DataUtils\nDataUtils.format_price({price})',
                'priority': 'low',
                'estimated_savings': 1
            }
        ]
        
        for pattern_info in data_patterns:
            matches = list(re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.DOTALL))
            if matches:
                pattern_info['matches'] = len(matches)
                pattern_info['total_savings'] = len(matches) * pattern_info['estimated_savings']
                pattern_info['examples'] = [match.group(0)[:100] + "..." for match in matches[:3]]
                self.refactoring_plan['data_patterns'].append(pattern_info)
                print(f"    ✅ 发现 {pattern_info['name']}: {len(matches)} 个实例")
    
    def _analyze_error_patterns(self, content: str):
        """分析错误处理重复模式"""
        print("  🛡️ 分析错误处理重复模式...")
        
        error_patterns = [
            {
                'name': 'API调用错误处理模式',
                'pattern': r'try:\s*\n\s*.*?requests\.(get|post).*?\n\s*.*?\n\s*except.*?Exception.*?:\s*\n\s*.*?QMessageBox\.(warning|critical).*?\n\s*.*?return\s+None',
                'replacement_template': 'from utils.error_handler import handle_api_errors\n@handle_api_errors(show_message=True)\ndef {method_name}(self):',
                'priority': 'high',
                'estimated_savings': 6
            },
            {
                'name': '通用异常处理模式',
                'pattern': r'try:\s*\n\s*(.*?)\n\s*except.*?Exception.*?as\s+e:\s*\n\s*.*?print.*?\n\s*.*?QMessageBox.*?\n\s*return',
                'replacement_template': 'from utils.error_handler import handle_exceptions\n@handle_exceptions(show_message=True)\ndef {method_name}(self):',
                'priority': 'medium',
                'estimated_savings': 4
            },
            {
                'name': '数据验证错误模式',
                'pattern': r'if\s+not\s+.*?:\s*\n\s*QMessageBox\.warning\(.*?\)\s*\n\s*return\s+False',
                'replacement_template': 'from utils.error_handler import validate_data\n@validate_data(required_fields=[...])',
                'priority': 'medium',
                'estimated_savings': 3
            }
        ]
        
        for pattern_info in error_patterns:
            matches = list(re.finditer(pattern_info['pattern'], content, re.MULTILINE | re.DOTALL))
            if matches:
                pattern_info['matches'] = len(matches)
                pattern_info['total_savings'] = len(matches) * pattern_info['estimated_savings']
                pattern_info['examples'] = [match.group(0)[:150] + "..." for match in matches[:2]]
                self.refactoring_plan['error_patterns'].append(pattern_info)
                print(f"    ✅ 发现 {pattern_info['name']}: {len(matches)} 个实例")
    
    def generate_refactoring_tasks(self):
        """生成具体的重构任务"""
        print("📋 生成重构任务...")
        
        task_id = 1
        
        # UI模式重构任务
        for pattern in self.refactoring_plan['ui_patterns']:
            task = {
                'id': task_id,
                'type': 'ui_refactoring',
                'name': f"重构{pattern['name']}",
                'pattern': pattern['name'],
                'instances': pattern['matches'],
                'estimated_time': f"{pattern['matches'] * 10} 分钟",
                'code_savings': pattern['total_savings'],
                'priority': pattern['priority'],
                'risk_level': 'low',
                'dependencies': ['ui_component_factory.py'],
                'validation_steps': [
                    '检查UI组件显示正常',
                    '验证事件绑定正确',
                    '确认样式应用正确'
                ]
            }
            self.refactoring_plan['refactoring_tasks'].append(task)
            task_id += 1
        
        # 数据处理重构任务
        for pattern in self.refactoring_plan['data_patterns']:
            task = {
                'id': task_id,
                'type': 'data_refactoring',
                'name': f"重构{pattern['name']}",
                'pattern': pattern['name'],
                'instances': pattern['matches'],
                'estimated_time': f"{pattern['matches'] * 15} 分钟",
                'code_savings': pattern['total_savings'],
                'priority': pattern['priority'],
                'risk_level': 'medium',
                'dependencies': ['data_utils.py'],
                'validation_steps': [
                    '验证数据处理逻辑正确',
                    '检查边界条件处理',
                    '确认错误情况处理'
                ]
            }
            self.refactoring_plan['refactoring_tasks'].append(task)
            task_id += 1
        
        # 错误处理重构任务
        for pattern in self.refactoring_plan['error_patterns']:
            task = {
                'id': task_id,
                'type': 'error_refactoring',
                'name': f"重构{pattern['name']}",
                'pattern': pattern['name'],
                'instances': pattern['matches'],
                'estimated_time': f"{pattern['matches'] * 20} 分钟",
                'code_savings': pattern['total_savings'],
                'priority': pattern['priority'],
                'risk_level': 'high',
                'dependencies': ['error_handler.py'],
                'validation_steps': [
                    '测试正常流程',
                    '测试异常情况',
                    '验证错误消息显示',
                    '确认程序不会崩溃'
                ]
            }
            self.refactoring_plan['refactoring_tasks'].append(task)
            task_id += 1
        
        print(f"✅ 生成 {len(self.refactoring_plan['refactoring_tasks'])} 个重构任务")
    
    def plan_execution_order(self):
        """规划执行顺序"""
        print("📅 规划执行顺序...")
        
        # 按优先级和风险排序
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        risk_order = {'low': 3, 'medium': 2, 'high': 1}
        
        tasks = self.refactoring_plan['refactoring_tasks']
        
        # 排序：高优先级 + 低风险优先
        sorted_tasks = sorted(tasks, key=lambda x: (
            priority_order.get(x['priority'], 0),
            risk_order.get(x['risk_level'], 0)
        ), reverse=True)
        
        # 分组执行
        execution_phases = {
            'phase_2a': {
                'name': '第二阶段A：低风险UI重构',
                'duration': '1-2天',
                'tasks': [],
                'description': '重构UI组件创建模式，风险最低'
            },
            'phase_2b': {
                'name': '第二阶段B：数据处理重构',
                'duration': '2-3天',
                'tasks': [],
                'description': '重构数据处理逻辑，需要仔细验证'
            },
            'phase_2c': {
                'name': '第二阶段C：错误处理重构',
                'duration': '1-2天',
                'tasks': [],
                'description': '重构错误处理模式，需要全面测试'
            }
        }
        
        # 分配任务到阶段
        for task in sorted_tasks:
            if task['type'] == 'ui_refactoring':
                execution_phases['phase_2a']['tasks'].append(task)
            elif task['type'] == 'data_refactoring':
                execution_phases['phase_2b']['tasks'].append(task)
            elif task['type'] == 'error_refactoring':
                execution_phases['phase_2c']['tasks'].append(task)
        
        self.refactoring_plan['execution_order'] = execution_phases
        
        print("✅ 执行顺序规划完成")
    
    def assess_risks(self):
        """评估重构风险"""
        print("⚠️ 评估重构风险...")
        
        total_tasks = len(self.refactoring_plan['refactoring_tasks'])
        total_instances = sum(task['instances'] for task in self.refactoring_plan['refactoring_tasks'])
        total_savings = sum(task['code_savings'] for task in self.refactoring_plan['refactoring_tasks'])
        
        high_risk_tasks = [task for task in self.refactoring_plan['refactoring_tasks'] if task['risk_level'] == 'high']
        
        risk_assessment = {
            'overall_risk': 'medium',
            'total_tasks': total_tasks,
            'total_instances': total_instances,
            'total_code_savings': total_savings,
            'high_risk_tasks': len(high_risk_tasks),
            'estimated_total_time': f"{sum(int(task['estimated_time'].split()[0]) for task in self.refactoring_plan['refactoring_tasks'])} 分钟",
            'success_probability': '85%',
            'rollback_complexity': 'medium',
            'recommendations': [
                '分阶段执行，每阶段后充分测试',
                '优先执行低风险任务建立信心',
                '高风险任务需要额外的测试覆盖',
                '保持备份，随时准备回滚',
                '建议在非生产时间执行'
            ]
        }
        
        self.refactoring_plan['risk_assessment'] = risk_assessment
        
        print(f"✅ 风险评估完成 - 总体风险: {risk_assessment['overall_risk']}")
    
    def generate_plan_report(self):
        """生成规划报告"""
        print("📊 生成第二阶段重构规划报告...")
        
        report = f"""# PyQt5电影票务管理系统 - 第二阶段重构规划报告

## 📊 规划概览

**规划时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}  
**规划阶段**：第二阶段 - 模式重构  
**基于工具**：第一阶段创建的3个工具类  

---

## 🎯 重构目标

### 核心目标
1. **应用第一阶段工具类**：充分利用已创建的工具类
2. **消除重复模式**：重构43个已识别的重复模式组
3. **提升代码质量**：减少重复代码，提高可维护性
4. **保持功能稳定**：确保重构过程中功能不受影响

### 量化目标
- **预计代码减少**：{self.refactoring_plan['risk_assessment']['total_code_savings']} 行
- **重构实例数**：{self.refactoring_plan['risk_assessment']['total_instances']} 个
- **重构任务数**：{self.refactoring_plan['risk_assessment']['total_tasks']} 个
- **预计用时**：{self.refactoring_plan['risk_assessment']['estimated_total_time']}

---

## 📋 发现的重复模式

### 🎨 UI组件重复模式
"""
        
        for pattern in self.refactoring_plan['ui_patterns']:
            report += f"""
#### {pattern['name']}
- **发现实例**：{pattern['matches']} 个
- **预计节省**：{pattern['total_savings']} 行代码
- **优先级**：{pattern['priority']}
- **示例**：
```python
{pattern['examples'][0] if pattern['examples'] else '暂无示例'}
```
"""
        
        report += "\n### 📊 数据处理重复模式\n"
        for pattern in self.refactoring_plan['data_patterns']:
            report += f"""
#### {pattern['name']}
- **发现实例**：{pattern['matches']} 个
- **预计节省**：{pattern['total_savings']} 行代码
- **优先级**：{pattern['priority']}
"""
        
        report += "\n### 🛡️ 错误处理重复模式\n"
        for pattern in self.refactoring_plan['error_patterns']:
            report += f"""
#### {pattern['name']}
- **发现实例**：{pattern['matches']} 个
- **预计节省**：{pattern['total_savings']} 行代码
- **优先级**：{pattern['priority']}
"""
        
        report += f"""
---

## 🚀 执行计划

### 分阶段执行策略
"""
        
        for phase_key, phase in self.refactoring_plan['execution_order'].items():
            report += f"""
### {phase['name']}
- **持续时间**：{phase['duration']}
- **任务数量**：{len(phase['tasks'])} 个
- **描述**：{phase['description']}

#### 具体任务：
"""
            for task in phase['tasks']:
                report += f"""
- **任务{task['id']}**：{task['name']}
  - 实例数：{task['instances']} 个
  - 预计时间：{task['estimated_time']}
  - 代码节省：{task['code_savings']} 行
  - 风险等级：{task['risk_level']}
"""
        
        report += f"""
---

## ⚠️ 风险评估

### 总体风险评估
- **风险等级**：{self.refactoring_plan['risk_assessment']['overall_risk']}
- **成功概率**：{self.refactoring_plan['risk_assessment']['success_probability']}
- **高风险任务**：{self.refactoring_plan['risk_assessment']['high_risk_tasks']} 个
- **回滚复杂度**：{self.refactoring_plan['risk_assessment']['rollback_complexity']}

### 风险控制建议
"""
        for rec in self.refactoring_plan['risk_assessment']['recommendations']:
            report += f"- {rec}\n"
        
        report += """
---

## 📋 执行检查清单

### 执行前准备
- [ ] 确认第一阶段工具类正常工作
- [ ] 创建新的备份分支
- [ ] 准备测试用例
- [ ] 通知团队成员

### 每个任务执行后
- [ ] 语法检查通过
- [ ] 相关功能测试通过
- [ ] 无新增错误日志
- [ ] 代码审查通过

### 每个阶段完成后
- [ ] 完整功能测试
- [ ] 性能基准测试
- [ ] 用户验收测试
- [ ] 文档更新

---

## 🎯 预期收益

### 代码质量提升
- **代码行数减少**：{self.refactoring_plan['risk_assessment']['total_code_savings']} 行
- **重复模式消除**：{self.refactoring_plan['risk_assessment']['total_instances']} 个实例
- **维护复杂度降低**：集中管理重复逻辑

### 开发效率提升
- **修改效率**：统一修改点，减少重复工作
- **调试效率**：标准化模式，更容易定位问题
- **扩展效率**：基于工具类，更容易添加新功能

### 系统稳定性提升
- **错误处理统一**：减少遗漏的错误处理
- **数据处理安全**：统一的数据验证和处理
- **UI一致性**：统一的组件创建和样式

---

## 🚀 开始执行

准备好开始第二阶段重构了吗？

1. **立即开始**：执行第二阶段A（UI重构）
2. **进一步规划**：详细分析具体重构点
3. **团队讨论**：与团队讨论执行策略

**建议从第二阶段A开始，因为UI重构风险最低，容易建立信心！**
"""
        
        # 保存报告
        with open('第二阶段重构规划报告.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("✅ 规划报告生成完成: 第二阶段重构规划报告.md")
    
    def run_planning(self):
        """运行完整规划"""
        print("🎬 PyQt5电影票务管理系统 - 第二阶段重构规划")
        print("=" * 60)
        
        self.analyze_main_file_patterns()
        self.generate_refactoring_tasks()
        self.plan_execution_order()
        self.assess_risks()
        self.generate_plan_report()
        
        return self.refactoring_plan

def main():
    """主函数"""
    planner = Phase2RefactoringPlanner()
    plan = planner.run_planning()
    
    # 显示摘要
    print(f"\n📊 第二阶段规划摘要:")
    print(f"  发现UI模式: {len(plan['ui_patterns'])} 个")
    print(f"  发现数据模式: {len(plan['data_patterns'])} 个")
    print(f"  发现错误模式: {len(plan['error_patterns'])} 个")
    print(f"  生成任务: {len(plan['refactoring_tasks'])} 个")
    print(f"  预计节省: {plan['risk_assessment']['total_code_savings']} 行代码")
    
    print(f"\n✅ 第二阶段重构规划完成！详细报告已保存到: 第二阶段重构规划报告.md")

if __name__ == "__main__":
    main()
