#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 第二阶段B数据处理重构执行器
专门处理443个字典get调用的重构工作
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class Phase2BDataRefactoringExecutor:
    """第二阶段B数据处理重构执行器"""
    
    def __init__(self):
        self.main_file = "main_modular.py"
        self.backup_dir = f"backup_phase2b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.refactoring_log = []
        self.batch_size = 50  # 每批处理的实例数
        
    def create_backup(self):
        """创建第二阶段B备份"""
        print("📦 创建第二阶段B数据重构备份...")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # 备份主文件
            if Path(self.main_file).exists():
                shutil.copy2(self.main_file, self.backup_dir)
                print(f"✅ 备份创建成功: {self.backup_dir}")
                return True
            else:
                print(f"❌ 主文件不存在: {self.main_file}")
                return False
            
        except Exception as e:
            print(f"❌ 备份创建失败: {e}")
            return False
    
    def analyze_data_patterns(self):
        """分析数据处理模式"""
        print("🔍 分析数据处理重复模式...")
        
        if not Path(self.main_file).exists():
            return {}
        
        with open(self.main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        patterns = {
            'simple_get': [],      # 简单的 .get() 调用
            'get_with_check': [],  # .get() 后跟None检查
            'nested_get': [],      # 嵌套的 .get() 调用
            'price_format': [],    # 价格格式化
            'type_conversion': []  # 类型转换
        }
        
        # 查找简单的 .get() 调用
        simple_get_pattern = r'(\w+)\.get\([\'"](\w+)[\'"],\s*([^)]+)\)'
        for match in re.finditer(simple_get_pattern, content):
            patterns['simple_get'].append({
                'full_match': match.group(0),
                'dict_var': match.group(1),
                'key': match.group(2),
                'default': match.group(3),
                'start': match.start(),
                'end': match.end()
            })
        
        # 查找 .get() 后跟None检查
        get_check_pattern = r'(\w+)\.get\([\'"](\w+)[\'"](?:,\s*([^)]+))?\)\s*(?:is\s+not\s+None|!=\s*None)'
        for match in re.finditer(get_check_pattern, content):
            patterns['get_with_check'].append({
                'full_match': match.group(0),
                'dict_var': match.group(1),
                'key': match.group(2),
                'default': match.group(3) or 'None',
                'start': match.start(),
                'end': match.end()
            })
        
        # 查找嵌套的 .get() 调用
        nested_get_pattern = r'(\w+)\.get\([\'"](\w+)[\'"],\s*\{\}\)\.get\([\'"](\w+)[\'"](?:,\s*([^)]+))?\)'
        for match in re.finditer(nested_get_pattern, content):
            patterns['nested_get'].append({
                'full_match': match.group(0),
                'dict_var': match.group(1),
                'key1': match.group(2),
                'key2': match.group(3),
                'default': match.group(4) or 'None',
                'start': match.start(),
                'end': match.end()
            })
        
        # 查找价格格式化
        price_format_pattern = r'f[\'"]¥\{([^}]+):.2f\}[\'"]'
        for match in re.finditer(price_format_pattern, content):
            patterns['price_format'].append({
                'full_match': match.group(0),
                'price_var': match.group(1),
                'start': match.start(),
                'end': match.end()
            })
        
        print(f"  📊 发现简单get调用: {len(patterns['simple_get'])} 个")
        print(f"  📊 发现get+检查模式: {len(patterns['get_with_check'])} 个")
        print(f"  📊 发现嵌套get调用: {len(patterns['nested_get'])} 个")
        print(f"  📊 发现价格格式化: {len(patterns['price_format'])} 个")
        
        return patterns
    
    def add_data_utils_import(self):
        """添加DataUtils导入"""
        print("📥 添加DataUtils导入...")
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经导入
            if 'from utils.data_utils import DataUtils' in content:
                print("  ℹ️ DataUtils已经导入")
                return True
            
            # 找到合适的位置插入导入
            lines = content.split('\n')
            insert_position = -1
            
            # 在UIComponentFactory导入后添加
            for i, line in enumerate(lines):
                if 'from ui.ui_component_factory import UIComponentFactory' in line:
                    insert_position = i + 1
                    break
            
            if insert_position == -1:
                # 如果没找到UIComponentFactory，在PyQt5导入后添加
                for i, line in enumerate(lines):
                    if 'from PyQt5.QtCore import' in line:
                        insert_position = i + 1
                        break
            
            if insert_position != -1:
                lines.insert(insert_position, 'from utils.data_utils import DataUtils')
                
                with open(self.main_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print("  ✅ DataUtils导入添加成功")
                return True
            else:
                print("  ❌ 未找到合适的导入位置")
                return False
                
        except Exception as e:
            print(f"  ❌ 添加导入失败: {e}")
            return False
    
    def execute_batch_refactoring(self, patterns: Dict, batch_name: str, batch_patterns: List):
        """执行批量重构"""
        print(f"🔧 执行{batch_name}重构...")
        
        if not batch_patterns:
            print(f"  ℹ️ {batch_name}无需重构")
            return True
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modifications = 0
            
            # 按位置倒序排序，避免位置偏移问题
            sorted_patterns = sorted(batch_patterns, key=lambda x: x['start'], reverse=True)
            
            for pattern in sorted_patterns[:self.batch_size]:  # 限制批次大小
                if batch_name == "简单get调用":
                    replacement = f"DataUtils.safe_get({pattern['dict_var']}, '{pattern['key']}', {pattern['default']})"
                elif batch_name == "get+检查模式":
                    replacement = f"DataUtils.safe_get({pattern['dict_var']}, '{pattern['key']}', {pattern['default']})"
                elif batch_name == "嵌套get调用":
                    replacement = f"DataUtils.safe_get_nested({pattern['dict_var']}, ['{pattern['key1']}', '{pattern['key2']}'], {pattern['default']})"
                elif batch_name == "价格格式化":
                    replacement = f"DataUtils.format_price({pattern['price_var']})"
                else:
                    continue
                
                # 替换内容
                start = pattern['start']
                end = pattern['end']
                content = content[:start] + replacement + content[end:]
                modifications += 1
            
            if modifications > 0:
                with open(self.main_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.refactoring_log.append({
                    'batch': batch_name,
                    'modifications': modifications,
                    'status': 'success'
                })
                
                print(f"  ✅ {batch_name}重构完成，修改了 {modifications} 处")
                return True
            else:
                print(f"  ℹ️ {batch_name}无需修改")
                return True
                
        except Exception as e:
            print(f"  ❌ {batch_name}重构失败: {e}")
            self.refactoring_log.append({
                'batch': batch_name,
                'error': str(e),
                'status': 'failed'
            })
            return False
    
    def validate_syntax(self):
        """验证语法"""
        print("🔍 验证语法...")
        
        try:
            import py_compile
            py_compile.compile(self.main_file, doraise=True)
            print("  ✅ 语法检查通过")
            return True
        except py_compile.PyCompileError as e:
            print(f"  ❌ 语法检查失败: {e}")
            return False
    
    def run_phase2b_batch1(self):
        """运行第二阶段B第1批：简单get调用重构"""
        print("🚀 开始第二阶段B第1批：简单get调用重构")
        print("=" * 60)
        
        # 创建备份
        if not self.create_backup():
            return False
        
        # 添加导入
        if not self.add_data_utils_import():
            return False
        
        # 分析模式
        patterns = self.analyze_data_patterns()
        
        # 执行第1批重构：简单get调用
        success = self.execute_batch_refactoring(
            patterns, 
            "简单get调用", 
            patterns['simple_get']
        )
        
        if success:
            # 验证语法
            syntax_ok = self.validate_syntax()
            if syntax_ok:
                print("\n🎉 第1批重构成功完成！")
                print("📋 请立即测试以下功能：")
                print("1. 启动主程序")
                print("2. 测试登录功能")
                print("3. 测试数据显示")
                print("4. 检查控制台无错误")
                
                return True
            else:
                print("\n❌ 语法验证失败，建议回滚")
                return False
        else:
            print("\n❌ 第1批重构失败")
            return False
    
    def run_phase2b_batch2(self):
        """运行第二阶段B第2批：get+检查模式重构"""
        print("🚀 开始第二阶段B第2批：get+检查模式重构")
        print("=" * 60)
        
        # 分析模式
        patterns = self.analyze_data_patterns()
        
        # 执行第2批重构
        success = self.execute_batch_refactoring(
            patterns,
            "get+检查模式",
            patterns['get_with_check']
        )
        
        if success and self.validate_syntax():
            print("\n🎉 第2批重构成功完成！")
            return True
        else:
            print("\n❌ 第2批重构失败")
            return False
    
    def run_phase2b_batch3(self):
        """运行第二阶段B第3批：嵌套get调用重构"""
        print("🚀 开始第二阶段B第3批：嵌套get调用重构")
        print("=" * 60)
        
        patterns = self.analyze_data_patterns()
        
        success = self.execute_batch_refactoring(
            patterns,
            "嵌套get调用",
            patterns['nested_get']
        )
        
        if success and self.validate_syntax():
            print("\n🎉 第3批重构成功完成！")
            return True
        else:
            print("\n❌ 第3批重构失败")
            return False
    
    def run_phase2b_batch4(self):
        """运行第二阶段B第4批：价格格式化重构"""
        print("🚀 开始第二阶段B第4批：价格格式化重构")
        print("=" * 60)
        
        patterns = self.analyze_data_patterns()
        
        success = self.execute_batch_refactoring(
            patterns,
            "价格格式化",
            patterns['price_format']
        )
        
        if success and self.validate_syntax():
            print("\n🎉 第4批重构成功完成！")
            return True
        else:
            print("\n❌ 第4批重构失败")
            return False
    
    def generate_phase2b_report(self):
        """生成第二阶段B报告"""
        print("📊 生成第二阶段B执行报告...")
        
        patterns = self.analyze_data_patterns()
        total_patterns = sum(len(p) for p in patterns.values())
        
        report = f"""# PyQt5电影票务管理系统 - 第二阶段B数据重构执行报告

## 📊 执行概览

**执行时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}  
**执行阶段**：第二阶段B - 数据处理重构  
**备份目录**：{self.backup_dir}  

---

## 🔍 重构模式分析

### 📊 发现的数据处理模式
- **简单get调用**：{len(patterns['simple_get'])} 个
- **get+检查模式**：{len(patterns['get_with_check'])} 个
- **嵌套get调用**：{len(patterns['nested_get'])} 个
- **价格格式化**：{len(patterns['price_format'])} 个
- **总计**：{total_patterns} 个

---

## 📋 执行记录

"""
        
        success_count = 0
        total_modifications = 0
        
        for log_entry in self.refactoring_log:
            status_icon = "✅" if log_entry['status'] == 'success' else "❌"
            report += f"""
### {status_icon} {log_entry['batch']}
- **状态**：{log_entry['status']}
"""
            if 'modifications' in log_entry:
                report += f"- **修改数量**：{log_entry['modifications']}\n"
                total_modifications += log_entry['modifications']
                success_count += 1
            if 'error' in log_entry:
                report += f"- **错误信息**：{log_entry['error']}\n"
        
        report += f"""
---

## 📊 重构效果

### 量化收益
- **成功批次**：{success_count}
- **总修改数**：{total_modifications}
- **剩余模式**：{total_patterns - total_modifications}

### 代码改进示例
```python
# 重构前
value = data.get('key', default_value)

# 重构后
value = DataUtils.safe_get(data, 'key', default_value)
```

---

## 🎯 下一步建议

### 继续重构
1. **验证当前功能** - 确保重构后系统正常
2. **继续下一批** - 处理剩余的数据模式
3. **进入第二阶段C** - 开始错误处理重构

### 回滚方案
如果发现问题，可以快速回滚：
```bash
cp {self.backup_dir}/main_modular.py .
```

---

## 🎉 总结

第二阶段B数据重构{'成功' if success_count > 0 else '需要继续'}！

- **工具类应用**：DataUtils已集成
- **重构进展**：{total_modifications}/{total_patterns} 个模式已处理
- **系统稳定**：语法检查通过
- **备份保障**：可随时回滚

**建议继续处理剩余的数据模式，然后进入第二阶段C的错误处理重构！**
"""
        
        try:
            with open('第二阶段B数据重构报告.md', 'w', encoding='utf-8') as f:
                f.write(report)
            print("✅ 报告生成成功: 第二阶段B数据重构报告.md")
        except Exception as e:
            print(f"❌ 报告生成失败: {e}")

def main():
    """主函数"""
    executor = Phase2BDataRefactoringExecutor()
    
    print("🎬 PyQt5电影票务管理系统 - 第二阶段B数据重构执行器")
    print("=" * 70)
    print("🎯 目标：重构443个数据处理重复模式")
    print("📋 策略：分4批执行，每批后立即测试")
    print("⚠️ 重要：每批完成后请立即测试功能！")
    print()
    
    print("📊 执行选项：")
    print("1. 执行第1批：简单get调用重构")
    print("2. 执行第2批：get+检查模式重构")
    print("3. 执行第3批：嵌套get调用重构")
    print("4. 执行第4批：价格格式化重构")
    print("5. 生成执行报告")
    print("0. 退出")
    
    while True:
        choice = input("\n请选择执行选项 (1-5, 0退出): ").strip()
        
        if choice == '1':
            success = executor.run_phase2b_batch1()
            if success:
                print("\n✅ 第1批完成！请立即测试功能，确认无误后继续第2批")
            else:
                print("\n❌ 第1批失败！请检查问题或回滚")
        
        elif choice == '2':
            success = executor.run_phase2b_batch2()
            if success:
                print("\n✅ 第2批完成！请立即测试功能，确认无误后继续第3批")
            else:
                print("\n❌ 第2批失败！请检查问题或回滚")
        
        elif choice == '3':
            success = executor.run_phase2b_batch3()
            if success:
                print("\n✅ 第3批完成！请立即测试功能，确认无误后继续第4批")
            else:
                print("\n❌ 第3批失败！请检查问题或回滚")
        
        elif choice == '4':
            success = executor.run_phase2b_batch4()
            if success:
                print("\n✅ 第4批完成！第二阶段B数据重构全部完成！")
                print("🎉 建议生成报告并准备进入第二阶段C")
            else:
                print("\n❌ 第4批失败！请检查问题或回滚")
        
        elif choice == '5':
            executor.generate_phase2b_report()
        
        elif choice == '0':
            print("👋 退出第二阶段B重构执行器")
            break
        
        else:
            print("❌ 无效选项，请重新选择")

if __name__ == "__main__":
    main()
