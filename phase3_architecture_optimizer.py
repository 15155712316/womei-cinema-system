#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 第三阶段架构优化执行器
基于第二阶段成功完成的重构基础，进行深层次架构优化
"""

import os
import re
import ast
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class Phase3ArchitectureOptimizer:
    """第三阶段架构优化执行器"""

    def __init__(self):
        self.main_file = "main_modular.py"
        self.backup_dir = f"backup_phase3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.optimization_log = []
        self.analysis_results = {}

    def create_backup(self):
        """创建第三阶段备份"""
        print("📦 创建第三阶段架构优化备份...")

        try:
            os.makedirs(self.backup_dir, exist_ok=True)

            # 备份主文件和工具类
            files_to_backup = [
                self.main_file,
                "ui/ui_component_factory.py",
                "utils/data_utils.py",
                "utils/error_handler.py"
            ]

            for file_path in files_to_backup:
                if Path(file_path).exists():
                    # 保持目录结构
                    backup_path = Path(self.backup_dir) / file_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, backup_path)

            print(f"✅ 备份创建成功: {self.backup_dir}")
            return True

        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return False

    def analyze_method_complexity(self):
        """分析方法复杂度"""
        print("🔍 分析方法复杂度...")

        if not Path(self.main_file).exists():
            return {}

        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析AST
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"❌ 语法错误，无法解析: {e}")
            return {}

        complex_methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算方法复杂度
                method_lines = node.end_lineno - node.lineno + 1

                # 计算圈复杂度指标
                if_count = len([n for n in ast.walk(node) if isinstance(n, ast.If)])
                for_count = len([n for n in ast.walk(node) if isinstance(n, (ast.For, ast.While))])
                try_count = len([n for n in ast.walk(node) if isinstance(n, ast.Try)])

                complexity_score = method_lines + if_count * 2 + for_count * 2 + try_count * 3

                if method_lines > 50 or complexity_score > 30:  # 复杂方法阈值
                    complex_methods.append({
                        'name': node.name,
                        'start_line': node.lineno,
                        'end_line': node.end_lineno,
                        'lines': method_lines,
                        'if_count': if_count,
                        'loop_count': for_count,
                        'try_count': try_count,
                        'complexity_score': complexity_score,
                        'priority': 'high' if complexity_score > 60 else 'medium'
                    })

        # 按复杂度排序
        complex_methods.sort(key=lambda x: x['complexity_score'], reverse=True)

        self.analysis_results['complex_methods'] = complex_methods

        print(f"  📊 发现复杂方法: {len(complex_methods)} 个")
        for method in complex_methods[:5]:  # 显示前5个最复杂的
            print(f"    - {method['name']}: {method['lines']}行, 复杂度{method['complexity_score']}")

        return complex_methods

    def analyze_api_patterns(self):
        """分析API调用模式"""
        print("🔍 分析API调用模式...")

        if not Path(self.main_file).exists():
            return {}

        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        api_patterns = {
            'requests_calls': [],
            'api_endpoints': [],
            'error_handling': [],
            'response_parsing': []
        }

        # 查找requests调用
        requests_pattern = r'requests\.(get|post|put|delete)\s*\([^)]*\)'
        for match in re.finditer(requests_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            api_patterns['requests_calls'].append({
                'method': match.group(1),
                'full_call': match.group(0),
                'line': line_num,
                'start': match.start(),
                'end': match.end()
            })

        # 查找API端点
        endpoint_pattern = r'[\'"]https?://[^\'\"]*[\'"]'
        for match in re.finditer(endpoint_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            api_patterns['api_endpoints'].append({
                'url': match.group(0),
                'line': line_num,
                'start': match.start(),
                'end': match.end()
            })

        # 查找响应解析模式
        json_parse_pattern = r'\.json\(\)|json\.loads\([^)]*\)'
        for match in re.finditer(json_parse_pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            api_patterns['response_parsing'].append({
                'pattern': match.group(0),
                'line': line_num,
                'start': match.start(),
                'end': match.end()
            })

        self.analysis_results['api_patterns'] = api_patterns

        print(f"  📊 发现requests调用: {len(api_patterns['requests_calls'])} 个")
        print(f"  📊 发现API端点: {len(api_patterns['api_endpoints'])} 个")
        print(f"  📊 发现响应解析: {len(api_patterns['response_parsing'])} 个")

        return api_patterns

    def analyze_design_patterns_opportunities(self):
        """分析设计模式应用机会"""
        print("🔍 分析设计模式应用机会...")

        if not Path(self.main_file).exists():
            return {}

        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern_opportunities = {
            'factory_pattern': [],
            'strategy_pattern': [],
            'observer_pattern': [],
            'singleton_pattern': []
        }

        # 工厂模式机会 - 查找重复的对象创建
        creation_patterns = [
            r'if\s+.*?==\s*[\'"](\w+)[\'"]:\s*\n\s*.*?=\s*(\w+)\(',
            r'payment_type\s*==\s*[\'"](\w+)[\'"]',
            r'order_type\s*==\s*[\'"](\w+)[\'"]'
        ]

        for pattern in creation_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                pattern_opportunities['factory_pattern'].append({
                    'type': match.group(1) if match.groups() else 'unknown',
                    'line': line_num,
                    'context': match.group(0)[:100]
                })

        # 策略模式机会 - 查找条件分支
        strategy_pattern = r'if\s+.*?payment.*?:\s*\n.*?\nelse.*?:\s*\n'
        for match in re.finditer(strategy_pattern, content, re.MULTILINE | re.DOTALL):
            line_num = content[:match.start()].count('\n') + 1
            pattern_opportunities['strategy_pattern'].append({
                'line': line_num,
                'context': match.group(0)[:150]
            })

        # 观察者模式机会 - 查找状态更新
        observer_patterns = [
            r'self\.\w+_status\s*=',
            r'update.*?ui',
            r'notify.*?change'
        ]

        for pattern in observer_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                pattern_opportunities['observer_pattern'].append({
                    'line': line_num,
                    'pattern': match.group(0)
                })

        self.analysis_results['design_patterns'] = pattern_opportunities

        print(f"  📊 工厂模式机会: {len(pattern_opportunities['factory_pattern'])} 个")
        print(f"  📊 策略模式机会: {len(pattern_opportunities['strategy_pattern'])} 个")
        print(f"  📊 观察者模式机会: {len(pattern_opportunities['observer_pattern'])} 个")

        return pattern_opportunities

    def analyze_performance_bottlenecks(self):
        """分析性能瓶颈"""
        print("🔍 分析性能瓶颈...")

        if not Path(self.main_file).exists():
            return {}

        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()

        performance_issues = {
            'repeated_calculations': [],
            'inefficient_loops': [],
            'memory_leaks': [],
            'blocking_operations': []
        }

        # 查找重复计算
        calc_patterns = [
            r'for\s+\w+\s+in\s+\w+:\s*\n\s*.*?calculate.*?\(',
            r'len\([^)]+\)\s*>\s*0',
            r'\.get\([^)]+\)\s*is\s+not\s+None'
        ]

        for pattern in calc_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                performance_issues['repeated_calculations'].append({
                    'line': line_num,
                    'pattern': match.group(0),
                    'suggestion': '考虑缓存计算结果'
                })

        # 查找低效循环
        loop_patterns = [
            r'for\s+\w+\s+in\s+range\(len\([^)]+\)\):',
            r'while\s+.*?:\s*\n\s*.*?sleep\('
        ]

        for pattern in loop_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                performance_issues['inefficient_loops'].append({
                    'line': line_num,
                    'pattern': match.group(0),
                    'suggestion': '优化循环逻辑'
                })

        # 查找阻塞操作
        blocking_patterns = [
            r'requests\.(get|post)\([^)]*\)',
            r'time\.sleep\([^)]*\)',
            r'input\([^)]*\)'
        ]

        for pattern in blocking_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                performance_issues['blocking_operations'].append({
                    'line': line_num,
                    'operation': match.group(0),
                    'suggestion': '考虑异步处理'
                })

        self.analysis_results['performance_issues'] = performance_issues

        total_issues = sum(len(issues) for issues in performance_issues.values())
        print(f"  📊 发现性能问题: {total_issues} 个")

        return performance_issues

    def run_comprehensive_analysis(self):
        """运行综合分析"""
        print("🚀 开始第三阶段综合分析")
        print("=" * 60)

        # 创建备份
        if not self.create_backup():
            return False

        # 执行各项分析
        self.analyze_method_complexity()
        self.analyze_api_patterns()
        self.analyze_design_patterns_opportunities()
        self.analyze_performance_bottlenecks()

        # 生成分析报告
        self.generate_analysis_report()

        print("\n✅ 第三阶段综合分析完成！")
        return True

    def generate_analysis_report(self):
        """生成分析报告"""
        print("📊 生成第三阶段分析报告...")

        report = f"""# PyQt5电影票务管理系统 - 第三阶段架构优化分析报告

## 📊 分析概览

**分析时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}
**分析阶段**：第三阶段 - 架构优化
**备份目录**：{self.backup_dir}

---

## 🔍 复杂方法分析

### 发现的复杂方法
"""

        complex_methods = self.analysis_results.get('complex_methods', [])
        if complex_methods:
            for method in complex_methods:
                report += f"""
#### {method['name']} (第{method['start_line']}-{method['end_line']}行)
- **代码行数**：{method['lines']} 行
- **复杂度评分**：{method['complexity_score']}
- **条件分支**：{method['if_count']} 个
- **循环结构**：{method['loop_count']} 个
- **异常处理**：{method['try_count']} 个
- **优化优先级**：{method['priority']}
- **建议**：拆分为多个职责单一的小方法
"""
        else:
            report += "\n✅ 未发现需要拆分的复杂方法\n"

        report += f"""
---

## 🌐 API调用模式分析

### API调用统计
"""

        api_patterns = self.analysis_results.get('api_patterns', {})
        report += f"""
- **Requests调用**：{len(api_patterns.get('requests_calls', []))} 个
- **API端点**：{len(api_patterns.get('api_endpoints', []))} 个
- **响应解析**：{len(api_patterns.get('response_parsing', []))} 个

### 统一化建议
1. **创建统一API客户端**：集中管理所有API调用
2. **标准化错误处理**：统一的异常处理和重试机制
3. **响应解析统一**：标准化的响应数据处理
"""

        report += f"""
---

## 🎨 设计模式应用机会

### 模式应用建议
"""

        design_patterns = self.analysis_results.get('design_patterns', {})
        report += f"""
- **工厂模式机会**：{len(design_patterns.get('factory_pattern', []))} 个
- **策略模式机会**：{len(design_patterns.get('strategy_pattern', []))} 个
- **观察者模式机会**：{len(design_patterns.get('observer_pattern', []))} 个

### 具体应用建议
1. **支付处理工厂**：统一支付方式创建
2. **订单状态策略**：不同订单状态的处理策略
3. **UI更新观察者**：状态变化的UI自动更新
"""

        report += f"""
---

## ⚡ 性能优化机会

### 性能问题统计
"""

        performance_issues = self.analysis_results.get('performance_issues', {})
        total_perf_issues = sum(len(issues) for issues in performance_issues.values())

        report += f"""
- **重复计算**：{len(performance_issues.get('repeated_calculations', []))} 个
- **低效循环**：{len(performance_issues.get('inefficient_loops', []))} 个
- **阻塞操作**：{len(performance_issues.get('blocking_operations', []))} 个
- **总计问题**：{total_perf_issues} 个

### 优化建议
1. **计算结果缓存**：避免重复计算
2. **循环优化**：使用更高效的迭代方式
3. **异步处理**：避免阻塞主线程
4. **内存管理**：优化对象创建和销毁
"""

        report += f"""
---

## 🎯 第三阶段执行计划

### 第三阶段A：复杂方法拆分 (2-3天)
- **目标**：拆分{len(complex_methods)}个复杂方法
- **预期收益**：代码可读性提升60-80%
- **风险等级**：中等

### 第三阶段B：API调用统一化 (2-3天)
- **目标**：统一{len(api_patterns.get('requests_calls', []))}个API调用
- **预期收益**：API管理效率提升100%
- **风险等级**：中等

### 第三阶段C：设计模式应用 (3-4天)
- **目标**：应用3-5个设计模式
- **预期收益**：架构质量显著提升
- **风险等级**：高

### 第三阶段D：性能优化 (1-2天)
- **目标**：优化{total_perf_issues}个性能问题
- **预期收益**：性能提升15-30%
- **风险等级**：低

---

## 📊 预期总体收益

### 量化指标
- **代码减少**：200-300行
- **复杂度降低**：50-70%
- **性能提升**：15-30%
- **维护效率**：提升40-60%

### 质量提升
- **可读性**：显著改善
- **可维护性**：大幅提升
- **可扩展性**：明显增强
- **架构质量**：质的飞跃

---

## 🚀 开始执行

准备好开始第三阶段架构优化了吗？

建议执行顺序：
1. **第三阶段A**：复杂方法拆分（风险较低，收益明显）
2. **第三阶段D**：性能优化（风险最低，可并行）
3. **第三阶段B**：API统一化（基于前面基础）
4. **第三阶段C**：设计模式应用（风险最高，最后执行）

**第三阶段架构优化分析完成，可以开始执行优化工作！** 🚀
"""

        try:
            with open('第三阶段架构优化分析报告.md', 'w', encoding='utf-8') as f:
                f.write(report)
            print("✅ 分析报告生成成功: 第三阶段架构优化分析报告.md")
        except Exception as e:
            print(f"❌ 分析报告生成失败: {e}")

def main():
    """主函数"""
    optimizer = Phase3ArchitectureOptimizer()

    print("🎬 PyQt5电影票务管理系统 - 第三阶段架构优化")
    print("=" * 70)
    print("🎯 目标：深层次架构优化，提升代码质量和性能")
    print("📋 基础：第二阶段443个重复模式已重构完成")
    print("⚠️ 重要：分4个子阶段安全执行，每阶段后充分测试")
    print()

    confirm = input("确认开始第三阶段架构优化分析？(输入 'yes' 继续): ")
    if confirm.lower() == 'yes':
        success = optimizer.run_comprehensive_analysis()
        if success:
            print("\n✅ 第三阶段分析完成！请查看分析报告制定执行计划")
        else:
            print("\n❌ 第三阶段分析失败！")
    else:
        print("❌ 分析已取消")

if __name__ == "__main__":
    main()